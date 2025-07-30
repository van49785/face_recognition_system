Face Recognition Attendance Management System
This project is a modern attendance management system that integrates face recognition technology to track employee presence. The system provides a comprehensive portal for both administrators and employees, ensuring an efficient, transparent, and secure attendance process.

Table of Contents
1. Key Features

2. Technologies Used

3. System Requirements

4. Installation and Setup

    - Backend

    - Frontend

5. Usage

    - Login

    - Public Attendance (Face Recognition)

    - Admin Portal

    - Employee Portal

6. Contributing

7. Contact

Key Features
    Face Recognition Attendance:

        Accurate face recognition for check-in/check-out.

        Face training with multiple poses (front, left, right, up, down) to improve accuracy.

        Liveness detection to prevent spoofing attempts.

    Comprehensive Employee Management (Admin):

        Add, edit, soft-delete, and restore employee information.

        Manage face training data for individual employees.

        Reset employee passwords.

    Attendance Management:

        Records check-in/check-out timestamps.

        Categorizes attendance: normal, late, half-day.

        Applies company attendance policies (work hours, lunch breaks, late arrival grace period, maximum check-ins/check-outs).

    Employee Self-Service Portal:

        View personal attendance history with date filtering.

        Submit attendance recovery/adjustment requests for discrepancies.

        Change account password.

    Reporting:

        Generate attendance reports by employee or department.

        Export reports to files (e.g., Excel).

    System Configuration (Admin):

        Manage critical system settings.

        Create database backups.

        Reset/restore the system.

    Robust Authentication System:

        Clear role-based access control for Admin and Employee.

        Account locking mechanism after multiple failed login attempts.

        Mandatory password change for initial employee logins.

Technologies Used
    Backend:

        Python 3.8+

        Flask: A microframework for web development.

        SQLAlchemy: An Object-Relational Mapper (ORM) for database interaction.

        face_recognition: A library for face recognition.

        dlib: A machine learning toolkit for various facial processing tasks.

        insightface: A high-performance face recognition library.

        pytz: For timezone handling.

    Frontend:

        Vue.js 3: A progressive JavaScript framework for building user interfaces.

        Pinia: A lightweight and powerful state management library for Vue.js.

        Vuetify 3: A Material Design UI framework for building beautiful and responsive interfaces.

        Axios: A Promise-based HTTP client for interacting with the backend API.

        Vue Router: The official routing library for Vue.js.

    Database:

        SQLite

System Requirements
To run this project, you need to have the following installed:

    Python 3.8+

    Node.js 16+ and npm (or Yarn)

    pip (Python package installer)

    OpenCV (Often installed as a dependency with face recognition libraries)

    C++ Build Tools (For Windows, required for dlib and related libraries. On Linux/macOS, basic development tools are usually sufficient).

Installation and Setup
Backend
1. Clone the repository:

git clone <YOUR_REPO_URL>
cd <your_project_folder>/backend

2. Create and activate a virtual environment:

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

3. Install Python dependencies:

pip install -r requirements.txt
# If you encounter issues installing dlib, refer to dlib's documentation or search for solutions specific to your operating system.

4. Configure the database:

Create a .env file in the backend/ directory (at the same level as app/ and run.py).

Add your database configuration. Example for SQLite (development):

DATABASE_URL=sqlite:///./data/attendance.db
SECRET_KEY=your_super_secret_key_here # Change this key!
JWT_SECRET_KEY=your_jwt_secret_key_here # Change this key!
UPLOAD_FOLDER=./data/uploads
EXPORT_FOLDER=./data/exports


Initialize the database:

flask db init
flask db migrate -m "Initial migration."
flask db upgrade
python seed_data.py  # Add initial admin user or sample data

Run the backend server:

python main.py
# By default, it will run on http://127.0.0.1:5000/

Frontend
Navigate to the frontend directory:

cd ../frontend # If you are currently in the backend directory

Install Node.js dependencies:

npm install
# Or if you use Yarn:
# yarn install

Run the frontend development server:

npm run dev
# Or if you use Yarn:
# yarn dev

The application will run on http://localhost:5173/ (or a different port if 5173 is already in use).

Usage
Once both the backend and frontend servers are running, you can access the application via your web browser.

Login
Access http://localhost:5173/login.
You will see two tabs: "Admin Login" and "Employee Login".

    Admin Login: For system administrators.

    Employee Login: For employees. If this is their first login or their password requires a change, the system will redirect them to a password change page.

Public Attendance (Face Recognition)
Access http://localhost:5173/attendance.
This is the main attendance interface where employees can use face recognition to check-in/check-out.

Admin Portal
    After logging in with an Admin account, you will be redirected to the admin dashboard. From here, you can:

        Manage Employees: Add, edit, soft-delete, and restore employee information and face data.

        View Attendance History: See detailed attendance records for all employees.

        Manage Recovery Requests: View and process attendance adjustment requests from employees.

        View Reports: Generate and export aggregated attendance reports.

        System Configuration: Adjust settings, create backups, etc.

Employee Portal
    After logging in with an Employee account, you will be redirected to your personal portal. From here, you can:

        View Personal Attendance History: See all your attendance records, with the ability to filter by date range.

        Submit Attendance Recovery Requests: Submit requests to adjust attendance records for forgotten check-ins/outs or errors.

        Change Password: Update your account password.

If you wish to contribute to this project, please fork the repository, create a new branch for your feature/bug fix, and submit a Pull Request.