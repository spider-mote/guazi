import pymongo

class Handle_mongo_guazi(object):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        self.client.admin.authenticate('root', 'abc123456')
        self.db = self.client['db_guazi']

    # 存储task
    def save_task(self,collection_name,task):
        print('当前存储的task为%s:'%task)
        collection = self.db[collection_name]
        task = dict(task)
        collection.insert_one(task)

    # 获取task
    def get_task(self,collection_name):
        collection = self.db[collection_name]
        task = collection.find_one_and_delete({})
        return task

    # 存储汽车数据
    def save_data(self,collection_name,data):
        print('当前存储的数据为%s:' % data)
        collection = self.db[collection_name]
        data = dict(data)
        collection.update({'car_id':data['car_id']},data,True)


mongo = Handle_mongo_guazi()