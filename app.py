from datetime import datetime, timedelta
import json
import math
from flask import Flask, render_template, request, redirect, url_for
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
import base64
import os
import csv
import shutil

app = Flask(__name__)

matplotlib.use('Agg')

def read_weights_from_csv(csv_db: str):
    weights: list[float] = [] 
    if os.path.exists(csv_db):
        with open(csv_db, "r") as f:
            rows = csv.reader(f)
            for r in rows:
                if r:
                    weights.append(float(r[0]))
    return weights

def write_json(file_path: str, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def read_json(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# use for last_seven and weekly_averages 
def update_csv(file: str, weights: list[float]):
    os.remove(file)
    with open(file, mode='a', newline='') as f:
        writer = csv.writer(f)
        for w in weights:
            writer.writerow([w])

def backup(source, target):
    shutil.copyfile(source, target)

def x_labels(all_weight) -> list[str]:
    dates: list[str] = list(all_weight.keys())
    res: list[str] = ["" for _ in range(len(dates) // 7)]
    index: int = 0
    for i in range(len(res)):
        start = dates[index]
        while index < len(dates) and (index + 1) % 7 != 0:
            index += 1

        if (index+1) % 7 == 0:
            end = dates[index]
            res[i] = f"{start} to {end}"
            index += 1
    
    if len(res) != math.ceil(len(dates) / 7):
        res.append(f"{dates[index]} to now")

    return res



def plot_weekly_weights(weekly_averages, all_weights, path: str, backup_path: str):
    x: list[str] = []
    y: list[float] = []

    for k, v in weekly_averages.items():
        x.append(k)
        y.append(v)
    

    # weekly_averages_json_dict = {}
    # for i in range(len(x)):
    #     weekly_averages_json_dict[x[i]] = weekly_averages.values()[i]

    # write_json(path, weekly_averages_json_dict)
    # backup(path, backup_path)

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
    all_weights_c[selected_date] = new_weight

    weekly_avg_keys: list[str] = []
    for k in weekly_average.keys():
        weekly_avg_keys.append(k)

    end_key = weekly_avg_keys[-1]

    if len(weekly_weights) == 7:
        average: float = 0
        for k in weekly_weights.values():
            average += k
        average = average / 7
        weekly_average[end_key] = average

        weekly_weights = {}
        weekly_weights[selected_date] = new_weight

        weekly_average[f"{selected_date} to now"] = new_weight
    else:
        weekly_weights[selected_date] = new_weight
        average: float = 0
        for k in weekly_weights.values():
            average += k
        average = average / len(weekly_weights.keys())
        weekly_average[end_key] = average

    write_json(all_weights_json, all_weights_c)
    write_json(last_seven_json, weekly_weights)
    write_json(weekly_averages_json, weekly_average)

    backup(all_weights_json, all_weights_backup)
    backup(last_seven_json, last_seven_backup)
    backup(weekly_averages_json, weekly_averages_json_backup)
    
    return all_weights_c, weekly_weights, weekly_average


def generate_dates():
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

all_weights_json: str = "./db/all_weights_db.json"
weekly_averages_csv: str = "./db/weekly_averages_db.csv"
last_seven_json: str = "./db/last_seven_db.json"
weekly_averages_json = "./db/weekly_averages_db.json"

all_weights_backup: str = "../weight_tracker_db_backup/all_weights_db.csv"
weekly_averages_csv_backup: str = "../weight_tracker_db_backup/weekly_averages_db.csv"
last_seven_backup: str = "../weight_tracker_db_backup/last_seven_db.json"
weekly_averages_json_backup: str = "../weight_tracker_db_backup/weekly_averages_db.json"

all_weights = read_json(all_weights_json)
last_seven = read_json(last_seven_json)
all_weekly_averages = read_json(weekly_averages_json)

@app.route('/', methods=['GET', 'POST'])
def index():
    dates = generate_dates()
    global all_weights, last_seven, all_weekly_averages
    if request.method == 'POST':
        selected_date = request.form['date']
        new_weight = float(request.form['new_weight'])
        all_weights, last_seven, all_weekly_averages = update_everything(last_seven, new_weight, all_weekly_averages, all_weights, selected_date)
        return redirect(url_for('index'))

    
    plot_url = plot_weekly_weights(all_weekly_averages, all_weights, weekly_averages_json, weekly_averages_json_backup)
    return render_template('index.html', plot_url=plot_url, dates=dates)

if __name__ == "__main__":
    app.run(debug=True)