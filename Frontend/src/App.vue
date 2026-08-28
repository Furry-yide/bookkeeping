<script setup>
import { useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
import LoginModal from './components/LoginModal.vue'
import { isLoggedIn, authState, logout, openLogin, loadMe } from './auth'

const route = useRoute()
const tabs = [
  { to: '/ledger', label: '🐱 记账', icon: '🐱' },
  { to: '/stats', label: '📊 统计', icon: '📊' },
  { to: '/budget', label: '🎯 预算', icon: '🎯' },
  { to: '/manage', label: '⚙️ 管理', icon: '⚙️' },
]
const active = computed(() => route.path)

onMounted(loadMe)
</script>

<template>
  <div class="app">
    <header class="topbar">
      <div class="brand">🐱 小猫的账本</div>
      <div class="auth">
        <button v-if="isLoggedIn" class="me" @click="logout">👤 {{ authState.user || '已登录' }} · 退出</button>
        <button v-else class="me ghost" @click="openLogin">🔓 登录</button>
      </div>
      <nav class="tabs">
        <router-link
          v-for="t in tabs"
          :key="t.to"
          :to="t.to"
          class="tab"
          :class="{ on: active.startsWith(t.to) }"
        >{{ t.label }}</router-link>
      </nav>
    </header>
    <main class="content">
      <router-view />
    </main>
    <LoginModal />
  </div>
</template>

<style scoped>
.app { max-width: 720px; margin: 0 auto; padding: 0 14px 40px; }
.topbar {
  position: sticky; top: 0; z-index: 10;
  background: var(--bg);
  padding: 16px 0 10px;
}
.brand { font-size: 20px; font-weight: 800; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
.auth { position: absolute; top: 16px; right: 14px; }
.me { border: none; background: var(--primary); color: #fff; font-weight: 600; padding: 6px 12px; border-radius: 10px; font-size: 13px; }
.me.ghost { background: #fff; color: var(--muted); box-shadow: var(--shadow); }
.tabs { display: flex; gap: 8px; }
.tab {
  flex: 1; text-align: center;
  padding: 10px; border-radius: 12px;
  text-decoration: none; color: var(--muted);
  background: #fff; font-weight: 600; box-shadow: var(--shadow);
}
.tab.on { color: #fff; background: var(--primary); }
.content { margin-top: 14px; }
</style>
