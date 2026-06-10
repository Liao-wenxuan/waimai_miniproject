<template>
  <div class="login-page">
    <!-- 有机背景图形 -->
    <div class="login-bg-art">
      <div class="bg-blob bg-blob-1"></div>
      <div class="bg-blob bg-blob-2"></div>
      <div class="bg-blob bg-blob-3"></div>
    </div>

    <div class="login-content">
      <!-- 品牌标识 -->
      <div class="brand-block">
        <div class="brand-mark">
          <svg viewBox="0 0 80 80" fill="none">
            <circle
              cx="40"
              cy="40"
              r="36"
              stroke="#fff"
              stroke-width="2.5"
              opacity="0.4"
            />
            <path
              d="M40 16c-8 0-16 4-20 12s-2 18 4 24c4 4 10 6 16 4s10-8 10-14c0-6-4-10-10-10s-10 4-10 10c0 4 2 8 6 10"
              stroke="#fff"
              stroke-width="2.5"
              stroke-linecap="round"
              fill="none"
            />
          </svg>
        </div>
        <h1 class="brand-name">Clay</h1>
        <p class="brand-tagline">从炉火到餐桌的温度</p>
      </div>

      <!-- 角色切换 — 药丸风格 -->
      <div class="role-switch">
        <button
          v-for="tab in roles"
          :key="tab.key"
          :class="['role-btn', { active: loginType === tab.key }]"
          @click="switchRole(tab.key)"
        >
          <span class="role-emoji">{{ tab.emoji }}</span>
          {{ tab.label }}
        </button>
      </div>

      <!-- 表单卡片 -->
      <div class="login-card">
        <!-- 用户登录 -->
        <template v-if="loginType === 'user'">
          <div class="field-group">
            <div class="clay-field">
              <span class="field-icon">📱</span>
              <input
                v-model="phone"
                type="tel"
                maxlength="11"
                placeholder="手机号码"
                class="field-input"
              />
            </div>
            <div class="clay-field code-field">
              <span class="field-icon">🔐</span>
              <input
                v-model="code"
                type="digit"
                maxlength="6"
                placeholder="验证码"
                class="field-input"
              />
              <span class="field-sep"></span>
              <button
                class="code-btn"
                :disabled="!!countdown"
                @click="sendCode"
              >
                {{ countdown ? `${countdown}s` : "发送" }}
              </button>
            </div>
          </div>
          <div class="login-hint">
            <span class="hint-dot">●</span> 验证码：<b>123456</b> ·
            输入任意11位手机号
          </div>
        </template>

        <!-- 商家/骑手登录 -->
        <template v-else>
          <div class="field-group">
            <div class="clay-field">
              <span class="field-icon">👤</span>
              <input
                v-model="username"
                placeholder="账号"
                class="field-input"
              />
            </div>
            <div class="clay-field">
              <span class="field-icon">🔑</span>
              <input
                v-model="password"
                type="password"
                placeholder="密码"
                class="field-input"
              />
            </div>
          </div>
          <div class="login-hint">
            <span class="hint-dot">●</span> 测试：<b>{{
              loginType === "merchant" ? "merchant" : "rider"
            }}</b>
            / <b>123456</b>
          </div>
        </template>

        <button
          class="clay-btn-primary"
          :disabled="loading"
          @click="handleLogin"
        >
          <span v-if="loading" class="btn-spinner"></span>
          <span v-else>开始使用</span>
        </button>
      </div>
    </div>

    <!-- 登录成功弹窗 -->
    <Teleport to="body">
      <transition name="modal-fade">
        <div
          v-if="showSuccess"
          class="success-overlay"
          @click.self="showSuccess = false"
        >
          <div class="success-modal">
            <div class="success-ring">
              <svg viewBox="0 0 60 60" class="success-check">
                <circle
                  cx="30"
                  cy="30"
                  r="28"
                  fill="none"
                  stroke="var(--clay-success)"
                  stroke-width="3"
                  stroke-dasharray="176"
                  stroke-dashoffset="176"
                  class="check-circle"
                />
                <path
                  d="M18 30l8 8 16-16"
                  fill="none"
                  stroke="var(--clay-success)"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-dasharray="40"
                  stroke-dashoffset="40"
                  class="check-path"
                />
              </svg>
            </div>
            <div class="success-title">欢迎回来</div>
            <div class="success-name">{{ successInfo.nickname }}</div>
            <div class="success-role">{{ successInfo.roleLabel }}</div>
            <div class="success-redirect">
              <span class="redirect-dot"></span>
              {{ successInfo.redirectHint }}
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "../stores/index";
import { showToast, showSuccessToast, showFailToast } from "vant";

const router = useRouter();
const store = useAppStore();

const loginType = ref("user");
const roles = [
  { key: "user", label: "用户", emoji: "🍽️" },
  { key: "merchant", label: "商家", emoji: "🏪" },
  { key: "rider", label: "骑手", emoji: "🛵" },
];

const phone = ref("13800138000");
const code = ref("");
const username = ref("");
const password = ref("");
const loading = ref(false);
const countdown = ref(0);

const showSuccess = ref(false);
const successInfo = reactive({ nickname: "", roleLabel: "", redirectHint: "" });

function switchRole(key) {
  loginType.value = key;
}

function sendCode() {
  showSuccessToast("验证码已发送");
  countdown.value = 60;
  const timer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) clearInterval(timer);
  }, 1000);
}

function showLoginSuccess() {
  const cfg = {
    user: { label: "美食家", hint: "正在进入首页…" },
    merchant: { label: "商家", hint: "正在进入订单管理…" },
    rider: { label: "骑手", hint: "正在进入工作台…" },
  }[loginType.value] || { label: "用户", hint: "跳转中…" };

  const info = store.userInfo;
  successInfo.nickname =
    info?.nickname ||
    info?.name ||
    (loginType.value === "user" ? "美食家" : username.value || "用户");
  successInfo.roleLabel = cfg.label;
  successInfo.redirectHint = cfg.hint;

  showSuccess.value = true;
  setTimeout(() => {
    const routes = {
      user: "/home",
      merchant: "/merchant-orders",
      rider: "/rider-orders",
    };
    router.push(routes[loginType.value] || "/home");
  }, 1600);
}

async function handleLogin() {
  loading.value = true;
  try {
    let result;
    if (loginType.value === "user") {
      if (!phone.value) {
        showFailToast("请输入手机号");
        loading.value = false;
        return;
      }
      result = await store.login(phone.value, code.value);
    } else if (loginType.value === "merchant") {
      result = await store.merchantLogin(
        username.value || "merchant",
        password.value || "123456",
      );
    } else {
      result = await store.riderLogin(
        username.value || "rider",
        password.value || "123456",
      );
    }
    if (result.success) showLoginSuccess();
    else showFailToast(result.msg || "登录失败");
  } catch (e) {
    const msg = e?.response?.data?.msg || e?.message || "网络错误，请检查后端";
    showFailToast(msg);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: linear-gradient(170deg, #c84b31 0%, #8b3a2a 60%, #5c2618 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 40px 24px;
}

/* 背景有机图形 */
.login-bg-art {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.15;
}
.bg-blob-1 {
  width: 300px;
  height: 300px;
  background: #e8a87c;
  top: -80px;
  right: -100px;
  animation: float-blob 8s ease-in-out infinite;
}
.bg-blob-2 {
  width: 200px;
  height: 200px;
  background: #d4a853;
  bottom: 10%;
  left: -60px;
  animation: float-blob 6s ease-in-out 2s infinite;
}
.bg-blob-3 {
  width: 160px;
  height: 160px;
  background: #fceae4;
  top: 50%;
  right: -40px;
  animation: float-blob 7s ease-in-out 4s infinite;
}
@keyframes float-blob {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(10px, -20px) scale(1.08);
  }
  66% {
    transform: translate(-10px, 10px) scale(0.94);
  }
}

.login-content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 360px;
}

/* 品牌 */
.brand-block {
  text-align: center;
  margin-bottom: 40px;
}
.brand-mark {
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
}
.brand-name {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 40px;
  font-weight: 400;
  color: #fff;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}
.brand-tagline {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.12em;
}

/* 角色切换 */
.role-switch {
  display: flex;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 28px;
  padding: 5px;
  margin-bottom: 28px;
  backdrop-filter: blur(8px);
}
.role-btn {
  flex: 1;
  padding: 10px 8px;
  border: none;
  border-radius: 24px;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s var(--spring);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-family: inherit;
}
.role-btn.active {
  background: #fff;
  color: var(--clay-brand);
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
.role-emoji {
  font-size: 16px;
}

/* 表单卡片 */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 28px 22px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}

.clay-field {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fdf8f0;
  border-radius: 14px;
  padding: 4px 16px;
  border: 1px solid #ebe3d6;
  transition: all 0.25s ease;
}
.clay-field:focus-within {
  border-color: var(--clay-brand);
  box-shadow: 0 0 0 3px var(--clay-brand-light);
}
.field-icon {
  font-size: 18px;
  flex-shrink: 0;
}
.field-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  color: var(--clay-text);
  outline: none;
  padding: 12px 0;
  font-family: inherit;
}
.field-input::placeholder {
  color: var(--clay-text-muted);
}

.code-field {
  padding-right: 0;
}

.field-sep {
  width: 1px;
  height: 20px;
  background: var(--clay-border);
  flex-shrink: 0;
  margin: 0 2px;
}

.code-btn {
  flex-shrink: 0;
  border: none;
  background: transparent;
  color: var(--clay-brand);
  font-size: 13px;
  font-weight: 600;
  padding: 4px 6px 4px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  white-space: nowrap;
  line-height: 1;
}
.code-btn:active {
  background: var(--clay-brand-light);
}
.code-btn:disabled {
  color: var(--clay-text-muted);
  cursor: not-allowed;
}

.login-hint {
  font-size: 12px;
  color: var(--clay-text-soft);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.hint-dot {
  color: var(--clay-accent);
  font-size: 8px;
}

/* 主按钮 */
.clay-btn-primary {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #c84b31 0%, #a13d28 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: all 0.3s var(--spring);
  font-family: inherit;
  box-shadow: 0 4px 20px rgba(200, 75, 49, 0.25);
}
.clay-btn-primary:active {
  transform: scale(0.97);
  box-shadow: 0 2px 10px rgba(200, 75, 49, 0.2);
}
.clay-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 成功弹窗 */
.success-overlay {
  position: fixed;
  inset: 0;
  background: rgba(44, 36, 22, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 40px;
}
.success-modal {
  background: #fff;
  border-radius: 28px;
  padding: 44px 32px 32px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  max-width: 300px;
  width: 100%;
  animation: modal-pop 0.4s var(--spring) both;
}
@keyframes modal-pop {
  from {
    transform: scale(0.8) translateY(30px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}
.success-ring {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
}
.check-circle {
  animation: draw-circle 0.6s var(--ease-out) 0.1s both;
}
.check-path {
  animation: draw-check 0.4s var(--ease-out) 0.5s both;
}
@keyframes draw-circle {
  to {
    stroke-dashoffset: 0;
  }
}
@keyframes draw-check {
  to {
    stroke-dashoffset: 0;
  }
}

.success-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--clay-text);
  margin-bottom: 6px;
}
.success-name {
  font-size: 15px;
  color: var(--clay-brand);
  font-weight: 600;
  margin-bottom: 12px;
}
.success-role {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 18px;
  border-radius: 20px;
  background: var(--clay-brand-light);
  color: var(--clay-brand);
  margin-bottom: 20px;
}
.success-redirect {
  font-size: 13px;
  color: var(--clay-text-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.redirect-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--clay-success);
  animation: pulse-dot 1s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

.modal-fade-enter-active {
  transition: opacity 0.3s ease;
}
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
