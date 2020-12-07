let linkPathChart = echarts.init(document.getElementById("link-path-chart"));

//关系图属性
let linkPathOption = {
    tooltip: {},
    animation: true,
    background: "red",
    color: ["#2c7be5", "#e6550d", "#31a354", "#756bb1", "#636363"],
    series: [
        {
            type: 'graph',
            layout: 'force',
            data: [],
            links: [],
            roam: true,
            symbolSize: 25,
            draggable: true,
            edgeSymbol: ['circle', 'arrow'],
            focusNodeAdjacency: true,
            label: {
                normal: {
                    position: 'inside',
                    show: true,
                }
            },
            force: {
                repulsion: 100,//节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。
                gravity: 0.01,//节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。
                edgeLength: [90, 100],//边的两个节点之间的距离，这个距离也会受 repulsion。[10, 50] ,值越小则长度越长
                layoutAnimation: true
            },
            lineStyle: {
                show: true,
                color: 'target',//决定边的颜色是与起点相同还是与终点相同
                curveness: 0//边的曲度，支持从 0 到 1 的值，值越大曲度越大。
            }
        }
    ]
};


/***
 * 获取联络路径
 * @param target 目标节点的id
 * @param type 目标节点类型： engineer or teacher
 */
function getLinkPath(target, type) {
    linkPathChart.showLoading();
    $.ajax({
        type: "get",
        url: "/link-path/path",
        // TODO
        data: {"target": target, "t_type": type},
        success: function (res) {
            linkPathOption.series[0].data = res.data.nodes;
            linkPathOption.series[0].links = res.data.links;
            linkPathOption.series[0].symbolSize = 25;

            linkPathChart.setOption(linkPathOption);
            linkPathChart.hideLoading();
        },
        error: function (error) {
            console.error(error);
        }
    });
}

/***
 *
 * @param target: String eg: e_123 or t_345
 * @param target_name: String
 */
function showLinkPath(target, target_name){
    let target_info = target.split("_");
    if(target_info.length < 2){
        return toggle_alert(false, "目标节点信息不正确");
    }
    let id = target_info[1];
    let type = target_info[0] === "e"?"engineer": "teacher";
    $("#linkPathModalLabel").text(`联络 ${target_name} 的路径`);
    $("#linkPathModal").modal();
    getLinkPath(id, type);

}

/**
 * 注册 echarts 图形的点击事件
 * @param chartObj
 */
function registerNodeClickEvent(chartObj){
    chartObj.on("click", function (param){
        if (param.dataType !== "node"){
            return false;
        }
        showLinkPath(param.data.id, param.data.name);
    });
}
