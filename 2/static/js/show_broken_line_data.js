function broken_line_chart(data) {

    var salaru_line = echarts.init(document.getElementById('broken_line'), 'infographic');
    window.addEventListener('resize', function () {
        salaru_line.resize();
    });

    var Data1 = data['3室2厅'];
    var Data2 = data['2室2厅'];
    var Data3 = data['2室1厅'];
    var Data4 = data['1室1厅'];

    echartsDate = [];
    for (var i = 0; i < data['date_li'].length; i++) {
        d = data['date_li'][i]
        echartsDate.push(d);
    }

    var option = {
        tooltip: {
            trigger: 'axis',
        },
        legend: {
            data: ['3室2厅', '2室2厅', '2室1厅', '1室1厅']
        },
        grid: {
            containLabel: true,
            left: '5%',
            right: '4%',
            bottom: '3%'
        },

        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: echartsDate
        },
        yAxis: {
            type: 'value',
            name: '平均价格/元',
            nameLocation: 'center',
            nameGap: 30,
            axisLine:{show:true}
        },
        series: [

            {
                name: '3室2厅',
                type: 'line',
                data: Data1
            },
            {
                name: '2室2厅',
                type: 'line',
                data: Data2
            },
            {
                name: '2室1厅',
                type: 'line',
                data: Data3
            },
            {
                name: '1室1厅',
                type: 'line',
                data: Data4
            }
        ]
    };

    salaru_line.setOption(option, true);
}