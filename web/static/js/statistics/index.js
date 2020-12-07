/**
 * 监听 项目变更 事件
 * */
$("#statistics_project").on("change", function () {
    let ta = $("#statistics_project option:selected");
    window.location.href = `/statistics?department_id=${ta.data('depart')}&pid=${ta.val()}`;
});


<!-- 当年活动和申报趋势柱状图 -->
let activity_declaration_change_bar = getEChartsObject("activity_declaration_change_bar");

let complete_comparison_pie = getEChartsObject("complete_comparison_pie");
$.ajax({
    type: "GET",
    url: "/statistics/get_complete_num",
    data: {"project_id": PROJECT_ID},
    dataType: "json",
    success: function (data) {
        set_pie_option(complete_comparison_pie, pieOption, data);
    }
});



function show_activity_declaration_trend() {
    if (!PROJECT_ID) {
        return false;
    }
    $.ajax({
        type: "get",
        url: "/statistics/get_month_activity_declaration",
        data: {"project_id": PROJECT_ID},
        dataType: "json",
        success: function (json_data) {
            if (!json_data.success){
                return toggle_alert(false, "数据获取失败，请稍后再试");
            }
            data = json_data.data;
            let bar_data = {
                "legend": ["申报", "活动"],
                "series": [
                    {
                        "data": data["declaration"],
                        "name": "申报",
                        "type": "line",
                        "itemStyle": {
                            normal: {
                                color: '#fd8d3c',//改变折线点的颜色
                                lineStyle: {
                                    color: '#fdae6b' //改变折线颜色
                                }
                            }
                        },
                        "areaStyle": {
                            normal: {
                                color: '#fdae6b' //改变区域颜色
                            }
                        },
                    },
                    {
                        "data": data["activity"],
                        "name": "活动",
                        "type": "line",
                        "itemStyle": {
                            normal: {
                                color: '#2c7be5',//改变折线点的颜色
                                lineStyle: {
                                    color: '#2c7be5' //改变折线颜色
                                }
                            }
                        },
                        "areaStyle": {
                            normal: {
                                color: '#2c7be5' //改变区域颜色
                            }
                        }
                    }
                ]
            };
            set_pile_option(activity_declaration_change_bar, pile_option, bar_data);
        }
    });
}