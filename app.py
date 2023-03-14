from flask import Flask,render_template,request
import json,pandas as pd
app=Flask(__name__)

stufiles=open("studetails.txt","r")
stulist=json.load(stufiles)



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
  studata=open("Test.csv","r")
  while True:
    line = studata.readline()
    if not line:
        break
    print()




  
if __name__=="__main__":
  app.run(host="0.0.0.0",debug=True)

