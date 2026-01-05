<template>
  <div class="report-container">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover">
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-value">{{ stat.prefix }}{{ stat.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-top: 20px;">
      <template #header><span>📈 营收走势图 (最近7天订单量)</span></template>
      <div id="revenueChart" style="height: 400px; width: 100%;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../utils/request' 


const stats = ref([])

const fetchStats = async () => {
  try {
    const res = await request.get('/api/reports/stats')
    stats.value = res
  } catch (error) {
    console.error("获取报表统计失败:", error)
  }
}

const initChart = async () => {
  const chartDom = document.getElementById('revenueChart')
  const myChart = echarts.init(chartDom)
  
  try {

    const res = await request.get('/api/reports/chart')
    
    const option = {
      xAxis: { 
        type: 'category', 
        data: res.days 
      },
      yAxis: { type: 'value' },
      tooltip: { trigger: 'axis' },
      series: [{
        data: res.data,
        type: 'line',
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64,158,255,0.5)' },
            { offset: 1, color: 'rgba(64,158,255,0.1)' }
          ])
        }
      }]
    }
    myChart.setOption(option)
    
    window.addEventListener('resize', () => myChart.resize())
  } catch (error) {
    console.error("图表数据加载失败:", error)
  }
}

onMounted(() => {
  fetchStats() 
  initChart() 
})
</script>

<style scoped>
.report-container { padding: 20px; }
.stat-title { color: #909399; font-size: 14px; }
.stat-value { font-size: 24px; font-weight: bold; margin-top: 10px; color: #409EFF; }
</style>