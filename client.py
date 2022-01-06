from time import time
from edb import query, Resource, get, key_startswith, add


t = time()

"""
print(query("test", "key_startswith", "look"))
query("test", "add", ("seff", "kek"))
query("test", "add", ("seff", "lolz"))
query("test", "add", ("seff", "rofl"))
"""

print(Resource("test2").create(dict()))
print(Resource("test2").add((str(time()), time())))
#test2 = Memdb("test2")
#print(test2.add(("ob", "fgai")))
print(Resource("test2").list()[1])

print(time() - t)
