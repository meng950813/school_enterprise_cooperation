let container = document.getElementById("array-graph-chart");
let color_pool = ["#2c7be5", "#e6550d", "#31a354", "#756bb1", "#636363", "#6baed6", "#fd8d3c", "#74c476", "#9e9ac8", "#969696"];
let links_color_pool = ["#9ecae1", "#fdae6b", "#a1d99b", "#bcbddc", "#bdbdbd", "#6baed6", "#fd8d3c", "#74c476", "#9e9ac8", "#969696"];

let ArrayGraphOption = {
    tooltip: {
        formatter: function (params) {
            return params.data.label;
        }
    },
    textStyle:{
        fontSize : 16
    },
    legend: [{data: []}],
    color: color_pool,
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
        type: 'graph',
        layout: 'none',
        data: [],
        links: [],
        categories: [],
        roam: true,
        focusNodeAdjacency: true,

        edgeLabel: {
            normal: {
                show: false,
                // textStyle: {
                //     fontSize: 14
                // },
                formatter: function (params) {
                    return params.data.weight !== undefined ? params.data.weight : "";
                },
            }
        },
        label: {
            normal: {
                show: true,
                formatter: function (params) {
                    return params.data.label !== undefined ? params.data.label : "";
                },
                position: 'bottom',
                color: '#5e5e5e'
            }
        },
        lineStyle: {
            normal: {
                width: 2,
                borderColor: '#fff',
                borderWidth: 1,
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                // curveness: 0.1,
            },
            emphasis: {
                width: 10
            }
        }
    }]
}


function formatGraphData(graph_data) {
    let nodes = [];
    let length = graph_data.nodes.length;
    let intervel = length > 0 ? 1.0 / (length - 1) : 0;
    for (let i = 0; i < length; i++) {
        nodes = nodes.concat(generateCoordinate(graph_data.nodes[i], i * intervel, 40, container));
    }

    ArrayGraphOption.series[0].data = nodes;
    ArrayGraphOption.series[0].links = formatLinks(graph_data.links);
    ArrayGraphOption.series[0].categories = graph_data.category;
    ArrayGraphOption.legend[0].data = graph_data.category.map(function (a) {
        return a.name;
    });
}


/**
 * 生成节点坐标
 * @param points 节点数组
 * @param offset 列数，用于确定横坐标
 * @param symbolSize 节点大小，用于将节点居中显示
 * @param container 父容器对象
 */
function generateCoordinate(points, offset, symbolSize, container) {
    if (!points) {
        return [];
    }
    let width = container.parentElement.clientWidth;
    while (container.parentElement !== undefined && container.parentElement.clientHeight === 0) {
        container = container.parentElement;
    }
    let height = container.parentElement.clientHeight;

    let interval = height / (points.length);
    let center = interval / 2;

    let x = offset * width, y;
    for (let i = 0, length = points.length; i < length; ++i) {
        // 注意，坐标轴原点在左下角， 垂直方向为 x轴， 水平方向为 y 轴
        y = i * interval + center + symbolSize / 2;
        // points[i].value = [x, y];
        points[i].x = x;
        points[i].y = y;
        points[i].symbolSize = symbolSize;
    }

    return points;
}

/**
 *
 * @param links
 */
function formatLinks(links) {
    let index = 0;
    for (let i = 0; i < links.length; i++) {
        index = links[i].category === undefined ? 0 : links[i].category % links_color_pool.length;
        links[i]["lineStyle"] = {
            color: links_color_pool[index]
        }
    }
    return links;
}

ChartArrayGraph = getEChartsObject("array-graph-chart");

ChartArrayGraph.on("click", function (param) {
    switch (param.dataType) {
        case "node":
            // 处理节点点击事件
            nodeClickEvent(param.data);
            break;
        case "edge":
            // 处理 边 点击事件
            edgeClickEvent(param.data);
            break;
        default:
            break;
    }
});

/**
 * 处理节点点击事件
 * @param data 节点属性 eg: {category: 0,label: "昆山国显光电有限公司",name: "c_58912", ...}
 */
function nodeClickEvent(data) {
    let info = data.name.split("_");
    let type = info[0], id = info[1];
    if ("c" === type) {
        // http://39.98.94.44:6439/get_ep_detail_name/58629/江苏华电昆山热电有限公司;
        let href = `http://39.98.94.44:6439/get_ep_detail_name/${id}/${data.label}`;
        href_blank(href);
    } else if ("e" === type || "t" === type) {
        // 查看联络工程师/专家路径
        showLinkPath(data.name, data.label);
    } else if ("u" === type) {
        let href = `http://39.98.94.44:6438/school/profile/index/${data.label}`;
        href_blank(href);
    } else if ("i" === type) {
        let href = ` http://39.98.94.44:6438/school/profile/institution_profile/${data.uni}/${data.label}`;
        href_blank(href);
    }
}

/**
 * 处理边点击事件
 * @param data 边属性 eg: {source: "e_670", target: "t_4681390", "weight": "xxx"...}
 */
function edgeClickEvent(data) {
    if (data.click && data.source && data.target) {
        let href = `/detail?s=${data.source}&t=${data.target}`;
        href_blank(href);
    }
}

function href_blank(href) {
    let redirect = document.createElement("a");
    redirect.href = href;
    redirect.target = "_blank";
    redirect.click();
}
