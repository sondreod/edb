""" A simple and flexible in-memory database written in Python.
Can be as simple as a keyvalue store, or you can query the in-memory
data at runtime with a custom python function.

Have cake, and eat it too.
"""
__version__ = "0.1-a1"

from pathlib import Path
import pickle
import socket
import asyncio
import logging
from os import environ
from typing import Any, Callable, Dict, Union, Tuple, List

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("EDB")


class Resource:
    def __init__(self, resource: str) -> None:

        self.resource = resource

    def create(self, type):
        query(self.resource, "create_resource", type)
        return self

    def delete(self):
        query(self.resource, "delete_resource")

    def NOT_IMPLEMENTED__getattribute__(self, *args, **kwargs) -> Any:
        """TODO: Send the calls dynamicaly, remove the functions below (except register)"""
        return query(self.resource, "__getattribute__", *args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return query(self.resource, "__repr__", *args, **kwargs)

    def __str__(self, *args, **kwargs):
        return query(self.resource, "__str__", *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return query(self.resource, "__setitem__", *args, **kwargs)

    def __getattr__(self, *args, **kwargs):
        return query(self.resource, "__getattr__", *args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return query(self.resource, "__getitem__", *args, **kwargs)

    def add(self, *args, **kwargs):
        return query(self.resource, "add", *args, **kwargs)

    def get(self, *args, **kwargs):
        return query(self.resource, "get", *args, **kwargs)

    def append(self, *args, **kwargs):
        return query(self.resource, "append", *args, **kwargs)

    def __len__(self):
        return query(self.resource, "__len__")

    def register():
        # --TODO:
        # Create functionality for registering custom functions and class-definitions so
        # classes can be unpickled server side, and function can be ran.
        # Probobaly a good idea to support storing the bytes unpickled
        # in the database, if search functinality on the data it self
        # (only keys e.g.) it's not important
        pass


def query(resource, func, *args, **kwargs):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect("/tmp/edb.socket")

        data = pickle.dumps((resource, func, args, kwargs))
        client.send(data)
        return pickle.loads(client.recv(4096))


class EdbServer(asyncio.Protocol):
    """TODO: hash the bytes of the pickled object with a preshared key/salt. Prepend to payload with a static length

    E.g. payload = |hash of pickled object, len always e.g. 64|pickled object as bytes|
    """

    def __init__(self, store: Dict[str, Any], register: List) -> None:
        self.store = store
        self.register = register
        super().__init__()

    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        log.debug(f"Connection from {peername}")
        self.transport = transport

    def data_received(self, data):
        resource, func, args, kwargs = pickle.loads(data)
        resource_type = type(self.store.get(resource))
        # print(resource, resource_type, func, args, kwargs)

        if func == "create_resource":
            if not self.store.get(resource):
                self.store[resource] = args[0]
            else:
                log.info("Resource already exists")
            response = pickle.dumps(True)
        elif func == "delete_resource":
            del self.store[resource]
            response = pickle.dumps(True)
        elif func == "list_resource":
            response = pickle.dumps(list(self.store.keys()))
        else:
            if isinstance(func, str):
                func = self._get_builtin_dbfunc_from_string(func, resource_type)
            result = func(self.store.get(resource), *args, **kwargs)
            response = pickle.dumps(result)

        self.transport.write(response)

        # Keep socket open, yield data when using generators.
        self.transport.close()

    @staticmethod
    def _get_builtin_dbfunc_from_string(func: str, resource_type):
        """Get callable function from dbfuncs with function name (str)"""

        functions = {
            method_name: getattr(resource_type, method_name)
            for method_name in dir(resource_type)
            if callable(getattr(resource_type, method_name))
        }  # Get builtin methods for resource_type
        functions.update({})  # TODO: Add registered function
        return functions[func]


async def periodic(store):
    while True:
        # Idéer: Her kan hele resource elementer byttes til en ny versjon laget i
        # en egen prosess, slik at bare bytte må gjøres synkront(blocking)
        # Mulig best med en Queue med tasks
        await asyncio.sleep(1)
        print(
            f"Number of resources {len(store)}, number of elements {sum([len(x) for x in store.values()])}",
            end="\r",
        )
        await asyncio.sleep(9)


async def main():
    store: Dict[str, Union[dict, list, set]] = {
        "default": dict(),
    }  # Dict holding the in-memory data
    register: List[Callable] = []  # List holding registered functions and classes

    loop = asyncio.get_running_loop()
    task = loop.create_task(
        periodic(store)
    )  # Use for healthchecks, cleanups and cache updates, persist db to file?

    socket_filename = "/tmp/edb.socket"
    if Path(socket_filename).is_file():
        Path(socket_filename).unlink()

    server = await loop.create_unix_server(
        lambda: EdbServer(store, register), socket_filename
    )
    log.warning(f"Started")

    async with server:
        await server.serve_forever()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
