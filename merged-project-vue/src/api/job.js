// 移除 mockData 依赖
import request from '@/utils/request'
import axios from 'axios'

// 从本地JSON文件加载职位数据
export function loadLocalJobs() {
  return axios.get('/data/jobs.json')
    .then(response => {
      return {
        code: 200,
        message: '获取成功',
        data: {
          list: response.data,
          total: response.data.length,
          totalPages: Math.ceil(response.data.length / 10)
        }
      };
    })
    .catch(error => {
      console.error('加载本地职位数据失败:', error);
      return {
        code: 500,
        message: '加载本地职位数据失败',
        data: {
          list: [],
          total: 0,
          totalPages: 0
        }
      };
    });
}

// 从本地JSON文件加载城市列表
export function loadLocalCities() {
  return axios.get('/data/cities.json')
    .then(response => {
      return {
        code: 200,
        message: '获取成功',
        data: response.data
      };
    })
    .catch(error => {
      console.error('加载本地城市数据失败:', error);
      return {
        code: 500,
        message: '加载本地城市数据失败',
        data: []
      };
    });
}

// 从本地JSON文件加载薪资分布数据
export function loadLocalSalaryDistribution() {
  return axios.get('/data/salary_distribution.json')
    .then(response => {
      return {
        code: 200,
        message: '获取成功',
        data: response.data
      };
    })
    .catch(error => {
      console.error('加载本地薪资分布数据失败:', error);
      return {
        code: 500,
        message: '加载本地薪资分布数据失败',
        data: []
      };
    });
}

// 从本地JSON文件加载城市分布数据
export function loadLocalCityDistribution() {
  return axios.get('/data/city_distribution.json')
    .then(response => {
      return {
        code: 200,
        message: '获取成功',
        data: response.data
      };
    })
    .catch(error => {
      console.error('加载本地城市分布数据失败:', error);
      return {
        code: 500,
        message: '加载本地城市分布数据失败',
        data: []
      };
    });
}

// 获取职位列表
export function getJobList(params) {
  // 尝试使用本地数据代替API请求
  if (process.env.VUE_APP_USE_LOCAL_DATA === 'true') {
    return loadLocalJobs();
  }
  
  // 使用真实接口替代模拟数据
  return request({
    url: '/job/get',
    method: 'get',
    params
  });
}

// 获取职位详情
export function getJobDetail(id) {
  return request({
    url: `/job/detail/${id}`,
    method: 'get'
  });
}

// 搜索职位
export function searchJobs(params) {
  // 尝试使用本地数据代替API请求
  if (process.env.VUE_APP_USE_LOCAL_DATA === 'true') {
    return loadLocalJobs();
  }
  
  return request({
    url: '/api/jobs',
    method: 'get',
    params
  });
}

// 获取推荐职位
export function getJobRecommend(userId) {
  return request({
    url: '/job/recommend',
    method: 'get',
    params: { userId }
  });
}

// 获取热门职位
export function getHotJobs(limit = 10) {
  return request({
    url: '/job/hot',
    method: 'get',
    params: { limit }
  });
}

// 获取最新职位
export function getLatestJobs(limit = 10) {
  return request({
    url: '/job/latest',
    method: 'get',
    params: { limit }
  });
}

// 获取职位分类
export function getJobCategories() {
  return request({
    url: '/job/categories',
    method: 'get'
  });
}

// 获取职位统计数据
export function getJobStatistics(params) {
  return request({
    url: '/job/getPanel',
    method: 'get',
    params
  });
}

// 获取薪资分布数据
export function getSalaryDistribution(params) {
  // 尝试使用本地数据代替API请求
  if (process.env.VUE_APP_USE_LOCAL_DATA === 'true') {
    return loadLocalSalaryDistribution();
  }
  
  return request({
    url: '/job/getChart1',
    method: 'get',
    params
  });
}

// 获取地区职位分布
export function getRegionDistribution() {
  // 尝试使用本地数据代替API请求
  if (process.env.VUE_APP_USE_LOCAL_DATA === 'true') {
    return loadLocalCityDistribution();
  }
  
  return request({
    url: '/job/getAreaChart',
    method: 'get'
  });
}

// 获取技能词云数据
export function getSkillsWordCloud() {
  // 模拟技能词云
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      { name: 'JavaScript', value: 100 },
      { name: 'Vue', value: 90 },
      { name: 'React', value: 85 },
      { name: 'Java', value: 80 },
      { name: 'Python', value: 75 },
      { name: 'Spring Boot', value: 70 },
      { name: 'MySQL', value: 65 },
      { name: 'Redis', value: 60 },
      { name: 'Docker', value: 55 },
      { name: 'Kubernetes', value: 50 },
      { name: 'TypeScript', value: 45 },
      { name: 'Node.js', value: 40 },
      { name: 'Flutter', value: 35 },
      { name: 'Go', value: 30 }
    ]
  });
}

// 获取职位趋势数据
export function getJobTrends(params) {
  // 模拟趋势数据
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      dates: ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05'],
      trends: [
        {
          name: '前端开发',
          data: [120, 132, 145, 160, 178]
        },
        {
          name: '后端开发',
          data: [140, 152, 165, 175, 188]
        },
        {
          name: '数据分析',
          data: [60, 68, 75, 82, 90]
        }
      ]
    }
  });
}

// 申请职位
export function applyJob(data) {
  return request({
    url: '/job/apply',
    method: 'post',
    data
  });
}

// 获取用户申请记录
export function getUserApplications(userId) {
  return request({
    url: '/job/applications',
    method: 'get',
    params: { userId }
  });
}

// 获取相似职位
export function getSimilarJobs(jobId, limit = 5) {
  return request({
    url: '/job/similar',
    method: 'get',
    params: { jobId, limit }
  });
}

// 获取用户收藏的职位
export function getFavoriteJobs(userId) {
  return request({
    url: '/job/favorites',
    method: 'get',
    params: { userId }
  });
}

// 收藏职位
export function favoriteJob(userId, jobId) {
  return request({
    url: '/job/favorite',
    method: 'post',
    data: { userId, jobId }
  });
}

// 取消收藏职位
export function unfavoriteJob(userId, jobId) {
  return request({
    url: '/job/unfavorite',
    method: 'post',
    data: { userId, jobId }
  });
}

// 获取热门公司职位
export function getPopularJobs(limit = 10) {
  return request({
    url: '/job/popular',
    method: 'get',
    params: { limit }
  });
}

// 测试搜索职位
export function testSearchJobs(keyword) {
  // 尝试使用本地数据代替API请求
  if (process.env.VUE_APP_USE_LOCAL_DATA === 'true') {
    return loadLocalJobs().then(response => {
      // 从本地数据中筛选符合关键词的职位
      if (response.code === 200) {
        const filteredJobs = response.data.list.filter(job => 
          job.position_name.toLowerCase().includes(keyword.toLowerCase())
        );
        return {
          code: 200,
          message: '搜索成功',
          data: {
            list: filteredJobs,
            count: filteredJobs.length,
            keyword: keyword
          }
        };
      }
      return response;
    });
  }
  
  return request({
    url: '/api/search',
    method: 'get',
    params: { keyword }
  });
} 