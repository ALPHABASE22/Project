import pandas as pd
from openpyxl import Workbook

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