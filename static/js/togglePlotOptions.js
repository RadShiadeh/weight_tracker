function togglePlotOptions() {
    const plotOptions = document.getElementById('plot-options');
    const selectedData = document.getElementById('data').value;

    if (selectedData === 'all_weights' || selectedData === 'weekly_averages') {
        plotOptions.style.display = 'block';
    } else {
        plotOptions.style.display = 'none';
    }
}

window.onload = togglePlotOptions;