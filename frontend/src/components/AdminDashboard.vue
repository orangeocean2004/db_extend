<template>
  <div class="admin-layout">
    <!-- 左侧折叠导航 -->
    <aside class="sidebar">
      <div class="brand">Admin Console</div>

      <div
        v-for="(group, gIdx) in navGroups"
        :key="group.title"
        class="nav-group"
      >
        <div class="nav-group-header" @click="toggleGroup(gIdx)">
          <span>{{ group.title }}</span>
          <span class="arrow" :class="{ open: !group.collapsed }">▾</span>
        </div>

        <transition name="collapse">
          <ul v-show="!group.collapsed" class="nav-items">
            <li
              v-for="item in group.items"
              :key="item.key"
              :class="{ active: activeKey === item.key }"
              @click="activate(item.key)"
            >
              {{ item.label }}
            </li>
          </ul>
        </transition>
      </div>

      <div class="sidebar-bottom">
        <button class="logout" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 右侧内容 -->
    <main class="main">
      <!-- 顶部条 -->
      <header class="topbar">
        <div class="title">{{ currentTitle }}</div>
        <div class="me">账号：{{ me?.account_no }}（{{ me?.role }}）</div>
      </header>

      <!-- 面板区域 -->
      <section class="panel">
        <!-- 创建用户 -->
        <div v-if="activeKey==='create-user'" class="card">
          <h3>创建用户</h3>
          <div class="form-grid">
            <input v-model="userForm.account_no" placeholder="账号(8位)" />
            <input v-model="userForm.password" type="password" placeholder="密码(留空用默认)" />
            <select v-model="userForm.role">
              <option value="student">student</option>
              <option value="teacher">teacher</option>
              <option value="admin">admin</option>
            </select>

            <template v-if="userForm.role==='student'">
              <input v-model="userForm.Sname" placeholder="学生姓名(必填)" />
              <input v-model="userForm.Ssex" placeholder="性别(必填)" />
              <input v-model="userForm.Sdept" placeholder="专业(必填)" />
              <input v-model.number="userForm.Sage" type="number" placeholder="年龄(可选)" />
            </template>
            <template v-else-if="userForm.role==='teacher'">
              <input v-model="userForm.Tname" placeholder="教师姓名(必填)" />
              <input v-model="userForm.Tdept" placeholder="院系(可选)" />
              <input v-model="userForm.Tsex" placeholder="性别(可选)" />
            </template>

            <button class="primary" @click="createUser" :disabled="loadingUser">
              {{ loadingUser ? '提交中...' : '创建用户' }}
            </button>
            <p v-if="msgUser" :class="msgUserOk ? 'ok' : 'err'">{{ msgUser }}</p>
          </div>
        </div>

        <!-- 用户列表/重置密码/删除 -->
        <div v-else-if="activeKey==='users'" class="card">
          <h3>用户列表</h3>
          <div class="toolbar">
            <label>角色：</label>
            <select v-model="usersRole" @change="loadUsers">
              <option value="student">student</option>
              <option value="teacher">teacher</option>
              <option value="admin">admin</option>
            </select>
            <button @click="loadUsers">刷新</button>
          </div>

          <table class="table">
            <thead>
              <tr>
                <th>账号</th>
                <th v-if="usersRole!=='admin'">姓名</th>
                <th v-if="usersRole==='student'">性别</th>
                <th v-if="usersRole==='student'">专业</th>
                <th v-if="usersRole==='student'">年龄</th>
                <th v-if="usersRole==='teacher'">院系</th>
                <th v-if="usersRole==='teacher'">性别</th>
                <th style="width:280px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.account_no || u.Sno || u.Tno">
                <td>{{ u.account_no || u.Sno || u.Tno }}</td>
                <td v-if="usersRole!=='admin'">{{ u.Sname || u.Tname }}</td>
                <td v-if="usersRole==='student'">{{ u.Ssex }}</td>
                <td v-if="usersRole==='student'">{{ u.Sdept }}</td>
                <td v-if="usersRole==='student'">{{ u.Sage }}</td>
                <td v-if="usersRole==='teacher'">{{ u.Tdept }}</td>
                <td v-if="usersRole==='teacher'">{{ u.Tsex }}</td>
                <td>
                  <div class="row-actions">
                    <input v-model="resetPwd[u.account_no || u.Sno || u.Tno]" placeholder="新密码(可空)" />
                    <button @click="resetPassword(u)">重置密码</button>
                    <button class="danger" @click="deleteUser(u)">删除用户</button>
                  </div>
                </td>
              </tr>
              <tr v-if="users.length===0">
                <td :colspan="usersRole==='admin'?2:8" class="empty">暂无数据</td>
              </tr>
            </tbody>
          </table>
          <p v-if="msgUsers" :class="msgUsersOk ? 'ok' : 'err'">{{ msgUsers }}</p>
        </div>

        <!-- 新增：编辑学生信息 -->
        <div v-else-if="activeKey==='edit-student'" class="card">
          <h3>编辑学生信息</h3>
          <div class="toolbar">
            <input v-model="stuEdit.Sno" placeholder="学号(Sno)" />
            <button @click="fetchStudent">查询</button>
          </div>

          <div v-if="stuLoaded" class="form-grid">
            <input v-model="stuEdit.Sname" placeholder="姓名" />
            <input v-model="stuEdit.Ssex" placeholder="性别" />
            <input v-model="stuEdit.Sdept" placeholder="专业" />
            <input type="number" v-model.number="stuEdit.Sage" placeholder="年龄" />
            <button class="primary" @click="saveStudent" :disabled="savingStu">
              {{ savingStu ? '保存中...' : '保存' }}
            </button>
          </div>
          <p v-if="msgStu" :class="msgStuOk ? 'ok' : 'err'">{{ msgStu }}</p>
        </div>

        <!-- 创建课程 -->
        <div v-else-if="activeKey==='create-course'" class="card">
          <h3>创建课程</h3>
          <div class="form-grid">
            <input v-model="courseForm.Cno" placeholder="课程号" />
            <input v-model="courseForm.Ctno" placeholder="教师工号(8位)" />
            <input v-model="courseForm.Cname" placeholder="课程名称" />
            <input v-model.number="courseForm.Ccredit" type="number" step="0.5" placeholder="学分" />
            <button class="primary" @click="createCourse" :disabled="loadingCourse">
              {{ loadingCourse ? '提交中...' : '创建课程' }}
            </button>
            <p v-if="msgCourse" :class="msgCourseOk ? 'ok' : 'err'">{{ msgCourse }}</p>
          </div>
        </div>

        <!-- 课程列表 -->
        <div v-else-if="activeKey==='courses'" class="card">
          <h3>全部课程</h3>
          <div class="toolbar">
            <button @click="loadCourses">刷新</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>课程号</th><th>教师号</th><th>课程名</th><th>学分</th><th>已选人数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in courses" :key="c.Cno+'_'+c.Ctno">
                <td>{{ c.Cno }}</td>
                <td>{{ c.Ctno }}</td>
                <td>{{ c.Cname }}</td>
                <td>{{ c.Ccredit }}</td>
                <td>{{ c.enrolled }}</td>
              </tr>
              <tr v-if="courses.length===0"><td colspan="5" class="empty">暂无课程</td></tr>
            </tbody>
          </table>
        </div>

        <!-- 选课与成绩 -->
        <div v-else-if="activeKey==='enrollments'" class="card">
          <h3>选课与成绩</h3>
          <div class="toolbar">
            <input v-model="enrollFilter.Sno" placeholder="学号(Sno)" />
            <input v-model="enrollFilter.Cno" placeholder="课程号(Cno)" />
            <input v-model="enrollFilter.Tno" placeholder="教师号(Tno)" />
            <button @click="loadEnrollments">查询</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>学号</th><th>学生姓名</th><th>课程号</th><th>课程名</th><th>教师号</th><th style="width:250px;">成绩</th><th style="width:160px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in enrollments" :key="e.Sno+'_'+e.Cno+'_'+e.Tno">
                <td>{{ e.Sno }}</td>
                <td>{{ e.Sname }}</td>
                <td>{{ e.Cno }}</td>
                <td>{{ e.Cname }}</td>
                <td>{{ e.Tno }}</td>
                <td>
                  <div class="row-actions">
                    <input type="number" min="0" max="100" v-model.number="editGrade[keyOf(e)]" placeholder="0-100" />
                    <span class="muted" v-if="e.grade!==null">当前：{{ e.grade }}</span>
                    <span class="muted" v-else>当前：无</span>
                  </div>
                </td>
                <td>
                  <div class="row-actions">
                    <button @click="saveGrade(e)">保存</button>
                    <button class="warning" @click="clearGrade(e)">清空</button>
                    <button class="danger" @click="adminUnenroll(e)">退课</button>
                  </div>
                </td>
              </tr>
              <tr v-if="enrollments.length===0"><td colspan="7" class="empty">暂无记录</td></tr>
            </tbody>
          </table>
          <p v-if="msgEnroll" :class="msgEnrollOk ? 'ok' : 'err'">{{ msgEnroll }}</p>
        </div>

        <div v-else class="card">
          <h3>欢迎使用管理员后台</h3>
          <p>从左侧选择一个功能开始。</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const me = ref(null)

// 导航分组
const navGroups = reactive([
  {
    title: '用户管理',
    collapsed: false,
    items: [
      { key: 'create-user', label: '创建用户' },
      { key: 'users', label: '用户列表 / 重置密码 / 删除' },
      { key: 'edit-student', label: '编辑学生信息' },
    ],
  },
  {
    title: '课程管理',
    collapsed: false,
    items: [
      { key: 'create-course', label: '创建课程' },
      { key: 'courses', label: '课程列表' },
    ],
  },
  {
    title: '选课与成绩',
    collapsed: false,
    items: [{ key: 'enrollments', label: '查询与改分' }],
  },
])

const titles = {
  'create-user': '创建用户',
  users: '用户列表',
  'edit-student': '编辑学生信息',
  'create-course': '创建课程',
  courses: '课程列表',
  enrollments: '选课与成绩',
}
const activeKey = ref('create-user')
const currentTitle = computed(() => titles[activeKey.value] || '管理员后台')

function toggleGroup(i) { navGroups[i].collapsed = !navGroups[i].collapsed }
function activate(key) { activeKey.value = key; preloadFor(key) }
function logout(){ localStorage.removeItem('token'); router.push('/login') }

onMounted(async () => {
  try {
    me.value = (await axios.get('/api/auth/me')).data
    if (me.value.role !== 'admin') return router.replace('/login')
    preloadFor(activeKey.value)
  } catch {
    router.replace('/login')
  }
})

function preloadFor(key) {
  if (key === 'courses') loadCourses()
  if (key === 'users') loadUsers()
  if (key === 'enrollments') loadEnrollments()
}

/* ========== 创建用户 ========== */
const userForm = ref({
  account_no: '',
  password: '',
  role: 'student',
  Sname: '',
  Ssex: '',
  Sdept: '',
  Sage: null,
  Tname: '',
  Tdept: '',
  Tsex: '',
})
const loadingUser = ref(false)
const msgUser = ref(''); const msgUserOk = ref(false)

async function createUser() {
  msgUser.value=''; msgUserOk.value=false; loadingUser.value=true
  try {
    await axios.post('/api/admin/users', userForm.value)
    msgUserOk.value=true; msgUser.value='创建成功'
    userForm.value.account_no=''; userForm.value.password=''
  } catch(e) {
    msgUser.value = e?.response?.data?.detail || '创建失败'
  } finally { loadingUser.value=false }
}

/* ========== 用户列表/重置/删除 ========== */
const usersRole = ref('student')
const users = ref([])
const resetPwd = reactive({})
const msgUsers = ref(''); const msgUsersOk = ref(false)

async function loadUsers() {
  msgUsers.value=''; msgUsersOk.value=false
  if (usersRole.value === 'student') {
    const rows = (await axios.get('/api/admin/students')).data
    users.value = rows.map(x => ({ ...x, account_no: x.Sno }))
  } else if (usersRole.value === 'teacher') {
    const rows = (await axios.get('/api/admin/teachers')).data
    users.value = rows.map(x => ({ ...x, account_no: x.Tno }))
  } else {
    users.value = []
    msgUsers.value = '管理员列表未提供，支持在下方输入账号进行操作'
  }
}

async function resetPassword(u) {
  try {
    await axios.post('/api/admin/users/reset-password', {
      account_no: u.account_no,
      new_password: resetPwd[u.account_no] || null
    })
    msgUsersOk.value = true; msgUsers.value = `已重置 ${u.account_no}`
    resetPwd[u.account_no] = ''
  } catch(e) {
    msgUsersOk.value = false; msgUsers.value = e?.response?.data?.detail || '重置失败'
  }
}

async function deleteUser(u) {
  if (!confirm(`确认删除用户 ${u.account_no} 吗？`)) return
  try {
    await axios.delete(`/api/admin/users/${u.account_no}`)
    msgUsersOk.value = true; msgUsers.value = `已删除 ${u.account_no}`
    await loadUsers()
  } catch(e) {
    msgUsersOk.value = false; msgUsers.value = e?.response?.data?.detail || '删除失败'
  }
}

/* ========== 课程 ========== */
const courseForm = ref({ Cno:'', Ctno:'', Cname:'', Ccredit:1 })
const loadingCourse = ref(false)
const msgCourse = ref(''); const msgCourseOk = ref(false)
const courses = ref([])

async function createCourse(){
  msgCourse.value=''; msgCourseOk.value=false; loadingCourse.value=true
  try{
    await axios.post('/api/admin/courses', courseForm.value)
    msgCourseOk.value=true; msgCourse.value='创建成功'
    courseForm.value.Cname=''; courseForm.value.Ccredit=1
    await loadCourses()
  }catch(e){
    msgCourse.value = e?.response?.data?.detail || '创建失败'
  }finally{ loadingCourse.value=false }
}

async function loadCourses(){
  courses.value = (await axios.get('/api/admin/courses')).data
}

/* ========== 选课与成绩 ========== */
const enrollments = ref([])
const enrollFilter = reactive({ Sno:'', Cno:'', Tno:'' })
const editGrade = reactive({})
const msgEnroll = ref(''); const msgEnrollOk = ref(false)

function keyOf(e) { return `${e.Sno}_${e.Cno}_${e.Tno}` }

async function loadEnrollments() {
  msgEnroll.value=''; msgEnrollOk.value=false
  const params = {}
  if (enrollFilter.Sno) params.Sno = enrollFilter.Sno
  if (enrollFilter.Cno) params.Cno = enrollFilter.Cno
  if (enrollFilter.Tno) params.Tno = enrollFilter.Tno
  const rows = (await axios.get('/api/admin/enrollments', { params })).data
  enrollments.value = rows.map(r => ({ ...r, Tno: r.Tno ?? null }))
  enrollments.value.forEach(r => { if (editGrade[keyOf(r)] === undefined) editGrade[keyOf(r)] = r.grade })
}

async function saveGrade(e) {
  try {
    const g = editGrade[keyOf(e)]
    const body = { grade: (g === '' || g === null || g === undefined) ? '' : String(g) }
    await axios.put(`/api/admin/enrollments/${e.Sno}/${e.Cno}/${e.Tno}/grade`, body)
    msgEnrollOk.value = true; msgEnroll.value = '成绩已保存'
    await loadEnrollments()
  } catch(err) {
    msgEnrollOk.value = false; msgEnroll.value = err?.response?.data?.detail || '保存失败'
  }
}
async function clearGrade(e) {
  editGrade[keyOf(e)] = ''
  await saveGrade(e)
}
async function adminUnenroll(e) {
  if (!confirm(`确认将 ${e.Sno} 从课程 ${e.Cno}/${e.Tno} 退课吗？`)) return
  try {
    await axios.delete(`/api/admin/enrollments/${e.Sno}/${e.Cno}/${e.Tno}`)
    msgEnrollOk.value = true; msgEnroll.value = '已退课'
    await loadEnrollments()
  } catch(err) {
    msgEnrollOk.value = false; msgEnroll.value = err?.response?.data?.detail || '退课失败'
  }
}

/* ========== 新增：编辑学生信息 ========== */
const stuEdit = reactive({ Sno:'', Sname:'', Ssex:'', Sdept:'', Sage:null })
const stuLoaded = ref(false)
const savingStu = ref(false)
const msgStu = ref(''); const msgStuOk = ref(false)

async function fetchStudent(){
  msgStu.value=''; msgStuOk.value=false; stuLoaded.value = false
  if (!stuEdit.Sno) { msgStu.value = '请先输入学号'; return }
  try{
    const data = (await axios.get(`/api/admin/students/${stuEdit.Sno}`)).data
    stuEdit.Sname = data.Sname || ''
    stuEdit.Ssex = data.Ssex || ''
    stuEdit.Sdept = data.Sdept || ''
    stuEdit.Sage = data.Sage ?? null
    stuLoaded.value = true
  }catch(e){
    msgStu.value = e?.response?.data?.detail || '未找到该学生'
  }
}

async function saveStudent(){
  msgStu.value=''; msgStuOk.value=false; savingStu.value=true
  try{
    await axios.put(`/api/admin/students/${stuEdit.Sno}`, {
      Sname: stuEdit.Sname,
      Ssex: stuEdit.Ssex,
      Sdept: stuEdit.Sdept,
      Sage: stuEdit.Sage
    })
    msgStuOk.value = true; msgStu.value = '已保存修改'
  }catch(e){
    msgStuOk.value = false; msgStu.value = e?.response?.data?.detail || '保存失败'
  }finally{
    savingStu.value=false
  }
}
</script>

<style scoped>
/* 布局 */
.admin-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: #f7f7f9;
}
.sidebar {
  background: #fff;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.brand {
  font-weight: 700;
  padding: 16px 18px;
  font-size: 18px;
  border-bottom: 1px solid #f0f0f0;
}

.nav-group { padding: 8px 0; }
.nav-group-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 18px; cursor: pointer; color:#333; font-weight:600;
}
.nav-items { list-style: none; margin: 0; padding: 0; }
.nav-items li {
  padding: 10px 22px; cursor: pointer; color: #555; transition: background .2s;
}
.nav-items li:hover { background: #f5f5f7; }
.nav-items li.active { background: #eee; color: #222; font-weight: 600; }
.arrow { transition: transform .2s; }
.arrow.open { transform: rotate(180deg); }

.sidebar-bottom { margin-top: auto; padding: 16px; border-top: 1px solid #f0f0f0; }
.logout {
  width: 100%; padding: 10px 12px; border: 1px solid #ff6b6b; color:#ff6b6b;
  background: #fff; border-radius: 6px; cursor: pointer;
}
.logout:hover { background: #fff5f5; }

.main { display: flex; flex-direction: column; }
.topbar {
  height: 56px; background: #fff; border-bottom: 1px solid #eee;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px;
}
.topbar .title { font-size: 16px; font-weight: 600; }
.topbar .me { color:#666; }

.panel { padding: 16px; }
.card {
  background: #fff; border: 1px solid #eee; border-radius: 8px;
  padding: 16px;
}

/* 表单与表格 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
input, select, button {
  padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; outline: none;
  background: #fff; font-size: 14px;
}
input:focus, select:focus { border-color: #409eff; }
button { cursor: pointer; }
button.primary { background: #409eff; color:#fff; border-color:#409eff; }
button.primary:hover { filter: brightness(0.98); }
button.danger { background: #ff6b6b; color:#fff; border-color:#ff6b6b; }
button.warning { background: #ffaa2b; color:#fff; border-color:#ffaa2b; }

.toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }

.table { width: 100%; border-collapse: collapse; background: #fff; }
.table th, .table td { border: 1px solid #f0f0f0; padding: 10px; text-align: left; }
.table thead { background: #fafafa; }
.empty { text-align: center; color:#888; }

.row-actions { display: flex; gap: 8px; align-items: center; }
.muted { color:#999; font-size: 12px; }

.ok { color:#2c7; margin-top: 8px; }
.err { color:#d33; margin-top: 8px; }

/* 折叠动效 */
.collapse-enter-active, .collapse-leave-active { transition: all .2s ease; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; transform: translateY(-6px); }
</style>