import request from '@/utils/request'

// 用户登录
export function login(data) {
  // 模拟登录验证 - 添加默认测试账号
  const defaultAccounts = [
    { username: 'admin', password: 'admin123' },
    { username: 'test', password: '123456' },
    { username: 'user', password: '123456' }
  ];

  // 检查是否为有效账号
  const validAccount = defaultAccounts.find(account =>
    account.username === data.username && account.password === data.password
  );

  if (validAccount) {
    return Promise.resolve({
      code: 0,
      msg: '登录成功',
      data: {
        id: validAccount.username === 'admin' ? 1 : Date.now(),
        username: validAccount.username,
        avatar: 'https://i.pravatar.cc/150?img=1'
      }
    });
  } else {
    return Promise.resolve({
      code: 401,
      msg: '用户名或密码错误'
    });
  }
}

// 用户注册
export function register(data) {
  // 模拟注册成功
  return Promise.resolve({
    code: 200,
    message: '注册成功',
    data: {
      id: Date.now(),
      username: data.username,
      email: data.email
    }
  });
}

// 用户登出
export function logout() {
  // 模拟登出成功
  return Promise.resolve({
    code: 0,
    msg: '登出成功'
  });
}

// 获取用户信息
export function getUserInfo(token) {
  // 返回空数据，需要连接真实API
  return Promise.resolve({
    code: 401,
    msg: '未授权'
  });
}

// 更新用户信息
export function updateUserInfo(data) {
  // 模拟更新成功
  return Promise.resolve({
    code: 0,
    msg: '更新成功',
    data
  });
}

// 更新用户头像
export function updateAvatar(data) {
  // 模拟更新成功
  return Promise.resolve({
    code: 0,
    msg: '头像更新成功',
    data: {
      avatar: data.avatar || 'https://i.pravatar.cc/150?img=1'
    }
  });
}

// 修改密码
export function changePassword(data) {
  // 模拟修改成功
  return Promise.resolve({
    code: 0,
    msg: '密码修改成功'
  });
}

// 获取用户简历
export function getUserResume(userId) {
  // 模拟简历数据
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      userId,
      name: '张三',
      phone: '13800138000',
      email: 'zhangsan@example.com',
      education: '本科',
      experience: [
        {
          id: 1,
          company: 'XX科技有限公司',
          position: '前端开发工程师',
          startDate: '2020-01',
          endDate: '2022-12',
          description: '负责公司产品的前端开发工作'
        }
      ],
      skills: ['JavaScript', 'Vue', 'React', 'HTML', 'CSS']
    }
  });
}

// 更新用户简历
export function updateUserResume(data) {
  // 模拟更新成功
  return Promise.resolve({
    code: 0,
    msg: '简历更新成功',
    data
  });
}

// 获取用户面试记录
export function getUserInterviews(userId) {
  // 模拟面试记录
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      {
        id: 1,
        position: '前端开发工程师',
        company: 'XX科技有限公司',
        date: '2023-05-20',
        score: 85,
        status: '已完成'
      },
      {
        id: 2,
        position: '后端开发工程师',
        company: 'YY互联网公司',
        date: '2023-05-25',
        score: 90,
        status: '已完成'
      }
    ]
  });
}

// 获取用户收藏的职位
export function getUserFavoriteJobs(userId) {
  // 模拟收藏职位
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      {
        id: 1,
        title: '前端开发工程师',
        company: '科技有限公司',
        location: '北京',
        salary: '15k-25k',
        publishTime: '2023-05-15'
      },
      {
        id: 2,
        title: '后端开发工程师',
        company: '互联网科技公司',
        location: '上海',
        salary: '20k-35k',
        publishTime: '2023-05-10'
      }
    ]
  });
}

// 添加职位收藏
export function addFavoriteJob(data) {
  // 模拟添加成功
  return Promise.resolve({
    code: 0,
    msg: '收藏成功'
  });
}

// 取消职位收藏
export function removeFavoriteJob(userId, jobId) {
  // 模拟取消成功
  return Promise.resolve({
    code: 0,
    msg: '取消收藏成功'
  });
} 