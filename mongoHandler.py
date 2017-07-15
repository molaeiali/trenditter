from pymongo import MongoClient
from bson.objectid import ObjectId

class MongoHandler(object):

    _connString = None
    _connection = None
    _db = None
    _collection = None

    def get_connection(self, connString):
        if self._connection is None:
            self._connection = MongoClient(connString)

        return self._connection

    def set_db_and_collection(self, db_name, collection_name):
        conn = self.get_connection(self._connString)
        self._db = conn[db_name]
        self._collection = self._db[collection_name]

    def insert(self, data):
        collection = self._collection
        ret = collection.insert_one(data)
        return ret.inserted_id

    def find(self, query={}):
        collection = self._collection
        ret = collection.find(query)

    def findById(self, id):
        collection = self._collection
        ret = collection.find_one({'_id': ObjectId(id)})
        return ret

    def __init__(self, connString, db_name, collection_name):
        self._connString = connString
        self.get_connection(connString)
        self.set_db_and_collection(db_name, collection_name)
