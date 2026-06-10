<template>
  <div class="rider-map-wrapper">
    <div ref="mapContainer" class="rmap-container"></div>
    <div class="rmap-loading" v-if="loading">
      <van-loading type="spinner" color="var(--clay-brand)" />
      <span>地图加载中…</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  merchantLng: { type: Number, default: 104.0657 },
  merchantLat: { type: Number, default: 30.6598 },
  userLng: { type: Number, default: 104.0657 },
  userLat: { type: Number, default: 30.6598 },
  riderLng: { type: Number, default: 104.0657 },
  riderLat: { type: Number, default: 30.6598 },
  showRider: { type: Boolean, default: false }
})

const mapContainer = ref(null)
const loading = ref(true)
let map = null, markers = []

function initMap() {
  if (!window.AMap || !mapContainer.value) return
  map = new AMap.Map(mapContainer.value, {
    zoom: 14, center: [props.merchantLng || 104.06, props.merchantLat || 30.66],
    features: ['bg', 'road', 'building', 'point'], showLabel: true
  })
  loading.value = false

  const merchantMarker = new AMap.Marker({ position: [props.merchantLng, props.merchantLat], title: '商家', label: { content: '🏪', offset: new AMap.Pixel(-10, -10) } })
  merchantMarker.setMap(map); markers.push(merchantMarker)

  const userMarker = new AMap.Marker({ position: [props.userLng, props.userLat], title: '收货地址', label: { content: '📍', offset: new AMap.Pixel(-10, -10) } })
  userMarker.setMap(map); markers.push(userMarker)

  if (props.showRider) {
    const riderMarker = new AMap.Marker({ position: [props.riderLng, props.riderLat], title: '骑手', label: { content: '🛵', offset: new AMap.Pixel(-12, -12) } })
    riderMarker.setMap(map); markers.push(riderMarker)
  }
  map.setFitView(null, false, [60,60,60,60])
}

watch(() => [props.riderLng, props.riderLat], ([nl, nlat]) => { if (markers.length >= 3 && map) markers[2].setPosition([nl, nlat]) })

onMounted(() => nextTick(() => initMap()))
onUnmounted(() => { if (map) { map.destroy(); map = null } })
</script>

<style scoped>
.rider-map-wrapper { position: relative; border-radius: 14px; overflow: hidden; border: 1px solid var(--clay-border); }
.rmap-container { width: 100%; height: 240px; }
.rmap-loading { position: absolute; inset: 0; background: rgba(253,248,240,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; font-size: 13px; color: var(--clay-text-soft); }
</style>
