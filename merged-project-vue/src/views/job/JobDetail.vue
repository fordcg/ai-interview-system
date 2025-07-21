<template>
  <div class="job-detail">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-4" elevation="2">
            <v-card-title class="headline primary--text">
              <v-icon left color="primary" large>mdi-briefcase</v-icon>
              {{ job.position_name || '职位详情' }}
            </v-card-title>
            
            <v-card-text v-if="loading">
              <div class="text-center py-5">
                <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
                <div class="mt-3">加载职位信息中...</div>
              </div>
            </v-card-text>
            
            <template v-else-if="job.id">
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="8">
                    <div class="d-flex align-center mb-4">
                      <v-avatar size="64" class="mr-4">
                        <v-img :src="getCompanyLogo(job.company_logo)" contain></v-img>
                      </v-avatar>
                      <div>
                        <div class="text-h5">{{ job.position_name }}</div>
                        <div class="subtitle-1 grey--text">{{ job.company_name }}</div>
                      </div>
                      <v-spacer></v-spacer>
                      <v-btn 
                        color="success" 
                        class="white--text" 
                        @click="startInterview"
                      >
                        <v-icon left>mdi-account-voice</v-icon>
                        开始面试
                      </v-btn>
                    </div>
                    
                    <v-divider class="mb-4"></v-divider>
                    
                    <v-row dense>
                      <v-col cols="12" sm="6" class="py-1">
                        <div class="caption grey--text">薪资范围</div>
                        <div class="subtitle-1">
                          <v-icon small color="green darken-2" class="mr-1">mdi-currency-cny</v-icon>
                          <span v-if="job.salary0 > 0 || job.salary1 > 0">
                            {{ job.salary0 }} - {{ job.salary1 }}K
                          </span>
                          <span v-else>面谈</span>
                        </div>
                      </v-col>
                      
                      <v-col cols="12" sm="6" class="py-1">
                        <div class="caption grey--text">工作地点</div>
                        <div class="subtitle-1">
                          <v-icon small color="blue-grey" class="mr-1">mdi-map-marker</v-icon>
                          {{ job.city }}
                        </div>
                      </v-col>
                      
                      <v-col cols="12" sm="6" class="py-1">
                        <div class="caption grey--text">学历要求</div>
                        <div class="subtitle-1">
                          <v-icon small color="indigo" class="mr-1">mdi-school</v-icon>
                          {{ job.degree }}
                        </div>
                      </v-col>
                      
                      <v-col cols="12" sm="6" class="py-1">
                        <div class="caption grey--text">企业性质</div>
                        <div class="subtitle-1">
                          <v-icon small color="deep-purple" class="mr-1">mdi-domain</v-icon>
                          {{ job.coattr }}·{{ job.nation }}
                        </div>
                      </v-col>
                      
                      <v-col cols="12" sm="6" class="py-1">
                        <div class="caption grey--text">公司规模</div>
                        <div class="subtitle-1">
                          <v-icon small color="cyan" class="mr-1">mdi-account-group</v-icon>
                          {{ job.cosize0 }} - {{ job.cosize1 }}人
                        </div>
                      </v-col>
                    </v-row>
                    
                    <v-divider class="my-4"></v-divider>
                    
                    <div class="subtitle-1 font-weight-bold mb-2">职位福利</div>
                    <v-chip-group>
                      <v-chip 
                        v-for="(welfare, idx) in getWelfareList(job.welfare)" 
                        :key="idx"
                        color="primary"
                        text-color="white"
                        small
                        class="mr-2 mb-2"
                      >
                        {{ welfare }}
                      </v-chip>
                    </v-chip-group>
                    
                    <v-divider class="my-4"></v-divider>
                    
                    <div class="subtitle-1 font-weight-bold mb-2">职位描述</div>
                    <div class="body-1 job-description">{{ job.intro || '暂无职位描述' }}</div>
                    
                    <v-divider class="my-4"></v-divider>
                    
                    <div class="subtitle-1 font-weight-bold mb-2">职位要求</div>
                    <div class="body-1 job-requirements" v-if="job.requirements">
                      <v-row>
                        <v-col cols="12" sm="6" v-for="(req, idx) in job.requirements" :key="idx">
                          <div class="d-flex align-start mb-2">
                            <v-icon color="amber" small class="mr-2 mt-1">mdi-check-circle</v-icon>
                            <span>{{ req }}</span>
                          </div>
                        </v-col>
                      </v-row>
                    </div>
                    <div class="body-1" v-else>暂无详细要求</div>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <v-card outlined class="mb-4">
                      <v-card-title class="subtitle-1">
                        <v-icon left color="blue">mdi-office-building</v-icon>
                        公司信息
                      </v-card-title>
                      <v-card-text>
                        <div class="mb-3">
                          <div class="caption grey--text">公司名称</div>
                          <div class="body-1">{{ job.company_name }}</div>
                        </div>
                        
                        <div class="mb-3">
                          <div class="caption grey--text">公司行业</div>
                          <div class="body-1">{{ job.industry || '未知' }}</div>
                        </div>
                        
                        <div class="mb-3">
                          <div class="caption grey--text">融资阶段</div>
                          <div class="body-1">{{ job.financing || '未知' }}</div>
                        </div>
                        
                        <v-btn 
                          block 
                          outlined 
                          color="primary" 
                          class="mt-4"
                          @click="viewCompanyDetails"
                        >
                          <v-icon left>mdi-web</v-icon>
                          访问公司主页
                        </v-btn>
                      </v-card-text>
                    </v-card>
                    
                    <v-card outlined class="mb-4">
                      <v-card-title class="subtitle-1">
                        <v-icon left color="green">mdi-chart-line</v-icon>
                        职位分析
                      </v-card-title>
                      <v-card-text>
                        <v-btn 
                          block 
                          color="info" 
                          class="white--text mb-3"
                          to="/job/analysis"
                        >
                          <v-icon left>mdi-chart-bar</v-icon>
                          查看职位分析
                        </v-btn>
                        
                        <v-btn 
                          block 
                          color="warning" 
                          class="white--text"
                          :to="`/interview/prepare/${job.id}`"
                        >
                          <v-icon left>mdi-lightbulb-on</v-icon>
                          面试准备
                        </v-btn>
                      </v-card-text>
                    </v-card>
                    
                    <v-card outlined>
                      <v-card-title class="subtitle-1">
                        <v-icon left color="deep-orange">mdi-share-variant</v-icon>
                        分享职位
                      </v-card-title>
                      <v-card-text>
                        <div class="d-flex justify-space-around">
                          <v-btn icon color="blue">
                            <v-icon>mdi-wechat</v-icon>
                          </v-btn>
                          <v-btn icon color="red">
                            <v-icon>mdi-email</v-icon>
                          </v-btn>
                          <v-btn icon color="blue-grey">
                            <v-icon>mdi-link</v-icon>
                          </v-btn>
                          <v-btn icon color="green">
                            <v-icon>mdi-download</v-icon>
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
            </template>
            
            <v-card-text v-else>
              <v-alert type="warning" outlined>
                未找到职位信息，请返回职位列表重新选择。
              </v-alert>
              <div class="text-center mt-4">
                <v-btn color="primary" to="/job/list">
                  <v-icon left>mdi-arrow-left</v-icon>
                  返回职位列表
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card v-if="job.id" elevation="2">
            <v-card-title class="subtitle-1">
              <v-icon left color="purple">mdi-lightbulb</v-icon>
              相似职位推荐
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6" md="4" v-for="n in 3" :key="n">
                  <v-skeleton-loader
                    v-if="!similarJobs.length"
                    type="card"
                    class="mx-auto"
                  ></v-skeleton-loader>
                  <job-card
                    v-else-if="similarJobs[n-1]"
                    :job="similarJobs[n-1]"
                    @start-interview="startInterview"
                  ></job-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- 面试确认对话框 -->
      <v-dialog v-model="interviewDialog" max-width="500">
        <v-card>
          <v-card-title>开始面试</v-card-title>
          <v-card-text>
            <p>您确定要开始"{{ job.position_name }}"的模拟面试吗？</p>
            <p class="text-caption grey--text">
              面试将包含多个问题，您需要在规定时间内完成回答。系统将对您的回答进行评分和分析。
            </p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="interviewDialog = false">取消</v-btn>
            <v-btn 
              color="primary" 
              :loading="interviewLoading"
              @click="confirmInterview"
            >
              开始面试
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { getJobDetail, getSimilarJobs } from '@/api/job'
import { startInterview } from '@/api/interview'
import JobCard from '../../components/job/JobCard.vue'

export default {
  name: 'JobDetail',
  components: {
    JobCard
  },
  data() {
    return {
      loading: true,
      job: {},
      similarJobs: [],
      interviewDialog: false,
      interviewLoading: false
    }
  },
  computed: {
    jobId() {
      return this.$route.params.id
    }
  },
  created() {
    this.fetchJobDetail()
  },
  methods: {
    async fetchJobDetail() {
      this.loading = true
      try {
        const response = await getJobDetail(this.jobId)
        this.job = response.data.data || {}
        
        // 获取相似职位
        if (this.job.id) {
          this.fetchSimilarJobs()
        }
      } catch (error) {
        console.error('获取职位详情失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '获取职位详情失败，请稍后再试',
          color: 'error'
        })
      } finally {
        this.loading = false
      }
    },
    
    async fetchSimilarJobs() {
      try {
        const response = await getSimilarJobs(this.jobId)
        this.similarJobs = response.data.data || []
      } catch (error) {
        console.error('获取相似职位失败:', error)
      }
    },
    
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
      return welfare.split(',').filter(item => item.trim() !== '')
    },
    
    viewCompanyDetails() {
      if (this.job.company_url) {
        window.open(this.job.company_url)
      } else {
        this.$store.dispatch('snackbar/showMessage', {
          message: '暂无公司主页信息',
          color: 'info'
        })
      }
    },
    
    startInterview() {
      this.interviewDialog = true
    },
    
    async confirmInterview() {
      this.interviewLoading = true
      try {
        const response = await startInterview(this.jobId)
        const interviewId = response.data.interview_id
        this.$router.push(`/interview/process/${interviewId}`)
      } catch (error) {
        console.error('开始面试失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '开始面试失败，请稍后再试',
          color: 'error'
        })
      } finally {
        this.interviewLoading = false
        this.interviewDialog = false
      }
    }
  }
}
</script>

<style scoped>
.job-detail {
  padding: 20px 0;
}

.job-description, .job-requirements {
  white-space: pre-line;
  line-height: 1.6;
}
</style> 