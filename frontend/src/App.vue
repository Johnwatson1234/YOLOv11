<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo-area">
          <div class="logo-icon">
            <el-icon :size="28"><Monitor /></el-icon>
          </div>
          <transition name="fade">
            <span v-if="!sidebarCollapsed" class="logo-text">慧眼课堂</span>
          </transition>
        </div>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: currentRoute === item.path }"
        >
          <el-icon :size="20"><component :is="item.icon" /></el-icon>
          <transition name="fade">
            <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
          <transition name="fade">
            <span v-if="!sidebarCollapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
          </transition>
        </router-link>
      </nav>

      <div class="sidebar-footer" style="display:flex;flex-direction:column;gap:12px">
        <button class="theme-toggle-btn" @click="toggleTheme" :title="isLight ? '切换到深色模式' : '切换到浅色模式'">
          <el-icon :size="18">
            <Sunny v-if="!isLight" />
            <Moon v-else />
          </el-icon>
          <transition name="fade">
            <span v-if="!sidebarCollapsed" class="theme-text">{{ isLight ? '切换为深色模式' : '切换为浅色模式' }}</span>
          </transition>
        </button>

        <div class="system-status">
          <span class="status-dot online"></span>
          <transition name="fade">
            <span v-if="!sidebarCollapsed" class="status-text">系统运行中</span>
          </transition>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const sidebarCollapsed = ref(false)
const currentRoute = computed(() => route.path)
const isLight = ref(false)

function toggleTheme() {
  isLight.value = !isLight.value
  const root = document.documentElement
  if (isLight.value) {
    root.classList.add('light-theme')
    root.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  } else {
    root.classList.remove('light-theme')
    root.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  }
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  // Project default is dark
  if (saved === 'light') {
    isLight.value = true
    document.documentElement.classList.add('light-theme')
    document.documentElement.classList.remove('dark')
  } else {
    document.documentElement.classList.add('dark')
  }
})

const navItems = [
  { path: '/dashboard', label: '系统工作台', icon: 'Monitor', badge: null },
  { path: '/monitor', label: '课堂监测', icon: 'VideoCameraFilled', badge: null },
  { path: '/attendance', label: '智能考勤', icon: 'UserFilled', badge: null },
  { path: '/report', label: '课后评估', icon: 'DataAnalysis', badge: null },
  { path: '/student', label: '学生画像', icon: 'User', badge: null },
  { path: '/alert', label: '异常预警', icon: 'WarningFilled', badge: '3' },
  { path: '/settings', label: '系统设置', icon: 'Setting', badge: null },
]
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  height: 100vh;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease, min-width 0.3s ease;
  z-index: 100;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
  min-width: var(--sidebar-collapsed);
}

.sidebar-header {
  padding: var(--space-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  min-height: 64px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  overflow: hidden;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-app);
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  background: linear-gradient(90deg, var(--primary), #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: var(--primary);
  background: var(--primary-bg);
}

/* ── Navigation ── */
.sidebar-nav {
  flex: 1;
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary-bg);
  color: var(--primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--primary);
  border-radius: 0 3px 3px 0;
}

.nav-label {
  font-size: 1.05rem;
  font-weight: 500;
}

.nav-badge {
  margin-left: auto;
  background: var(--danger);
  color: #fff;
  font-size: 0.7rem;
  padding: 1px 7px;
  border-radius: 10px;
  font-weight: 600;
}

/* ── Footer ── */
.sidebar-footer {
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
}

.system-status {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.online {
  background: var(--safe);
  box-shadow: 0 0 8px var(--safe);
  animation: breath 3s ease-in-out infinite;
}

.status-text {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ── Theme Toggle ── */
.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 100%;
  overflow: hidden;
  justify-content: center;
}

.sidebar:not(.collapsed) .theme-toggle-btn {
  justify-content: flex-start;
}

.theme-toggle-btn:hover {
  background: var(--bg-hover);
  border-color: var(--primary);
  color: var(--primary);
}

.theme-text {
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
}

/* ── Main Content ── */
.main-content {
  flex: 1;
  overflow: hidden;
  background: var(--bg-app);
}

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.page-enter-active {
  animation: scaleFade 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.page-leave-active {
  animation: fadeOut 0.15s ease;
}

@keyframes scaleFade {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>
