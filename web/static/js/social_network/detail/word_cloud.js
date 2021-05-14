let EngineerWordCloudChart = getEChartsObject("chart-word-cloud-engineer");
let TeacherWordCloudChart = getEChartsObject("chart-word-cloud-teacher");

let option = {
    // title: {
    //   // text: '企业一专利热词'
    // },
    tooltip: {},
    series: [{
        type: 'wordCloud',
        gridSize: 2,
        sizeRange: [12, 50],
        // rotationRange: [-90, 90],
        rotationRange: [-50, 50],
        shape: 'triangle',
        // width: 100,
        // height: 400,
        textStyle: {
            normal: {
                color: function () {
                    return 'rgb(' + [
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160),
                        Math.round(Math.random() * 160)
                    ].join(',') + ')';
                }
            },
            emphasis: {
                shadowBlur: 10,
                shadowColor: '#333'
            }
        },
        data: [
            {
                name: 'Point Break',
                value: 265
            }
        ]
    }]
}

function getWordCloud(teamId, type, echartsObj){
    $.ajax({
        type: "get",
        url: "/detail/wordCloud",
        data: {"teamId": teamId, "type": type},
        success: function (res) {
            let wordCloudOption = JSON.parse(JSON.stringify(option));

            wordCloudOption.series[0].data = res.data;
            echartsObj.setOption(wordCloudOption);
        },
        error: function (error) {
            console.error(error);
        }
    });
}

getWordCloud(ENGINEER_ID, 0, EngineerWordCloudChart);
getWordCloud(TEACHER_ID, 1, TeacherWordCloudChart);