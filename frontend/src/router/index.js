import { createRouter, createWebHistory } from 'vue-router'

import Login from '../components/Login.vue'
import AdminDashboard from '../components/AdminDashboard.vue'
import TeacherDashboard from '../components/TeacherDashboard.vue'
import StudentDashboard from '../components/StudentDashboard.vue' // 新增

const routes = [
    { path: '/login', component: Login },
    { path: '/admin', component: AdminDashboard },
    { path: '/teacher', component: TeacherDashboard },
    { path: '/student', component: StudentDashboard },
    { path: '/', redirect: '/login' }
]

export default createRouter({ history: createWebHistory(), routes })