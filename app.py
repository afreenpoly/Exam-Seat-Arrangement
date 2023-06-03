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
with open('static/dates.txt', 'r') as datefiles:
    dates = json.load(datefiles)

# routes

# homepage


@app.route('/')
def index():
    return render_template('home.html')

# signup page for admin


@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if usercollections.find_one({'username': username}):
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        else:
            usercollections.insert_one(
                {'username': username, 'password': password})
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
    else:
        return render_template('adminlogin.html')


# login page for admin
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = usercollections.find_one(
            {'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('adminlogin.html')


# main page of admin where he can choose the classes
# -issue-:the classes chosen should used in /details for more processing,
    # these are the available classes where the students should be seated
@app.route('/admin')
def admin():
    return render_template('adminhome.html')


# currently not working
# -issue-: When student enters their rollnumber and a particular date .
    # their corresponding seating should be displayed
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
    

@app.route('/class', methods=['GET'])
def classchoose():
    return render_template('classavailable.html')


# page for uploading student details
@app.route('/uploaddata', methods=['GET'])
def uploadpage():
    return render_template('studentdataupload.html')

# when the data is submitted from /uploaddata or studentdataupload.html the data is processed here
# Here the data is checked and uploaded to the database
    # with sheetname as classname,year,classroom:which is the class they are going to be seated
# the data is also passed to "listy" for later usage in /seating
# finally the uploaded data is displayed in uploadeddata.html


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

# page for displaying the data via "GET" method


@app.route('/displaydata', methods=['GET'])
def display_data():
    return render_template('displaydata.html', data2=data2, data3=data3, data4=data4)

# here the timetable is uploaded via timetableupload.html
# the filename is checked


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

        # "Year" field is set to "SecondYear"
        # creates a list of the "_id" field values for those documents.
        # It then repeats this process for students in their third and fourth year of study,
        # creating separate lists of IDs for each year level.

        second_year_students = stucollections.find({"Year": "SecondYear"})
        second_year_student_ids = [student["_id"]
                                   for student in second_year_students]
        third_year_students = stucollections.find({"Year": "ThirdYear"})
        third_year_student_ids = [student["_id"]
                                  for student in third_year_students]
        fourth_year_students = stucollections.find({"Year": "FourthYear"})
        fourth_year_student_ids = [student["_id"]
                                   for student in fourth_year_students]

        # The code first checks if the timetable exists by checking if "timetable2" is not None.
        # If it does exist, the code iterates over the sheets in the timetable ("timetable2.items()"),
        # and for each subject in each sheet, it converts the "date" field to a string in the format '%d-%m-%Y'
        # using the "datetime.fromtimestamp()" and "strftime()" functions.
        # It then checks if the subject date is already in the "dates" list, and if not , adds it to the list.
        # The code then updates the "subject" field for each sheet in the "stucollections"
        # collection based on the sheet name, year level, and student IDs.
        # For each sheet, it uses the "update_many()" method to update the "subject" field of all documents in the collection
        # where the "sheet_name" field is equal to the current sheet, the "Year" field is equal to "SecondYear",
        # and the "_id" field is in the list of second-year student IDs retrieved earlier.

        # The updated "subject" field is set to the contents of the corresponding sheet in the "timetable2" dictionary,
        # which is accessed using the sheet name as the key(e.g., "timetable2["csa"]").

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

        with open('static/dates.txt', 'w') as f:
            json.dump(dates, f, indent=4)
        return render_template('timetableupload.html', status="successful")
    else:
        return render_template('timetableupload.html')

# the timetable is fetched and displayed here
@app.route('/viewtimetable', methods=['GET'])
def view_timetable():
    documents = stucollections.find(
        {}, {'sheet_name': 1, 'subject': 1, 'Year': 1})
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
    timetables = jsonify(timetables)
    return timetables


# unlike the /displaydata which displays the uploaded data
# this route fetches the uploaded data from the mongodb
@app.route('/viewdata', methods=['GET'])
def view_data():
    documents = stucollections.find(
        {}, {'name': 1, 'rollnum': 1, 'sheet_name': 1, 'Year': 1})
    data = []
    for doc in documents:
        data.append({
            'name': doc['name'],
            'rollnum': doc['rollnum'],
            'sheet_name': doc['sheet_name'],
            'Year': doc['Year']
        })
    data = jsonify(data)
    return data


# here we are assigning the classname and seat num for each class
@app.route('/details', methods=['POST'])
def details():
    items = request.form.getlist('item[]')
    class_data = []
    class_details = {
        'ADM 303': {'class_name': 'ADM 303', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 304': {'class_name': 'ADM 304', 'column': 8, 'rows': 3, 'seats': 40},
        'ADM 305': {'class_name': 'ADM 305', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 306': {'class_name': 'ADM 306', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 307': {'class_name': 'ADM 307', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 308': {'class_name': 'ADM 308', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 309': {'class_name': 'ADM 309', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 310': {'class_name': 'ADM 310', 'column': 7, 'rows': 3, 'seats': 40},
        'ADM 311': {'class_name': 'ADM 311', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 206': {'class_name': 'EAB 206', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 306': {'class_name': 'EAB 306', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 401': {'class_name': 'EAB 401', 'column': 8, 'rows': 3, 'seats': 40},
        'EAB 304': {'class_name': 'EAB 304', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 303': {'class_name': 'EAB 303', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 104': {'class_name': 'EAB 104', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 103': {'class_name': 'EAB 103', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 203': {'class_name': 'EAB 203', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 204': {'class_name': 'EAB 204', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 206': {'class_name': 'WAB 206', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 105': {'class_name': 'WAB 105', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 107': {'class_name': 'WAB 107', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 207': {'class_name': 'WAB 207', 'column': 8, 'rows': 3, 'seats': 40},
        'WAB 212': {'class_name': 'WAB 212', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 210': {'class_name': 'WAB 210', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 211': {'class_name': 'WAB 211', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 205': {'class_name': 'WAB 205', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 305': {'class_name': 'WAB 305', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 303': {'class_name': 'WAB 303', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 403': {'class_name': 'WAB 403', 'column': 7, 'rows': 3, 'seats': 40},
        'WAB 405': {'class_name': 'WAB 405', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 415': {'class_name': 'EAB 415', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 416': {'class_name': 'EAB 416', 'column': 8, 'rows': 3, 'seats': 40},
        'WAB 412': {'class_name': 'WAB 412', 'column': 7, 'rows': 3, 'seats': 40},
        'EAB 310': {'class_name': 'EAB 310', 'column': 7, 'rows': 3, 'seats': 40},
    }
    
    for item in items:
        if item in class_details:
            class_data.append(class_details[item])


    with open('static/stuarrange.txt', 'w') as f:
        json.dump(class_data, f, indent=4)

    global filled
    filled = False
    return render_template('classdetails.html')


# here the seating is done
# only two students can sit one bench but with different subjects as exam
# -issue-:this issue may arise when there is limited class and students with same subject maybe seated nearby
# using the skeleton file stuarrange.txt the students are seated into the classrooms
# the timetable/date is noted . stuarrange.txt files which is the seating arrangement is generated for each day in the timetable

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
            with open('static/stuarrange.txt', 'r') as stufiles:
                stulist = json.load(stufiles)
            for i in stulist:
                i["a"] = []
                i["b"] = []
                class_name = i.get("class_name")
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
                        {"date": date, "seatnum": "a" + str(len(i["a"])), "classroom": class_name}]
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
                        {"date": date, "seatnum": "a" + str(len(i["a"])), "classroom": class_name}]
                    stucollections.update_one({"rollnum": firstitem["ro"][0]}, {
                        "$addToSet": {"seatnum": seatinfo}})
                    firstitem["ro"].pop(0)
                if len(firstitem["ro"]) != 0:
                    listy.append(firstitem)
            newlist = list(stulist)
            with open('static/stuarrange'+date+'.txt', 'w') as f:
                json.dump(newlist, f, indent=4)
            filled = True
            
    return render_template('seating.html')
                           
#Resetting everything out


@app.route('/reset/collections', methods=['GET'])
def reset_collections():
    global filled
    filled = False
    usercollections.drop()  # Drop the 'users' collection
    stucollections.drop()  # Drop the 'student' collection
    message = "Student data has been deleted."
    return render_template('reset.html', message=message)


@app.route('/reset/static', methods=['GET'])
def reset_static():
    with open('static/dates.txt', 'w') as f:
        json.dump([], f, indent=4)
    folder_path = 'static'
    files = os.listdir(folder_path)
    for file in files:
        if file.startswith("stuarrange"):
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
    message = "Static files have been reset."
    return render_template('reset.html', message=message)


@app.route('/reset/uploads', methods=['GET'])
def reset_uploads():
    folder_path = 'uploads'
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)
    message = "Uploads have been reset."
    return render_template('reset.html', message=message)




# main function
if __name__ == '__main__':
    app.run()

# -issue-: The output should be displayed as a table with seatnumber and their rollnumber.
    # the heading should be the classroom name
    # this should be downloadable
# -issue-: Another output should be generated in which a range is displayed for the current day and the corresponding seating
    # ex: 25-12-2025
    # 12012001 - 12012035  : EAB 103
    # 12012036 - 12012063  : EAB 104
# -issue-:Since iam using admission number (120120__) instead of University Number(JEC____)
    # this might cause an issue for LET students
    # they get the admission num (121120__) of juniors while the university number is continous (LJEC____)
