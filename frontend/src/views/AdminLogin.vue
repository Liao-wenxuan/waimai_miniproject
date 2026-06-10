<template>
  <div class="admin-login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">🎛️</div>
        <h1>管理后台</h1>
        <p>外卖平台管理系统</p>
      </div>

      <div class="form-group">
        <label>账号</label>
        <div class="input-wrapper">
          <span class="input-icon">👤</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入账号"
            class="form-input"
            @keyup.enter="handleLogin"
          />
        </div>
      </div>

      <div class="form-group">
        <label>密码</label>
        <div class="input-wrapper">
          <span class="input-icon">🔒</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            class="form-input"
            @keyup.enter="handleLogin"
          />
        </div>
      </div>

      <button
        class="login-btn"
        :disabled="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <div class="demo-info">
        <span>测试账号：admin / admin</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { showToast } from 'vant'

const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.username.trim()) {
    showToast('请输入账号')
    return
  }
  if (!form.password.trim()) {
    showToast('请输入密码')
    return
  }

  loading.value = true
  try {
    const res = await axios.post('/api/admin/login', {
      username: form.username.trim(),
      password: form.password.trim()
    })
    if (res.data.code === 200) {
      localStorage.setItem('token', res.data.data.token)
      localStorage.setItem('role', 'admin')
      showToast('登录成功')
      setTimeout(() => {
        window.location.href = '/#/admin'
      }, 1000)
    } else {
      showToast(res.data.msg || '登录失败')
    }
  } catch (e) {
    showToast('登录失败，请检查网络')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.login-header p {
  font-size: 14px;
  color: #666;
  margin: 8px 0 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: 12px 12px 12px 38px;
  border: 1px solid #d9d9d9;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #0288d1;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #0288d1, #0277bd);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 8px;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-btn:not(:disabled):hover {
  opacity: 0.9;
}

.demo-info {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #999;
}
</style>