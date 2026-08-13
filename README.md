# University Management System

A desktop-based University Management System developed using **Python Tkinter** and **PostgreSQL (Neon)** for the Database Management Systems course.

## Features

* User Login System
* Department Management (CRUD)
* Student Management (CRUD)
* Lecturer Management (CRUD)
* Course Management (CRUD)
* Student Enrollment
* Grade Management
* PostgreSQL Database Integration
* Shared cloud-hosted database using Neon PostgreSQL

## Technologies Used

* Python 3
* Tkinter
* PostgreSQL
* Neon PostgreSQL
* psycopg2
* python-dotenv

## Project Structure

```text
University-Management-System/
├── main.py
├── config.py
├── database.py
├── login.py
├── migrate.py
├── requirements.txt
├── README.md
├── .gitignore
├── routes/
│   └── __init__.py
│   └── dashboard.py
│   └── report.py
│   └── student.py
│   └── lecturer.py
│   └── grade.py
│   └── enrollment.py
│   └── department.py
│   └── course.py
│   └── payment.py
├── database/
│   └── university_management.sql
└── .env
```

> **Note:** `.env` contains sensitive database credentials and should not be committed to Git.

## Installation

### 1. Install Python

Install **Python 3.8 or later**.

Verify the installation:

```bash
python --version
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The main dependencies include:

* `psycopg2`
* `python-dotenv`
* `werkzeug`

### 4. Configure the Database

This project uses **Neon PostgreSQL** as its shared remote database.

Create a `.env` file in the project root:

```env
DATABASE_URL=your_neon_connection_string
```

Replace `your_neon_connection_string` with the PostgreSQL connection string provided by Neon.

The connection string should include the required SSL configuration, for example:

```text
postgresql://username:password@host/database?sslmode=require
```

The application reads this value from the `DATABASE_URL` environment variable.

### 5. Run the Application

After configuring the database connection, start the application:

```bash
python main.py
```

The application will connect to the shared Neon PostgreSQL database automatically.

## Database

The project uses **PostgreSQL hosted on Neon**.

Unlike a local PostgreSQL installation, the database is hosted remotely and can be accessed by multiple installations of the application.

```text
Application 1 ──┐
Application 2 ──┼──> Neon PostgreSQL
Application 3 ──┘
```

This allows users running the application on different computers to access the same database and see the same data.

The database has already been initialized with the required tables, relationships, constraints, and sample data.

### SQL Database File

A SQL file containing the database schema and sample data is included in:

```text
database/university_management.sql
```

The SQL file is **not required for normal application setup**, because the application's database is already hosted on Neon.

It is provided as a backup/reproducible database definition and can be used to recreate the database if necessary.

## Environment Variables

The project uses a `.env` file to store the Neon database connection string.

Example:

```env
DATABASE_URL=postgresql://username:password@host/university_management?sslmode=require
```

Do **not** commit the `.env` file to the repository.

The `.gitignore` file should contain:

```text
.env
__pycache__/
*.pyc
```

## Requirements

* Python 3.8+
* Internet connection
* Access to the configured Neon PostgreSQL database
* `psycopg2`
* `python-dotenv`
* Tkinter

A local PostgreSQL server and pgAdmin 4 installation are **not required** to run the application.

## Important Notes

* The application requires an active internet connection to access the Neon database.
* Database credentials should be kept private.
* Do not upload the `.env` file to GitHub or other public repositories.
* The Neon database must remain available for the application to access shared data.
* The SQL file is provided for backup and database restoration purposes.

## Author

Created as a Database Management Systems course project.