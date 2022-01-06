from time import time, sleep
from dataclasses import dataclass, field
from edb import Resource


users = Resource("users").create(list())


for i in range(3):
    user = {
        "id": i,
        "name": 'Trolol Guy',
    }
    users.add(user)

print(len(users))

print(users[1])

print(Resource("test").list())
