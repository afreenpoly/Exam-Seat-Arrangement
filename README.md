# Exam Seat Arrangement

## Overview

The application helps in arranging seats for students taking exams, ensuring that no two students with the same subject are seated nearby removing malpractice, and optimally arranging the seats for the students

You can access the live demo of the application [here](https://exam-seat-arrangement.onrender.com/).

## Features

- Generate seating arrangements for exams.
- Choose the corresponding classes to be seated
- Prevent students with the same subject from sitting close to each other.
- Choose the particular year or branch. Upload timetable, student details
- Reset data, including student information and seating arrangements.

## Technologies Used
- Python
- Flask
- MongoDB
- HTML
- CSS
- Bootstrap

## Screenshots
### Admin Page
![Admin Page](./screenshots/admin.png)

### Student Details
![Student Details](./screenshots/student_details.png)




## Usage

To use the Exam Seat Arrangement web application, follow these steps:

1. Clone this repository to your local machine.

   ```
   git clone https://github.com/afreenpoly/exam-seat-arrangement.git
2. Install the required dependencies.
   ```
    pip install -r requirements.txt
3. Change MongoDB
   To use your own mongodb Atlas, Copy the string from your Atlas Mongodb ,similar to which i have shown
   ```
   mongodb+srv://afreenpoly:<password>@studetails.ebwix9o.mongodb.net/
   ```
   Replace the username and password.
   In this system password is passed as an env variable, therefore create an .env file and set MONGO_PASSWORD as your password
   ```
   MONGO_URI = f"mongodb+srv://afreenpoly:{MONGO_PASSWORD}@studetails.ebwix9o.mongodb.net/"
   ```
3. Run the Flask application.
   ```
    python app.py
   ```
   or
   ```
    Flask run
5. Access the web application by navigating to http://localhost:5000 in your web browser.
6. Follow the on-screen instructions to generate exam seating arrangements, view existing seating plans, and perform other related tasks.

## License

This project is licensed under the MIT License.



