/**
 * Snackbar模块，用于显示消息通知
 */

// 状态
const state = {
  show: false,
  content: '',
  color: 'info', // 'success', 'info', 'warning', 'error'
  timeout: 5000,
  multiLine: false
}

// getter
const getters = {
  show: state => state.show,
  content: state => state.content,
  color: state => state.color,
  timeout: state => state.timeout,
  multiLine: state => state.multiLine
}

// actions
const actions = {
  /**
   * 显示消息
   * @param {Object} context - Vuex上下文
   * @param {Object} payload - 消息配置
   * @param {String} payload.content - 消息内容
   * @param {String} payload.color - 消息颜色，可选值：'success', 'info', 'warning', 'error'
   * @param {Number} payload.timeout - 显示时间，单位毫秒
   * @param {Boolean} payload.multiLine - 是否多行显示
   */
  showMessage({ commit }, payload) {
    commit('SET_CONTENT', payload.content || '')
    commit('SET_COLOR', payload.color || 'info')
    commit('SET_TIMEOUT', payload.timeout || 5000)
    commit('SET_MULTILINE', payload.multiLine || false)
    commit('SHOW_SNACKBAR')
    
    // 自动隐藏
    setTimeout(() => {
      commit('HIDE_SNACKBAR')
    }, payload.timeout || 5000)
  },
  
  /**
   * 隐藏消息
   */
  hideMessage({ commit }) {
    commit('HIDE_SNACKBAR')
  }
}

// mutations
const mutations = {
  SHOW_SNACKBAR(state) {
    state.show = true
  },
  
  HIDE_SNACKBAR(state) {
    state.show = false
  },
  
  SET_CONTENT(state, content) {
    state.content = content
  },
  
  SET_COLOR(state, color) {
    state.color = color
  },
  
  SET_TIMEOUT(state, timeout) {
    state.timeout = timeout
  },
  
  SET_MULTILINE(state, multiLine) {
    state.multiLine = multiLine
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 