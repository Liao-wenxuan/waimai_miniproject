<template>
  <div class="order-detail-page">
    <!-- 状态头部 — 有机形态 -->
    <div class="od-header" v-if="order.status !== undefined">
      <div class="od-blob-bg"></div>
      <div class="od-header-content">
        <div class="od-status-icon">
          <span class="od-emoji">{{ statusEmoji(order.status) }}</span>
        </div>
        <div class="od-status-text">{{ statusText(order.status) }}</div>
        <div class="od-status-sub">{{ statusSubText(order.status) }}</div>
      </div>
    </div>

    <!-- 骑手卡片 -->
    <div v-if="order.rider" class="section rider-card">
      <div class="rider-avatar">🛵</div>
      <div class="rider-body">
        <div class="rider-name">{{ order.rider.name }}</div>
        <div class="rider-phone">{{ order.rider.phone }}</div>
      </div>
      <button class="rider-call">📞</button>
    </div>

    <!-- 地图 -->
    <div class="map-wrap" v-if="showMap">
      <div id="order-map" ref="mapRef" style="width:100%;height:240px"></div>
    </div>

    <!-- 地址 -->
    <div class="section">
      <div class="sec-title">
        <span class="sec-icon">📍</span> 收货地址
      </div>
      <div class="sec-body">{{ order.address || '暂无' }}</div>
    </div>

    <!-- 商家 -->
    <div class="section" v-if="order.merchant">
      <div class="sec-title">
        <span class="sec-icon">🏪</span> {{ order.merchant.name }}
      </div>
      <div class="sec-body">{{ order.merchant.address }}</div>
    </div>

    <!-- 商品 -->
    <div class="section">
      <div class="sec-title">订单详情</div>
      <div class="item-row" v-for="item in order.items" :key="item.id">
        <span class="ir-name">{{ item.product_name }}</span>
        <span class="ir-qty">×{{ item.quantity }}</span>
        <span class="ir-price">¥{{ (item.price * item.quantity).toFixed(1) }}</span>
      </div>
    </div>

    <!-- 金额 -->
    <div class="section">
      <div class="total-row">
        <span>订单金额</span>
        <span class="total-amount">¥{{ order.total_amount }}</span>
      </div>
      <div class="remark-row" v-if="order.remark">
        <span class="remark-tag">备注</span>
        <span>{{ order.remark }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="order.status === 0 || order.status === 1" class="section action-section">
      <button class="cancel-btn" :disabled="cancelling" @click="handleCancelOrder">
        {{ cancelling ? '取消中…' : '取消订单' }}
      </button>
      <p class="cancel-hint">
        {{ order.status === 0 ? '取消后订单将无法恢复' : '商家已开始准备，确定取消吗？' }}
      </p>
    </div>

    <!-- 时间线 -->
    <div class="section timeline">
      <div class="tl-title">订单信息</div>
      <div class="tl-item" v-if="order.id">
        <span class="tl-label">编号</span>
        <span class="tl-value">#{{ order.id }}</span>
      </div>
      <div class="tl-item" v-if="order.create_time">
        <span class="tl-label">创建</span>
        <span class="tl-value">{{ order.create_time }}</span>
      </div>
      <div class="tl-item" v-if="order.pay_time">
        <span class="tl-label">支付</span>
        <span class="tl-value">{{ order.pay_time }}</span>
      </div>
      <div class="tl-item" v-if="order.accept_time">
        <span class="tl-label">接单</span>
        <span class="tl-value">{{ order.accept_time }}</span>
      </div>
      <div class="tl-item" v-if="order.finish_time">
        <span class="tl-label">完成</span>
        <span class="tl-value">{{ order.finish_time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { showToast, showSuccessToast, showFailToast, showConfirmDialog, showLoadingToast, closeToast } from 'vant'

const route = useRoute()
const router = useRouter()
const order = ref({})
const mapRef = ref(null)
let mapInstance = null, riderMarker = null

const showMap = computed(() => order.value.status === 3 && order.value.rider)

const statusEmoji = s => ({ '0':'⏳','1':'📋','2':'👨‍🍳','3':'🛵','4':'✅','-1':'✕' }[s] || '⏳')
const statusText = s => ({ '0':'待支付','1':'等待商家接单','2':'商家已接单，备餐中','3':'骑手正在赶来','4':'订单已完成','-1':'订单已取消' }[s] || '未知')
const statusSubText = s => ({ '0':'请尽快完成支付','1':'商家即将接单','2':'请耐心等待','3':'请保持电话畅通','4':'感谢您的惠顾','-1':'' }[s] || '')

function initMap() {
  if (!window.AMap || !showMap.value) return
  nextTick(() => {
    const el = document.getElementById('order-map'); if (!el) return
    mapInstance = new AMap.Map('order-map', { zoom: 14, center: [114.33, 30.50] })
    const markers = []
    if (order.value.merchant) {
      const m = order.value.merchant
      new AMap.Marker({ position: [m.lng, m.lat], title: m.name, icon: new AMap.Icon({ size: new AMap.Size(32,32), image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png', imageSize: new AMap.Size(32,32) }) }).setMap(mapInstance)
      markers.push({ lng: m.lng, lat: m.lat })
    }
    if (order.value.address_lng) {
      new AMap.Marker({ position: [order.value.address_lng, order.value.address_lat], title: '收货地址', icon: new AMap.Icon({ size: new AMap.Size(32,32), image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png', imageSize: new AMap.Size(32,32) }) }).setMap(mapInstance)
      markers.push({ lng: order.value.address_lng, lat: order.value.address_lat })
    }
    if (order.value.rider) {
      riderMarker = new AMap.Marker({ position: [order.value.rider.lng, order.value.rider.lat], title: order.value.rider.name, icon: new AMap.Icon({ size: new AMap.Size(36,36), image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_bs.png', imageSize: new AMap.Size(36,36) }) })
      riderMarker.setMap(mapInstance)
      markers.push({ lng: order.value.rider.lng, lat: order.value.rider.lat })
    }
    if (markers.length > 0) mapInstance.setFitView(markers)
    if (markers.length >= 2 && window.AMap.Driving) {
      new AMap.Driving({ map: mapInstance, panel: null }).search(new AMap.LngLat(markers[0].lng, markers[0].lat), new AMap.LngLat(markers[markers.length-1].lng, markers[markers.length-1].lat))
    }
  })
}

function updateRiderPosition(data) {
  if (!riderMarker || !mapInstance) return
  riderMarker.setPosition([data.lng, data.lat])
}
function onRiderLocation(e) { if (e.detail.order_id === order.value.id) updateRiderPosition(e.detail) }

const cancelling = ref(false)

async function handleCancelOrder() {
  try {
    await showConfirmDialog({
      title: '取消订单',
      message: order.value.status === 0
        ? '订单尚未支付，取消后无法恢复。确定要取消吗？'
        : '商家可能已开始备餐，确定要取消订单吗？',
      confirmButtonText: '确定取消',
      cancelButtonText: '再想想',
      confirmButtonColor: '#C0392B',
    })
  } catch (e) {
    return // 用户点了取消
  }

  cancelling.value = true
  showLoadingToast({ message: '取消中…', forbidClick: true })
  try {
    const res = await axios.post(`/api/orders/${route.params.id}/cancel`)
    if (res.data.code === 200) {
      closeToast()
      showSuccessToast('订单已取消')
      order.value.status = -1
    } else {
      closeToast()
      showFailToast(res.data.msg || '取消失败')
    }
  } catch (e) {
    closeToast()
    showFailToast('网络错误，请检查后端')
  } finally {
    cancelling.value = false
  }
}

async function loadOrder() {
  try {
    const res = await axios.get(`/api/orders/${route.params.id}`)
    if (res.data.code === 200) { order.value = res.data.data; nextTick(() => initMap()) }
  } catch (e) {
    order.value = {}
  }
}

onMounted(() => { loadOrder(); window.addEventListener('rider_location_changed', onRiderLocation) })
onUnmounted(() => { window.removeEventListener('rider_location_changed', onRiderLocation); if (mapInstance) { mapInstance.destroy(); mapInstance = null } })
</script>

<style scoped>
.order-detail-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 30px; }

/* 状态头部 — 有机 blob */
.od-header {
  position: relative; padding: 40px 20px 48px; text-align: center; color: #fff; overflow: hidden;
}
.od-blob-bg {
  position: absolute; inset: 0;
  background: linear-gradient(160deg, #C84B31 0%, #8B3A2A 70%, #5C2618 100%);
  border-radius: 0 0 55% 45% / 0 0 35% 30%;
}
.od-header-content { position: relative; z-index: 1; }
.od-emoji { font-size: 40px; }
.od-status-text { font-size: 22px; font-weight: 700; margin-top: 8px; letter-spacing: 0.03em; }
.od-status-sub { font-size: 13px; opacity: 0.8; margin-top: 4px; }

/* 通用 section */
.section { background: var(--clay-card); margin: 10px 14px; border-radius: 16px; padding: 16px; border: 1px solid var(--clay-border); }
.sec-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; color: var(--clay-text); margin-bottom: 8px; }
.sec-icon { font-size: 18px; }
.sec-body { font-size: 14px; color: var(--clay-text-soft); padding-left: 28px; }

/* 骑手卡片 */
.rider-card { display: flex; align-items: center; gap: 12px; background: var(--clay-accent-light); border-color: #F0E4CC; }
.rider-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--clay-accent); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.rider-body { flex: 1; }
.rider-name { font-size: 15px; font-weight: 600; color: var(--clay-text); }
.rider-phone { font-size: 13px; color: var(--clay-text-soft); }
.rider-call { width: 40px; height: 40px; border-radius: 50%; border: 1px solid var(--clay-brand); background: var(--clay-brand-light); font-size: 18px; cursor: pointer; transition: all 0.2s var(--spring); }
.rider-call:active { transform: scale(0.9); }

/* 地图 */
.map-wrap { margin: 0 14px; border-radius: 16px; overflow: hidden; border: 1px solid var(--clay-border); }

/* 商品 */
.item-row { display: flex; align-items: center; padding: 8px 0; font-size: 14px; }
.item-row + .item-row { border-top: 1px solid var(--clay-divider); }
.ir-name { flex: 1; color: var(--clay-text); }
.ir-qty { color: var(--clay-text-soft); margin: 0 14px; }
.ir-price { color: var(--clay-brand); font-weight: 600; }

/* 金额 */
.total-row { display: flex; justify-content: space-between; font-size: 15px; font-weight: 600; }
.total-amount { color: var(--clay-brand); font-size: 22px; font-weight: 700; font-family: Georgia, serif; }
.remark-row { display: flex; gap: 8px; margin-top: 8px; font-size: 13px; color: var(--clay-text-soft); }
.remark-tag { background: var(--clay-brand-light); color: var(--clay-brand); padding: 1px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; }

/* 操作按钮 */
.action-section { text-align: center; padding: 20px 16px; }
.cancel-btn {
  width: 100%; padding: 14px;
  border: 2px solid var(--clay-danger);
  border-radius: 16px;
  background: #fff;
  color: var(--clay-danger);
  font-size: 16px; font-weight: 700;
  cursor: pointer; font-family: inherit;
  transition: all 0.25s var(--spring);
  letter-spacing: 0.04em;
}
.cancel-btn:active { transform: scale(0.97); background: var(--clay-danger-bg); }
.cancel-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.cancel-hint {
  margin-top: 8px; font-size: 12px; color: var(--clay-text-muted);
}

/* 时间线 */
.timeline { color: var(--clay-text-soft); }
.tl-title { font-size: 15px; font-weight: 600; color: var(--clay-text); margin-bottom: 10px; }
.tl-item { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; }
.tl-label { font-weight: 500; }
.tl-value { color: var(--clay-text-body); }
</style>
