// Global Highcharts options
Highcharts.setOptions({
    lang: {
        downloadCSV: "Download CSV",
        downloadJPEG: "Download JPEG image",
        downloadPDF: "Download PDF document",
        downloadPNG: "Download PNG image",
        downloadSVG: "Download SVG vector image",
        downloadXLS: "Download XLS",
        loading: "Loading Data",
        noData: "Please Select A District"
    },
});

function placeholder() {
    // Place holder chart
    chart = Highcharts.chart('highchart', {
        title: {
            align: "center",
            text: "Historical Risk"
        },
        xAxis: {
            type: 'datetime',
            title: {text: "Time"}
        },
        yAxis: {
            title: {text: 'Risk Level'}
        },
        series: [{
            data: []
        }],
        chart: {
            animation: true,
            zoomType: 'x',
            borderColor: '#000000',
            borderWidth: 2,
            type: 'area'
        },
        noData: {
            style: {
                fontWeight: 'bold',
                fontSize: '15px',
                color: '#303030'
            }
        }
    });
}

function historicRiskPlot(data) {
    chart = Highcharts.chart('highchart', {
        title: {
            align: "center",
            text: '2019 Outbreak Probability (Epiweek ' + data['epiweek'] + ') for District ' + data['ubigeo']
        },
        xAxis: {
            type: 'linear',
            title: {text: "2019 Epidemiological Week (Epiweek)"}
        },
        yAxis: {
            title: {text: 'Probability of Outbreak'},
            min: 0,
            max: 1,
            tickInterval: .2,
            lineColor: 'transparent',
            gridLineWidth: 0,
            plotBands: [
                {
                    color: 'red',
                    from: .8,
                    to: 1,
                    label: {
                        text: 'High Risk',
                        align: 'left',
                    }
                },
                {
                    color: 'yellow',
                    from: .6,
                    to: .8,
                    label: {
                        text: 'Medium Risk',
                        align: 'left',
                    }
                },
                {
                    color: 'green',
                    from: 0,
                    to: .6,
                    label: {
                        text: 'Low Risk',
                        align: 'left',
                    }
                },
            ]
        },
        series: [
            {
                data: data['historical'],
                type: "line",
                name: 'Historical Risk',
                color: 'black'
            }
        ],
        chart: {
            animation: true,
            zoomType: 'x',
            borderColor: '#000000',
            borderWidth: 2,
            type: 'area'
        }
    });
}