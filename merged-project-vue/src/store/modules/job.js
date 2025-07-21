import { getJobList, getJobDetail, getJobRecommend } from '@/api/job'

const state = {
  jobList: [],
  currentJob: null,
  recommendJobs: [],
  searchParams: {
    keyword: '',
    location: '',
    category: '',
    salary: '',
    experience: '',
    education: '',
    page: 1,
    limit: 10
  },
  totalCount: 0
}

const mutations = {
  SET_JOB_LIST: (state, jobList) => {
    state.jobList = jobList
  },
  SET_CURRENT_JOB: (state, job) => {
    state.currentJob = job
  },
  SET_RECOMMEND_JOBS: (state, jobs) => {
    state.recommendJobs = jobs
  },
  SET_SEARCH_PARAMS: (state, params) => {
    state.searchParams = { ...state.searchParams, ...params }
  },
  SET_TOTAL_COUNT: (state, count) => {
    state.totalCount = count
  },
  CLEAR_JOB_LIST: (state) => {
    state.jobList = []
    state.totalCount = 0
  }
}

const actions = {
  // 获取职位列表
  getJobList({ commit, state }) {
    return new Promise((resolve, reject) => {
      getJobList(state.searchParams)
        .then(response => {
          const { data } = response
          commit('SET_JOB_LIST', data.items)
          commit('SET_TOTAL_COUNT', data.total)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取职位详情
  getJobDetail({ commit }, jobId) {
    return new Promise((resolve, reject) => {
      getJobDetail(jobId)
        .then(response => {
          const { data } = response
          commit('SET_CURRENT_JOB', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取推荐职位
  getRecommendJobs({ commit }, userId) {
    return new Promise((resolve, reject) => {
      getJobRecommend(userId)
        .then(response => {
          const { data } = response
          commit('SET_RECOMMEND_JOBS', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 更新搜索参数
  updateSearchParams({ commit, dispatch }, params) {
    commit('SET_SEARCH_PARAMS', params)
    return dispatch('getJobList')
  },

  // 清空职位列表
  clearJobList({ commit }) {
    commit('CLEAR_JOB_LIST')
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 