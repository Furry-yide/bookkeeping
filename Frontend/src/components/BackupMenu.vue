<script setup>
import { ref } from 'vue'
import http from '../api'
import { isLoggedIn, openLogin } from '../auth'

const fileInput = ref(null)
const busy = ref(false)
const toast = ref('')
let timer = null

function show(msg) {
  toast.value = msg
  clearTimeout(timer)
  timer = setTimeout(() => (toast.value = ''), 2600)
}

async function exportData() {
  if (!isLoggedIn.value) return openLogin()
  busy.value = true
  try {
    const { data } = await http.get('/backup/export')
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `小猫的账本_备份_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    show('✅ 导出成功')
  } catch {
    show('❌ 导出失败')
  } finally {
    busy.value = false
  }
}

function pickFile() {
  if (!isLoggedIn.value) return openLogin()
  fileInput.value.click()
}

async function onFile(e) {
  const f = e.target.files[0]
  if (!f) return
  if (!confirm('导入将覆盖当前全部数据，确定继续？')) {
    e.target.value = ''
    return
  }
  busy.value = true
  try {
    const text = await f.text()
    const payload = JSON.parse(text)
    const { data } = await http.post('/backup/import', payload)
    show(`✅ 导入成功（流水 ${data.imported.transactions} 条）`)
  } catch (err) {
    show('❌ 导入失败：' + (err.response?.data?.detail || '数据格式错误'))
  } finally {
    busy.value = false
    e.target.value = ''
  }
}
</script>

<template>
  <div class="backup">
    <button class="btn ghost" :disabled="busy" @click="exportData">⬇️ 导出</button>
    <button class="btn ghost" :disabled="busy" @click="pickFile">⬆️ 导入</button>
    <input ref="fileInput" type="file" accept="application/json" hidden @change="onFile" />
    <transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.backup { position: relative; display: inline-flex; gap: 6px; }
.btn {
  border: none;
  background: var(--primary);
  color: #fff;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 13px;
}
.btn.ghost { background: #fff; color: var(--muted); box-shadow: var(--shadow); }
.toast {
  position: fixed; left: 50%; bottom: 28px; transform: translateX(-50%);
  background: #2c2c3a; color: #fff; padding: 10px 18px; border-radius: 999px;
  font-size: 14px; z-index: 200; box-shadow: var(--shadow);
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
