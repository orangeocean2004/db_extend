from sqlalchemy import (
    Column, Integer, String, Float,
    PrimaryKeyConstraint, ForeignKey, ForeignKeyConstraint
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_no = Column(String(8), unique=True, index=True, nullable=False)  # 8位账号
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), nullable=False)  # admin | teacher | student

class Student(Base):
    __tablename__ = "students"
    Sno = Column(String(8), ForeignKey("users.account_no", ondelete="CASCADE"), primary_key=True)
    Sname = Column(String(64), nullable=False)
    Ssex = Column(String(8), nullable=False)
    Sdept = Column(String(64), nullable=False)
    Sage = Column(Integer)

class Teacher(Base):
    __tablename__ = "teachers"
    Tno = Column(String(8), ForeignKey("users.account_no", ondelete="CASCADE"), primary_key=True)
    Tname = Column(String(64), nullable=False)
    Tdept = Column(String(64))
    Tsex = Column(String(8))

class Course(Base):
    __tablename__ = "courses"
    Cno = Column(String(32), nullable=False)
    Ctno = Column(String(8), nullable=False)  # 任课教师号
    Cname = Column(String(128), nullable=False)
    Ccredit = Column(Float, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint("Cno", "Ctno", name="pk_course"),
        ForeignKeyConstraint(["Ctno"], ["teachers.Tno"], ondelete="CASCADE"),
    )

class SC(Base):
    __tablename__ = "sc"
    Sno = Column(String(8), nullable=False)
    Cno = Column(String(32), nullable=False)
    Tno = Column(String(8), nullable=False)
    grade = Column(Integer)
    __table_args__ = (
        PrimaryKeyConstraint("Sno", "Cno", "Tno", name="pk_sc"),
        ForeignKeyConstraint(["Sno"], ["students.Sno"], ondelete="CASCADE"),
        ForeignKeyConstraint(["Cno", "Tno"], ["courses.Cno", "courses.Ctno"], ondelete="CASCADE"),
    )