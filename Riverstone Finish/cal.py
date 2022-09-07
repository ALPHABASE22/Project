from flask import Flask, request, render_template,redirect, url_for

from datetime import date
import datetime
import holidays
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
#from holi import h_list
import os 
from xml.dom import minidom
app = Flask(__name__,template_folder='templates') 

class Calender:
    @app.route('/', methods =["GET", "POST"])
    def calender():
        details = []
        tree = ET.parse("Config.xml")
        root = tree.getroot()
        if request.method == "POST":
            date = request.form.get("date")
            des = request.form.get("des")
            print(date)
            print(des)
            #tree = ET.parse("Config.xml")
            print(tree)
            print("hiiiiii")
            #root = tree.getroot()
            for holiday in root.findall(".//Holiday"):
                sub_element = ET.SubElement(holiday,'add')
                # data1.text = ' '.join([data1]*1)
                sub_element.set("key", des)
                sub_element.set("value", date)
            tree.write("Config.xml")
            for holiday in root.findall(".//Holiday"):
                loop = holiday
                #print(loop)
                count = len(loop)
                count_value = range(0,count)
                for i in count_value:
                    #if loop[int(i)]:
                    details.append(loop[int(i)].attrib)
                
                print("Details :",details)
                return render_template("calendar.html",data=details)

        if request.method == "GET":
            for holiday in root.findall(".//Holiday"):
                loop = holiday
                #print(loop)
                count = len(loop)
                count_value = range(0,count)
                for i in count_value:
                    #if loop[int(i)]:
                    details.append(loop[int(i)].attrib)
                
                print("Details :",details)
                return render_template("calendar.html",data=details)
                

obj = Calender()
obj.calender(app.run())



