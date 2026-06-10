<template>
  <div class="nearby-map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <!-- 中心十字准星 -->
    <div class="crosshair" :class="{ active: isDragging }">
      <div class="ch-pin">
        <div class="ch-head"></div>
        <div class="ch-body"></div>
        <div class="ch-shadow"></div>
      </div>
    </div>

    <!-- 当前地点标签 -->
    <div class="loc-label" v-if="currentLabel && !loading" @click="locateMe">
      <span class="loc-dot"></span>
      <span class="loc-text">{{ currentLabel }}</span>
    </div>

    <!-- 选取确认 -->
    <div class="pick-bar" v-if="isDragging && pickedCoords">
      <div class="pick-hint">
        <span>📍</span> 拖拽地图选取位置
      </div>
      <button class="pick-btn" @click="confirmPickLocation">在此查找</button>
    </div>

    <!-- 控制按钮 -->
    <div class="map-ctrls">
      <button class="mctrl-btn" @click="locateMe">
        <span :style="{ color: isLocated ? 'var(--clay-success)' : 'var(--clay-brand)' }">◎</span>
      </button>
      <button class="mctrl-btn" @click="toggleLayer">
        <span>◉</span>
      </button>
    </div>

    <!-- 缩放 -->
    <div class="zoom-ctrls">
      <button class="zoom-btn" @click="zoomIn">+</button>
      <div class="zoom-div"></div>
      <button class="zoom-btn" @click="zoomOut">−</button>
    </div>

    <div class="zoom-badge" v-if="currentZoom">{{ currentZoom }}级</div>

    <div class="map-loading" v-if="loading">
      <van-loading type="spinner" size="24" color="var(--clay-brand)" />
      <span>地图加载中…</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { showToast, showSuccessToast } from 'vant'

const props = defineProps({
  merchants: { type: Array, default: () => [] },
  userLng: { type: Number, default: 0 },
  userLat: { type: Number, default: 0 },
  addressLabel: { type: String, default: '' }
})
const emit = defineEmits(['merchant-click', 'locate', 'center-changed'])

const mapContainer = ref(null)
const loading = ref(true)
const currentLabel = ref('')
const currentZoom = ref(0)
const isLocated = ref(false)
const isDragging = ref(false)
const pickedCoords = ref(null)

let map = null, userMarker = null, merchantMarkers = [], userCircle = null, layerNormal = true, moveTimer = null
let resizeObserver = null, amapCheckTimer = null, initAttempted = false

function containerReady() {
  if (!mapContainer.value) return false
  const rect = mapContainer.value.getBoundingClientRect()
  return rect.width > 0 && rect.height > 0
}

function initMap() {
  if (initAttempted) return
  if (!window.AMap) return
  if (!containerReady()) {
    // 容器还没有尺寸，稍后重试
    setTimeout(() => initMap(), 300)
    return
  }
  initAttempted = true
  if (amapCheckTimer) { clearInterval(amapCheckTimer); amapCheckTimer = null }

  try {
    map = new AMap.Map(mapContainer.value, {
      zoom: 16,
      center: [props.userLng || 103.00, props.userLat || 29.98],
      features: ['bg', 'road', 'building', 'point'],
      showLabel: true,
      touchZoom: true,
      dragEnable: true,
      zoomEnable: true,
      animateEnable: true,
    })
  } catch (e) {
    console.error('Map init error:', e)
    loading.value = false
    return
  }

  loading.value = false
  currentZoom.value = map.getZoom()

  map.on('zoomchange', () => { currentZoom.value = map.getZoom() })
  map.on('movestart', () => { isDragging.value = true })
  map.on('moveend', () => {
    const c = map.getCenter()
    if (c) pickedCoords.value = { lng: c.lng, lat: c.lat }
    clearTimeout(moveTimer)
  })
  map.on('click', (e) => {
    isDragging.value = true
    if (e.lnglat) {
      const { lng, lat } = e.lnglat
      map.setCenter([lng, lat])
      pickedCoords.value = { lng, lat }
    }
  })

  addUserMarker()
  addMerchantMarkers()
  fitView()
}

function confirmPickLocation() {
  if (!pickedCoords.value) return
  emit('center-changed', pickedCoords.value)
  isDragging.value = false
  showSuccessToast('已更新位置')
}

function addUserMarker() {
  if (!map) return
  if (userMarker) { userMarker.setMap(null); userMarker = null }
  if (userCircle) { userCircle.setMap(null); userCircle = null }
  if (!props.userLng || !props.userLat) return
  const pos = [props.userLng, props.userLat]
  try {
    userCircle = new AMap.Circle({
      center: pos, radius: 100,
      strokeColor: 'rgba(200,75,49,0.3)', strokeWeight: 2, strokeStyle: 'dashed',
      fillColor: 'rgba(200,75,49,0.06)', zIndex: 99
    })
    userCircle.setMap(map)
    userMarker = new AMap.Marker({
      position: pos,
      icon: new AMap.Icon({
        size: new AMap.Size(28, 42),
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
        imageSize: new AMap.Size(28, 42)
      }),
      zIndex: 102, title: '我的位置',
      offset: new AMap.Pixel(-14, -21)
    })
    userMarker.setMap(map)
    isLocated.value = true
  } catch (e) {
    console.error('Add user marker error:', e)
  }
}

function addMerchantMarkers() {
  if (!map || !window.AMap) return
  merchantMarkers.forEach(m => { try { m.setMap(null) } catch (e) {} })
  merchantMarkers = []
  if (!props.merchants?.length) return
  props.merchants.forEach(merchant => {
    if (!merchant.lng || !merchant.lat) return
    try {
      const content = document.createElement('div')
      content.className = 'merchant-marker'
      content.innerHTML = `<div class="mm-pin"><div class="mm-emoji">${getCategoryEmoji(merchant.name)}</div></div><div class="mm-card"><div class="mm-name">${merchant.name}</div><div class="mm-info">⭐${merchant.rating} · ¥${merchant.delivery_fee}配送</div></div>`
      const marker = new AMap.Marker({
        position: [merchant.lng, merchant.lat],
        content,
        offset: new AMap.Pixel(-55, -65),
        zIndex: 50,
        extData: { id: merchant.id, name: merchant.name }
      })
      marker.on('click', () => emit('merchant-click', merchant))
      marker.setMap(map)
      merchantMarkers.push(marker)
    } catch (e) {}
  })
}

function getCategoryEmoji(name) {
  if (!name) return '🏪'
  if (name.includes('冰城') || name.includes('奶茶')) return '🍦'
  if (name.includes('烧仙草')) return '🧋'
  if (name.includes('华莱士') || name.includes('汉堡')) return '🍔'
  if (name.includes('鸡排')) return '🍗'
  if (name.includes('麦当劳')) return '🍟'
  if (name.includes('火锅') || name.includes('海底捞')) return '🍲'
  if (name.includes('咖啡') || name.includes('星巴克')) return '☕'
  if (name.includes('酸奶牛')) return '🥛'
  if (name.includes('茶百道')) return '🍵'
  return '🏪'
}

function fitView() {
  if (!map) return
  try {
    const pts = []
    if (props.userLng && props.userLat) pts.push([props.userLng, props.userLat])
    if (props.merchants) props.merchants.forEach(m => { if (m.lng && m.lat) pts.push([m.lng, m.lat]) })
    if (pts.length > 1) map.setFitView(pts, false, [60, 60, 60, 60])
    else if (pts.length === 1) map.setZoomAndCenter(16, pts[0])
  } catch (e) {}
}

function resizeMap() {
  if (!map) return
  nextTick(() => {
    try { map.resize() } catch (e) {}
  })
}

function locateMe() {
  emit('locate')
  if (map && props.userLng && props.userLat) {
    map.setZoomAndCenter(16, [props.userLng, props.userLat])
    isLocated.value = true
  }
}

function toggleLayer() {
  if (!map) return
  layerNormal = !layerNormal
  map.setFeatures(layerNormal ? ['bg', 'road', 'building', 'point'] : ['bg', 'road', 'point'])
  showToast(layerNormal ? '标准地图' : '卫星地图')
}

function zoomIn() { if (map) map.setZoom(Math.min(map.getZoom() + 1, 19)) }
function zoomOut() { if (map) map.setZoom(Math.max(map.getZoom() - 1, 3)) }

watch(() => props.merchants, () => {
  if (map) nextTick(() => { addMerchantMarkers(); fitView() })
}, { deep: true })

watch(() => [props.userLng, props.userLat], () => {
  if (map) nextTick(() => addUserMarker())
})

watch(() => props.addressLabel, (v) => {
  if (v && !v.includes('定位中') && !v.includes('(')) currentLabel.value = v
})

// 暴露 resizeMap 给父组件
defineExpose({ resizeMap })

onMounted(() => {
  // ResizeObserver 检测容器何时获得尺寸（从隐藏变可见）
  if (mapContainer.value) {
    resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          if (!initAttempted) {
            initMap()
          } else if (map) {
            // 已有 map 实例但容器尺寸变了，resize
            try { map.resize() } catch (e) {}
          }
        }
      }
    })
    resizeObserver.observe(mapContainer.value)
  }

  // 轮询等待 AMap 加载
  let checkCount = 0
  amapCheckTimer = setInterval(() => {
    checkCount++
    if (window.AMap && containerReady()) {
      initMap()
      return
    }
    // 超时 20 秒后停止
    if (checkCount > 100) {
      clearInterval(amapCheckTimer)
      amapCheckTimer = null
      loading.value = false
      console.error('[Map] AMap script failed to load')
    }
  }, 200)
})

onUnmounted(() => {
  if (amapCheckTimer) { clearInterval(amapCheckTimer); amapCheckTimer = null }
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (map) {
    try { map.destroy() } catch (e) {}
    map = null
  }
  initAttempted = false
})
</script>

<style scoped>
.nearby-map-wrapper { position: relative; width: 100%; height: 380px; border-radius: 0 0 18px 18px; overflow: hidden; background: #EBE3D6; }
.map-container { width: 100%; height: 100%; }
.map-loading { position: absolute; inset: 0; background: rgba(253,248,240,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; font-size: 13px; color: var(--clay-text-soft); z-index: 30; }

.crosshair { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -100%); pointer-events: none; z-index: 15; opacity: 0; transition: opacity 0.2s; }
.crosshair.active { opacity: 1; }
.ch-pin { display: flex; flex-direction: column; align-items: center; }
.ch-head { width: 18px; height: 18px; border-radius: 50%; background: var(--clay-brand); border: 3px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.ch-body { width: 3px; height: 16px; background: var(--clay-brand); margin-top: -1px; }
.ch-shadow { width: 6px; height: 3px; border-radius: 50%; background: rgba(0,0,0,0.15); margin-top: 2px; }

.loc-label { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); padding: 5px 14px; border-radius: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); z-index: 25; max-width: 85%; cursor: pointer; }
.loc-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--clay-success); box-shadow: 0 0 0 3px rgba(107,142,107,0.25); flex-shrink: 0; }
.loc-text { font-size: 12px; font-weight: 600; color: var(--clay-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.pick-bar { position: absolute; bottom: 14px; left: 14px; right: 14px; background: #fff; border-radius: 22px; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 20px rgba(0,0,0,0.1); z-index: 25; animation: slideUp 0.25s ease; }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.pick-hint { font-size: 12px; color: var(--clay-text-soft); display: flex; align-items: center; gap: 4px; }
.pick-btn { padding: 8px 18px; border-radius: 20px; border: none; background: var(--clay-brand); color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }

.map-ctrls { position: absolute; right: 10px; bottom: 76px; display: flex; flex-direction: column; gap: 8px; z-index: 20; }
.mctrl-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: transform 0.15s; }
.mctrl-btn:active { transform: scale(0.9); }

.zoom-ctrls { position: absolute; right: 10px; top: 10px; background: #fff; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); overflow: hidden; z-index: 20; }
.zoom-btn { width: 40px; height: 38px; border: none; background: transparent; font-size: 18px; font-weight: 600; color: var(--clay-text); cursor: pointer; display: flex; align-items: center; justify-content: center; font-family: inherit; }
.zoom-btn:active { background: var(--clay-page); }
.zoom-div { height: 1px; background: var(--clay-divider); margin: 0 6px; }
.zoom-badge { position: absolute; left: 10px; bottom: 80px; background: rgba(44,36,22,0.5); color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 10px; z-index: 20; pointer-events: none; }

:deep(.merchant-marker) { display: flex; flex-direction: column; align-items: center; cursor: pointer; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.12)); transition: transform 0.15s; }
:deep(.merchant-marker:active) { transform: scale(1.07); }
:deep(.mm-pin) { display: flex; flex-direction: column; align-items: center; }
:deep(.mm-emoji) { width: 36px; height: 36px; border-radius: 50%; background: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); border: 2px solid var(--clay-brand); }
:deep(.mm-card) { background: #fff; border-radius: 10px; padding: 5px 10px; margin-top: 4px; white-space: nowrap; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
:deep(.mm-name) { font-size: 12px; font-weight: 700; color: var(--clay-text); max-width: 100px; overflow: hidden; text-overflow: ellipsis; }
:deep(.mm-info) { font-size: 10px; color: var(--clay-text-soft); margin-top: 2px; }
</style>
