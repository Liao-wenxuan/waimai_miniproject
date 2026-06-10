<template>
  <div class="help-page">
    <div class="help-search">
      <van-search v-model="searchText" shape="round" placeholder="搜索问题" @search="onSearch" clearable />
    </div>
    <div class="quick-row">
      <button v-for="item in quickEntries" :key="item.title" class="quick-chip" @click="scrollTo(item.id)">
        <span>{{ item.emoji }}</span> {{ item.title }}
      </button>
    </div>
    <div class="faq-section">
      <h3 class="faq-heading">常见问题</h3>
      <van-collapse v-model="activeNames" accordion>
        <van-collapse-item v-for="(item, idx) in filteredFaq" :key="idx" :name="idx" :id="'faq-' + idx">
          <template #title>
            <div class="faq-title"><span class="faq-dot"></span>{{ item.q }}</div>
          </template>
          <div class="faq-answer">{{ item.a }}</div>
        </van-collapse-item>
      </van-collapse>
    </div>
    <div class="contact-section">
      <h3 class="faq-heading">联系我们</h3>
      <van-cell-group inset>
        <van-cell title="客服电话" value="0835-2882000" />
        <van-cell title="客服微信" value="claywaimai" />
        <van-cell title="工作时间" value="09:00 - 22:00" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { showToast } from 'vant'
const searchText = ref(''); const activeNames = ref([])
const quickEntries = [
  { id: 'faq-0', emoji: '🛒', title: '下单' },
  { id: 'faq-1', emoji: '💳', title: '支付' },
  { id: 'faq-2', emoji: '🛵', title: '配送' },
  { id: 'faq-3', emoji: '🎁', title: '优惠' },
  { id: 'faq-4', emoji: '↩️', title: '退款' },
  { id: 'faq-5', emoji: '📍', title: '定位' },
]
const faqList = [
  { q:'怎么下单？', a:'1. 打开App，允许定位后自动显示附近商家。\n2. 点击商家进入菜单页，选择商品加入购物车。\n3. 确认后点击"去结算"，选择地址并支付。\n\n💡 地图上可以拖拽选取位置。' },
  { q:'支持哪些支付方式？', a:'目前为模拟支付模式，点击"立即支付"即可完成。无需真实付款。初始账户余额为 ¥500.00。' },
  { q:'配送怎么运作的？', a:'下单后商家准备餐品 → 骑手取餐 → 配送至收货地址。配送过程中可在地图上实时查看骑手位置。' },
  { q:'有什么优惠活动？', a:'🎉 首单立减 ¥5 · 满 ¥20 免配送费\n🔥 每日签到领积分 · 邀请好友各得 ¥3 优惠券' },
  { q:'如何申请退款？', a:'订单未接单时可随时取消。已接单请联系商家协商。食品质量问题可拍照上传全额退款。客服：0835-2882000' },
  { q:'定位不准怎么办？', a:'1. 确保GPS已开启\n2. 允许浏览器位置权限\n3. 点击首页地址栏刷新按钮\n4. 可拖拽地图手动选择位置' },
]
const filteredFaq = computed(() => {
  if (!searchText.value.trim()) return faqList
  const kw = searchText.value.trim().toLowerCase()
  return faqList.filter(f => f.q.includes(kw) || f.a.includes(kw))
})
function onSearch() { if (filteredFaq.value.length === 0) showToast('未找到相关问题') }
function scrollTo(id) {
  const el = document.getElementById(id)
  if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); activeNames.value = [parseInt(id.split('-')[1])] }
}
</script>

<style scoped>
.help-page { min-height: 100vh; background: var(--clay-page); padding-bottom: 30px; }
.help-search { background: var(--clay-card); padding: 4px 8px 8px; }
.quick-row { display: flex; gap: 8px; padding: 12px 16px; overflow-x: auto; background: var(--clay-card); border-bottom: 1px solid var(--clay-border); -webkit-overflow-scrolling: touch; }
.quick-row::-webkit-scrollbar { display: none; }
.quick-chip { flex-shrink: 0; display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 10px 16px; border: 1px solid var(--clay-border); border-radius: 14px; background: var(--clay-page); font-size: 12px; font-weight: 600; color: var(--clay-text-soft); cursor: pointer; font-family: inherit; transition: all 0.2s var(--spring); }
.quick-chip:active { background: var(--clay-brand-light); border-color: var(--clay-brand); color: var(--clay-brand); transform: scale(0.94); }
.faq-heading { font-size: 16px; font-weight: 700; color: var(--clay-text); padding: 24px 18px 10px; }
.faq-section { padding: 0 16px; }
.faq-section :deep(.van-collapse-item) { border-radius: 14px !important; overflow: hidden; margin-bottom: 6px; border: 1px solid var(--clay-border) !important; }
.faq-title { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; color: var(--clay-text); }
.faq-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--clay-brand); flex-shrink: 0; }
.faq-answer { font-size: 13px; color: var(--clay-text-body); line-height: 1.9; padding: 4px 0 10px; white-space: pre-line; }
.contact-section { padding: 0 16px; margin-top: 8px; }
.contact-section :deep(.van-cell-group) { border-radius: 16px; overflow: hidden; border: 1px solid var(--clay-border); }
</style>
