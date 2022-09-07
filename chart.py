from openpyxl import Workbook
from openpyxl.chart import Reference, LineChart

wb = Workbook()
ws = wb.active
ws.title = 'chart'

rows = [
    ('Month', 'Apple Sales', 'Banana Sales'),
    ('Jan', 100, 200),
    ('Feb', 200, 300),
    ('Mar', 300, 400),
    ('Apr', 50, 20),
    ('May', 500, 600),
    ('Jun', 100, 200),
]

for row in rows:
    ws.append(row)

wb.save('chart_eg.xlsx')
values = Reference(ws, min_col= 2, min_row=1, max_col = 3, max_row = 7)
x_values = Reference(ws, range_string="chart!A2:A7")

#initialize LineChart object
chart = LineChart()
#add data to the LineChart object
chart.add_data(values, titles_from_data = True)
#set x-axis
chart.set_categories(x_values)

##cosmetics
chart.title = 'Fruit Sales'
chart.x_axis.title = 'Month'
chart.y_axis.title = 'Fruit Sales (USD Mil)'
chart.legend.position = 'b'

ws.add_chart(chart, 'H1')
wb.save('chart_eg.xlsx')