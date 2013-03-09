#    sostore - SQLite Object Store
#    Copyright (C) 2013 Jeffrey Armstrong 
#                            <jeffrey.armstrong@approximatrix.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sqlite3
import warnings
import json
import collections
import random

_ID_COLUMN = '_id'
_DATA_COLUMN = '_data'

ID_KEY = _ID_COLUMN

ASCENDING  = 'ASC'
DESCENDING = 'DESC'

class Collection():
    def __init__(self, collection, connection=None, db=":memory:"):
        """Initializes access to a collection
        
        Args:
            collection  The collection within the database to use
            
            connection  A valid sqlite3.Connection object, can be None
                        if db is specified
                        
            db          Database filename, unused if connection is
                        specified
        """
        
        if collection is None:
            raise ValueError('A Collection name must be specified')
    
        if connection is not None:
            self.connection = connection
        else:
            self.connection = sqlite3.connect(db, isolation_level=None)
            
        self.collection = collection
        
        self.connection.execute("CREATE TABLE IF NOT EXISTS {0}({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2} TEXT)".format(self.collection, _ID_COLUMN, _DATA_COLUMN))
        self.connection.commit()
        
    def done(self):
        """Closes the connection to the Collection"""
        if self.connection is not None:
            self.connection.close()
        self.connection = None
        
    def get(self, id):
        """Retrieves a dictionary from the Collection
        
        Args:
            id  the id of the dictionary to retrieve
        """
        
        str = self.connection.execute("SELECT {0},{1} FROM {2} WHERE {0}=?".format(_ID_COLUMN, _DATA_COLUMN, self.collection), (id,)).fetchone()
        if str is None or len(str) != 2:
            return None

        d = json.loads(str[1])
        d[_ID_COLUMN] = id
        
        return d
        
    def get_many(self, ids, fields=None):
        """Retrieves multiple dictionaries as a list, possibly with only a subset of dictionary keys
        
        Args:
            ids     A list of database ids to retrieve
            
            fields  The keys from each dictionary to retrieve, 
                    defaults to None (all keys)
        """
        
        entries = []
        for id in ids:
            d = self.get(id)
            if fields is not None:
                for k in d.keys():
                    if not k in fields:
                        del d[k]
            entries.append(d)
            
        return entries
        
    def all(self, fields=None):
        """Retrieves all the dictionaries from the Collection
        
        Args:
            fields  The subset of keys to retrieve for each dictionary, 
                    defaults to None (all keys)
            
        """
        
        entries = []
        
        cursor = self.connection.cursor()
        for row in cursor.execute("SELECT {0},{1} FROM {2}".format(_ID_COLUMN, _DATA_COLUMN, self.collection)):
            toret = json.loads(row[1])
            toret[_ID_COLUMN] = row[0]
            if fields is not None:
                for k in toret.keys():
                    if not k in fields:
                        del toret[k]
            entries.append(toret)

        return entries    

    def _random_id(self):
        """Private random database id generator"""
        while True:
            id = random.randint(1E+6, 1E+9)
            if self.get(id) is None:
                return id

    def _match_value(self, value, check):
        """Private value matching (helps with string<->int comparisons)"""
        if type(value) == type(check):
            return value == check
        elif isinstance(value, int):
            try:
                return value == int(check)
            except ValueError:
                return False
        else:
            return False

    def insert(self, object, randomize=False):
        """Inserts a new dictionary into the Collection
        
        Args:
            object      A dictionary to insert into the Collection
            
            randomize   Randomize the object's id in the Collection, defaults to False
            
        """
            
        if _ID_COLUMN in object:
            if object[_ID_COLUMN] is None:
                del object[_ID_COLUMN]
            else:
                raise ValueError("An object insert was attempted with a non-None id")
                
        str = json.dumps(object)
        cursor = self.connection.cursor()
        if not randomize:
            cursor.execute("INSERT INTO {0}({1}) VALUES(?)".format(self.collection, _DATA_COLUMN), (str,))
        else:
            id = self._random_id()
            cursor.execute("INSERT INTO {0}({1}, {2}) VALUES(?, ?)".format(self.collection, _ID_COLUMN, _DATA_COLUMN), (id, str,))
        self.connection.commit()
        
        object[_ID_COLUMN] = cursor.lastrowid
        return object
        
    def update(self, object):
        """Updates an existing dictionary in the Collection
        
        Args:
            object  A dictionary with a valid "_id" key, which will entirely
                    replace the existing dictionary associated with the id
        """
        
        if not _ID_COLUMN in object.keys():
            raise ValueError('Update called on a nonexistant db record')

        id = object[_ID_COLUMN]
        del object[_ID_COLUMN]
        
        str = json.dumps(object)
        
        self.connection.execute("UPDATE {0} SET {1}=? WHERE {2}=?".format(self.collection, _DATA_COLUMN, _ID_COLUMN), (str, id))
        self.connection.commit()
        
        object[_ID_COLUMN] = id
        
        return object
        
    def remove(self, object_or_id):
        """Removes a dictionary from the Collection
        
        Args:
            object_or_id    Either an object with a valid "_id" key 
                            or the object's id itself
        """
        
        deletion = object_or_id
        if isinstance(deletion, dict):
            deletion = object_or_id[_ID_COLUMN]

        self.connection.execute("DELETE FROM {0} WHERE {1}=?".format(self.collection, _ID_COLUMN), (deletion,))
        self.connection.commit()
        
    def find_one(self, field, value):
        """Finds a single dictionary in the Collection that has a matching value for a specified key (field).
        
        Args:
            field   The dictionary key being specified in the value
                    argument
                    
            value   The value to search for in the specified dictionary 
                    key
                    
        Notes:
            See Collection.find_field for more information on behavior
        """
        
        id = self.find_field(field, value)
        
        if len(id) == 0:
            return None
        else:
            return self.get(id[0])
    
    def random_entries(self, count=1):
        """Retrieve random dictionaries from the Collection
        
        Args:
            count   The number of random dictionaries to retrieve, defaults to 1
        """
        
        entries = []
        cursor = self.connection.cursor()
        for row in cursor.execute("SELECT * FROM {0} ORDER BY RANDOM() LIMIT {1};".format(self.collection, count)):
            toret = json.loads(row[1])
            toret[_ID_COLUMN] = row[0]
            entries.append(toret)

        return entries    
    
    def random_entry(self):
        """Retrieve a single random dictionary from the Collection"""
        
        entries = self.random_entries(1)
        if len(entries) == 1:
            return entries[0]
        
        return None
    
    def find_field(self, field, value):
        """Finds id's of dictionaries in the Collection that have a matching value for a specified key (field).
        
        Args:
            field   The dictionary key being specified in the value
                    argument
                    
            value   The value to search for in the specified dictionary 
                    key
                    
        Notes:
            If the value of the field in the dictionary is a list, the routine
            will search each element of the list for a matching value.  If the
            value is specified as a string and the value in the dictionary is
            an integer, a conversion will be attempted during matching.
        """
        
        fieldsearch = self.all(fields=('_id', field))
        matching = []
        for d in fieldsearch:
            if isinstance(d[field], collections.Iterable) and not isinstance(d[field], str):
                if value in d[field]:
                    matching.append(d['_id'])
            elif d[field] == value:
                matching.append(d['_id'])
                
        return matching
