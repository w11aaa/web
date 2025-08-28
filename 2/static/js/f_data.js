function getdata1(data) {
    var center1 = echarts.init(document.getElementById('f_line'), 'infographic');
    window.addEventListener('resize', function () {
        center1.resize();
    });

    var myRegression = ecStat.regression('linear', data['data-predict']);
    myRegression.points.sort(function (a, b) {
        return a[0] - b[0];
    });

    echartsDate = [];
    for (var i = 0; i < data['date_li'].length; i++) {
        d = data['date_li'][i]
        echartsDate.push(d);
    }
    option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        grid: {
            show: true,//是否显示直角坐标系的网格,true显示，false不显示
            left: '5%',//grid组件离容器左侧的距离
            containLabel: true,//grid 区域是否包含坐标轴的刻度标签，在无法确定坐标轴标签的宽度，容器有比较小无法预留较多空间的时候，可以设为 true 防止标签溢出容器。
            // width: '360px',
            right:'0%',
            top:'10%',
        },


        xAxis: {
            type: 'category',
            height: '100px',
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            },
            data:echartsDate
        },
        yAxis: {
            type: 'value',
            min: 1.5,
            splitLine: {
                lineStyle: {
                    type: 'dashed'
                }
            },
            name: '平均价格/元',
            nameLocation: 'center',
            nameGap: 30

        },
        series: [{
            name: '分散值(实际值)',
            type: 'scatter',
            label: {
                emphasis: {
                    show: true,
                    position: 'left',
                    textStyle: {
                        color: 'blue',
                        fontSize: 12
                    }
                }
            },
            data: data['data-predict']
        }, {
            name: '线性值(预测值)',
            type: 'line',
            showSymbol: false,
            data: myRegression.points,
            markPoint: {
                itemStyle: {
                    normal: {
                        color: 'transparent'
                    }
                },
                label: {
                    normal: {
                        show: true,
                        position: 'left',
                        formatter: myRegression.expression,
                        textStyle: {
                            color: '#333',
                            fontSize: 12
                        }
                    }
                },
                data: [{
                    coord: myRegression.points[myRegression.points.length - 1]
                }]
            }
        }]
    };
    center1.setOption(option, true);

}