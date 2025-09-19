"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
Uses SQLAlchemy for database persistence.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

# Import database models and utilities
from .database import (
    get_db, init_db, SessionLocal,
    Activity, Student, Participation
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with participant information"""
    activities = db.query(Activity).all()

    # Build response with participant counts
    result = {}
    for activity in activities:
        # Count current participants
        participant_count = db.query(Participation).filter(
            Participation.activity_id == activity.id
        ).count()

        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participant_count  # Return count instead of list for privacy
        }

    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Get the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get or create student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        student = Student(email=email)
        db.add(student)
        db.flush()

    # Check if student is already signed up
    existing_participation = db.query(Participation).filter(
        Participation.student_id == student.id,
        Participation.activity_id == activity.id
    ).first()

    if existing_participation:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
        )

    # Check if activity is full
    participant_count = db.query(Participation).filter(
        Participation.activity_id == activity.id
    ).count()

    if participant_count >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )

    # Create participation
    participation = Participation(student_id=student.id, activity_id=activity.id)
    db.add(participation)
    db.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Get the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Find the participation
    participation = db.query(Participation).filter(
        Participation.student_id == student.id,
        Participation.activity_id == activity.id
    ).first()

    if not participation:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove participation
    db.delete(participation)
    db.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
