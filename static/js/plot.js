function plot(dictData, chartTitle, start, end) {
    const ctx = document.getElementById('myChart').getContext('2d');
    console.log(start, end)
    let dataValues = [];
    let labels = [];
    let startAdding = false;

    for (const [key, value] of Object.entries(dictData)) {
        // Start adding data only when start key is reached
        if (key === start) {
            startAdding = true;
        }
        // Add data only if startAdding is true
        if (startAdding) {
            dataValues.push(value[0]);
            labels.push(key); // Use key as label to display dates
        }
        // Stop adding data once end key is reached
        if (key === end) {
            break;
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
