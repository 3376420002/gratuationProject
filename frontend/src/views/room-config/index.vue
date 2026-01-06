<template>
  <div class="config-container">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">🏨 酒店客房资源管理</span>
          <el-button type="primary" @click="handleAdd" icon="Plus">新增房间</el-button>
        </div>
      </template>

      <el-table :data="rooms" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="number" label="房号" width="100" align="center">
          <template #default="scope">
            <span class="room-number">{{ scope.row.number }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="房间类型" width="150" align="center">
          <template #default="scope">
            <el-tag :type="getRoomTypeTag(scope.row.room_type)" effect="dark" class="custom-tag">
              {{ scope.row.room_type || '未设房型' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="configuration" label="核心配置" show-overflow-tooltip>
           <template #default="scope">
             <span class="config-text">{{ scope.row.configuration || '暂无详细配置信息' }}</span>
           </template>
        </el-table-column>

        <el-table-column prop="price" label="标准房价" width="110" align="center">
          <template #default="scope">
            <span class="price-value">¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="当前状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '空闲' ? 'success' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              type="warning" 
              plain 
              @click="handleRepair(scope.row)"
              :disabled="scope.row.status === '维修中'"
            >报修</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑房间配置' : '新增房间'" width="450px" destroy-on-close>
      <el-form :model="form" label-width="100px" label-position="right">
        <el-form-item label="房号">
          <el-input v-model="form.number" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="房型种类">
          <el-select v-model="form.room_type" style="width: 100%">
            <el-option label="影音大床房" value="影音大床房" />
            <el-option label="电竞双人间" value="电竞双人间" />
            <el-option label="商务麻将房" value="商务麻将房" />
            <el-option label="标准双床房" value="标准双床房" />
          </el-select>
        </el-form-item>
        <el-form-item label="核心配置">
          <el-input v-model="form.configuration" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="标准房价">
          <el-input-number v-model="form.price" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确认并保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../../utils/request' 
import { ElMessage, ElMessageBox } from 'element-plus'

const rooms = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({ id: null, number: '', room_type: '', price: 0, configuration: '' })

const fetchRooms = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/reports/room-wall')
    rooms.value = res
  } catch (error) {
    ElMessage.error("获取数据失败")
  } finally {
    loading.value = false
  }
}

const getRoomTypeTag = (type) => {
  const map = { '影音大床房': 'success', '电竞双人间': 'primary', '商务麻将房': 'warning', '标准双床房': 'info' }
  return map[type] || ''
}

const handleAdd = () => {
  isEdit.value = false
  form.value = { id: null, number: '', room_type: '', price: 0, configuration: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  // 深拷贝，确保 id 和 configuration 都能进入表单
  form.value = JSON.parse(JSON.stringify(row))
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    const id = form.value.id
    if (isEdit.value) {
      // 这里的提交必须包含 configuration 字段给后端
      await request.put(`/api/rooms/${id}`, form.value)
      ElMessage.success('编辑已同步')
    } else {
      await request.post('/api/rooms', form.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchRooms() // 刷新列表查看最新配置
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleRepair = async (row) => {
  try {
    await request.put(`/api/rooms/${row.id}/status`, { status: '维修中' })
    ElMessage.warning(`房间 ${row.number} 已报修`)
    fetchRooms()
  } catch (e) { ElMessage.error('报修失败') }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除 ${row.number} 吗？`, '警告', { type: 'warning' }).then(async () => {
    await request.delete(`/api/rooms/${row.id}`)
    ElMessage.success('已删除')
    fetchRooms()
  })
}

onMounted(fetchRooms)
</script>

<style scoped>
.config-container { padding: 25px; background-color: #f0f2f5; min-height: 100vh; }
.main-card { border-radius: 8px; border: none; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 600; color: #409EFF; }
.price-value { color: #f56c6c; font-weight: bold; }
.config-text { color: #606266; font-size: 13px; }
</style>