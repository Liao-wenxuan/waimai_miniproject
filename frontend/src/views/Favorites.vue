<template>
  <div class="favorites-page">
    <div class="fav-feed" v-if="merchants.length > 0">
      <article v-for="m in merchants" :key="m.id" class="fav-card" @click="$router.push('/merchant/' + m.id)">
        <div class="fc-img">
          <img :src="m.logo || defaultLogo" />
        </div>
        <div class="fc-body">
          <h3 class="fc-name">{{ m.name }}</h3>
          <div class="fc-stars">
            <span v-for="i in 5" :key="i" :class="{ filled: i <= Math.round(m.rating) }">★</span>
            <span class="fc-rating">{{ m.rating }}</span>
            <span class="fc-sales">月售{{ m.monthly_sales }}</span>
          </div>
          <div class="fc-meta">¥{{ m.delivery_fee }} 配送 · 起送 ¥{{ m.min_price }}</div>
        </div>
        <button class="fc-del" @click.stop="removeFav(m.id)">✕</button>
      </article>
    </div>
    <van-empty v-else description="还没有收藏商家">
      <van-button type="primary" round size="small" @click="$router.push('/home')">去首页逛逛</van-button>
    </van-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { showToast, showFailToast } from 'vant'
const merchants = ref([])
const defaultLogo = 'https://img.yzcdn.cn/vant/cat.jpeg'
async function loadFavorites() {
  try { const r = await axios.get('/api/user/favorites'); if (r.data.code === 200) merchants.value = r.data.data } catch (e) {}
}
async function removeFav(id) {
  try { await axios.delete('/api/user/favorites/' + id); merchants.value = merchants.value.filter(m => m.id !== id); showToast('已取消收藏') } catch (e) { showFailToast('操作失败') }
}
onMounted(loadFavorites)
</script>

<style scoped>
.favorites-page { min-height: 100vh; background: var(--clay-page); padding: 14px 16px 30px; }
.fav-feed { display: flex; flex-direction: column; gap: 10px; }
.fav-card { display: flex; align-items: center; gap: 14px; background: var(--clay-card); border-radius: 18px; padding: 16px; border: 1px solid var(--clay-border); cursor: pointer; transition: all 0.2s var(--spring); }
.fav-card:active { transform: scale(0.985); background: var(--clay-card-warm); }
.fc-img { width: 68px; height: 68px; border-radius: 14px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.fc-img img { width: 100%; height: 100%; object-fit: cover; }
.fc-body { flex: 1; min-width: 0; }
.fc-name { font-size: 16px; font-weight: 600; color: var(--clay-text); margin-bottom: 4px; }
.fc-stars { display: flex; align-items: center; gap: 2px; margin-bottom: 2px; }
.fc-stars span { font-size: 11px; color: var(--clay-border); }
.fc-stars span.filled { color: var(--clay-accent); }
.fc-rating { font-size: 12px; font-weight: 600; color: var(--clay-accent); margin-left: 4px; }
.fc-sales { font-size: 11px; color: var(--clay-text-soft); margin-left: 6px; }
.fc-meta { font-size: 12px; color: var(--clay-text-soft); }
.fc-del { width: 32px; height: 32px; border-radius: 50%; border: none; background: var(--clay-page); color: var(--clay-text-soft); font-size: 14px; cursor: pointer; flex-shrink: 0; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; }
.fc-del:active { background: var(--clay-danger-bg); color: var(--clay-danger); }
</style>
