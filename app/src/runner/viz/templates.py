


def simple_bar():
    return """{
  "title": {
    "text": "Key Green Hydrogen Projects in Europe and North America"
  },
  "tooltip": {},
  "xAxis": {
    "type": "category",
    "data": ["Becancour", "Douglas", "Hyport", "Transport Sector - Phase I", "Transport Sector - Phase II", "Transport Sector - Phase III", "HyGreen Provence", "REFHYNE", "Westküste 100 - Phase I", "Westküste 100 - Phase II", "Hollandse Kust", "Delfzijl", "NortH2"]
  },
  "yAxis": {
    "type": "value",
    "name": "Electrolyser (MW)"
  },
  "series": [
    {
      "data": [20, 5, 50, 10, 240, 1050, 760, 10, 30, 680, 200, 20, 750],
      "type": "bar"
    }
  ],
}""" 

def vertical_bar():
    """
    
    """
    return """
{
  title: {
    text: 'World Population'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    boundaryGap: [0, 0.01]
  },
  yAxis: {
    type: 'category',
    data: ['Brazil', 'Indonesia', 'USA', 'India', 'China', 'World']
  },
  series: [
    {
      type: 'bar',
      data: [18203, 23489, 29034, 104970, 131744, 630230]
    },
  ]
}

"""


echarts_templates = {

    "bar": simple_bar,


}


