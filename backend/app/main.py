from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from . import models, crud, auth, schemas
from .deps import get_db
from .auth import require_role

app = FastAPI(title="学生信息管理系统 API")

# 默认初始 / 重置密码
DEFAULT_PASSWORD = "123456"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 认证与通用 ==========

@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account_no = form.username.strip()
    user = crud.get_user_by_account(db, account_no)
    if not user or not auth.verify_password(form.password, user.password_hash):
        raise HTTPException(401, "账号或密码错误")
    token = auth.create_access_token({"account_no": user.account_no, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
def me(current=Depends(auth.get_current_user)):
    return current

# ========== 管理员：用户与档案 ==========

@app.post("/api/admin/users", response_model=schemas.UserOut)
def admin_create_user(body: schemas.AdminCreateUser,
                      current=Depends(require_role(["admin"])),
                      db: Session = Depends(get_db)):
    if crud.get_user_by_account(db, body.account_no):
        raise HTTPException(400, "账号已存在")
    pwd = body.password or DEFAULT_PASSWORD
    user = crud.create_user(db, body.account_no, pwd, body.role)
    if body.role == "student":
        if not (body.Sname and body.Ssex and body.Sdept):
            raise HTTPException(400, "学生需提供 Sname/Ssex/Sdept")
        crud.create_student(db, user.account_no, body.Sname, body.Ssex, body.Sdept, body.Sage)
    elif body.role == "teacher":
        if not body.Tname:
            raise HTTPException(400, "教师需提供 Tname")
        crud.create_teacher(db, user.account_no, body.Tname, body.Tdept, body.Tsex)
    return {"account_no": user.account_no, "role": user.role}

@app.post("/api/admin/users/reset-password")
def admin_reset_password(body: schemas.AdminResetPassword,
                         current=Depends(require_role(["admin"])),
                         db: Session = Depends(get_db)):
    if not crud.get_user_by_account(db, body.account_no):
        raise HTTPException(404, "用户不存在")
    new_pwd = body.new_password or DEFAULT_PASSWORD
    crud.set_user_password(db, body.account_no, new_pwd)
    return {"ok": True, "account_no": body.account_no, "reset_to_default": body.new_password is None}

@app.delete("/api/admin/users/{account_no}")
def admin_delete_user(account_no: str,
                      current=Depends(require_role(["admin"])),
                      db: Session = Depends(get_db)):
    if account_no == "12345678":
        raise HTTPException(400, "不可删除系统管理员")
    ok = crud.delete_user(db, account_no)
    if not ok:
        raise HTTPException(404, "用户不存在")
    return {"ok": True}

# 学生档案
@app.get("/api/admin/students", response_model=List[schemas.StudentOut])
def admin_list_students(current=Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    return [schemas.StudentOut(Sno=s.Sno, Sname=s.Sname, Ssex=s.Ssex, Sdept=s.Sdept, Sage=s.Sage)
            for s in crud.list_students(db)]

@app.get("/api/admin/students/{Sno}", response_model=schemas.StudentOut)
def admin_get_student(Sno: str, current=Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    s = crud.get_student(db, Sno)
    if not s:
        raise HTTPException(404, "学生不存在")
    return {"Sno": s.Sno, "Sname": s.Sname, "Ssex": s.Ssex, "Sdept": s.Sdept, "Sage": s.Sage}

@app.put("/api/admin/students/{Sno}", response_model=schemas.StudentOut)
def admin_update_student(Sno: str, body: schemas.StudentUpdate,
                         current=Depends(require_role(["admin"])),
                         db: Session = Depends(get_db)):
    s = crud.update_student(db, Sno, Sname=body.Sname, Ssex=body.Ssex, Sdept=body.Sdept, Sage=body.Sage)
    if not s:
        raise HTTPException(404, "学生不存在")
    return {"Sno": s.Sno, "Sname": s.Sname, "Ssex": s.Ssex, "Sdept": s.Sdept, "Sage": s.Sage}

# 教师档案
@app.get("/api/admin/teachers", response_model=List[schemas.TeacherOut])
def admin_list_teachers(current=Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    return [schemas.TeacherOut(Tno=t.Tno, Tname=t.Tname, Tdept=t.Tdept, Tsex=t.Tsex)
            for t in crud.list_teachers(db)]

@app.get("/api/admin/teachers/{Tno}", response_model=schemas.TeacherOut)
def admin_get_teacher(Tno: str, current=Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    t = crud.get_teacher(db, Tno)
    if not t:
        raise HTTPException(404, "教师不存在")
    return {"Tno": t.Tno, "Tname": t.Tname, "Tdept": t.Tdept, "Tsex": t.Tsex}

@app.put("/api/admin/teachers/{Tno}", response_model=schemas.TeacherOut)
def admin_update_teacher(Tno: str, body: schemas.TeacherUpdate,
                         current=Depends(require_role(["admin"])),
                         db: Session = Depends(get_db)):
    t = crud.update_teacher(db, Tno, Tname=body.Tname, Tdept=body.Tdept, Tsex=body.Tsex)
    if not t:
        raise HTTPException(404, "教师不存在")
    return {"Tno": t.Tno, "Tname": t.Tname, "Tdept": t.Tdept, "Tsex": t.Tsex}

# ========== 管理员：课程与选课成绩 ==========

@app.get("/api/admin/courses", response_model=List[schemas.CourseOut])
def admin_list_courses(current=Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    courses = crud.list_courses(db)
    counts = crud.get_enrolled_counts(db)
    return [{
        "Cno": c.Cno, "Ctno": c.Ctno, "Cname": c.Cname, "Ccredit": c.Ccredit,
        "enrolled": counts.get((c.Cno, c.Ctno), 0), "selected": False
    } for c in courses]

@app.post("/api/admin/courses", response_model=schemas.CourseOut)
def admin_create_course(body: schemas.CourseCreate,
                        current=Depends(require_role(["admin"])),
                        db: Session = Depends(get_db)):
    if not crud.get_teacher(db, body.Ctno):
        raise HTTPException(400, "教师不存在")
    if crud.course_exists(db, body.Cno, body.Ctno):
        raise HTTPException(409, "该教师已开设该课程")
    c = crud.create_course(db, body.Cno, body.Ctno, body.Cname, body.Ccredit)
    return {"Cno": c.Cno, "Ctno": c.Ctno, "Cname": c.Cname, "Ccredit": c.Ccredit,
            "enrolled": 0, "selected": False}

@app.delete("/api/admin/courses/{Cno}/{Ctno}")
def admin_delete_course(Cno: str, Ctno: str,
                        current=Depends(require_role(["admin"])),
                        db: Session = Depends(get_db)):
    ok = crud.delete_course(db, Cno, Ctno)
    if not ok:
        raise HTTPException(404, "课程不存在")
    return {"ok": True}

@app.get("/api/admin/enrollments", response_model=List[schemas.AdminEnrollmentOut])  # 改用 AdminEnrollmentOut
def admin_list_enrollments(Sno: Optional[str] = Query(None),
                           Cno: Optional[str] = Query(None),
                           Tno: Optional[str] = Query(None),
                           current=Depends(require_role(["admin"])),
                           db: Session = Depends(get_db)):
    rows = crud.list_enrollments(db, Sno=Sno, Cno=Cno, Tno=Tno)
    return [ _normalize_grade({
        "Sno": sc.Sno, "Sname": sname,
        "Cno": sc.Cno, "Tno": sc.Tno, "Cname": cname,
        "grade": sc.grade
    }) for sc, sname, cname in rows]

@app.put("/api/admin/enrollments/{Sno}/{Cno}/{Tno}/grade")
def admin_update_grade(Sno: str, Cno: str, Tno: str,
                       body: schemas.GradeUpdate,
                       current=Depends(require_role(["admin"])),
                       db: Session = Depends(get_db)):
    grade_val = None if (body.grade is None or body.grade == "") else int(body.grade)
    sc = crud.set_grade(db, Sno, Cno, Tno, grade_val)
    if not sc:
        raise HTTPException(404, "记录不存在")
    return {"ok": True}

@app.delete("/api/admin/enrollments/{Sno}/{Cno}/{Tno}")
def admin_unenroll(Sno: str, Cno: str, Tno: str,
                   current=Depends(require_role(["admin"])),
                   db: Session = Depends(get_db)):
    ok = crud.admin_unenroll(db, Sno, Cno, Tno)
    if not ok:
        raise HTTPException(404, "记录不存在")
    return {"ok": True}

# ========== 学生端 ==========

@app.get("/api/student/profile", response_model=schemas.StudentOut)
def student_profile(current=Depends(require_role(["student"])), db: Session = Depends(get_db)):
    s = crud.get_student(db, current["account_no"])
    if not s:
        raise HTTPException(404, "学生信息不存在")
    return {"Sno": s.Sno, "Sname": s.Sname, "Ssex": s.Ssex, "Sdept": s.Sdept, "Sage": s.Sage}

@app.put("/api/student/profile", response_model=schemas.StudentOut)
def student_profile_update(body: schemas.StudentSelfUpdate,
                           current=Depends(require_role(["student"])),
                           db: Session = Depends(get_db)):
    s = crud.update_student(db, current["account_no"],
                            Sname=body.Sname, Ssex=body.Ssex,
                            Sdept=body.Sdept, Sage=body.Sage)
    if not s:
        raise HTTPException(404, "学生信息不存在")
    return {"Sno": s.Sno, "Sname": s.Sname, "Ssex": s.Ssex, "Sdept": s.Sdept, "Sage": s.Sage}

@app.get("/api/student/courses", response_model=List[schemas.CourseOut])
def student_courses(current=Depends(require_role(["student"])), db: Session = Depends(get_db)):
    sno = current["account_no"]
    selected_pairs = {(x.Cno, x.Tno) for x in crud.list_student_selected(db, sno)}
    courses = crud.list_courses(db)
    counts = crud.get_enrolled_counts(db)
    return [{
        "Cno": c.Cno, "Ctno": c.Ctno, "Cname": c.Cname, "Ccredit": c.Ccredit,
        "enrolled": counts.get((c.Cno, c.Ctno), 0),
        "selected": (c.Cno, c.Ctno) in selected_pairs
    } for c in courses]

@app.post("/api/student/enroll")
def student_enroll(body: schemas.EnrollRequest,
                   current=Depends(require_role(["student"])),
                   db: Session = Depends(get_db)):
    sno = current["account_no"]
    if not crud.course_exists(db, body.Cno, body.Tno):
        raise HTTPException(404, "课程不存在")
    try:
        crud.enroll(db, sno, body.Cno, body.Tno)
    except IntegrityError:
        raise HTTPException(409, "不能重复选课")
    return {"ok": True}

@app.delete("/api/student/enroll/{Cno}/{Tno}")
def student_unenroll(Cno: str, Tno: str,
                     current=Depends(require_role(["student"])),
                     db: Session = Depends(get_db)):
    ok = crud.unenroll(db, current["account_no"], Cno, Tno)
    if not ok:
        raise HTTPException(404, "未选该课")
    return {"ok": True}

@app.get("/api/student/enrollments", response_model=List[schemas.StudentEnrollmentOut])
def student_my_enrollments(current=Depends(require_role(["student"])), db: Session = Depends(get_db)):
    sno = current["account_no"]
    rows = crud.list_enrollments_by_student(db, sno)
    return [ _normalize_grade({
        "Cno": sc.Cno,
        "Tno": sc.Tno,
        "Tname": tname,
        "Cname": cname,
        "Ccredit": ccredit,
        "grade": sc.grade
    }) for sc, cname, ccredit, tname in rows]

# ========== 教师端 ==========

@app.get("/api/teacher/profile", response_model=schemas.TeacherOut)
def teacher_profile(current=Depends(require_role(["teacher"])), db: Session = Depends(get_db)):
    t = crud.get_teacher(db, current["account_no"])
    if not t:
        raise HTTPException(404, "教师信息不存在")
    return {"Tno": t.Tno, "Tname": t.Tname, "Tdept": t.Tdept, "Tsex": t.Tsex}

@app.put("/api/teacher/profile", response_model=schemas.TeacherOut)
def teacher_profile_update(body: schemas.TeacherSelfUpdate,
                           current=Depends(require_role(["teacher"])),
                           db: Session = Depends(get_db)):
    t = crud.update_teacher(db, current["account_no"],
                            Tname=body.Tname, Tdept=body.Tdept, Tsex=body.Tsex)
    if not t:
        raise HTTPException(404, "教师信息不存在")
    return {"Tno": t.Tno, "Tname": t.Tname, "Tdept": t.Tdept, "Tsex": t.Tsex}

@app.get("/api/teacher/courses", response_model=List[schemas.CourseOut])
def teacher_courses(current=Depends(require_role(["teacher"])), db: Session = Depends(get_db)):
    tno = current["account_no"]
    courses = [c for c in crud.list_courses(db) if c.Ctno == tno]
    counts = crud.get_enrolled_counts(db)
    return [{
        "Cno": c.Cno, "Ctno": c.Ctno, "Cname": c.Cname, "Ccredit": c.Ccredit,
        "enrolled": counts.get((c.Cno, c.Ctno), 0), "selected": False
    } for c in courses]

@app.get("/api/teacher/enrollments", response_model=List[schemas.TeacherEnrollmentOut])
def teacher_enrollments(Cno: Optional[str] = Query(None),
                        search: Optional[str] = Query(None),
                        current=Depends(require_role(["teacher"])),
                        db: Session = Depends(get_db)):
    rows = crud.list_enrollments_by_teacher(db, current["account_no"], Cno=Cno, search=search)
    return [ _normalize_grade({
        "Sno": sc.Sno, "Sname": sname,
        "Cno": sc.Cno, "Cname": cname,
        "grade": sc.grade
    }) for sc, sname, cname in rows]

@app.put("/api/teacher/enrollments/{Sno}/{Cno}/grade")
def teacher_update_grade(Sno: str, Cno: str,
                         body: schemas.GradeUpdate,
                         current=Depends(require_role(["teacher"])),
                         db: Session = Depends(get_db)):
    grade_val = None if (body.grade is None or body.grade == "") else int(body.grade)
    sc = crud.set_grade(db, Sno, Cno, current["account_no"], grade_val)
    if not sc:
        raise HTTPException(404, "选课记录不存在")
    return {"ok": True}


@app.post("/api/auth/change-password")
def change_password(
    payload: schemas.ChangePasswordIn,
    current=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")

    user = crud.get_user_by_account(db, current["account_no"])
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 校验旧密码
    if not auth.verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")

    # 设置新密码（内部完成加密）
    crud.set_user_password(db, user.account_no, payload.new_password)
    return {"ok": True, "msg": "密码已更新"}


def _normalize_grade(row: dict) -> dict:
    g = row.get("grade", None)
    if g is None or g == "":
        return {**row, "grade": None}
    return {**row, "grade": str(g)}