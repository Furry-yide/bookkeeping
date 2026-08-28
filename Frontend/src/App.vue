<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const tabs = [
  { to: '/ledger', label: '🐱 记账', icon: '🐱' },
  { to: '/stats', label: '📊 统计', icon: '📊' },
  { to: '/budget', label: '🎯 预算', icon: '🎯' },
]
const active = computed(() => route.path)
</script>

<template>
  <div class="app">
    <header class="topbar">
      <div class="brand">🐱 小猫的账本</div>
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
  </div>
</template>

<style scoped>
.app { max-width: 720px; margin: 0 auto; padding: 0 14px 40px; }
.topbar {
  position: sticky; top: 0; z-index: 10;
  background: var(--bg);
  padding: 16px 0 10px;
}
.brand { font-size: 20px; font-weight: 800; margin-bottom: 10px; }
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
