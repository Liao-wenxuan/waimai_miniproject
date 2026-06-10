<template>
  <div class="settings-page">
    <div class="set-label">通知</div>
    <van-cell-group inset>
      <van-cell title="新订单通知" center><template #right-icon><van-switch v-model="settings.orderNotify" active-color="#C84B31" size="26" @change="onToggle('orderNotify')" /></template></van-cell>
      <van-cell title="配送状态提醒" center><template #right-icon><van-switch v-model="settings.statusNotify" active-color="#C84B31" size="26" @change="onToggle('statusNotify')" /></template></van-cell>
      <van-cell title="声音提醒" center label="接单/完成时播放提示音"><template #right-icon><van-switch v-model="settings.soundNotify" active-color="#C84B31" size="26" @change="onToggle('soundNotify')" /></template></van-cell>
    </van-cell-group>

    <div class="set-label">显示</div>
    <van-cell-group inset>
      <van-cell title="暗黑模式" center><template #right-icon><van-switch v-model="settings.darkMode" active-color="#2C2416" size="26" @change="onToggle('darkMode')" /></template></van-cell>
      <van-cell title="默认视图" is-link :value="settings.mapView === 'map' ? '附近地图' : '商家列表'" @click="showMapPicker = true" />
    </van-cell-group>

    <div class="set-label">通用</div>
    <van-cell-group inset>
      <van-cell title="清理缓存" is-link @click="clearCache"><template #icon><span style="margin-right:8px">🗑</span></template></van-cell>
      <van-cell title="检查更新" is-link value="v1.0.0" @click="checkUpdate" />
    </van-cell-group>

    <div class="set-label">关于</div>
    <van-cell-group inset>
      <van-cell title="用户协议" is-link @click="showToast('开发中')" />
      <van-cell title="隐私政策" is-link @click="showToast('开发中')" />
      <van-cell title="版本号" value="v1.0.0 · Clay" />
    </van-cell-group>

    <van-popup v-model:show="showMapPicker" position="bottom" round :style="{ height: '30%' }">
      <div class="picker-wrap">
        <div class="picker-title">默认视图</div>
        <van-radio-group v-model="settings.mapView" direction="horizontal" @change="saveSettings">
          <van-radio name="map"><div class="radio-card"><span>◧</span> 地图</div></van-radio>
          <van-radio name="list"><div class="radio-card"><span>☰</span> 列表</div></van-radio>
        </van-radio-group>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { showToast, showSuccessToast, showConfirmDialog } from 'vant'
const SETTINGS_KEY = 'app_settings'
const settings = reactive({ orderNotify: true, statusNotify: true, soundNotify: true, darkMode: false, mapView: 'list' })
const showMapPicker = ref(false)
function loadSettings() { try { const s = localStorage.getItem(SETTINGS_KEY); if (s) Object.assign(settings, JSON.parse(s)); if (settings.darkMode) document.documentElement.classList.add('dark') } catch (e) {} }
function saveSettings() { localStorage.setItem(SETTINGS_KEY, JSON.stringify({...settings})) }
function onToggle(key) { if (key === 'darkMode') document.documentElement.classList.toggle('dark', settings.darkMode); saveSettings(); showToast(settings[key] ? '已开启' : '已关闭') }
function clearCache() {
  showConfirmDialog({ title: '清理缓存', message: '清除本地缓存数据，不影响账号和订单。', confirmButtonColor: '#C84B31' }).then(() => {
    const keep = ['token','role','userInfo',SETTINGS_KEY,'saved_location']
    Object.keys(localStorage).forEach(k => { if (!keep.includes(k)) localStorage.removeItem(k) })
    showSuccessToast('缓存已清理')
  }).catch(() => {})
}
function checkUpdate() { showToast('已是最新版本') }
onMounted(loadSettings)
</script>

<style scoped>
.settings-page { min-height: 100vh; background: var(--clay-page); padding: 14px 16px 30px; }
.set-label { font-size: 12px; font-weight: 700; color: var(--clay-text-soft); padding: 22px 4px 8px; letter-spacing: 0.06em; text-transform: uppercase; }
.settings-page :deep(.van-cell-group) { border-radius: 16px; overflow: hidden; border: 1px solid var(--clay-border); }
.picker-wrap { padding: 32px 20px; }
.picker-title { font-size: 17px; font-weight: 700; color: var(--clay-text); margin-bottom: 24px; text-align: center; }
:deep(.van-radio-group--horizontal) { justify-content: center; gap: 20px; }
.radio-card { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 24px; background: var(--clay-page); border-radius: 16px; font-size: 14px; font-weight: 600; color: var(--clay-text-soft); border: 1px solid var(--clay-border); }
.radio-card span { font-size: 24px; }
</style>
