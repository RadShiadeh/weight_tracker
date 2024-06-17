from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
import base64
import os
import csv

app = Flask(__name__)

all_weights_csv: str = "all_weights_db.csv"
weekly_averages_csv: str = "weekly_averages_db.csv"
last_seven_csv: str = "last_seven_db.csv"

def read_weights_from_csv(csv_db: str):
    weights: list[float] = [] 
    if os.path.exists(csv_db):
        with open(csv_db, "r") as f:
            rows = csv.readlines(f)
            for r in rows:
                if r:
                    weights.append(float(r[0]))
    return weights

def write_weights_to_csv(csv_file: str, weight: float):
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([weight])

# use for last_seven and weekly_averages 
def update_csv(file: str, weights: list[float]):
    with open(file, mode='a', newline='') as f:
        writer = csv.writer(f)
        for w in weights:
            writer.writerow([w])



all_weights: list[float] = read_weights_from_csv(all_weights_csv)
all_weekly_averages: list[int] = read_weights_from_csv(weekly_averages_csv)
last_seven: list[float] = read_weights_from_csv(last_seven_csv)


def plot_weekly_weights(weekly_averages: list[int]):
    x: list[int] = []
    for i in range(len(weekly_averages)):
        x.append(i+1)

    fig, ax = plt.subplots()

    ax.plot(x, weekly_averages, marker ='o', linestyle='-', color='r')

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(1, len(x)) 

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

def update_everything(weekly_weights: list[int], new_weight: int, weekly_average: list[int]):
    if len(weekly_weights) == 7:
        average: int = sum(weekly_weights) / 7
        weekly_average[-1] = average

        weekly_weights = []
        weekly_weights.append(new_weight)

        weekly_average.append(new_weight)
    else:
        weekly_weights.append(new_weight)
        average: int = sum(weekly_weights) / len(weekly_weights)
        weekly_average[-1] = average

    update_csv(last_seven_csv, last_seven)
    update_csv(weekly_averages_csv, weekly_average)
    
    return weekly_weights, weekly_average

@app.route('/', methods=['GET', 'POST'])
def index():
    global all_weights, last_seven, all_weekly_averages
    if request.method == 'POST':
        new_weight = float(request.form['new_weight'])
        last_seven, all_weekly_averages = update_everything(last_seven, new_weight, all_weekly_averages)
        write_weights_to_csv(all_weights, new_weight)
        return redirect(url_for('index'))

    plot_url = plot_weekly_weights(all_weekly_averages)
    return render_template('index.html', plot_url=plot_url)

if __name__ == "__main__":
    app.run(debug=True)