<template>
  <div class="auth-page">
    <div class="container" :class="{ 'right-panel-active': isAdmin }">
      <!-- 管理员登录（Administer Mode） -->
      <div class="form-container sign-up-container">
        <form @submit.prevent="submitAdmin">
          <h1>Administer Mode</h1>
          <span>仅限管理员登录</span>
          <input v-model="adminAccount" type="text" placeholder="管理员账号(8位)" />
          <input v-model="adminPassword" type="password" placeholder="密码" />
          <button :disabled="loadingAdmin">{{ loadingAdmin ? '登录中...' : '管理员登录' }}</button>
          <p v-if="errorAdmin" class="err">{{ errorAdmin }}</p>
        </form>
      </div>

      <!-- 普通用户登录 -->
      <div class="form-container sign-in-container">
        <form @submit.prevent="submitUser">
          <h1>Sign in</h1>
          <span>学生/教师使用账号密码登录</span>
          <input v-model="account" type="text" placeholder="账号(8位)" />
          <input v-model="password" type="password" placeholder="密码" />
          <button :disabled="loadingUser">{{ loadingUser ? '登录中...' : '登录' }}</button>
          <p v-if="errorUser" class="err">{{ errorUser }}</p>
        </form>
      </div>

      <!-- 右侧遮罩与切换按钮 -->
      <div class="overlay-container">
        <div class="overlay">
          <div class="overlay-panel overlay-left">
            <h1>欢迎回来</h1>
            <p>返回普通登录</p>
            <button class="ghost" type="button" @click="isAdmin=false">User Sign In</button>
          </div>
          <div class="overlay-panel overlay-right">
            <h1>Hello!</h1>
            <p>进入管理员模式以管理用户与课程</p>
            <button class="ghost" type="button" @click="isAdmin=true">Administer Mode</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// UI 切换
const isAdmin = ref(false)

// 普通登录
const account = ref('')
const password = ref('')
const loadingUser = ref(false)
const errorUser = ref('')

// 管理员登录
const adminAccount = ref('')
const adminPassword = ref('')
const loadingAdmin = ref(false)
const errorAdmin = ref('')

async function doLogin(acc, pwd) {
  const form = new FormData()
  form.append('username', acc.trim())
  form.append('password', pwd)
  form.append('grant_type', 'password')
  const res = await axios.post('/api/auth/login', form)
  localStorage.setItem('token', res.data.access_token)
  axios.defaults.headers.Authorization = 'Bearer ' + res.data.access_token
  return (await axios.get('/api/auth/me')).data
}

async function submitUser() {
  errorUser.value = ''; loadingUser.value = true
  try {
    const me = await doLogin(account.value, password.value)
    if (me.role === 'admin') router.push('/admin')
    else if (me.role === 'teacher') router.push('/teacher')
    else router.push('/student')
  } catch (e) {
    errorUser.value = e?.response?.data?.detail || '登录失败'
  } finally {
    loadingUser.value = false
  }
}

async function submitAdmin() {
  errorAdmin.value = ''; loadingAdmin.value = true
  try {
    const me = await doLogin(adminAccount.value, adminPassword.value)
    if (me.role !== 'admin') {
      errorAdmin.value = '该账号不是管理员'
      localStorage.removeItem('token')
      return
    }
    router.push('/admin')
  } catch (e) {
    errorAdmin.value = e?.response?.data?.detail || '登录失败'
  } finally {
    loadingAdmin.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Montserrat:400,800');

.auth-page {
  background: #f6f5f7;
  min-height: 100vh;
  display: grid;
  place-items: center;
  font-family: 'Montserrat', sans-serif;
}

.err { color:#d33; margin-top:8px; }

h1 { font-weight: bold; margin: 0; }
span { font-size: 12px; }

button {
  border-radius: 20px;
  border: 1px solid #FF4B2B;
  background-color: #FF4B2B;
  color: #FFFFFF;
  font-size: 12px;
  font-weight: bold;
  padding: 12px 45px;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: transform 80ms ease-in;
}
button:active { transform: scale(0.95); }
button:focus { outline: none; }
button.ghost { background-color: transparent; border-color: #FFFFFF; }

input {
  background-color: #eee;
  border: none;
  padding: 12px 15px;
  margin: 8px 0;
  width: 100%;
}

.container {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
  position: relative;
  overflow: hidden;
  width: 900px;           /* 稍加宽，避免拥挤 */
  max-width: 100%;
  min-height: 560px;

  --left-form-offset: 45%;   /* 左侧表单右边距 → 数值越大越靠左（远离中线） */
  --right-form-offset:19%;  /* 右侧表单左边距 → 数值越大越靠右（远离中线） */
  --form-width: 75%;         /* 两侧表单的相对宽度（相对于各自半屏） */
}

/* 表单容器通用 */
.form-container {
  position: absolute;
  top: 0; height: 100%;
  transition: all 0.6s ease-in-out;
  display: flex; align-items: center; justify-content: center;
  flex-direction: column;
  padding: 0 50px; text-align: center;
}

/* 关键1：给表单一个“内容宽度”，始终在各自半边的中间 */
.form-container form {
  width: clamp(300px, var(--form-width), 420px);          /* 相对半边的宽度，≈减少 1/4 */
  max-width: 420px;     /* 上限，避免超宽 */
  min-width: 300px;     /* 下限，避免过窄 */
  margin: 0 auto;
}

/* 关键2：输入/按钮占满表单内容宽度（替代之前 80% 的规则） */
.form-container input,
.form-container button {
  width: 100%;
}

/* 左侧：用户登录（可见时置顶） */
.sign-in-container form {
  margin-right: var(--left-form-offset);
  margin-left: auto;
}
.container.right-panel-active .sign-in-container {
  transform: translateX(-100%);
  opacity: 0;
  z-index: 1; /* 隐藏时降层级 */
}

/* 右侧：管理员登录（固定在右侧；可见时置顶） */
.sign-up-container {
  right: 0; left: auto; width: 50%;
  opacity: 0; z-index: 1; transform: none;
}
.container.right-panel-active .sign-up-container {
  opacity: 1; z-index: 5; transform: none;
}

/* 右侧表单的居中偏移应加在 form 上（原来写在容器上会整体错位） */
.sign-up-container form {
  width: clamp(300px, var(--form-width), 420px);
  margin-left: var(--right-form-offset);
  margin-right: auto;
}

/* 遮罩容器：保持在两表单之下，但仍可点击 */
.overlay-container {
  position: absolute; top: 0; left: 50%;
  width: 50%; height: 100%;
  overflow: hidden; transition: transform 0.6s ease-in-out;
  z-index: 2;            /* 低于表单(5)，高于背景 */
  pointer-events: auto;  /* 按钮可点击 */
}
.container.right-panel-active .overlay-container { transform: translateX(-100%); }

/* 遮罩内容动画保持不变 */
.overlay {
  background: linear-gradient(to right, #FF4B2B, #FF416C);
  background-repeat: no-repeat; background-size: cover; background-position: 0 0;
  color: #FFFFFF; position: relative; left: -100%;
  height: 100%; width: 200%; transform: translateX(0);
  transition: transform 0.6s ease-in-out;
}
.container.right-panel-active .overlay { transform: translateX(50%); }

.overlay-panel {
  position: absolute; display: flex; align-items: center; justify-content: center; flex-direction: column;
  padding: 0 40px; text-align: center; top: 0; height: 100%; width: 50%;
  transform: translateX(0); transition: transform 0.6s ease-in-out;
}
.overlay-left { transform: translateX(-20%); }
.container.right-panel-active .overlay-left { transform: translateX(0); }
.overlay-right { right: 0; transform: translateX(0); }
.container.right-panel-active .overlay-right { transform: translateX(20%); }
</style>