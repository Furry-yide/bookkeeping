<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../api'

const month = ref(currentMonth())
const selectedDay = ref(currentDate())
const summary = ref({ total_income: 0, total_expense: 0, balance: 0, by_category: [] })
const sourceBalances = ref([])
const monthTransactions = ref([])

const palette = ['#ff9a3c','#ff5b5b','#2ecc71','#5b8def','#a66bff','#ffce54','#3ec9c9','#ff7eb6','#9aa0b4']
const total = computed(() => summary.value.by_category.reduce((s, c) => s + c.total, 0))

const calendarDays = computed(() => {
  const [y, m] = month.value.split('-').map(Number)
  const firstDay = new Date(y, m - 1, 1).getDay()
  const daysInMonth = new Date(y, m, 0).getDate()
  const expenseByDay = {}
  const incomeByDay = {}
  monthTransactions.value.forEach(t => {
    const d = t.occurred_at.slice(8, 10)
    if (t.type === 'expense') expenseByDay[d] = (expenseByDay[d] || 0) + t.amount
    else if (t.type === 'income') incomeByDay[d] = (incomeByDay[d] || 0) + t.amount
  })
  const maxAmt = Math.max(...Object.values(expenseByDay), ...Object.values(incomeByDay), 1)
  const days = []
  for (let i = 0; i < firstDay; i++) days.push({ empty: true })
  for (let d = 1; d <= daysInMonth; d++) {
    const dd = String(d).padStart(2, '0')
    const dateStr = `${month.value}-${dd}`
    const expense = expenseByDay[dd] || 0
    const income = incomeByDay[dd] || 0
    const expenseIntensity = expense > 0 ? Math.min(expense / maxAmt, 1) : 0
    const incomeIntensity = income > 0 ? Math.min(income / maxAmt, 1) : 0
    days.push({ day: d, dateStr, expense, income, expenseIntensity, incomeIntensity, empty: false })
  }
  return days
})

const selectedDayTransactions = computed(() => {
  const prefix = selectedDay.value.slice(0, 10)
  return monthTransactions.value.filter(t => t.occurred_at.slice(0, 10) === prefix)
})
const selectedDayTotal = computed(() => selectedDayTransactions.value.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0))
const selectedDayIncome = computed(() => selectedDayTransactions.value.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0))
const selectedDayCount = computed(() => selectedDayTransactions.value.length)
const showDayDetail = ref(false)
const dayByCategory = computed(() => {
  const map = {}
  selectedDayTransactions.value.filter(t => t.type === 'expense').forEach(t => {
    const name = t.category?.name || '其他'
    const icon = t.category?.icon || '📝'
    if (!map[name]) map[name] = { name, icon, total: 0, count: 0 }
    map[name].total += t.amount
    map[name].count++
  })
  return Object.values(map).sort((a, b) => b.total - a.total)
})
const dayTotalForChart = computed(() => dayByCategory.value.reduce((s, c) => s + c.total, 0))
const daySegments = computed(() => {
  let acc = 0
  const t = dayTotalForChart.value || 1
  return dayByCategory.value.map((c, i) => {
    const frac = c.total / t
    const seg = { ...c, color: palette[i % palette.length], frac, offset: acc }
    acc += frac
    return seg
  })
})
const dayDonut = computed(() => {
  const r = 40, c = 2 * Math.PI * r
  return daySegments.value.map(s => ({
    ...s,
    dash: `${s.frac * c} ${c}`,
    offset: -s.offset * c,
  }))
})

async function load() {
  const [{ data: summaryData }, { data: sb }, { data: txs }] = await Promise.all([
    http.get('/stats/summary', { params: { month: month.value } }),
    http.get('/stats/source-balances'),
    http.get('/transactions', { params: { month: month.value } }),
  ])
  summary.value = summaryData
  sourceBalances.value = sb
  monthTransactions.value = txs
}
async function loadDay() {
  const { data } = await http.get('/transactions', { params: { day: selectedDay.value } })
  monthTransactions.value = data
}
function selectDay(dayObj) {
  if (dayObj.empty) return
  selectedDay.value = dayObj.dateStr
}
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

async function exportCsv() {
  const [{ data: txs }, { data: cats }, { data: srcs }] = await Promise.all([
    http.get('/transactions', { params: { month: month.value } }),
    http.get('/categories'),
    http.get('/payment-sources'),
  ])
  const catMap = Object.fromEntries(cats.map(c => [c.id, c]))
  const srcMap = Object.fromEntries(srcs.map(s => [s.id, s]))
  const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`
  const rows = [['日期', '类型', '分类', '支付源', '金额', '备注']]
  txs.forEach(t => {
    let typeLabel = t.type === 'income' ? '收入' : (t.type === 'expense' ? '支出' : '转账')
    let catName = catMap[t.category_id]?.name || ''
    let srcName = ''
    if (t.type === 'transfer') {
      catName = '转账'
      const f = t.payment_source_id != null ? srcMap[t.payment_source_id]?.name : ''
      const to = t.transfer_to_id != null ? srcMap[t.transfer_to_id]?.name : ''
      srcName = `${f} → ${to}`
    } else {
      srcName = t.payment_source_id != null ? (srcMap[t.payment_source_id]?.name || '') : ''
    }
    rows.push([
      new Date(t.occurred_at).toLocaleString('zh-CN'),
      typeLabel,
      catName,
      srcName,
      t.amount,
      t.note || '',
    ])
  })
  const csv = '\uFEFF' + rows.map(r => r.map(esc).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `账本流水_${month.value}.csv`
  a.click()
}

onMounted(load)

function currentMonth() {
  const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`
}
function currentDate() {
  const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
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
        <h3 class="title" style="margin:0">日支出分类</h3>
        <span class="muted small">{{ selectedDay }}</span>
      </div>
      <div v-if="dayDonut.length" class="chart-wrap">
        <svg viewBox="0 0 100 100" class="donut donut-sm">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#eee" stroke-width="14" />
          <circle
            v-for="(s, i) in dayDonut" :key="i"
            cx="50" cy="50" r="40" fill="none"
            :stroke="s.color" stroke-width="14"
            :stroke-dasharray="s.dash"
            :stroke-dashoffset="s.offset"
            transform="rotate(-90 50 50)"
          />
        </svg>
        <div class="legend">
          <div v-for="(s, i) in dayDonut" :key="i" class="lg">
            <span class="dot" :style="{ background: s.color }"></span>
            <span class="lg-name">{{ s.icon }} {{ s.name }}</span>
            <span class="muted small">{{ s.count }}笔 {{ (s.frac*100).toFixed(1) }}%</span>
            <span class="expense">{{ fmt(s.total) }}</span>
          </div>
        </div>
      </div>
      <p v-else class="muted" style="text-align:center;padding:16px 0">该日暂无支出</p>
    </section>

    <section class="card">
      <div class="row spread">
        <h3 class="title" style="margin:0">月度日历</h3>
        <input v-model="month" type="month" @change="load" />
      </div>
      <div class="cal-header">
        <span v-for="w in ['日','一','二','三','四','五','六']" :key="w">{{ w }}</span>
      </div>
      <div class="cal-grid">
        <div
          v-for="(d, i) in calendarDays" :key="i"
          class="cal-cell"
          :class="{ empty: d.empty, selected: d.dateStr === selectedDay }"
          :style="d.expense > 0 ? { background: `rgba(255,91,91,${0.08 + d.expenseIntensity * 0.5})` } : d.income > 0 ? { background: `rgba(46,204,113,${0.08 + d.incomeIntensity * 0.5})` } : {}"
          @click="selectDay(d)"
        >
          <template v-if="!d.empty">
            <span class="cal-day">{{ d.day }}</span>
            <span v-if="d.expense > 0" class="cal-amt expense">{{ fmt(d.expense) }}</span>
            <span v-if="d.income > 0" class="cal-amt income">{{ fmt(d.income) }}</span>
          </template>
        </div>
      </div>
      <div class="day-detail">
        <div class="row spread toggle-header" @click="showDayDetail = !showDayDetail">
          <h4 class="title" style="margin:0;font-size:14px">{{ selectedDay }} 明细</h4>
          <span class="muted small">
            <span v-if="selectedDayIncome > 0" class="income">收入 {{ fmt(selectedDayIncome) }}</span>
            <span v-if="selectedDayIncome > 0 && selectedDayTotal > 0"> · </span>
            <span v-if="selectedDayTotal > 0" class="expense">支出 {{ fmt(selectedDayTotal) }}</span>
            · {{ selectedDayCount }} 笔
            <span class="toggle-arrow">{{ showDayDetail ? '▲' : '▼' }}</span>
          </span>
        </div>
        <div v-if="showDayDetail && selectedDayTransactions.length" class="day-list">
          <div v-for="t in selectedDayTransactions" :key="t.id" class="day-row">
            <span class="day-ico" v-if="t.type==='transfer'">🔁</span>
            <span class="day-ico" v-else-if="t.type==='income'">{{ t.category?.icon || '💰' }}</span>
            <span class="day-ico" v-else>{{ t.category?.icon || '📝' }}</span>
            <span class="day-info">
              <span class="day-cat">{{ t.type==='transfer' ? '转账' : (t.category?.name || '') }}</span>
              <span class="day-src muted small">{{ t.payment_source?.name || '' }}<template v-if="t.transfer_to"> → {{ t.transfer_to.name }}</template> · {{ new Date(t.occurred_at).toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit'}) }}</span>
              <span v-if="t.note" class="day-note muted small">{{ t.note }}</span>
            </span>
            <span v-if="t.type==='transfer'" class="day-amt transfer">⇄ {{ fmt(t.amount) }}</span>
            <span v-else :class="t.type" class="day-amt">{{ t.type==='income'?'+':'-' }}{{ fmt(t.amount) }}</span>
          </div>
        </div>
        <p v-else-if="showDayDetail && !selectedDayTransactions.length" class="muted" style="text-align:center;padding:20px 0">该日暂无记录</p>
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

    <section class="card">
      <h3 class="title">支付源余额</h3>
      <div class="src-list">
        <div v-for="s in sourceBalances" :key="s.id" class="src-row">
          <span class="src-ico">{{ s.icon }}</span>
          <span class="src-name">{{ s.name }}</span>
          <span class="muted small">收 {{ fmt(s.income) }} / 支 {{ fmt(s.expense) }}</span>
          <span class="src-bal" :class="s.balance>=0?'income':'expense'">{{ fmt(s.balance) }}</span>
        </div>
        <p v-if="!sourceBalances.length" class="muted">暂无支付源数据~</p>
      </div>
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
.donut-sm { width: 120px; height: 120px; }
.legend { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 8px; }
.lg { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.lg-name { flex: 1; }
.toggle-header { cursor: pointer; user-select: none; }
.toggle-header:hover { opacity: 0.8; }
.toggle-arrow { margin-left: 8px; font-size: 10px; }
.btn.small { padding: 5px 10px; font-size: 12px; }
.small { font-size: 12px; }
.src-list { display: flex; flex-direction: column; gap: 4px; }
.src-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.src-row:last-child { border-bottom: none; }
.src-ico { font-size: 20px; width: 36px; height: 36px; display: grid; place-items: center; background: var(--bg); border-radius: 10px; }
.src-name { font-weight: 600; width: 90px; }
.src-bal { margin-left: auto; font-weight: 800; font-size: 16px; }
.day-stats { display: flex; gap: 10px; margin-top: 14px; }
.day-list { margin-top: 10px; display: flex; flex-direction: column; }
.day-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.day-row:last-child { border-bottom: none; }
.day-ico { font-size: 20px; width: 36px; height: 36px; display: grid; place-items: center; background: var(--bg); border-radius: 10px; flex: none; }
.day-info { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.day-cat { font-weight: 600; font-size: 14px; }
.day-src { font-size: 12px; }
.day-note { font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.day-amt { font-weight: 800; font-size: 15px; flex: none; }
.cal-header { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: 12px; color: var(--muted); margin-top: 14px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 8px; }
.cal-cell { aspect-ratio: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 10px; cursor: pointer; transition: all 0.15s; position: relative; }
.cal-cell:hover { background: var(--border); }
.cal-cell.empty { cursor: default; }
.cal-cell.empty:hover { background: transparent; }
.cal-cell.selected { outline: 2px solid var(--primary); }
.cal-day { font-size: 14px; font-weight: 600; }
.cal-amt { font-size: 10px; margin-top: 1px; font-weight: 700; }
.cal-amt.expense { color: #ff5b5b; }
.cal-amt.income { color: #2ecc71; }
.day-detail { margin-top: 16px; }
</style>
