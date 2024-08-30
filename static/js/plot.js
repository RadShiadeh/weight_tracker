function plot(dictData, chartTitle, start, end, dt) {
    const ctx = document.getElementById('myChart').getContext('2d');
    let dataValues = [];
    let labels = [];
    let startAdding = false;
    let wrongKeys = true;
    let lenIndexes = 0;

    for ([k, v] of Object.entries(dictData)) {
        lenIndexes += 1;
    }

    if (dt === "weekly_averages") {
        for (const [key, value] of Object.entries(dictData)) {
            if (key === start) {
                wrongKeys = false;
                break
            }
        }
    }

    let start_index = start;
    let end_index = end;
    if (wrongKeys === true && dt === "weekly_averages") {
        const firstEntry = Object.entries(dictData).find(([key, value]) => value[1] === 1);
        if (firstEntry) {
            start = firstEntry[0];
            const end_entry = Object.entries(dictData).find(([k, v]) => v[1] === lenIndexes);
            end = end_entry[0];
        }
    }

    start_date = Date.now();
    end_date = Date.now();

    if (dt == "all_weights") {
        start_date = new Date(start);
        end_date = new Date(end);
    } else {
        start_date = start_index;
        end_date = end_index;
    }

    if ((dt == "all_weights" && start_date > end_date) || (dt == "weekly_averages" && start_date > end_date)) {
        wrongDates(start_date, end_date);
        return;
    }


    if (dt !== "last_seven") {
        for (const [key, value] of Object.entries(dictData)) {
            if (key === start) {
                startAdding = true;
            }
            if (startAdding) {
                dataValues.push(value[0]);
                if (dt === 'weekly_averages') {
                    labels.push(value[1]);
                } else {
                    labels.push(key);
                }
            }
            if (key === end) {
                break;
            }
        }
    } else {
        for (const [key, value] of Object.entries(dictData)) {
            dataValues.push(value[0]);
            labels.push(key);
        }
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: chartTitle,
                data: dataValues,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: chartTitle
                }
            }
        }
    });
}

function wrongDates(start, end) {
    alert("the start date has to be before the end dates");

    document.getElementById('plot-from').value = start;
    document.getElementById('plot-to').value = end;
}