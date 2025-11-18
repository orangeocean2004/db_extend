<template>
  <div class="student-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="brand">Student Console</div>

      <div v-for="(group, i) in navGroups" :key="group.title" class="nav-group">
        <div class="nav-group-header" @click="toggleGroup(i)">
          <span>{{ group.title }}</span>
          <span class="arrow" :class="{ open: !group.collapsed }">▾</span>
        </div>
        <transition name="collapse">
          <ul v-show="!group.collapsed" class="nav-items">
            <li v-for="it in group.items"
                :key="it.key"
                :class="{ active: activeKey===it.key }"
                @click="activate(it.key)">
              {{ it.label }}
            </li>
          </ul>
        </transition>
      </div>

      <div class="sidebar-bottom">
        <button class="logout" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 主区域 -->
    <main class="main">
      <header class="topbar">
        <div class="title">{{ currentTitle }}</div>
        <div class="me">
          学生：{{ displayName }}（{{ profile?.Sno || me?.account_no }}）
        </div>
      </header>

      <section class="panel">
        <!-- 可选课程 -->
        <div v-if="activeKey==='courses'" class="card">
          <h3>可选课程</h3>
          <div class="toolbar">
            <button @click="loadCourses">刷新</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>课程号</th><th>教师号</th><th>课程名</th><th>学分</th><th>已选人数</th><th style="width:160px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in courses" :key="c.Cno+'_'+c.Ctno">
                <td>{{ c.Cno }}</td>
                <td>{{ c.Ctno }}</td>
                <td>
                  {{ c.Cname }}
                  <span v-if="c.selected" class="tag">已选</span>
                </td>
                <td>{{ c.Ccredit }}</td>
                <td>{{ c.enrolled }}</td>
                <td>
                  <button v-if="!c.selected" class="primary" @click="enroll(c)">选课</button>
                  <button v-else class="danger" @click="unenroll(c)">退课</button>
                </td>
              </tr>
              <tr v-if="courses.length===0"><td colspan="6" class="empty">暂无课程</td></tr>
            </tbody>
          </table>
          <p v-if="msgCourse" :class="msgCourseOk?'ok':'err'">{{ msgCourse }}</p>
        </div>

        <!-- 我的课程与成绩 -->
        <div v-else-if="activeKey==='my-enrollments'" class="card">
          <h3>我的课程与成绩</h3>
          <div class="toolbar">
            <button @click="loadMyEnrollments">刷新</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>课程号</th><th>课程名</th><th>教师</th><th>学分</th><th>成绩</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in myEnrollments" :key="e.Cno+'_'+e.Tno">
                <td>{{ e.Cno }}</td>
                <td>{{ e.Cname }}</td>
                <td>{{ e.Tname }}</td>
                <td>{{ e.Ccredit }}</td>
                <td>{{ e.grade===null ? '—' : e.grade }}</td>
              </tr>
              <tr v-if="myEnrollments.length===0"><td colspan="5" class="empty">暂无选课</td></tr>
            </tbody>
          </table>
        </div>

        <!-- 个人资料 -->
        <div v-else-if="activeKey==='profile'" class="card">
          <h3>个人资料</h3>
          <div class="form-grid">
            <input v-model="profileForm.Sname" placeholder="姓名" />
            <input v-model="profileForm.Ssex" placeholder="性别" />
            <input v-model="profileForm.Sdept" placeholder="专业" />
            <input type="number" v-model.number="profileForm.Sage" placeholder="年龄" />
            <button class="primary" @click="saveProfile" :disabled="savingProfile">
              {{ savingProfile ? '保存中...' : '保存' }}
            </button>
            <p v-if="msgProfile" :class="msgProfileOk?'ok':'err'">{{ msgProfile }}</p>
          </div>
        </div>

        <!-- 修改密码 -->
        <div v-else-if="activeKey==='password'" class="card">
          <h3>修改密码</h3>
          <div class="form-grid">
            <input type="password" v-model="pwdForm.old_password" placeholder="当前密码" />
            <input type="password" v-model="pwdForm.new_password" placeholder="新密码(至少6位)" />
            <input type="password" v-model="pwdForm.confirm" placeholder="确认新密码" />
            <button class="primary" @click="changePassword" :disabled="changingPwd">
              {{ changingPwd ? '提交中...' : '修改密码' }}
            </button>
            <p v-if="msgPwd" :class="pwdOk ? 'ok' : 'err'">{{ msgPwd }}</p>
          </div>
        </div>

        <div v-else class="card">
          <h3>欢迎</h3>
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
const profile = ref(null)

// 左侧导航
const navGroups = reactive([
  { title: '课程中心', collapsed: false, items: [{ key: 'courses', label: '可选课程' }] },
  { title: '我的学习', collapsed: false, items: [{ key: 'my-enrollments', label: '我的课程与成绩' }] },
  { title: '个人信息', collapsed: false, items: [
      { key: 'profile', label: '个人资料' },
      { key: 'password', label: '修改密码' },   // 新增
    ] },
])

const titles = {
  courses: '可选课程',
  'my-enrollments': '我的课程与成绩',
  profile: '个人资料',
  password: '修改密码',
}
const activeKey = ref('courses')
const currentTitle = computed(() => titles[activeKey.value] || '学生后台')

// 顶部显示姓名
const displayName = computed(() => profile.value?.Sname || me.value?.name || '')

function toggleGroup(i){ navGroups[i].collapsed = !navGroups[i].collapsed }
function activate(k){ activeKey.value = k; preloadFor(k) }
function logout(){
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(async () => {
  try {
    me.value = (await axios.get('/api/auth/me')).data
    if (me.value.role !== 'student') return router.replace('/login')
    await loadProfile()
    preloadFor(activeKey.value)
  } catch {
    router.replace('/login')
  }
})

function preloadFor(k){
  if (k === 'courses') loadCourses()
  if (k === 'my-enrollments') loadMyEnrollments()
  if (k === 'profile') syncProfileForm()
}

/* 个人资料 */
async function loadProfile(){
  profile.value = (await axios.get('/api/student/profile')).data
  syncProfileForm()
}
const profileForm = reactive({ Sname:'', Ssex:'', Sdept:'', Sage:null })
function syncProfileForm(){
  if (!profile.value) return
  profileForm.Sname = profile.value.Sname || ''
  profileForm.Ssex = profile.value.Ssex || ''
  profileForm.Sdept = profile.value.Sdept || ''
  profileForm.Sage = profile.value.Sage ?? null
}
const savingProfile = ref(false)
const msgProfile = ref(''); const msgProfileOk = ref(false)
async function saveProfile(){
  msgProfile.value=''; msgProfileOk.value=false; savingProfile.value=true
  try{
    const data = (await axios.put('/api/student/profile', profileForm)).data
    profile.value = data; msgProfileOk.value = true; msgProfile.value='已保存'
  }catch(e){
    msgProfile.value = e?.response?.data?.detail || '保存失败'
  }finally{ savingProfile.value=false }
}

/* 修改密码 */
const pwdForm = reactive({ old_password:'', new_password:'', confirm:'' })
const changingPwd = ref(false)
const msgPwd = ref(''); const pwdOk = ref(false)

async function changePassword(){
  msgPwd.value = ''; pwdOk.value = false

  // 简单前端校验
  if (!pwdForm.old_password || !pwdForm.new_password) {
    msgPwd.value = '请输入当前密码与新密码'
    return
  }
  if (pwdForm.new_password.length < 6) {
    msgPwd.value = '新密码至少 6 位'
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm) {
    msgPwd.value = '两次输入的新密码不一致'
    return
  }
  if (pwdForm.new_password === pwdForm.old_password) {
    msgPwd.value = '新密码不能与当前密码相同'
    return
  }

  changingPwd.value = true
  try {
    // 后端常见路径：/api/auth/change-password
    await axios.post('/api/auth/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    pwdOk.value = true
    msgPwd.value = '修改成功，请重新登录'
    setTimeout(() => logout(), 1000)
  } catch (e) {
    msgPwd.value = e?.response?.data?.detail || '修改失败'
  } finally {
    changingPwd.value = false
  }
}

/* 可选课程 */
const courses = ref([])
const msgCourse = ref(''); const msgCourseOk = ref(false)

async function loadCourses(){
  msgCourse.value=''; msgCourseOk.value=false
  courses.value = (await axios.get('/api/student/courses')).data
}
async function enroll(c){
  try{
    await axios.post('/api/student/enroll', { Cno: c.Cno, Tno: c.Ctno })
    msgCourseOk.value = true; msgCourse.value = '选课成功'
    await loadCourses(); await loadMyEnrollments()
  }catch(e){
    msgCourseOk.value = false; msgCourse.value = e?.response?.data?.detail || '选课失败'
  }
}
async function unenroll(c){
  if(!confirm(`确认从 ${c.Cname}(${c.Cno}/${c.Ctno}) 退课？`)) return
  try{
    await axios.delete(`/api/student/enroll/${c.Cno}/${c.Ctno}`)
    msgCourseOk.value = true; msgCourse.value = '已退课'
    await loadCourses(); await loadMyEnrollments()
  }catch(e){
    msgCourseOk.value = false; msgCourse.value = e?.response?.data?.detail || '退课失败'
  }
}

/* 我的课程与成绩 */
const myEnrollments = ref([])
async function loadMyEnrollments(){
  myEnrollments.value = (await axios.get('/api/student/enrollments')).data
}
</script>

<style scoped>
.student-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: #f7f7f9;
}
.sidebar {
  background: #fff; border-right: 1px solid #eee;
  display: flex; flex-direction: column;
}
.brand { font-weight: 700; padding: 16px 18px; font-size: 18px; border-bottom: 1px solid #f0f0f0; }

.nav-group { padding: 8px 0; }
.nav-group-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 18px; cursor: pointer; color:#333; font-weight:600;
}
.nav-items { list-style:none; margin:0; padding:0; }
.nav-items li { padding:10px 22px; cursor:pointer; color:#555; transition:background .2s; }
.nav-items li:hover { background:#f5f5f7; }
.nav-items li.active { background:#eee; color:#222; font-weight:600; }
.arrow { transition: transform .2s; }
.arrow.open { transform: rotate(180deg); }

.sidebar-bottom { margin-top:auto; padding:16px; border-top:1px solid #f0f0f0; }
.logout { width:100%; padding:10px 12px; border:1px solid #ff6b6b; color:#ff6b6b; background:#fff; border-radius:6px; cursor:pointer; }
.logout:hover { background:#fff5f5; }

.main { display:flex; flex-direction:column; }
.topbar {
  height:56px; background:#fff; border-bottom:1px solid #eee;
  display:flex; align-items:center; justify-content:space-between; padding:0 16px;
}
.topbar .title { font-size:16px; font-weight:600; }
.topbar .me { color:#666; }

.panel { padding:16px; }
.card { background:#fff; border:1px solid #eee; border-radius:8px; padding:16px; }

/* 表单/表格 */
.form-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:10px; }
input, select, button { padding:10px 12px; border:1px solid #ddd; border-radius:6px; background:#fff; font-size:14px; }
input:focus, select:focus { border-color:#409eff; }
button { cursor:pointer; }
button.primary { background:#409eff; color:#fff; border-color:#409eff; }
button.danger { background:#ff6b6b; color:#fff; border-color:#ff6b6b; }

.toolbar { display:flex; gap:8px; align-items:center; margin-bottom:12px; }

.table { width:100%; border-collapse:collapse; background:#fff; }
.table th, .table td { border:1px solid #f0f0f0; padding:10px; text-align:left; }
.table thead { background:#fafafa; }
.empty { text-align:center; color:#888; }

.tag { margin-left:6px; padding:2px 6px; background:#eef5ff; color:#3a7bfd; border-radius:10px; font-size:12px; }

.ok { color:#2c7; margin-top:8px; }
.err { color:#d33; margin-top:8px; }

/* 折叠动效 */
.collapse-enter-active, .collapse-leave-active { transition: all .2s ease; }
.collapse-enter-from, .collapse-leave-to { opacity:0; transform: translateY(-6px); }
</style>