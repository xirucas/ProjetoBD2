import pymongo
from decouple import config

mongoConnection= pymongo.MongoClient(config("MONGODB_URL"))[config("MONGODB_DB")]

