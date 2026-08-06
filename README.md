# University Management System

A desktop-based University Management System developed using **Python Tkinter** and **PostgreSQL** for the Database Management Systems course.

## Features

* User Login System
* Department Management (CRUD)
* Student Management (CRUD)
* Lecturer Management (CRUD)
* Course Management (CRUD)
* Student Enrollment
* Grade Management
* PostgreSQL Database Integration

## Technologies Used

* Python 3
* Tkinter
* PostgreSQL
* pgAdmin 4
* psycopg2

## Installation

1. Install **Python 3**.
2. Install **PostgreSQL** and **pgAdmin 4**.
3. Create a new PostgreSQL database.
4. Import the `student_management.sql` file into the database.
5. Install the required Python packages:

```bash
pip install -r requirements.txt
```

6. Update the PostgreSQL connection settings in the project if necessary.
7. Run the application:

```bash
python main.py
```

## Database

The database schema and sample data are included in:

```text
database/student_management.sql
```

Import this file before running the application.

## Requirements

* Python 3.x
* PostgreSQL
* pgAdmin 4
* psycopg2

## Author

Created as a Database Management Systems course project.
