import { login, logout, getUserInfo } from '@/api/user'
import { clearTempData, clearUserData } from '@/utils/localStorage'

const state = {
  token: localStorage.getItem('token'),
  userId: localStorage.getItem('userId'),
  username: localStorage.getItem('username'),
  avatar: localStorage.getItem('avatar'),
  roles: [],
  permissions: []
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
    localStorage.setItem('token', token)
  },
  SET_USER_ID: (state, userId) => {
    state.userId = userId
    localStorage.setItem('userId', userId)
  },
  SET_USERNAME: (state, username) => {
    state.username = username
    localStorage.setItem('username', username)
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
    localStorage.setItem('avatar', avatar)
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  },
  SET_PERMISSIONS: (state, permissions) => {
    state.permissions = permissions
  },
  CLEAR_USER: (state) => {
    state.token = ''
    state.userId = ''
    state.username = ''
    state.avatar = ''
    state.roles = []
    state.permissions = []

    // 清理用户相关数据
    clearUserData()

    // 清理所有临时数据
    clearTempData()

    console.log('用户数据和临时数据已清理完成')
  }
}

const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password })
        .then(response => {
          const { data } = response
          commit('SET_TOKEN', data.token)
          commit('SET_USER_ID', data.userId)
          commit('SET_USERNAME', data.username)
          commit('SET_AVATAR', data.avatar)
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取用户信息
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getUserInfo(state.token)
        .then(response => {
          const { data } = response
          if (!data) {
            reject('获取用户信息失败，请重新登录')
          }
          
          const { roles, permissions } = data
          commit('SET_ROLES', roles)
          commit('SET_PERMISSIONS', permissions)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 用户登出
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout(state.token)
        .then(() => {
          commit('CLEAR_USER')
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 前端登出
  fedLogout({ commit }) {
    return new Promise(resolve => {
      commit('CLEAR_USER')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 