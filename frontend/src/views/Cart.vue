<template>
  <div class="checkout-page">
    <!-- 顶部导航栏 — 返回按钮 -->
    <div class="checkout-header">
      <button class="back-btn" @click="goBack">
        <svg
          viewBox="0 0 24 24"
          width="22"
          height="22"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
      <span class="header-title">确认订单</span>
      <span class="header-spacer" />
    </div>

    <!-- 地址选择 -->
    <div class="section addr-sect" @click="showAddressPopup = true">
      <div class="addr-icon">
        <svg
          viewBox="0 0 24 24"
          width="22"
          height="22"
          fill="none"
          stroke="var(--clay-brand)"
          stroke-width="2"
        >
          <path
            d="M12 2C8.1 2 5 5.1 5 9c0 5.5 7 13 7 13s7-7.5 7-13c0-3.9-3.1-7-7-7z"
          />
          <circle cx="12" cy="9" r="2.5" />
        </svg>
      </div>
      <div class="addr-body">
        <div class="addr-line1">
          <b>{{ address.name || "选择收货地址" }}</b>
          <span class="addr-phone">{{ address.phone }}</span>
        </div>
        <div class="addr-line2">{{ address.detail }}</div>
      </div>
      <span class="addr-arrow">→</span>
    </div>

    <!-- 商家 -->
    <div class="section">
      <div class="section-label">{{ merchant.name }}</div>
      <div class="section-sub" v-if="merchant.min_price">
        起送 ¥{{ merchant.min_price }}
      </div>
    </div>

    <!-- 商品清单 -->
    <div class="section">
      <div class="section-label-sm">商品清单</div>
      <div class="checkout-item" v-for="item in items" :key="item.product_id">
        <span class="ci-name">{{
          item.product_name || `商品${item.product_id}`
        }}</span>
        <span class="ci-qty">×{{ item.quantity || 1 }}</span>
        <span class="ci-price"
          >¥{{
            ((parseFloat(item.price) || 0) * (item.quantity || 1)).toFixed(2)
          }}</span
        >
      </div>
    </div>

    <!-- 费用明细 — 动态计算 -->
    <div class="section fee-section">
      <div class="section-label-sm">费用明细</div>
      <div class="fee-row">
        <span>商品小计</span>
        <span>¥{{ subtotal }}</span>
      </div>
      <div class="fee-row">
        <span>配送费</span>
        <span>{{
          deliveryFee > 0 ? "¥" + deliveryFee.toFixed(2) : "免配送费"
        }}</span>
      </div>
      <div class="fee-row">
        <span>打包费</span>
        <span>¥{{ packagingFee.toFixed(2) }}</span>
      </div>
      <!-- 未达起送价提示 -->
      <div v-if="!meetsMinPrice" class="min-price-warn">
        ⚠ 还差 ¥{{
          (merchant.min_price - parseFloat(subtotal)).toFixed(2)
        }}
        达到起送价 ¥{{ merchant.min_price }}
      </div>
      <div class="divider-organic"></div>
      <div class="fee-row fee-total">
        <span>合计</span>
        <span class="total-num">¥{{ total }}</span>
      </div>
    </div>

    <!-- 备注 -->
    <div class="section">
      <div class="remark-field">
        <span class="remark-icon">✎</span>
        <input
          v-model="remark"
          placeholder="备注（选填）"
          class="remark-input"
        />
      </div>
    </div>

    <!-- 提交 -->
    <div class="submit-bar">
      <div class="submit-total">
        <span>合计</span>
        <span class="submit-price">¥{{ total }}</span>
      </div>
      <button
        class="submit-btn"
        :disabled="submitting || !meetsMinPrice"
        @click="submitOrder"
      >
        {{
          submitting ? "提交中…" : meetsMinPrice ? "提交订单" : "金额未达起送价"
        }}
      </button>
    </div>

    <!-- 地址选择弹窗 -->
    <van-popup
      v-model:show="showAddressPopup"
      position="bottom"
      round
      :style="{ maxHeight: '70%' }"
    >
      <div class="popup-hd">选择收货地址</div>
      <div class="address-list-container">
        <div
          v-for="item in addressList"
          :key="item.id"
          class="address-item"
          :class="{ selected: chosenAddressId === item.id }"
          @click="onSelectAddress(item)"
        >
          <div class="address-item-header">
            <div class="address-item-left">
              <span class="address-item-name">{{ item.name }}</span>
              <span class="address-item-phone">{{ item.tel }}</span>
            </div>
            <div class="address-item-right">
              <span v-if="item.isDefault" class="address-item-tag">默认</span>
              <span v-else-if="item.tag" class="address-item-tag">{{
                item.tag
              }}</span>
              <span v-if="chosenAddressId === item.id" class="address-check"
                >✓</span
              >
            </div>
          </div>
          <div class="address-item-detail">{{ item.address }}</div>
          <div class="address-item-actions">
            <button
              class="address-item-btn edit"
              @click.stop="onEditAddress(item)"
            >
              编辑
            </button>
            <button
              class="address-item-btn delete"
              @click.stop="deleteAddress(item.id)"
            >
              删除
            </button>
          </div>
        </div>
        <div v-if="addressList.length === 0" class="empty-address">
          <div class="empty-icon">📍</div>
          <div class="empty-text">暂无收货地址</div>
        </div>
      </div>
      <div class="popup-ft">
        <button class="add-addr-btn" @click="showAddAddress = true">
          新增地址
        </button>
      </div>
    </van-popup>

    <!-- 新增/编辑地址弹窗 -->
    <van-popup
      v-model:show="showAddAddress"
      position="bottom"
      round
      :style="{ maxHeight: '80%' }"
    >
      <div class="popup-hd">
        {{ editingAddress.id ? "编辑地址" : "新增地址" }}
      </div>
      <div class="addr-form">
        <div class="form-row">
          <label>收货人</label>
          <input
            v-model="editingAddress.name"
            placeholder="请输入收货人姓名"
            class="form-input"
          />
        </div>
        <div class="form-row">
          <label>手机号</label>
          <input
            v-model="editingAddress.phone"
            type="tel"
            maxlength="11"
            placeholder="请输入手机号"
            class="form-input"
          />
        </div>
        <div class="form-row">
          <label>详细地址</label>
          <textarea
            v-model="editingAddress.address"
            placeholder="请输入详细地址"
            class="form-textarea"
          ></textarea>
        </div>
        <div class="form-row">
          <label>标签</label>
          <input
            v-model="editingAddress.tag"
            placeholder="如：家、公司"
            class="form-input"
          />
        </div>
        <div class="form-row form-row-switch">
          <span>设为默认地址</span>
          <van-switch v-model="editingAddress.is_default" size="24" />
        </div>
      </div>
      <div class="popup-ft">
        <button class="save-addr-btn" @click="saveAddress">保存地址</button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import {
  showToast,
  showSuccessToast,
  showFailToast,
  showLoadingToast,
  closeToast,
  showConfirmDialog,
} from "vant";

const router = useRouter();
const merchant = ref({});
const items = ref([]);
const remark = ref("");
const submitting = ref(false);
const showAddressPopup = ref(false);
const showAddAddress = ref(false);
const chosenAddressId = ref("1");
const address = ref({ name: "", phone: "", detail: "点击选择收货地址" });
const addressList = ref([]);
const editingAddress = ref({
  id: "",
  name: "",
  phone: "",
  address: "",
  tag: "",
  is_default: false,
});

// ---- 动态费用计算 ----
// 打包费：每件商品 ¥0.5
const packagingFee = computed(() => {
  const qty = items.value.reduce((s, i) => s + (i.quantity || 0), 0);
  return Math.max(0, qty * 0.5);
});

// 配送费来自商家数据
const deliveryFee = computed(
  () => parseFloat(merchant.value.delivery_fee) || 0,
);

// 商品小计
const subtotal = computed(() => {
  const total = items.value.reduce(
    (s, i) => s + (parseFloat(i.price) || 0) * (i.quantity || 0),
    0,
  );
  return total.toFixed(2);
});

// 合计
const total = computed(() => {
  const st = parseFloat(subtotal.value) || 0;
  const df = parseFloat(deliveryFee.value) || 0;
  const pf = parseFloat(packagingFee.value) || 0;
  return (st + df + pf).toFixed(2);
});

// 是否达到起送价
const meetsMinPrice = computed(() => {
  const mp = parseFloat(merchant.value.min_price);
  if (!mp) return true;
  return parseFloat(subtotal.value) >= mp;
});

// ---- 返回按钮 ----
function goBack() {
  // 将购物车商品序列化回 Merchant 页面可读取的格式
  if (items.value.length > 0) {
    localStorage.setItem("checkout_restore", JSON.stringify(items.value));
  }
  router.back();
}

// ---- 地址 ----
async function loadAddresses() {
  try {
    const res = await axios.get("/api/user/addresses");
    if (res.data.code === 200) {
      const list = res.data.data;
      addressList.value = list.map((a) => ({
        id: String(a.id),
        name: a.name,
        tel: a.phone,
        address: a.address,
        lng: a.lng,
        lat: a.lat,
        isDefault: a.is_default === 1,
      }));
      const def = list.find((a) => a.is_default) || list[0];
      if (def) {
        address.value = {
          name: def.name,
          phone: def.phone,
          detail: def.address,
          lng: def.lng,
          lat: def.lat,
        };
        chosenAddressId.value = String(def.id);
      }
    }
  } catch (e) {}
}

function onSelectAddress(item) {
  address.value = {
    name: item.name,
    phone: item.tel,
    detail: item.address,
    lng: item.lng || 0,
    lat: item.lat || 0,
  };
  showAddressPopup.value = false;
}

function onEditAddress(item) {
  editingAddress.value = {
    id: item.id,
    name: item.name,
    phone: item.tel,
    address: item.address,
    tag: item.tag || "",
    is_default: item.isDefault || false,
  };
  showAddAddress.value = true;
}

async function saveAddress() {
  if (!editingAddress.value.name || !editingAddress.value.address) {
    showFailToast("请填写完整信息");
    return;
  }

  try {
    const data = {
      name: editingAddress.value.name,
      phone: editingAddress.value.phone,
      address: editingAddress.value.address,
      tag: editingAddress.value.tag,
      is_default: editingAddress.value.is_default ? 1 : 0,
    };

    if (editingAddress.value.id) {
      await axios.put(`/api/user/addresses/${editingAddress.value.id}`, data);
      showSuccessToast("地址更新成功");
    } else {
      await axios.post("/api/user/addresses", data);
      showSuccessToast("地址添加成功");
    }

    showAddAddress.value = false;
    editingAddress.value = {
      id: "",
      name: "",
      phone: "",
      address: "",
      tag: "",
      is_default: false,
    };
    await loadAddresses();
  } catch (e) {
    showFailToast("操作失败");
  }
}

async function deleteAddress(id) {
  try {
    await showConfirmDialog({
      title: '删除地址',
      message: '确定要删除这个地址吗？',
      confirmButtonText: '删除',
      confirmButtonColor: '#C0392B',
    })
  } catch {
    return // 用户取消
  }

  try {
    await axios.delete(`/api/user/addresses/${id}`);
    showSuccessToast("删除成功");
    await loadAddresses();
  } catch (e) {
    showFailToast("删除失败");
  }
}

// ---- 提交订单 ----
async function submitOrder() {
  if (!meetsMinPrice.value) {
    showFailToast("未达到起送价");
    return;
  }
  submitting.value = true;
  showLoadingToast({ message: "提交中…", forbidClick: true });
  try {
    const res = await axios.post("/api/orders", {
      merchant_id: merchant.value.id,
      items: items.value.map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
      })),
      address: address.value.detail,
      address_lng: address.value.lng || 0,
      address_lat: address.value.lat || 0,
      remark: remark.value,
    });
    if (res.data.code === 200) {
      await axios.post(`/api/orders/${res.data.data.order_id}/pay`);
      closeToast();
      showSuccessToast("支付成功");
      localStorage.removeItem("checkout_items");
      localStorage.removeItem("checkout_merchant");
      localStorage.removeItem("checkout_total");
      setTimeout(
        () => router.push(`/order-detail/${res.data.data.order_id}`),
        800,
      );
    } else {
      closeToast();
      showFailToast(res.data.msg || "下单失败");
    }
  } catch (e) {
    closeToast();
    showFailToast("网络错误，请检查后端");
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  const sm = localStorage.getItem("checkout_merchant");
  const si = localStorage.getItem("checkout_items");
  if (sm) merchant.value = JSON.parse(sm);
  if (si) items.value = JSON.parse(si);
  loadAddresses();
});
</script>

<style scoped>
.checkout-page {
  padding-top: 0;
  min-height: 100vh;
  background: var(--clay-page);
  padding-bottom: 120px;
}

/* 顶部导航 */
.checkout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 12px 12px 4px;
  background: var(--clay-card);
  border-bottom: 1px solid var(--clay-border);
  position: sticky;
  top: 0;
  z-index: 50;
}
.back-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--clay-text);
  border-radius: 12px;
  transition: background 0.2s;
}
.back-btn:active {
  background: var(--clay-page);
}
.header-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--clay-text);
}
.header-spacer {
  width: 40px;
}

.section {
  background: var(--clay-card);
  margin: 8px 14px;
  border-radius: 16px;
  padding: 14px 16px;
  border: 1px solid var(--clay-border);
}
.section-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--clay-text);
}
.section-label-sm {
  font-size: 13px;
  font-weight: 600;
  color: var(--clay-text-soft);
  margin-bottom: 10px;
}
.section-sub {
  font-size: 12px;
  color: var(--clay-text-soft);
  margin-top: 4px;
}

.addr-sect {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.addr-icon {
  flex-shrink: 0;
}
.addr-body {
  flex: 1;
  min-width: 0;
}
.addr-line1 {
  display: flex;
  gap: 10px;
  align-items: baseline;
}
.addr-line1 b {
  font-size: 15px;
  color: var(--clay-text);
}
.addr-phone {
  font-size: 13px;
  color: var(--clay-text-soft);
}
.addr-line2 {
  font-size: 13px;
  color: var(--clay-text-soft);
  margin-top: 2px;
}
.addr-arrow {
  color: var(--clay-text-muted);
}

.checkout-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;
}
.checkout-item + .checkout-item {
  border-top: 1px solid var(--clay-divider);
}
.ci-name {
  flex: 1;
  color: var(--clay-text);
}
.ci-qty {
  color: var(--clay-text-soft);
  margin: 0 14px;
}
.ci-price {
  color: var(--clay-brand);
  font-weight: 600;
}

/* 费用明细 */
.fee-section {
  padding-bottom: 10px;
}
.fee-row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  font-size: 14px;
  color: var(--clay-text-soft);
}
.fee-total {
  font-size: 16px;
  font-weight: 600;
  color: var(--clay-text);
}
.total-num {
  color: var(--clay-brand);
  font-size: 22px;
  font-family: Georgia, serif;
  font-weight: 700;
}

.min-price-warn {
  margin-top: 4px;
  padding: 8px 12px;
  background: #fff7e6;
  border-radius: 10px;
  font-size: 12px;
  color: #e6a23c;
  font-weight: 500;
  border: 1px solid #faecd8;
}

.remark-field {
  display: flex;
  align-items: center;
  gap: 10px;
}
.remark-icon {
  color: var(--clay-text-muted);
  font-size: 16px;
}
.remark-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--clay-text);
  outline: none;
  font-family: inherit;
  padding: 4px 0;
}
.remark-input::placeholder {
  color: var(--clay-text-muted);
}

.submit-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  background: var(--clay-card);
  padding: 16px;
  border-top: 1px solid var(--clay-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}
.submit-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 14px;
  color: var(--clay-text-soft);
}
.submit-price {
  font-size: 28px;
  font-weight: 700;
  color: var(--clay-brand);
  font-family: Georgia, serif;
}
.submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #c84b31, #a13d28);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.06em;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s var(--spring);
  box-shadow: 0 4px 20px rgba(200, 75, 49, 0.25);
}
.submit-btn:active {
  transform: scale(0.97);
}
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.popup-hd {
  text-align: center;
  padding: 18px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--clay-divider);
}

.popup-ft {
  padding: 14px;
  border-top: 1px solid var(--clay-divider);
  background: #fff;
}

.add-addr-btn,
.save-addr-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #c84b31, #a13d28);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s var(--spring);
  box-shadow: 0 4px 16px rgba(200, 75, 49, 0.3);
}

.add-addr-btn:hover,
.save-addr-btn:hover {
  box-shadow: 0 6px 20px rgba(200, 75, 49, 0.4);
}

.add-addr-btn:active,
.save-addr-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(200, 75, 49, 0.2);
}

.addr-form {
  padding: 20px;
  background: #fff;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.form-row label {
  font-size: 14px;
  font-weight: 600;
  color: var(--clay-text);
  padding-left: 4px;
}

.form-input {
  padding: 14px 16px;
  border: 2px solid var(--clay-border);
  border-radius: 14px;
  font-size: 15px;
  color: var(--clay-text);
  outline: none;
  font-family: inherit;
  transition: all 0.3s var(--spring);
  background: #fafafa;
}

.form-input:focus {
  border-color: var(--clay-brand);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(200, 75, 49, 0.1);
}

.form-input::placeholder {
  color: var(--clay-text-muted);
}

.form-textarea {
  padding: 14px 16px;
  border: 2px solid var(--clay-border);
  border-radius: 14px;
  font-size: 15px;
  color: var(--clay-text);
  outline: none;
  font-family: inherit;
  min-height: 100px;
  resize: none;
  transition: all 0.3s var(--spring);
  background: #fafafa;
}

.form-textarea:focus {
  border-color: var(--clay-brand);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(200, 75, 49, 0.1);
}

.form-textarea::placeholder {
  color: var(--clay-text-muted);
}

.form-row-switch {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 12px;
}

.form-row-switch span {
  font-size: 15px;
  color: var(--clay-text);
  font-weight: 500;
}

/* 地址选择列表优化 */
.address-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 16px;
  border: 2px solid transparent;
  transition: all 0.3s var(--spring);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.address-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.address-item.selected {
  border-color: var(--clay-brand);
  background: linear-gradient(
    135deg,
    rgba(200, 75, 49, 0.05),
    rgba(200, 75, 49, 0.02)
  );
}

.address-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.address-item-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--clay-text);
  margin-right: 12px;
}

.address-item-phone {
  font-size: 14px;
  color: var(--clay-text-muted);
}

.address-item-tag {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  background: var(--clay-brand-light);
  color: var(--clay-brand);
  font-weight: 500;
}

.address-item-detail {
  font-size: 14px;
  color: var(--clay-text);
  line-height: 1.6;
  padding-left: 4px;
}

.address-item-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--clay-divider);
}

.address-item-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.address-item-btn.edit {
  background: #f5f5f5;
  color: var(--clay-text);
}

.address-item-btn.delete {
  background: #fff5f5;
  color: #ff4757;
}

.address-item-btn:hover {
  opacity: 0.85;
}

.address-item-btn:active {
  transform: scale(0.96);
}

.address-list-container {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.address-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.address-item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.address-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #c84b31, #a13d28);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.empty-address {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--clay-text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
}
</style>
