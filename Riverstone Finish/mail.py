from os import path
import smtplib
import datetime
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree import ElementTree
#from service import *
from msaccess import Str_C_date, res
from jinja2 import Environment
from bs4 import BeautifulSoup
from holi import response
import schedule
#print("Response :",response)
# result = next(item['value'] for item in response if item["key"] == "Host")

class AttendanceEmail:

  def get_ml_vales(self,key):
    result = next(item['value'] for item in response if item["key"] == key)
    return result
  
  def generate_message(self,SENDER_EMAIL,RECEIVER_EMAIL,HTML,mail_subject ,message):
    message['Subject'] = mail_subject
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    return message
  def fetchData(self,Str_C_date):
        tree = ElementTree.parse("Config.xml")
        print(type(tree))
        root = tree.getroot()
        details = []
        for holiday in root.findall(".//Holiday"):
            loop = holiday
            count = len(loop)
            count_value = range(0,count)            
            for i in count_value:
                test = (loop[int(i)].attrib)
                if(test["value"] == Str_C_date):
                    return True
        return False


  def send_message(self,HTML,Str_C_date):
    xml = response
    SENDER_EMAIL = self.get_ml_vales("FromMail")
    print("sender mail :",SENDER_EMAIL)
    message = MIMEMultipart()
    day = datetime.datetime.strptime(Str_C_date, '%d-%m-%Y').weekday()    
    if(self.fetchData(Str_C_date)):
      alert = self.get_ml_vales("HolidaySubject")
      mail_subject = alert+" "+Str_C_date
      message = MIMEMultipart("alternative", None, [MIMEText(Environment().from_string(HTML).render(Str_C_date=Str_C_date,res = res,), "html")])
    elif(day == 5 or day == 6):
      alert = self.get_ml_vales("WeekendSubject")
      mail_subject = alert+" "+Str_C_date
      message = MIMEMultipart("alternative", None, [MIMEText(Environment().from_string(HTML).render(Str_C_date=Str_C_date,res = res,), "html")])
    else:
      daily = self.get_ml_vales("WorkingDaySubject")
      mail_subject = daily+" "+Str_C_date
      message = MIMEMultipart("alternative", None, [MIMEText(Environment().from_string(HTML).render(Str_C_date=Str_C_date,res = res,), "html")])
    sender = self.get_ml_vales("ToMail")
    x = sender.split(",")
    for val in x :
      RECEIVER_EMAIL = val
      print("Receiver mail :",RECEIVER_EMAIL)
      SENDER_PASSWORD = self.get_ml_vales("Password")
      host = self.get_ml_vales("Host")
      port = self.get_ml_vales("Port")
      SERVER = host+":"+port
      message = self.generate_message(SENDER_EMAIL,RECEIVER_EMAIL,HTML,mail_subject,message  )
      server = smtplib.SMTP(SERVER)
      server.ehlo()
      server.starttls()
      server.login(SENDER_EMAIL, SENDER_PASSWORD)
      server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
      server.quit()
    print("Mail Sent")
  

  def schedule(self):
    interval1 = self.get_ml_vales("Interval 1")
    interval2 = self.get_ml_vales("Interval 2")
    schedule.every().day.at(interval1).do(self.send_message,HTML,Str_C_date)
    schedule.every().day.at(interval2).do(self.send_message,HTML,Str_C_date)
    while 1:
      schedule.run_pending()
      #time.sleep(1)



HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <style type="text/css">
      table, td, th {
  		border: 1px solid black;
		}
      table {
  		width: 50%;
  		border-collapse: collapse;
		}
      th{
      background-color: #89ace8;
      color: black;
      }
    </style>
  </head>
  <body>
  <h2>The Attendance Report {{Str_C_date}}</h2><br>
    <table>
      <thead>
        <tr style="border: 1px solid #1b1e24;">
          <th>S.No</th>
          <th>Employee Name</th>
          <th>Attendance Date</th>
          <th>In Time</th>
          <th>Out Time</th>
        </tr>
      </thead>
      <tbody>
      {% if res is defined %}
        {% for list in res %}
        <tr>
          <td>{{list[0]}}</td>
          <td>{{list[1]}}</td>
          <td>{{list[2]}}</td>
          <td>{{list[3]}}</td>
          <td>{{list[4]}}</td>
        </tr>
      {% else %}
          <tr>
           <td colspan="5" style="text-align:center;">No Record not found</td>
          </tr> 
        {% endfor %}
      {% endif %}
      </tbody>
    </table>
  </body>
</html>
"""
obj = AttendanceEmail()
obj.schedule()
#obj.send_message(HTML,Str_C_date)