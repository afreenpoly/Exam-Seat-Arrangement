from math import ceil
from flask import Flask,render_template,request
import json,pandas as pd
app=Flask(__name__)

stufiles=open("studetails.txt","r")
stulist=json.load(stufiles)

listy = []

@app.route("/")
def hi():
  return render_template("home.html")



@app.route('/submit', methods=["POST"])
def home1():
    dict=request.form
    stulist.append(dict)
    stufile=open("studetails.txt","w")
    json.dump(stulist,stufile)
    stufile.close()
    return stulist

@app.route('/data', methods=["GET"])
def data():
    studata = open("Test.csv", "r")
    exams=[]
    while True:
        line = studata.readline()
        if not line:
            break
        ligma = line.replace('\n','').split(',')
        if not ligma[2] in exams:
            exams.append(ligma[2])
            dict={'name':ligma[2],'ro':[]}
            listy.append(dict)
    studata.seek(0)
    while True:
        line = studata.readline()
        if not line:
            break
        ligma = line.replace('\n','').split(',')
        for d in listy:
            if d['name'] == ligma[2]:
                d['ro'].append(ligma[0])
    return listy

@app.route('/seating', methods=["GET"])
def seating():
  k=0;
  for i in stulist:
    a=ceil(i["column"]/2)*i["rows"]
    b=(i["column"]*i["rows"])-a
    while k<a:
      for j in listy:
        if len(j["ro"])!=0:
          i["a"].append(j["ro"][0])
          del j["ro"][0]
          
          
          

  
if __name__=="__main__":
  app.run(host="0.0.0.0",debug=True)

