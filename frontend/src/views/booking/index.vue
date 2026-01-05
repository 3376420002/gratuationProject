<template>
  <div class="booking-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>📅 未来房态查询</span>
              <el-date-picker
                v-model="searchDate"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                @change="checkRoomAvailability"
              />
            </div>
          </template>
          
          <el-table :data="availableRooms" border stripe v-loading="loading">
            <el-table-column prop="number" label="房号" width="100" />
            <el-table-column prop="room_type" label="房型" />
            <el-table-column prop="price" label="单价" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="primary" size="small" @click="openBookingDialog(scope.row)">
                  登记预订
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card header="今日预订提醒" shadow="never">
          <el-timeline v-if="todayBookings.length > 0">
            <el-timeline-item 
              v-for="(item, index) in todayBookings" 
              :key="index"
              :timestamp="item.time" 
              type="primary"
            >
              {{ item.guest_name }} - {{ item.room_number }}房间
            </el-timeline-item>
          </el-timeline>

          <el-empty v-else description="今日无预定" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="bookingVisible" title="新建预订订单" width="450px">
      <el-form :model="bookingForm" label-width="100px">
        <el-form-item label="所选房间">
          <el-tag>{{ selectedRoom?.number }} ({{ selectedRoom?.room_type }})</el-tag>
        </el-form-item>
        <el-form-item label="预订人">
          <el-input v-model="bookingForm.guest_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="入住周期">
          <el-date-picker
            v-model="bookingForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="入住"
            end-placeholder="离店"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">提交订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../../utils/request'
import { ElMessage } from 'element-plus'

const searchDate = ref(new Date().toISOString().split('T')[0])
const availableRooms = ref([])
const loading = ref(false)
const bookingVisible = ref(false)
const selectedRoom = ref(null)
const bookingForm = ref({ guest_name: '', dateRange: [] })
const todayBookings = ref([])


const checkRoomAvailability = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/rooms/available', {
      params: { 
        target_date: searchDate.value  
      }
    })
    availableRooms.value = res
  } catch (error) {
    console.error(error)
    ElMessage.error('查询失败')
  }
  loading.value = false
}

const openBookingDialog = (room) => {
  selectedRoom.value = room
  bookingVisible.value = true
}

const fetchTodayBookings = async () => {
  try {
    const res = await request.get('/api/bookings/today')
    todayBookings.value = res
  } catch (error) {
    console.error("获取提醒失败", error)
  }
}


const submitOrder = async () => {
  if (!bookingForm.value.guest_name || !bookingForm.value.dateRange) {
    return ElMessage.warning('请填写完整信息')
  }
  
  try {
    await request.post('/api/bookings', {
      room_id: selectedRoom.value.id,
      guest_name: bookingForm.value.guest_name,
      start_date: bookingForm.value.dateRange[0],
      end_date: bookingForm.value.dateRange[1]
    })
    ElMessage.success('预订成功！')
    bookingVisible.value = false
    checkRoomAvailability()
  } catch (error) {
    ElMessage.error('该时段房间已被占用')
  }
}


onMounted(() => {
  checkRoomAvailability()
  fetchTodayBookings() 
})
</script>