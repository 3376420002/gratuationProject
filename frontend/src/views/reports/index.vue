<template>
  <div class="report-container">
    <div class="dashboard-header">
      <h2 class="page-title">数据看板 & 经营分析</h2>
      <el-button type="success" :icon="Download" @click="handleExport" :loading="exportLoading">
        导出报表到 Excel
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
           <div class="stat-title">{{ stat.title }}</div>
           <div class="stat-value">{{ stat.prefix }}{{ stat.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="10">
        <el-card shadow="hover" header="🏢 实时房态网格监控">
          <div class="room-wall-grid">
            <div v-for="room in roomWall" :key="room.number" 
                 class="room-node" :class="statusMap[room.status]">
              <div class="node-no">{{ room.number }}</div>
              <div class="node-status">{{ room.status }}</div>
            </div>
          </div>
          <div class="grid-legend">
            <span class="legend-item"><i class="dot free"></i>空闲</span>
            <span class="legend-item"><i class="dot busy"></i>已入住</span>
            <span class="legend-item"><i class="dot repair"></i>维修</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="hover" header="📊 热门房型预订占比">
          <div id="pieChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px;" header="📈 营收走势深度分析">
      <div id="revenueChart" style="height: 350px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { Download } from '@element-plus/icons-vue'
import request from '../../utils/request'
import { ElMessage } from 'element-plus' // 建议引入消息提示

const stats = ref([])
const roomWall = ref([])
const exportLoading = ref(false)
const statusMap = { '空闲': 'free', '已入住': 'busy', '维修': 'repair' }

// 🌟 修正后的导出逻辑
const handleExport = () => {
  exportLoading.value = true
  
  // 1. 确保端口是 8001
  // 2. 加上时间戳参数 t=${new Date().getTime()}，双重保险防止浏览器缓存旧文件
  const downloadUrl = `http://127.0.0.1:8088/api/reports/export-excel?t=${new Date().getTime()}`
  
  try {
    // 使用 window.location.href 是触发 StreamingResponse 下载最直接的方式
    window.location.href = downloadUrl
    
    // 提示用户
    ElMessage.success('报表正在生成并下载...')
  } catch (error) {
    console.error("导出失败:", error)
    ElMessage.error('导出失败，请检查后端服务是否开启')
  } finally {
    // 模拟 loading 效果，提升用户体验
    setTimeout(() => { exportLoading.value = false }, 1500)
  }
}

const fetchData = async () => {
  try {
    stats.value = await request.get('/api/reports/stats')
    roomWall.value = await request.get('/api/reports/room-wall')
    initPieChart()
    initLineChart()
  } catch (error) {
    console.error("获取数据失败:", error)
  }
}

// ... initPieChart 和 initLineChart 逻辑保持不变 ...
const initPieChart = async () => {
  const data = await request.get('/api/reports/room-type-dist')
  const chartDom = document.getElementById('pieChart')
  if(!chartDom) return
  const chart = echarts.init(chartDom)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: data
    }]
  })
}

const initLineChart = async () => {
  const res = await request.get('/api/reports/chart')
  const chartDom = document.getElementById('revenueChart')
  if(!chartDom) return
  const chart = echarts.init(chartDom)
  chart.setOption({
    xAxis: { type: 'category', data: res.days },
    yAxis: { type: 'value' },
    tooltip: { trigger: 'axis' },
    series: [{
      data: res.data,
      type: 'line',
      smooth: true,
      areaStyle: { color: 'rgba(64,158,255,0.2)' }
    }]
  })
}

onMounted(() => fetchData())
</script>

<style scoped>
/* 增加顶栏样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.page-title { margin: 0; color: #303133; font-size: 20px; }

/* 其他样式保持不变 */
.report-container { padding: 20px; background: #f0f2f5; }
.room-wall-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: 10px;
  height: 300px;
  overflow-y: auto;
}
.room-node {
  height: 60px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}
.node-no { font-weight: bold; font-size: 14px; }
.free { background: #67C23A; }
.busy { background: #F56C6C; }
.repair { background: #909399; }

.grid-legend { margin-top: 15px; display: flex; gap: 20px; font-size: 12px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
</style>