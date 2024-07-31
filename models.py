import os
import mongoengine as me
import bcrypt
from pymongo import MongoClient
import string_1
import mongoengine as me

class AllWeights(me.EmbeddedDocument):
    date = me.StringField(required=True)
    weight = me.FloatField(required=True)

    meta = {
        'collection': 'all_weights',
        'ordering': ['-date'],
        'indexes': ['date', 'weight']
    }

class LastSeven(me.EmbeddedDocument):
    data = me.DictField(required=True)
    index = me.IntField(required=True)

    meta = {
        'collection' : 'last_seven',
        'ordering': ['index']
    }

class WeeklyAverages(me.EmbeddedDocument):
    date = me.StringField(required=True)
    average = me.FloatField(required=True)
    index = me.IntField(required=True)

    meta = {
        'collection': 'weekly_average',
        'ordering': ['-index'],
    }

class User(me.Document):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    all_weights = me.ListField(me.EmbeddedDocumentField(AllWeights), default = [])
    weekly_avgs = me.ListField(me.EmbeddedDocumentField(WeeklyAverages), default = [])
    last_seven = me.ListField(me.EmbeddedDocumentField(LastSeven), default = [])

    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }

    def clean(self):
        if self._created or self._changed_fields:
            self.password = bcrypt.hashpw(str.encode(self.password, 'utf-8'), bcrypt.gensalt()).decode('utf-8')






# For testing use
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# def main():
#     # uri = string_1.ret_uri()
#     # client = MongoClient(uri)
#     # db = client["Flask_weight_tracker"]
#     # collection = db["users"]
#     # last_seven, all_weights, week_avg = gen_data()

#     # me.connect(host=uri)
    

#     # new_user = User(
#     #     username="Rad",
#     #     email="radurfakelmao@gmail.com",
#     #     password="09116393920rR",
#     #     all_weights=[AllWeights(date=d, weight=w) for d, w in all_weights.items()],
#     #     weekly_avgs=[WeeklyAverages(date=d, average=v[0], index=v[1]) for d, v in week_avg.items()],
#     #     last_seven=[LastSeven(data=last_seven[0], index=last_seven[1])]
#     # )

#     # new_user.save()
    
#     # user_data = collection.find_one({"username" : "RadShiadeh"})
#     # if user_data:
#     #     print("")
#     # else:
#     #     print(404)
#     pass




# if __name__ == "__main__":
#     main()