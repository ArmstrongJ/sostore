sostore
=======

SQLite Object Store - An absurdly simple object "database" for Python

sostore is a straightforward storage engine for storing and retrieving 
dictionaries from an SQLite database.  Much of the terminology is taken
from MongoDB as this engine was originally designed to replace a PyMongo
implementation.

This library may seem trivial because it very much is.  However, some 
others may need a super-lightweight dictionary store.  Linking of 
objects within the database is not supported unless explicitly handled 
by the developer.

sostore is almost certainly not performant.  It can be thread-safe as 
long as Collection objects aren't passed around between threads as they
contain sqlite3.Connection objects.

Requirements
------------

sostore should work with Python 2.6 and higher, including Python 3.x. 

Usage
-----

__Inserting__
<pre>
>>> import sostore
>>> collection = sostore.Collection("peoples")
>>> d = {"name": "Margaux LaFleur", "hair color":"black"}
>>> d = collection.insert(d)
>>>
</pre>

__Retrieval__
<pre>
>>> d = collection.get(1)
>>> print(d)
{'_id': 1, 'name': 'Margaux LaFleur', 'hair color': 'black'}
>>>
</pre>

__Retrieval by Field__
<pre>
>>> d = collection.find_one("name", "Margaux LaFleur")
>>> print(d)
{'_id': 1, 'name': 'Margaux LaFleur', 'hair color': 'black'}
>>> d = collection.find_one("occupation", "magician")
>>> print(d)
None
>>>
</pre>

__Cleanup__
<pre>
>>> collection.done()
>>>
</pre>

__Updating__
<pre>
>>> d = collection.get(1)
>>> d['occupation'] = "witch"
>>> collection.update(d)
>>>
</pre>

Behind the Scenes
-----------------

sostore uses a ridiculously simple and naive backend.  Each Collection 
the user creates generates a new table in the database with the name of
that Collection as the name of the table.  The table will have two 
columns, "_id" and "_data."  The names of these columns, however, are 
not particularly important to the user.

The "_id" column is an auto-incrementing primary key (unless a random id
setting is enabled).  The "_data" column is a text blob that contains 
the JSON-ified Python dictionary to be stored *without the _id key*.  
The "_id" key is always removed on store and added back into the 
dictionary upon retrieval to ensure consistency.

The SQLite commands within this library use safe prepare statements and,
therefore, can be assumed safe from SQLite injection attacks.  However,
the Collection names are *not* safe.  You should not allow dirty 
Collection names to be specified under any circumstance.

That's about all there is to it.

License
-------

sostore - SQLite Object Store
Copyright (C) 2013 Jeffrey Armstrong 
                        <jeffrey.armstrong@approximatrix.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

