<template>
  <div class="profile-page">
    <!-- 头部 -->
    <div class="profile-header">
      <div class="ph-blob-bg"></div>
      <div class="ph-content">
        <div class="ph-avatar">
          <img :src="user.avatar || 'https://img.yzcdn.cn/vant/cat.jpeg'" />
        </div>
        <div class="ph-name">{{ user.nickname || "美食家" }}</div>
        <div class="ph-phone">{{ user.phone || "未绑定手机" }}</div>
      </div>
    </div>

    <!-- 快捷卡片 -->
    <div class="quick-cards">
      <div class="qc-card balance" @click="showToast('余额功能开发中')">
        <span class="qc-icon">💰</span>
        <div class="qc-info">
          <div class="qc-label">账户余额</div>
          <div class="qc-value">¥{{ user.balance || "0.00" }}</div>
        </div>
      </div>
      <div class="qc-card orders" @click="$router.push('/orders')">
        <span class="qc-icon">📋</span>
        <div class="qc-info">
          <div class="qc-label">我的订单</div>
          <div class="qc-value">查看全部 →</div>
        </div>
      </div>
    </div>

    <!-- 菜单 -->
    <div class="menu-section">
      <div class="menu-item" @click="showNicknameEdit = true">
        <span class="mi-icon" style="background: #e8f5e9">👤</span>
        <span class="mi-label">修改昵称</span>
        <span class="mi-arrow">→</span>
      </div>
      <div class="menu-item" @click="showAddressManager = true">
        <span class="mi-icon" style="background: var(--clay-brand-light)"
          >📍</span
        >
        <span class="mi-label">我的地址</span>
        <span class="mi-arrow">→</span>
      </div>
      <div class="menu-item" @click="$router.push('/favorites')">
        <span class="mi-icon" style="background: var(--clay-danger-bg)">♥</span>
        <span class="mi-label">我的收藏</span>
        <span class="mi-arrow">→</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="$router.push('/help')">
        <span class="mi-icon" style="background: var(--clay-success-bg)"
          >❓</span
        >
        <span class="mi-label">帮助中心</span>
        <span class="mi-arrow">→</span>
      </div>
      <div class="menu-item" @click="$router.push('/settings')">
        <span class="mi-icon" style="background: #f5f2ed">⚙</span>
        <span class="mi-label">设置</span>
        <span class="mi-arrow">→</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="showAdminDialog = true">
        <span class="mi-icon" style="background: #1a1a2e">🛡️</span>
        <span class="mi-label">管理后台</span>
        <span class="mi-arrow">→</span>
      </div>
    </div>

    <!-- 修改昵称弹窗 -->
    <van-popup v-model:show="showNicknameEdit" position="center" round>
      <div class="nickname-edit">
        <div class="ne-title">修改昵称</div>
        <van-field
          v-model="newNickname"
          placeholder="请输入新昵称"
          maxlength="20"
          @confirm="saveNickname"
        />
        <div class="ne-actions">
          <van-button plain @click="showNicknameEdit = false">取消</van-button>
          <van-button type="primary" @click="saveNickname">保存</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 退出 -->
    <div class="logout-area">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>

    <!-- 管理后台验证弹窗 -->
    <van-popup v-model:show="showAdminDialog" position="center" round :style="{ width: '85%', maxWidth: '360px' }">
      <div class="admin-dialog">
        <div class="ad-header">
          <span class="ad-icon">🛡️</span>
          <h3>管理后台</h3>
          <p>请输入管理员密码进行验证</p>
        </div>
        <div class="ad-body">
          <input
            v-model="adminPassword"
            type="password"
            placeholder="请输入管理员密码"
            class="ad-input"
            @keyup.enter="verifyAdmin"
          />
        </div>
        <div class="ad-actions">
          <van-button plain @click="showAdminDialog = false">取消</van-button>
          <van-button type="primary" :loading="adminLoading" @click="verifyAdmin">验证进入</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 地址管理 -->
    <van-action-sheet
      v-model:show="showAddressManager"
      title="我的地址"
      close-on-popup-action
    >
      <div class="addr-sheet">
        <div class="addr-list">
          <div
            v-for="addr in addressList"
            :key="addr.id"
            :class="['addr-card', { 'is-default': addr.is_default }]"
          >
            <div class="ac-info" @click="selectAddress(addr)">
              <div class="ac-top">
                <b>{{ addr.name }}</b>
                <span class="ac-phone">{{ addr.phone }}</span>
                <span v-if="addr.tag" class="ac-tag">{{ addr.tag }}</span>
                <span v-if="addr.is_default" class="ac-default">默认</span>
              </div>
              <div class="ac-text">{{ addr.address }}</div>
            </div>
            <div class="ac-actions">
              <button class="ac-edit" @click="editAddress(addr)">✎</button>
              <button class="ac-del" @click="deleteAddress(addr.id)">✕</button>
            </div>
          </div>
          <van-empty
            v-if="addressList.length === 0"
            description="还没有添加地址"
          />
        </div>
        <button class="addr-add-btn" @click="startAddAddress">
          + 添加新地址
        </button>
      </div>
    </van-action-sheet>

    <!-- 地址编辑弹窗 -->
    <van-popup
      v-model:show="showAddressForm"
      position="bottom"
      round
      :style="{ maxHeight: '80%' }"
      closeable
      :title="isEditing ? '编辑地址' : '添加地址'"
    >
      <div class="addr-form">
        <van-form @submit="saveAddress">
          <div class="af-search">
            <van-search
              v-model="searchQuery"
              placeholder="搜索地址（小区/大厦/街道）"
              @search="searchAddress"
              @input="onSearchInput"
              clearable
              shape="round"
            />
            <div class="af-results" v-if="searchResults.length > 0">
              <div
                v-for="(item, idx) in searchResults"
                :key="idx"
                class="af-result"
                @click="pickSearchResult(item)"
              >
                <span>📍</span>
                <div class="afr-info">
                  <div class="afr-name">{{ item.name }}</div>
                  <div class="afr-addr">{{ item.address }}</div>
                </div>
                <span
                  v-if="selectedPoi && selectedPoi.id === item.id"
                  class="afr-check"
                  >✓</span
                >
              </div>
            </div>
            <div class="af-selected" v-if="selectedPoi">
              <span>📍</span> {{ selectedPoi.address || selectedPoi.name }}
              <button class="af-clear" @click="selectedPoi = null">✕</button>
            </div>
          </div>
          <van-cell-group inset>
            <van-field
              v-model="form.name"
              label="收件人"
              placeholder="姓名"
              :rules="[{ required: true }]"
            />
            <van-field
              v-model="form.phone"
              label="电话"
              placeholder="手机号"
              :rules="[
                { required: true },
                { pattern: /^1\d{10}$/, message: '请输入正确手机号' },
              ]"
            />
            <van-field
              v-model="form.address"
              label="详细地址"
              placeholder="门牌号/楼栋"
            />
            <van-field name="tag" label="标签">
              <template #input>
                <div class="tag-row">
                  <span
                    v-for="t in tags"
                    :key="t"
                    :class="['tag-chip', { active: form.tag === t }]"
                    @click="form.tag = t"
                    >{{ t }}</span
                  >
                </div>
              </template>
            </van-field>
          </van-cell-group>
          <div style="margin: 16px">
            <van-button round block type="primary" native-type="submit">{{
              isEditing ? "保存" : "添加"
            }}</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/index";
import axios from "axios";
import { showToast, showFailToast, showDialog, showSuccessToast } from "vant";

const router = useRouter();
const store = useAppStore();
const user = ref({});

const showNicknameEdit = ref(false);
const newNickname = ref("");
const showAdminDialog = ref(false);
const adminPassword = ref("");
const adminLoading = ref(false);
const showAddressManager = ref(false);
const addressList = ref([]);
const showAddressForm = ref(false);
const isEditing = ref(false);
const editingId = ref(null);
const searchQuery = ref("");
const searchResults = ref([]);
const selectedPoi = ref(null);
const tags = ["家", "公司", "学校"];
const form = reactive({ name: "", phone: "", address: "", tag: "" });
let searchTimer = null,
  placeSearch = null;

async function loadAddresses() {
  try {
    const r = await axios.get("/api/user/addresses");
    if (r.data.code === 200) addressList.value = r.data.data;
  } catch (e) {}
}
function selectAddress(addr) {
  showAddressManager.value = false;
  showToast("已选择: " + addr.address);
}
function startAddAddress() {
  isEditing.value = false;
  editingId.value = null;
  form.name = store.userInfo?.phone
    ? `用户${store.userInfo.phone.slice(-4)}`
    : "";
  form.phone = store.userInfo?.phone || "";
  form.address = "";
  form.tag = "";
  selectedPoi.value = null;
  searchQuery.value = "";
  searchResults.value = [];
  showAddressForm.value = true;
}
function editAddress(addr) {
  isEditing.value = true;
  editingId.value = addr.id;
  form.name = addr.name;
  form.phone = addr.phone;
  form.address = addr.address;
  form.tag = addr.tag || "";
  selectedPoi.value = {
    id: addr.id,
    name: "",
    address: addr.address,
    lng: addr.lng,
    lat: addr.lat,
  };
  searchQuery.value = "";
  searchResults.value = [];
  showAddressForm.value = true;
}
async function deleteAddress(id) {
  showDialog({
    title: "删除地址",
    message: "确定删除？",
    showCancelButton: true,
  })
    .then(async () => {
      try {
        await axios.delete(`/api/user/addresses/${id}`);
        showSuccessToast("已删除");
        loadAddresses();
      } catch {
        showFailToast("删除失败");
      }
    })
    .catch(() => {});
}
function initPlaceSearch() {
  if (window.AMap && !placeSearch)
    placeSearch = new AMap.PlaceSearch({
      type: "poi",
      pageSize: 20,
      pageIndex: 1,
      cityLimit: false,
    });
}
function searchAddress(q) {
  if (!q.trim()) {
    searchResults.value = [];
    return;
  }
  initPlaceSearch();
  if (placeSearch)
    placeSearch.search(q, (status, result) => {
      if (status === "complete" && result.poiList?.pois)
        searchResults.value = result.poiList.pois.slice(0, 10).map((p) => ({
          id: p.id,
          name: p.name,
          address: p.pname + p.cityname + p.adname + p.address,
          lng: p.location.lng,
          lat: p.location.lat,
        }));
      else searchResults.value = [];
    });
}
function onSearchInput(v) {
  clearTimeout(searchTimer);
  if (!v.trim()) {
    searchResults.value = [];
    return;
  }
  searchTimer = setTimeout(() => searchAddress(v), 400);
}
function pickSearchResult(item) {
  selectedPoi.value = item;
  form.address = item.address;
  searchResults.value = [];
  searchQuery.value = item.name;
}
async function saveAddress() {
  const payload = {
    name: form.name,
    phone: form.phone,
    address: form.address,
    tag: form.tag || "",
    lng: selectedPoi.value?.lng || 0,
    lat: selectedPoi.value?.lat || 0,
    is_default: addressList.value.length === 0 ? 1 : 0,
  };
  try {
    if (isEditing.value) {
      await axios.put(`/api/user/addresses/${editingId.value}`, payload);
      showSuccessToast("已更新");
    } else {
      await axios.post("/api/user/addresses", payload);
      showSuccessToast("已添加");
    }
    showAddressForm.value = false;
    loadAddresses();
  } catch (e) {
    showFailToast("保存失败");
  }
}
async function saveNickname() {
  if (!newNickname.value.trim()) {
    showFailToast("请输入昵称");
    return;
  }
  try {
    const res = await axios.put("/api/user/profile", {
      nickname: newNickname.value,
    });
    if (res.data.code === 200) {
      showSuccessToast("修改成功");
      user.value.nickname = newNickname.value;
      store.userInfo = { ...store.userInfo, nickname: newNickname.value };
      showNicknameEdit.value = false;
    } else {
      showFailToast(res.data.msg || "修改失败");
    }
  } catch (e) {
    showFailToast("修改失败");
  }
}
async function verifyAdmin() {
  if (!adminPassword.value.trim()) {
    showFailToast("请输入管理员密码");
    return;
  }
  adminLoading.value = true;
  try {
    const res = await axios.post("/api/admin/login", {
      username: "admin",
      password: adminPassword.value.trim(),
    });
    if (res.data.code === 200) {
      // 保存 admin token 和 role
      localStorage.setItem("token", res.data.data.token);
      localStorage.setItem("role", "admin");
      localStorage.setItem("userInfo", JSON.stringify(res.data.data.admin));
      showSuccessToast("验证成功，正在跳转...");
      adminPassword.value = "";
      showAdminDialog.value = false;
      setTimeout(() => {
        window.location.href = "/#/admin";
      }, 800);
    } else {
      showFailToast(res.data.msg || "密码错误");
    }
  } catch (e) {
    showFailToast("验证失败，请检查网络");
  } finally {
    adminLoading.value = false;
  }
}

async function loadProfile() {
  try {
    const r = await axios.get("/api/user/profile");
    if (r.data.code === 200) user.value = r.data.data;
  } catch (e) {
    user.value = store.userInfo || { phone: "138****0000", nickname: "美食家" };
  }
}
function handleLogout() {
  showDialog({
    title: "退出登录",
    message: "确定退出吗？",
    showCancelButton: true,
    confirmButtonText: "退出",
    confirmButtonColor: "#C84B31",
  })
    .then(() => {
      store.logout();
      showSuccessToast("已退出，期待再次光临 👋");
      setTimeout(() => router.push("/login"), 1500);
    })
    .catch(() => {});
}
onMounted(() => {
  loadProfile();
  loadAddresses();
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--clay-page);
  padding-bottom: 30px;
}

/* 头部 Blob */
.profile-header {
  position: relative;
  padding: 40px 20px 50px;
  text-align: center;
  color: #fff;
  overflow: hidden;
}
.ph-blob-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, #c84b31 0%, #8b3a2a 60%, #5c2618 100%);
  border-radius: 0 0 50% 50% / 0 0 38% 35%;
}
.ph-content {
  position: relative;
  z-index: 1;
}
.ph-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.4);
  padding: 3px;
  margin: 0 auto 14px;
}
.ph-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
}
.ph-name {
  font-size: 22px;
  font-weight: 700;
}
.ph-phone {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

/* 快捷卡片 */
.quick-cards {
  display: flex;
  gap: 10px;
  margin: -18px 16px 18px;
  position: relative;
  z-index: 2;
}
.qc-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--clay-card);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid var(--clay-border);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: all 0.2s var(--spring);
}
.qc-card:active {
  transform: scale(0.97);
}
.qc-icon {
  font-size: 24px;
}
.qc-label {
  font-size: 12px;
  color: var(--clay-text-soft);
}
.qc-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--clay-text);
}
.balance .qc-value {
  color: var(--clay-brand);
}

/* 菜单 */
.menu-section {
  margin: 0 16px;
  background: var(--clay-card);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--clay-border);
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.menu-item:active {
  background: var(--clay-card-warm);
}
.menu-item + .menu-item {
  border-top: 1px solid var(--clay-divider);
}
.menu-divider {
  height: 8px;
  background: var(--clay-page);
}
.mi-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.mi-label {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--clay-text);
}
.mi-arrow {
  color: var(--clay-text-muted);
}

/* 退出 */
.logout-area {
  padding: 30px 20px;
}
.logout-btn {
  width: 100%;
  padding: 14px;
  border: 1px solid var(--clay-border);
  border-radius: 16px;
  background: var(--clay-card);
  color: var(--clay-text-soft);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s ease;
}
.logout-btn:active {
  background: var(--clay-danger-bg);
  color: var(--clay-danger);
  border-color: var(--clay-danger);
}

/* 地址管理 */
.addr-sheet {
  max-height: 60vh;
  overflow-y: auto;
  padding: 0 16px 20px;
}
.addr-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.addr-card {
  display: flex;
  align-items: center;
  background: #fdf8f0;
  border-radius: 14px;
  padding: 14px;
  border: 1px solid var(--clay-border);
}
.addr-card.is-default {
  border-color: var(--clay-brand);
  background: var(--clay-brand-light);
}
.ac-info {
  flex: 1;
  cursor: pointer;
}
.ac-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.ac-top b {
  font-size: 15px;
}
.ac-phone {
  font-size: 13px;
  color: var(--clay-text-soft);
}
.ac-tag,
.ac-default {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 10px;
}
.ac-tag {
  background: var(--clay-info-bg);
  color: var(--clay-info);
}
.ac-default {
  background: var(--clay-brand-light);
  color: var(--clay-brand);
}
.ac-text {
  font-size: 13px;
  color: var(--clay-text-soft);
}
.ac-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-left: 8px;
}
.ac-edit,
.ac-del {
  border: none;
  background: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  color: var(--clay-text-soft);
}
.ac-del:active {
  color: var(--clay-danger);
}
.addr-add-btn {
  width: 100%;
  margin-top: 12px;
  padding: 14px;
  border: 2px dashed var(--clay-border);
  border-radius: 16px;
  background: transparent;
  color: var(--clay-brand);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.addr-add-btn:active {
  background: var(--clay-brand-light);
}

/* 地址表单 */
.addr-form {
  padding: 8px 0;
}
.af-search {
  padding: 0 16px;
  margin-bottom: 12px;
}
.af-results {
  max-height: 180px;
  overflow-y: auto;
  background: var(--clay-card);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
}
.af-result {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-bottom: 1px solid var(--clay-divider);
  cursor: pointer;
  font-size: 13px;
}
.af-result:active {
  background: var(--clay-card-warm);
}
.afr-name {
  font-weight: 500;
  color: var(--clay-text);
}
.afr-addr {
  font-size: 11px;
  color: var(--clay-text-soft);
  margin-top: 2px;
}
.afr-check {
  color: var(--clay-success);
  font-weight: 700;
}
.af-selected {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--clay-brand-light);
  border-radius: 10px;
  margin-top: 8px;
  font-size: 13px;
  color: var(--clay-text);
}
.af-clear {
  margin-left: auto;
  border: none;
  background: none;
  color: var(--clay-text-soft);
  cursor: pointer;
  font-size: 14px;
}
.tag-row {
  display: flex;
  gap: 8px;
}
.tag-chip {
  padding: 4px 14px;
  border-radius: 14px;
  background: #f5f2ed;
  font-size: 13px;
  color: var(--clay-text-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}
.tag-chip.active {
  background: var(--clay-brand-light);
  color: var(--clay-brand);
  font-weight: 600;
}

/* 管理后台弹窗 */
.admin-dialog {
  padding: 28px 24px 24px;
}

.ad-header {
  text-align: center;
  margin-bottom: 20px;
}

.ad-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 10px;
}

.ad-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--clay-text);
  margin: 0 0 6px;
}

.ad-header p {
  font-size: 13px;
  color: var(--clay-text-soft);
  margin: 0;
}

.ad-body {
  margin-bottom: 20px;
}

.ad-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid var(--clay-border);
  border-radius: 12px;
  font-size: 16px;
  text-align: center;
  letter-spacing: 4px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.ad-input:focus {
  border-color: var(--clay-brand);
}

.ad-actions {
  display: flex;
  gap: 12px;
}

.ad-actions .van-button {
  flex: 1;
}

/* 修改昵称弹窗 */
.nickname-edit {
  width: 300px;
  padding: 20px;
}
.ne-title {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--clay-text);
}
.ne-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.ne-actions .van-button {
  flex: 1;
}
</style>
