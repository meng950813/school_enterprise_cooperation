$("#search-select").select2({
    data: JSON.parse(universities)
});
$("#search-btn").on("click", function () {
    let data = $("#search-select").val().join(",");
    $.ajax({
        url: "/recommend/recommendES",
        type: "post",
        data: {"uni": data},
        success: function (res) {
            if (res.success == false) {
                toggle_alert(false, res.message);
                return false;
            }
            generateRow(res.data);
        },
        error: function (error) {
            toggle_alert(false, error.statusText);
            console.error(error.responseText);
        }
    });
})

function generateRow(data) {
    let rows = ["<hr>"];
    recommend_result = data.length;
    for (let i = 0; i < data.length; i++) {
        let item = data[i];
        rows.push(`<div class="row">
                    <div class="col-4 card">
                        <div class="card-body">
                            <p class="h4 card-header-title">${item.c_name}</p>
                            <p><span>${item.e_name} 团队</span></p>
                            <p><embed>团队专利:</embed> <strong class="text-primary">23</strong> &nbsp;
                               <embed>团队规模:</embed> <strong class="text-primary">${item.e_member}</strong></p>
                        </div>
                    </div>
                    <div class="col-4 card p-0"><div id="chart-compare-${i}" data-value=${item.weight}></div></div>
                    <div class="col-4 card">
                        <div class="card-body text-right">
                            <p class="h4 card-header-title">${item.u_name} - ${item.institution}</p>
                            <p><span>${item.t_name} 团队</span></p>
                            <p><strong class="text-primary">23</strong><embed>:团队专利</embed> &nbsp;
                                <strong class="text-primary">${item.t_member}</strong><embed>:团队规模</embed>
                            </p>
                        </div>
                    </div>
                </div>`);
    }
    $("#result-container").html(rows.join(""));
    setCharts();
}

let gaugeOption = {
    tooltip: {
        formatter: '{a} <br/>{b} : {c}%'
    },
    series: [
        {
            name: '技术领域',
            type: 'gauge',
            detail: {formatter: '{value}%'},
            data: [{value: 50, name: '相似度'}],

        }
    ],
    color: ["#e6550d", "#2c7be5", "#31a354"],
    textStyle: {
        height: 8,
        weight: 8
    }
};

function setCharts() {
    for (let i = 0; i < recommend_result; i++) {
        let gaugeChart = getEChartsObject(`chart-compare-${i}`);
        gaugeChart.showLoading();
        let option = JSON.parse(JSON.stringify(gaugeOption));
        let val = $(`#chart-compare-${i}`).data("value");
        option.series[0].data[0].value = ((1 - val) * 100).toFixed(2);
        gaugeChart.setOption(option);
        gaugeChart.hideLoading();
    }
}