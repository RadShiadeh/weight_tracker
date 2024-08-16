import mongoengine as me
import bcrypt
import mongoengine as me
# testing imports
# from gen_data import gen_data
# from pymongo import MongoClient
# import string_1
# import os

class AllWeights(me.EmbeddedDocument):
    date = me.StringField(required=True)
    weight = me.FloatField(required=True)
    index = me.IntField(required=True)

    meta = {
        'collection': 'all_weights',
        'ordering': ['-date'],
        'indexes': ['date', 'weight', 'index']
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
    # # create a new user
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
    #------------------------------------------------------------------------------------------------------------------------------------------------------------

    #update an existing user
    # uri = string_1.ret_uri()
    # client = MongoClient(uri)
    # db = client["Flask_weight_tracker"]
    # collection = db["users"]
    # last_seven, all_weights, week_avg = gen_data()

    # me.connect(host=uri)

    # existing_user = User.objects(username="RadShiadeh").first()
    # if existing_user:
    #     existing_user.all_weights = [
    #         AllWeights(date=d, weight=w[0], index=w[1])
    #         for d, w in all_weights.items()
    #     ]

    #     existing_user.weekly_avgs = [
    #         WeeklyAverages(date=d, average=v[0], index=v[1])
    #         for d, v in week_avg.items()
    #     ]

    #     existing_user.last_seven = [
    #         LastSeven(data=last_seven[0]["data"], index=last_seven[0]["index"])
    #     ]

    #     existing_user.save()
    # else:
    #     print(f"User 'RadShiadeh' not found in the database.")




# if __name__ == "__main__":
#     main()