function plot(dictData, chartTitle, start, end, dt) {
    const ctx = document.getElementById('myChart').getContext('2d');
    let dataValues = [];
    let labels = [];
    let startAdding = false;

    if (dt !== "last_seven") {
        for (const [key, value] of Object.entries(dictData)) {
            if (key === start) {
                startAdding = true;
            }
            if (startAdding) {
                dataValues.push(value[0]);
                labels.push(key);
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
