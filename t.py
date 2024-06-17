import csv

csv_file_all = 'all_weights_db.csv'
csv_weekly = 'weekly_averages_db.csv'
last_seven = 'last_seven_db.csv'

# Initial weights
initial_weights = [87.7, 88, 88.2]
average = sum(initial_weights) / len(initial_weights)

# Write initial weights to CSV
with open(csv_file_all, mode='w', newline='') as file:
    writer = csv.writer(file)
    for weight in initial_weights:
        writer.writerow([weight])

with open(csv_weekly, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([average])

with open(last_seven, mode='w', newline='') as file:
    writer = csv.writer(file)
    for weight in initial_weights:
        writer.writerow([weight])

print(f"CSV file '{csv_file_all}' initialized with weights: {initial_weights}")
