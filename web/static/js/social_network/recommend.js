let $table_present_recommend = $("#present-result");

$("#search-btn").on("click", function () {
    let config = bootstrap_table_config();
    $table_present_recommend.bootstrapTable("destroy").bootstrapTable(config);

})

function bootstrap_table_config() {
    return {
        //基本设置
        url: "/recommend/recommendTeacherForArea",
        method: 'get',						//请求方法
        sidePagination: "server",           //分页方式：client客户端分页，server 服务端分页（*）
        striped: false,                      //是否显示行间隔色
        cache: true,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
        locale: "zh-CN",                   // 中文显示

        //分页设置
        pagination: true,                   //是否显示分页（*）
        pageNumber:1,                       //初始化加载第一页，默认第一页
        pageSize: 10,                       //每页的记录行数（*）
        pageList: [2, 10, 25, 100],        //可供选择的每页的行数（*）

        //外置div区域的工具栏
        // toolbar: '#toolbar', //工具按钮用哪个容器

        //查询参数,每次调用是会带上这个参数，可自定义
        queryParams: function (params) {
            let uni = $("#search-select").val().join(",");
            return {
                pageNum: params.offset,
                pageSize: params.limit,
                sort: params.sort,
                order:params.order,
                uni: uni
            };
        },
        //返回数据格式处理
        responseHandler: function (res) {
            if (res.success == false) {
                toggle_alert(false, res.message);
                return false;
            }
            return {
                "total": res.total,//总页数
                "rows": formatData(res.data, res.offset, res.limit, res.team)   //数据
            };
        },

        //工具栏
        // search: true,						//是否启用搜索框
        // searchOnEnterKey: true,				//按回车触发搜索方法
        showColumns: true,                  //是否显示所有的列
        showExport: true,                   //展示导出按钮
        exportDataType: "selected",         //basic', 'all', 'selected'.
        exportTypes: ['excel', 'csv'], // 文件导出类型

        //列信息和列设置
        columns: [{
            title: "选择",
            checkbox: true,
        },{
            field: 'no',
            title: '序号',
        }, {
            field: 'company',
            title: '企业',
            sortable:true,
        }, {
            field: 'e_team',
            title: '工程师团队',
        }, {
            field: 'sim',
            title: '相似度',
        }, {
            field: 't_team',
            title: '专家团队',
        }, {
            field: 'institution',
            title: '学院',
        }, {
            field: 'university',
            title: '高校',
            sortable:true,
        }]
    }
}

/**
 * 将数据格式化为 适合 bootstrap-table渲染的格式
 * */
function formatData(data, offset=0, limit=10, team=true){
    let row = [], sim, param;
    let is_team = team?1:0;
    for (let i = 0, length = data.length; i < length; i++){
        param = `eid=${data[i].e_id}&tid=${data[i].t_id}&team=${is_team}`;
        sim = `<a target="_blank" href="/recommend/recommendDetail?${param}">${((1 - data[i].weight) * 100).toFixed(2)}%</a>`;
        row.push({
            no: (offset * limit) + i + 1,
            company: data[i].c_name,
            e_team:  data[i].e_name,
            university: data[i].u_name,
            institution: data[i].institution,
            t_team: data[i].t_name,
            sim: sim
        })
    }
    return row;
}