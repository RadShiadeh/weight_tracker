from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from pymongo import MongoClient
import string_1
from datetime import datetime
from helper import helpers

app = Flask(__name__)
key = string_1.get_secret_key()
app.secret_key = key

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    
    return wrap

uri = string_1.ret_uri()
client = MongoClient(uri)
db = client["test"]

from users import routes

@app.route('/login/')
def login_page():
    return render_template('login.html')

@app.route('/')
def signup_page():
    return render_template('signup.html')

@app.route('/home/', methods=['GET', 'POST'])
@login_required
def index():
    dates = helpers.generate_dates()
    global all_weights, last_seven, all_weekly_averages

    user_name = session["user"]["username"]
    collection = db["users"]
    user_data = collection.find_one({"username": user_name})

    if user_data:
        all_weights = {w["date"]: [w["weight"][0], w["weight"][1]] for w in user_data["all_weights"]}
        all_weekly_averages = {w["date"]: [w["average"], w["index"]] for w in user_data["weekly_avgs"]}
        last_seven = user_data["last_seven"]
    else:
        print(f"user {user_name} not found")

        
    duplicate = request.args.get('duplicate', 'false')
    if all_weights and all_weekly_averages:
        all_weights, all_weekly_averages, last_seven = helpers.auto_fill_missing_dates(all_weights, all_weekly_averages, last_seven)

    selected_data = 'weekly_averages'
    if request.method == 'POST':
        if 'new_weight' in request.form:
            selected_date = request.form['date']
            all_weight_dates = [datetime.strptime(date, "%Y-%m-%d") for date in all_weights.keys()]
            earliest_entry = min(all_weight_dates)
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            
            new_weight = float(request.form['new_weight'])
            is_duplicate = False

            if earliest_entry > selected_date_obj:
                helpers.auto_fill_prior_dates(all_weights, selected_date, new_weight)
                all_weights = helpers.reorder_indexs(all_weights)
                all_weekly_averages = helpers.update_weekly_averages(all_weights)
            else:
                all_weights, last_seven, all_weekly_averages, is_duplicate = helpers.update_everything(last_seven, new_weight, all_weekly_averages, all_weights, selected_date)

            if is_duplicate:
                helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)
                return redirect(url_for('index', duplicate='true'))
            
            helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)

        elif 'data-select' in request.form:
            selected_data = request.form.get('data-select', 'weekly_averages')
    
    dict_data = {}
    chart_title = ""
    if all_weights and all_weekly_averages:
        if selected_data == 'last_seven' and last_seven:
            dict_data = {date: [value, index] for index, (date, value) in enumerate(last_seven[0]['data'].items(), 1)}
            chart_title = "Last Seven Entries"
        elif selected_data == 'all_weights':
            dict_data = all_weights
            chart_title = "All Weight Entries"
        else:
            dict_data = all_weekly_averages
            chart_title = "Weekly Averages"

    return render_template('index.html', dates=dates, dict_data=dict_data, duplicate=duplicate, chart_title=chart_title, selected_data=selected_data)




if __name__ == "__main__":
    app.run(debug=True)