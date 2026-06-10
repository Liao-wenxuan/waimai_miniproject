<template>
  <div class="home-page">
    <!-- 地址栏 — 压缩的有机形态 -->
    <div class="addr-strip" @click="refreshLocation">
      <div class="addr-pin">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="var(--clay-brand)" stroke-width="2">
          <path d="M12 2C8.1 2 5 5.1 5 9c0 5.5 7 13 7 13s7-7.5 7-13c0-3.9-3.1-7-7-7z"/>
          <circle cx="12" cy="9" r="2.5"/>
        </svg>
      </div>
      <div class="addr-text-wrap">
        <span class="addr-label">{{ locating ? '定位中…' : (currentAddress || '点击定位') }}</span>
        <span v-if="!locating && currentAddress" class="addr-sub">当前区域</span>
      </div>
      <span class="addr-action" v-if="!locating">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.5 15.5A9 9 0 005.6 5.6"/></svg>
      </span>
    </div>

    <!-- 搜索 -->
    <div class="search-strip">
      <van-search
        v-model="searchText" shape="round"
        background="transparent" placeholder="搜索你想吃的…"
        @search="onSearch" @input="onSearchInput" clearable
      />
    </div>

    <!-- 视图切换 -->
    <div class="view-toggle">
      <button :class="['toggle-btn', { active: viewMode === 'map' }]" @click="viewMode = 'map'">
        <span class="toggle-icon">◧</span> 地图
      </button>
      <button :class="['toggle-btn', { active: viewMode === 'list' }]" @click="viewMode = 'list'">
        <span class="toggle-icon">☰</span> 列表
      </button>
    </div>

    <!-- 地图视图 -->
    <div v-show="viewMode === 'map'" class="map-view">
      <NearbyMap ref="nearbyMap"
        :merchants="merchants" :userLng="userLng" :userLat="userLat"
        :addressLabel="currentAddress" @merchant-click="goMerchant"
        @locate="refreshLocation" @center-changed="onMapCenterChanged"
      />
    </div>

    <!-- 列表视图 -->
    <div v-show="viewMode === 'list'" class="list-view">
      <!-- 距离滑块 -->
      <div class="range-bar">
        <div class="range-header">
          <span class="range-title">搜索范围</span>
          <span class="range-value">{{ distanceRange }}<small>km</small></span>
        </div>
        <van-slider v-model="distanceRange" :min="1" :max="10" :step="1"
          bar-color="var(--clay-brand)" active-color="var(--clay-brand-light)"
          @update:model-value="onRangeChangeDebounced" />
        <div class="range-labels"><span>1</span><span>5</span><span>10</span></div>
      </div>

      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <!-- 范围变化时的加载遮罩 -->
        <div v-if="rangeLoading" class="range-loading-overlay">
          <div class="range-loading-card">
            <van-loading type="spinner" size="22" color="var(--clay-brand)" />
            <span>正在搜索 {{ distanceRange }}km 内的商家…</span>
          </div>
        </div>

        <div class="merchant-grid" :class="{ 'is-loading': rangeLoading }">
          <article
            v-for="(m, idx) in merchants" :key="m.id"
            :class="['merchant-card', `animate-rise animate-rise-${(idx % 4) + 1}`]"
            @click="goMerchant(m.id)"
          >
            <div class="mc-media">
              <img :src="m.logo || defaultLogo" :alt="m.name" />
              <button class="mc-fav" :class="{ liked: favIds.includes(m.id) }" @click.stop="toggleFav(m.id)">
                {{ favIds.includes(m.id) ? '♥' : '♡' }}
              </button>
            </div>
            <div class="mc-body">
              <h3 class="mc-name">{{ m.name }}</h3>
              <div class="mc-stars">
                <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.round(m.rating) }">★</span>
                <span class="mc-rating">{{ m.rating }}</span>
              </div>
              <div class="mc-meta">
                <span>起送 ¥{{ m.min_price }}</span>
                <span class="mc-dot">·</span>
                <span>配送 ¥{{ m.delivery_fee }}</span>
              </div>
              <div class="mc-footer">
                <span class="mc-distance">{{ m.distance?.toFixed(1) }}km</span>
                <span v-if="m.monthly_sales > 500" class="mc-hot">热销</span>
              </div>
            </div>
          </article>

          <van-empty v-if="!refreshing && merchants.length === 0"
            :description="searchText ? '没有找到匹配的商家' : '附近暂无商家'" />
        </div>
      </van-pull-refresh>
    </div>

    <!-- 手动输入坐标弹窗 -->
    <van-dialog v-model:show="showManualInput" title="手动设置坐标"
      show-cancel-button confirm-button-text="确认" confirm-button-color="#C84B31"
      @confirm="applyManualLocation">
      <div class="manual-form">
        <van-field v-model="manualLng" label="经度" placeholder="例如: 103.00" type="number" />
        <van-field v-model="manualLat" label="纬度" placeholder="例如: 29.98" type="number" />
        <div class="manual-hint">雅安坐标参考: 经度 103.00, 纬度 29.98</div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { showToast, showLoadingToast, closeToast, showSuccessToast, showFailToast } from 'vant'
import NearbyMap from '../components/NearbyMap.vue'

const router = useRouter()

const viewMode = ref('list')
const nearbyMap = ref(null)
const merchants = ref([])
const refreshing = ref(false)
const rangeLoading = ref(false)
const searchText = ref('')
const currentAddress = ref('')
const favIds = ref([])
const locating = ref(false)
const locationFailed = ref(false)
const manualPick = ref(false)

const defaultLogo = 'https://img.yzcdn.cn/vant/cat.jpeg'
const userLng = ref(0)
const userLat = ref(0)
const distanceRange = ref(3)

const showManualInput = ref(false)
const manualLng = ref('')
const manualLat = ref('')

let searchTimer = null
let watchId = null
let loadReqId = 0
let watchDebounceTimer = null

function applyManualLocation() {
  const lng = parseFloat(manualLng.value), lat = parseFloat(manualLat.value)
  if (isNaN(lng) || isNaN(lat)) { showFailToast('请输入有效坐标'); return }
  userLng.value = lng; userLat.value = lat
  manualPick.value = true; locationFailed.value = false
  reverseGeocode(lng, lat); loadMerchants()
  setTimeout(() => saveLocation(), 1000)
  showSuccessToast('位置已更新')
}

function startWatchingPosition() {
  if (!navigator.geolocation) { currentAddress.value = '浏览器不支持定位'; locationFailed.value = true; return }
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { longitude: lng, latitude: lat, accuracy: acc } = pos.coords
      if (!manualPick.value || acc < 50) {
        userLng.value = lng; userLat.value = lat
        locationFailed.value = false
        reverseGeocode(lng, lat)
        if (!manualPick.value) { loadMerchants(); setTimeout(() => saveLocation(), 1000) }
      }
      locating.value = !(acc < 500)
    },
    (err) => {
      locationFailed.value = true; locating.value = false
      const msgs = { 1: '权限被拒绝，请允许定位', 2: '无法获取位置', 3: '定位超时' }
      currentAddress.value = msgs[err.code] || '定位失败，请手动输入坐标'
    },
    { timeout: 10000, enableHighAccuracy: false, maximumAge: 60000 }
  )
  if ('watchPosition' in navigator.geolocation) {
    let lastAcc = Infinity
    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { longitude: lng, latitude: lat, accuracy: acc } = pos.coords
        if (!manualPick.value || acc < 30) {
          if (acc < lastAcc || acc < 500) {
            lastAcc = acc
            userLng.value = lng; userLat.value = lat
            reverseGeocode(lng, lat)
            if (acc < 200 && !manualPick.value) setTimeout(() => saveLocation(), 1000)
            // 每次定位更新后重新筛选商家（防抖 2 秒）
            clearTimeout(watchDebounceTimer)
            watchDebounceTimer = setTimeout(() => loadMerchants(searchText.value), 2000)
          }
        }
        if (acc < 100) locating.value = false
      },
      (err) => { if (err.code === 1) { locationFailed.value = true; currentAddress.value = '定位权限被拒绝' }; locating.value = false },
      { enableHighAccuracy: true, timeout: 20000, maximumAge: 3000 }
    )
  }
}

function stopWatchingPosition() {
  if (watchId !== null) { navigator.geolocation.clearWatch(watchId); watchId = null }
}

function refreshLocation() {
  showLoadingToast({ message: '正在定位…', forbidClick: true, duration: 0 })
  manualPick.value = false
  stopWatchingPosition()
  startWatchingPosition()
  const check = setInterval(() => {
    if (!locating.value) {
      clearInterval(check); closeToast()
      if (!locationFailed.value && userLng.value !== 0) showSuccessToast('定位成功 ✦')
      else if (locationFailed.value) showFailToast('定位失败，请检查GPS')
    }
  }, 300)
  setTimeout(() => { clearInterval(check); closeToast(); if (locating.value) showFailToast('定位超时') }, 8000)
}

function reverseGeocode(lng, lat) {
  if (!lng || !lat) return
  currentAddress.value = '定位中…'
  if (!window.AMap) { currentAddress.value = `${lat.toFixed(2)}, ${lng.toFixed(2)}`; return }
  try {
    const ps = new AMap.PlaceSearch({ type: '050000|060000|070000|080000|120000', pageSize: 1, pageIndex: 1, radius: 200 })
    ps.searchNearBy('', [lng, lat], 200, (status, result) => {
      if (status === 'complete' && result.poiList?.pois?.length > 0) {
        const n = result.poiList.pois[0]
        if (n.name && n.name.length > 2 && !n.name.match(/^[\d.]+$/)) { currentAddress.value = n.name; return }
        if (n.address) { currentAddress.value = n.address.length > 28 ? n.address.substring(0, 28) + '…' : n.address; return }
      }
      fallbackGeocode(lng, lat)
    })
  } catch (e) { fallbackGeocode(lng, lat) }
}

function fallbackGeocode(lng, lat) {
  try {
    const gc = new AMap.Geocoder({ radius: 500 })
    gc.getAddress([lng, lat], (status, result) => {
      if (status === 'complete' && result.regeocode) {
        const c = result.regeocode.addressComponent || {}
        const parts = [c.district, c.township, c.street, c.streetNumber].filter(Boolean)
        currentAddress.value = parts.length >= 2 ? parts.join('') : (result.regeocode.formattedAddress || `${lat.toFixed(2)}, ${lng.toFixed(2)}`)
      } else { currentAddress.value = `${lat.toFixed(2)}, ${lng.toFixed(2)}` }
    })
  } catch (e) { currentAddress.value = `${lat.toFixed(2)}, ${lng.toFixed(2)}` }
}

async function loadMerchants(keyword = '') {
  const reqId = ++loadReqId
  try {
    const res = await axios.get('/api/merchants', { params: { lng: userLng.value, lat: userLat.value, keyword, range: distanceRange.value } })
    if (reqId !== loadReqId) return
    if (res.data.code === 200) {
      merchants.value = res.data.data
      localStorage.setItem('cached_merchants', JSON.stringify({ data: res.data.data, time: Date.now() }))
    }
  } catch (e) { if (reqId !== loadReqId) return }
}

function restoreMerchants() {
  try {
    const raw = localStorage.getItem('cached_merchants')
    if (!raw) return false
    const c = JSON.parse(raw)
    if (c.data?.length && (Date.now() - c.time < 10 * 60 * 1000)) { merchants.value = c.data; return true }
  } catch (e) {}
  return false
}

function onSearch() { loadMerchants(searchText.value); if (viewMode.value === 'map') viewMode.value = 'list' }
function onSearchInput(v) { clearTimeout(searchTimer); searchTimer = setTimeout(() => loadMerchants(v), 500) }
async function onRefresh() { await loadMerchants(searchText.value); refreshing.value = false }
let rangeDebounceTimer = null
function onRangeChangeDebounced() {
  clearTimeout(rangeDebounceTimer)
  rangeLoading.value = true
  rangeDebounceTimer = setTimeout(async () => {
    await loadMerchants(searchText.value)
    rangeLoading.value = false
  }, 300)
}

async function loadFavIds() {
  try { const r = await axios.get('/api/user/favorites'); if (r.data.code === 200) favIds.value = r.data.data.map(m => m.id) } catch (e) {}
}
async function toggleFav(mid) {
  const isFav = favIds.value.includes(mid)
  try {
    if (isFav) { await axios.delete('/api/user/favorites/' + mid); favIds.value = favIds.value.filter(id => id !== mid); showToast('已取消收藏') }
    else { await axios.post('/api/user/favorites/' + mid); favIds.value.push(mid); showSuccessToast('已收藏 ♥') }
  } catch (e) { showFailToast('操作失败') }
}

function goMerchant(id) { router.push(`/merchant/${id}`) }

const LOCATION_KEY = 'saved_location'
function saveLocation() {
  if (userLng.value && userLat.value) localStorage.setItem(LOCATION_KEY, JSON.stringify({ lng: userLng.value, lat: userLat.value, address: currentAddress.value, time: Date.now() }))
}
function restoreLocation() {
  try {
    const r = localStorage.getItem(LOCATION_KEY); if (!r) return false
    const s = JSON.parse(r)
    if (s.lng && s.lat && (Date.now() - s.time < 24 * 3600 * 1000)) {
      userLng.value = s.lng; userLat.value = s.lat; manualPick.value = true
      if (s.address && !s.address.includes('定位中')) currentAddress.value = s.address
      return true
    }
  } catch (e) {}
  return false
}

function onMapCenterChanged({ lng, lat }) {
  userLng.value = lng; userLat.value = lat; manualPick.value = true; locationFailed.value = false
  stopWatchingPosition(); reverseGeocode(lng, lat); loadMerchants()
  setTimeout(() => saveLocation(), 1000)
}

onMounted(() => {
  loadFavIds()
  const restored = restoreLocation()
  const hasCache = restoreMerchants()
  if (!hasCache) loadMerchants()
  if (hasCache) loadMerchants()
  if (!restored) startWatchingPosition()
})

// 切换到地图视图时主动触发 resize
watch(viewMode, (mode) => {
  if (mode === 'map') {
    setTimeout(() => {
      if (nearbyMap.value?.resizeMap) nearbyMap.value.resizeMap()
    }, 100)
  }
})
onUnmounted(() => { stopWatchingPosition(); clearTimeout(searchTimer); clearTimeout(watchDebounceTimer) })
</script>

<style scoped>
.home-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 20px; }

/* 地址栏 */
.addr-strip {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  background: var(--clay-card);
  border-bottom: 1px solid var(--clay-border);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.addr-pin { flex-shrink: 0; }
.addr-text-wrap { flex: 1; min-width: 0; }
.addr-label {
  font-size: 14px; font-weight: 600; color: var(--clay-text);
  display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.addr-sub { font-size: 11px; color: var(--clay-text-soft); }
.addr-action { color: var(--clay-text-soft); opacity: 0.5; }

/* 搜索 */
.search-strip { background: var(--clay-card); padding: 0 8px 4px; }
.search-strip :deep(.van-search__content) { background: var(--clay-page) !important; border: 1px solid var(--clay-border) !important; }

/* 视图切换 */
.view-toggle { display: flex; gap: 8px; padding: 8px 16px; background: var(--clay-card); }
.toggle-btn {
  flex: 1; padding: 10px;
  border: 1px solid var(--clay-border); border-radius: 14px;
  background: var(--clay-page); color: var(--clay-text-soft);
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.3s var(--spring); font-family: inherit;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.toggle-btn.active {
  background: var(--clay-brand-light); color: var(--clay-brand);
  border-color: var(--clay-brand);
  box-shadow: 0 2px 12px rgba(200, 75, 49, 0.1);
}
.toggle-icon { font-size: 16px; }

/* 地图 */
.map-view { position: relative; }

/* 距离滑块 */
.range-bar { background: var(--clay-card); padding: 12px 16px 8px; margin-bottom: 8px; }
.range-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px; }
.range-title { font-size: 13px; font-weight: 600; color: var(--clay-text-body); }
.range-value { font-size: 20px; font-weight: 700; color: var(--clay-brand); font-family: Georgia, serif; }
.range-value small { font-size: 12px; font-weight: 400; color: var(--clay-text-soft); }
.range-labels { display: flex; justify-content: space-between; font-size: 10px; color: var(--clay-text-muted); padding-top: 2px; }

/* 商家网格 */
.merchant-grid { padding: 0 14px; display: flex; flex-direction: column; gap: 12px; }

.merchant-card {
  display: flex; gap: 14px;
  background: var(--clay-card);
  border-radius: 18px;
  padding: 14px;
  border: 1px solid var(--clay-border);
  cursor: pointer;
  transition: all 0.25s var(--spring);
  position: relative;
  overflow: hidden;
}
.merchant-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--clay-brand);
  border-radius: 0 4px 4px 0;
  transform: scaleY(0);
  transition: transform 0.3s var(--spring);
}
.merchant-card:active { transform: scale(0.985); background: var(--clay-card-warm); }
.merchant-card:active::before { transform: scaleY(1); }

.mc-media {
  width: 80px; height: 80px; border-radius: 14px; overflow: hidden;
  flex-shrink: 0; position: relative;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.mc-media img { width: 100%; height: 100%; object-fit: cover; }
.mc-fav {
  position: absolute; top: 4px; right: 4px;
  width: 28px; height: 28px; border-radius: 50%;
  border: none; background: rgba(255,255,255,0.9);
  font-size: 14px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s var(--spring);
  color: var(--clay-text-muted); line-height: 1;
}
.mc-fav:active { transform: scale(1.2); }
.mc-fav.liked { color: #C0392B; background: #fff; }

.mc-body { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.mc-name { font-size: 16px; font-weight: 600; color: var(--clay-text); letter-spacing: 0.01em; }
.mc-stars { display: flex; align-items: center; gap: 2px; }
.star { font-size: 11px; color: var(--clay-border); }
.star.filled { color: var(--clay-accent); }
.mc-rating { font-size: 12px; font-weight: 600; color: var(--clay-accent); margin-left: 4px; }
.mc-meta { font-size: 12px; color: var(--clay-text-soft); display: flex; align-items: center; gap: 6px; }
.mc-dot { color: var(--clay-text-muted); }
.mc-footer { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.mc-distance {
  font-size: 12px; font-weight: 600;
  background: var(--clay-brand-light); color: var(--clay-brand);
  padding: 2px 10px; border-radius: 12px;
}
.mc-hot {
  font-size: 11px; font-weight: 700;
  background: var(--clay-accent-light); color: var(--clay-accent);
  padding: 2px 10px; border-radius: 12px;
}

/* 范围加载遮罩 */
.range-loading-overlay {
  position: absolute; inset: 0; z-index: 10;
  display: flex; align-items: flex-start; justify-content: center;
  padding-top: 60px;
}
.range-loading-card {
  display: flex; align-items: center; gap: 10px;
  background: var(--clay-card);
  padding: 12px 20px;
  border-radius: 20px;
  box-shadow: var(--shadow-lg);
  font-size: 13px; color: var(--clay-text-soft);
}
.merchant-grid.is-loading {
  opacity: 0.35;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

/* 手动坐标 */
.manual-form { padding: 16px 16px 8px; }
.manual-hint { font-size: 11px; color: var(--clay-text-soft); padding: 8px 16px; }
</style>
