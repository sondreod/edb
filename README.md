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

test = Resource("test").create(dict()) #  Create a "test" dict resource 
test.add(("key_to_add", "vaule_to_add"))


```

##### FastAPI

```python
class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def run_main(self):
        while True:
            await asyncio.sleep(0.1)
            self.value += 1

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())
```