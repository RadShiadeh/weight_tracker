from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from pymongo import MongoClient
import string_1
from datetime import datetime, timedelta
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
    all_weights, last_seven, all_weekly_averages = {}, {}, {}

    user_name = session["user"]["username"]
    collection = db["users"]
    user_data = collection.find_one({"username": user_name})

    if user_data:
        all_weights = {w["date"]: [w["weight"][0], w["weight"][1]] for w in user_data["all_weights"]}
        all_weekly_averages = {w["date"]: [w["average"], w["index"]] for w in user_data["weekly_avgs"]}
        last_seven = user_data["last_seven"]
    else:
        return redirect(url_for('/', sign_in="true"))

    duplicate = request.args.get('duplicate', 'false')
    gap = request.args.get('gap', 'false')
    alert_ = request.args.get('alert_', 'false')
    auto_fill = request.args.get('auto_fill', 'false')

    all_weight_dates = []
    earliest_entry = ""
    latest_entry = ""
    session["start_key"] = request.form.get('plot-from', "")
    session["end_key"] = request.form.get('plot-to', "")

    if "nw_dup" not in session.keys():
        session["nw_dup"] = 0
    
    if "date_dup" not in session.keys():
        session["date_dup"] = ""

    if all_weights and all_weekly_averages:
        all_weights, all_weekly_averages, last_seven = helpers.auto_fill_missing_dates(all_weights, all_weekly_averages, last_seven)
        all_weight_dates = [datetime.strptime(date, "%Y-%m-%d") for date in all_weights.keys()]
        earliest_entry = min(all_weight_dates)
        latest_entry = max(all_weight_dates)
        session["start_key"] = request.form.get('plot-from', earliest_entry.strftime('%Y-%m-%d'))
        session["end_key"] = request.form.get('plot-to', latest_entry.strftime('%Y-%m-%d'))


    if request.method == 'POST':
        alert_ = False
        if 'date_del' in request.form:
            date_to_delete = request.form['date_del']
            all_weights, all_weekly_averages, last_seven, alert_ = helpers.delete_date(all_weights, all_weekly_averages, last_seven, date_to_delete)
            helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)

            if alert_:
                return redirect(url_for('index', alert_='true'))
            else:
                return redirect(url_for('index'))

        if 'new_weight' in request.form:
            selected_date = request.form['date']
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            day_before = selected_date_obj - timedelta(days=1)
            
            new_weight = float(request.form['new_weight'])
            is_duplicate = False
            gap = False
            auto_fill = False

            if all_weight_dates and earliest_entry > selected_date_obj:
                auto_fill = helpers.auto_fill_prior_dates(all_weights, selected_date, new_weight)
                all_weights = helpers.reorder_indexs(all_weights)
                all_weekly_averages = helpers.update_weekly_averages(all_weights)
                last_seven = helpers.update_last_seven(last_seven, all_weights)
                helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)

            elif all_weight_dates and latest_entry < day_before:
                all_weights, last_seven, all_weekly_averages, gap = helpers.fill_gaps(all_weights, last_seven, all_weekly_averages, latest_entry, new_weight, day_before)
                helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)

            elif not all_weight_dates: #new user
                all_weights, last_seven, all_weekly_averages, is_duplicate = helpers.update_local_enteries(last_seven, new_weight, all_weekly_averages, all_weights, selected_date)
                helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)
            
            else: #duplicate weight
                all_weights, last_seven, all_weekly_averages, is_duplicate = helpers.update_local_enteries(last_seven, new_weight, all_weekly_averages, all_weights, selected_date)

            if is_duplicate:
                session["date_dup"] = selected_date
                session["nw_dup"] = new_weight
                return redirect(url_for('index', duplicate='true', new_weight=session["nw_dup"], date=session["date_dup"]))
            
            if gap:
                return redirect(url_for('index', gap='true'))
            
            if alert_:
                return redirect(url_for('index', alert_='true'))
            
            if auto_fill:
                return redirect(url_for('index', auto_fill='true'))

        elif 'data-select' in request.form:
            session["selected_plot_data"] = request.form.get('data-select', 'weekly_averages')

    if all_weight_dates:
        session["start_key"] = request.form.get('plot-from', earliest_entry.strftime('%Y-%m-%d'))
        session["end_key"] = request.form.get('plot-to', latest_entry.strftime('%Y-%m-%d'))
    else:
        session["start_key"] = 1
        session["end_key"] = 1

    if all_weights and all_weekly_averages:
        if session["selected_plot_data"] == 'last_seven' and last_seven:
            session["data"] = {date: [value, index] for index, (date, value) in enumerate(last_seven[0]['data'].items(), 1)}
            session["chart_title"] = "Last Seven Entries"
        elif session["selected_plot_data"] == 'all_weights':
            session["data"] = all_weights
            session["chart_title"] = "All Entries"
        else:
            start_index = session["start_key"]
            end_index = session["end_key"]
            for d, w in all_weekly_averages.items():
                if str(w[1]) == start_index:
                    session["start_key"] = d
                elif str(w[1]) == end_index:
                    session["end_key"] = d
                    break
                
            session["data"] = all_weekly_averages
            session["chart_title"] = "Weekly Averages"


    return render_template(
        'index.html', 
        dates=dates, 
        dict_data=session["data"], 
        duplicate=duplicate, 
        chart_title=session["chart_title"], 
        selected_data=session["selected_plot_data"], 
        alert_=alert_, 
        gap=gap, 
        start_key=session["start_key"], 
        end_key=session["end_key"],
        sign_in="false",
        auto_fill=auto_fill,
        new_weight=session["nw_dup"],
        date=session["date_dup"]
    )




if __name__ == "__main__":
    app.run(debug=True)