// 获取最近的高企相关活动
function get_recent_activities() {
    let params = {"project_id": PROJECT_ID};
    $.ajax({
        type: "get",
        url: "/statistics/get_recent_activities",
        data: params,
        dataType: "json",
        success: function (data) {
            let key = Object.keys(params);
            let value = params[key];
            fill_recent_activities(data["data"], key, value);
        }
    });
}


// 获取最近的相关政策
// function get_recent_policies() {
//     let params = {"project_id": 82};
//     $.ajax({
//         type: "get",
//         url: "/statistics/get_recent_policies",
//         data: params,
//         dataType: "json",
//         success: function (data) {
//             debugger
//             fill_recent_policies(data["data"]);
//         }
//     });
// }

/*
填充近期的活动
by zhang
 */
function fill_recent_activities(data, key, value) {
    let html = [];
    if (data.length == 0){
        let row_str = `
            <div class="list-group-item">
                <div class="row justify-content-center">
                    <h4 class="col one-row mb-0 text-center">暂无活动</h4>
                </div>
            </div>`;
        html.push(row_str);
    }else {
        for (let i = 0; i < data.length; i++) {
            let row_str = `
            <div class="list-group-item">
                <div class="row justify-content-center">
                    <h4 class="col one-row mb-0">
                        <a class="" target="_blank" href="/activity/show_base_info/${data[i]["activity_id"]}">${data[i]["title"]}</a>
                    </h4>
                    <p class="col-auto card-text small text-muted">
                        <time class="ml-auto">${data[i]["gmt_create"]}</time>
                    </p>
                </div>
            </div>`;
            html.push(row_str);
        }
    }
    let inner_str = html.join("");
    $("#recent_activities").html(inner_str);
}


// function fill_recent_policies(data) {
//     let html = [];
//     if (data.length == 0){
//          $("#recent_activities").html(`<h4 class="list-group-item text-center">未上传政策</h4>`);
//          return false;
//     }
//     for (let i = 0; i < data.length; i++) {
//         let postfix = data[i].name.split('.').pop().toLowerCase();
//         let row_str = `
//             <div class="list-group-item p-1">
//                 <div class="row justify-content-center align-items-center">
//                     <div class="col-auto px-0">
//                         <span class="file-logo ${postfix}"></span>
//                     </div>
//                     <h4 class="col one-row">
//                         <a class="small" target="_blank" href="/download_by_path/${data[i]['path']}/${data[i]["name"]}">${data[i]["name"]}</a>
//                     </h4>
//                     <p class="col-auto card-text small text-muted">
//                         <time class="ml-auto">${data[i]["ctime"]}</time>
//                     </p>
//                 </div>
//             </div>`;
//         html.push(row_str);
//     }
//     let inner_str = html.join("");
//     $("#recent_activities").html(inner_str);
// }