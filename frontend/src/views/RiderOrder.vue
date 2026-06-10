<template>
  <div class="rider-page">
    <div class="rider-navbar">
      <div class="rn-title">工作台</div>
      <div class="rn-actions">
        <button class="rn-btn" @click="refreshAll">↻</button>
        <button class="rn-btn" @click="$router.push('/rider-profile')">👤</button>
        <button class="rn-btn" @click="handleLogout">↩</button>
      </div>
    </div>

    <div class="rider-status-bar">
      <div :class="['rs-indicator', rider.status === 0 ? 'idle' : 'busy']">
        <span class="rs-dot"></span>
        {{ rider.status === 0 ? '空闲中 · 可接单' : '配送中' }}
      </div>
    </div>

    <div v-if="myOrder" class="current-order">
      <div class="co-label">当前配送</div>
      <div class="co-card">
        <div class="co-step">
          <span class="cos-icon">🏪</span>
          <div><b>取餐</b><br/>{{ myOrder.merchant?.name }} · {{ myOrder.merchant?.address }}</div>
        </div>
        <div class="co-step">
          <span class="cos-icon">📍</span>
          <div><b>送达</b><br/>{{ myOrder.user?.address }}</div>
        </div>
        <div class="co-items">
          <span v-for="item in myOrder.items" :key="item.name" class="coi-tag">{{ item.name }}×{{ item.qty }}</span>
        </div>
        <div class="co-actions">
          <button class="coa-loc" @click="reportLocation">📍 上报位置</button>
          <button class="coa-done" @click="completeDelivery">完成配送</button>
        </div>
      </div>
    </div>

    <div class="available-section">
      <div class="co-label">可抢订单 ({{ availableOrders.length }})</div>
      <article v-for="o in availableOrders" :key="o.id" class="ao-card">
        <div class="aoc-head">
          <span class="aoc-name">{{ o.merchant_name }}</span>
          <span class="aoc-dist">{{ o.distance_to_merchant }}km</span>
        </div>
        <div class="aoc-route">
          <div>🏪 {{ o.merchant_address }}</div>
          <div>📦 {{ o.user_address }}</div>
        </div>
        <div class="co-items" style="margin:6px 0">
          <span v-for="item in o.items" :key="item.name" class="coi-tag">{{ item.name }}×{{ item.qty }}</span>
        </div>
        <div class="aoc-foot">
          <span class="aoc-amount">¥{{ o.total_amount }}</span>
          <button class="aoc-grab" @click="grabOrder(o.id)">抢单</button>
        </div>
      </article>
      <van-empty v-if="availableOrders.length === 0" description="暂无可抢订单" />
    </div>

    <div class="sim-badge" v-if="locationTimer">
      <span>⏱ 位置模拟中 (每3秒)</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { showToast, showSuccessToast, showFailToast, showDialog } from 'vant'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/index'

const rider = reactive({ status: 0, lng: 0, lat: 0 })
const availableOrders = ref([])
const myOrder = ref(null)
let locationTimer = null
let simLng = 0, simLat = 0, simInitialized = false

function initRiderLocation() {
  if (simInitialized) return
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(p => { simLng = p.coords.longitude; simLat = p.coords.latitude; rider.lng = simLng; rider.lat = simLat; simInitialized = true },
      () => { simLng = 104.0657; simLat = 30.6598; rider.lng = simLng; rider.lat = simLat; simInitialized = true }, { timeout: 5000, enableHighAccuracy: false })
  } else { simLng = 104.0657; simLat = 30.6598; simInitialized = true }
}
async function loadAvailableOrders() { try { const r = await axios.get('/api/rider/available-orders'); if (r.data.code === 200) availableOrders.value = r.data.data } catch (e) {} }
async function loadMyOrder() { try { const r = await axios.get('/api/rider/my-order'); if (r.data.code === 200) myOrder.value = r.data.data } catch (e) {} }
async function grabOrder(id) {
  try { const r = await axios.post(`/api/rider/orders/${id}/grab`); if (r.data.code === 200) { showSuccessToast('抢单成功！'); startLocationSimulation(); loadAvailableOrders(); loadMyOrder() } else showFailToast(r.data.msg) } catch (e) { showFailToast('抢单失败') }
}
async function completeDelivery() {
  if (!myOrder.value) return
  try { const r = await axios.post(`/api/rider/orders/${myOrder.value.id}/complete`); if (r.data.code === 200) { showSuccessToast('配送完成！'); stopLocationSimulation(); myOrder.value = null; rider.status = 0; loadAvailableOrders() } } catch (e) { showFailToast('操作失败') }
}
async function reportLocation() { simLng += (Math.random()-0.5)*0.002; simLat += (Math.random()-0.5)*0.002; try { await axios.post('/api/rider/location', { lng: simLng, lat: simLat }); rider.lng = simLng; rider.lat = simLat; showToast('已上报') } catch (e) {} }
function startLocationSimulation() { rider.status = 1; locationTimer = setInterval(() => reportLocation(), 3000) }
function stopLocationSimulation() { if (locationTimer) { clearInterval(locationTimer); locationTimer = null }; rider.status = 0 }
function refreshAll() { loadAvailableOrders(); loadMyOrder() }

const router = useRouter(); const store = useAppStore()
function handleLogout() {
  showDialog({ title:'退出骑手账号', message:'确定退出吗？', showCancelButton:true, confirmButtonText:'退出', confirmButtonColor:'#C84B31' }).then(() => {
    stopLocationSimulation(); store.logout(); showSuccessToast('已退出 🛵'); setTimeout(() => router.push('/login'), 1500)
  }).catch(() => {})
}
onMounted(() => { initRiderLocation(); loadAvailableOrders(); loadMyOrder() })
onUnmounted(() => stopLocationSimulation())
</script>

<style scoped>
.rider-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 70px; }

.rider-navbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: var(--clay-card); border-bottom: 1px solid var(--clay-border); }
.rn-title { font-size: 17px; font-weight: 700; color: var(--clay-text); }
.rn-actions { display: flex; gap: 6px; }
.rn-btn { width: 36px; height: 36px; border-radius: 50%; border: none; background: var(--clay-page); font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

.rider-status-bar { padding: 12px 16px; background: var(--clay-card); margin-bottom: 4px; border-bottom: 1px solid var(--clay-border); }
.rs-indicator { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; }
.rs-dot { width: 10px; height: 10px; border-radius: 50%; }
.idle .rs-dot { background: var(--clay-success); box-shadow: 0 0 0 4px rgba(107,142,107,0.2); }
.idle { color: var(--clay-success); }
.busy .rs-dot { background: var(--clay-brand); box-shadow: 0 0 0 4px rgba(200,75,49,0.2); }
.busy { color: var(--clay-brand); }

.co-label { font-size: 14px; font-weight: 700; color: var(--clay-text); padding: 14px 16px 8px; }
.co-card { margin: 0 14px; background: var(--clay-accent-light); border-radius: 16px; padding: 16px; border: 1px solid #F0E4CC; }
.co-step { display: flex; gap: 10px; margin-bottom: 10px; font-size: 14px; color: var(--clay-text); }
.co-step b { color: var(--clay-brand); }
.cos-icon { font-size: 20px; flex-shrink: 0; }
.co-items { display: flex; flex-wrap: wrap; gap: 6px; }
.coi-tag { background: #fff; padding: 2px 10px; border-radius: 6px; font-size: 12px; color: var(--clay-text-soft); border: 1px solid var(--clay-border); }
.co-actions { display: flex; gap: 10px; margin-top: 12px; }
.coa-loc { flex: 1; padding: 10px; border-radius: 14px; border: 1px solid var(--clay-brand); background: transparent; color: var(--clay-brand); font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
.coa-done { flex: 1; padding: 10px; border-radius: 14px; border: none; background: var(--clay-success); color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }
.coa-done:active { opacity: 0.85; }

.available-section { padding: 0 14px; }
.ao-card { background: var(--clay-card); border-radius: 16px; padding: 16px; margin-bottom: 10px; border: 1px solid var(--clay-border); }
.aoc-head { display: flex; justify-content: space-between; margin-bottom: 8px; }
.aoc-name { font-weight: 600; color: var(--clay-text); }
.aoc-dist { font-weight: 700; color: var(--clay-brand); font-size: 13px; }
.aoc-route { font-size: 13px; color: var(--clay-text-soft); }
.aoc-route div { padding: 2px 0; }
.aoc-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--clay-divider); }
.aoc-amount { font-size: 20px; font-weight: 700; color: var(--clay-brand); font-family: Georgia, serif; }
.aoc-grab { padding: 10px 28px; border-radius: 22px; border: none; background: var(--clay-brand); color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; font-family: inherit; }
.aoc-grab:active { background: var(--clay-brand-deep); transform: scale(0.95); }

.sim-badge { text-align: center; padding: 16px; font-size: 13px; color: var(--clay-text-soft); }
</style>
