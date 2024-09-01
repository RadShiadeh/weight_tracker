from collections import defaultdict
from datetime import datetime, timedelta


def update_local_enteries(last_seven, new_weight: float, weekly_average, all_weights_c, selected_date):
    new_weight = float("{:.3f}".format(new_weight))
    if not weekly_average:
        k = str(selected_date) + " to " + "now"
        weekly_average[k] = [new_weight, 1]
        all_weights_c[selected_date] = [new_weight, 1]
        last_seven = [{'data': {selected_date: new_weight}, 'index': 1}]
        return all_weights_c, last_seven, weekly_average, False

    duplicate = False
    val = [new_weight, 0]
    old_weight_entry = new_weight

    if selected_date in all_weights_c.keys():
        i = all_weights_c[selected_date][1]
        old_weight_entry = all_weights_c[selected_date][0]
        val = [new_weight, i]
        duplicate = True
    
    all_weights_c[selected_date] = val

    if not duplicate:
        weekly_avg_keys: list[str] = []
        for k in weekly_average.keys():
            weekly_avg_keys.append(k)
    
        end_key = weekly_avg_keys[-1]
        end_week_index = weekly_average[end_key][1]

        if len(last_seven[0]['data']) == 7:
            average: float = 0
            for k in last_seven[0]['data'].values():
                average += k
            average = average / 7
            average = float("{:.3f}".format(average))

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

            last_seven = [{'data': {}, 'index': last_seven[0]['index'] + 1}]
            last_seven[0]['data'][selected_date] = new_weight

            weekly_average[f"{selected_date} to now"] = [new_weight, int(end_week_index)+1]
            all_weights_c[selected_date][1] = end_week_index+1
        else:
            last_seven[0]['data'][selected_date] = new_weight
            average: float = 0
            for k in last_seven[0]['data'].values():
                average += k

            average = average / len(last_seven[0]['data'].keys())
            average = float("{:.3f}".format(average))
            weekly_average[end_key] = [average, int(end_week_index)]
            all_weights_c[selected_date][1] = end_week_index
    else:
        index = val[1]
        key = ""
        for k, v in weekly_average.items():
            if v[1] == index:
                key = k
                break
        
        pre_average = weekly_average[key][0]
        post_average = 0
        
        if selected_date in last_seven[0]['data'].keys():
            last_seven[0]['data'][selected_date] = new_weight
            len_last_seven = len(last_seven[0]['data'])
            post_average = ( ( (pre_average * len_last_seven) - old_weight_entry) + new_weight ) / len_last_seven
        else:
            post_average = ( ( (pre_average * 7) - old_weight_entry) + new_weight ) / 7

        post_average = float("{:.3f}".format(post_average))
        weekly_average[key][0] = post_average
    
    print("i get called")
    
    return all_weights_c, last_seven, weekly_average, duplicate


def auto_fill_missing_dates(all_weights, weekly_averages, last_seven):
    all_weight_dates = [datetime.strptime(date, "%Y-%m-%d") for date in all_weights.keys()]
    last_weight_date = max(all_weight_dates)

    last_avg_entry = max(weekly_averages.items(), key=lambda x: x[1][1])
    last_avg_value = last_avg_entry[1][0]

    today = datetime.today()
    current_date = last_weight_date + timedelta(days=1)

    while current_date < today:
        formatted_date = current_date.strftime("%Y-%m-%d")
        all_weights, last_seven, weekly_averages, _ = update_local_enteries(last_seven, last_avg_value, weekly_averages, all_weights, formatted_date)
        current_date += timedelta(days=1)
    
    return all_weights, weekly_averages, last_seven

    
def auto_fill_prior_dates(all_weights, entery_date, val):
    all_weight_dates = [datetime.strptime(date, "%Y-%m-%d") for date in all_weights.keys()]
    first_weight_date = min(all_weight_dates)

    entery_date_obj = datetime.strptime(entery_date, "%Y-%m-%d")
    index = 1
    c = 1

    while entery_date_obj < first_weight_date:
        formatted_date = entery_date_obj.strftime("%Y-%m-%d")
        all_weights[formatted_date] = [val, int(index)]
        c+=1
        if c == 7:
            index += 1
            c = 1
        entery_date_obj += timedelta(days=1)
    
    return True

def reorder_indexs(all_weights):
    all_weight_dates = sorted([datetime.strptime(date, "%Y-%m-%d") for date in all_weights.keys()])
    temp = {}
    index = 1
    c = 0
    for d in all_weight_dates:
        str_date = d.strftime('%Y-%m-%d')
        weight = all_weights[str_date][0]
        
        if c == 7:
            c = 0
            index += 1
        
        c += 1
        temp[str_date] = [weight, int(index)]

    return temp

def update_last_seven(last_seven, all_weights):
    latest_key = list(sorted(all_weights.keys()))[-1]
    last_index = all_weights[latest_key][1]
    data = []

    for d, e in all_weights.items():
        if e[1] == last_index:
            data.append([d, e[0]])

    last_seven[0]['index'] = int(last_index)
    for d in data:
        last_seven[0]['data'][d[0]] = d[1]
    
    return last_seven


def update_weekly_averages(all_weights):
    grouped_weights = defaultdict(list)
    max_index = 0
    for date, (weight, index) in all_weights.items():
        max_index = max(max_index, index)
        grouped_weights[index].append((date, weight))
    
    weekly_averages = {}
    for index, values in grouped_weights.items():
        dates = [datetime.strptime(date, "%Y-%m-%d") for date, _ in values]
        min_date = min(dates).strftime('%Y-%m-%d')
        max_date = max(dates).strftime('%Y-%m-%d')
        avg_weight = sum(weight for _, weight in values) / len(values)
        key = f"{min_date} to {max_date}"
        
        if index == max_index:
            key = f"{min_date} to now"

        weekly_averages[key] = [avg_weight, int(index)]
    
    return weekly_averages

def generate_dates():
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return dates

def update_db(all_weights, all_weekly_averages, last_seven, collection, user_name):
    all_weights_list = [{'date': d, 'weight': w} for d, w in all_weights.items()]
    weekly_avgs_list = [{'date': d, 'average': v[0], 'index': v[1]} for d, v in all_weekly_averages.items()]
    last_seven_list = [{'data': ls['data'], 'index': ls['index']} for ls in last_seven]

    collection.update_one(
        {"username": user_name},
        {
            "$set": {
                "all_weights": all_weights_list,
                "weekly_avgs": weekly_avgs_list,
                "last_seven": last_seven_list
            }
        }
    )

def delete_date(all_weights, all_weekly_averages, last_seven, date):
    alert = False
    today = datetime.today()
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    if today > date_obj:
        alert = True
        return all_weights, all_weekly_averages, last_seven, alert

    if date not in all_weights.keys():
        alert = True
        return all_weights, all_weekly_averages, last_seven, alert

    val = all_weights[date][1]

    length_of_last_seven = len(last_seven[0]['data'])

    last_avg_entry_key = list(all_weekly_averages.keys())[-1]
    last_avg_value = all_weekly_averages[last_avg_entry_key][1]

    del all_weights[date]

    if length_of_last_seven - 1 > 0:
        new_val = ((length_of_last_seven * last_avg_value) - val) / (length_of_last_seven - 1)
        all_weekly_averages[last_avg_entry_key][1] = new_val
        del last_seven[0]["data"][date]
    else:
        last_seven[0]["data"] = {}
        del all_weekly_averages[last_avg_entry_key]
        last_avg_entry_key = list(all_weekly_averages.keys())[-1]

        new_key = ""
        for s in last_avg_entry_key:
            if s == "o":
                break
            new_key += s

        new_key += "o now"
        all_weekly_averages[new_key] = all_weekly_averages[last_avg_entry_key]
        del all_weekly_averages[last_avg_entry_key]
    
    last_seven = update_last_seven(last_seven, all_weights)

    return all_weights, all_weekly_averages, last_seven, alert

def fill_gaps(all_weights, last_seven, all_weekly_averages, latest, new_entry, new_date):
    while latest <= new_date:
        latest += timedelta(days=1)
        date_str = latest.strftime("%Y-%m-%d")
        all_weights, last_seven, all_weekly_averages, _ = update_local_enteries(last_seven, new_entry, all_weekly_averages, all_weights, date_str)
    
    return all_weights, last_seven, all_weekly_averages, True


def reformat_averages(all_weekly_averages):
    for k, v in all_weekly_averages.items():
        v[0] = float("{:.3f}".format(v[0]))
        all_weekly_averages[k] = [v[0], v[1]]
    
    return all_weekly_averages