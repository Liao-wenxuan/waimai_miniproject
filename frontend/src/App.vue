<template>
  <div id="app-container">
    <!-- 自定义导航栏 (不再依赖 Vant NavBar 默认样式) -->
    <div v-if="showNavBar" class="clay-navbar" :class="{ 'nav-scrolled': scrolled }">
      <div class="nav-left" @click="$router.back()">
        <span class="nav-back-arrow">←</span>
      </div>
      <div class="nav-title">{{ navTitle }}</div>
      <div class="nav-right"></div>
    </div>

    <div :class="['main-content', { 'has-tabbar': showTabBar, 'has-navbar': showNavBar }]">
      <router-view v-slot="{ Component }">
        <transition name="page-reveal" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>

    <!-- 自定义底部导航 - 有机形态 -->
    <nav v-if="showTabBar" class="clay-tabbar">
      <div class="tabbar-bg"></div>
      <router-link to="/home" class="tabbar-item" :class="{ active: route.path === '/home' }">
        <div class="tab-icon-wrap">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/>
            <path d="M9 21V12h6v9"/>
          </svg>
        </div>
        <span class="tab-label">探索</span>
      </router-link>
      <router-link to="/orders" class="tabbar-item" :class="{ active: route.path === '/orders' }">
        <div class="tab-icon-wrap">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <rect x="3" y="3" width="7" height="7" rx="1.5"/>
            <rect x="14" y="3" width="7" height="7" rx="1.5"/>
            <rect x="3" y="14" width="7" height="7" rx="1.5"/>
            <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          </svg>
        </div>
        <span class="tab-label">订单</span>
      </router-link>
      <router-link to="/profile" class="tabbar-item" :class="{ active: route.path === '/profile' }">
        <div class="tab-icon-wrap">
          <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>
          </svg>
        </div>
        <span class="tab-label">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scrolled = ref(false)

const tabBarRoutes = ['/home', '/orders', '/profile']
const showTabBar = computed(() => tabBarRoutes.includes(route.path))

const navBarRoutes = ['/merchant', '/order-detail', '/favorites', '/help', '/settings',
  '/merchant-orders', '/merchant-profile', '/rider-orders', '/rider-profile']
const showNavBar = computed(() => navBarRoutes.some(r => route.path.startsWith(r)))

const navTitle = computed(() => {
  const titles = {
    '/merchant': '商家',
    '/order-detail': '订单详情',
    '/favorites': '收藏',
    '/help': '帮助',
    '/settings': '设置',
    '/merchant-orders': '订单管理',
    '/merchant-profile': '商家中心',
    '/rider-orders': '工作台',
    '/rider-profile': '骑手中心',
  }
  for (const [prefix, title] of Object.entries(titles)) {
    if (route.path.startsWith(prefix)) return title
  }
  return ''
})

// Scroll detection for nav transparency
if (typeof window !== 'undefined') {
  window.addEventListener('scroll', () => {
    scrolled.value = window.scrollY > 20
  }, { passive: true })
}
</script>

<style>
/* ============================================================
   「 Clay & Hearth 」 Design System
   陶土与炉火  —  有机 · 温暖 · 手工质感
   ============================================================ */

/* --- CSS Custom Properties --- */
:root {
  /* Palette */
  --clay-brand:        #C84B31;
  --clay-brand-deep:   #8B3A2A;
  --clay-brand-light:  #FCEAE4;
  --clay-brand-glow:   #FDF3EF;
  --clay-accent:       #C8963E;
  --clay-accent-light: #FBF3E2;
  --clay-success:      #6B8E6B;
  --clay-success-bg:   #EDF4ED;
  --clay-danger:       #C0392B;
  --clay-danger-bg:    #FDF0ED;
  --clay-info:         #5B7FA5;
  --clay-info-bg:      #EDF3F8;

  /* Surfaces */
  --clay-page:         #FDF8F0;
  --clay-card:         #FFFFFF;
  --clay-card-warm:    #FFFBF7;
  --clay-border:       #EBE3D6;
  --clay-divider:      #F2EBE0;

  /* Text */
  --clay-text:         #2C2416;
  --clay-text-body:    #4A3F32;
  --clay-text-soft:    #8C7A6B;
  --clay-text-muted:   #BFB3A4;

  /* Radii — intentionally varied */
  --radius-sm:    6px;
  --radius-md:    12px;
  --radius-lg:    20px;
  --radius-xl:    28px;
  --radius-blob:  40% 60% 55% 45% / 45% 50% 50% 55%;

  /* Shadows */
  --shadow-sm:    0 1px 3px rgba(44, 36, 22, 0.04);
  --shadow-md:    0 4px 20px rgba(44, 36, 22, 0.06);
  --shadow-lg:    0 8px 40px rgba(44, 36, 22, 0.08);
  --shadow-glow:  0 4px 24px rgba(200, 75, 49, 0.12);

  /* Springs */
  --spring:       cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-out:     cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out:  cubic-bezier(0.76, 0, 0.24, 1);
}

/* --- Reset & Base --- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: Georgia, 'Noto Serif SC', 'Source Han Serif SC', serif;
  background: var(--clay-page);
  color: var(--clay-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.6;
}

#app { min-height: 100vh; max-width: 480px; margin: 0 auto; position: relative; overflow-x: hidden; }

@media (min-width: 481px) {
  #app {
    border-left: 1px solid var(--clay-border);
    border-right: 1px solid var(--clay-border);
    box-shadow: 0 0 60px rgba(44, 36, 22, 0.06);
  }
}

/* --- Page Transitions --- */
.page-reveal-enter-active {
  transition: opacity 0.35s var(--ease-out), transform 0.4s var(--spring);
}
.page-reveal-leave-active {
  transition: opacity 0.15s ease, transform 0.2s ease;
}
.page-reveal-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}
.page-reveal-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* --- Main Content --- */
.main-content { min-height: 100vh; }
.main-content.has-tabbar { padding-bottom: 80px; }
.main-content.has-navbar { padding-top: 52px; }

/* ============================================================
   Custom Clay Navbar
   ============================================================ */
.clay-navbar {
  position: fixed;
  top: 0; left: 50%;
  transform: translateX(-50%);
  width: 100%; max-width: 480px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  z-index: 200;
  background: rgba(253, 248, 240, 0.85);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid transparent;
  transition: all 0.3s var(--ease-out);
}
.clay-navbar.nav-scrolled {
  border-bottom-color: var(--clay-border);
  box-shadow: 0 1px 12px rgba(44, 36, 22, 0.04);
}
.nav-left, .nav-right { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.nav-back-arrow { font-size: 22px; color: var(--clay-text); font-family: serif; transition: transform 0.2s var(--spring); display: inline-block; }
.nav-left:active .nav-back-arrow { transform: translateX(-3px); }
.nav-title { font-size: 16px; font-weight: 600; color: var(--clay-text); letter-spacing: 0.02em; }

/* ============================================================
   Custom Clay Tabbar — organic blob indicator
   ============================================================ */
.clay-tabbar {
  position: fixed;
  bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 100%; max-width: 480px;
  height: 72px;
  display: flex;
  align-items: flex-start;
  justify-content: space-around;
  padding: 8px 16px 0;
  z-index: 200;
}
.tabbar-bg {
  position: absolute;
  inset: 8px 12px 0;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 22px 22px 0 0;
  border: 1px solid var(--clay-border);
  border-bottom: none;
  box-shadow: 0 -4px 24px rgba(44, 36, 22, 0.05);
}
.tabbar-item {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 20px;
  text-decoration: none;
  color: var(--clay-text-muted);
  transition: all 0.3s var(--spring);
  -webkit-tap-highlight-color: transparent;
}
.tabbar-item.active { color: var(--clay-brand); }
.tabbar-item.active .tab-icon-wrap {
  background: var(--clay-brand-light);
  transform: translateY(-2px);
}
.tab-icon-wrap {
  width: 36px; height: 36px;
  border-radius: var(--radius-blob);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.35s var(--spring);
}
.tab-icon { width: 20px; height: 20px; }
.tab-label { font-size: 10px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }

/* ============================================================
   Vant Overrides — morph Vant into Clay
   ============================================================ */

/* Buttons */
.van-button--primary {
  --van-button-primary-background: var(--clay-brand);
  --van-button-primary-border-color: var(--clay-brand);
  font-family: inherit !important;
  letter-spacing: 0.03em;
  font-weight: 600 !important;
  border-radius: var(--radius-lg) !important;
  transition: all 0.3s var(--spring) !important;
}
.van-button--primary:active {
  transform: scale(0.96);
  --van-button-primary-background: var(--clay-brand-deep);
}

/* Tabs */
.van-tabs__nav { background: transparent !important; }
.van-tab { font-family: inherit !important; font-size: 14px !important; color: var(--clay-text-soft) !important; }
.van-tab--active { color: var(--clay-brand) !important; font-weight: 700 !important; }
.van-tabs__line { background: var(--clay-brand) !important; border-radius: 2px !important; height: 3px !important; }

/* Search */
.van-search__content { border-radius: var(--radius-lg) !important; background: var(--clay-page) !important; }

/* Tags */
.van-tag--primary { --van-tag-primary-color: var(--clay-brand); }
.van-tag--danger { --van-tag-danger-color: var(--clay-danger); }
.van-tag--success { --van-tag-success-color: var(--clay-success); }

/* Cell */
.van-cell { font-family: inherit !important; }
.van-cell-group { border-radius: var(--radius-lg) !important; overflow: hidden; }

/* Popup */
.van-popup--bottom.van-popup--round { border-radius: 24px 24px 0 0 !important; }

/* Toast */
.van-toast {
  background: var(--clay-text) !important;
  color: #fff !important;
  border-radius: var(--radius-lg) !important;
  font-family: inherit !important;
}

/* Dialog */
.van-dialog { border-radius: var(--radius-xl) !important; overflow: hidden; }
.van-dialog__confirm {
  color: var(--clay-brand) !important;
  font-weight: 600 !important;
}

/* Empty */
.van-empty__description { color: var(--clay-text-soft) !important; }

/* Slider */
.van-slider__bar { background: var(--clay-brand) !important; }

/* Switch */
.van-switch--on { background: var(--clay-brand) !important; }

/* Notice bar */
.van-notice-bar { border-radius: var(--radius-md) !important; background: var(--clay-brand-light) !important; color: var(--clay-brand-deep) !important; }

/* Rate */
.van-rate__icon--full { color: var(--clay-accent) !important; }

/* ============================================================
   Shared Utility Classes
   ============================================================ */

/* Card base — organic rounded variant */
.card-clay {
  background: var(--clay-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--clay-border);
  transition: all 0.25s var(--spring);
}
.card-clay:active {
  transform: scale(0.985);
  box-shadow: var(--shadow-md);
}

/* Section header with organic blob */
.section-blob-header {
  position: relative;
  padding: 32px 20px 40px;
  text-align: center;
  color: #fff;
  overflow: hidden;
}
.section-blob-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, var(--clay-brand) 0%, var(--clay-brand-deep) 100%);
  border-radius: 0 0 60% 40% / 0 0 30% 30%;
  z-index: 0;
}
.section-blob-header > * { position: relative; z-index: 1; }

/* Status badges */
.badge-clay {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}
.badge-pending { background: var(--clay-brand-light); color: var(--clay-brand); }
.badge-active { background: var(--clay-success-bg); color: var(--clay-success); }
.badge-info { background: var(--clay-info-bg); color: var(--clay-info); }
.badge-done { background: #F5F2ED; color: var(--clay-text-soft); }
.badge-cancel { background: var(--clay-danger-bg); color: var(--clay-danger); }

/* Price display */
.price-clay {
  font-family: Georgia, 'Times New Roman', serif;
  font-weight: 700;
  color: var(--clay-brand);
  letter-spacing: -0.02em;
}
.price-clay::before { content: '¥'; font-size: 0.6em; vertical-align: super; margin-right: 1px; }

/* Organic divider */
.divider-organic {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--clay-border) 20%, var(--clay-border) 80%, transparent);
  margin: 12px 0;
}

/* Loading shimmer */
@keyframes clay-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton-clay {
  background: linear-gradient(105deg, var(--clay-divider) 25%, var(--clay-border) 50%, var(--clay-divider) 75%);
  background-size: 200% 100%;
  animation: clay-shimmer 1.8s infinite;
  border-radius: var(--radius-sm);
}

/* Spring press effect */
.spring-press { transition: transform 0.2s var(--spring); }
.spring-press:active { transform: scale(0.95); }

/* Noise texture overlay (for cards that need depth) */
.texture-noise {
  position: relative;
}
.texture-noise::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: inherit;
}

/* Animated entrance */
@keyframes rise-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-rise {
  animation: rise-up 0.5s var(--spring) both;
}
.animate-rise-1 { animation-delay: 0.05s; }
.animate-rise-2 { animation-delay: 0.1s; }
.animate-rise-3 { animation-delay: 0.15s; }
.animate-rise-4 { animation-delay: 0.2s; }
</style>
