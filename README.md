# EDB

A simple and flexible in-memory database written in Python.
Can be used as a simple keyvalue store, or you can query the in-memory data at runtime with a custom python function.


### Installation
```bash
pip install edb
```

### Usage

##### Generic
```python
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



```

##### FastAPI

```python

# Not finished
class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def run_main(self):
        while True:
            self.value = 1

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(edb.run())
# /Not finished

```