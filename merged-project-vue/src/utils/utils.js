/**
 * 格式化时间
 * @param {(Object|string|number)} time
 * @param {string} cFormat
 * @returns {string | null}
 */
export function parseTime(time, cFormat) {
  if (arguments.length === 0 || !time) {
    return null
  }
  
  const format = cFormat || '{y}-{m}-{d} {h}:{i}:{s}'
  let date
  
  if (typeof time === 'object') {
    date = time
  } else {
    if ((typeof time === 'string')) {
      if ((/^[0-9]+$/.test(time))) {
        // 支持 "1548221490638"
        time = parseInt(time)
      } else {
        // 支持 safari
        time = time.replace(new RegExp(/-/gm), '/')
      }
    }
    
    if ((typeof time === 'number') && (time.toString().length === 10)) {
      time = time * 1000
    }
    
    date = new Date(time)
  }
  
  const formatObj = {
    y: date.getFullYear(),
    m: date.getMonth() + 1,
    d: date.getDate(),
    h: date.getHours(),
    i: date.getMinutes(),
    s: date.getSeconds(),
    a: date.getDay()
  }
  
  const time_str = format.replace(/{([ymdhisa])+}/g, (result, key) => {
    const value = formatObj[key]
    // 注意: getDay() 返回 0 表示周日
    if (key === 'a') { return ['日', '一', '二', '三', '四', '五', '六'][value ] }
    return value.toString().padStart(2, '0')
  })
  
  return time_str
}

/**
 * 格式化时间为相对时间
 * @param {number} time
 * @param {string} option
 * @returns {string}
 */
export function formatTime(time, option) {
  if (('' + time).length === 10) {
    time = parseInt(time) * 1000
  } else {
    time = +time
  }
  
  const d = new Date(time)
  const now = Date.now()
  
  const diff = (now - d) / 1000
  
  if (diff < 30) {
    return '刚刚'
  } else if (diff < 3600) {
    // 少于1小时
    return Math.ceil(diff / 60) + '分钟前'
  } else if (diff < 3600 * 24) {
    // 少于24小时
    return Math.ceil(diff / 3600) + '小时前'
  } else if (diff < 3600 * 24 * 2) {
    // 少于2天
    return '1天前'
  }
  
  if (option) {
    return parseTime(time, option)
  } else {
    return (
      d.getMonth() +
      1 +
      '月' +
      d.getDate() +
      '日' +
      d.getHours() +
      '时' +
      d.getMinutes() +
      '分'
    )
  }
}

/**
 * 将URL参数转为对象
 * @param {string} url
 * @returns {Object}
 */
export function getQueryObject(url) {
  url = url == null ? window.location.href : url
  const search = url.substring(url.lastIndexOf('?') + 1)
  const obj = {}
  const reg = /([^?&=]+)=([^?&=]*)/g
  search.replace(reg, (rs, $1, $2) => {
    const name = decodeURIComponent($1)
    let val = decodeURIComponent($2)
    val = String(val)
    obj[name] = val
    return rs
  })
  return obj
}

/**
 * 深拷贝
 * @param {Object} source
 * @returns {Object}
 */
export function deepClone(source) {
  if (!source && typeof source !== 'object') {
    throw new Error('error arguments', 'deepClone')
  }
  
  const targetObj = source.constructor === Array ? [] : {}
  
  Object.keys(source).forEach(keys => {
    if (source[keys] && typeof source[keys] === 'object') {
      targetObj[keys] = deepClone(source[keys])
    } else {
      targetObj[keys] = source[keys]
    }
  })
  
  return targetObj
}

/**
 * 防抖函数
 * @param {Function} func
 * @param {number} wait
 * @param {boolean} immediate
 * @return {*}
 */
export function debounce(func, wait, immediate) {
  let timeout, args, context, timestamp, result

  const later = function() {
    // 据上一次触发时间间隔
    const last = +new Date() - timestamp

    // 上次被包装函数被调用时间间隔 last 小于设定时间间隔 wait
    if (last < wait && last > 0) {
      timeout = setTimeout(later, wait - last)
    } else {
      timeout = null
      // 如果设定为immediate===true，因为开始边界已经调用过了此处无需调用
      if (!immediate) {
        result = func.apply(context, args)
        if (!timeout) context = args = null
      }
    }
  }

  return function(...args) {
    context = this
    timestamp = +new Date()
    const callNow = immediate && !timeout
    // 如果延时不存在，重新设定延时
    if (!timeout) timeout = setTimeout(later, wait)
    if (callNow) {
      result = func.apply(context, args)
      context = args = null
    }

    return result
  }
}

/**
 * 节流函数
 * @param {Function} func
 * @param {number} wait
 * @param {Object} options
 * @return {*}
 */
export function throttle(func, wait, options) {
  let timeout, context, args
  let previous = 0
  if (!options) options = {}

  const later = function() {
    previous = options.leading === false ? 0 : +new Date()
    timeout = null
    func.apply(context, args)
    if (!timeout) context = args = null
  }

  const throttled = function() {
    const now = +new Date()
    if (!previous && options.leading === false) previous = now
    const remaining = wait - (now - previous)
    context = this
    args = arguments
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout)
        timeout = null
      }
      previous = now
      func.apply(context, args)
      if (!timeout) context = args = null
    } else if (!timeout && options.trailing !== false) {
      timeout = setTimeout(later, remaining)
    }
  }

  return throttled
}

/**
 * 将对象转为URL参数字符串
 * @param {Object} obj
 * @returns {string}
 */
export function objectToParams(obj) {
  if (!obj) return ''
  
  return Object.keys(obj)
    .map(key => {
      if (obj[key] === undefined) return ''
      return encodeURIComponent(key) + '=' + encodeURIComponent(obj[key])
    })
    .filter(item => item)
    .join('&')
}

/**
 * 获取字符串的字节长度
 * @param {string} str
 * @returns {number}
 */
export function getByteLength(str) {
  let len = 0
  for (let i = 0; i < str.length; i++) {
    if (str.charCodeAt(i) > 127 || str.charCodeAt(i) === 94) {
      len += 2
    } else {
      len++
    }
  }
  return len
}

/**
 * 检查元素是否有指定class
 * @param {HTMLElement} elm
 * @param {string} cls
 * @returns {boolean}
 */
export function hasClass(ele, cls) {
  return !!ele.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'))
}

/**
 * 为元素添加class
 * @param {HTMLElement} elm
 * @param {string} cls
 */
export function addClass(ele, cls) {
  if (!hasClass(ele, cls)) ele.className += ' ' + cls
}

/**
 * 从元素移除class
 * @param {HTMLElement} elm
 * @param {string} cls
 */
export function removeClass(ele, cls) {
  if (hasClass(ele, cls)) {
    const reg = new RegExp('(\\s|^)' + cls + '(\\s|$)')
    ele.className = ele.className.replace(reg, ' ')
  }
}

/**
 * 生成随机字符串
 * @param {number} len
 * @returns {string}
 */
export function randomString(len) {
  len = len || 32
  const chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
  const maxPos = chars.length
  let str = ''
  for (let i = 0; i < len; i++) {
    str += chars.charAt(Math.floor(Math.random() * maxPos))
  }
  return str
}

export default {
  install(Vue) {
    Vue.prototype.$utils = {
      parseTime,
      formatTime,
      getQueryObject,
      deepClone,
      debounce,
      throttle,
      objectToParams,
      getByteLength,
      hasClass,
      addClass,
      removeClass,
      randomString
    }
  }
} 