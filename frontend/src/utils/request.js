import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8001', // 后端地址
  timeout: 5000
})


request.interceptors.response.use(
  response => response.data,
  error => {
    const msg = error.response?.data?.detail || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {

    config.headers['token'] = token
  }
  return config
})

export default request