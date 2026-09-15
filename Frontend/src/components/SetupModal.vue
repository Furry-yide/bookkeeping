<script setup>
import { ref } from 'vue'
import { ui } from '../store'
import { setup } from '../auth'

const username = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  const name = username.value.trim()
  if (!name) { error.value = '请输入用户名'; return }
  if (password.value.length < 6) { error.value = '密码至少 6 位'; return }
  if (password.value !== confirm.value) { error.value = '两次输入的密码不一致'; return }
  loading.value = true
  try {
    await setup(name, password.value)
  } catch (e) {
    error.value = e.response?.data?.detail || '创建失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="ui.showSetup" class="overlay">
    <div class="modal">
      <div class="welcome">🐱</div>
      <h3 class="title">欢迎使用小猫的账本</h3>
      <p class="muted small">第一次使用，请先创建一个账户，用于保护你的账本数据。</p>
      <input v-model="username" placeholder="设置用户名" @keyup.enter="submit" />
      <input v-model="password" type="password" placeholder="设置密码（至少 6 位）" @keyup.enter="submit" />
      <input v-model="confirm" type="password" placeholder="确认密码" @keyup.enter="submit" />
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn block" :disabled="loading" @click="submit">{{ loading ? '创建中...' : '创建账户并开始' }}</button>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed; inset: 0; background: rgba(20,20,40,0.55);
  display: grid; place-items: center; z-index: 200; padding: 16px;
}
.modal {
  background: #fff; border-radius: 16px; padding: 24px; width: 100%; max-width: 340px;
  display: flex; flex-direction: column; gap: 10px; box-shadow: var(--shadow);
}
.welcome { font-size: 40px; text-align: center; }
.modal .title { text-align: center; margin: 0; }
.modal input { width: 100%; }
.btn.block { width: 100%; }
.err { color: var(--expense); font-size: 13px; margin: 0; }
.small { font-size: 12px; text-align: center; }
</style>