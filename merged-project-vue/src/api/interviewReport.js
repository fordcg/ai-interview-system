import request from '@/utils/request'

/**
 * 保存面试报告到数据库
 * @param {Object} reportData - 报告数据
 * @returns {Promise}
 */
export function saveInterviewReport(reportData) {
  return request({
    url: '/interview-report/save',
    method: 'post',
    data: reportData
  })
}

/**
 * 获取用户的报告列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getInterviewReportList(params = {}) {
  return request({
    url: '/interview-report/list',
    method: 'get',
    params
  })
}

/**
 * 获取特定报告详情
 * @param {number} reportId - 报告ID
 * @returns {Promise}
 */
export function getInterviewReportDetail(reportId) {
  return request({
    url: `/interview-report/${reportId}`,
    method: 'get'
  })
}

/**
 * 更新报告
 * @param {number} reportId - 报告ID
 * @param {Object} reportData - 更新的报告数据
 * @returns {Promise}
 */
export function updateInterviewReport(reportId, reportData) {
  return request({
    url: `/interview-report/${reportId}`,
    method: 'put',
    data: reportData
  })
}

/**
 * 删除报告
 * @param {number} reportId - 报告ID
 * @returns {Promise}
 */
export function deleteInterviewReport(reportId) {
  return request({
    url: `/interview-report/${reportId}`,
    method: 'delete'
  })
}

/**
 * 获取报告统计信息
 * @returns {Promise}
 */
export function getInterviewReportStats() {
  return request({
    url: '/interview-report/stats',
    method: 'get'
  })
}
