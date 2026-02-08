import axios from 'axios'

export class OpenCngsmAPI {
  constructor() {
    this.baseURL = '/api'
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Add token to requests
    this.client.interceptors.request.use(config => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
  }

  async login(userId, secret) {
    const response = await this.client.post('/auth/login', { user_id: userId, secret })
    return response.data
  }

  async getStatus() {
    const response = await this.client.get('/status')
    return response.data
  }

  async sendMessage(message, userId) {
    const response = await this.client.post('/message', { message, user_id: userId })
    return response.data
  }

  async getSkills() {
    const response = await this.client.get('/skills')
    return response.data
  }
}
