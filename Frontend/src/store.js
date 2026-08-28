import { reactive } from 'vue'

export const ui = reactive({ showLogin: false })
export const authState = reactive({
  token: localStorage.getItem('cat_token') || '',
  user: null,
})
