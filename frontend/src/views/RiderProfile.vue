<template>
  <div class="rider-profile-page">
    <div class="rp-header">
      <div class="rph-bg"></div>
      <div class="rph-content">
        <div class="rph-avatar">🛵</div>
        <div class="rph-name">{{ profile.name || '骑手' }}</div>
        <div :class="['rph-status', profile.status === 0 ? 'idle' : 'busy']">
          <span class="rphs-dot"></span>
          {{ profile.status === 0 ? '空闲中' : '配送中' }}
        </div>
      </div>
    </div>

    <div class="rp-section">
      <van-cell-group inset>
        <van-cell title="骑手ID" :value="String(profile.id || '-')" />
        <van-cell title="姓名" :value="profile.name || '未填写'" />
        <van-cell title="电话" :value="profile.phone || '未填写'" />
        <van-cell title="位置" :value="`${profile.lng?.toFixed(4)}, ${profile.lat?.toFixed(4)}`" label="GPS/模拟定位自动更新" />
      </van-cell-group>
    </div>

    <div class="rp-section">
      <van-cell-group inset>
        <van-cell title="编辑信息" is-link @click="openEditDialog" />
        <van-cell title="配送记录" is-link @click="showToast('开发中')" />
        <van-cell title="收入统计" is-link @click="showToast('开发中')" />
      </van-cell-group>
    </div>

    <div class="logout-area"><button class="logout-btn" @click="handleLogout">退出登录</button></div>

    <van-popup v-model:show="showEdit" position="bottom" round :style="{ maxHeight: '70%' }" closeable title="编辑信息">
      <div class="edit-form">
        <van-form @submit="saveProfile">
          <van-cell-group inset>
            <van-field v-model="editForm.name" label="姓名" placeholder="请输入姓名" :rules="[{ required: true }]" />
            <van-field v-model="editForm.phone" label="电话" placeholder="请输入手机号" :rules="[{ required: true }, { pattern: /^1\d{10}$/, message: '请输入正确手机号' }]" />
          </van-cell-group>
          <div style="margin:16px"><van-button round block type="primary" native-type="submit" :loading="saving">保存</van-button></div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/index'
import axios from 'axios'
import { showToast, showSuccessToast, showFailToast, showDialog } from 'vant'

const router = useRouter(); const store = useAppStore()
const profile = reactive({ id:0, name:'', phone:'', lng:0, lat:0, status:0 })
const showEdit = ref(false); const saving = ref(false)
const editForm = reactive({ name:'', phone:'' })

async function loadProfile() {
  try { const r = await axios.get('/api/rider/profile'); if (r.data.code === 200) Object.assign(profile, r.data.data) } catch (e) { const c = store.userInfo; if (c) Object.assign(profile, c) }
}
function openEditDialog() { editForm.name = profile.name; editForm.phone = profile.phone; showEdit.value = true }
async function saveProfile() {
  saving.value = true
  try {
    const r = await axios.put('/api/rider/profile', { name: editForm.name, phone: editForm.phone })
    if (r.data.code === 200) { Object.assign(profile, r.data.data); store.userInfo = r.data.data; localStorage.setItem('userInfo', JSON.stringify(r.data.data)); showEdit.value = false; showSuccessToast('已更新 ✨') }
    else showFailToast(r.data.msg || '保存失败')
  } catch (e) { showFailToast('网络错误') }
  finally { saving.value = false }
}
function handleLogout() {
  showDialog({ title:'退出骑手账号', message:'确定退出吗？', showCancelButton:true, confirmButtonText:'退出', confirmButtonColor:'#C84B31' }).then(() => { store.logout(); showSuccessToast('已退出 🛵'); setTimeout(() => router.push('/login'), 1500) }).catch(() => {})
}
onMounted(loadProfile)
</script>

<style scoped>
.rider-profile-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 40px; }

.rp-header { position: relative; padding: 30px 20px 36px; text-align: center; color: #fff; overflow: hidden; }
.rph-bg { position: absolute; inset: 0; background: linear-gradient(160deg, #C84B31, #8B3A2A 60%, #5C2618); border-radius: 0 0 50% 50% / 0 0 38% 35%; }
.rph-content { position: relative; z-index: 1; }
.rph-avatar { width: 76px; height: 76px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.4); background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-size: 40px; margin: 0 auto 12px; }
.rph-name { font-size: 22px; font-weight: 700; }
.rph-status { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; font-size: 13px; font-weight: 600; padding: 4px 18px; border-radius: 20px; }
.rph-status.idle { background: rgba(107,142,107,0.3); }
.rph-status.busy { background: rgba(255,255,255,0.15); }
.rphs-dot { width: 8px; height: 8px; border-radius: 50%; }
.idle .rphs-dot { background: var(--clay-success); }
.busy .rphs-dot { background: #FF8C3A; }

.rp-section { margin: -10px 8px 0; position: relative; z-index: 2; }
.rp-section + .rp-section { margin-top: 14px; }
.rp-section :deep(.van-cell-group) { border-radius: 16px; overflow: hidden; border: 1px solid var(--clay-border); }

.logout-area { padding: 30px 20px; }
.logout-btn { width: 100%; padding: 14px; border: 1px solid var(--clay-border); border-radius: 16px; background: var(--clay-card); color: var(--clay-text-soft); font-size: 15px; font-weight: 600; cursor: pointer; font-family: inherit; }
.logout-btn:active { background: var(--clay-danger-bg); color: var(--clay-danger); }

.edit-form { padding: 16px 0; }
</style>
