<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../api'

const month = ref(currentMonth())
const budget = ref(null)
const form = ref({ limit_amount: '' })
const progress = ref(null)
const loading = ref(false)

async function load() {
  const { data } = await http.get('/budgets')
  budget.value = data.find(b => b.month === month.value) || null
  if (budget.value) form.value.limit_amount = budget.value.limit_amount
  await loadProgress()
}
async function loadProgress() {
  const { data } = await http.get('/stats/budget-progress', { params: { month: month.value } })
  progress.value = data
}
async function save() {
  if (!form.value.limit_amount) return
  loading.value = true
  try {
    if (budget.value) {
      await http.put(`/budgets/${budget.value.id}`, { month: month.value, limit_amount: Number(form.value.limit_amount) })
    } else {
      await http.post('/budgets', { month: month.value, limit_amount: Number(form.value.limit_amount) })
    }
    await load()
  } finally { loading.value = false }
}

const percent = computed(() => progress.value?.percent || 0)
const barColor = computed(() => {
  const p = percent.value
  if (p >= 100) return 'var(--expense)'
  if (p >= 80) return '#ffce54'
  return 'var(--income)'
})

onMounted(load)

function currentMonth() {
  const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
}
function fmt(n) { return Number(n||0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
</script>

<template>
  <div class="stack">
    <section class="card">
      <div class="row spread">
        <h3 class="title" style="margin:0">月度预算</h3>
        <input v-model="month" type="month" @change="load" />
      </div>
      <div class="row" style="margin-top:12px">
        <input v-model.number="form.limit_amount" type="number" step="0.01" placeholder="设置本月支出预算" style="flex:1" />
        <button class="btn" :disabled="loading" @click="save">保存</button>
      </div>
    </section>

    <section class="card" v-if="progress?.has_budget">
      <div class="row spread">
        <h3 class="title" style="margin:0">执行进度</h3>
        <span :class="progress.over?'expense':'income'" style="font-weight:700">
          {{ progress.over ? '已超支' : '预算内' }}
        </span>
      </div>
      <div class="nums">
        <div><span class="muted small">预算</span> {{ fmt(progress.limit_amount) }}</div>
        <div><span class="muted small">已花</span> <span class="expense">{{ fmt(progress.spent) }}</span></div>
        <div><span class="muted small">剩余</span> <span :class="progress.remaining>=0?'income':'expense'">{{ fmt(progress.remaining) }}</span></div>
      </div>
      <div class="bar">
        <div class="fill" :style="{ width: Math.min(percent,100)+'%', background: barColor }"></div>
      </div>
      <div class="muted small" style="text-align:right;margin-top:6px">已使用 {{ percent }}%</div>
    </section>

    <section class="card" v-else>
      <p class="muted">本月还没有设置预算，先在上方设置一个吧~</p>
    </section>
  </div>
</template>

<style scoped>
.stack { display: flex; flex-direction: column; gap: 14px; }
.nums { display: flex; gap: 16px; margin: 14px 0 10px; font-size: 15px; font-weight: 600; flex-wrap: wrap; }
.bar { height: 14px; background: var(--bg); border-radius: 99px; overflow: hidden; }
.fill { height: 100%; border-radius: 99px; transition: width 0.4s; }
.small { font-size: 12px; }
</style>
