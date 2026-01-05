import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 新增这一行：引入路由配置

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(router) // 新增这一行：使用路由
app.mount('#app')