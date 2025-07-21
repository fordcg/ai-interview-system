<template>
  <v-card
    :loading="loading"
    class="mx-auto my-4 job-card custom-card"
    max-width="380"
    elevation="0"
    hover
  >
    <template slot="progress">
      <v-progress-linear
        color="primary"
        height="10"
        indeterminate
      ></v-progress-linear>
    </template>

    <v-img
      height="100"
      :src="getCompanyLogo(job.company_logo)"
      class="company-logo"
      gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.6)"
      :style="{ borderTopLeftRadius: '16px', borderTopRightRadius: '16px' }"
    >
      <div class="company-badge">
        <v-chip
          x-small
          :color="getCompanyTypeColor(job.coattr)"
          text-color="white"
          class="mt-1 ml-1"
        >
          {{ job.coattr }}
        </v-chip>
      </div>
    </v-img>

    <v-card-title class="job-title pb-2 px-4 pt-4">
      <div class="gradient-text">
        {{ job.position_name }}
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-icon
              v-if="job.hot"
              color="error"
              small
              class="ml-1 pulse-animation"
              v-bind="attrs"
              v-on="on"
            >
              mdi-fire
            </v-icon>
          </template>
          <span>热门职位</span>
        </v-tooltip>
      </div>
    </v-card-title>

    <v-card-subtitle class="pb-0 pt-2 px-4">
      <div class="company-name">
        <v-icon size="18" color="#3949ab" class="mr-2">mdi-office-building</v-icon>
        {{ job.company_name }}
      </div>
      
      <div class="location-info mt-2">
        <v-icon size="16" color="#4895ef" class="mr-1">mdi-map-marker</v-icon>
        {{ job.city }}
        <v-icon size="16" color="#4895ef" class="ml-3 mr-1">mdi-school</v-icon>
        {{ job.degree }}
      </div>
    </v-card-subtitle>

    <v-card-text class="pt-3 px-4">
      <div class="salary-display">
        <v-icon size="20" color="success" class="mr-2">mdi-currency-cny</v-icon>
        <span class="salary-text" v-if="job.salary0 > 0 || job.salary1 > 0">
          {{ job.salary0 }} - {{ job.salary1 }}<span class="salary-unit">K</span>
        </span>
        <span class="salary-text" v-else>
          面谈
        </span>
      </div>

      <div class="company-info mt-3">
        <v-icon size="18" color="#3949ab" class="mr-2">mdi-domain</v-icon>
        {{ job.nation }} · {{ job.cosize0 }}-{{ job.cosize1 }}人
      </div>

      <v-divider class="my-2 divider-light"></v-divider>

      <div class="job-intro">{{ job.intro }}</div>

      <v-divider class="my-2 divider-light"></v-divider>

      <div class="welfare-title">
        <v-icon small color="warning" class="mr-1">mdi-star</v-icon>
        公司福利
      </div>
      <v-chip-group
        class="welfare-chips"
        column
      >
        <v-chip 
          v-for="(welfare, idx) in getWelfareList(job.welfare)" 
          :key="idx"
          x-small
          outlined
          color="accent"
          class="mr-1 mb-1 welfare-chip"
        >
          {{ welfare }}
        </v-chip>
      </v-chip-group>
    </v-card-text>

    <v-divider class="divider-light"></v-divider>

    <v-card-actions class="px-3 pb-3 pt-1 d-flex justify-space-between">
      <v-btn
        text
        small
        color="primary"
        class="action-btn elevated-btn primary-btn"
        @click="viewJobDetails(job.id)"
      >
        <v-icon left small>mdi-text-box-search</v-icon>
        详情
      </v-btn>
      <v-btn
        text
        small
        color="indigo darken-1"
        class="action-btn elevated-btn company-btn"
        @click="viewCompanyDetails(job.company_url)"
      >
        <v-icon left small>mdi-office-building</v-icon>
        公司
      </v-btn>
      <v-btn
        text
        small
        color="success"
        class="action-btn elevated-btn success-btn"
        @click="startInterview(job.id)"
      >
        <v-icon left small>mdi-file-search</v-icon>
        分析
      </v-btn>
    </v-card-actions>

    <!-- 收藏按钮 -->
    <v-btn
      icon
      small
      absolute
      top
      right
      :color="isFavorite ? 'error' : 'grey lighten-1'"
      class="favorite-btn"
      @click.stop="toggleFavorite"
    >
      <v-icon>{{ isFavorite ? 'mdi-heart' : 'mdi-heart-outline' }}</v-icon>
    </v-btn>
  </v-card>
</template>

<script>
export default {
  name: "JobCard",
  props: {
    job: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    loading: false,
    isFavorite: false
  }),
  methods: {
    getCompanyLogo(src) {
      let trueSrc = ''
      if (src != null && src.startsWith("http")) {
        trueSrc = src
      } else if (src != null && src != '') {
        trueSrc = 'https://images.weserv.nl/?url=' + src
      } else {
        trueSrc = require("../../assets/images/nologo.png")
      }
      return trueSrc
    },
    
    getWelfareList(welfare) {
      if (!welfare) return []
      return welfare.split(',').filter(item => item.trim() !== '').slice(0, 6) // 最多显示6个福利
    },
    
    viewCompanyDetails(url) {
      this.loading = true
      setTimeout(() => {
        this.loading = false
        if (url) {
          window.open(url)
        } else {
          this.$store.dispatch('snackbar/showMessage', {
            message: '暂无公司主页信息',
            color: 'info'
          })
        }
      }, 800)
    },
    
    viewJobDetails(id) {
      this.loading = true
      setTimeout(() => {
        this.loading = false
        this.$router.push(`/job/detail/${id}`)
      }, 400)
    },
    
    startInterview(jobId) {
      this.$emit('start-interview', jobId)
    },
    
    toggleFavorite() {
      this.isFavorite = !this.isFavorite
      // 这里可以添加收藏/取消收藏的API调用
      const message = this.isFavorite ? '已添加到收藏夹' : '已从收藏夹移除'
      this.$store.dispatch('snackbar/showMessage', {
        message,
        color: this.isFavorite ? 'success' : 'info'
      })
    },
    
    getCompanyTypeColor(type) {
      const typeMap = {
        '私营企业': 'blue',
        '国有企业': 'red',
        '外资企业': 'purple',
        '合资企业': 'deep-orange',
        '上市公司': 'green'
      }
      return typeMap[type] || 'blue-grey'
    },
    
    getDegreeColor(degree) {
      const degreeMap = {
        '博士': 'deep-purple',
        '硕士': 'purple',
        '本科': 'indigo',
        '大专': 'blue',
        '高中': 'cyan'
      }
      return degreeMap[degree] || 'blue-grey'
    }
  }
};
</script>

<style scoped>
.job-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(233, 236, 239, 0.8);
  border-radius: 16px !important;
  color: #333333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

.job-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 25px rgba(0, 0, 0, 0.1) !important;
}

.company-logo {
  object-fit: cover;
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background-color: #f5f7fa;
}

.company-badge {
  position: absolute;
  top: 0;
  left: 0;
}

.job-title {
  font-weight: 700;
  line-height: 1.3;
  font-size: 1.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.01em;
  padding: 2px 0;
}

.company-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.95rem;
  color: #303030;
  margin-top: 5px;
  letter-spacing: 0.01em;
  font-weight: 500;
}

.location-info {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: #505050;
  letter-spacing: 0.01em;
}

.salary-display {
  background-color: rgba(40, 167, 69, 0.08);
  padding: 6px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
}

.salary-text {
  color: #28a745;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.salary-unit {
  font-size: 0.8rem;
  font-weight: 400;
  margin-left: 2px;
  color: #28a745;
  opacity: 0.8;
}

.company-info {
  font-size: 0.88rem;
  color: #505050;
  display: flex;
  align-items: center;
}

.job-intro {
  margin: 8px 0;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  font-size: 0.85rem;
  color: #333333;
  line-height: 1.4;
}

.welfare-title {
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #424242;
  display: flex;
  align-items: center;
}

.welfare-chips {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
}

.welfare-chip {
  background: rgba(72, 149, 239, 0.12) !important;
  border-color: rgba(72, 149, 239, 0.3) !important;
  transition: all 0.2s ease;
  color: #1a56db !important;
  font-weight: 500;
}

.welfare-chip:hover {
  background: rgba(72, 149, 239, 0.2) !important;
  transform: translateY(-2px);
}

.favorite-btn {
  margin: 10px;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
}

.favorite-btn:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.divider-light {
  border-color: rgba(0, 0, 0, 0.06) !important;
  margin: 8px 16px !important;
}

.location-chip, .degree-chip {
  font-size: 0.7rem;
}

.action-btn {
  transition: all 0.3s ease;
  border-radius: 8px !important;
  margin: 0;
  padding: 0 10px !important;
  min-width: 80px;
}

.action-btn:hover {
  transform: translateY(-3px);
  background: rgba(0, 0, 0, 0.04) !important;
}

.elevated-btn {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.elevated-btn:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.primary-btn {
  background: rgba(25, 118, 210, 0.08) !important;
}

.primary-btn:hover {
  background: rgba(25, 118, 210, 0.15) !important;
  box-shadow: 0 4px 8px rgba(25, 118, 210, 0.25);
}

.company-btn {
  background: rgba(63, 81, 181, 0.08) !important;
}

.company-btn:hover {
  background: rgba(63, 81, 181, 0.15) !important;
  box-shadow: 0 4px 8px rgba(63, 81, 181, 0.25);
}

.success-btn {
  background: rgba(40, 167, 69, 0.08) !important;
}

.success-btn:hover {
  background: rgba(40, 167, 69, 0.15) !important;
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.25);
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.pulse-animation {
  animation: pulse 1.5s infinite;
}
</style> 