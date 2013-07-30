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

class CollectionException(Exception):
    """A catch-all exception for sostore exceptions"""
    
    def __init__(self, collection, msg):
        Exception.__init__(self, msg)
        self.collection = collection
    
class RandomIdException(CollectionException):
    """Thrown when a random id was requested, but failed to be calcuated"""
    
    def __init__(self, collection):
        CollectionException.__init__(self, 
                                     collection, 
                                     "A random row id could not be calculated in a reasonable amount of tries")
                                     
class ConnectionException(CollectionException):
    """Thrown when an action is attempted with a collection that has no connection"""
    
    def __init__(self, collection):
        CollectionException.__init__(self, 
                                     collection, 
                                     "The collection '{0}' no longer has a database connection".format(collection))