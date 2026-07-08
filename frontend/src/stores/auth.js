import { defineStore } from 'pinia'
import api, { setTokens, clearTokens, getAccessToken } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: getAccessToken(),
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isVerified: (state) => !!state.user?.is_verified,
  },
  actions: {
    async login(username_or_email, password) {
      const { data } = await api.post('/auth/login', { username_or_email, password })
      setTokens(data)
      this.accessToken = data.access_token
      await this.fetchMe()
    },
    async register(payload) {
      const { data } = await api.post('/auth/register', payload)
      return data
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.user = data
      return data
    },
    async updateMe(payload) {
      const { data } = await api.patch('/users/me', payload)
      this.user = data
      return data
    },
    logout() {
      clearTokens()
      this.user = null
      this.accessToken = null
    },
  },
})
