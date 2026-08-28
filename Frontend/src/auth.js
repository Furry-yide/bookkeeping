import { reactive, computed } from 'vue'
import http from './api'
import { ui } from './store'

const state = reactive({ user: null })
const isLoggedIn = computed(() => !!localStorage.getItem('cat_token'))

async function login(username, password) {
  const { data } = await http.post('/auth/login', { username, password })
  localStorage.setItem('cat_token', data.access_token)
  ui.showLogin = false
  await loadMe()
}
async function loadMe() {
  if (!isLoggedIn.value) return
  try {
    const { data } = await http.get('/auth/me')
    state.user = data.username
  } catch {
    state.user = null
  }
}
function logout() {
  localStorage.removeItem('cat_token')
  state.user = null
}
function openLogin() { ui.showLogin = true }

export { state, isLoggedIn, login, logout, openLogin, loadMe }
