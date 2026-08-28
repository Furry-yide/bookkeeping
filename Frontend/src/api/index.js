import axios from 'axios'
import { ui, authState } from '../store'

const http = axios.create({ baseURL: '/api' })

http.interceptors.request.use((cfg) => {
  if (authState.token) cfg.headers.Authorization = `Bearer ${authState.token}`
  return cfg
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401) {
      authState.token = ''
      authState.user = null
      localStorage.removeItem('cat_token')
      ui.showLogin = true
    }
    return Promise.reject(err)
  }
)

export default http
