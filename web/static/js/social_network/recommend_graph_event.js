/**
 * 搜索内容的响应事件
 * */
$(".fuzzy-matching").on("input", debounce((e) => {
    let $input = $(e.target);
    let val = $input.val();
    let org_type = $input.data("org-type");
    if (!val || val.trim().length === 0) {
        return false;
    }
    $.ajax({
        url: "/recommend-graph/org-info",
        data: {"name": val, "type": org_type},
        dataType: "json",
        success: function (res) {
            if (res.success === false) {
                toggle_alert(false, res.message);
                return false;
            }
            show_item_list($input, res.data);
        },
        error: function (error) {
            console.error(error);
            return false;
        }
    });
}, 500));

/**
 * 显示联想内容
 * @param {*} $input input 标签
 * @param {*} data ==> [{"id":xxx, "name": xxx}, ...]
 */
function show_item_list($input, data) {
    let $show_items = $input.siblings(".show-items");
    let html = data.length > 0 ? "" : `<li class="list-group-item disabled">未查找到相关内容</li>`;
    for (let i = 0; i < data.length; i++) {
        html += `<li class="list-group-item show-one-line" data-id=${data[i]['id']} title="${data[i]["name"]}">${data[i]["name"]}</li>`;
    }
    $show_items.html(html).show();
}


/**
 * 设置联想内容的点击事件
 * */
$(".show-items").on("click", ".list-group-item", function (e) {
    let $items_container = $(e.target);
    $items_container.parent().siblings("input").val("");// 清空输入框
    create_tag($items_container, $items_container.attr("data-id"), $items_container.text());
    $items_container.parent().hide()
})

/**
 * 添加标签
 */
function create_tag($list_item, id, name) {
    $list_item.parent().parent().siblings(".tag-list").prepend(`
         <span class='btn btn-dark tag-container'>
             <span class="tag" data-id=${id}>${name}</span>
             <span class="remove-tag cursor-pointer">
                <i class="fe fe-x"></i>
             </span> 
         </span>
    `);
}


/**
 * 隐藏联想内容
 * @param $input 对应输入框的 jquery 对象
 */
function hide_item_list($input) {
    $input.siblings(".show-items").hide();
}


/**
 * 删除标签的响应事件
 * */
$(".tag-list").on("click", ".remove-tag", function (e) {
    $(e.target).parents(".tag-container").remove();
})


/**
 * 查询表单的提交事件
 */
$("#selector-submit").on("click", function () {
    let form_data = {
        "town": $("#town").val(),
        "com": get_tags_id($(".company-tags .tag")),
        "uni": get_tags_id($(".university-tags .tag")),
        "limit": $("#search-number").val()
    }
    sendRecommendRequest(form_data, ChartArrayGraph);
})

/**
 * 请求推荐结果
 * @param data 请求参数
 * @param graphContainer 展示推荐结果的容器 ==> echarts 对象
 */
function sendRecommendRequest(data, graphContainer) {
    graphContainer.showLoading();
    $.ajax({
        type: "get",
        url: "/recommend-graph/recommend",
        data: data,
        success: function (res) {
            if (res.success === false) {
                toggle_alert(false, res.message);
                return false;
            }
            formatGraphData(res.data);
            graphContainer.setOption(ArrayGraphOption);
        },
        error: function (error) {
            console.error(error);
            toggle_alert(false, "获取数据失败，请稍后再试");
            return false;
        },
        complete: function (){
            graphContainer.hideLoading();
        }
    });
}

$("#short-path").on("click", function () {
    params = $("#selector-form").serialize();

    myChart.showLoading();

    $.ajax({
        url: "/getPath",
        type: "get",
        data: {
            "s_label": "Engineer", "s_key": "id", "s_value": 1964,
            "t_label": "Teacher", "t_key": "id", "t_value": 137339
        },
        dataType: "json",
        success: function (data) {
            console.log("success", data);
            reloadGraph(PathGraphOption, data);
        },
        error: function (error) {
            console.error(error);
            myChart.hideLoading();
        }
    })
});


/**
 * 获取标签中的id
 * @param $tagList tag标签对应的 jquery 对象数组
 * @returns {string} eg: 123,345,567
 */
function get_tags_id($tagList) {
    let id_list = [];
    $tagList.each(function () {
        id_list.push($(this).data("id"));
    })
    return id_list.join(",");
}


function debounce(fn, delay) {
    // 定时器，用来 setTimeout
    let timer;

    // 返回一个函数，这个函数会在一个时间区间结束后的 delay 毫秒时执行 fn 函数
    return function () {

        // 保存函数调用时的上下文和参数，传递给 fn
        let context = this;
        let args = arguments;

        // 每次这个返回的函数被调用，就清除定时器，以保证不执行 fn
        clearTimeout(timer);

        // 当返回的函数被最后一次调用后（也就是用户停止了某个连续的操作），
        // 再过 delay 毫秒就执行 fn
        timer = setTimeout(function () {
            fn.apply(context, args);
        }, delay);
    }
}