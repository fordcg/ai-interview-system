// 最小化的面试测试数据
// 仅用于测试模式，提供基本的面试问题结构

// 基础面试问题数据
const basicQuestions = [
  { id: 1, text: '请简单介绍一下您自己。', type: 'open' },
  { id: 2, text: '您为什么想要这个职位？', type: 'open' },
  { id: 3, text: '您最大的优势是什么？', type: 'open' },
  { id: 4, text: '描述一个您克服困难的经历。', type: 'behavioral' },
  { id: 5, text: '您对我们公司了解多少？', type: 'open' },
  { id: 6, text: '您的职业规划是什么？', type: 'open' },
  { id: 7, text: '您如何处理工作压力？', type: 'behavioral' },
  { id: 8, text: '您有什么问题要问我们吗？', type: 'open' }
]

// 技术相关问题
const technicalQuestions = [
  { id: 9, text: '请解释一下您最熟悉的技术栈。', type: 'technical' },
  { id: 10, text: '描述一个您解决的技术难题。', type: 'technical' }
]

// 面试数据结构
export const testInterviewData = {
  frontend: {
    title: '前端工程师面试',
    position: '前端工程师',
    questions: [...basicQuestions, ...technicalQuestions]
  },
  backend: {
    title: '后端工程师面试',
    position: '后端工程师',
    questions: [...basicQuestions, ...technicalQuestions]
  },
  product: {
    title: '产品经理面试',
    position: '产品经理',
    questions: basicQuestions
  },
  dataAnalyst: {
    title: '数据分析师面试',
    position: '数据分析师',
    questions: [...basicQuestions, ...technicalQuestions]
  },
  general: {
    title: '通用面试',
    position: '通用职位',
    questions: basicQuestions
  }
}

// 根据职位类型获取面试数据
export function getInterviewDataByPosition(position) {
  return testInterviewData[position] || testInterviewData.general
}

// 根据难度级别过滤问题
export function filterQuestionsByDifficulty(questions, difficulty = 'medium') {
  if (!questions || !Array.isArray(questions)) {
    return basicQuestions
  }
  
  switch (difficulty) {
    case 'easy':
      return questions.filter(q => q.type === 'open').slice(0, 5)
    case 'hard':
      return questions
    case 'medium':
    default:
      return questions.slice(0, 8)
  }
}

export default testInterviewData
