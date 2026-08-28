<script setup>
import { ref, onMounted } from 'vue'
import http from '../api'
import { isLoggedIn, openLogin } from '../auth'

const tab = ref('category')
const categories = ref([])
const sources = ref([])

const catForm = ref({ id: null, icon: '💰', name: '', type: 'expense' })
const srcForm = ref({ id: null, icon: '💳', name: '' })

async function loadCategories() {
  const { data } = await http.get('/categories')
  categories.value = data
}
async function loadSources() {
  const { data } = await http.get('/payment-sources')
  sources.value = data
}

async function saveCat() {
  if (!catForm.value.name) return
  if (catForm.value.id) {
    await http.put(`/categories/${catForm.value.id}`, catForm.value)
  } else {
    await http.post('/categories', catForm.value)
  }
  catForm.value = { id: null, icon: '💰', name: '', type: 'expense' }
  await loadCategories()
}
function editCat(c) {
  catForm.value = { id: c.id, icon: c.icon, name: c.name, type: c.type }
}
async function delCat(id) {
  await http.delete(`/categories/${id}`)
  await loadCategories()
}

async function saveSrc() {
  if (!srcForm.value.name) return
  if (srcForm.value.id) {
    await http.put(`/payment-sources/${srcForm.value.id}`, srcForm.value)
  } else {
    await http.post('/payment-sources', srcForm.value)
  }
  srcForm.value = { id: null, icon: '💳', name: '' }
  await loadSources()
}
function editSrc(s) {
  srcForm.value = { id: s.id, icon: s.icon, name: s.name }
}
async function delSrc(id) {
  await http.delete(`/payment-sources/${id}`)
  await loadSources()
}

onMounted(async () => { await loadCategories(); await loadSources() })
</script>

<template>
  <div class="stack">
    <div v-if="!isLoggedIn" class="ro-banner">
      🔒 当前为<strong>只读模式</strong>，登录后可新增 / 编辑 / 删除。
      <button class="link" @click="openLogin">去登录</button>
    </div>
    <div class="tabs">
      <button :class="{ on: tab==='category' }" @click="tab='category'">📂 使用方向（分类）</button>
      <button :class="{ on: tab==='source' }" @click="tab='source'">💳 支付源</button>
    </div>

    <!-- 分类管理 -->
    <section v-if="tab==='category'" class="card">
      <h3 class="title">分类管理</h3>
      <div class="form">
        <input v-model="catForm.icon" class="icon" maxlength="2" placeholder="图标" />
        <input v-model="catForm.name" placeholder="名称，如 餐饮" />
        <select v-model="catForm.type">
          <option value="expense">支出</option>
          <option value="income">收入</option>
        </select>
        <button class="btn" :disabled="!isLoggedIn" @click="saveCat">{{ catForm.id ? '保存修改' : '添加分类' }}</button>
        <button v-if="catForm.id" class="btn ghost" @click="catForm={id:null,icon:'💰',name:'',type:'expense'}">取消</button>
      </div>
      <ul class="list">
        <li v-for="c in categories" :key="c.id" class="row spread">
          <span class="row">
            <span class="badge">{{ c.icon }} {{ c.name }}</span>
            <span class="tag" :class="c.type">{{ c.type==='income'?'收入':'支出' }}</span>
          </span>
          <span class="row">
            <button class="btn ghost small" :disabled="!isLoggedIn" @click="editCat(c)">编辑</button>
            <button class="btn danger small" :disabled="!isLoggedIn" @click="delCat(c.id)">删除</button>
          </span>
        </li>
        <p v-if="!categories.length" class="muted">暂无分类</p>
      </ul>
    </section>

    <!-- 支付源管理 -->
    <section v-else class="card">
      <h3 class="title">支付源管理</h3>
      <div class="form">
        <input v-model="srcForm.icon" class="icon" maxlength="2" placeholder="图标" />
        <input v-model="srcForm.name" placeholder="名称，如 微信支付" />
        <button class="btn" :disabled="!isLoggedIn" @click="saveSrc">{{ srcForm.id ? '保存修改' : '添加支付源' }}</button>
        <button v-if="srcForm.id" class="btn ghost" @click="srcForm={id:null,icon:'💳',name:''}">取消</button>
      </div>
      <ul class="list">
        <li v-for="s in sources" :key="s.id" class="row spread">
          <span class="badge">{{ s.icon }} {{ s.name }}</span>
          <span class="row">
            <button class="btn ghost small" :disabled="!isLoggedIn" @click="editSrc(s)">编辑</button>
            <button class="btn danger small" :disabled="!isLoggedIn" @click="delSrc(s.id)">删除</button>
          </span>
        </li>
        <p v-if="!sources.length" class="muted">暂无支付源</p>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.stack { display: flex; flex-direction: column; gap: 14px; }
.ro-banner {
  background: #fff7ed; border: 1px solid #ffd8a8; color: #b45309;
  padding: 10px 14px; border-radius: 12px; font-size: 13px;
}
.ro-banner .link { border: none; background: none; color: var(--primary-dark); font-weight: 700; padding: 0 4px; text-decoration: underline; }
.tabs { display: flex; gap: 8px; }
.tabs button { flex: 1; padding: 10px; border-radius: 12px; border: none; background: #fff; box-shadow: var(--shadow); font-weight: 600; color: var(--muted); }
.tabs button.on { background: var(--primary); color: #fff; }
.form { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.form input, .form select { flex: 1; min-width: 110px; }
.form .icon { flex: none; width: 56px; text-align: center; }
.list { list-style: none; padding: 0; margin: 0; }
.list li { padding: 11px 0; border-bottom: 1px solid var(--border); }
.list li:last-child { border-bottom: none; }
.badge { font-weight: 600; font-size: 15px; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 8px; background: var(--bg); }
.tag.income { color: var(--income); }
.tag.expense { color: var(--expense); }
.btn.small { padding: 5px 10px; font-size: 12px; }
</style>
