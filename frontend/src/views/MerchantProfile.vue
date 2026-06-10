<template>
  <div class="merchant-profile-page">
    <div class="mp-header">
      <div class="mph-bg"></div>
      <div class="mph-content">
        <div class="mph-logo">
          <img :src="profile.logo || 'https://img.yzcdn.cn/vant/cat.jpeg'" />
        </div>
        <div class="mph-name">{{ profile.name || '商家' }}</div>
        <div class="mph-meta">
          <span>★ {{ profile.rating }}</span>
          <span>· 月售{{ profile.monthly_sales || 0 }}</span>
        </div>
        <div :class="['mph-status', profile.status === 1 ? 'open' : 'closed']">
          {{ profile.status === 1 ? '🟢 营业中' : '🔴 休息中' }}
        </div>
      </div>
    </div>

    <div class="mp-section">
      <van-cell-group inset>
        <van-cell title="商家ID" :value="String(profile.id || '-')" />
        <van-cell title="电话" :value="profile.phone || '未填写'" />
        <van-cell title="地址" :value="profile.address || '未填写'" />
        <van-cell title="配送费" :value="'¥' + (profile.delivery_fee || 0)" />
        <van-cell title="起送价" :value="'¥' + (profile.min_price || 0)" />
      </van-cell-group>
    </div>

    <div class="mp-section">
      <van-cell-group inset>
        <van-cell title="编辑商家信息" is-link @click="openEditDialog" />
        <van-cell title="商品管理" is-link @click="showToast('开发中')" />
        <van-cell title="营业状态" center>
          <template #right-icon>
            <van-switch v-model="profile.status" :active-value="1" :inactive-value="0" active-color="#6B8E6B" size="24" @change="toggleStatus" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="logout-area"><button class="logout-btn" @click="handleLogout">退出登录</button></div>

    <van-popup v-model:show="showEdit" position="bottom" round :style="{ maxHeight: '85%' }" closeable title="编辑商家信息">
      <div class="edit-form">
        <van-form @submit="saveProfile">
          <van-cell-group inset>
            <van-field v-model="editForm.name" label="名称" placeholder="商家名称" :rules="[{ required: true }]" />
            <van-field v-model="editForm.phone" label="电话" placeholder="联系电话" />
            <van-field v-model="editForm.address" label="地址" placeholder="商家地址" rows="2" type="textarea" />
            <van-field v-model="editForm.lng" label="经度" placeholder="103.001" />
            <van-field v-model="editForm.lat" label="纬度" placeholder="29.978" />
            <van-field v-model="editForm.delivery_fee" label="配送费" type="number" placeholder="0" />
            <van-field v-model="editForm.min_price" label="起送价" type="number" placeholder="0" />
            <van-field v-model="editForm.logo" label="Logo URL" placeholder="图片URL" />
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
const profile = reactive({ id:0, name:'', address:'', phone:'', lng:0, lat:0, logo:'', rating:5, monthly_sales:0, delivery_fee:0, min_price:0, status:1 })
const showEdit = ref(false); const saving = ref(false)
const editForm = reactive({ name:'', phone:'', address:'', lng:'', lat:'', delivery_fee:'', min_price:'', logo:'' })

async function loadProfile() {
  try { const r = await axios.get('/api/merchant/profile'); if (r.data.code === 200) Object.assign(profile, r.data.data) } catch (e) { const c = store.userInfo; if (c) Object.assign(profile, c) }
}
function openEditDialog() {
  editForm.name = profile.name; editForm.phone = profile.phone; editForm.address = profile.address
  editForm.lng = String(profile.lng || ''); editForm.lat = String(profile.lat || '')
  editForm.delivery_fee = String(profile.delivery_fee || ''); editForm.min_price = String(profile.min_price || '')
  editForm.logo = profile.logo || ''; showEdit.value = true
}
async function saveProfile() {
  saving.value = true
  try {
    const p = { name: editForm.name, phone: editForm.phone, address: editForm.address, lng: parseFloat(editForm.lng)||0, lat: parseFloat(editForm.lat)||0, delivery_fee: parseFloat(editForm.delivery_fee)||0, min_price: parseFloat(editForm.min_price)||0, logo: editForm.logo }
    const r = await axios.put('/api/merchant/profile', p)
    if (r.data.code === 200) { Object.assign(profile, r.data.data); store.userInfo = r.data.data; localStorage.setItem('userInfo', JSON.stringify(r.data.data)); showEdit.value = false; showSuccessToast('已更新 ✨') }
    else showFailToast(r.data.msg || '保存失败')
  } catch (e) { showFailToast('网络错误') }
  finally { saving.value = false }
}
async function toggleStatus(v) { try { await axios.put('/api/merchant/profile', { status: v }); showToast(v === 1 ? '营业中 🟢' : '休息中 🔴') } catch (e) { profile.status = v === 1 ? 0 : 1; showFailToast('切换失败') } }
function handleLogout() {
  showDialog({ title:'退出商家账号', message:'确定退出吗？', showCancelButton:true, confirmButtonText:'退出', confirmButtonColor:'#C84B31' }).then(() => { store.logout(); showSuccessToast('已退出 🏪'); setTimeout(() => router.push('/login'), 1500) }).catch(() => {})
}
onMounted(loadProfile)
</script>

<style scoped>
.merchant-profile-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 40px; }

.mp-header { position: relative; padding: 30px 20px 36px; text-align: center; color: #fff; overflow: hidden; }
.mph-bg { position: absolute; inset: 0; background: linear-gradient(160deg, #C84B31, #8B3A2A 60%, #5C2618); border-radius: 0 0 50% 50% / 0 0 38% 35%; }
.mph-content { position: relative; z-index: 1; }
.mph-logo { width: 76px; height: 76px; border-radius: 18px; border: 3px solid rgba(255,255,255,0.4); overflow: hidden; margin: 0 auto 12px; }
.mph-logo img { width: 100%; height: 100%; object-fit: cover; }
.mph-name { font-size: 22px; font-weight: 700; }
.mph-meta { font-size: 13px; opacity: 0.9; margin-top: 4px; }
.mph-status { margin-top: 10px; font-size: 13px; padding: 4px 18px; border-radius: 20px; display: inline-block; }
.mph-status.open { background: rgba(107,142,107,0.3); }
.mph-status.closed { background: rgba(255,255,255,0.15); }

.mp-section { margin: -10px 8px 0; position: relative; z-index: 2; }
.mp-section + .mp-section { margin-top: 14px; }
.mp-section :deep(.van-cell-group) { border-radius: 16px; overflow: hidden; border: 1px solid var(--clay-border); }

.logout-area { padding: 30px 20px; }
.logout-btn { width: 100%; padding: 14px; border: 1px solid var(--clay-border); border-radius: 16px; background: var(--clay-card); color: var(--clay-text-soft); font-size: 15px; font-weight: 600; cursor: pointer; font-family: inherit; }
.logout-btn:active { background: var(--clay-danger-bg); color: var(--clay-danger); }

.edit-form { padding: 16px 0; }
</style>
