// 获取面试问题
export function getQuestion(category) {
  // 返回空数据，需要连接真实API
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: []
  });
}

// 分析面试回答
export function analyze(data) {
  // 模拟分析结果
  return Promise.resolve({
    code: 0,
    msg: '分析成功',
    data: {
      score: Math.floor(Math.random() * 30) + 70, // 70-100的随机分数
      strengths: ['表达清晰', '逻辑性强'],
      weaknesses: ['专业术语使用不够准确'],
      suggestions: ['建议加强专业知识学习', '多参加模拟面试练习']
    }
  });
}

// 获取面试报告
export function getReport(reportId) {
  // 返回空数据，需要连接真实API
  return Promise.resolve({
    code: 404,
    msg: '报告不存在'
  });
}

// 获取排名信息
export function getRanking() {
  // 模拟排名数据
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      { userId: 1, username: '张三', score: 95, rank: 1 },
      { userId: 2, username: '李四', score: 90, rank: 2 },
      { userId: 3, username: '王五', score: 85, rank: 3 },
      { userId: 4, username: '赵六', score: 80, rank: 4 },
      { userId: 5, username: '钱七', score: 75, rank: 5 }
    ]
  });
}

// 分析语音
export function analyzeSpeech(audio) {
  // 模拟语音分析结果
  return Promise.resolve({
    code: 0,
    msg: '分析成功',
    data: {
      clarity: 85,
      pace: 75,
      tone: 80,
      confidence: 90,
      suggestions: ['语速可以适当放慢', '注意语调变化']
    }
  });
}

// 元宇宙面试体验
export function getMetaverseInterview() {
  // 模拟元宇宙面试数据
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      sceneUrl: 'https://example.com/metaverse/interview',
      avatarOptions: [
        { id: 1, name: '商务男士', url: 'https://example.com/avatar/male1' },
        { id: 2, name: '商务女士', url: 'https://example.com/avatar/female1' }
      ],
      interviewers: [
        { id: 1, name: 'AI面试官-技术', avatar: 'https://example.com/interviewer/tech' },
        { id: 2, name: 'AI面试官-HR', avatar: 'https://example.com/interviewer/hr' }
      ]
    }
  });
}

// 获取面试详情
export function getInterviewDetail(id) {
  // 模拟面试详情
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      id: Number(id),
      title: '前端开发工程师面试',
      date: '2023-06-01',
      duration: 45, // 分钟
      questions: [
        { id: 1, question: '请介绍一下你自己', answer: '我是一名前端开发工程师，有5年工作经验...' },
        { id: 2, question: '你对Vue的理解是什么？', answer: 'Vue是一个渐进式JavaScript框架...' }
      ],
      feedback: {
        overall: 85,
        technical: 80,
        communication: 90,
        attitude: 85
      }
    }
  });
}

// 获取面试列表
export function getInterviewList(params) {
  // 模拟面试列表
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      total: 10,
      list: [
        { id: 1, title: '前端开发工程师面试', date: '2023-06-01', status: '已完成', score: 85 },
        { id: 2, title: '后端开发工程师面试', date: '2023-06-05', status: '已完成', score: 90 },
        { id: 3, title: '数据分析师面试', date: '2023-06-10', status: '未开始', score: null }
      ]
    }
  });
}

// 获取面试问题
export function getInterviewQuestions(params) {
  // 返回空数据，需要连接真实API
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: []
  });
}

// 获取面试排名
export function getInterviewRanking(params) {
  // 复用排名数据
  return getRanking();
}

// 获取面试报告
export function getInterviewReport(id) {
  // 返回空数据，需要连接真实API
  return Promise.resolve({
    code: 404,
    msg: '报告不存在'
  });
}

// 获取用户面试历史
export function getUserInterviewHistory(userId) {
  // 模拟用户面试历史
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      { id: 1, title: '前端开发工程师面试', date: '2023-05-20', score: 85 },
      { id: 2, title: '后端开发工程师面试', date: '2023-05-25', score: 90 }
    ]
  });
}

// 提交面试答案
export function submitInterviewAnswer(data) {
  // 模拟提交成功
  return Promise.resolve({
    code: 0,
    msg: '提交成功',
    data: {
      id: Date.now(),
      questionId: data.questionId,
      answer: data.answer,
      score: Math.floor(Math.random() * 30) + 70 // 70-100的随机分数
    }
  });
}

// 开始面试
export function startInterview(jobId) {
  // 模拟开始面试
  return Promise.resolve({
    code: 0,
    msg: '开始面试成功',
    data: {
      interview_id: Date.now(),
      job_id: jobId,
      start_time: new Date().toISOString(),
      status: 'in_progress',
      totalQuestions: 5,
      firstQuestion: {
        id: 1,
        question: '请简单介绍一下你自己和你的技能背景',
        type: 'text'
      }
    }
  });
} 