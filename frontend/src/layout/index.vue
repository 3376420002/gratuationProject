<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <span class="logo-icon">🏨</span>
        <span class="logo-text">智慧酒店系统</span>
      </div>
      
      <el-menu
        :default-active="route.path"
        class="el-menu-vertical"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>实时房态</span>
        </el-menu-item>
        
        <el-menu-item index="/booking">
          <el-icon><Calendar /></el-icon>
          <span>预订管理</span>
        </el-menu-item>
        
        <el-menu-item index="/room-config">
          <el-icon><House /></el-icon>
          <span>客房配置</span>
        </el-menu-item>
        
        <el-menu-item index="/reports">
          <el-icon><PieChart /></el-icon>
          <span>营收报表</span>
        </el-menu-item>
      </el-menu>

    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>后台管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentMenuName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              管理员 <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view /> </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Odometer, Calendar, House, PieChart, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const currentMenuName = computed(() => {
  const map = {
    '/dashboard': '实时房态',
    '/booking': '预订管理',
    '/room-config': '客房配置',
    '/reports': '营收报表'
  }
  return map[route.path] || '首页'
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.aside { background-color: #304156; transition: width 0.3s; overflow: hidden; }
.logo {
  height: 60px; display: flex; align-items: center; padding-left: 20px;
  background: #2b2f3a; color: white;
}
.logo-icon { font-size: 24px; margin-right: 10px; }
.logo-text { font-weight: bold; font-size: 16px; white-space: nowrap; }

.el-menu-vertical { border-right: none; }
.header {
  background: white; border-bottom: 1px solid #e6e6e6;
  display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
}
.user-info { cursor: pointer; color: #409EFF; font-weight: 500; }
.main { background-color: #f0f2f5; padding: 20px; }
</style>