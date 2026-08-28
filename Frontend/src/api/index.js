import axios from 'axios'
import { ui } from '../store'

const http = axios.create({ baseURL: '/api' })

http.interceptors.request.use((cfg) => {
  const t = localStorage.getItem('cat_token')
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('cat_token')
      ui.showLogin = true
    }
    return Promise.reject(err)
  }
)

export default http
