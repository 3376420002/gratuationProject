<!-- <template>
  <div class="member-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span style="font-weight: bold; font-size: 18px;">💎 会员体系管理</span>
          <el-button type="primary" @click="openAddDialog">新增会员</el-button>
        </div>
      </template>

      <el-table :data="memberList" stripe style="width: 100%">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="level" label="等级">
          <template #default="scope">
            <el-tag :type="getLevelTag(scope.row.level)">{{ scope.row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="当前积分" />
        <el-table-column prop="balance" label="余额 (¥)">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">{{ scope.row.balance.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reg_date" label="注册日期" width="150" />
        
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">注销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '修改会员信息' : '新会员入会'" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="初始密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="form.level" placeholder="请选择等级">
            <el-option label="普通会员" value="普通会员" />
            <el-option label="白金会员" value="白金会员" />
            <el-option label="钻石会员" value="钻石会员" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户余额">
          <el-input-number v-model="form.balance" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const memberList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', phone: '', password: '123', level: '普通会员', balance: 0 })
const currentId = ref(null)

// 获取会员数据
const fetchMembers = async () => {
  const res = await axios.get('http://127.0.0.1:8088/api/members')
  memberList.value = res.data
}

// 保存逻辑
const handleSave = async () => {
  if (isEdit.value) {
    await axios.put(`http://127.0.0.1:8088/api/members/${currentId.value}`, form.value)
    ElMessage.success('更新成功')
  } else {
    await axios.post('http://127.0.0.1:8088/api/members', form.value)
    ElMessage.success('入会成功')
  }
  dialogVisible.value = false
  fetchMembers()
}

// 删除逻辑
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要注销该会员吗？此操作不可恢复', '警告', { type: 'warning' }).then(async () => {
    await axios.delete(`http://127.0.0.1:8088/api/members/${id}`)
    ElMessage.success('注销成功')
    fetchMembers()
  })
}

// 辅助：等级标签颜色
const getLevelTag = (level) => {
  if (level === '钻石会员') return 'danger'
  if (level === '白金会员') return 'warning'
  return 'info'
}

const openAddDialog = () => {
  isEdit.value = false
  form.value = { name: '', phone: '', password: '123', level: '普通会员', balance: 0 }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  currentId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

onMounted(fetchMembers)
</script>

<style scoped>
.member-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style> -->


<template>
  <div class="member-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="title">
            <el-icon><User /></el-icon>
            <span>会员体系管理</span>
          </div>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>新增会员
          </el-button>
        </div>
      </template>

      <el-table :data="memberList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column prop="level" label="等级" min-width="120">
          <template #default="scope">
            <el-tag :type="getLevelTag(scope.row.level)" effect="dark">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" min-width="100">
          <template #default="scope">
            <el-statistic :value="scope.row.points" color="#409EFF" />
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额 (¥)" min-width="120">
          <template #default="scope">
            <span class="balance-text">¥{{ scope.row.balance.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reg_date" label="注册日期" min-width="120" />
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(scope.row)">注销</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '修改会员信息' : '新会员入会'" 
      width="460px"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" style="padding-right: 20px;">
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="登录密码">
          <el-input v-model="form.password" type="password" show-password placeholder="设置初始密码" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-radio-group v-model="form.level">
            <el-radio-button label="普通会员" />
            <el-radio-button label="白金会员" />
            <el-radio-button label="钻石会员" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="账户余额">
          <el-input-number v-model="form.balance" :precision="2" :step="100" :min="0" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSave">确 定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus } from '@element-plus/icons-vue'

const memberList = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref(null)

const form = ref({
  name: '',
  phone: '',
  password: '123',
  level: '普通会员',
  balance: 0
})

// 初始化获取数据
const fetchMembers = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8088/api/members')
    memberList.value = res.data
  } catch (err) {
    ElMessage.error('获取会员列表失败')
  } finally {
    loading.value = false
  }
}

// 保存（新增/编辑）
const handleSave = async () => {
  try {
    if (isEdit.value) {
      await axios.put(`http://127.0.0.1:8088/api/members/${currentId.value}`, form.value)
      ElMessage.success('会员信息更新成功')
    } else {
      await axios.post('http://127.0.0.1:8088/api/members', form.value)
      ElMessage.success('会员注册成功')
    }
    dialogVisible.value = false
    fetchMembers()
  } catch (err) {
    ElMessage.error('操作失败，请检查后端服务')
  }
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要注销会员 [${row.name}] 吗？注销后积分和余额将清空。`, '警告', {
    confirmButtonText: '确定注销',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await axios.delete(`http://127.0.0.1:8088/api/members/${row.id}`)
    ElMessage.success('已成功注销该会员')
    fetchMembers()
  })
}

// 标签颜色逻辑
const getLevelTag = (level) => {
  const map = { '钻石会员': 'danger', '白金会员': 'warning', '普通会员': 'info' }
  return map[level] || 'info'
}

const openAddDialog = () => {
  isEdit.value = false
  form.value = { name: '', phone: '', password: '123', level: '普通会员', balance: 0 }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  currentId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

onMounted(fetchMembers)
</script>

<style scoped>
.member-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}
.balance-text {
  color: #f56c6c;
  font-weight: bold;
}
</style>