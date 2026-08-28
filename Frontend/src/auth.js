import { computed } from 'vue'
import http from './api'
import { ui, authState } from './store'

const isLoggedIn = computed(() => !!authState.token)

async function login(username, password) {
  const { data } = await http.post('/auth/login', { username, password })
  authState.token = data.access_token
  localStorage.setItem('cat_token', authState.token)
  ui.showLogin = false
  await loadMe()
}
async function loadMe() {
  if (!isLoggedIn.value) return
  try {
    const { data } = await http.get('/auth/me')
    authState.user = data.username
  } catch {
    authState.user = null
  }
}
function logout() {
  authState.token = ''
  authState.user = null
  localStorage.removeItem('cat_token')
}
function openLogin() { ui.showLogin = true }

export { authState, isLoggedIn, login, logout, openLogin, loadMe }
