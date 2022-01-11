from edb import Resource
import json

# Create resources on in the database. Does nothing if they already exists.
# For convinience; create() returns the Resource object.
my_list: list = Resource("my_list").create(list())
my_dictionary: dict = Resource("my_dictionary").create(dict())


# Dictionary
my_dictionary["a_new_key"] = "my_value"

print(
    my_dictionary["a_new_key"],  # This returns as expected 'my_value'
    len(my_dictionary),  # Returns 1 (there is one key in the dictionary)
)

my_dictionary.delete()  # This delete the resource on the server, returns None


# List
for i in "abcdefghij":
    my_list.append(i)

print(
    len(my_list),  # Returns 10
    my_list[4],  # Returns e
    my_list[3:],  # Returns ['d', 'e', 'f', 'g', 'h', 'i', 'j']
)

# Updating a resource when the elements point to a collection type.
# For now you will have to get the element, update it localy and then update the database with the new data

new_list = Resource("new_list").create(list())
new_list.append([1, 2, 3])
print(new_list)  # Returns [[1, 2, 3]]

# Extend the element
l = new_list[0]  # Create a local copy
l.extend([4, 5, 6])  # Update the element localy
new_list[0] = l  # Update the database

print(new_list)  # Returns [[1, 2, 3, 4, 5, 6]]


#  Example with dictionary in list resource
users = Resource("users").create(list())
for i in range(3):
    user = {
        "id": i,
        "name": "Trololo Guy",
    }
    users.append(user)

print(
    users
)  # [{'id': 0, 'name': 'Trololo Guy'}, {'id': 1, 'name': 'Trololo Guy'}, {'id': 2, 'name': 'Trololo Guy'}]
