from datetime import datetime, timedelta
import json
from flask import Flask, render_template, request, redirect, url_for
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
import base64
import os
import shutil

app = Flask(__name__)

matplotlib.use('Agg')

def write_json(file_path: str, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def read_json(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def backup(source, target):
    shutil.copyfile(source, target)

def plot_weekly_weights(weekly_averages):
    y: list[float] = []
    x: list[int] = []
    for _, v in weekly_averages.items():
        y.append(v[0])
        x.append(v[1])

    fig, ax = plt.subplots()

    ax.plot(x, y, marker ='o', linestyle='-', color='r')

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    ymin: float = min(y) - 0.5
    ymax: float = max(y) + 0.5
    ax.set_ylim([ymin, ymax])

    ax.set_xlabel('week')
    ax.set_ylabel('Weekly Weight')
    ax.set_title('Weekly Weight Averages from June 14th')
    ax.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

def update_everything(weekly_weights, new_weight: int, weekly_average, all_weights_c, selected_date):
    if selected_date in all_weights_c.keys():
        return all_weights_c, weekly_weights, weekly_average, True
    
    all_weights_c[selected_date] = new_weight

    weekly_avg_keys: list[str] = []
    for k in weekly_average.keys():
        weekly_avg_keys.append(k)

    end_key = weekly_avg_keys[-1]
    end_week_index = weekly_average[end_key][1]

    if len(weekly_weights) == 7:
        average: float = 0
        for k in weekly_weights.values():
            average += k
        average = average / 7

        start_d: str = ""
        all_weights_ks: list[str] = []
        for k in all_weights_c.keys():
            all_weights_ks.append(k)
        
        end_d: str = all_weights_ks[len(all_weights_ks) - 2]

        for c in end_key:
            if c == " ":
                break
            start_d += c

        del weekly_average[end_key]
        end_key = f"{start_d} to {end_d}"
        weekly_average[end_key] = [average, end_week_index]

        weekly_weights = {}
        weekly_weights[selected_date] = new_weight

        weekly_average[f"{selected_date} to now"] = [new_weight, end_week_index+1]
    else:
        weekly_weights[selected_date] = new_weight
        average: float = 0
        for k in weekly_weights.values():
            average += k
        average = average / len(weekly_weights.keys())
        weekly_average[end_key] = [average, end_week_index]
    

    write_json(all_weights_json, all_weights_c)
    write_json(last_seven_json, weekly_weights)
    write_json(weekly_averages_json, weekly_average)

    backup(all_weights_json, all_weights_backup)
    backup(last_seven_json, last_seven_backup)
    backup(weekly_averages_json, weekly_averages_json_backup)
    
    return all_weights_c, weekly_weights, weekly_average, False


def generate_dates():
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

all_weights_json: str = "./db/all_weights_db.json"
weekly_averages_csv: str = "./db/weekly_averages_db.csv"
last_seven_json: str = "./db/last_seven_db.json"
weekly_averages_json = "./db/weekly_averages_db.json"

all_weights_backup: str = "../weight_tracker_db_backup/all_weights_db.json"
last_seven_backup: str = "../weight_tracker_db_backup/last_seven_db.json"
weekly_averages_json_backup: str = "../weight_tracker_db_backup/weekly_averages_db.json"

all_weights = read_json(all_weights_json)
last_seven = read_json(last_seven_json)
all_weekly_averages = read_json(weekly_averages_json)

@app.route('/', methods=['GET', 'POST'])
def index():
    dates = generate_dates()
    global all_weights, last_seven, all_weekly_averages
    duplicate = request.args.get('duplicate', 'false')

    if request.method == 'POST':
        selected_date = request.form['date']
        new_weight = float(request.form['new_weight'])
        all_weights, last_seven, all_weekly_averages, is_duplicate = update_everything(last_seven, new_weight, all_weekly_averages, all_weights, selected_date)

        if is_duplicate:
            return redirect(url_for('index', duplicate='true'))
        
        return redirect(url_for('index'))
    
    plot_url = plot_weekly_weights(all_weekly_averages)
    return render_template('index.html', plot_url=plot_url, dates=dates, dict_data=all_weekly_averages, duplicate=duplicate)

if __name__ == "__main__":
    app.run(debug=True)