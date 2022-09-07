import pyodbc
import datetime
from datetime import date
from holi import response

class MsaccessDB:
    def get_ml_vales(self,key):
        result = next(item['value'] for item in response if item["key"] == key)
        return result
    def dbConnect(self,Str_C_date):
        path = self.get_ml_vales("DBPath")
        conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+path )
        print (conn)
        cursor = conn.cursor()
        print('Cursor :',cursor)        
        Query = 'select Employees.EmployeeName, AttendanceLogs.AttendanceDate, AttendanceLogs.InTime,  AttendanceLogs.OutTime from AttendanceLogs inner join Employees on AttendanceLogs.EmployeeId = Employees.EmployeeId where AttendanceDate = #'+dates+'# order by EmployeeName'
        cursor.execute(Query)
        data = cursor.fetchall()
        return data
    def date(self,data):
        i=1
        ADdata =[]
        for row in data:
            date = datetime.datetime.strptime(str(row.AttendanceDate),"%Y-%m-%d %H:%M:%S").strftime("%d-%m-%y")
            inTime = datetime.datetime.strptime(str(row.InTime),"%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            outTime = datetime.datetime.strptime(str(row.OutTime),"%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            result = (i,row.EmployeeName, date, inTime, outTime)
            #print(result)
            ADdata.append(result)
            i+=1
        return ADdata

C_date = date.today()
#Str_C_date = datetime.datetime.strptime(str(C_date),"%Y-%m-%d").strftime("%d/%m/%Y")
#dates = datetime.datetime.strptime(str(C_date),"%Y-%m-%d").strftime("%m/%d/%Y")
dates = "02-04-2019"
Str_C_date = "04-02-2019"
obj = MsaccessDB()
res = obj.date(obj.dbConnect(Str_C_date))