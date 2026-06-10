<template>
  <div class="order-list-page">
    <!-- 自定义状态Tab -->
    <div class="status-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['stab-btn', { active: activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="order-feed">
      <article
        v-for="o in orders"
        :key="o.id"
        class="order-card"
        @click="$router.push(`/order-detail/${o.id}`)"
      >
        <div class="oc-head">
          <div class="oc-merchant">
            <div class="oc-m-icon">
              <img
                :src="o.merchant_logo || 'https://img.yzcdn.cn/vant/cat.jpeg'"
              />
            </div>
            <span class="oc-m-name">{{ o.merchant_name }}</span>
          </div>
          <span :class="['oc-status', statusClass(o.status)]">{{
            statusText(o.status)
          }}</span>
        </div>

        <div class="oc-items" v-if="o.items">
          <div
            v-for="item in o.items.slice(0, 3)"
            :key="item.name"
            class="oc-item"
          >
            <span class="oci-name">{{ item.name }}</span>
            <span class="oci-qty">×{{ item.qty }}</span>
          </div>
          <div v-if="o.items.length > 3" class="oc-more">
            等 {{ o.items.length }} 件商品…
          </div>
        </div>

        <div class="oc-foot">
          <span class="oc-time">{{ o.create_time }}</span>
          <span class="oc-price">¥{{ o.total_amount }}</span>
        </div>

        <div class="oc-rider" v-if="o.rider">
          <span class="ocr-icon">🛵</span>
          <span>{{ o.rider.name }}</span>
          <span class="ocr-phone">{{ o.rider.phone }}</span>
        </div>
      </article>

      <van-empty v-if="orders.length === 0" description="暂无订单">
        <template #image><div class="empty-icon">📋</div></template>
      </van-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";

const activeTab = ref("");
const orders = ref([]);
const tabs = [
  { label: "全部", value: "" },
  { label: "待接单", value: "1" },
  { label: "配送中", value: "3" },
  { label: "已完成", value: "4" },
];

const statusText = (s) =>
  ({
    0: "待支付",
    1: "待接单",
    2: "已接单",
    3: "配送中",
    4: "已完成",
    "-1": "已取消",
  })[s] || "未知";
const statusClass = (s) => {
  const m = {
    1: "oc-pending",
    2: "oc-accepted",
    3: "oc-delivering",
    4: "oc-done",
    "-1": "oc-cancel",
  };
  return m[s] || "";
};

async function loadOrders() {
  try {
    const params = activeTab.value ? { status: parseInt(activeTab.value) } : {};
    const res = await axios.get("/api/orders", { params });
    if (res.data.code === 200) orders.value = res.data.data;
  } catch (e) {
    orders.value = [];
  }
}

watch(activeTab, () => loadOrders());
onMounted(() => loadOrders());
</script>

<style scoped>
.order-list-page {
  min-height: 100vh;
  background: var(--clay-page);
}

/* 状态Tab */
.status-tabs {
  display: flex;
  gap: 6px;
  padding: 12px 14px;
  background: var(--clay-card);
  border-bottom: 1px solid var(--clay-border);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.status-tabs::-webkit-scrollbar {
  display: none;
}
.stab-btn {
  flex-shrink: 0;
  padding: 8px 18px;
  border-radius: 22px;
  border: 1px solid var(--clay-border);
  background: var(--clay-page);
  color: var(--clay-text-soft);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s var(--spring);
  font-family: inherit;
}
.stab-btn.active {
  background: var(--clay-brand);
  color: #fff;
  border-color: var(--clay-brand);
  box-shadow: 0 2px 12px rgba(200, 75, 49, 0.25);
}

/* 订单列表 */
.order-feed {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  background: var(--clay-card);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid var(--clay-border);
  cursor: pointer;
  transition: all 0.25s var(--spring);
}
.order-card:active {
  transform: scale(0.985);
  background: var(--clay-card-warm);
}

.oc-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.oc-merchant {
  display: flex;
  align-items: center;
  gap: 10px;
}
.oc-m-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
}
.oc-m-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.oc-m-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--clay-text);
}

.oc-status {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}
.oc-pending {
  background: var(--clay-brand-light);
  color: var(--clay-brand);
}
.oc-accepted {
  background: var(--clay-success-bg);
  color: var(--clay-success);
}
.oc-delivering {
  background: var(--clay-info-bg);
  color: var(--clay-info);
}
.oc-done {
  background: #f5f2ed;
  color: var(--clay-text-soft);
}
.oc-cancel {
  background: var(--clay-danger-bg);
  color: var(--clay-danger);
}

.oc-items {
  padding: 8px 0;
  border-top: 1px solid var(--clay-divider);
}
.oc-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--clay-text-soft);
  padding: 3px 0;
}
.oci-name {
  flex: 1;
}
.oci-qty {
  color: var(--clay-text-muted);
}
.oc-more {
  font-size: 12px;
  color: var(--clay-text-muted);
  margin-top: 2px;
}

.oc-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--clay-divider);
}
.oc-time {
  font-size: 12px;
  color: var(--clay-text-muted);
}
.oc-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--clay-brand);
  font-family: Georgia, serif;
}

.oc-rider {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--clay-divider);
  font-size: 13px;
  color: var(--clay-text-soft);
}
.ocr-icon {
  font-size: 16px;
}
.ocr-phone {
  margin-left: auto;
  color: var(--clay-text-muted);
}

.empty-icon {
  font-size: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}
</style>
