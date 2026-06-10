<template>
  <div class="merchant-order-page">
    <!-- 自定义导航 -->
    <div class="mo-navbar">
      <div class="mon-title">订单管理</div>
      <div class="mon-actions">
        <button class="mon-btn" @click="loadOrders">↻</button>
        <button class="mon-btn" @click="$router.push('/merchant-profile')">👤</button>
        <button class="mon-btn" @click="handleLogout">↩</button>
      </div>
    </div>

    <van-notice-bar v-if="newOrderAlert" mode="closeable" color="#C84B31" background="#FCEAE4" left-icon="volume-o" @close="newOrderAlert = false">
      新订单！订单号 #{{ newOrderId }}
    </van-notice-bar>

    <van-tabs v-model:active="activeTab" color="var(--clay-brand)" sticky>
      <van-tab title="新订单" name="1" :badge="counts[1]" />
      <van-tab title="进行中" name="2" :badge="counts[2]" />
      <van-tab title="配送中" name="3" :badge="counts[3]" />
      <van-tab title="已完成" name="4" />
    </van-tabs>

    <div class="mo-list">
      <article v-for="o in orders" :key="o.id" class="mo-card" @click="showDetail(o)">
        <div class="moc-head">
          <span class="moc-id">#{{ o.id }}</span>
          <span :class="['moc-status', statusClass(o.status)]">{{ statusText(o.status) }}</span>
        </div>
        <div class="moc-user">👤 {{ o.user_name }} {{ o.user_phone }}</div>
        <div class="moc-items">
          <span v-for="item in o.items" :key="item.name" class="moc-item-tag">{{ item.name }}×{{ item.qty }}</span>
        </div>
        <div class="moc-addr">📍 {{ o.address }}</div>
        <div class="moc-remark" v-if="o.remark">📝 {{ o.remark }}</div>
        <div class="moc-foot">
          <span class="moc-time">{{ o.create_time }}</span>
          <span class="moc-total">¥{{ o.total_amount }}</span>
        </div>
        <div class="moc-actions" v-if="o.status === 1" @click.stop>
          <button class="moa-reject" @click.stop="rejectOrder(o.id)">拒单</button>
          <button class="moa-accept" @click.stop="acceptOrder(o.id)">接单</button>
        </div>
        <div class="moc-actions" v-if="o.status === 2 || o.status === 3" @click.stop>
          <button class="moa-accept" @click.stop="completeOrder(o.id)">确认完成</button>
        </div>
      </article>
      <van-empty v-if="orders.length === 0" description="暂无订单" />
    </div>

    <van-popup v-model:show="showDetailPopup" position="bottom" round :style="{ maxHeight: '70%' }" closeable>
      <div class="detail-popup" v-if="detailOrder">
        <div class="dp-head">
          <span class="dp-id">订单 #{{ detailOrder.id }}</span>
          <span :class="['moc-status', statusClass(detailOrder.status)]">{{ statusText(detailOrder.status) }}</span>
        </div>
        <van-cell-group inset>
          <van-cell title="用户" :value="detailOrder.user_name" />
          <van-cell title="电话" :value="detailOrder.user_phone" />
          <van-cell title="地址" :value="detailOrder.address" />
          <van-cell title="时间" :value="detailOrder.create_time" />
          <van-cell title="备注" :value="detailOrder.remark || '无'" />
        </van-cell-group>
        <div class="dp-items-title">商品清单</div>
        <div class="dp-items">
          <div v-for="item in detailOrder.items" :key="item.name" class="dp-item">
            <span>{{ item.name }}</span>
            <span>×{{ item.qty }}</span>
            <span>¥{{ (item.price * item.qty).toFixed(2) }}</span>
          </div>
        </div>
        <div class="dp-total">
          <span>合计</span>
          <span>¥{{ detailOrder.total_amount }}</span>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { showToast, showSuccessToast, showFailToast, showDialog } from 'vant'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/index'

const activeTab = ref('1')
const orders = ref([])
const counts = ref({ 1:0, 2:0, 3:0, 4:0 })
const newOrderAlert = ref(false)
const newOrderId = ref('')
const showDetailPopup = ref(false)
const detailOrder = ref(null)

const statusText = s => ({ 1:'待接单',2:'已接单',3:'配送中',4:'已完成','-1':'已取消' }[s])
const statusClass = s => ({ 1:'ms-pending',2:'ms-accepted',3:'ms-delivering',4:'ms-done','-1':'ms-cancel' }[s])

async function loadOrders() {
  try { const r = await axios.get('/api/merchant/orders', { params: { status: parseInt(activeTab.value) } }); if (r.data.code === 200) orders.value = r.data.data } catch (e) {}
}
async function loadCounts() {
  try { for (const s of [1,2,3,4]) { const r = await axios.get('/api/merchant/orders', { params: { status: s } }); if (r.data.code === 200) counts.value[s] = r.data.data.length } } catch (e) {}
}
async function acceptOrder(id) {
  try { const r = await axios.post(`/api/merchant/orders/${id}/accept`); if (r.data.code === 200) { showSuccessToast('接单成功'); loadOrders(); loadCounts() } else showFailToast(r.data.msg) } catch (e) { showFailToast('操作失败') }
}
async function rejectOrder(id) {
  try { const r = await axios.post(`/api/merchant/orders/${id}/reject`); if (r.data.code === 200) { showToast('已拒单'); loadOrders(); loadCounts() } } catch (e) { showFailToast('操作失败') }
}
async function completeOrder(id) {
  try { const r = await axios.post(`/api/merchant/orders/${id}/complete`); if (r.data.code === 200) { showSuccessToast('已完成'); loadOrders(); loadCounts() } } catch (e) { showFailToast('操作失败') }
}
function showDetail(o) { detailOrder.value = o; showDetailPopup.value = true }

const router = useRouter()
const store = useAppStore()
function handleLogout() {
  showDialog({ title:'退出商家账号', message:'确定退出吗？', showCancelButton:true, confirmButtonText:'退出', confirmButtonColor:'#C84B31' }).then(() => {
    store.logout(); showSuccessToast('已退出 🏪'); setTimeout(() => router.push('/login'), 1500)
  }).catch(() => {})
}
function onNewOrder(data) { newOrderAlert.value = true; newOrderId.value = data.id || ''; loadOrders(); loadCounts(); setTimeout(() => newOrderAlert.value = false, 8000) }
watch(activeTab, () => loadOrders())
onMounted(() => { loadOrders(); loadCounts(); const s = window._socketInstance; if (s) s.on('new_order', onNewOrder) })
onUnmounted(() => { const s = window._socketInstance; if (s) s.off('new_order', onNewOrder) })
</script>

<style scoped>
.merchant-order-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 20px; }

.mo-navbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--clay-card); border-bottom: 1px solid var(--clay-border); }
.mon-title { font-size: 17px; font-weight: 700; color: var(--clay-text); }
.mon-actions { display: flex; gap: 6px; }
.mon-btn { width: 36px; height: 36px; border-radius: 50%; border: none; background: var(--clay-page); font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

.mo-list { padding: 10px 14px; display: flex; flex-direction: column; gap: 10px; }
.mo-card { background: var(--clay-card); border-radius: 16px; padding: 16px; border: 1px solid var(--clay-border); }
.moc-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.moc-id { font-weight: 600; color: var(--clay-text); }
.moc-status { font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 12px; }
.ms-pending { background: var(--clay-brand-light); color: var(--clay-brand); }
.ms-accepted { background: var(--clay-success-bg); color: var(--clay-success); }
.ms-delivering { background: var(--clay-info-bg); color: var(--clay-info); }
.ms-done { background: #F5F2ED; color: var(--clay-text-soft); }
.ms-cancel { background: var(--clay-danger-bg); color: var(--clay-danger); }
.moc-user { font-size: 14px; color: var(--clay-text-body); margin-bottom: 6px; }
.moc-items { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.moc-item-tag { background: var(--clay-page); padding: 2px 10px; border-radius: 6px; font-size: 12px; color: var(--clay-text-soft); }
.moc-addr, .moc-remark { font-size: 13px; color: var(--clay-text-soft); margin-bottom: 4px; }
.moc-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--clay-divider); }
.moc-time { font-size: 12px; color: var(--clay-text-muted); }
.moc-total { font-size: 18px; font-weight: 700; color: var(--clay-brand); font-family: Georgia, serif; }
.moc-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--clay-divider); }
.moa-reject { padding: 8px 18px; border-radius: 20px; border: 1px solid var(--clay-danger); background: transparent; color: var(--clay-danger); font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
.moa-accept { padding: 8px 18px; border-radius: 20px; border: none; background: var(--clay-brand); color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
.moa-accept:active { background: var(--clay-brand-deep); }
.moa-reject:active { background: var(--clay-danger-bg); }

.detail-popup { padding: 20px 0 30px; }
.dp-head { display: flex; justify-content: space-between; align-items: center; padding: 0 16px 16px; }
.dp-id { font-size: 18px; font-weight: 700; color: var(--clay-text); }
.dp-items-title { font-size: 14px; font-weight: 700; padding: 16px 16px 8px; }
.dp-items { padding: 0 16px; }
.dp-item { display: flex; align-items: center; gap: 8px; padding: 10px 0; border-bottom: 1px solid var(--clay-divider); font-size: 14px; }
.dp-item span:first-child { flex: 1; }
.dp-item span:nth-child(2) { color: var(--clay-text-soft); }
.dp-item span:last-child { font-weight: 600; color: var(--clay-brand); }
.dp-total { display: flex; justify-content: space-between; padding: 16px; margin: 12px 16px 0; background: var(--clay-brand-light); border-radius: 14px; font-size: 15px; font-weight: 600; }
.dp-total span:last-child { font-size: 20px; font-weight: 700; color: var(--clay-brand); font-family: Georgia, serif; }
</style>
