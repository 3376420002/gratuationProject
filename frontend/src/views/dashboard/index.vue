<template>
  <div class="dashboard-container">
    <div class="carousel-section">
      <el-carousel :interval="5000" type="card" height="320px">
        <el-carousel-item v-for="item in roomTypeShowcase" :key="item.name">
          <div class="room-card">
            <img :src="item.img" class="room-img" />
            <div class="room-overlay">
              <div class="overlay-content">
                <h3>{{ item.name }}</h3>
                <p>{{ item.desc }}</p>
                <div class="tags">
                  <el-tag size="small" type="warning" effect="dark">精品推荐</el-tag>
                  <el-tag size="small" type="info" effect="dark" style="margin-left: 8px">极致体验</el-tag>
                </div>
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
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon icon-green">📈</div>
            <div class="stat-info">
              <div class="label">当前入住率</div>
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
          <span class="title">房态与运维控制台</span>
          <el-button type="primary" @click="getRooms">刷新数据</el-button>
        </div>
      </template>

      <el-table :data="rooms" v-loading="loading" stripe border>
        <el-table-column prop="number" label="房间号" width="100" align="center" />
        <el-table-column prop="room_type" label="房型" />
        <el-table-column prop="price" label="房费/日">
          <template #default="scope">
            <span class="price-text">￥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="当前状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="住客/备注" width="180">
          <template #default="scope">
            <div v-if="scope.row.status === '已入住'">
              <el-tag type="info" effect="plain">👤 {{ scope.row.guest_name || '散客' }}</el-tag>
            </div>
            <div v-else-if="scope.row.status === '待打扫'">
              <span style="color: #E6A23C; font-size: 12px">🧹 等待保洁处理...</span>
            </div>
            <div v-else-if="scope.row.status === '维修中'">
              <span style="color: #F56C6C; font-size: 12px">🛠️ 设施报修中</span>
            </div>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>

        <el-table-column label="管理操作" width="300">
          <template #default="scope">
            <el-button v-if="scope.row.status === '空闲'" size="small" type="warning" @click="openCheckIn(scope.row)">办理入住</el-button>
            <el-button v-if="scope.row.status === '已入住'" size="small" type="info" @click="openCheckOut(scope.row)">办理退房</el-button>
            <el-button v-if="scope.row.status === '待打扫'" size="small" type="success" @click="updateRoomStatus(scope.row, '空闲')">确认打扫</el-button>
            <el-button v-if="scope.row.status === '维修中'" size="small" type="success" plain @click="updateRoomStatus(scope.row, '空闲')">修毕</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCheckInDialog" title="办理入住登记" width="450px">
      <el-form :model="checkInForm" label-width="100px">
        <el-form-item label="住客姓名"><el-input v-model="checkInForm.guest_name" /></el-form-item>
        <el-form-item label="身份证号"><el-input v-model="checkInForm.guest_id_card" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="checkInForm.guest_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCheckInDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCheckIn">确认入住</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCheckOutDialog" title="退房结算账单" width="400px">
      <div style="padding: 10px; background: #fdf6ec; border-radius: 8px; margin-bottom: 20px">
        <p><strong>房号：</strong>{{ currentRoom?.number }}</p>
        <p><strong>住客：</strong>{{ currentRoom?.guest_name }}</p>
        <p><strong>标准房费：</strong>￥{{ currentRoom?.price }}</p>
      </div>
      <el-form label-width="100px">
        <el-form-item label="额外消费">
          <el-input-number v-model="extraCharge" :min="0" style="width: 100%" />
        </el-form-item>
        <div style="text-align: right; margin-top: 20px; border-top: 1px dashed #ccc; padding-top: 20px">
          <span style="font-size: 16px">应收总计：</span>
          <span style="font-size: 24px; color: #f56c6c; font-weight: bold">￥{{ (currentRoom?.price || 0) + extraCharge }}</span>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showCheckOutDialog = false">返回</el-button>
        <el-button type="primary" @click="confirmCheckOut">确认收款并退房</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '../../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

// 数据引用
const rooms = ref([])
const loading = ref(false)
const showCheckInDialog = ref(false)
const showCheckOutDialog = ref(false)
const currentRoom = ref(null)
const extraCharge = ref(0)
const checkInForm = ref({ guest_name: '', guest_id_card: '', guest_phone: '' })

// 房型展示数据
const roomTypeShowcase = [
  {
    name: '商务麻将房',
    img: 'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&q=80',
    desc: '集成自动麻将机与商务洽谈区，是朋友聚会与休闲娱乐的首选。'
  },
  {
    name: '标准双床房',
    img: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&q=80',
    desc: '经典双向配置，高品质纯棉床品，为您提供静谧的商旅睡眠。'
  },
  {
    name: '影音大床房',
    img: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80',
    desc: '配备4K投影与影院级音响，让您在房间即可享受私人影院体验。'
  },
  {
    name: '电竞双人间',
    img: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&q=80',
    desc: '4090顶级显卡与专业电竞椅，专为极致游戏玩家打造。'
  }
]

// 计算入住率
const occupancyRate = computed(() => {
  if (rooms.value.length === 0) return 0
  const occupied = rooms.value.filter(r => r.status === '已入住').length
  return ((occupied / rooms.value.length) * 100).toFixed(1)
})

// 获取房态颜色
const getStatusType = (status) => {
  const map = { '空闲': 'success', '已入住': 'danger', '待打扫': 'warning', '维修中': 'info' }
  return map[status] || 'info'
}

// 核心业务方法
const getRooms = async () => {
  loading.value = true
  try {
    rooms.value = await request.get('/api/rooms')
  } catch (err) {
    ElMessage.error('获取房态失败')
  } finally {
    loading.value = false
  }
}

const openCheckIn = (room) => {
  currentRoom.value = room
  checkInForm.value = { guest_name: '', guest_id_card: '', guest_phone: '' }
  showCheckInDialog.value = true
}

const submitCheckIn = async () => {
  if (!checkInForm.value.guest_name) return ElMessage.warning('姓名必填')
  try {
    await request.put(`/api/rooms/${currentRoom.value.id}/status`, {
      status: '已入住',
      ...checkInForm.value
    })
    ElMessage.success('入住登记成功')
    showCheckInDialog.value = false
    getRooms()
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

const openCheckOut = (room) => {
  currentRoom.value = room
  extraCharge.value = 0
  showCheckOutDialog.value = true
}

const confirmCheckOut = async () => {
  try {
    const total = currentRoom.value.price + extraCharge.value
    await request.put(`/api/rooms/${currentRoom.value.id}/status`, {
      status: '待打扫',
      guest_name: '', guest_id_card: '', guest_phone: ''
    })
    ElMessageBox.alert(`结算完成！实收总额：￥${total}`, '账单确认', { type: 'success' })
    showCheckOutDialog.value = false
    getRooms()
  } catch (err) {
    ElMessage.error('结算失败')
  }
}

const updateRoomStatus = async (room, nextStatus) => {
  try {
    await request.put(`/api/rooms/${room.id}/status`, {
      status: nextStatus,
      guest_name: '', guest_id_card: '', guest_phone: ''
    })
    ElMessage.success(`状态已更新为 ${nextStatus}`)
    getRooms()
  } catch (err) {
    ElMessage.error('更新失败')
  }
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除这个房间吗？', '警告', { type: 'error' }).then(async () => {
    await request.delete(`/api/rooms/${id}`)
    ElMessage.success('删除成功')
    getRooms()
  })
}

onMounted(getRooms)
</script>

<style scoped>
.dashboard-container { padding: 25px; background-color: #f8fafc; min-height: 100vh; }

/* 轮播图样式 */
.carousel-section { margin-bottom: 30px; }
.room-card { position: relative; width: 100%; height: 100%; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.room-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s ease; }
.room-card:hover .room-img { transform: scale(1.1); }
.room-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.75); display: flex; align-items: center; justify-content: center;
  padding: 30px; box-sizing: border-box; opacity: 0; transition: opacity 0.4s ease;
}
.room-card:hover .room-overlay { opacity: 1; }
.overlay-content { text-align: center; color: #fff; transform: translateY(20px); transition: transform 0.4s ease; }
.room-card:hover .overlay-content { transform: translateY(0); }
.overlay-content h3 { font-size: 24px; margin-bottom: 15px; }
.overlay-content p { font-size: 14px; line-height: 1.6; margin-bottom: 20px; }
.room-title-bar { position: absolute; bottom: 0; width: 100%; background: linear-gradient(transparent, rgba(0,0,0,0.8)); color: white; padding: 15px; text-align: center; font-weight: bold; }

/* 统计卡片 */
.statistics { margin-bottom: 25px; }
.stat-card { border-radius: 12px; border: none; }
.stat-content { display: flex; align-items: center; padding: 5px; }
.stat-icon { width: 50px; height: 50px; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 24px; margin-right: 15px; }
.icon-blue { background: #eff6ff; color: #3b82f6; }
.icon-green { background: #f0fdf4; color: #22c55e; }
.icon-orange { background: #fff7ed; color: #f59e0b; }
.icon-red { background: #fef2f2; color: #ef4444; }
.label { font-size: 13px; color: #64748b; }
.value { font-size: 22px; font-weight: bold; color: #1e293b; }

/* 表格样式 */
.table-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 16px; font-weight: bold; color: #334155; }
.price-text { color: #e11d48; font-weight: 700; }
</style>