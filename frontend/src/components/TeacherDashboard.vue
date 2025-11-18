<template>
  <div class="teacher-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="brand">Teacher Console</div>

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
          教师：{{ displayName }}（{{ profile?.Tno || me?.account_no }}）
        </div>
      </header>

      <section class="panel">
        <!-- 我的课程 -->
        <div v-if="activeKey==='courses'" class="card">
          <h3>我的课程</h3>
          <div class="toolbar">
            <button @click="loadCourses">刷新</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>课程号</th><th>课程名</th><th>学分</th><th>已选人数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in courses" :key="c.Cno+'_'+c.Ctno">
                <td>{{ c.Cno }}</td>
                <td>{{ c.Cname }}</td>
                <td>{{ c.Ccredit }}</td>
                <td>{{ c.enrolled }}</td>
              </tr>
              <tr v-if="courses.length===0"><td colspan="4" class="empty">暂无课程</td></tr>
            </tbody>
          </table>
        </div>

        <!-- 选课名单与成绩 -->
        <div v-else-if="activeKey==='enrollments'" class="card">
          <h3>选课名单与成绩</h3>
          <div class="toolbar">
            <label>课程：</label>
            <select v-model="enrollCourse" @change="loadEnrollments">
              <option value="">全部</option>
              <option v-for="c in courses" :key="c.Cno" :value="c.Cno">
                {{ c.Cno }} - {{ c.Cname }}
              </option>
            </select>
            <input v-model="enrollSearch" placeholder="按学号/姓名搜索" @keyup.enter="loadEnrollments" />
            <button @click="loadEnrollments">查询</button>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th>学号</th><th>学生姓名</th><th>课程号</th><th>课程名</th>
                <th style="width:260px;">成绩</th>
                <th style="width:160px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in enrollments" :key="e.Sno+'_'+e.Cno">
                <td>{{ e.Sno }}</td>
                <td>{{ e.Sname }}</td>
                <td>{{ e.Cno }}</td>
                <td>{{ e.Cname }}</td>
                <td>
                  <div class="row-actions">
                    <input type="number" min="0" max="100" v-model.number="editGrade[keyOf(e)]" placeholder="0-100" />
                    <span class="muted" v-if="e.grade!==null && e.grade!==''">当前：{{ e.grade }}</span>
                    <span class="muted" v-else>当前：无</span>
                  </div>
                </td>
                <td>
                  <div class="row-actions">
                    <button @click="saveGrade(e)">保存</button>
                    <button class="warning" @click="clearGrade(e)">清空</button>
                  </div>
                </td>
              </tr>
              <tr v-if="enrollments.length===0"><td colspan="6" class="empty">暂无记录</td></tr>
            </tbody>
          </table>
          <p v-if="msgEnroll" :class="msgEnrollOk ? 'ok' : 'err'">{{ msgEnroll }}</p>
        </div>

        <!-- 个人资料 -->
        <div v-else-if="activeKey==='profile'" class="card">
          <h3>个人资料</h3>
          <div class="form-grid">
            <input v-model="profileForm.Tname" placeholder="姓名" />
            <input v-model="profileForm.Tdept" placeholder="院系" />
            <input v-model="profileForm.Tsex" placeholder="性别" />
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

/* 导航 */
const navGroups = reactive([
  { title: '教学管理', collapsed: false, items: [
      { key: 'courses', label: '我的课程' },
      { key: 'enrollments', label: '选课名单与成绩' },
    ] },
  { title: '个人信息', collapsed: false, items: [
      { key: 'profile', label: '个人资料' },
      { key: 'password', label: '修改密码' },
    ] },
])
const titles = {
  courses: '我的课程',
  enrollments: '选课名单与成绩',
  profile: '个人资料',
  password: '修改密码',
}
const activeKey = ref('courses')
const currentTitle = computed(() => titles[activeKey.value] || '教师后台')
const displayName = computed(() => profile.value?.Tname || me.value?.name || '')

function toggleGroup(i){ navGroups[i].collapsed = !navGroups[i].collapsed }
function activate(k){ activeKey.value = k; preloadFor(k) }
function logout(){ localStorage.removeItem('token'); router.push('/login') }

onMounted(async () => {
  try{
    me.value = (await axios.get('/api/auth/me')).data
    if (me.value.role !== 'teacher') return router.replace('/login')
    await loadProfile()
    await loadCourses()
    preloadFor(activeKey.value)
  }catch{
    router.replace('/login')
  }
})

function preloadFor(k){
  if (k === 'enrollments') loadEnrollments()
}

/* 个人资料 */
async function loadProfile(){
  profile.value = (await axios.get('/api/teacher/profile')).data
  syncProfileForm()
}
const profileForm = reactive({ Tname:'', Tdept:'', Tsex:'' })
function syncProfileForm(){
  if (!profile.value) return
  profileForm.Tname = profile.value.Tname || ''
  profileForm.Tdept = profile.value.Tdept || ''
  profileForm.Tsex = profile.value.Tsex || ''
}
const savingProfile = ref(false)
const msgProfile = ref(''); const msgProfileOk = ref(false)
async function saveProfile(){
  msgProfile.value=''; msgProfileOk.value=false; savingProfile.value=true
  try{
    const data = (await axios.put('/api/teacher/profile', profileForm)).data
    profile.value = data; msgProfileOk.value = true; msgProfile.value = '已保存'
  }catch(e){
    msgProfile.value = e?.response?.data?.detail || '保存失败'
  }finally{ savingProfile.value=false }
}

/* 修改密码 */
const pwdForm = reactive({ old_password:'', new_password:'', confirm:'' })
const changingPwd = ref(false)
const msgPwd = ref(''); const pwdOk = ref(false)
async function changePassword(){
  msgPwd.value=''; pwdOk.value=false
  if (!pwdForm.old_password || !pwdForm.new_password){ msgPwd.value='请输入当前密码与新密码'; return }
  if (pwdForm.new_password.length < 6){ msgPwd.value='新密码至少 6 位'; return }
  if (pwdForm.new_password !== pwdForm.confirm){ msgPwd.value='两次输入的新密码不一致'; return }
  if (pwdForm.new_password === pwdForm.old_password){ msgPwd.value='新旧密码不能相同'; return }
  changingPwd.value = true
  try{
    await axios.post('/api/auth/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    pwdOk.value = true; msgPwd.value='修改成功，请重新登录'
    setTimeout(() => logout(), 1000)
  }catch(e){
    msgPwd.value = e?.response?.data?.detail || '修改失败'
  }finally{
    changingPwd.value = false
  }
}

/* 我的课程 */
const courses = ref([])
async function loadCourses(){
  courses.value = (await axios.get('/api/teacher/courses')).data
}

/* 选课名单与成绩 */
const enrollments = ref([])
const enrollCourse = ref('')
const enrollSearch = ref('')
const editGrade = reactive({})
const msgEnroll = ref(''); const msgEnrollOk = ref(false)
function keyOf(e){ return `${e.Sno}_${e.Cno}` }

async function loadEnrollments(){
  msgEnroll.value=''; msgEnrollOk.value=false
  const params = {}
  if (enrollCourse.value) params.Cno = enrollCourse.value
  if (enrollSearch.value) params.search = enrollSearch.value
  const rows = (await axios.get('/api/teacher/enrollments', { params })).data
  enrollments.value = rows
  rows.forEach(r => { if (editGrade[keyOf(r)] === undefined) editGrade[keyOf(r)] = r.grade })
}

async function saveGrade(e){
  try{
    const g = editGrade[keyOf(e)]
    const body = { grade: (g === '' || g === null || g === undefined) ? '' : String(g) } // 按后端 schema 传字符串
    await axios.put(`/api/teacher/enrollments/${e.Sno}/${e.Cno}/grade`, body)
    msgEnrollOk.value = true; msgEnroll.value='成绩已保存'
    await loadEnrollments()
  }catch(err){
    msgEnrollOk.value = false; msgEnroll.value = err?.response?.data?.detail || '保存失败'
  }
}
async function clearGrade(e){
  editGrade[keyOf(e)] = ''
  await saveGrade(e)
}
</script>

<style scoped>
.teacher-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: #f7f7f9;
}
.sidebar { background:#fff; border-right:1px solid #eee; display:flex; flex-direction:column; }
.brand { font-weight:700; padding:16px 18px; font-size:18px; border-bottom:1px solid #f0f0f0; }

.nav-group { padding:8px 0; }
.nav-group-header { display:flex; justify-content:space-between; align-items:center; padding:10px 18px; cursor:pointer; color:#333; font-weight:600; }
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
.topbar { height:56px; background:#fff; border-bottom:1px solid #eee; display:flex; align-items:center; justify-content:space-between; padding:0 16px; }
.topbar .title { font-size:16px; font-weight:600; }
.topbar .me { color:#666; }

.panel { padding:16px; }
.card { background:#fff; border:1px solid #eee; border-radius:8px; padding:16px; }

.form-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:10px; }
input, select, button { padding:10px 12px; border:1px solid #ddd; border-radius:6px; background:#fff; font-size:14px; }
input:focus, select:focus { border-color:#409eff; }
button { cursor:pointer; }
button.primary { background:#409eff; color:#fff; border-color:#409eff; }
button.warning { background:#ffaa2b; color:#fff; border-color:#ffaa2b; }

.toolbar { display:flex; gap:8px; align-items:center; margin-bottom:12px; }
.table { width:100%; border-collapse:collapse; background:#fff; }
.table th, .table td { border:1px solid #f0f0f0; padding:10px; text-align:left; }
.table thead { background:#fafafa; }
.empty { text-align:center; color:#888; }
.row-actions { display:flex; gap:8px; align-items:center; }
.muted { color:#999; font-size:12px; }
.ok { color:#2c7; margin-top:8px; }
.err { color:#d33; margin-top:8px; }

/* 折叠动效 */
.collapse-enter-active, .collapse-leave-active { transition: all .2s ease; }
.collapse-enter-from, .collapse-leave-to { opacity:0; transform: translateY(-6px); }
</style>