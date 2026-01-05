<template>
  <div class="config-container">
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>🏨 酒店客房资源管理</span>
          <el-button type="primary" @click="handleAdd">新增房间</el-button>
        </div>
      </template>

      <el-table :data="rooms" border stripe style="width: 100%">
        <el-table-column prop="number" label="房号" width="120" />
        <el-table-column prop="room_type" label="房间类型" />
        <el-table-column prop="price" label="标准房价 (元/晚)">
          <template #default="scope">¥ {{ scope.row.price }}</template>
        </el-table-column>
        <el-table-column prop="status" label="当前状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === '空闲' ? 'success' : (scope.row.status === '已入住' ? 'danger' : 'warning')">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑房间' : '新增房间'" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="房号">
          <el-input v-model="form.number" :disabled="isEdit" placeholder="如：101" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.room_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="标准单人间" value="标准单人间" />
            <el-option label="豪华大床房" value="豪华大床房" />
            <el-option label="商务套房" value="商务套房" />
          </el-select>
        </el-form-item>
        <el-form-item label="房价">
          <el-input-number v-model="form.price" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../../utils/request' 
import { ElMessage, ElMessageBox } from 'element-plus'

const rooms = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null) 
const form = ref({ number: '', room_type: '', price: 0 })

const fetchRooms = async () => {
  const res = await request.get('/api/rooms')
  rooms.value = res
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = null
  form.value = { number: '', room_type: '', price: 0 }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentId.value = row.id 
  form.value = { 
    number: row.number, 
    room_type: row.room_type, 
    price: row.price 
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (isEdit.value) {
      await request.put(`/api/rooms/${currentId.value}`, form.value)
      ElMessage.success('修改成功')
    } else {

      await request.post('/api/rooms', form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchRooms() 
  } catch (err) {
    ElMessage.error('操作失败，请检查后端接口')
  }
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该房间吗？删除后相关的预订信息也会丢失！', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await request.delete(`/api/rooms/${id}`)
    ElMessage.success('删除成功')
    fetchRooms()
  }).catch(() => {})
}

onMounted(fetchRooms)
</script>

<style scoped>
.config-container {
  padding: 20px;
}
</style>