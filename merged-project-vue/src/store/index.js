import Vue from 'vue'
import Vuex from 'vuex'

// 导入模块
import user from './modules/user'
import job from './modules/job'
import interview from './modules/interview'
import snackbar from './modules/snackbar'

Vue.use(Vuex)

// 根状态
const state = {
  appName: '职位与面试系统',
  sidebar: {
    opened: localStorage.getItem('sidebarStatus') ? !!+localStorage.getItem('sidebarStatus') : true
  }
}

// 根mutations
const mutations = {
  TOGGLE_SIDEBAR: state => {
    state.sidebar.opened = !state.sidebar.opened
    if (state.sidebar.opened) {
      localStorage.setItem('sidebarStatus', 1)
    } else {
      localStorage.setItem('sidebarStatus', 0)
    }
  }
}

// 根actions
const actions = {
  toggleSidebar({ commit }) {
    commit('TOGGLE_SIDEBAR')
  }
}

// 根getters
const getters = {
  sidebar: state => state.sidebar
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  modules: {
    user,
    job,
    interview,
    snackbar
  }
}) 