<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../api'
import { isLoggedIn, openLogin } from '../auth'

const categories = ref([])
const sources = ref([])
const transactions = ref([])
const month = ref(currentMonth())
const type = ref('expense')
const filterType = ref('')
const filterSource = ref(null)
const form = ref({ amount: '', category_id: null, payment_source_id: null, note: '', occurred_at: toLocalInput(new Date()) })
const loading = ref(false)

const filteredCats = computed(() =>
  categories.value.filter(c => c.type === type.value)
)

async function loadCategories() {
  const { data } = await http.get('/categories')
  categories.value = data
  if (!form.value.category_id && filteredCats.value.length) {
    form.value.category_id = filteredCats.value[0].id
  }
}
async function loadSources() {
  const { data } = await http.get('/payment-sources')
  sources.value = data
  if (!form.value.payment_source_id && sources.value.length) {
    form.value.payment_source_id = sources.value[0].id
  }
}
async function loadTransactions() {
  const params = { month: month.value }
  if (filterType.value) params.type = filterType.value
  if (filterSource.value) params.payment_source_id = filterSource.value
  const { data } = await http.get('/transactions', { params })
  transactions.value = data
}
async function submit() {
  if (!form.value.amount || !form.value.category_id) return
  loading.value = true
  try {
    await http.post('/transactions', {
      amount: Number(form.value.amount),
      type: type.value,
      category_id: form.value.category_id,
      payment_source_id: form.value.payment_source_id || null,
      note: form.value.note,
      occurred_at: new Date(form.value.occurred_at).toISOString(),
    })
    form.value.amount = ''
    form.value.note = ''
    await loadTransactions()
  } finally { loading.value = false }
}
async function remove(id) {
  await http.delete(`/transactions/${id}`)
  await loadTransactions()
}

function onTypeChange() {
  const c = filteredCats.value[0]
  form.value.category_id = c ? c.id : null
}

onMounted(async () => { await loadCategories(); await loadSources(); await loadTransactions() })

function currentMonth() {
  const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
}
function toLocalInput(d) {
  const p = n => String(n).padStart(2,'0')
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
}
function fmt(n) { return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function catOf(id) { return categories.value.find(c => c.id === id) }
function srcOf(id) { return sources.value.find(s => s.id === id) }
</script>

<template>
  <div class="stack">
    <div v-if="!isLoggedIn" class="ro-banner">
      🔒 当前为<strong>只读模式</strong>，登录后可记账 / 删除。
      <button class="link" @click="openLogin">去登录</button>
    </div>
    <section class="card">
      <h3 class="title">记一笔</h3>
      <div class="type-toggle">
        <button :class="{ on: type==='expense' }" @click="type='expense'; onTypeChange()">支出</button>
        <button :class="{ on: type==='income' }" @click="type='income'; onTypeChange()">收入</button>
      </div>
      <div class="grid">
        <input v-model.number="form.amount" type="number" step="0.01" placeholder="金额" />
        <select v-model="form.category_id">
          <option v-for="c in filteredCats" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
        </select>
      </div>
      <div class="grid">
        <select v-model="form.payment_source_id">
          <option :value="null">选择支付源</option>
          <option v-for="s in sources" :key="s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
        </select>
        <input v-model="form.note" placeholder="备注（可选）" />
      </div>
      <input v-model="form.occurred_at" type="datetime-local" class="full" />
      <button class="btn block" :disabled="loading" @click="!isLoggedIn ? openLogin() : submit()">添加记录</button>
    </section>

    <section class="card">
      <div class="row spread">
        <h3 class="title" style="margin:0">明细</h3>
        <input v-model="month" type="month" @change="loadTransactions" />
      </div>
      <div class="filters">
        <select v-model="filterType" @change="loadTransactions">
          <option value="">全部类型</option>
          <option value="income">收入</option>
          <option value="expense">支出</option>
        </select>
        <select v-model="filterSource" @change="loadTransactions">
          <option :value="null">全部支付源</option>
          <option v-for="s in sources" :key="s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
        </select>
        <button class="btn ghost small" @click="filterType=''; filterSource=null; loadTransactions()">重置</button>
      </div>
      <p v-if="!transactions.length" class="muted">本月还没有记录~</p>
      <ul class="list">
        <li v-for="t in transactions" :key="t.id" class="item">
          <span class="ico">{{ catOf(t.category_id)?.icon || '💰' }}</span>
          <div class="meta">
            <div class="name">{{ catOf(t.category_id)?.name || '未分类' }}
              <span class="muted small">· {{ srcOf(t.payment_source_id)?.icon || '💳' }} {{ srcOf(t.payment_source_id)?.name || '无支付源' }}<template v-if="t.note"> · {{ t.note }}</template></span>
            </div>
            <div class="muted small">{{ new Date(t.occurred_at).toLocaleString('zh-CN') }}</div>
          </div>
          <span :class="t.type" class="amt">{{ t.type==='income'?'+':'-' }}{{ fmt(t.amount) }}</span>
          <button class="btn ghost small" @click="!isLoggedIn ? openLogin() : remove(t.id)">删</button>
        </li>
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
.type-toggle { display: flex; gap: 8px; margin-bottom: 12px; }
.type-toggle button {
  flex: 1; padding: 9px; border-radius: 10px; border: 1px solid var(--border);
  background: #fff; font-weight: 600; color: var(--muted);
}
.type-toggle button.on { background: var(--primary); color: #fff; border-color: var(--primary); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.full { width: 100%; margin-bottom: 10px; }
.btn.block { width: 100%; margin-top: 4px; }
.list { list-style: none; padding: 0; margin: 10px 0 0; }
.filters { display: flex; gap: 8px; margin: 14px 0 4px; flex-wrap: wrap; }
.filters select { flex: 1; min-width: 120px; }
.item { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.item:last-child { border-bottom: none; }
.ico { font-size: 22px; width: 38px; height: 38px; display: grid; place-items: center; background: var(--bg); border-radius: 10px; }
.meta { flex: 1; }
.name { font-weight: 600; }
.small { font-size: 12px; }
.amt { font-weight: 700; }
.btn.small { padding: 5px 10px; font-size: 12px; }
</style>
