from xml.etree import ElementTree
class Service:
    def fetchData(self):
        tree = ElementTree.parse("Config.xml")
        print(type(tree))
        root_node = tree.getroot()
        loop = root_node[0]
        count = len(loop)
        count_value = range(0,count)
        details = []
        for i in count_value:
            # if loop[int(i)]:
            details.append(loop[int(i)].attrib)
        #print(details)
        return details
    
obj = Service()
response = obj.fetchData()

    


















# import pandas as pd
# import datetime

# df = pd.read_excel (r'C:\Users\Lenovo\Documents\Riverstone\2021.xlsx')
# li = []

# for index, row in df.iterrows():
#     li.append(row.to_list())
#     p =  li[index]
#     c = datetime.datetime.strptime(str(p[1]),"%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
#     print(c)
    
# #data = pd.DataFrame(df, rows= 1)C:\Users\Lenovo\Documents\Riverstone\2021.xlsx





















# from xlrd import open_workbook
# wb = open_workbook(r'C:\Users\Lenovo\Documents\Riverstone\2021.xlsx')
# print(wb)
# for s in wb.sheets():
#     #print 'Sheet:',s.name
#     values = []
#     for row in range(s.nrows):
#         col_value = []
#         for col in range(s.ncols):
#             value  = (s.cell(row,col).value)
#             try : value = str(int(value))
#             except : pass
#             col_value.append(value)
#         values.append(col_value)
# # print values