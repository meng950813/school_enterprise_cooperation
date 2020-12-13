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

/**
 * 搜索内容的响应事件
 * */
$(".fuzzy-matching").on("input", debounce((e) => {
    let $input = $(e.target);
    let val = $input.val();
    if (!val || val.trim().length === 0) {
        return false;
    }
    $.ajax({
        url: "/fuzzy-org",
        data: {"name": val, "type": $input.data('org-type')},
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


$(".fuzzy-matching-engineer").on("input", debounce((e) => {
    let $input = $(e.target);
    let val = $input.val(), com = $("#com-id").val();
    if (!val || val.trim().length === 0) {
        return false;
    }
    if (!com){
        return toggle_alert(false, "请先选择企业");
    }
    $.ajax({
        url: "/fuzzy-engineer",
        data: {"name": val, "com": com},
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


$(".fuzzy-matching-teacher").on("input", debounce((e) => {
    let $input = $(e.target);
    let val = $input.val(), uni = $("#university").val();
    if (!val || val.trim().length === 0 || !uni) {
        return false;
    }
    $.ajax({
        url: "/fuzzy-teacher",
        data: {"name": val, "uni": uni},
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
    let $input = $items_container.parent().prev("input");
    $input.val($items_container.text());
    let target = $input.data("target");
    $("#" + target).val($items_container.data("id"));
    $items_container.parent().hide()
})