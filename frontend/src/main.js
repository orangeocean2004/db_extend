import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

axios.defaults.baseURL = '/'
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})
axios.interceptors.response.use(
    r => r,
    e => {
        if (e.response && e.response.status === 401) {
            localStorage.removeItem('token')
            router.push('/login')
        }
        return Promise.reject(e)
    }
)

createApp(App).use(router).mount('#app')