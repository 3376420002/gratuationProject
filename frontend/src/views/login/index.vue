<template>
  <div class="login-container">
    <div class="bg-image"></div>
    
    <div class="login-box">
      <div class="login-header">
        <span class="hotel-icon">🏨</span>
        <h2 class="title">酒店管理系统登录</h2>
        <p class="subtitle">Hotel Management System</p>
      </div>

      <el-form :model="loginForm" class="login-form">
        <el-form-item>
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名" 
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button 
          type="primary" 
          class="login-button" 
          @click="handleLogin" 
        >
          登 录
        </el-button>
      </el-form>
      
      <div class="login-footer">
        © 2026 智慧酒店系统
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()

const loginForm = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    return ElMessage.warning('请输入用户名 and 密码')
  }

  try {
    const res = await request.post('/api/login', loginForm.value)
    localStorage.setItem('token', 'logged-in-secret') 
    ElMessage({
      message: '欢迎回来，系统管理员',
      type: 'success',
      duration: 3000,
      showClose: true
    })
    router.push('/dashboard')
    
  } catch (error) {
    console.error('登录失败详情:', error)
    ElMessage.error('用户名或密码错误，请检查后端服务')
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1920&q=80') no-repeat center center;
  background-size: cover;
  filter: brightness(0.6); 
}
.login-box {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(15px); 
  border-radius: 20px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.login-header { margin-bottom: 30px; }
.hotel-icon { font-size: 40px; display: block; margin-bottom: 10px; }
.title { margin: 0; font-size: 24px; color: #333; letter-spacing: 1px; }
.subtitle { font-size: 12px; color: #666; margin-top: 5px; }

.login-form { margin-top: 20px; }

:deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.9) !important;
  border-radius: 10px !important;
  height: 45px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  border-radius: 10px;
  margin-top: 15px;
  background: linear-gradient(135deg, #409eff 0%, #0076ff 100%);
  border: none;
  font-weight: bold;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(64, 158, 255, 0.4);
}

.login-footer {
  margin-top: 30px;
  font-size: 12px;
  color: #666;
}
</style>