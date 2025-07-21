import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.use(Vuetify)

// 将HSL颜色转换为十六进制颜色代码的辅助函数
function hslToHex(h, s, l) {
  // 将HSL值转换为RGB
  l /= 100;
  const a = s * Math.min(l, 1 - l) / 100;
  const f = n => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

// 主题颜色 - 基于theme-variables.css中的HSL值
const primaryHsl = { h: 221.2, s: 83.2, l: 53.3 };
const secondaryHsl = { h: 240, s: 5.9, l: 10 };
const accentHsl = { h: 240, s: 4.8, l: 95.9 };
const errorHsl = { h: 0, s: 84.2, l: 60.2 };
const successHsl = { h: 142.1, s: 76.2, l: 36.3 };
const warningHsl = { h: 38, s: 92, l: 50 };
const infoHsl = { h: 198, s: 93, l: 60 };
const backgroundHsl = { h: 240, s: 10, l: 3.9 };

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: hslToHex(primaryHsl.h, primaryHsl.s, primaryHsl.l),
        secondary: hslToHex(secondaryHsl.h, secondaryHsl.s, secondaryHsl.l),
        accent: hslToHex(accentHsl.h, accentHsl.s, accentHsl.l),
        error: hslToHex(errorHsl.h, errorHsl.s, errorHsl.l),
        success: hslToHex(successHsl.h, successHsl.s, successHsl.l),
        warning: hslToHex(warningHsl.h, warningHsl.s, warningHsl.l),
        info: hslToHex(198, 93, 60),
        background: hslToHex(backgroundHsl.h, backgroundHsl.s, backgroundHsl.l)
      },
      dark: {
        primary: hslToHex(217.2, 91.2, 59.8),
        secondary: hslToHex(240, 3.7, 15.9),
        accent: hslToHex(240, 3.7, 15.9),
        error: hslToHex(0, 62.8, 30.6),
        success: hslToHex(142.1, 70.6, 45.3),
        warning: hslToHex(38, 92, 50),
        info: hslToHex(198, 93, 60),
        background: hslToHex(240, 10, 3.9)
      }
    },
    dark: false,
    options: { customProperties: true }
  },
  icons: {
    iconfont: 'mdi'
  }
}) 