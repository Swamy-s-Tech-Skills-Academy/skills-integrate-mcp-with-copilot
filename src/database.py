"""
Database models and configuration for the High School Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school_activities.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


class Student(Base):
    """Student model representing school students"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    grade = Column(Integer, nullable=True)
    class_section = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with participations
    participations = relationship("Participation", back_populates="student")


class Activity(Base):
    """Activity model representing extracurricular activities"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    schedule = Column(String(255), nullable=True)
    max_participants = Column(Integer, nullable=False, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with participations
    participations = relationship("Participation", back_populates="activity")


class Participation(Base):
    """Participation model representing student-activity relationships"""
    __tablename__ = "participations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="participations")
    activity = relationship("Activity", back_populates="participations")

    # Ensure unique student-activity pairs
    __table_args__ = (
        {"sqlite_autoincrement": True} if DATABASE_URL.startswith("sqlite") else {}
    )


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


# Initialize database
def init_db():
    """Initialize database with sample data"""
    create_tables()

    # Get a session
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(Activity).first():
            print("Database already initialized")
            return

        # Create sample activities
        activities_data = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30
            },
            {
                "name": "Soccer Team",
                "description": "Join the school soccer team and compete in matches",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 22
            },
            {
                "name": "Basketball Team",
                "description": "Practice and play basketball with the school team",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 15
            },
            {
                "name": "Art Club",
                "description": "Explore your creativity through painting and drawing",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15
            },
            {
                "name": "Drama Club",
                "description": "Act, direct, and produce plays and performances",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 20
            },
            {
                "name": "Math Club",
                "description": "Solve challenging problems and participate in math competitions",
                "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                "max_participants": 10
            },
            {
                "name": "Debate Team",
                "description": "Develop public speaking and argumentation skills",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 12
            }
        ]

        # Create activities
        for activity_data in activities_data:
            activity = Activity(**activity_data)
            db.add(activity)

        # Create sample students and participations
        sample_participants = {
            "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
            "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
            "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
            "Soccer Team": ["liam@mergington.edu", "noah@mergington.edu"],
            "Basketball Team": ["ava@mergington.edu", "mia@mergington.edu"],
            "Art Club": ["amelia@mergington.edu", "harper@mergington.edu"],
            "Drama Club": ["ella@mergington.edu", "scarlett@mergington.edu"],
            "Math Club": ["james@mergington.edu", "benjamin@mergington.edu"],
            "Debate Team": ["charlotte@mergington.edu", "henry@mergington.edu"]
        }

        # Create students and participations
        for activity_name, emails in sample_participants.items():
            activity = db.query(Activity).filter(Activity.name == activity_name).first()
            if activity:
                for email in emails:
                    # Create or get student
                    student = db.query(Student).filter(Student.email == email).first()
                    if not student:
                        student = Student(email=email)
                        db.add(student)
                        db.flush()  # Get the ID

                    # Create participation
                    participation = Participation(student_id=student.id, activity_id=activity.id)
                    db.add(participation)

        db.commit()
        print("Database initialized with sample data")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()