from flask import Flask,render_template,request
import json
app=Flask(__name__)

stufiles=open("studetails.txt","r")
list=json.load(stufiles)

@app.route("/")
def hi():
  return render_template("home.html")



@app.route('/submit', methods=["POST"])
def home1():
    dict=request.form
    list.append(dict)
    stufile=open("studetails.txt","w")
    json.dump(list,stufile)
    stufile.close()
    return list


  
if __name__=="__main__":
  app.run(host="0.0.0.0",debug=True)

