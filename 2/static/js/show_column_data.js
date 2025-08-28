function column_chart(data) {

    var salaru_line = echarts.init(document.getElementById('scolumn_line'));
    window.addEventListener('resize', function () {
        salaru_line.resize();
    });
    var XData = data['name_list_x']; // X轴的数据
    var YData = data['num_list_y'];  // Y轴的数据

    var dataMin = parseInt(Math.min.apply(null, YData) / 2);

    var option = {
        backgroundColor: "#fff",
        grid: {
            height: '200px',
            width: '320px',
            left: '50px'
        },
        xAxis: {
            axisTick: {
                show: false
            },
            splitLine: {
                show: false
            },
            splitArea: {
                show: false
            },
            data: XData,
            axisLabel: {
                formatter: function (value) {
                    var ret = ""; // 拼接类目项
                    var maxLength = 1; // 每项显示文字个数
                    var valLength = value.length; // X轴类目项的文字个数
                    var rowN = Math.ceil(valLength / maxLength); // 类目项需要换行的行数
                    if (rowN > 1) // 如果类目项的文字个数大于3,
                    {
                        for (var i = 0; i < rowN; i++) {
                            var temp = ""; // 存放每次截取的字符串
                            var start = i * maxLength; // 开始截取的位置
                            var end = start + maxLength; // 结束截取的位置
                            temp = value.substring(start, end) + "\n";
                            ret += temp; // 拼接最终得到的字符串
                        }
                        return ret;
                    } else {
                        return value;
                    }
                },
                interval: 0,
                fontSize: 11,
                fontWeight: 100,
                textStyle: {
                    color: '#555',

                }
            },
            axisLine: {
                show: {
                    color: '#4d4d4d'
                }
            }
        },
        yAxis: {
            name: '房源数量/套',
            nameLocation: 'center',
            nameGap: 35,

            axisTick: {
                show: false
            },
            splitLine: {
                show: false
            },
            splitArea: {
                show: false
            },
            min: dataMin,
            axisLabel: {
                textStyle: {
                    color: '#9faeb5',
                    fontSize: 12,
                }
            },
            axisLine: {
                lineStyle: {
                    color: '#4d4d4d'
                }
            }
        },
        "tooltip": {
            "trigger": "item",
            "textStyle": {
                "fontSize": 12
            },
            "formatter": "{b0}: {c0}套"
        },
        series: [{
            type: "bar",
            itemStyle: {
                normal: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [{
                            offset: 0,
                            color: '#00d386' // 0% 处的颜色
                        }, {
                            offset: 1,
                            color: '#0076fc' // 100% 处的颜色
                        }],
                        globalCoord: false // 缺省为 false
                    },
                    barBorderRadius: 15,
                }
            },
            data: YData,
            label: {
                show: true,
                position: 'top',
                "fontSize": 10
            }
        }]
    };
    salaru_line.setOption(option, true);
}