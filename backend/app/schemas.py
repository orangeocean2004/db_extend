from pydantic import BaseModel
from typing import Optional, List

# ========== 管理员创建用户 ==========
class AdminCreateUser(BaseModel):
    account_no: str
    password: Optional[str] = None
    role: str
    Sname: Optional[str] = None
    Ssex: Optional[str] = None
    Sdept: Optional[str] = None
    Sage: Optional[int] = None
    Tname: Optional[str] = None
    Tdept: Optional[str] = None
    Tsex: Optional[str] = None

class UserOut(BaseModel):
    account_no: str
    role: str

# ========== 课程相关 ==========
class CourseCreate(BaseModel):
    Cno: str
    Ctno: str
    Cname: str
    Ccredit: float

class CourseOut(BaseModel):
    Cno: str
    Ctno: str
    Cname: str
    Ccredit: float
    enrolled: int
    selected: bool

class EnrollRequest(BaseModel):
    Cno: str
    Tno: str

# ========== 密码相关 ==========
class AdminResetPassword(BaseModel):
    account_no: str
    new_password: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ========== 成绩与选课记录（管理员 / 教师） ==========
class GradeUpdate(BaseModel):
    grade: Optional[str] = None

class EnrollmentOut(BaseModel):
    Sno: str
    Sname: Optional[str] = None
    Cno: str
    Tno: str
    Cname: Optional[str] = None
    grade: Optional[str] = None

# ========== 档案 ==========
class StudentOut(BaseModel):
    Sno: str
    Sname: Optional[str] = None
    Ssex: Optional[str] = None
    Sdept: Optional[str] = None
    Sage: Optional[int] = None

class TeacherOut(BaseModel):
    Tno: str
    Tname: Optional[str] = None
    Tdept: Optional[str] = None
    Tsex: Optional[str] = None

class StudentUpdate(BaseModel):
    Sname: Optional[str] = None
    Ssex: Optional[str] = None
    Sdept: Optional[str] = None
    Sage: Optional[int] = None

class TeacherUpdate(BaseModel):
    Tname: Optional[str] = None
    Tdept: Optional[str] = None
    Tsex: Optional[str] = None

class StudentSelfUpdate(BaseModel):
    Sname: Optional[str] = None
    Ssex: Optional[str] = None
    Sdept: Optional[str] = None
    Sage: Optional[int] = None

class StudentEnrollmentOut(BaseModel):
    Cno: str
    Tno: str
    Tname: Optional[str] = None   # 新增老师姓名
    Cname: Optional[str] = None
    Ccredit: Optional[float] = None
    grade: Optional[str] = None

class TeacherSelfUpdate(BaseModel):
    Tname: Optional[str] = None
    Tdept: Optional[str] = None
    Tsex: Optional[str] = None

class TeacherEnrollmentOut(BaseModel):
    Sno: str
    Sname: Optional[str] = None
    Cno: str
    Cname: Optional[str] = None
    grade: Optional[str] = None
    
# ========== 通用：修改密码 ==========
class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str