let agentTrendChart = getEChartsObject('agent_trend_chart');
let data = {};

//中介对比
let agentRank = getEChartsObject('AgentRank');
setAgentRank('activity');
function setAgentRank(category){
    $.ajax({
        type: "get",
        url: "/statistics/get_agent_comparison",
        data: {'category': category, 'project_id': PROJECT_ID},
        dataType: "json",
        success: function (data) {
            barOption.xAxis.data = data["agent_list"];
            if(category === "declaration"){
                barOption.yAxis.name = "个";
            }else{
                barOption.yAxis.name = "次";
            }
            set_option(agentRank, barOption, data);
        }
    });
}



