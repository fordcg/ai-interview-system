// 通用API函数

// 获取验证码
export function getVerifyCode(phone) {
  // 模拟获取验证码
  return Promise.resolve({
    code: 0,
    msg: '验证码发送成功',
    data: {
      expireTime: Date.now() + 60 * 1000 // 1分钟后过期
    }
  });
}

// 上传文件
export function uploadFile(file) {
  // 模拟文件上传
  return new Promise((resolve) => {
    // 模拟上传延迟
    setTimeout(() => {
      resolve({
        code: 0,
        msg: '上传成功',
        data: {
          url: 'https://example.com/uploads/' + file.name,
          name: file.name,
          size: file.size
        }
      });
    }, 1000);
  });
}

// 获取系统配置
export function getSystemConfig() {
  // 模拟系统配置
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: {
      siteName: '面试星途 - 多模态智能面试模拟与评估系统',
      logo: '/logo.png',
      footer: '© 2023 面试星途',
      contactEmail: 'contact@mianshixingtu.com',
      contactPhone: '400-888-8888'
    }
  });
}

// 获取公告信息
export function getAnnouncements() {
  // 模拟公告信息
  return Promise.resolve({
    code: 0,
    msg: '获取成功',
    data: [
      {
        id: 1,
        title: '系统升级通知',
        content: '系统将于2023年6月15日凌晨2:00-4:00进行升级维护，请提前做好准备。',
        date: '2023-06-10',
        important: true
      },
      {
        id: 2,
        title: '新功能上线',
        content: '元宇宙面试体验功能已上线，欢迎体验！',
        date: '2023-06-05',
        important: false
      }
    ]
  });
} 