import os
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

class AllWeights:
    def __init__(self, date, weight: float) -> None:
        self.date: str = date
        self.weight: float = weight


class WeeklyAverages:
    def __init__(self, date, average: float, index: int) -> None:
        self.date = date
        self.average = average
        self.index = index

class Users:
    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password_hash = self.set_password(password)
        self.all_weights = []
        self.weekly_averages = []

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_weight(self, date, weight):
        self.all_weights.append(AllWeights(date, weight))

    def add_weekly_average(self, date_range, values):
        new_index = 1
        if self.weekly_averages:
            last_obj = self.weekly_averages[-1]
            last_index = last_obj.index
            new_index = last_index + 1
        
        self.weekly_averages.append(WeeklyAverages(date_range, values, new_index))

    def to_dict(self):
        all_w = {}

        for obj in self.all_weights:
            all_w[obj.date] = obj.weight

        all_w_avg = {}

        for obj in self.weekly_averages:
            all_w_avg[obj.date] = [obj.average, obj.index]

        return {
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'all_weights': all_w,
            'weekly_averages': all_w_avg
        }



#testing
all_weights = {
    "2024-06-14": 87.7,
    "2024-06-15": 88.0,
    "2024-06-16": 88.2,
    "2024-06-17": 88.0,
    "2024-06-18": 87.9,
    "2024-06-19": 87.5,
    "2024-06-20": 87.9,
    "2024-06-21": 87.5,
    "2024-06-22": 87.9,
    "2024-06-23": 88.0,
    "2024-06-24": 87.9,
    "2024-06-25": 88.4,
    "2024-06-26": 88.2,
    "2024-06-27": 87.9,
    "2024-06-28": 87.9,
    "2024-06-29": 87.9,
    "2024-06-30": 88.0,
    "2024-07-01": 88.2,
    "2024-08-02": 89.0,
    "2024-07-03": 89.0,
    "2024-07-04": 89.0,
    "2024-07-05": 88.0,
    "2024-07-06": 88.7,
    "2024-07-07": 88.0,
    "2024-07-08": 87.9,
    "2024-07-09": 88.0,
    "2024-07-10": 88.5,
    "2024-07-11": 88.3,
    "2024-07-12": 88.5,
    "2024-07-13": 88.0,
    "2024-07-14": 88.9,
    "2024-07-15": 89.0,
    "2024-07-16": 87.9,
    "2024-07-17": 88.0,
    "2024-07-18": 88.0,
    "2024-07-19": 88.3
}

week_avg = {
    "2024-06-14 to 2024-06-20": [
        87.88571428571429,
        1
    ],
    "2024-06-21 to 2024-06-27": [
        87.97142857142856,
        2
    ],
    "2024-06-28 to 2024-07-04": [
        88.42857142857143,
        3
    ],
    "2024-07-05 to 2024-07-11": [
        88.2,
        4
    ],
    "2024-07-12 to 2024-07-18": [
        88.32857142857142,
        5
    ],
    "2024-07-19 to now": [
        88.3,
        6
    ]
}




user = Users("Rad", "rad123", "gradmehr0@...", "123")
for d, w in all_weights.items():
    user.add_weight(d, w)

for d, w in week_avg.items():
    user.add_weekly_average(d, w[0])


uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client["Flask_weight_tracker"]
db.users.insert_one(user.to_dict())