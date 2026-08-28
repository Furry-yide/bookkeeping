import { createRouter, createWebHistory } from 'vue-router'
import Ledger from '../views/Ledger.vue'
import Stats from '../views/Stats.vue'
import Budget from '../views/Budget.vue'

const routes = [
  { path: '/', redirect: '/ledger' },
  { path: '/ledger', name: 'ledger', component: Ledger, meta: { title: '记账' } },
  { path: '/stats', name: 'stats', component: Stats, meta: { title: '统计' } },
  { path: '/budget', name: 'budget', component: Budget, meta: { title: '预算' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
