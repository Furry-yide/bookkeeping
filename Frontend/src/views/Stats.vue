<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../api'

const month = ref(currentMonth())
const summary = ref({ total_income: 0, total_expense: 0, balance: 0, by_category: [] })

const palette = ['#ff9a3c','#ff5b5b','#2ecc71','#5b8def','#a66bff','#ffce54','#3ec9c9','#ff7eb6','#9aa0b4']
const total = computed(() => summary.value.by_category.reduce((s, c) => s + c.total, 0))
const segments = computed(() => {
  let acc = 0
  const t = total.value || 1
  return summary.value.by_category.map((c, i) => {
    const frac = c.total / t
    const seg = { ...c, color: palette[i % palette.length], frac, offset: acc }
    acc += frac
    return seg
  })
})
const donut = computed(() => {
  const r = 60, c = 2 * Math.PI * r
  return segments.value.map(s => ({
    ...s,
    dash: `${s.frac * c} ${c}`,
    offset: -s.offset * c,
  }))
})

async function load() {
  const { data } = await http.get('/stats/summary', { params: { month: month.value } })
  summary.value = data
}
function exportCsv() {
  const rows = [['分类','金额']]
  summary.value.by_category.forEach(c => rows.push([c.name, c.total]))
  rows.push(['总收入', summary.value.total_income])
  rows.push(['总支出', summary.value.total_expense])
  const csv = '\uFEFF' + rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `账本统计_${month.value}.csv`
  a.click()
}

onMounted(load)

function currentMonth() {
  const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
}
function fmt(n) { return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
</script>

<template>
  <div class="stack">
    <section class="card">
      <div class="row spread">
        <h3 class="title" style="margin:0">本月概览</h3>
        <input v-model="month" type="month" @change="load" />
      </div>
      <div class="kpis">
        <div class="kpi"><div class="lbl">收入</div><div class="income v">{{ fmt(summary.total_income) }}</div></div>
        <div class="kpi"><div class="lbl">支出</div><div class="expense v">{{ fmt(summary.total_expense) }}</div></div>
        <div class="kpi"><div class="lbl">结余</div><div class="v" :class="summary.balance>=0?'income':'expense'">{{ fmt(summary.balance) }}</div></div>
      </div>
    </section>

    <section class="card">
      <div class="row spread">
        <h3 class="title" style="margin:0">支出分类</h3>
        <button class="btn ghost small" @click="exportCsv">导出 CSV</button>
      </div>
      <div v-if="summary.by_category.length" class="chart-wrap">
        <svg viewBox="0 0 160 160" class="donut">
          <circle cx="80" cy="80" r="60" fill="none" stroke="#eee" stroke-width="22" />
          <circle
            v-for="(s, i) in donut" :key="i"
            cx="80" cy="80" r="60" fill="none"
            :stroke="s.color" stroke-width="22"
            :stroke-dasharray="s.dash"
            :stroke-dashoffset="s.offset"
            transform="rotate(-90 80 80)"
          />
        </svg>
        <div class="legend">
          <div v-for="(s, i) in donut" :key="i" class="lg">
            <span class="dot" :style="{ background: s.color }"></span>
            <span class="lg-name">{{ s.icon }} {{ s.name }}</span>
            <span class="muted small">{{ (s.frac*100).toFixed(1) }}%</span>
            <span class="expense">{{ fmt(s.total) }}</span>
          </div>
        </div>
      </div>
      <p v-else class="muted">本月暂无支出数据~</p>
    </section>
  </div>
</template>

<style scoped>
.stack { display: flex; flex-direction: column; gap: 14px; }
.kpis { display: flex; gap: 10px; margin-top: 14px; }
.kpi { flex: 1; text-align: center; background: var(--bg); border-radius: 12px; padding: 12px 6px; }
.lbl { color: var(--muted); font-size: 12px; }
.v { font-size: 18px; font-weight: 800; margin-top: 4px; }
.chart-wrap { display: flex; gap: 20px; align-items: center; margin-top: 14px; flex-wrap: wrap; }
.donut { width: 160px; height: 160px; flex: none; }
.legend { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 8px; }
.lg { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.lg-name { flex: 1; }
.btn.small { padding: 5px 10px; font-size: 12px; }
.small { font-size: 12px; }
</style>
