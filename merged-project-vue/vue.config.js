const path = require('path')

function resolve(dir) {
  return path.join(__dirname, dir)
}

// 是否为生产环境
const isProduction = process.env.NODE_ENV === 'production'

// 代理目标地址
const target = 'http://localhost:5000'

module.exports = {
  // 部署应用包时的基本URL
  publicPath: '/',
  
  // 输出文件目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'static',
  
  // 是否在保存时使用eslint-loader检查
  lintOnSave: process.env.NODE_ENV === 'development',
  
  // 生产环境是否生成sourceMap
  productionSourceMap: false,
  
  // webpack配置
  configureWebpack: {
    // 提供一个对象，会被合并到最终的配置中
    name: '职位面试系统',
    resolve: {
      alias: {
        '@': resolve('src')
      }
    }
  },
  
  // webpack-dev-server配置
  devServer: {
    port: 8080,
    open: true,
    overlay: {
      warnings: false,
      errors: true
    },
    // 代理配置
    proxy: {
      // 将所有以/api开头的请求代理到target
      '/api': {
        target,
        changeOrigin: true,
        // 不重写路径，保持/api前缀
      },
      // 添加/data路径的代理
      '/data': {
        target,
        changeOrigin: true
      }
    }
  },
  
  // CSS配置
  css: {
    // 是否使用css分离插件
    extract: isProduction,
    // 是否开启CSS source maps
    sourceMap: false,
    // CSS预处理器配置
    loaderOptions: {
      sass: {
        // 全局引入变量和mixin
        additionalData: `
          @import "@/styles/variables.scss";
          @import "@/styles/mixin.scss";
        `
      }
    }
  }
} 