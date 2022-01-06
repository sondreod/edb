""" A simple and flexible in-memory database written in Python.
Can be used as a simple keyvalue store, or you can query the in-memory data at runtime with a custom python function

Have cake, and eat it too.
"""
__version__ = "0.1-a0"

import random
import sys
import pickle
import socket
import asyncio
from typing import Any, Callable, Dict, Union, Tuple, List
from functools import partial, lru_cache
from os import environ
import logging


class Resource:
    def __init__(self, resource) -> None:
        self.resource = resource

    def query(self, *args, **kwargs):
        return query(self.resource, *args, **kwargs)

    def list(self):
        return query(self.resource, "list_resource")

    def create(self, type=None):
        if not type:
            type = dict()
        return query(self.resource, "create_resource", type)

    def delete(self):
        return query(self.resource, "delete_resource")

    def __getattr__(self, name):
        """Lookup builtin dbfuncs"""

        def method(*args, **kwargs):
            return self.query(name, *args, **kwargs)

        return method


def query(resource, func, *args, **kwargs):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("localhost", environ.get("EDB_PORT", 54200)))

        data = pickle.dumps((resource, func, args, kwargs))
        client.send(data)
        return pickle.loads(client.recv(4096))


class EdbServer(asyncio.Protocol):
    """TODO: hash the bytes of the pickled object with a preshared key/salt. Prepend to payload with a static length

    E.g. payload = |hash of pickled object, len always e.g. 64|pickled object as bytes|
    """

    def __init__(self, store) -> None:
        self.store = store
        assert id(store) == id(self.store)
        super().__init__()

    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        print(f"Connection from {peername}")
        self.transport = transport

    def data_received(self, data):
        resource, func, args, kwargs = pickle.loads(data)

        if func == "create_resource":
            if not self.store.get(resource):
                self.store[resource] = args[0]
            else:
                print("Resource already exists")
            response = pickle.dumps(True)
        elif func == "delete_resource":
            del self.store[resource]
            response = pickle.dumps(True)
        elif func == "list_resource":
            response = pickle.dumps(list(self.store.keys()))
        else:
            if isinstance(func, str):
                func = self._get_builtin_dbfunc_from_string(func)
            fn = partial(func, *args, **kwargs)
            result = fn(self.store.get(resource))

            response = pickle.dumps(result)

        self.transport.write(response)
        self.transport.close()

    def create_resource(self, name: str, o: Union[dict, list, tuple]):
        # Fix resource handling
        self.store[name] = 0

    @staticmethod
    def _get_builtin_dbfunc_from_string(func: str):
        """Get callable function from dbfuncs with function name (str)"""
        return globals()[func]


async def periodic(store):
    while True:
        # Ideer: Her kan hele resource elementer byttes til en ny versjon laget i
        # en egen prosess, slik at bare bytte må gjøres synkront(blocking)
        # Mulig best med en Queue med tasks
        print(
            f"Number of resources {len(store)}, number of elements {sum([len(x) for x in store.values()])}",
            end="\r",
        )
        await asyncio.sleep(10)


# Dbfuncs


def add(elem, o):
    if isinstance(o, dict):
        key, value = elem
        o[key] = value
        return True
    if isinstance(o, list):
        return o.append(elem)
    raise NotImplementedError(
        f"Unsupported resource type {type(o)}. Unable to access elem {elem}"
    )


def get(key_or_index: str, o):
    if isinstance(o, dict):
        return o.get(key_or_index)
    if isinstance(o, list):
        return o[key_or_index]
    raise NotImplementedError(
        f"Unsupported resource type {type(o)}. Unable to access key_or_index {key_or_index}"
    )


def key_startswith(string: str, o) -> List[Tuple[str, Any]]:
    def _fn():
        for key, value in o.items():
            if key.startswith(string):
                yield key, value

    return list(_fn())


def get_resource(o):
    return o


async def main():
    store: Dict[str, Union[dict, list, set]] = {
        "default": dict()
    }  # Dict holding the in-memory data
    loop = asyncio.get_running_loop()
    task = loop.create_task(
        periodic(store)
    )  # Use for healthchecks, cleanups and cache updates, persist db to file?

    server = await loop.create_server(
        lambda: EdbServer(store), "127.0.0.1", environ.get("EDB_PORT")
    )
    logging.warning(
        f"EDB in-memory database server started on port {environ.get('EDB_PORT')}"
    )

    async with server:
        await server.serve_forever()


def run(port=54200):
    if not environ.get("EDB_PORT"):
        environ["EDB_PORT"] = str(port)
    asyncio.run(main())


if __name__ == "__main__":
    run()