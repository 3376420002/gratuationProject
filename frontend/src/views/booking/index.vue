<!-- <template>
  <div class="room-manager-container">
    <div class="toolbar">
      <div class="page-title">
        <el-icon><Management /></el-icon>
        <span>前台客房管理</span>
      </div>
      <div class="filters">
        <el-radio-group v-model="filterStatus" @change="filterRooms">
          <el-radio-button label="全部" />
          <el-radio-button label="空闲" />
          <el-radio-button label="已入住" />
          <el-radio-button label="待打扫" />
        </el-radio-group>
        <el-button type="primary" :icon="Refresh" circle @click="loadRooms" />
      </div>
    </div>

    <div class="room-grid" v-loading="loading">
      <div 
        v-for="room in displayedRooms" 
        :key="room.id" 
        class="room-card"
        :class="getCardClass(room.status)"
        @click="handleCardClick(room)"
      >
        <div class="card-header">
          <span class="room-num">{{ room.number }}</span>
          <el-tag size="small" effect="dark" :type="getTagType(room.status)">
            {{ room.status }}
          </el-tag>
        </div>
        
        <div class="card-body">
          <div class="room-type">{{ room.room_type }}</div>
          <div class="room-price">¥{{ room.price }} / 晚</div>
          
          <div v-if="room.status === '已入住'" class="guest-info">
            <div class="guest-row">
              <el-icon><User /></el-icon> {{ room.guest_name }}
            </div>
            <div class="guest-row small">
              <el-icon><Iphone /></el-icon> {{ room.guest_phone }}
            </div>
          </div>
          
          <div v-else class="empty-hint">
            <el-icon><Plus /></el-icon> 点击办理入住
          </div>
        </div>

        <div class="card-overlay">
          <span>{{ getActionText(room.status) }}</span>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="checkInVisible"
      title="办理入住登记"
      width="500px"
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="checkInForm" label-position="top" :rules="rules" ref="checkInFormRef">
        <div class="dialog-header-info">
          正在为 <strong>{{ currentRoom?.number }}</strong> ({{ currentRoom?.room_type }}) 办理入住
        </div>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="住客姓名" prop="guest_name">
              <el-input v-model="checkInForm.guest_name" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="手机号码" prop="guest_phone">
              <el-input v-model="checkInForm.guest_phone" placeholder="11位手机号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="身份证号" prop="guest_id_card">
          <el-input v-model="checkInForm.guest_id_card" placeholder="请输入身份证号" />
        </el-form-item>

        <el-form-item label="预计住宿时间" prop="dateRange">
          <el-date-picker
            v-model="checkInForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="入住日期"
            end-placeholder="预计离店"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCheckIn" :loading="submitting">确认办理入住</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="checkOutVisible"
      title="退房账单结算"
      width="400px"
      class="custom-dialog"
    >
      <div v-loading="billLoading" class="bill-container">
        <div class="bill-header">
          <h2>{{ billInfo.room_number }}</h2>
          <p>{{ billInfo.room_type }}</p>
        </div>
        
        <div class="bill-details">
          <div class="bill-row">
            <span>住客姓名</span>
            <span>{{ billInfo.guest_name }}</span>
          </div>
          <div class="bill-row">
            <span>单价</span>
            <span>¥{{ billInfo.price_per_night }}</span>
          </div>
          <div class="bill-row">
            <span>入住天数</span>
            <span>x {{ billInfo.stay_days }} 天</span>
          </div>
          <el-divider border-style="dashed" />
          <div class="bill-row total">
            <span>应收总额</span>
            <span class="price">¥{{ billInfo.total_amount }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="checkOutVisible = false">取消</el-button>
        <el-button type="success" @click="submitCheckOut">确认收款并退房</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { User, Iphone, Management, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'
import dayjs from 'dayjs'

// 数据状态
const rooms = ref([])
const displayedRooms = ref([])
const loading = ref(false)
const filterStatus = ref('全部')
const currentRoom = ref(null)

// 入住表单
const checkInVisible = ref(false)
const submitting = ref(false)
const checkInFormRef = ref(null)
const checkInForm = ref({
  guest_name: '',
  guest_phone: '',
  guest_id_card: '',
  dateRange: []
})

// 退房数据
const checkOutVisible = ref(false)
const billLoading = ref(false)
const billInfo = ref({})

// 表单校验
const rules = {
  guest_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  guest_phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  guest_id_card: [{ required: true, message: '请输入身份证', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择入住时间', trigger: 'change' }]
}

// 1. 加载房间列表
const loadRooms = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/rooms')
    // 按房间号排序
    rooms.value = res.sort((a, b) => parseInt(a.number) - parseInt(b.number))
    filterRooms()
  } catch (error) {
    ElMessage.error('加载房态失败')
  } finally {
    loading.value = false
  }
}

// 筛选逻辑
const filterRooms = () => {
  if (filterStatus.value === '全部') {
    displayedRooms.value = rooms.value
  } else {
    displayedRooms.value = rooms.value.filter(r => r.status === filterStatus.value)
  }
}

// 2. 核心交互：点击卡片
const handleCardClick = (room) => {
  currentRoom.value = room
  
  if (room.status === '空闲') {
    // 打开入住弹窗
    checkInForm.value = {
      guest_name: '',
      guest_phone: '',
      guest_id_card: '',
      // 默认选中今天到明天
      dateRange: [dayjs().format('YYYY-MM-DD'), dayjs().add(1, 'day').format('YYYY-MM-DD')]
    }
    checkInVisible.value = true
    
  } else if (room.status === '已入住') {
    // 打开退房弹窗
    openCheckOut(room)
    
  } else if (room.status === '待打扫') {
    // 快捷转为空闲
    ElMessageBox.confirm('房间已打扫完毕，确认为空闲状态？', '房务确认', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => updateRoomStatus(room.id, '空闲'))
  }
}

// 3. 提交入住
const submitCheckIn = async () => {
  if (!checkInFormRef.value) return
  await checkInFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await request.post(`/api/rooms/${currentRoom.value.id}/walk-in`, {
          guest_name: checkInForm.value.guest_name,
          guest_phone: checkInForm.value.guest_phone,
          guest_id_card: checkInForm.value.guest_id_card,
          check_in_date: checkInForm.value.dateRange[0],
          check_out_date: checkInForm.value.dateRange[1]
        })
        ElMessage.success('入住办理成功')
        checkInVisible.value = false
        loadRooms()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '办理失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 4. 获取账单并准备退房
const openCheckOut = async (room) => {
  checkOutVisible.value = true
  billLoading.value = true
  try {
    const res = await request.get(`/api/rooms/${room.id}/bill`)
    billInfo.value = res
  } catch (error) {
    ElMessage.error('无法获取账单信息')
    checkOutVisible.value = false
  } finally {
    billLoading.value = false
  }
}

// 5. 确认退房
const submitCheckOut = async () => {
  try {
    await request.post(`/api/bookings/${billInfo.value.booking_id}/confirm-checkout`)
    ElMessage.success('退房结账成功，房间已转为待打扫')
    checkOutVisible.value = false
    loadRooms()
  } catch (error) {
    ElMessage.error('退房失败')
  }
}

// 辅助函数：手动更新状态（用于保洁）
const updateRoomStatus = async (roomId, status) => {
  try {
    // 这里复用之前的update接口，只更状态
    await request.put(`/api/rooms/${roomId}/status`, { 
      status: status,
      guest_name: null,
      guest_id_card: null,
      guest_phone: null
    })
    ElMessage.success('状态已更新')
    loadRooms()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 样式辅助
const getCardClass = (status) => {
  return {
    'status-free': status === '空闲',
    'status-occupied': status === '已入住',
    'status-cleaning': status === '待打扫',
    'status-repair': status === '维修中'
  }
}
const getTagType = (status) => {
  const map = { '空闲': 'success', '已入住': 'danger', '待打扫': 'warning' }
  return map[status] || 'info'
}
const getActionText = (status) => {
  const map = { '空闲': '办理入住', '已入住': '结账退房', '待打扫': '完成打扫' }
  return map[status] || '查看详情'
}

onMounted(loadRooms)
</script>

<style scoped>
.room-manager-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 84px);
}

/* 顶部栏 */
.toolbar {
  background: white;
  padding: 15px 25px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  margin-bottom: 25px;
}
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

/* 房态网格 */
.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

/* 卡片设计 */
.room-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  border: 2px solid transparent;
}
.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

/* 状态色条边框 */
.status-free { border-top-color: #67c23a; }
.status-occupied { border-top-color: #f56c6c; }
.status-cleaning { border-top-color: #e6a23c; }

/* 卡片内部 */
.card-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f5f7fa;
}
.room-num {
  font-size: 20px;
  font-weight: 800;
  color: #303133;
}

.card-body {
  padding: 20px 15px;
  text-align: center;
}
.room-type {
  color: #606266;
  font-size: 14px;
  margin-bottom: 5px;
}
.room-price {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
}

.guest-info {
  margin-top: 15px;
  background: #fef0f0;
  padding: 8px;
  border-radius: 6px;
  color: #f56c6c;
}
.guest-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 14px;
  font-weight: 600;
}
.guest-row.small {
  font-size: 12px;
  font-weight: normal;
  margin-top: 4px;
}

.empty-hint {
  margin-top: 15px;
  color: #c0c4cc;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* 悬浮遮罩 */
.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  opacity: 0;
  transition: opacity 0.3s;
}
.room-card:hover .card-overlay {
  opacity: 1;
}

/* 弹窗样式 */
.dialog-header-info {
  background: #ecf5ff;
  color: #409eff;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

/* 账单样式 */
.bill-container {
  text-align: center;
  padding: 10px;
}
.bill-header h2 {
  font-size: 32px;
  margin: 0;
  color: #303133;
}
.bill-header p {
  color: #909399;
  margin: 5px 0 20px;
}
.bill-details {
  background: #f9fafc;
  padding: 15px;
  border-radius: 8px;
}
.bill-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  color: #606266;
}
.bill-row.total {
  margin-top: 15px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
.bill-row.total .price {
  color: #f56c6c;
  font-size: 24px;
}
</style> -->

<template>
  <div class="room-manager-container">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">
          <el-icon><Management /></el-icon>
          <span>前台客房管理</span>
        </div>
      </div>

      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索房号..."
          prefix-icon="Search"
          clearable
          style="width: 150px"
          @input="filterRooms"
        />

        <el-select 
          v-model="selectedType" 
          placeholder="所有房型" 
          clearable 
          style="width: 160px"
          @change="filterRooms"
        >
          <el-option 
            v-for="type in uniqueRoomTypes" 
            :key="type" 
            :label="type" 
            :value="type" 
          />
        </el-select>

        <el-radio-group v-model="filterStatus" @change="filterRooms">
          <el-radio-button label="全部" />
          <el-radio-button label="空闲" />
          <el-radio-button label="已入住" />
          <el-radio-button label="待打扫" />
        </el-radio-group>

        <el-button type="primary" :icon="Refresh" circle @click="loadRooms" title="刷新数据" />
      </div>
    </div>

    <div class="room-grid" v-loading="loading">
      <div v-if="displayedRooms.length === 0" class="no-data">
        <el-empty description="没有找到符合条件的房间" />
      </div>

      <div 
        v-for="room in displayedRooms" 
        :key="room.id" 
        class="room-card"
        :class="getCardClass(room.status)"
        @click="handleCardClick(room)"
      >
        <div class="card-header">
          <span class="room-num">{{ room.number }}</span>
          <el-tag size="small" effect="dark" :type="getTagType(room.status)">
            {{ room.status }}
          </el-tag>
        </div>
        
        <div class="card-body">
          <div class="room-type">{{ room.room_type }}</div>
          <div class="room-price">¥{{ room.price }} / 晚</div>
          
          <div v-if="room.status === '已入住'" class="guest-info">
            <div class="guest-row">
              <el-icon><User /></el-icon> {{ room.guest_name }}
            </div>
            <div class="guest-row small">
              <el-icon><Iphone /></el-icon> {{ room.guest_phone }}
            </div>
          </div>
          
          <div v-else class="empty-hint">
            <el-icon><Plus /></el-icon> 点击办理入住
          </div>
        </div>
        
        <div class="card-overlay">
          <span>{{ getActionText(room.status) }}</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="checkInVisible" title="办理入住登记" width="500px" destroy-on-close>
      <el-form :model="checkInForm" label-position="top" :rules="rules" ref="checkInFormRef">
        <div class="dialog-header-info">
          正在为 <strong>{{ currentRoom?.number }}</strong> ({{ currentRoom?.room_type }}) 办理入住
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="住客姓名" prop="guest_name">
              <el-input v-model="checkInForm.guest_name" placeholder="请输入真实姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="手机号码" prop="guest_phone">
              <el-input v-model="checkInForm.guest_phone" placeholder="11位手机号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="身份证号" prop="guest_id_card">
          <el-input v-model="checkInForm.guest_id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="预计住宿时间" prop="dateRange">
          <el-date-picker
            v-model="checkInForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="入住日期"
            end-placeholder="预计离店"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCheckIn" :loading="submitting">确认办理入住</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="checkOutVisible" title="退房账单结算" width="400px">
      <div v-loading="billLoading" class="bill-container">
        <div class="bill-header">
          <h2>{{ billInfo.room_number }}</h2>
          <p>{{ billInfo.room_type }}</p>
        </div>
        <div class="bill-details">
          <div class="bill-row">
            <span>住客姓名</span>
            <span>{{ billInfo.guest_name }}</span>
          </div>
          <div class="bill-row">
            <span>单价</span>
            <span>¥{{ billInfo.price_per_night }}</span>
          </div>
          <div class="bill-row">
            <span>入住天数</span>
            <span>x {{ billInfo.stay_days }} 天</span>
          </div>
          <el-divider border-style="dashed" />
          <div class="bill-row total">
            <span>应收总额</span>
            <span class="price">¥{{ billInfo.total_amount }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="checkOutVisible = false">取消</el-button>
        <el-button type="success" @click="submitCheckOut">确认收款并退房</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
// 注意：这里引入了 Search 图标
import { User, Iphone, Management, Refresh, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'
import dayjs from 'dayjs'

// 数据状态
const rooms = ref([])
const displayedRooms = ref([])
const loading = ref(false)
const currentRoom = ref(null)

// --- 新增的筛选状态 ---
const filterStatus = ref('全部')
const searchKeyword = ref('') // 房间号搜索词
const selectedType = ref('')  // 选中的房型

// --- 自动计算有哪些房型 (去重) ---
const uniqueRoomTypes = computed(() => {
  const types = rooms.value.map(r => r.room_type)
  return [...new Set(types)] // ES6 去重
})

// 入住表单相关
const checkInVisible = ref(false)
const submitting = ref(false)
const checkInFormRef = ref(null)
const checkInForm = ref({ guest_name: '', guest_phone: '', guest_id_card: '', dateRange: [] })
const rules = {
  guest_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  guest_phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  guest_id_card: [{ required: true, message: '请输入身份证', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择入住时间', trigger: 'change' }]
}

// 退房数据
const checkOutVisible = ref(false)
const billLoading = ref(false)
const billInfo = ref({})

// 1. 加载房间列表
const loadRooms = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/rooms')
    // 按房间号排序
    rooms.value = res.sort((a, b) => parseInt(a.number) - parseInt(b.number))
    filterRooms() // 加载完立即筛选一次
  } catch (error) {
    ElMessage.error('加载房态失败')
  } finally {
    loading.value = false
  }
}

// --- 核心升级：多条件联合筛选 ---
const filterRooms = () => {
  displayedRooms.value = rooms.value.filter(room => {
    // 1. 状态匹配
    const matchStatus = filterStatus.value === '全部' || room.status === filterStatus.value
    
    // 2. 房型匹配 (如果没选房型，则算匹配)
    const matchType = !selectedType.value || room.room_type === selectedType.value
    
    // 3. 房间号模糊搜索 (如果没输文字，则算匹配)
    const matchSearch = !searchKeyword.value || room.number.includes(searchKeyword.value)

    // 三个条件必须同时满足
    return matchStatus && matchType && matchSearch
  })
}

// 2. 点击卡片逻辑 (保持不变)
const handleCardClick = (room) => {
  currentRoom.value = room
  if (room.status === '空闲') {
    checkInForm.value = {
      guest_name: '', guest_phone: '', guest_id_card: '',
      dateRange: [dayjs().format('YYYY-MM-DD'), dayjs().add(1, 'day').format('YYYY-MM-DD')]
    }
    checkInVisible.value = true
  } else if (room.status === '已入住') {
    openCheckOut(room)
  } else if (room.status === '待打扫') {
    ElMessageBox.confirm('房间已打扫完毕，确认为空闲状态？', '房务确认', {
      confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning'
    }).then(() => updateRoomStatus(room.id, '空闲'))
  }
}

// 3. 提交入住 (保持不变)
const submitCheckIn = async () => {
  if (!checkInFormRef.value) return
  await checkInFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await request.post(`/api/rooms/${currentRoom.value.id}/walk-in`, {
          guest_name: checkInForm.value.guest_name,
          guest_phone: checkInForm.value.guest_phone,
          guest_id_card: checkInForm.value.guest_id_card,
          check_in_date: checkInForm.value.dateRange[0],
          check_out_date: checkInForm.value.dateRange[1]
        })
        ElMessage.success('入住办理成功')
        checkInVisible.value = false
        loadRooms()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '办理失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 4. 获取账单 (保持不变)
const openCheckOut = async (room) => {
  checkOutVisible.value = true
  billLoading.value = true
  try {
    const res = await request.get(`/api/rooms/${room.id}/bill`)
    billInfo.value = res
  } catch (error) {
    ElMessage.error('无法获取账单信息')
    checkOutVisible.value = false
  } finally {
    billLoading.value = false
  }
}

// 5. 确认退房 (保持不变)
const submitCheckOut = async () => {
  try {
    await request.post(`/api/bookings/${billInfo.value.booking_id}/confirm-checkout`)
    ElMessage.success('退房结账成功')
    checkOutVisible.value = false
    loadRooms()
  } catch (error) {
    ElMessage.error('退房失败')
  }
}

// 辅助函数 (保持不变)
const updateRoomStatus = async (roomId, status) => {
  try {
    await request.put(`/api/rooms/${roomId}/status`, { 
      status: status, guest_name: null, guest_id_card: null, guest_phone: null
    })
    ElMessage.success('状态已更新')
    loadRooms()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}
const getCardClass = (status) => ({
  'status-free': status === '空闲',
  'status-occupied': status === '已入住',
  'status-cleaning': status === '待打扫',
  'status-repair': status === '维修中'
})
const getTagType = (status) => {
  const map = { '空闲': 'success', '已入住': 'danger', '待打扫': 'warning' }
  return map[status] || 'info'
}
const getActionText = (status) => {
  const map = { '空闲': '办理入住', '已入住': '结账退房', '待打扫': '完成打扫' }
  return map[status] || '查看详情'
}

onMounted(loadRooms)
</script>

<style scoped>
.room-manager-container {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 84px);
}

/* --- 顶部栏样式升级 --- */
.toolbar {
  background: white;
  padding: 15px 25px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  margin-bottom: 25px;
  flex-wrap: wrap; /* 防止小屏幕拥挤 */
  gap: 15px;
}

.toolbar-left { display: flex; align-items: center; }
.toolbar-right { display: flex; align-items: center; gap: 15px; }

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

/* 房态网格 */
.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.no-data {
  grid-column: 1 / -1; /* 占满所有列 */
  display: flex;
  justify-content: center;
  padding: 50px 0;
}

/* 卡片样式 (保持不变) */
.room-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  border: 2px solid transparent;
}
.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}
.status-free { border-top-color: #67c23a; }
.status-occupied { border-top-color: #f56c6c; }
.status-cleaning { border-top-color: #e6a23c; }

.card-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f5f7fa;
}
.room-num { font-size: 20px; font-weight: 800; color: #303133; }

.card-body { padding: 20px 15px; text-align: center; }
.room-type { color: #606266; font-size: 14px; margin-bottom: 5px; }
.room-price { color: #409eff; font-weight: bold; font-size: 16px; }

.guest-info { margin-top: 15px; background: #fef0f0; padding: 8px; border-radius: 6px; color: #f56c6c; }
.guest-row { display: flex; align-items: center; justify-content: center; gap: 5px; font-size: 14px; font-weight: 600; }
.guest-row.small { font-size: 12px; font-weight: normal; margin-top: 4px; }

.empty-hint { margin-top: 15px; color: #c0c4cc; font-size: 13px; display: flex; align-items: center; justify-content: center; gap: 4px; }

.card-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7); color: white;
  display: flex; justify-content: center; align-items: center;
  font-size: 18px; font-weight: bold;
  opacity: 0; transition: opacity 0.3s;
}
.room-card:hover .card-overlay { opacity: 1; }

/* 弹窗样式补充 */
.dialog-header-info { background: #ecf5ff; color: #409eff; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }
.bill-container { text-align: center; padding: 10px; }
.bill-header h2 { font-size: 32px; margin: 0; color: #303133; }
.bill-header p { color: #909399; margin: 5px 0 20px; }
.bill-details { background: #f9fafc; padding: 15px; border-radius: 8px; }
.bill-row { display: flex; justify-content: space-between; margin-bottom: 12px; color: #606266; }
.bill-row.total { margin-top: 15px; font-size: 18px; font-weight: bold; color: #303133; }
.bill-row.total .price { color: #f56c6c; font-size: 24px; }
</style>