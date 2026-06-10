import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { io } from 'socket.io-client'
import { showToast } from 'vant'

export const useAppStore = defineStore('app', () => {
  // ========== 用户状态 ==========
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || 'user')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const isLoggedIn = computed(() => !!token.value)

  // ========== SocketIO ==========
  let socket = null

  function connectSocket() {
    if (!token.value) return
    socket = io('/', {
      query: { token: token.value },
      transports: ['websocket', 'polling']
    })
    // 全局暴露 socket 实例，供组件监听事件
    window._socketInstance = socket

    socket.on('connect', () => {
      console.log('[Socket] 已连接')
    })

    socket.on('disconnect', () => {
      console.log('[Socket] 断开连接')
    })

    socket.on('new_order', (data) => {
      console.log('[Socket] 新订单通知:', data)
      showToast({
        message: `新订单！订单号 #${data.id}`,
        duration: 3000,
      })
      // 播放提示音
      playNotificationSound()
    })

    socket.on('order_status_changed', (data) => {
      console.log('[Socket] 订单状态更新:', data)
      const statusMap = {
        1: '订单已支付，等待商家接单',
        2: '商家已接单，准备出餐',
        3: '骑手已取餐，正在配送中',
        4: '订单已完成',
        '-1': '订单已被取消'
      }
      showToast(statusMap[data.status] || '订单状态已更新')
    })

    socket.on('location_changed', (data) => {
      console.log('[Socket] 骑手位置更新:', data)
      // 触发自定义事件供地图组件监听
      window.dispatchEvent(new CustomEvent('rider_location_changed', {
        detail: data
      }))
    })
  }

  function disconnectSocket() {
    if (socket) {
      socket.disconnect()
      socket = null
      window._socketInstance = null
    }
  }

  function playNotificationSound() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.frequency.value = 800
      gain.gain.value = 0.3
      osc.start()
      osc.stop(ctx.currentTime + 0.3)
    } catch (e) {
      // 忽略音频播放错误
    }
  }

  // ========== 登录 ==========
  async function login(phone, code) {
    try {
      const res = await axios.post('/api/user/login', { phone, code })
      if (res.data.code === 200) {
        const { token: t, user } = res.data.data
        token.value = t
        role.value = 'user'
        userInfo.value = user
        localStorage.setItem('token', t)
        localStorage.setItem('role', 'user')
        localStorage.setItem('userInfo', JSON.stringify(user))
        connectSocket()
        return { success: true }
      }
      return { success: false, msg: res.data.msg || '登录失败' }
    } catch (e) {
      const msg = e.response?.data?.msg || e.message || '网络错误，请检查后端是否启动'
      return { success: false, msg }
    }
  }

  async function merchantLogin(username, password) {
    try {
      const res = await axios.post('/api/merchant/login', { username, password })
      if (res.data.code === 200) {
        const { token: t, merchant } = res.data.data
        token.value = t
        role.value = 'merchant'
        userInfo.value = merchant
        localStorage.setItem('token', t)
        localStorage.setItem('role', 'merchant')
        localStorage.setItem('userInfo', JSON.stringify(merchant))
        connectSocket()
        return { success: true, data: merchant }
      }
      return { success: false, msg: res.data.msg || '登录失败' }
    } catch (e) {
      const msg = e.response?.data?.msg || e.message || '网络错误，请检查后端是否启动'
      return { success: false, msg }
    }
  }

  async function riderLogin(username, password) {
    try {
      const res = await axios.post('/api/rider/login', { username, password })
      if (res.data.code === 200) {
        const { token: t, rider } = res.data.data
        token.value = t
        role.value = 'rider'
        userInfo.value = rider
        localStorage.setItem('token', t)
        localStorage.setItem('role', 'rider')
        localStorage.setItem('userInfo', JSON.stringify(rider))
        connectSocket()
        return { success: true }
      }
      return { success: false, msg: res.data.msg || '登录失败' }
    } catch (e) {
      const msg = e.response?.data?.msg || e.message || '网络错误，请检查后端是否启动'
      return { success: false, msg }
    }
  }

  function logout() {
    // 清空内存状态
    token.value = ''
    role.value = 'user'
    userInfo.value = null

    // 精确清理 localStorage（只删认证和购物车缓存，保留其他数据）
    const keysToRemove = [
      'token', 'role', 'userInfo',
      'checkout_items', 'checkout_merchant', 'checkout_total'
    ]
    keysToRemove.forEach(key => localStorage.removeItem(key))

    // 断开 WebSocket
    disconnectSocket()
  }

  // ========== Axios 拦截器 ==========
  axios.interceptors.request.use(config => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  })

  axios.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        logout()
        window.location.hash = '#/login'
      }
      return Promise.reject(error)
    }
  )

  return {
    token, role, userInfo, isLoggedIn,
    connectSocket, disconnectSocket,
    login, merchantLogin, riderLogin, logout
  }
})
