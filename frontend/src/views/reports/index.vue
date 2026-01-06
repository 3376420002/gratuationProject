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
                 class="room-node" :class="statusClassMap[room.status]">
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
import { ElMessage } from 'element-plus'

const stats = ref([])
const roomWall = ref([])
const exportLoading = ref(false)
const statusClassMap = { '空闲': 'free', '已入住': 'busy', '维修中': 'repair' }

const handleExport = () => {
  exportLoading.value = true
  // 注意：此处 URL 端口必须与后端实际运行端口一致（8001）
  const downloadUrl = `http://127.0.0.1:8088/api/reports/export-excel?t=${new Date().getTime()}`
  window.location.href = downloadUrl
  ElMessage.success('报表下载中...')
  setTimeout(() => { exportLoading.value = false }, 2000)
}

const fetchData = async () => {
  try {
    stats.value = await request.get('/api/reports/stats')
    roomWall.value = await request.get('/api/reports/room-wall')
    initPieChart()
    initLineChart()
  } catch (error) {
    console.error("加载报表失败", error)
  }
}

const initPieChart = async () => {
  const data = await request.get('/api/reports/room-type-dist')
  const chart = echarts.init(document.getElementById('pieChart'))
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      data: data,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

const initLineChart = async () => {
  const res = await request.get('/api/reports/chart')
  const chart = echarts.init(document.getElementById('revenueChart'))
  chart.setOption({
    xAxis: { type: 'category', data: res.days },
    yAxis: { type: 'value' },
    tooltip: { trigger: 'axis' },
    series: [{ data: res.data, type: 'line', smooth: true, areaStyle: { color: 'rgba(64,158,255,0.2)' } }]
  })
}

onMounted(fetchData)
</script>

<style scoped>
.report-container { padding: 20px; background: #f0f2f5; min-height: 100vh; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.stat-card { text-align: center; border-radius: 10px; }
.stat-title { color: #909399; font-size: 14px; }
.stat-value { font-size: 24px; font-weight: bold; color: #303133; margin-top: 10px; }
.room-wall-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 10px; height: 300px; overflow-y: auto; }
.room-node { height: 60px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-size: 12px; }
.free { background: #67C23A; }
.busy { background: #F56C6C; }
.repair { background: #909399; }
.grid-legend { margin-top: 15px; display: flex; gap: 20px; font-size: 12px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
</style>