from flask import Flask, flash, render_template, request, redirect, url_for, jsonify, session, Markup
from datetime import datetime
from static.converter import excel_to_json
import os
import math
import fnmatch
import json
import pymongo
from werkzeug.utils import secure_filename

# configuring flask

app = Flask(__name__)
app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = r'C:\Users\hp\Desktop\Exam-Seat-Arrangement\uploads'

# configuring mongodb
client = pymongo.MongoClient(
    "mongodb://localhost:27017")
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
        
        # Check if the username already exists in the database
        if usercollections.find_one({'username': username}):
            flash('Username already exists', 'registration-error')
            return redirect(url_for('register'))
        
        else:
            # If the username is unique, insert the new user into the database
            usercollections.insert_one(
                {'username': username, 'password': password})
            flash('Registration successful!', 'registration-success')
            return redirect(url_for('login'))
    else:
        return render_template('adminlogin.html')


# login page for admin
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve the username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password match a user in the database
        user = usercollections.find_one(
            {'username': username, 'password': password})
        
        if user:
            # If the user exists, store the username in the session
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'login-error')
            return redirect(url_for('login'))
    else:
        return render_template('adminlogin.html')


# main page of admin where he can choose the classes
@app.route('/admin')
def admin():
    return render_template('adminhome.html')


# When student enters their rollnumber
    # their corresponding seating is displayed
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        roll = request.form['roll_num']
        student_data = stucollections.find_one({'rollnum': int(roll)})
        
        # Retrieve the seat number for the student
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
    file2 = request.files['file2']
    file3 = request.files['file3']
    file4 = request.files['file4']

    if file2.filename == '' and file3.filename == '' and file4.filename == '':
        flash('No files uploaded', 'error')
        return render_template('studentdataupload.html')

    if file2.filename:
        filename2 = secure_filename(file2.filename)
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        global data2
        data2 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename2))
    else:
        data2 = None

    if file3.filename:
        filename3 = secure_filename(file3.filename)
        file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
        global data3
        data3 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename3))
    else:
        data3 = None

    if file4.filename:
        filename4 = secure_filename(file4.filename)
        file4.save(os.path.join(app.config['UPLOAD_FOLDER'], filename4))
        global data4
        data4 = excel_to_json(os.path.join(
            app.config['UPLOAD_FOLDER'], filename4))
    else:
        data4 = None

    if data2 is not None:
        for sheet_name, sheet_data in data2.items():
            stucollections.insert_many([
                {**item, "sheet_name": sheet_name, "Year": "SecondYear", "classroom": None} for item in sheet_data
            ])

    if data3 is not None:
        for sheet_name, sheet_data in data3.items():
            stucollections.insert_many([
                {**item, "sheet_name": sheet_name, "Year": "ThirdYear", "classroom": None} for item in sheet_data
            ])

    if data4 is not None:
        for sheet_name, sheet_data in data4.items():
            stucollections.insert_many([
                {**item, "sheet_name": sheet_name, "Year": "FourthYear", "classroom": None} for item in sheet_data
            ])

    global listy
    listy = []
    details = []
    details = stucollections.aggregate(
        [{"$group": {"_id": "$subject", "ro": {"$push": "$rollnum"}}}])
    for i in details:
        listy.append(i)

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
        # Retrieve uploaded files
        file2 = request.files['file2']
        file3 = request.files['file3']
        file4 = request.files['file4']

        if not file2 and not file3 and not file4:
            flash('No files uploaded', 'error')
            return render_template('timetableupload.html')

        # Check if file2 is uploaded
        if file2.filename:
            filename2 = secure_filename(file2.filename)
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            global timetable2
            timetable2 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename2))
        else:
            timetable2 = None

        # Check if file3 is uploaded
        if file3.filename:
            filename3 = secure_filename(file3.filename)
            file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
            global timetable3
            timetable3 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename3))
        else:
            timetable3 = None

        # Check if file4 is uploaded
        if file4.filename:
            filename4 = secure_filename(file4.filename)
            file4.save(os.path.join(app.config['UPLOAD_FOLDER'], filename4))
            global timetable4
            timetable4 = excel_to_json(os.path.join(
                app.config['UPLOAD_FOLDER'], filename4))
        else:
            timetable4 = None

        # "Year" field is set to "SecondYear"
        # creates a list of the "_id" field values for those documents.
        # It then repeats this process for students in their third and fourth year of study,
        # Fetch student IDs for each year level

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
        # Update subjects in the "stucollections" collection based on the uploaded timetables

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
                {"$set": {"subject": timetable2["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ec", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["ec"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ee", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["ee"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ad", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["ad"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ce", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["ce"]}}
            )
            # stucollections.update_many(
            #     {"sheet_name": "mea", "Year": "SecondYear",
            #         "_id": {"$in": second_year_student_ids}},
            #     {"$set": {"subject": timetable2["me"]}}
            # )
            # stucollections.update_many(
            #     {"sheet_name": "meb", "Year": "SecondYear",
            #         "_id": {"$in": second_year_student_ids}},
            #     {"$set": {"subject": timetable2["me"]}}
            # )
            stucollections.update_many(
                {"sheet_name": "me", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "mr", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["mr"]}}
            )
            stucollections.update_many(
                {"sheet_name": "rb", "Year": "SecondYear",
                    "_id": {"$in": second_year_student_ids}},
                {"$set": {"subject": timetable2["rb"]}}
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
                {"$set": {"subject": timetable3["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ee", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["ee"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ec", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["ec"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ce", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["ce"]}}
            )
            stucollections.update_many(
                {"sheet_name": "mea", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "meb", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "me", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "mr", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["mr"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ad", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["ad"]}}
            )
            stucollections.update_many(
                {"sheet_name": "rb", "Year": "ThirdYear",
                    "_id": {"$in": third_year_student_ids}},
                {"$set": {"subject": timetable3["rb"]}}
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
                {"$set": {"subject": timetable4["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "csb", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["cs"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ec", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["ec"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ce", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["ce"]}}
            )
            stucollections.update_many(
                {"sheet_name": "ee", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["ee"]}}
            )
            stucollections.update_many(
                {"sheet_name": "me", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "mea", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "meb", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["me"]}}
            )
            stucollections.update_many(
                {"sheet_name": "mr", "Year": "FourthYear",
                    "_id": {"$in": fourth_year_student_ids}},
                {"$set": {"subject": timetable4["mr"]}}
            )

        with open('static/dates.txt', 'w') as f:
            json.dump(dates, f, indent=4)
            flash('Upload successful', 'success')
        return render_template('timetableupload.html')
    else:
        flash('Upload failed', 'danger')
    return render_template('timetableupload.html')

# the timetable is fetched and displayed here
@app.route('/viewtimetable', methods=['GET'])
def view_timetable():
    # Fetch the documents from the MongoDB collection
    documents = stucollections.find(
        {}, {'sheet_name': 1, 'subject': 1, 'Year': 1})
    
    # Dictionary to store the timetable data
    timetables = {}
    for doc in documents:
        year = doc['Year']
        sheet_name = doc['sheet_name']
        subject = doc['subject']

        if year not in timetables:
            timetables[year] = {}

        if sheet_name not in timetables[year]:
            timetables[year][sheet_name] = []
        # Append the subject to the corresponding year and sheet_name in the timetable dictionary
        timetables[year][sheet_name].append(subject)
        
    # Convert the timetable dictionary to JSON format
    timetables = jsonify(timetables)
    return timetables


# unlike the /displaydata which displays the uploaded data
# this route fetches the uploaded data from the mongodb
@app.route('/viewdata', methods=['GET'])
def view_data():
    # Fetch the documents from the MongoDB collection
    documents = stucollections.find(
        {}, {'name': 1, 'rollnum': 1, 'sheet_name': 1, 'Year': 1})
    
    # List to store the retrieved data
    data = []
    
    for doc in documents:
        # Extract the relevant fields from each document and append them to the data list
        data.append({
            'name': doc['name'],
            'rollnum': doc['rollnum'],
            'sheet_name': doc['sheet_name'],
            'Year': doc['Year']
        })
        
    # Convert the data list to JSON format
    data = jsonify(data)
    return data


# here we are assigning the classname and seat num for each class
@app.route('/details', methods=['POST'])
def details():
    # Get the list of selected items from the form
    items = request.form.getlist('item[]')
    
    # List to store the details of selected classes
    class_data = []
    
    # Dictionary mapping class items to their details
    class_details = {
        'ADM 303': {'class_name': 'ADM 303', 'column': 6, 'rows': 7},
        'ADM 304': {'class_name': 'ADM 304', 'column': 8, 'rows': 3},
        'ADM 305': {'class_name': 'ADM 305', 'column': 7, 'rows': 3},
        'ADM 306': {'class_name': 'ADM 306', 'column': 7, 'rows': 3},
        'ADM 307': {'class_name': 'ADM 307', 'column': 7, 'rows': 3},
        'ADM 308': {'class_name': 'ADM 308', 'column': 7, 'rows': 3},
        'ADM 309': {'class_name': 'ADM 309', 'column': 7, 'rows': 3},
        'ADM 310': {'class_name': 'ADM 310', 'column': 7, 'rows': 3},
        'ADM 311': {'class_name': 'ADM 311', 'column': 7, 'rows': 3},
        'EAB 206': {'class_name': 'EAB 206', 'column': 7, 'rows': 3},
        'EAB 306': {'class_name': 'EAB 306', 'column': 7, 'rows': 3},
        'EAB 401': {'class_name': 'EAB 401', 'column': 8, 'rows': 3},
        'EAB 304': {'class_name': 'EAB 304', 'column': 7, 'rows': 3},
        'EAB 303': {'class_name': 'EAB 303', 'column': 7, 'rows': 3},
        'EAB 104': {'class_name': 'EAB 104', 'column': 7, 'rows': 3},
        'EAB 103': {'class_name': 'EAB 103', 'column': 7, 'rows': 3},
        'EAB 203': {'class_name': 'EAB 203', 'column': 7, 'rows': 3},
        'EAB 204': {'class_name': 'EAB 204', 'column': 7, 'rows': 3},
        'WAB 206': {'class_name': 'WAB 206', 'column': 7, 'rows': 3},
        'WAB 105': {'class_name': 'WAB 105', 'column': 7, 'rows': 3},
        'WAB 107': {'class_name': 'WAB 107', 'column': 7, 'rows': 3},
        'WAB 207': {'class_name': 'WAB 207', 'column': 8, 'rows': 3},
        'WAB 212': {'class_name': 'WAB 212', 'column': 7, 'rows': 3},
        'WAB 210': {'class_name': 'WAB 210', 'column': 7, 'rows': 3},
        'WAB 211': {'class_name': 'WAB 211', 'column': 7, 'rows': 3},
        'WAB 205': {'class_name': 'WAB 205', 'column': 7, 'rows': 3},
        'WAB 305': {'class_name': 'WAB 305', 'column': 7, 'rows': 3},
        'WAB 303': {'class_name': 'WAB 303', 'column': 7, 'rows': 3},
        'WAB 403': {'class_name': 'WAB 403', 'column': 7, 'rows': 3},
        'WAB 405': {'class_name': 'WAB 405', 'column': 7, 'rows': 3},
        'EAB 415': {'class_name': 'EAB 415', 'column': 7, 'rows': 3},
        'EAB 416': {'class_name': 'EAB 416', 'column': 8, 'rows': 3},
        'WAB 412': {'class_name': 'WAB 412', 'column': 7, 'rows': 3},
        'EAB 310': {'class_name': 'EAB 310', 'column': 7, 'rows': 3},
    }

    for item in items:
        if item in class_details:
            class_data.append(class_details[item])

    # Write the class_data list to 'static/stuarrange.txt' file as JSON
    with open('static/stuarrange.txt', 'w') as f:
        json.dump(class_data, f, indent=4)

    global filled
    filled = False
    return render_template('classdetails.html', class_data=class_data)


# here the seating is done
# only two students can sit one bench but with different subjects as exam
# -issue-:this issue may arise when there is limited class and students with same subject maybe seated nearby
# using the skeleton file stuarrange.txt the students are seated into the classrooms
# the timetable/date is noted . stuarrange.txt files which is the seating arrangement is generated for each day in the timetable

@app.route('/seating', methods=['GET'])
def seating():
    global filled
    
    # Check if 'stuarrange.txt' file doesn't exist, flash an error message and redirect to 'admin' route
    if not os.path.exists('static/stuarrange.txt'):
        flash('Choose Class', 'error')
        return redirect(url_for('admin'))
    
    if filled:
        with open('static/stuarrange.txt', 'r') as stufiles:
            stulist = json.load(stufiles)  # Load the JSON data from the file
        flash('Already generated', 'error')
        return redirect(url_for('admin'))
    
    else:
        #reset data to avoid redundancy
        stucollections.update_many({}, {"$unset": {"seatnum": ""}})
        
        for date in dates:
            global listyy
            
            #all date , subjects and students
            listyy = []
            
            #rollnumbers of each subject
            details = stucollections.aggregate(
                [{"$group": {"_id": "$subject", "ro": {"$push": "$rollnum"}}}])
            for i in details:
                listyy.append(i)
            
            #sorting rollnumber by date of exam.
            #current date subjects and students
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
                
                # Calculate the number of seats in 'a' ,'b'
                a = math.ceil(int(i["column"])/2)*int(i["rows"])
                b = (int(i["column"])*int(i["rows"]))-a
                
                #selecting the subject into firstitem
                firstitem = listy[0]
                
                #inserts current date subject
                idlist = []
                idlist.append(firstitem["_id"])
                
                listy.pop(0)
                
                # Assign students to seats in category 'a'
                for j in range(0, a):
                    #checking if currentsubject students is over and seats and students of other subject exist
                    if len(firstitem["ro"]) == 0:
                        
                        #check if students list is empty
                        if len(listy) == 0:
                            break
                        
                        #takes next subject into firstitem
                        firstitem = listy[0]
                        
                        #contains currents date's(firstitem selected) subject
                        idlist.append(firstitem["_id"])
                        listy.pop(0)
                        
                    i["a"].append(firstitem["ro"][0])
                    #assigning seat
                    
                    seatinfo = [
                        {"date": date, "seatnum": "a" + str(len(i["a"])), "classroom": class_name, "subject": firstitem["_id"]["subject"]}]
                    stucollections.update_one({"rollnum": firstitem["ro"][0]}, {
                        "$addToSet": {"seatnum": seatinfo}})
                    
                    #remove student after seating from the current subject
                    firstitem["ro"].pop(0)
                    
                #a section is over while students are remaining
                #then remaining students is appended back to the listy
                if len(firstitem["ro"]) != 0:
                    listy.append(firstitem)
                
                # check if students list is empty
                if len(listy) == 0:
                    break
                
                
                # takes next subject into firstitem since a has been filled. And different subject should be taken
                firstitem = listy[0]
                listy.pop(0)
                
                # Assign students to seats in category 'b'
                for k in range(0, b):
                    if len(firstitem["ro"]) == 0:
                        
                        # check if students list is empty
                        if len(listy) == 0:
                            break
                        
                        # takes next subject into firstitem since there are no students left for that subject(firstitem)
                        firstitem = listy[0]
                        listy.pop(0)
                    
                    
                    #check if a has the same subject as b
                    if firstitem["_id"] in idlist:
                        break
                    #this is why some rows are left in b column
                    
                    i["b"].append(firstitem["ro"][0])
                    seatinfo = [
                        {"date": date, "seatnum": "b" + str(len(i["b"])), "classroom": class_name, "subject": firstitem["_id"]["subject"]}]
                    stucollections.update_one({"rollnum": firstitem["ro"][0]}, {
                        "$addToSet": {"seatnum": seatinfo}})
                    firstitem["ro"].pop(0)
                    
                # b section is over while students are remaining
                # then remaining students is appended back to the listy
                if len(firstitem["ro"]) != 0:
                    listy.append(firstitem)
                    
            newlist = list(stulist)
            # Open 'stuarrange<date>.txt' file in write mode
            with open('static/stuarrange'+date+'.txt', 'w') as f:
                json.dump(newlist, f, indent=4)
            filled = True  # Set 'filled' to True to indicate that seating is generated


        flash('Generated', 'success')
        return render_template("adminhome.html")


@app.route('/viewseating', methods=['GET'])
def viewseating():
    global filled
    if not filled:
        flash('Firstly generate seating', 'error')
        return render_template("adminhome.html")
    with open('static/dates.txt', 'r') as file:
        content = file.read()
    return render_template('viewseating.html', dates=Markup(content))
# Render the 'viewseating.html' template, passing the content of 'dates.txt' as the 'dates' variable
# Markup is used to mark the content as safe to render HTML tags, assuming the content contains HTML


@app.route('/viewseating/<path:name>', methods=['GET'])
def viewseating1(name):
    global filled
    if filled:
        file_loc = 'static/stuarrange'+name+'.txt'
        # Assumes static folder is defined in your Flask app
        with open(file_loc, 'r') as file:  # Open the file in read mode
            content = file.read()  # Read the content of the file

    else:
        flash('Firstly generate seating', 'error')
        return render_template("adminhome.html")
    return content


# Resetting everything out
@app.route('/reset', methods=['GET'])
def reset():
    return render_template('reset.html')


@app.route('/reset/collections', methods=['GET'])
def reset_collections():
    global filled
    filled = False
    stucollections.drop()  # Drop the 'student' collection
    message = "Student data has been deleted."
    return render_template('reset.html', message=message)


@app.route('/reset/users', methods=['GET'])
def reset_users():
    usercollections.drop()  # Drop the 'users' collection
    message = "Users has been deleted."
    return render_template('reset.html', message=message)


@app.route('/reset/static', methods=['GET'])
def reset_static():
    folder_path = 'static'
    files = os.listdir(folder_path)  # Get a list of all files in the folder
    for file in files:
        if file.startswith("stuarrange"):
            # Get the full path of the file
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)  # Remove the file from the folder
    message = "Static files have been reset."
    global filled
    filled = False
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
