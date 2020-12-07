let ChartPersonalNetwork = getEChartsObject("personal-network-chart");


let nodes = [];
let links = [];
let legend = [];
let categories = [];

let colors = ["#00c7ef", "#e6550d", "#AF5AFF", "#25dd59", "#6E35FF", "#002AFF", "#8CD282", "#3B0EFF", "#00BE74", "#4a3ac6"];
let gradient = ["#0AF3FF", "#fd8d3c", "#B62AFF", "#29f463", "#6E67FF", "#0048FF", "#95F300", "#604BFF", "#04FDB8", "#604BFF"];


//计算list
function generateNode(nodeInfo, idx, colorIndex=0, category=undefined) {
    if (!nodeInfo) {
        return false;
    }
    colorIndex = colorIndex % colors.length
    //计算出颜色,从第二级开始
    if (idx === 1) {
        legend.push(nodeInfo.name);
        category = nodeInfo.name;
    }
    let node = {
        id: nodeInfo.id,
        name: nodeInfo.name,
        symbolSize: generateNodeSize(idx),
        category: category,
    };

    if (nodeInfo.list && nodeInfo.list.length > 0) {
        //非子节点
        node["itemStyle"] = {
            borderColor: gradient[colorIndex],
            color: generateNodeColor(colorIndex, idx === 0),
        };
    } else {
        //子节点
        node["itemStyle"] = {
            borderColor: gradient[colorIndex],
            color: "transparent",
        };
    }
    nodes.push(node);
    if (nodeInfo.list && nodeInfo.list.length > 0){
        for (let i in nodeInfo.list){
            generateNode(nodeInfo.list[i], idx + 1, colorIndex, category);
            if (idx === 0){
                colorIndex++;
            }
        }
    }
}

function generateNodeSize(idx = 0) {
    if (idx === 0) {
        return 70;
    } else if (idx === 1) {
        return 50;
    }
    return 10;
}

function generateNodeColor(colorIndex, isRoot = false) {
    if (isRoot) {
        return {
            type: "radial",
            x: 0.5,
            y: 0.5,
            r: 0.5,
            colorStops: [
                {
                    offset: 0,
                    color: "#00c7ef" // 0% 处的颜色
                },
                {
                    offset: 0.8,
                    color: "#0AF3FF" // 80% 处的颜色
                },
                {
                    offset: 1,
                    color: "rgba(0, 0, 0, 0.3)" // 100% 处的颜色
                }
            ],
            global: false
        };
    } else {
        return {
            type: "radial",
            x: 0.5,
            y: 0.5,
            r: 0.5,
            colorStops: [
                {
                    offset: 0,
                    color: colors[colorIndex] // 0% 处的颜色
                },
                {
                    offset: 0.4,
                    color: colors[colorIndex] // 40% 处的颜色
                },
                {
                    offset: 1,
                    color: gradient[colorIndex] // 100% 处的颜色
                }
            ],
            global: false
        };
    }
}

// 生成links
function generateLinks(data, clear = false) {
    if (clear) {
        links = [];
    }
    if (data.list && data.list.length > 0) {
        let list = data.list;
        for (let i in list) {
            let link = {
                source: data.id,
                target: list[i].id
            };
            if (list[i].hasOwnProperty("V")) {
                link["label"] = `拜访 ${list[i].V}次<br>参与活动 ${list[i].A}次<br>合作 ${list[i].C}次`;
            }
            links.push(link);
            generateLinks(list[i], false);
        }
    }

}

function fillData() {
    PersonalNetworkOption.legend.data = legend;
    PersonalNetworkOption.series[0].data = nodes;
    PersonalNetworkOption.series[0].links = links;
    PersonalNetworkOption.series[0].categories = categories;

}

let PersonalNetworkOption = {
    backgroundColor: "#fafafa",
    toolbox: {
        show: true,
        left: "right",
        right: 20,
        top: "bottom",
        bottom: 20,
    },
    color: colors,
    legend: {
        show: true,
        data: [],
        textStyle: {
            color: "#000",
            fontSize: 14
        },
        // inactiveColor: "#fff",
        icon: "circle",
        type: "scroll",
        orient: "vertical",
        left: "right",
        right: 20,
        top: 20,
        bottom: 80,
        // itemWidth: 12,
        // itemHeight: 12,
        pageIconColor: "#00f6ff",
        pageIconInactiveColor: "#000",
        pageIconSize: 12,
        pageTextStyle: {
            color: "#000",
            fontSize: 12
        }
    },
    tooltip: {
        formatter: function (param){
            if (param.data.label){
                return param.data.label;
            }
        }
    },
    animationDuration: 1500,
    animationEasingUpdate: "quinticInOut",
    series: [{
        name: "",
        type: "graph",
        hoverAnimation: true,
        layout: "force",
        force: {
            repulsion: 300,
            gravity: 0.03,
            edgeLength: 150,
            layoutAnimation: true
        },
        nodeScaleRatio: 0.6,
        draggable: true,
        roam: true,
        symbol: "circle",
        data: [],
        links: [],
        categories: [],
        focusNodeAdjacency: true,
        scaleLimit: {
            //所属组件的z分层，z值小的图形会被z值大的图形覆盖
            min: 0.5, //最小的缩放值
            max: 9 //最大的缩放值
        },
        edgeSymbol: ["circle", "arrow"],
        edgeSymbolSize: [4, 8],
        label: {
            normal: {
                show: true,
                position: "inside",
                color: "#000",
                distance: 5,
                fontSize: 14
            }
        },
        lineStyle: {
            normal: {
                width: 1.5,
                curveness: 0,
                type: "solid"
            }
        }
    }]
};

function getData() {
    $.ajax({
        url: "/recommend-graph/getPersonalNetwork",
        dataType: "json",
        success: function (res) {
            if (res.success === false) {
                toggle_alert(false, res.message);
                return false;
            }
            categories = res.data.list.map(item => {
                return {
                    name: item.name
                };
            });
            generateNode(res.data, 0);
            generateLinks(res.data, true);
            fillData();

            ChartPersonalNetwork.setOption(PersonalNetworkOption);
        }
    });
}

getData();
