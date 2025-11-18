from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from . import models
from .auth import get_password_hash

# ========== 用户相关 ==========

# 根据账号获取用户
def get_user_by_account(db: Session, account_no: str):
    return db.query(models.User).filter(models.User.account_no == account_no).first()

# 创建用户（写入加密密码与角色）
def create_user(db: Session, account_no: str, password: str, role: str):
    u = models.User(account_no=account_no, password_hash=get_password_hash(password), role=role)
    db.add(u); db.commit(); db.refresh(u)
    return u

# 设置用户新密码
def set_user_password(db: Session, account_no: str, new_password: str):
    u = get_user_by_account(db, account_no)
    if not u:
        return None
    u.password_hash = get_password_hash(new_password)
    db.add(u); db.commit(); db.refresh(u)
    return u

# 删除用户（级联删除其档案与相关记录）
def delete_user(db: Session, account_no: str) -> bool:
    u = get_user_by_account(db, account_no)
    if not u:
        return False
    db.delete(u); db.commit()
    return True

# ========== 学生 / 教师档案 ==========

# 创建学生档案
def create_student(db: Session, Sno: str, Sname: str, Ssex: str, Sdept: str, Sage: int | None):
    s = models.Student(Sno=Sno, Sname=Sname, Ssex=Ssex, Sdept=Sdept, Sage=Sage)
    db.add(s); db.commit()
    return s

# 创建教师档案
def create_teacher(db: Session, Tno: str, Tname: str, Tdept: str | None, Tsex: str | None):
    t = models.Teacher(Tno=Tno, Tname=Tname, Tdept=Tdept, Tsex=Tsex)
    db.add(t); db.commit()
    return t

# 获取学生档案
def get_student(db: Session, Sno: str):
    return db.query(models.Student).filter(models.Student.Sno == Sno).first()

# 获取教师档案
def get_teacher(db: Session, Tno: str):
    return db.query(models.Teacher).filter(models.Teacher.Tno == Tno).first()

# 列出所有学生
def list_students(db: Session):
    return db.query(models.Student).all()

# 列出所有教师
def list_teachers(db: Session):
    return db.query(models.Teacher).all()

# 更新学生档案（部分字段）
def update_student(db: Session, Sno: str, *, Sname=None, Ssex=None, Sdept=None, Sage=None):
    s = get_student(db, Sno)
    if not s:
        return None
    if Sname is not None: s.Sname = Sname
    if Ssex is not None: s.Ssex = Ssex
    if Sdept is not None: s.Sdept = Sdept
    if Sage is not None: s.Sage = Sage
    db.add(s); db.commit(); db.refresh(s)
    return s

# 更新教师档案（部分字段）
def update_teacher(db: Session, Tno: str, *, Tname=None, Tdept=None, Tsex=None):
    t = get_teacher(db, Tno)
    if not t:
        return None
    if Tname is not None: t.Tname = Tname
    if Tdept is not None: t.Tdept = Tdept
    if Tsex is not None: t.Tsex = Tsex
    db.add(t); db.commit(); db.refresh(t)
    return t

# ========== 课程相关 ==========

# 创建课程
def create_course(db: Session, Cno: str, Ctno: str, Cname: str, Ccredit: float):
    c = models.Course(Cno=Cno, Ctno=Ctno, Cname=Cname, Ccredit=Ccredit)
    db.add(c); db.commit()
    return c

# 列出全部课程
def list_courses(db: Session):
    return db.query(models.Course).all()

# 判断课程是否存在
def course_exists(db: Session, Cno: str, Ctno: str) -> bool:
    return db.query(models.Course).filter(
        models.Course.Cno == Cno, models.Course.Ctno == Ctno
    ).first() is not None

# 删除课程（级联删除选课记录）
def delete_course(db: Session, Cno: str, Ctno: str) -> bool:
    c = db.query(models.Course).filter(models.Course.Cno == Cno, models.Course.Ctno == Ctno).first()
    if not c:
        return False
    db.delete(c); db.commit()
    return True

# 获取所有课程的已选人数（批量聚合）
def get_enrolled_counts(db: Session) -> dict[tuple[str, str], int]:
    rows = db.query(models.SC.Cno, models.SC.Tno, func.count('*')).group_by(models.SC.Cno, models.SC.Tno).all()
    return {(r[0], r[1]): r[2] for r in rows}

# ========== 选课与成绩 ==========

# 列出某学生已选记录（SC 行）
def list_student_selected(db: Session, Sno: str):
    return db.query(models.SC).filter(models.SC.Sno == Sno).all()

# 学生选课
def enroll(db: Session, Sno: str, Cno: str, Tno: str):
    sc = models.SC(Sno=Sno, Cno=Cno, Tno=Tno)
    db.add(sc)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    return sc

# 学生退课
def unenroll(db: Session, Sno: str, Cno: str, Tno: str) -> bool:
    row = db.query(models.SC).filter(
        models.SC.Sno == Sno, models.SC.Cno == Cno, models.SC.Tno == Tno
    ).first()
    if not row:
        return False
    db.delete(row); db.commit()
    return True

# 管理员代退课
def admin_unenroll(db: Session, Sno: str, Cno: str, Tno: str) -> bool:
    sc = db.query(models.SC).filter(
        models.SC.Sno == Sno, models.SC.Cno == Cno, models.SC.Tno == Tno
    ).first()
    if not sc:
        return False
    db.delete(sc); db.commit()
    return True

# 设置成绩（教师或管理员使用，grade 为 0-100 或 None）
def set_grade(db: Session, Sno: str, Cno: str, Tno: str, grade: int | None):
    sc = db.query(models.SC).filter(
        models.SC.Sno == Sno,
        models.SC.Cno == Cno,
        models.SC.Tno == Tno
    ).first()
    if not sc:
        return None
    sc.grade = grade
    db.add(sc); db.commit(); db.refresh(sc)
    return sc

# 通用选课记录联合查询（管理员使用，可按学生/课程/教师过滤）
def list_enrollments(db: Session, Sno: str | None = None, Cno: str | None = None, Tno: str | None = None):
    q = db.query(models.SC, models.Student.Sname, models.Course.Cname).join(
        models.Student, models.Student.Sno == models.SC.Sno
    ).join(
        models.Course, and_(models.Course.Cno == models.SC.Cno, models.Course.Ctno == models.SC.Tno)
    )
    if Sno:
        q = q.filter(models.SC.Sno == Sno)
    if Cno:
        q = q.filter(models.SC.Cno == Cno)
    if Tno:
        q = q.filter(models.SC.Tno == Tno)
    return q.all()

# 学生视角：列出自身选课（附课程名/学分/教师名）
def list_enrollments_by_student(db: Session, Sno: str):
    rows = list_enrollments(db, Sno=Sno)
    out = []
    for sc, _sname, cname in rows:
        course = db.query(models.Course).filter(
            models.Course.Cno == sc.Cno, models.Course.Ctno == sc.Tno
        ).first()
        teacher = get_teacher(db, sc.Tno)
        out.append((sc, cname, course.Ccredit if course else None, teacher.Tname if teacher else None))
    return out

# 教师视角：查看自己授课的选课记录（支持课程号与搜索学号/姓名）
def list_enrollments_by_teacher(db: Session, Tno: str, Cno: str | None = None, search: str | None = None):
    q = db.query(models.SC, models.Student.Sname, models.Course.Cname).join(
        models.Student, models.Student.Sno == models.SC.Sno
    ).join(
        models.Course, and_(models.Course.Cno == models.SC.Cno, models.Course.Ctno == models.SC.Tno)
    ).filter(models.SC.Tno == Tno)
    if Cno:
        q = q.filter(models.SC.Cno == Cno)
    if search:
        like = f"%{search}%"
        q = q.filter((models.Student.Sno.like(like)) | (models.Student.Sname.like(like)))
    return q.all()

def update_user_password(db: Session, user, new_hashed: str):
    """
    兼容字段名 hashed_password / password_hash
    """
    if hasattr(user, "hashed_password"):
        user.hashed_password = new_hashed
    elif hasattr(user, "password_hash"):
        user.password_hash = new_hashed
    else:
        # 如果你的模型字段名不同，改这里
        raise ValueError("User model has no password hash field")

    db.add(user)
    db.commit()
    db.refresh(user)
    return user