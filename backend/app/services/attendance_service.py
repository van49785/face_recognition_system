# Logic chấm công 
from app.models.attendance import Attendance
from app.db import db

def record_attendance(employee_id, status, timestamp):
    attendance = Attendance(
        employee_id=employee_id,
        timestamp=timestamp,
        status=status
    )

    db.session.add(attendance)
    db.session.commit()
    return attendance