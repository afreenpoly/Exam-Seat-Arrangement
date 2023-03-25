from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from converter import excel_to_json
import os
import math
import json
import pymongo
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = r'C:\Users\hp\Desktop\Exam-Seat-Arrangement\uploads'

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.Studetails
collections = db.student

listy = []
filled = False

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        roll = request.form['roll_number']
        return render_template('student.html', roll_num=roll)
    else:
        return render_template('student.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))
        collections.delete_many({})
        collections.insert_many(data)
        global listy
        listy = []
        details = []
        details = collections.aggregate(
            [{"$group": {"_id": "$subject", "ro": {"$push": "$rollnum"}}}])
        for i in details:
            listy.append(i)
    else:
        data = None
    return render_template('uploads.html', data=data)



@app.route('/details', methods=['POST'])
def details():
    option = request.form.get('dropdown')
    if option == '0':
        return "Error: Please select a Class"
    elif option == '1' or option == '2':
        seats = 40
    elif option == '3':
        seats = 150
    elif option == '4':
        seats = 140
    elif option == '5' or option == '6':
        seats = 50
    else:
        seats = 0
    noofclass = request.form.get('noofclass')
    if not noofclass:
        return "Error: Please enter a value for Number of Class"
    noofclass = int(noofclass)
    totalseats = noofclass * seats
    max_rows = 3
    max_columns = 7
    seats_per_bench = 2
    columns = min(max_columns, (totalseats + (seats_per_bench *
                  max_rows) - 1) // (seats_per_bench * max_rows))
    rows = min(max_rows, (totalseats + seats_per_bench - 1) // seats_per_bench)
    data = []
    for i in range(noofclass):
        data.append({"column": str(columns),
                    "rows": str(rows), "a": [], "b": []})
    with open('stuarrange.txt', 'w') as f:
        json.dump(data, f, indent=4)
    global filled
    filled=False
    return render_template('classdetails.html', seats=seats,
                           noofclass=noofclass, totalseats=totalseats, rows=rows, cols=columns)


@app.route('/seating', methods=['GET'])
def seating():
    global filled
    if filled:
        with open('stuarrange.txt', 'r') as stufiles:
            stulist = json.load(stufiles)
        return render_template('seating.html', newlist=stulist)
    with open('stuarrange.txt', 'r') as stufiles:
        stulist = json.load(stufiles)
    for i in stulist:
        i["a"] = []
        i["b"] = []
        if len(listy) == 0:
            break
        a = math.ceil(int(i["column"])/2)*int(i["rows"])
        b = (int(i["column"])*int(i["rows"]))-a
        firstitem = listy[0]
        idlist = []
        idlist.append(firstitem["_id"])
        listy.pop(0)
        for j in range(0, a):
            if len(firstitem["ro"]) == 0:
                if len(listy) == 0:
                    break
                firstitem = listy[0]
                idlist.append(firstitem["_id"])
                listy.pop(0)
            i["a"].append(firstitem["ro"][0])
            collections.update_one({"rollnum": firstitem["ro"][0]}, {
                                   "$set": {"seat no": "a" + str(len(i["a"]))}})
            firstitem["ro"].pop(0)
        if len(firstitem["ro"]) != 0:
            listy.append(firstitem)
        if len(listy) == 0:
                break
        firstitem = listy[0]
        listy.pop(0)
        for k in range(0, b):
            if len(firstitem["ro"]) == 0:
                if len(listy) == 0:
                    break
                firstitem = listy[0]
                listy.pop(0)
            if firstitem["_id"] in idlist:
                break
            i["b"].append(firstitem["ro"][0])
            collections.update_one({"rollnum": firstitem["ro"][0]}, {
                                   "$set": {"seat no": "b" + str(len(i["b"]))}})
            firstitem["ro"].pop(0)
        if len(firstitem["ro"]) != 0:
            listy.append(firstitem)
    newlist = list(stulist)
    with open('stuarrange.txt', 'w') as f:
        json.dump(newlist, f, indent=4)
    filled=True
    return render_template('seating.html', newlist=newlist)


if __name__ == '__main__':
    app.run()
