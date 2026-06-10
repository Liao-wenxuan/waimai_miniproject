<template>
  <div class="admin-page">
    <!-- 顶部导航 -->
    <div class="admin-header">
      <div class="admin-logo">🍔 外卖平台管理后台</div>
      <div class="header-right">
        <span class="header-user">👤 admin</span>
        <button class="switch-btn" @click="switchToUser">👥 用户端</button>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>

    <div class="admin-body">
      <!-- 侧边栏 -->
      <div class="admin-sidebar">
        <div
          v-for="item in menuItems"
          :key="item.key"
          class="sidebar-item"
          :class="{ active: activeMenu === item.key }"
          @click="activeMenu = item.key"
        >
          <span class="menu-icon">{{ item.icon }}</span>
          <span class="menu-text">{{ item.label }}</span>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="admin-content">
        <!-- ========== 数据统计 ========== -->
        <div v-if="activeMenu === 'statistics'" class="section">
          <h2 class="section-title">📊 数据统计</h2>
          <div class="stats-grid">
            <div class="stat-card blue">
              <div class="stat-value">{{ statistics.today_orders }}</div>
              <div class="stat-label">今日订单</div>
            </div>
            <div class="stat-card green">
              <div class="stat-value">¥{{ statistics.today_amount }}</div>
              <div class="stat-label">今日交易额</div>
            </div>
            <div class="stat-card purple">
              <div class="stat-value">{{ statistics.total_orders }}</div>
              <div class="stat-label">总订单数</div>
            </div>
            <div class="stat-card orange">
              <div class="stat-value">{{ statistics.total_users }}</div>
              <div class="stat-label">总用户数</div>
            </div>
            <div class="stat-card cyan">
              <div class="stat-value">{{ statistics.total_merchants }}</div>
              <div class="stat-label">总商家数</div>
            </div>
            <div class="stat-card pink">
              <div class="stat-value">{{ statistics.total_riders }}</div>
              <div class="stat-label">总骑手数</div>
            </div>
          </div>

          <!-- 近7天趋势 -->
          <div class="sub-section">
            <h3>📈 近7天订单趋势</h3>
            <div class="chart-bar">
              <div class="bar-item" v-for="d in statistics.week_orders" :key="d.date">
                <div class="bar-value">{{ d.count }}</div>
                <div class="bar-fill" :style="{ height: barHeight(d.count, 'orders') + 'px' }"></div>
                <div class="bar-date">{{ d.date }}</div>
              </div>
            </div>
          </div>

          <div class="sub-section">
            <h3>💰 近7天交易额趋势</h3>
            <div class="chart-bar">
              <div class="bar-item" v-for="d in statistics.week_amount" :key="d.date">
                <div class="bar-value">¥{{ d.amount }}</div>
                <div class="bar-fill amount" :style="{ height: barHeight(d.amount, 'amount') + 'px' }"></div>
                <div class="bar-date">{{ d.date }}</div>
              </div>
            </div>
          </div>

          <!-- 订单状态分布 -->
          <div class="two-col">
            <div class="sub-section">
              <h3>📋 订单状态分布</h3>
              <div class="status-list">
                <div class="status-row" v-for="s in statistics.status_breakdown" :key="s.status">
                  <span class="status-label">{{ s.label }}</span>
                  <span class="status-count">{{ s.count }}</span>
                  <div class="status-bar-bg">
                    <div class="status-bar-fill" :style="{ width: statusPercent(s.count) + '%' }"></div>
                  </div>
                </div>
                <div v-if="!statistics.status_breakdown?.length" class="empty-tip">暂无数据</div>
              </div>
            </div>

            <div class="sub-section">
              <h3>🏆 热销商家 Top5</h3>
              <div class="top-list">
                <div class="top-row" v-for="(m, idx) in statistics.top_merchants" :key="m.id">
                  <span class="top-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</span>
                  <span class="top-name">{{ m.name }}</span>
                  <span class="top-info">{{ m.order_count }}单 ¥{{ m.total_revenue }}</span>
                </div>
                <div v-if="!statistics.top_merchants?.length" class="empty-tip">暂无数据</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ========== 订单管理 ========== -->
        <div v-if="activeMenu === 'orders'" class="section">
          <h2 class="section-title">📋 订单管理</h2>
          <div class="toolbar">
            <select v-model.number="orderFilter.status" class="native-select" @change="fetchOrders">
              <option :value="undefined">全部状态</option>
              <option :value="0">待支付</option>
              <option :value="1">待接单</option>
              <option :value="2">已接单</option>
              <option :value="3">配送中</option>
              <option :value="4">已完成</option>
              <option :value="-1">已取消</option>
            </select>
            <input v-model="orderFilter.keyword" placeholder="搜索订单号/用户" class="filter-input" @keyup.enter="fetchOrders" />
            <button class="btn btn-sm" @click="fetchOrders">🔍 搜索</button>
          </div>

          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th><th>用户</th><th>商家</th><th>骑手</th><th>金额</th><th>状态</th><th>时间</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in orders" :key="o.id">
                  <td>{{ o.id }}</td>
                  <td>{{ o.user_name || '-' }}<br><small>{{ o.user_phone }}</small></td>
                  <td>{{ o.merchant_name || '-' }}</td>
                  <td>{{ o.rider_name || '-' }}</td>
                  <td>¥{{ o.total_amount }}</td>
                  <td><span class="badge" :class="'s-' + o.status">{{ statusText(o.status) }}</span></td>
                  <td>{{ o.create_time }}</td>
                  <td class="action-cell">
                    <button class="btn btn-xs" @click="viewOrderDetail(o.id)">详情</button>
                    <button class="btn btn-xs btn-warn" @click="changeOrderStatus(o)">状态</button>
                    <button class="btn btn-xs btn-danger" @click="deleteOrderConfirm(o.id)">删除</button>
                  </td>
                </tr>
                <tr v-if="!orders.length"><td colspan="8" class="empty-td">暂无订单</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ========== 商家管理 ========== -->
        <div v-if="activeMenu === 'merchants'" class="section">
          <div class="section-header">
            <h2 class="section-title">🏪 商家管理</h2>
            <button class="btn btn-primary" @click="openMerchantForm()">+ 新增商家</button>
          </div>
          <div class="toolbar">
            <input v-model="merchantFilter" placeholder="搜索商家名称/电话" class="filter-input" @keyup.enter="fetchMerchants" />
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th><th>名称</th><th>地址</th><th>电话</th><th>评分</th><th>月销</th><th>配送费</th><th>状态</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in filteredMerchants" :key="m.id">
                  <td>{{ m.id }}</td>
                  <td>{{ m.name }}</td>
                  <td>{{ m.address }}</td>
                  <td>{{ m.phone }}</td>
                  <td>⭐{{ m.rating }}</td>
                  <td>{{ m.monthly_sales }}</td>
                  <td>¥{{ m.delivery_fee }}</td>
                  <td><span class="badge" :class="m.status ? 's-4' : 's--1'">{{ m.status ? '营业' : '休息' }}</span></td>
                  <td class="action-cell">
                    <button class="btn btn-xs" @click="openMerchantForm(m)">编辑</button>
                    <button class="btn btn-xs btn-danger" @click="deleteMerchantConfirm(m)">删除</button>
                  </td>
                </tr>
                <tr v-if="!filteredMerchants.length"><td colspan="9" class="empty-td">暂无商家</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ========== 骑手管理 ========== -->
        <div v-if="activeMenu === 'riders'" class="section">
          <div class="section-header">
            <h2 class="section-title">🛵 骑手管理</h2>
            <button class="btn btn-primary" @click="openRiderForm()">+ 新增骑手</button>
          </div>
          <div class="toolbar">
            <input v-model="riderFilter" placeholder="搜索骑手姓名/电话" class="filter-input" />
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th><th>姓名</th><th>电话</th><th>经度</th><th>纬度</th><th>状态</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in filteredRiders" :key="r.id">
                  <td>{{ r.id }}</td>
                  <td>{{ r.name }}</td>
                  <td>{{ r.phone }}</td>
                  <td>{{ r.lng }}</td>
                  <td>{{ r.lat }}</td>
                  <td><span class="badge" :class="r.status ? 's-3' : 's-0'">{{ r.status ? '配送中' : '空闲' }}</span></td>
                  <td class="action-cell">
                    <button class="btn btn-xs" @click="openRiderForm(r)">编辑</button>
                    <button class="btn btn-xs btn-danger" @click="deleteRiderConfirm(r)">删除</button>
                  </td>
                </tr>
                <tr v-if="!filteredRiders.length"><td colspan="7" class="empty-td">暂无骑手</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ========== 用户管理 ========== -->
        <div v-if="activeMenu === 'users'" class="section">
          <h2 class="section-title">👤 用户管理</h2>
          <div class="toolbar">
            <input v-model="userFilter" placeholder="搜索用户昵称/手机号" class="filter-input" @keyup.enter="fetchUsers" />
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th><th>昵称</th><th>手机号</th><th>余额</th><th>注册时间</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>{{ u.id }}</td>
                  <td>{{ u.nickname }}</td>
                  <td>{{ u.phone }}</td>
                  <td>¥{{ u.balance }}</td>
                  <td>{{ u.create_time }}</td>
                  <td class="action-cell">
                    <button class="btn btn-xs" @click="openUserForm(u)">编辑</button>
                    <button class="btn btn-xs btn-danger" @click="deleteUserConfirm(u)">删除</button>
                  </td>
                </tr>
                <tr v-if="!users.length"><td colspan="6" class="empty-td">暂无用户</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ========== 商品管理 ========== -->
        <div v-if="activeMenu === 'products'" class="section">
          <div class="section-header">
            <h2 class="section-title">🍔 商品管理</h2>
            <button class="btn btn-primary" @click="openProductForm()">+ 新增商品</button>
          </div>
          <div class="toolbar">
            <select v-model.number="productFilter.merchant_id" class="native-select" @change="fetchProducts">
              <option :value="undefined">全部商家</option>
              <option v-for="m in merchantList" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
            <input v-model="productFilter.keyword" placeholder="搜索商品名" class="filter-input" />
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th><th>商品名</th><th>所属商家</th><th>价格</th><th>分类</th><th>销量</th><th>状态</th><th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredProducts" :key="p.id">
                  <td>{{ p.id }}</td>
                  <td>{{ p.name }}</td>
                  <td>{{ p.merchant_name }}</td>
                  <td>¥{{ p.price }}</td>
                  <td>{{ p.category }}</td>
                  <td>{{ p.sales }}</td>
                  <td><span class="badge" :class="p.is_available ? 's-4' : 's--1'">{{ p.is_available ? '上架' : '下架' }}</span></td>
                  <td class="action-cell">
                    <button class="btn btn-xs" @click="openProductForm(p)">编辑</button>
                    <button class="btn btn-xs btn-danger" @click="deleteProductConfirm(p)">删除</button>
                  </td>
                </tr>
                <tr v-if="!filteredProducts.length"><td colspan="8" class="empty-td">暂无商品</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 弹窗：订单详情 ========== -->
    <van-popup v-model:show="orderDetailVisible" position="center" round :style="{ width: '90%', maxWidth: '600px', maxHeight: '80vh', overflow: 'auto' }">
      <div class="popup-content">
        <h3>📋 订单详情 #{{ currentOrder?.id }}</h3>
        <div v-if="currentOrder" class="detail-grid">
          <div class="detail-item"><label>用户</label><span>{{ currentOrder.user_name }} ({{ currentOrder.user_phone }})</span></div>
          <div class="detail-item"><label>商家</label><span>{{ currentOrder.merchant_name }}</span></div>
          <div class="detail-item"><label>骑手</label><span>{{ currentOrder.rider_name || '未分配' }}</span></div>
          <div class="detail-item"><label>金额</label><span>¥{{ currentOrder.total_amount }}</span></div>
          <div class="detail-item"><label>状态</label><span class="badge" :class="'s-' + currentOrder.status">{{ statusText(currentOrder.status) }}</span></div>
          <div class="detail-item"><label>地址</label><span>{{ currentOrder.address }}</span></div>
          <div class="detail-item"><label>备注</label><span>{{ currentOrder.remark || '-' }}</span></div>
          <div class="detail-item"><label>创建</label><span>{{ currentOrder.create_time }}</span></div>
          <div class="detail-item"><label>支付</label><span>{{ currentOrder.pay_time || '-' }}</span></div>
          <div class="detail-item"><label>完成</label><span>{{ currentOrder.finish_time || '-' }}</span></div>
        </div>
        <div v-if="currentOrder?.items?.length" class="order-items">
          <h4>商品清单</h4>
          <div class="item-row" v-for="item in currentOrder.items" :key="item.id">
            <span>{{ item.product_name }} ×{{ item.quantity }}</span>
            <span>¥{{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        <div class="popup-actions">
          <button class="btn" @click="orderDetailVisible = false">关闭</button>
        </div>
      </div>
    </van-popup>

    <!-- ========== 弹窗：修改订单状态 ========== -->
    <van-popup v-model:show="orderStatusVisible" position="center" round :style="{ width: '90%', maxWidth: '400px' }">
      <div class="popup-content">
        <h3>修改订单状态</h3>
        <p class="popup-desc">当前状态：<span class="badge" :class="'s-' + editingOrder?.status">{{ statusText(editingOrder?.status) }}</span></p>
        <select v-model.number="newOrderStatus" class="native-select full-select">
          <option :value="0">待支付</option>
          <option :value="1">待接单</option>
          <option :value="2">已接单</option>
          <option :value="3">配送中</option>
          <option :value="4">已完成</option>
          <option :value="-1">已取消</option>
        </select>
        <div class="popup-actions">
          <button class="btn" @click="orderStatusVisible = false">取消</button>
          <button class="btn btn-primary" @click="submitOrderStatus">确认修改</button>
        </div>
      </div>
    </van-popup>

    <!-- ========== 弹窗：商家表单 ========== -->
    <van-popup v-model:show="merchantFormVisible" position="center" round :style="{ width: '90%', maxWidth: '550px', maxHeight: '80vh', overflow: 'auto' }">
      <div class="popup-content">
        <h3>{{ editingMerchant?.id ? '编辑商家' : '新增商家' }}</h3>
        <div class="form-grid">
          <div class="form-item"><label>名称 *</label><input v-model="merchantForm.name" class="form-input" /></div>
          <div class="form-item"><label>地址</label><input v-model="merchantForm.address" class="form-input" /></div>
          <div class="form-item"><label>电话</label><input v-model="merchantForm.phone" class="form-input" /></div>
          <div class="form-row">
            <div class="form-item"><label>经度</label><input v-model.number="merchantForm.lng" type="number" class="form-input" /></div>
            <div class="form-item"><label>纬度</label><input v-model.number="merchantForm.lat" type="number" class="form-input" /></div>
          </div>
          <div class="form-row">
            <div class="form-item"><label>评分</label><input v-model.number="merchantForm.rating" type="number" step="0.1" class="form-input" /></div>
            <div class="form-item"><label>月销量</label><input v-model.number="merchantForm.monthly_sales" type="number" class="form-input" /></div>
          </div>
          <div class="form-row">
            <div class="form-item"><label>配送费</label><input v-model.number="merchantForm.delivery_fee" type="number" class="form-input" /></div>
            <div class="form-item"><label>起送价</label><input v-model.number="merchantForm.min_price" type="number" class="form-input" /></div>
          </div>
          <div class="form-item"><label>Logo URL</label><input v-model="merchantForm.logo" class="form-input" /></div>
          <div class="form-item"><label>营业状态</label>
            <select v-model="merchantForm.status" class="native-select">
              <option :value="1">营业中</option>
              <option :value="0">休息中</option>
            </select>
          </div>
          <div class="form-item"><label>密码</label><input v-model="merchantForm.password" type="password" class="form-input" placeholder="留空不修改密码" /></div>
        </div>
        <div class="popup-actions">
          <button class="btn" @click="merchantFormVisible = false">取消</button>
          <button class="btn btn-primary" @click="submitMerchant">{{ editingMerchant?.id ? '保存' : '创建' }}</button>
        </div>
      </div>
    </van-popup>

    <!-- ========== 弹窗：骑手表单 ========== -->
    <van-popup v-model:show="riderFormVisible" position="center" round :style="{ width: '90%', maxWidth: '450px' }">
      <div class="popup-content">
        <h3>{{ editingRider?.id ? '编辑骑手' : '新增骑手' }}</h3>
        <div class="form-grid">
          <div class="form-item"><label>姓名 *</label><input v-model="riderForm.name" class="form-input" /></div>
          <div class="form-item"><label>电话 *</label><input v-model="riderForm.phone" class="form-input" /></div>
          <div class="form-row">
            <div class="form-item"><label>经度</label><input v-model.number="riderForm.lng" type="number" class="form-input" /></div>
            <div class="form-item"><label>纬度</label><input v-model.number="riderForm.lat" type="number" class="form-input" /></div>
          </div>
          <div class="form-item"><label>状态</label>
            <select v-model="riderForm.status" class="native-select">
              <option :value="0">空闲</option>
              <option :value="1">配送中</option>
            </select>
          </div>
          <div class="form-item"><label>密码</label><input v-model="riderForm.password" type="password" class="form-input" placeholder="留空不修改密码" /></div>
        </div>
        <div class="popup-actions">
          <button class="btn" @click="riderFormVisible = false">取消</button>
          <button class="btn btn-primary" @click="submitRider">{{ editingRider?.id ? '保存' : '创建' }}</button>
        </div>
      </div>
    </van-popup>

    <!-- ========== 弹窗：用户表单 ========== -->
    <van-popup v-model:show="userFormVisible" position="center" round :style="{ width: '90%', maxWidth: '420px' }">
      <div class="popup-content">
        <h3>编辑用户</h3>
        <div class="form-grid">
          <div class="form-item"><label>昵称</label><input v-model="userForm.nickname" class="form-input" /></div>
          <div class="form-item"><label>手机号</label><input v-model="userForm.phone" class="form-input" /></div>
          <div class="form-item"><label>余额</label><input v-model.number="userForm.balance" type="number" class="form-input" /></div>
        </div>
        <div class="popup-actions">
          <button class="btn" @click="userFormVisible = false">取消</button>
          <button class="btn btn-primary" @click="submitUser">保存</button>
        </div>
      </div>
    </van-popup>

    <!-- ========== 弹窗：商品表单 ========== -->
    <van-popup v-model:show="productFormVisible" position="center" round :style="{ width: '90%', maxWidth: '500px', maxHeight: '80vh', overflow: 'auto' }">
      <div class="popup-content">
        <h3>{{ editingProduct?.id ? '编辑商品' : '新增商品' }}</h3>
        <div class="form-grid">
          <div class="form-item"><label>商品名称 *</label><input v-model="productForm.name" class="form-input" /></div>
          <div class="form-item"><label>所属商家</label>
            <select v-model.number="productForm.merchant_id" class="native-select">
              <option v-for="m in merchantList" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-item"><label>价格 *</label><input v-model.number="productForm.price" type="number" class="form-input" /></div>
            <div class="form-item"><label>分类</label><input v-model="productForm.category" class="form-input" /></div>
          </div>
          <div class="form-row">
            <div class="form-item"><label>销量</label><input v-model.number="productForm.sales" type="number" class="form-input" /></div>
            <div class="form-item"><label>状态</label>
              <select v-model="productForm.is_available" class="native-select">
                <option :value="1">上架</option>
                <option :value="0">下架</option>
              </select>
            </div>
          </div>
          <div class="form-item"><label>图片 URL</label><input v-model="productForm.image" class="form-input" /></div>
          <div class="form-item"><label>描述</label><textarea v-model="productForm.description" class="form-textarea" rows="3"></textarea></div>
        </div>
        <div class="popup-actions">
          <button class="btn" @click="productFormVisible = false">取消</button>
          <button class="btn btn-primary" @click="submitProduct">{{ editingProduct?.id ? '保存' : '创建' }}</button>
        </div>
      </div>
    </van-popup>

    <!-- Toast -->
    <van-toast />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { showToast, showConfirmDialog } from 'vant'

// ========== 菜单 ==========
const menuItems = [
  { key: 'statistics', icon: '📊', label: '数据统计' },
  { key: 'orders', icon: '📋', label: '订单管理' },
  { key: 'merchants', icon: '🏪', label: '商家管理' },
  { key: 'riders', icon: '🛵', label: '骑手管理' },
  { key: 'users', icon: '👤', label: '用户管理' },
  { key: 'products', icon: '🍔', label: '商品管理' }
]
const activeMenu = ref('statistics')

// ========== 登录检查 ==========
const token = localStorage.getItem('token') || ''
const role = localStorage.getItem('role') || ''
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('userInfo')
  window.location.href = '/#/admin/login'
}

function switchToUser() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('userInfo')
  window.location.href = '/#/login'
}

// ========== 辅助函数 ==========
const STATUS_MAP = { '-1': '已取消', 0: '待支付', 1: '待接单', 2: '已接单', 3: '配送中', 4: '已完成' }
function statusText(s) { return STATUS_MAP[String(s)] || '未知' }

function showDeleteConfirm(name, cb) {
  showConfirmDialog({
    title: '确认删除',
    message: `确定要删除「${name}」吗？此操作不可恢复！`,
    confirmButtonText: '确认删除',
    confirmButtonColor: '#ee0a24',
    cancelButtonText: '取消'
  }).then(() => cb()).catch(() => {})
}

// ========== 数据统计 ==========
const statistics = ref({
  today_orders: 0, today_amount: 0,
  total_orders: 0, total_users: 0, total_merchants: 0, total_riders: 0, total_products: 0,
  week_orders: [], week_amount: [], status_breakdown: [], top_merchants: []
})

async function fetchStatistics() {
  try {
    const res = await axios.get('/api/admin/statistics')
    if (res.data.code === 200) statistics.value = res.data.data
  } catch (e) {
    console.error('fetch statistics', e)
  }
}

function barHeight(val, type) {
  if (!val) return 4
  const all = type === 'orders' ? statistics.value.week_orders : statistics.value.week_amount
  if (!all.length) return 4
  const maxVal = Math.max(...all.map(d => type === 'orders' ? d.count : d.amount), 1)
  return Math.max(4, (val / maxVal) * 120)
}

function statusPercent(count) {
  const all = statistics.value.status_breakdown || []
  const total = all.reduce((s, d) => s + d.count, 0) || 1
  return Math.round((count / total) * 100)
}

// ========== 订单管理 ==========
const orders = ref([])
const orderFilter = reactive({ status: undefined, keyword: '' })
const orderDetailVisible = ref(false)
const orderStatusVisible = ref(false)
const currentOrder = ref(null)
const editingOrder = ref(null)
const newOrderStatus = ref(0)

async function fetchOrders() {
  try {
    const params = {}
    if (orderFilter.status !== undefined && orderFilter.status !== '' && orderFilter.status !== null) {
      params.status = orderFilter.status
    }
    if (orderFilter.keyword) params.keyword = orderFilter.keyword
    const res = await axios.get('/api/admin/orders', { params })
    if (res.data.code === 200) orders.value = res.data.data
  } catch (e) {
    console.error('fetch orders', e)
  }
}

async function viewOrderDetail(id) {
  try {
    const res = await axios.get(`/api/admin/orders/${id}`)
    if (res.data.code === 200) {
      currentOrder.value = res.data.data
      orderDetailVisible.value = true
    }
  } catch (e) {
    showToast('获取订单详情失败')
  }
}

function changeOrderStatus(o) {
  editingOrder.value = o
  newOrderStatus.value = o.status
  orderStatusVisible.value = true
}

async function submitOrderStatus() {
  if (!editingOrder.value) return
  try {
    const res = await axios.put(`/api/admin/orders/${editingOrder.value.id}`, { status: newOrderStatus.value })
    if (res.data.code === 200) {
      showToast('状态已更新')
      orderStatusVisible.value = false
      fetchOrders()
      fetchStatistics()
    } else {
      showToast(res.data.msg)
    }
  } catch (e) {
    showToast('操作失败')
  }
}

function deleteOrderConfirm(id) {
  showDeleteConfirm(`订单 #${id}`, () => deleteOrder(id))
}

async function deleteOrder(id) {
  try {
    const res = await axios.delete(`/api/admin/orders/${id}`)
    if (res.data.code === 200) {
      showToast('订单已删除')
      fetchOrders()
      fetchStatistics()
    }
  } catch (e) {
    showToast('删除失败')
  }
}

// ========== 商家管理 ==========
const merchants = ref([])
const merchantFilter = ref('')
const merchantFormVisible = ref(false)
const editingMerchant = ref(null)
const merchantForm = reactive(blankMerchant())

function blankMerchant() {
  return { name: '', address: '', phone: '', lng: 0, lat: 0, logo: '', rating: 5, monthly_sales: 0, delivery_fee: 0, min_price: 0, status: 1, password: '' }
}

const filteredMerchants = computed(() => {
  if (!merchantFilter.value) return merchants.value
  const kw = merchantFilter.value.toLowerCase()
  return merchants.value.filter(m => m.name.includes(kw) || m.phone.includes(kw))
})

async function fetchMerchants() {
  try {
    const params = {}
    if (merchantFilter.value) params.keyword = merchantFilter.value
    const res = await axios.get('/api/admin/merchants', { params })
    if (res.data.code === 200) merchants.value = res.data.data
  } catch (e) {
    console.error('fetch merchants', e)
  }
}

function openMerchantForm(m = null) {
  if (m) {
    editingMerchant.value = m
    Object.assign(merchantForm, m, { password: '' })
  } else {
    editingMerchant.value = null
    Object.assign(merchantForm, blankMerchant())
  }
  merchantFormVisible.value = true
}

async function submitMerchant() {
  try {
    let res
    if (editingMerchant.value?.id) {
      res = await axios.put(`/api/admin/merchants/${editingMerchant.value.id}`, merchantForm)
    } else {
      res = await axios.post('/api/admin/merchants', merchantForm)
    }
    if (res.data.code === 200) {
      showToast(editingMerchant.value?.id ? '商家已更新' : '商家已创建')
      merchantFormVisible.value = false
      fetchMerchants()
      fetchStatistics()
    } else {
      showToast(res.data.msg)
    }
  } catch (e) {
    showToast('操作失败')
  }
}

function deleteMerchantConfirm(m) {
  showDeleteConfirm(m.name, () => deleteMerchant(m.id))
}

async function deleteMerchant(id) {
  try {
    const res = await axios.delete(`/api/admin/merchants/${id}`)
    if (res.data.code === 200) {
      showToast('商家已删除')
      fetchMerchants()
      fetchStatistics()
    }
  } catch (e) {
    showToast('删除失败')
  }
}

// ========== 骑手管理 ==========
const riders = ref([])
const riderFilter = ref('')
const riderFormVisible = ref(false)
const editingRider = ref(null)
const riderForm = reactive(blankRider())

function blankRider() { return { name: '', phone: '', lng: 0, lat: 0, status: 0, password: '' } }

const filteredRiders = computed(() => {
  if (!riderFilter.value) return riders.value
  const kw = riderFilter.value.toLowerCase()
  return riders.value.filter(r => r.name.includes(kw) || r.phone.includes(kw))
})

async function fetchRiders() {
  try {
    const params = {}
    if (riderFilter.value) params.keyword = riderFilter.value
    const res = await axios.get('/api/admin/riders', { params })
    if (res.data.code === 200) riders.value = res.data.data
  } catch (e) {
    console.error('fetch riders', e)
  }
}

function openRiderForm(r = null) {
  if (r) {
    editingRider.value = r
    Object.assign(riderForm, r, { password: '' })
  } else {
    editingRider.value = null
    Object.assign(riderForm, blankRider())
  }
  riderFormVisible.value = true
}

async function submitRider() {
  try {
    let res
    if (editingRider.value?.id) {
      res = await axios.put(`/api/admin/riders/${editingRider.value.id}`, riderForm)
    } else {
      res = await axios.post('/api/admin/riders', riderForm)
    }
    if (res.data.code === 200) {
      showToast(editingRider.value?.id ? '骑手已更新' : '骑手已创建')
      riderFormVisible.value = false
      fetchRiders()
      fetchStatistics()
    } else {
      showToast(res.data.msg)
    }
  } catch (e) {
    showToast('操作失败')
  }
}

function deleteRiderConfirm(r) {
  showDeleteConfirm(r.name, () => deleteRider(r.id))
}

async function deleteRider(id) {
  try {
    const res = await axios.delete(`/api/admin/riders/${id}`)
    if (res.data.code === 200) {
      showToast('骑手已删除')
      fetchRiders()
      fetchStatistics()
    }
  } catch (e) {
    showToast('删除失败')
  }
}

// ========== 用户管理 ==========
const users = ref([])
const userFilter = ref('')
const userFormVisible = ref(false)
const editingUser = ref(null)
const userForm = reactive({ nickname: '', phone: '', balance: 0 })

async function fetchUsers() {
  try {
    const params = {}
    if (userFilter.value) params.keyword = userFilter.value
    const res = await axios.get('/api/admin/users', { params })
    if (res.data.code === 200) users.value = res.data.data
  } catch (e) {
    console.error('fetch users', e)
  }
}

function openUserForm(u) {
  editingUser.value = u
  Object.assign(userForm, { nickname: u.nickname, phone: u.phone, balance: u.balance })
  userFormVisible.value = true
}

async function submitUser() {
  if (!editingUser.value) return
  try {
    const res = await axios.put(`/api/admin/users/${editingUser.value.id}`, userForm)
    if (res.data.code === 200) {
      showToast('用户已更新')
      userFormVisible.value = false
      fetchUsers()
    } else {
      showToast(res.data.msg)
    }
  } catch (e) {
    showToast('操作失败')
  }
}

function deleteUserConfirm(u) {
  showDeleteConfirm(u.nickname || u.phone, () => deleteUser(u.id))
}

async function deleteUser(id) {
  try {
    const res = await axios.delete(`/api/admin/users/${id}`)
    if (res.data.code === 200) {
      showToast('用户已删除')
      fetchUsers()
      fetchStatistics()
    }
  } catch (e) {
    showToast('删除失败')
  }
}

// ========== 商品管理 ==========
const products = ref([])
const merchantList = ref([])
const productFilter = reactive({ merchant_id: undefined, keyword: '' })
const productFormVisible = ref(false)
const editingProduct = ref(null)
const productForm = reactive(blankProduct())

function blankProduct() { return { merchant_id: undefined, name: '', price: 0, image: '', description: '', sales: 0, category: '', is_available: 1 } }

const filteredProducts = computed(() => {
  let list = products.value
  if (productFilter.merchant_id) {
    list = list.filter(p => p.merchant_id === productFilter.merchant_id)
  }
  if (productFilter.keyword) {
    const kw = productFilter.keyword.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(kw))
  }
  return list
})

async function fetchProducts() {
  try {
    const params = {}
    if (productFilter.merchant_id) params.merchant_id = productFilter.merchant_id
    if (productFilter.keyword) params.keyword = productFilter.keyword
    const res = await axios.get('/api/admin/products', { params })
    if (res.data.code === 200) products.value = res.data.data
  } catch (e) {
    console.error('fetch products', e)
  }
}

async function fetchMerchantList() {
  try {
    const res = await axios.get('/api/admin/merchants')
    if (res.data.code === 200) merchantList.value = res.data.data
  } catch (e) {
    console.error('fetch merchant list', e)
  }
}

function openProductForm(p = null) {
  if (p) {
    editingProduct.value = p
    Object.assign(productForm, {
      merchant_id: p.merchant_id,
      name: p.name,
      price: p.price,
      image: p.image || '',
      description: p.description || '',
      sales: p.sales,
      category: p.category || '',
      is_available: p.is_available
    })
  } else {
    editingProduct.value = null
    Object.assign(productForm, blankProduct())
  }
  productFormVisible.value = true
}

async function submitProduct() {
  try {
    let res
    if (editingProduct.value?.id) {
      res = await axios.put(`/api/admin/products/${editingProduct.value.id}`, productForm)
    } else {
      res = await axios.post('/api/admin/products', productForm)
    }
    if (res.data.code === 200) {
      showToast(editingProduct.value?.id ? '商品已更新' : '商品已创建')
      productFormVisible.value = false
      fetchProducts()
    } else {
      showToast(res.data.msg)
    }
  } catch (e) {
    showToast('操作失败')
  }
}

function deleteProductConfirm(p) {
  showDeleteConfirm(p.name, () => deleteProduct(p.id))
}

async function deleteProduct(id) {
  try {
    const res = await axios.delete(`/api/admin/products/${id}`)
    if (res.data.code === 200) {
      showToast('商品已删除')
      fetchProducts()
    }
  } catch (e) {
    showToast('删除失败')
  }
}

// ========== 初始化 ==========
onMounted(() => {
  if (role !== 'admin') {
    window.location.href = '/#/admin/login'
    return
  }
  fetchStatistics()
  fetchOrders()
  fetchMerchants()
  fetchRiders()
  fetchUsers()
  fetchProducts()
  fetchMerchantList()
})
</script>

<style scoped>
/* ===== 全局布局 ===== */
.admin-page {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: #1a1a2e;
  color: #fff;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.admin-logo {
  font-size: 18px;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-user {
  font-size: 14px;
  opacity: 0.8;
}

.switch-btn {
  background: rgba(255,255,255,0.08);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.switch-btn:hover { background: rgba(255,255,255,0.2); }

.logout-btn {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.logout-btn:hover { background: rgba(255,255,255,0.25); }

/* ===== 侧栏 + 主内容 ===== */
.admin-body {
  display: flex;
  flex: 1;
}

.admin-sidebar {
  width: 200px;
  background: #16213e;
  padding: 12px 0;
  flex-shrink: 0;
  min-height: calc(100vh - 60px);
}

.sidebar-item {
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.sidebar-item:hover { color: #fff; background: rgba(255,255,255,0.05); }
.sidebar-item.active {
  color: #fff;
  background: rgba(255,255,255,0.1);
  border-left-color: #4fc3f7;
}

.menu-icon { font-size: 18px; }
.menu-text { font-weight: 500; }

/* ===== 内容区 ===== */
.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 20px;
  color: #1a1a2e;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.section-header .section-title { margin-bottom: 0; }

.sub-section {
  margin-top: 24px;
}

.sub-section h3 {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  color: #fff;
}

.stat-card.blue { background: linear-gradient(135deg, #4fc3f7, #0288d1); }
.stat-card.green { background: linear-gradient(135deg, #81c784, #388e3c); }
.stat-card.purple { background: linear-gradient(135deg, #ce93d8, #7b1fa2); }
.stat-card.orange { background: linear-gradient(135deg, #ffb74d, #f57c00); }
.stat-card.cyan { background: linear-gradient(135deg, #4dd0e1, #00838f); }
.stat-card.pink { background: linear-gradient(135deg, #f48fb1, #c2185b); }

.stat-value {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
}

/* ===== 柱状图 ===== */
.chart-bar {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 160px;
  padding: 8px 0;
  border-bottom: 2px solid #e0e0e0;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.bar-value {
  font-size: 11px;
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
}

.bar-fill {
  width: 32px;
  background: linear-gradient(to top, #4fc3f7, #0288d1);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  transition: height 0.3s;
}

.bar-fill.amount {
  background: linear-gradient(to top, #81c784, #388e3c);
}

.bar-date {
  font-size: 11px;
  color: #999;
  margin-top: 6px;
}

/* ===== 两栏布局 ===== */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* ===== 状态分布 ===== */
.status-list { display: flex; flex-direction: column; gap: 8px; }
.status-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label { font-size: 13px; min-width: 56px; color: #555; }
.status-count { font-size: 13px; font-weight: 600; min-width: 30px; }
.status-bar-bg { flex: 1; height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.status-bar-fill { height: 100%; background: #4fc3f7; border-radius: 4px; transition: width 0.3s; }

/* ===== Top 商家列表 ===== */
.top-list { display: flex; flex-direction: column; gap: 8px; }
.top-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.top-rank { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff; background: #999; }
.top-rank.rank-1 { background: #f44336; }
.top-rank.rank-2 { background: #ff9800; }
.top-rank.rank-3 { background: #ffc107; }
.top-name { flex: 1; font-size: 13px; font-weight: 500; }
.top-info { font-size: 12px; color: #888; }

.empty-tip { color: #bbb; font-size: 13px; text-align: center; padding: 20px; }

/* ===== 工具栏 ===== */
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.native-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  outline: none;
  min-width: 120px;
  cursor: pointer;
}

.native-select:focus { border-color: #4fc3f7; }

.native-select.full-select { width: 100%; margin-bottom: 12px; }

.filter-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 13px;
  width: 200px;
  outline: none;
}

.filter-input:focus { border-color: #4fc3f7; }

/* ===== 表格 ===== */
.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: #fafafa;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e8e8e8;
  white-space: nowrap;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.data-table td small { color: #999; font-size: 11px; }

.data-table tbody tr:hover { background: #fafafa; }

.empty-td { text-align: center; color: #bbb; padding: 30px !important; }

/* ===== 状态徽章 ===== */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.badge.s-0 { background: #fff3e0; color: #e65100; }
.badge.s-1 { background: #e3f2fd; color: #1565c0; }
.badge.s-2 { background: #e8f5e9; color: #2e7d32; }
.badge.s-3 { background: #fce4ec; color: #c62828; }
.badge.s-4 { background: #f3e5f5; color: #6a1b9a; }
.badge.s--1 { background: #eceff1; color: #546e7a; }

/* ===== 按钮 ===== */
.btn {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
}

.btn:hover { border-color: #4fc3f7; color: #0288d1; }

.btn-primary { background: #0288d1; color: #fff; border-color: #0288d1; }
.btn-primary:hover { background: #0277bd; color: #fff; }

.btn-sm { padding: 6px 14px; font-size: 12px; }

.btn-xs { padding: 3px 8px; font-size: 11px; border-radius: 4px; }

.btn-warn { background: #fff3e0; border-color: #ff9800; color: #e65100; }
.btn-warn:hover { background: #ffe0b2; }

.btn-danger { color: #ee0a24; border-color: #ffcdd2; }
.btn-danger:hover { background: #ffebee; border-color: #ee0a24; }

/* ===== 操作单元格 ===== */
.action-cell {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* ===== 弹窗 ===== */
.popup-content {
  padding: 24px;
}

.popup-content h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #1a1a2e;
}

.popup-desc { font-size: 14px; color: #666; margin-bottom: 12px; }

.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.full-select { width: 100%; margin-bottom: 12px; }

/* ===== 详情网格 ===== */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-item label { font-size: 11px; color: #999; font-weight: 500; }
.detail-item span { font-size: 13px; color: #333; }

.order-items { margin-top: 16px; padding-top: 16px; border-top: 1px solid #f0f0f0; }
.order-items h4 { font-size: 14px; margin: 0 0 8px; }
.item-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; }
.item-row span:last-child { color: #e65100; font-weight: 600; }

/* ===== 表单 ===== */
.form-grid { display: flex; flex-direction: column; gap: 12px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.form-item { display: flex; flex-direction: column; gap: 4px; }
.form-item label { font-size: 12px; font-weight: 600; color: #555; }

.form-input, .form-textarea {
  padding: 8px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus { border-color: #4fc3f7; }

.form-textarea { resize: vertical; font-family: inherit; }

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
  .two-col { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .admin-sidebar { width: 60px; }
  .sidebar-item { padding: 12px 16px; justify-content: center; }
  .menu-text { display: none; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar { flex-wrap: wrap; }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
  .admin-header { padding: 0 12px; }
  .admin-content { padding: 12px; }
}
</style>
