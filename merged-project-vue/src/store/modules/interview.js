import { 
  getInterviewList, 
  getInterviewDetail, 
  startInterview, 
  submitInterviewAnswer,
  getInterviewReport,
  getInterviewRanking
} from '@/api/interview'

const state = {
  interviewList: [],
  currentInterview: null,
  currentQuestion: null,
  interviewReport: null,
  interviewRanking: [],
  interviewProgress: {
    totalQuestions: 0,
    currentIndex: 0,
    completed: false
  }
}

const mutations = {
  SET_INTERVIEW_LIST: (state, list) => {
    state.interviewList = list
  },
  SET_CURRENT_INTERVIEW: (state, interview) => {
    state.currentInterview = interview
  },
  SET_CURRENT_QUESTION: (state, question) => {
    state.currentQuestion = question
  },
  SET_INTERVIEW_REPORT: (state, report) => {
    state.interviewReport = report
  },
  SET_INTERVIEW_RANKING: (state, ranking) => {
    state.interviewRanking = ranking
  },
  SET_INTERVIEW_PROGRESS: (state, progress) => {
    state.interviewProgress = { ...state.interviewProgress, ...progress }
  },
  CLEAR_CURRENT_INTERVIEW: (state) => {
    state.currentInterview = null
    state.currentQuestion = null
    state.interviewProgress = {
      totalQuestions: 0,
      currentIndex: 0,
      completed: false
    }
  }
}

const actions = {
  // 获取面试列表
  getInterviewList({ commit }, userId) {
    return new Promise((resolve, reject) => {
      getInterviewList(userId)
        .then(response => {
          const { data } = response
          commit('SET_INTERVIEW_LIST', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取面试详情
  getInterviewDetail({ commit }, interviewId) {
    return new Promise((resolve, reject) => {
      getInterviewDetail(interviewId)
        .then(response => {
          const { data } = response
          commit('SET_CURRENT_INTERVIEW', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 开始面试
  startInterview({ commit }, params) {
    return new Promise((resolve, reject) => {
      startInterview(params)
        .then(response => {
          const { data } = response
          commit('SET_CURRENT_INTERVIEW', data.interview)
          commit('SET_CURRENT_QUESTION', data.firstQuestion)
          commit('SET_INTERVIEW_PROGRESS', {
            totalQuestions: data.totalQuestions,
            currentIndex: 0,
            completed: false
          })
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 提交面试答案
  submitAnswer({ commit, state }, answer) {
    return new Promise((resolve, reject) => {
      submitInterviewAnswer({
        interviewId: state.currentInterview.id,
        questionId: state.currentQuestion.id,
        answer: answer
      })
        .then(response => {
          const { data } = response
          const newIndex = state.interviewProgress.currentIndex + 1
          const isCompleted = newIndex >= state.interviewProgress.totalQuestions
          
          commit('SET_INTERVIEW_PROGRESS', {
            currentIndex: newIndex,
            completed: isCompleted
          })
          
          if (!isCompleted) {
            commit('SET_CURRENT_QUESTION', data.nextQuestion)
          }
          
          resolve({
            completed: isCompleted,
            nextQuestion: data.nextQuestion,
            analysis: data.analysis
          })
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取面试报告
  getInterviewReport({ commit }, interviewId) {
    return new Promise((resolve, reject) => {
      getInterviewReport(interviewId)
        .then(response => {
          const { data } = response
          commit('SET_INTERVIEW_REPORT', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取面试排名
  getInterviewRanking({ commit }) {
    return new Promise((resolve, reject) => {
      getInterviewRanking()
        .then(response => {
          const { data } = response
          commit('SET_INTERVIEW_RANKING', data)
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 清空当前面试
  clearCurrentInterview({ commit }) {
    commit('CLEAR_CURRENT_INTERVIEW')
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 