import pymongo
from datetime import  datetime
class app_log:
    def __init__(self, username, password):
        self.username=username
        self.password=password
        self.dbName='application_logging'
        self.collectionName='logger'
        self.client = pymongo.MongoClient(f"mongodb+srv://{self.username}:{self.password}@image-scrapper-cluster.v5iga.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    def log(self, tag, message):
        timestamp=str(datetime.now())
        database = self.client[self.dbName]
        collection = database[self.collectionName]
        data_to_insert={'timestamp':timestamp, 'tag':tag, 'message':message}
        collection.insert_one(data_to_insert)


