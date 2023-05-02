from flask import Flask, flash, render_template, request, redirect, url_for, jsonify, session
from datetime import datetime
from static.converter import excel_to_json
import os
import math
import json
import pymongo
from werkzeug.utils import secure_filename

# configuring flask

app = Flask(__name__)
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = r'C:\Users\hp\Desktop\Exam-Seat-Arrangement\uploads'

# configuring mongodb

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.Studetails
usercollections = db.users
stucollections = db.student
# global variables
listy = []
filled = False
dates = []

# routes


@app.route('/')
def index():
    return render_template('home.html')



@app.route('/admin')
def admin():
    return render_template('adminhome.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = usercollections.find_one({'username': username, 'password': password})
		if user:
			session['username'] = username
			return redirect(url_for('admin'))
		else:
			return redirect(url_for('login'))
	else:
		return render_template('adminlogin.html')


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if usercollections.find_one({'username': username}):
			flash('Username already exists', 'error')
			return redirect(url_for('register'))
		else:
			usercollections.insert_one({'username': username, 'password': password})
			flash('Registration successful!', 'success')
			return redirect(url_for('login'))
	else:
		return render_template('adminlogin.html')





@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        roll = request.form['roll_num']
        student_data = stucollections.find_one({'rollnum': int(roll)})
        seatnum = None
        if student_data is not None:
            seatnum = student_data['seatnum']
        return render_template('studentpage.html', roll_num=roll, seat_num=seatnum)
    else:
        return render_template('studentpage.html')


@app.route('/uploaddata', methods=['GET'])
def uploadpage():
    return render_template('studentdataupload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file2' not in request.files or 'file3' not in request.files or 'file4' not in request.files:
        flash('Error: No file part')
        return redirect(url_for('admin'))
    file2 = request.files['file2']
    file3 = request.files['file3']
    file4 = request.files['file4']
    if file2.filename == '' or file3.filename == '' or file4.filename == '':
        flash('No selected file')
        return redirect(url_for('admin'))
    if file2.filename and file3.filename and file4.filename:
        filename2 = secure_filename(file2.filename)
        filename3 = secure_filename(file3.filename)
        filename4 = secure_filename(file4.filename)
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
        file4.save(os.path.join(app.config['UPLOAD_FOLDER'], filename4))

        global data2, data3, data4
        data2 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename2))
        data3 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename3))
        data4 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename4))
        if data2 is not None and data3 is not None and data4 is not None:
            stucollections.delete_many({})
            for sheet_name, sheet_data in data2.items():
                stucollections.insert_many([
                    {**item, "sheet_name": sheet_name, "Year": "SecondYear",
                     "classroom": None} for item in sheet_data
                ])
            for sheet_name, sheet_data in data3.items():
                stucollections.insert_many([
                    {**item, "sheet_name": sheet_name, "Year": "ThirdYear",
                     "classroom": None} for item in sheet_data
                ])
            for sheet_name, sheet_data in data4.items():
                stucollections.insert_many([
                    {**item, "sheet_name": sheet_name, "Year": "FourthYear",
                     "classroom": None} for item in sheet_data
                ])
        global listy
        listy = []
        details = []
        details = stucollections.aggregate(
            [{"$group": {"_id": "$subject", "ro": {"$push": "$rollnum"}}}])
        for i in details:
            listy.append(i)
    else:
        data2 = data3 = data4 = None
    return render_template('uploadeddata.html', data2=data2, data3=data3, data4=data4)


@app.route('/displaydata', methods=['GET'])
def display_data():
    return render_template('displaydata.html', data2=data2, data3=data3, data4=data4)


@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    if request.method == 'POST':
        file2 = request.files['file2']
        file3 = request.files['file3']
        file4 = request.files['file4']

        # Check if file2 is uploaded
        if file2.filename:
            filename2 = secure_filename(file2.filename)
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            global timetable2
            timetable2 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename2))
            print(timetable2)
        # Check if file3 is uploaded
        if file3.filename:
            filename3 = secure_filename(file3.filename)
            file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
            global timetable3
            timetable3 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename3))
            print(timetable3)
        # Check if file4 is uploaded
        if file4.filename:
            filename4 = secure_filename(file4.filename)
            file4.save(os.path.join(app.config['UPLOAD_FOLDER'], filename4))
            global timetable4
            timetable4 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename4))
            print(timetable4)

        second_year_students = stucollections.find({"Year": "SecondYear"})
        second_year_student_ids = [student["_id"]
                                   for student in second_year_students]
        third_year_students = stucollections.find({"Year": "ThirdYear"})
        third_year_student_ids = [student["_id"]
                                  for student in third_year_students]
        fourth_year_students = stucollections.find({"Year": "FourthYear"})
        fourth_year_student_ids = [student["_id"]
                                   for student in fourth_year_students]

        if timetable2 is not None:
            for sheet_name, subjects in timetable2.items():
                for subject in subjects:
                    subject_date = datetime.fromtimestamp(
                        subject['date'] / 1000.0).strftime('%d-%m-%Y')
                    subject['date'] = subject_date
                    if subject_date not in dates:
                        dates.append(subject_date)
            stucollections.update_many(
                {"sheet_name": "csa", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["csa"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["csb"]}}
            )
            stucollections.update_many(
                {"sheet_name": "eee", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["eee"]}}
            )

        if timetable3 is not None:
            for sheet_name, subjects in timetable3.items():
                for subject in subjects:
                    subject_date = datetime.fromtimestamp(
                        subject['date'] / 1000.0).strftime('%d-%m-%Y')
                    subject['date'] = subject_date
                    if subject_date not in dates:
                        dates.append(subject_date)
            stucollections.update_many(
                {"sheet_name": "csa", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["csa"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["csb"]}}
            )
            stucollections.update_many(
                {"sheet_name": "eee", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["eee"]}}
            )
        if timetable4 is not None:
            for sheet_name, subjects in timetable4.items():
                for subject in subjects:
                    subject_date = datetime.fromtimestamp(
                        subject['date'] / 1000.0).strftime('%d-%m-%Y')
                    subject['date'] = subject_date
                    if subject_date not in dates:
                        dates.append(subject_date)
            stucollections.update_many(
                {"sheet_name": "csa", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["csa"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["csb"]}}
            )
            stucollections.update_many(
                {"sheet_name": "eee", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["eee"]}}
            )
        return render_template('timetableupload.html', status="successful")
    else:
        return render_template('timetableupload.html')


@app.route('/viewtimetable', methods=['GET'])
def view_timetable():
    documents = stucollections.find({}, {'sheet_name': 1, 'subject': 1, 'Year':1})
    timetables = {}
    for doc in documents:
        year = doc['Year']
        sheet_name = doc['sheet_name']
        subject = doc['subject']

        if year not in timetables:
            timetables[year] = {}
            
        if sheet_name not in timetables[year]:
            timetables[year][sheet_name] = []
        timetables[year][sheet_name].append(subject)
    timetables=jsonify(timetables)
    return timetables

@app.route('/viewdata', methods=['GET'])
def view_data():
    documents = stucollections.find({}, {'name': 1, 'rollnum': 1, 'sheet_name': 1, 'Year': 1})
    data = []
    for doc in documents:
        data.append({
            'name': doc['name'],
            'rollnum': doc['rollnum'],
            'sheet_name': doc['sheet_name'],
            'Year': doc['Year']
        })
    data=jsonify(data)
    return data
    


@app.route('/details', methods=['POST'])
def details():
    items = request.form.getlist('item[]')
    class_data = []
    for item in items:
        if item == 'ADM1':
            class_name = 'ADM 303'
            seats = 40
        elif item == 'ADM2':
            class_name = 'ADM 304'
            seats = 40
        elif item == 'C1':
            class_name = 'EAB 407'
            seats = 40
        elif item == 'C2':
            class_name = 'EAB 106'
            seats = 40
        elif item == 'C15':
            class_name = 'WAB 206'
            seats = 40
        elif item == 'C16':
            class_name = 'WAB 105'
            seats = 40
        elif item == 'CEH1':
            class_name = 'Common Exam Hall 1'
            seats = 150
        elif item == 'CEH2':
            class_name = 'Common Exam Hall 2'
            seats = 140
        elif item == 'DH1':
            class_name = 'Drawing Hall'
            seats = 50
        elif item == 'SH1':
            class_name = 'Seminar Hall'
            seats = 50

        max_rows = 7
        max_columns = 6
        seats_per_bench = 2
        columns = min(max_columns, (seats + (seats_per_bench *
                      max_rows) - 1) // (seats_per_bench * max_rows))
        rows = min(max_rows, (seats + seats_per_bench - 1) // seats_per_bench)

        class_data.append(
            {"column": str(columns),
             "rows": str(rows), "a": [], "b": [], "class_name": class_name})

    with open('static/stuarrange.txt', 'w') as f:
        json.dump(class_data, f, indent=4)
        
        
    global filled
    filled = False
    return render_template('classdetails.html')


@app.route('/seating', methods=['GET'])
def seating():
    global filled
    if filled:
        with open('static/stuarrange.txt', 'r') as stufiles:
            stulist = json.load(stufiles)
        return render_template('seating.html', newlist=stulist)
    else:
        for date in dates:
            global listyy
            listyy = []
            details = stucollections.aggregate(
                [{"$group": {"_id": "$subject", "ro": {"$push": "$rollnum"}}}])
            for i in details:
                listyy.append(i)
            listy = []
            for item in listyy:
                for item1 in item["_id"]:
                    if item1.get("date") == date:
                        tempdict = dict(item)
                        tempdict["_id"] = item1
                        listy.append(tempdict)
            print(listyy)
            with open('static/stuarrange.txt', 'r') as stufiles:
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
                    seatinfo = [
                        {"date": date, "seatnum": "a" + str(len(i["a"]))}]
                    stucollections.update_one({"rollnum": firstitem["ro"][0]}, {
                        "$addToSet": {"seatnum": seatinfo}})
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
                    seatinfo = [
                        {"date": date, "seatnum": "a" + str(len(i["a"]))}]
                    stucollections.update_one({"rollnum": firstitem["ro"][0]}, {
                        "$addToSet": {"seatnum": seatinfo}})
                    firstitem["ro"].pop(0)
                if len(firstitem["ro"]) != 0:
                    listy.append(firstitem)
            newlist = list(stulist)
            with open('static/stuarrange'+date+'.txt', 'w') as f:
                json.dump(newlist, f, indent=4)
            filled = True
    return "Completed"
            

@app.route('/test', methods=['GET'])
def test():
    global filled
    filled = False
    return "Unfilled"


if __name__ == '__main__':
    app.run()
