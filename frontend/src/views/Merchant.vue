<template>
  <div class="merchant-page">
    <!-- 商家头部 — 带有机形态遮罩 -->
    <div class="mch-header">
      <img :src="merchant.logo || defaultLogo" class="mch-cover" />
      <div class="mch-overlay">
        <div class="mch-info">
          <h1 class="mch-name">{{ merchant.name }}</h1>
          <div class="mch-stats">
            <span class="mch-rating">★ {{ merchant.rating }}</span>
            <span class="mch-sep">·</span>
            <span>月售 {{ merchant.monthly_sales }}</span>
          </div>
          <p class="mch-addr">{{ merchant.address }}</p>
        </div>
        <div class="mch-actions">
          <button class="mch-act-btn" @click.stop="showRouteMap = true">
            <span>↗</span> 导航
          </button>
          <button
            :class="['mch-act-btn', { liked: isFav }]"
            @click.stop="toggleFav"
          >
            <span>{{ isFav ? "♥" : "♡" }}</span> {{ isFav ? "已收藏" : "收藏" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 路线弹窗 -->
    <van-popup
      v-model:show="showRouteMap"
      position="bottom"
      round
      :style="{ maxHeight: '55%' }"
      closeable
      @closed="destroyRouteMap"
    >
      <div class="route-popup">
        <h3 class="route-title">前往 {{ merchant.name }}</h3>
        <div class="route-info" v-if="routeInfo">
          <span
            >距离 <b>{{ routeInfo.distance }}</b></span
          >
          <span
            >预计 <b>{{ routeInfo.duration }}</b></span
          >
        </div>
        <div id="route-map" ref="routeMapRef" class="route-map"></div>
      </div>
    </van-popup>

    <!-- 分类 Tab -->
    <van-tabs
      v-model:active="activeCategory"
      sticky
      offset-top="0"
      color="var(--clay-brand)"
    >
      <van-tab v-for="cat in categories" :key="cat" :title="cat" :name="cat">
        <div class="product-list">
          <article
            v-for="p in groupedProducts[cat]"
            :key="p.id"
            class="product-card"
          >
            <div class="prod-img">
              <img :src="p.image || defaultLogo" :alt="p.name" />
            </div>
            <div class="prod-body">
              <h3 class="prod-name">{{ p.name }}</h3>
              <p class="prod-desc" v-if="p.description">{{ p.description }}</p>
              <div class="prod-meta">
                <span class="prod-sales">月售{{ p.sales }}</span>
              </div>
              <div class="prod-row">
                <span class="prod-price"
                  >¥<b>{{ p.price }}</b></span
                >
                <div class="prod-ctrl">
                  <button
                    v-if="getCartQty(p.id) > 0"
                    class="ctrl-btn"
                    @click="removeFromCart(p)"
                  >
                    −
                  </button>
                  <span v-if="getCartQty(p.id) > 0" class="ctrl-qty">{{
                    getCartQty(p.id)
                  }}</span>
                  <button class="ctrl-btn ctrl-plus" @click="addToCart(p)">
                    +
                  </button>
                </div>
              </div>
            </div>
          </article>
          <van-empty
            v-if="!groupedProducts[cat]?.length"
            description="暂无商品"
          />
        </div>
      </van-tab>
    </van-tabs>

    <!-- 底部购物车栏 -->
    <div v-if="cartTotalQty > 0" class="cart-dock">
      <div class="cart-dock-icon" @click="showCart = true">
        <span class="cart-dock-bag">🛒</span>
        <span class="cart-dock-badge">{{ cartTotalQty }}</span>
      </div>
      <div class="cart-dock-info" @click="showCart = true">
        <span class="cart-dock-total">¥{{ cartTotalPrice }}</span>
        <span class="cart-dock-fee">配送费 ¥{{ merchant.delivery_fee }}</span>
      </div>
      <button
        class="cart-dock-btn"
        :disabled="cartTotalPrice < merchant.min_price"
        @click="goCheckout"
      >
        {{
          cartTotalPrice < merchant.min_price
            ? `差 ¥${(merchant.min_price - cartTotalPrice).toFixed(1)}`
            : "去结算"
        }}
      </button>
    </div>

    <!-- 购物车弹出 -->
    <van-popup
      v-model:show="showCart"
      position="bottom"
      round
      :style="{ maxHeight: '50%' }"
    >
      <div class="cart-popup">
        <div class="cart-popup-hd">
          <span>购物车</span>
          <button class="cart-clear" @click="clearCart">清空</button>
        </div>
        <div class="cart-popup-list">
          <div v-for="item in cartItems" :key="item.id" class="cart-popup-row">
            <span class="cart-row-name">{{ item.name }}</span>
            <span class="cart-row-price">¥{{ item.price }}</span>
            <div class="cart-row-ctrl">
              <button class="ctrl-btn sm" @click="removeFromCart(item)">
                −
              </button>
              <span>{{ item.qty }}</span>
              <button class="ctrl-btn sm ctrl-plus" @click="addToCart(item)">
                +
              </button>
            </div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import {
  showToast,
  showLoadingToast,
  closeToast,
  showSuccessToast,
  showFailToast,
} from "vant";

const route = useRoute();
const router = useRouter();
const merchant = ref({});
const products = ref([]);
const categories = ref([]);
const activeCategory = ref("");
const isFav = ref(false);
const showCart = ref(false);
const cartItems = reactive([]);
const defaultLogo = "https://img.yzcdn.cn/vant/cat.jpeg";

const showRouteMap = ref(false);
const routeMapRef = ref(null);
const routeInfo = ref(null);
let routeMapInstance = null;
let routeDriving = null;

const groupedProducts = computed(() => {
  const map = {};
  products.value.forEach((p) => {
    const c = p.category || "其他";
    if (!map[c]) map[c] = [];
    map[c].push(p);
  });
  return map;
});
const cartTotalQty = computed(() => cartItems.reduce((s, i) => s + i.qty, 0));
const cartTotalPrice = computed(() =>
  cartItems.reduce((s, i) => s + i.price * i.qty, 0).toFixed(1),
);

function getCartQty(pid) {
  const i = cartItems.find((x) => x.id === pid);
  return i ? i.qty : 0;
}
function addToCart(p) {
  const i = cartItems.find((x) => x.id === p.id);
  if (i) i.qty++;
  else cartItems.push({ ...p, qty: 1 });
}
function removeFromCart(p) {
  const idx = cartItems.findIndex((x) => x.id === p.id);
  if (idx >= 0) {
    if (cartItems[idx].qty > 1) cartItems[idx].qty--;
    else cartItems.splice(idx, 1);
  }
}
function clearCart() {
  cartItems.splice(0, cartItems.length);
  showCart.value = false;
}

function goCheckout() {
  const items = cartItems.map((i) => ({ product_id: i.id, product_name: i.name, price: i.price, quantity: i.qty }));
  localStorage.setItem("checkout_items", JSON.stringify(items));
  localStorage.setItem(
    "checkout_merchant",
    JSON.stringify({
      id: merchant.value.id,
      name: merchant.value.name,
      delivery_fee: merchant.value.delivery_fee,
      min_price: merchant.value.min_price,
    }),
  );
  localStorage.setItem("checkout_total", cartTotalPrice.value);
  router.push("/cart");
}

// ======== 路线规划（步行路线 + Haversine 兜底） ========
function getMyLocation() {
  return new Promise((resolve) => {
    if (navigator.geolocation)
      navigator.geolocation.getCurrentPosition(
        (p) => resolve([p.coords.longitude, p.coords.latitude]),
        () => resolve([103.001, 29.978]),
        { timeout: 5000, enableHighAccuracy: true },
      );
    else resolve([103.001, 29.978]);
  });
}

function haversineDistance(lng1, lat1, lng2, lat2) {
  const R = 6371000
  const toRad = (deg) => (deg * Math.PI) / 180
  const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

/** 等待 AMap.Walking 插件加载 */
function waitForWalking(retries = 30) {
  return new Promise((resolve) => {
    let n = 0
    const check = () => {
      if (window.AMap?.Walking) { resolve(true); return }
      if (++n >= retries) { resolve(false); return }
      setTimeout(check, 200)
    }
    check()
  })
}

async function initRouteMap() {
  if (!showRouteMap.value) return
  nextTick(async () => {
    const el = document.getElementById("route-map");
    if (!el || !window.AMap) return

    const mPos = [Number(merchant.value.lng), Number(merchant.value.lat)]
    const uPos = await getMyLocation()

    // 先用 Haversine 立即显示直线距离
    const straightDist = haversineDistance(uPos[0], uPos[1], mPos[0], mPos[1])
    routeInfo.value = {
      distance: straightDist > 1000 ? (straightDist / 1000).toFixed(1) + ' km' : Math.round(straightDist) + ' m',
      duration: '约' + Math.max(5, Math.ceil(straightDist / 80)) + ' 分钟',
    }

    showLoadingToast({ message: '规划路线…', forbidClick: true })

    // 创建地图
    routeMapInstance = new AMap.Map("route-map", { zoom: 15, center: mPos, resizeEnable: true })

    // 商家标记（终点）
    new AMap.Marker({
      position: mPos, title: merchant.value.name,
      icon: new AMap.Icon({
        size: new AMap.Size(32, 32),
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
        imageSize: new AMap.Size(32, 32),
      }),
      map: routeMapInstance,
    })
    // 用户标记（起点）
    new AMap.Marker({
      position: uPos, title: '我的位置',
      icon: new AMap.Icon({
        size: new AMap.Size(32, 32),
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
        imageSize: new AMap.Size(32, 32),
      }),
      map: routeMapInstance,
    })

    // 等待 Walking 插件，绘制步行路线
    const walkingReady = await waitForWalking()
    if (walkingReady) {
      const walking = new AMap.Walking({ map: routeMapInstance })
      walking.search(
        new AMap.LngLat(uPos[0], uPos[1]),
        new AMap.LngLat(mPos[0], mPos[1]),
        (status, result) => {
          closeToast()
          if (status === 'complete' && result.routes?.length > 0) {
            // 步行路线已自动绘制到地图上（蓝色虚线 + 转弯指引）
            const r = result.routes[0]
            routeInfo.value = {
              distance: r.distance > 1000 ? (r.distance / 1000).toFixed(1) + ' km' : r.distance + ' m',
              duration: Math.round(r.time / 60) + ' 分钟',
            }
            routeMapInstance.setFitView(null, false, [60, 60, 60, 60])
          } else {
            // 步行失败，用直线距离兜底
            routeMapInstance.setFitView(null, false, [80, 80, 80, 80])
          }
        }
      )
    } else {
      closeToast()
      routeMapInstance.setFitView(null, false, [80, 80, 80, 80])
    }
  });
}
function destroyRouteMap() {
  if (routeMapInstance) {
    routeMapInstance.destroy();
    routeMapInstance = null;
    routeDriving = null;
    routeInfo.value = null;
  }
}
watch(showRouteMap, (v) => {
  if (v) initRouteMap();
});

async function loadMerchant() {
  try {
    const res = await axios.get(`/api/merchants/${route.params.id}`);
    if (res.data.code === 200) {
      merchant.value = res.data.data.merchant;
      const all = [];
      const cats = Object.keys(res.data.data.products);
      categories.value = cats;
      activeCategory.value = cats[0] || "";
      cats.forEach((c) =>
        res.data.data.products[c].forEach((p) => all.push(p)),
      );
      products.value = all;
    }
  } catch (e) {
    merchant.value = {
      id: route.params.id,
      name: "测试商家",
      rating: 4.8,
      monthly_sales: 1234,
      delivery_fee: 5,
      min_price: 20,
      address: "武汉市洪山区",
    };
    categories.value = ["热销", "主食", "饮品", "小食"];
    activeCategory.value = "热销";
    products.value = [
      {
        id: 1,
        name: "巨无霸汉堡",
        price: 35,
        description: "双层牛肉饼",
        sales: 567,
        category: "热销",
      },
      {
        id: 2,
        name: "麦辣鸡腿堡",
        price: 28,
        description: "香辣鸡腿",
        sales: 890,
        category: "热销",
      },
      {
        id: 3,
        name: "薯条(大)",
        price: 14,
        description: "金黄酥脆",
        sales: 1200,
        category: "小食",
      },
      {
        id: 4,
        name: "可口可乐",
        price: 10,
        description: "冰镇",
        sales: 800,
        category: "饮品",
      },
    ];
  }
}
async function checkFav() {
  try {
    const r = await axios.get("/api/user/favorites");
    if (r.data.code === 200)
      isFav.value = r.data.data.some((m) => m.id === parseInt(route.params.id));
  } catch (e) {}
}
async function toggleFav() {
  const id = parseInt(route.params.id);
  try {
    if (isFav.value) {
      await axios.delete("/api/user/favorites/" + id);
      isFav.value = false;
      showToast("已取消收藏");
    } else {
      await axios.post("/api/user/favorites/" + id);
      isFav.value = true;
      showSuccessToast("已收藏 ♥");
    }
  } catch (e) {
    showFailToast("操作失败");
  }
}

function restoreCartFromCheckout() {
  try {
    const raw = localStorage.getItem('checkout_restore')
    if (!raw) return
    const items = JSON.parse(raw)
    if (!Array.isArray(items) || items.length === 0) return
    // 将下单页的商品数据恢复到购物车格式
    items.forEach(item => {
      const existing = cartItems.find(x => x.id === item.product_id)
      if (existing) {
        existing.qty = Math.max(existing.qty, item.quantity || 1)
      } else {
        cartItems.push({
          id: item.product_id,
          name: item.product_name || '商品',
          price: item.price || 0,
          qty: item.quantity || 1
        })
      }
    })
    localStorage.removeItem('checkout_restore')
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  loadMerchant();
  checkFav();
  // 从下单页返回时恢复购物车
  restoreCartFromCheckout()
});
</script>

<style scoped>
.merchant-page {
  min-height: 100vh;
  background: var(--clay-page);
  padding-bottom: 70px;
}

/* 头部 */
.mch-header {
  position: relative;
  height: 200px;
  overflow: hidden;
}
.mch-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: brightness(0.55) saturate(0.8);
}
.mch-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(0deg, rgba(44, 36, 22, 0.7) 0%, transparent 60%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 20px 18px;
}
.mch-name {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.02em;
  margin-bottom: 4px;
}
.mch-stats {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}
.mch-rating {
  color: var(--clay-accent);
  font-weight: 600;
}
.mch-sep {
  opacity: 0.5;
}
.mch-addr {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}
.mch-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.mch-act-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  backdrop-filter: blur(4px);
}
.mch-act-btn:active {
  background: rgba(255, 255, 255, 0.3);
}
.mch-act-btn.liked {
  background: rgba(200, 75, 49, 0.6);
  border-color: rgba(200, 75, 49, 0.8);
}

/* 商品列表 */
.product-list {
  padding: 8px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.product-card {
  display: flex;
  gap: 14px;
  background: var(--clay-card);
  border-radius: 16px;
  padding: 14px;
  border: 1px solid var(--clay-border);
  transition: all 0.2s var(--spring);
}
.product-card:active {
  background: var(--clay-card-warm);
  transform: scale(0.985);
}
.prod-img {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.prod-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.prod-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.prod-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--clay-text);
}
.prod-desc {
  font-size: 12px;
  color: var(--clay-text-soft);
}
.prod-sales {
  font-size: 11px;
  color: var(--clay-text-muted);
}
.prod-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}
.prod-price {
  font-family: Georgia, serif;
  color: var(--clay-brand);
  font-size: 13px;
}
.prod-price b {
  font-size: 20px;
  font-weight: 700;
}
.prod-ctrl {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ctrl-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1.5px solid var(--clay-brand);
  background: transparent;
  color: var(--clay-brand);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s var(--spring);
  font-family: inherit;
  line-height: 1;
}
.ctrl-btn:active {
  transform: scale(0.9);
}
.ctrl-plus {
  background: var(--clay-brand);
  color: #fff;
}
.ctrl-btn.sm {
  width: 24px;
  height: 24px;
  font-size: 14px;
}
.ctrl-qty {
  font-size: 15px;
  font-weight: 700;
  color: var(--clay-text);
  min-width: 20px;
  text-align: center;
}

/* 底部购物车 */
.cart-dock {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--clay-text);
  z-index: 100;
}
.cart-dock-icon {
  position: relative;
  flex-shrink: 0;
  cursor: pointer;
}
.cart-dock-bag {
  font-size: 28px;
  display: block;
}
.cart-dock-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  background: var(--clay-brand);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}
.cart-dock-info {
  flex: 1;
  color: #fff;
  cursor: pointer;
}
.cart-dock-total {
  font-size: 18px;
  font-weight: 700;
  font-family: Georgia, serif;
}
.cart-dock-fee {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
}
.cart-dock-btn {
  padding: 10px 22px;
  border-radius: 22px;
  border: none;
  background: var(--clay-brand);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s var(--spring);
  font-family: inherit;
  white-space: nowrap;
}
.cart-dock-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.cart-dock-btn:not(:disabled):active {
  transform: scale(0.95);
}

/* 购物车弹出 */
.cart-popup {
  padding-bottom: 20px;
}
.cart-popup-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--clay-divider);
}
.cart-clear {
  border: none;
  background: none;
  color: var(--clay-text-soft);
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
}
.cart-popup-list {
  padding: 8px 18px;
}
.cart-popup-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--clay-divider);
}
.cart-row-name {
  flex: 1;
  font-size: 14px;
  color: var(--clay-text);
}
.cart-row-price {
  color: var(--clay-brand);
  font-weight: 600;
  margin: 0 16px;
}
.cart-row-ctrl {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

/* 路线弹窗 */
.route-popup {
  padding: 20px 18px;
}
.route-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}
.route-info {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: var(--clay-text-soft);
  margin-bottom: 12px;
}
.route-info b {
  color: var(--clay-brand);
}
.route-map {
  width: 100%;
  height: 200px;
  border-radius: 14px;
  overflow: hidden;
}
</style>
