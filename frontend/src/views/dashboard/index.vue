<template>
  <div class="dashboard-container">

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
          <div>
            <!-- <el-button type="success" @click="showDialog = true">新增房间</el-button> -->
            <el-button type="primary" @click="getRooms">刷新数据</el-button>
          </div>
        </div>
      </template>

      <el-table :data="rooms" v-loading="loading" stripe border>
        <el-table-column prop="number" label="房间号" width="100" />
        <el-table-column prop="room_type" label="房型" />
        <el-table-column prop="price" label="房费/日">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold">￥{{ scope.row.price }}</span>
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
              <el-tag type="info" effect="plain">👤 {{ scope.row.guest_name }}</el-tag>
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
            
            <el-button v-if="scope.row.status === '空闲'" size="small" type="danger" plain @click="updateRoomStatus(scope.row, '维修中')">报修</el-button>
            <el-button v-if="scope.row.status === '维修中'" size="small" type="success" plain @click="updateRoomStatus(scope.row, '空闲')">修毕</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" title="新增客房" width="400px">
      <el-form :model="newRoom" label-width="80px">
        <el-form-item label="房间号"><el-input v-model="newRoom.number" /></el-form-item>
        <el-form-item label="房型">
          <el-select v-model="newRoom.room_type" style="width: 100%">
            <el-option label="标准单人间" value="标准单人间" />
            <el-option label="豪华大床房" value="豪华大床房" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格"><el-input-number v-model="newRoom.price" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddRoom">提交</el-button>
      </template>
    </el-dialog>

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
          <div style="font-size: 12px; color: #999">请输入小卖部、饮品等额外费用</div>
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
import { useRouter } from 'vue-router'

const router = useRouter()
const rooms = ref([])
const loading = ref(false)
const showDialog = ref(false)
const showCheckInDialog = ref(false)
const showCheckOutDialog = ref(false) 
const currentRoom = ref(null)      
const extraCharge = ref(0)

const newRoom = ref({ number: '', room_type: '', price: 0, status: '空闲' })
const checkInForm = ref({ guest_name: '', guest_id_card: '', guest_phone: '' })


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
  rooms.value = await request.get('/api/rooms')
  loading.value = false
}

const openCheckIn = (room) => {
  currentRoom.value = room
  checkInForm.value = { guest_name: '', guest_id_card: '', guest_phone: '' }
  showCheckInDialog.value = true
}

const submitCheckIn = async () => {
  if (!checkInForm.value.guest_name) return ElMessage.warning('姓名必填')
  await request.put(`/api/rooms/${currentRoom.value.id}/status`, {
    status: '已入住',
    ...checkInForm.value
  })
  showCheckInDialog.value = false
  getRooms()
}

const openCheckOut = (room) => {
  currentRoom.value = room
  extraCharge.value = 0 // 重置金额
  showCheckOutDialog.value = true
}

const confirmCheckOut = async () => {
  const total = currentRoom.value.price + extraCharge.value
  try {
    await request.put(`/api/rooms/${currentRoom.value.id}/status`, {
      status: '待打扫',
      guest_name: '', guest_id_card: '', guest_phone: ''
    })
    
    ElMessageBox.alert(
      `结算完成！<br/>房费：￥${currentRoom.value.price}<br/>额外消费：￥${extraCharge.value}<hr/><b>实收总额：￥${total}</b>`,
      '收银凭据',
      { dangerouslyUseHTMLString: true, type: 'success' }
    )
    
    showCheckOutDialog.value = false
    getRooms()
  } catch (error) {
    ElMessage.error('结算失败')
  }
}

const updateRoomStatus = async (room, nextStatus) => {
  await request.put(`/api/rooms/${room.id}/status`, {
    status: nextStatus,
    guest_name: '', guest_id_card: '', guest_phone: ''
  })
  ElMessage.success(`操作成功`)
  getRooms()
}

const handleAddRoom = async () => {
  await request.post('/api/rooms', newRoom.value)
  showDialog.value = false
  getRooms()
}
const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除吗？', '警告').then(async () => {
    await request.delete(`/api/rooms/${id}`)
    getRooms()
  })
}
const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(getRooms)
</script>

<style scoped>
.dashboard-container { padding: 0 20px 20px 20px; background-color: #f5f7fa; min-height: 100vh; }
.top-header { height: 64px; display: flex; justify-content: space-between; align-items: center; background-color: #fff; margin: 0 -20px 25px -20px; padding: 0 30px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.system-title { font-size: 22px; font-weight: bold; color: #409EFF; }
.statistics { margin-bottom: 25px; }
.stat-card { border-radius: 12px; border: none; transition: transform 0.3s; }
.stat-card:hover { transform: translateY(-5px); }
.stat-content { display: flex; align-items: center; padding: 10px 5px; }
.stat-icon { width: 54px; height: 54px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 28px; margin-right: 15px; }
.icon-blue { background: #ecf5ff; color: #409eff; }
.icon-green { background: #f0f9eb; color: #67c23a; }
.icon-orange { background: #fdf6ec; color: #e6a23c; }
.icon-red { background: #fef0f0; color: #f56c6c; }
.label { font-size: 13px; color: #909399; margin-bottom: 6px; }
.value { font-size: 22px; font-weight: bold; color: #303133; }
.table-card { border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.03); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: bold; color: #409eff; }
</style>