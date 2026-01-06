<template>
  <div class="dashboard-container">
    <div class="carousel-section">
      <el-carousel :interval="5000" type="card" height="300px">
        <el-carousel-item v-for="item in roomTypeShowcase" :key="item.name">
          <div class="room-card">
            <img :src="item.img" class="room-img" />
            <div class="room-overlay">
              <div class="overlay-content">
                <h3>{{ item.name }}</h3>
                <p>{{ item.desc }}</p>
                <el-tag size="small" type="warning" effect="dark">精品推荐</el-tag>
              </div>
            </div>
            <div class="room-title-bar">{{ item.name }}</div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <el-row :gutter="20" class="statistics">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-blue">🏨</div>
            <div class="stat-info">
              <div class="label">总房间数</div>
              <div class="value">{{ rooms.length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card clickable" @click="router.push('/booking')">
          <div class="stat-content">
            <div class="stat-icon icon-green">📈</div>
            <div class="stat-info">
              <div class="label">当前入住率 (点击去办理)</div>
              <div class="value">{{ occupancyRate }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-orange">🧹</div>
            <div class="stat-info">
              <div class="label">待打扫房间</div>
              <div class="value">{{ rooms.filter(r => r.status === '待打扫').length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-red">🛠️</div>
            <div class="stat-info">
              <div class="label">维修中</div>
              <div class="value">{{ rooms.filter(r => r.status === '维修中').length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">实时房态监控看板</span>
            <el-tag type="info" size="small" class="sync-tag">系统已通过身份证(UID)实名校验</el-tag>
          </div>
          <el-button type="primary" plain @click="getRooms">同步实时数据</el-button>
        </div>
      </template>

      <el-table :data="rooms" v-loading="loading" stripe border>
        <el-table-column prop="number" label="房号" width="100" align="center" sortable />
        <el-table-column prop="room_type" label="房型" width="150" />
        <el-table-column prop="price" label="房费/日" width="120">
          <template #default="scope">
            <span class="price-text">￥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="当前状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="住客/信息 (点击姓名查看详情)">
          <template #default="scope">
            <div v-if="scope.row.status === '已入住'" class="guest-link" @click="openGuestDrawer(scope.row)">
              <el-icon><User /></el-icon>
              <span class="guest-name">{{ scope.row.guest_name || '散客' }}</span>
              <span class="click-hint">查看详情 ></span>
            </div>
            <div v-else-if="scope.row.status === '待打扫'">
              <span class="status-text-warning">🧹 等待保洁处理</span>
            </div>
            <div v-else-if="scope.row.status === '维修中'">
              <span class="status-text-danger">🛠️ 设施故障报修中</span>
            </div>
            <span v-else style="color: #ccc">--</span>
          </template>
        </el-table-column>

        <el-table-column label="运维/清洁状态" width="180">
          <template #default="scope">
            <span :class="['ops-status', scope.row.status === '维修中' ? 'error' : 'ok']">
              {{ scope.row.status === '维修中' ? '停止运行' : '正常运行中' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer
      v-model="drawerVisible"
      title="住客详细档案"
      direction="rtl"
      size="400px"
      :destroy-on-close="true"
    >
      <div v-if="selectedRoom" class="drawer-detail">
        <div class="room-header">
          <div class="room-num">{{ selectedRoom.number }}</div>
          <div class="room-type">{{ selectedRoom.room_type }}</div>
        </div>

        <el-divider content-position="left">核心实名信息</el-divider>
        <div class="info-group">
          <div class="info-row">
            <span class="label">姓名</span>
            <span class="value">{{ selectedRoom.guest_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">证件号码</span>
            <span class="value">{{ selectedRoom.guest_id_card || '未登记' }}</span>
          </div>
          <div class="info-row">
            <span class="label">联系电话</span>
            <span class="value highlight">{{ selectedRoom.guest_phone }}</span>
          </div>
        </div>

        <el-divider content-position="left">住宿周期信息</el-divider>
        <div class="info-group">
          <div class="info-row">
            <span class="label">入住日期</span>
            <span class="value">{{ selectedRoom.check_in_date || '2026-01-06' }}</span>
          </div>
          <div class="info-row">
            <span class="label">预离日期</span>
            <span class="value">{{ selectedRoom.check_out_date || '2026-01-07' }}</span>
          </div>
        </div>

        <div class="drawer-footer">
          <el-button type="success" size="large" class="call-btn" @click="handleCall(selectedRoom.guest_phone)">
            <el-icon><PhoneFilled /></el-icon>
            一键通话联系住客
          </el-button>
          <div class="call-notice">点击后将唤起系统通讯录拨号界面</div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, PhoneFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

const router = useRouter()
const rooms = ref([])
const loading = ref(false)

// 侧拉栏相关状态
const drawerVisible = ref(false)
const selectedRoom = ref(null)

// 轮播图模拟数据
const roomTypeShowcase = [
  { name: '商务麻将房', img: 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800', desc: '配备全自动麻将机，独立新风系统。' },
  { name: '标准双床房', img: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800', desc: '纯棉高织床品，打造静谧睡眠。' },
  { name: '影音大床房', img: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800', desc: '4K超清投影，环绕立体声音响。' },
  { name: '电竞双人间', img: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800', desc: 'RTX 4090顶级显卡，240Hz刷新率。' }
]

const occupancyRate = computed(() => {
  if (rooms.value.length === 0) return 0
  const occupied = rooms.value.filter(r => r.status === '已入住').length
  return ((occupied / rooms.value.length) * 100).toFixed(1)
})

const getStatusType = (status) => {
  const map = { '空闲': 'success', '已入住': 'danger', '待打扫': 'warning', '维修中': 'info' }
  return map[status] || 'info'
}

const getRooms = async () => {
  loading.value = true
  try {
    rooms.value = await request.get('/api/rooms')
  } catch (err) {
    ElMessage.error('获取实时数据失败')
  } finally {
    loading.value = false
  }
}

// 侧拉栏逻辑
const openGuestDrawer = (room) => {
  selectedRoom.value = room
  drawerVisible.value = true
}

// 通话功能
const handleCall = (phone) => {
  if (!phone) return ElMessage.warning('该住客未登记有效联系电话')
  window.location.href = `tel:${phone}`
}

onMounted(getRooms)
</script>

<style scoped>
.dashboard-container { padding: 20px; background-color: #f5f7fa; min-height: 100vh; }

/* 轮播图样式 */
.carousel-section { margin-bottom: 25px; }
.room-card { position: relative; width: 100%; height: 100%; border-radius: 12px; overflow: hidden; }
.room-img { width: 100%; height: 100%; object-fit: cover; }
.room-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: 0.4s;
}
.room-card:hover .room-overlay { opacity: 1; }
.overlay-content { text-align: center; color: #fff; padding: 20px; }
.room-title-bar { 
  position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.6); 
  color: white; padding: 10px; text-align: center; font-weight: bold; 
}

/* 统计卡片 */
.statistics { margin-bottom: 25px; }
.stat-card { border-radius: 8px; border: none; }
.clickable { cursor: pointer; }
.clickable:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.stat-content { display: flex; align-items: center; }
.stat-icon { width: 45px; height: 45px; border-radius: 8px; display: flex; justify-content: center; align-items: center; font-size: 20px; margin-right: 15px; }
.icon-blue { background: #e6f7ff; color: #1890ff; }
.icon-green { background: #f6ffed; color: #52c41a; }
.icon-orange { background: #fff7e6; color: #fa8c16; }
.icon-red { background: #fff1f0; color: #f5222d; }
.value { font-size: 20px; font-weight: bold; }

/* 表格样式 */
.table-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 10px; }
.title { font-size: 16px; font-weight: bold; color: #333; }
.price-text { color: #f56c6c; font-weight: bold; }

.guest-link { color: #409eff; cursor: pointer; display: flex; align-items: center; gap: 5px; font-weight: 500; }
.click-hint { font-size: 11px; color: #999; margin-left: auto; }
.status-text-warning { color: #e6a23c; font-size: 13px; }
.status-text-danger { color: #f56c6c; font-size: 13px; }
.ops-status { font-size: 13px; }
.ops-status.ok { color: #67c23a; }
.ops-status.error { color: #f56c6c; }

/* 侧拉栏内部样式 */
.drawer-detail { padding: 0 10px; }
.room-header { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
.room-num { background: #409eff; color: white; padding: 5px 15px; border-radius: 4px; font-size: 22px; font-weight: bold; }
.info-group { display: flex; flex-direction: column; gap: 18px; margin-bottom: 30px; }
.info-row { display: flex; justify-content: space-between; align-items: center; }
.label { color: #909399; font-size: 14px; }
.value { color: #303133; font-weight: 600; }
.value.highlight { color: #409eff; font-size: 18px; }

.drawer-footer { margin-top: 50px; text-align: center; }
.call-btn { width: 100%; height: 50px; font-size: 16px; border-radius: 25px; }
.call-notice { margin-top: 10px; font-size: 12px; color: #c0c4cc; }
</style>