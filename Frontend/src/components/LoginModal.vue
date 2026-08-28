<script setup>
import { ref } from 'vue'
import { ui } from '../store'
import { login } from '../auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    username.value = ''
    password.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="ui.showLogin" class="overlay" @click.self="ui.showLogin = false">
    <div class="modal">
      <h3 class="title">🔐 登录后修改账本</h3>
      <p class="muted small">只读模式：未登录可查看，但无法增删改。</p>
      <input v-model="username" placeholder="用户名" @keyup.enter="submit" />
      <input v-model="password" type="password" placeholder="密码" @keyup.enter="submit" />
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn block" :disabled="loading" @click="submit">登录</button>
      <button class="btn ghost block" @click="ui.showLogin = false">取消</button>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(20,20,40,0.45);
  display: grid; place-items: center; z-index: 100; padding: 16px;
}
.modal {
  background: #fff; border-radius: 16px; padding: 22px; width: 100%; max-width: 320px;
  display: flex; flex-direction: column; gap: 10px; box-shadow: var(--shadow);
}
.modal input { width: 100%; }
.btn.block { width: 100%; }
.err { color: var(--expense); font-size: 13px; margin: 0; }
.small { font-size: 12px; }
</style>
