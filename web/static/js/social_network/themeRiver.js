/**
 * 河流图
 * */
let riverChart = getEChartsObject("chart-river");
// let engineerRiverOption,

let riverOption = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'line',

        }
    },

    legend: {
        data: []
    },

    singleAxis: {
        top: 50,
        bottom: 50,
        axisTick: {},
        axisLabel: {},
        type: 'time',
        axisPointer: {
            animation: true,
            label: {
                show: true
            }
        },
        splitLine: {
            show: true,
            lineStyle: {
                type: 'dashed',
                opacity: 0.2
            }
        }
    },
    color: ["#2c7be5", "#6baed6",  "#c6dbef",
        "#e6550d", "#fd8d3c",  "#fdd0a2",
        "#31a354", "#74c476",  "#c7e9c0",
        "#756bb1", "#9e9ac8",  "#dadaeb",
        "#636363", "#969696",  "#d9d9d9"],
    series: [
        {
            type: 'themeRiver',
            emphasis: {
                itemStyle: {
                    shadowBlur: 20,
                    shadowColor: 'rgba(0, 0, 0, 0.8)'
                }
            },
            label: {
                show: false
            },
            data: []
        }
    ]
};

function getRiverData(type = 1) {
    let teamId = type == 1 ? TEACHER_ID : ENGINEER_ID;
    $.ajax({
        type: "get",
        url: "/detail/river",
        data: {"teamId": teamId, "type": type},
        success: function (res) {
            if (res.success === false) {
                toggle_alert(false, res.message);
                return false;
            }
            let option = riverOption;
            option.legend.data = res.data.legend;
            option.series[0].data = res.data.data;

            riverChart.setOption(option);
            riverChart.hideLoading();
        },
        error: function (error) {
            console.error(error);
        }
    });
}


function showRiver(type = 0) {
    getRiverData(type)
}

showRiver();