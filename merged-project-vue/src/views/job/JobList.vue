<template>
  <!-- 
    job-list-container 添加 dark-background 类控制背景颜色
    当 isSearchExpanded 为 true 时，背景变为黑色
    当 isSearchExpanded 为 false 时，背景恢复为白色
    点击外部区域时，通过 handleOutsideClick 方法将 isSearchExpanded 设为 false
  -->
  <div class="job-list-container" :class="{'dark-background': isSearchExpanded}" @click="handleOutsideClick">
    <!-- 搜索、筛选和统计区域 -->
    <v-card 
      class="search-filter-card mb-3" 
      dark
      color="black"
      :class="{'expanded': isSearchExpanded, 'collapsed': !isSearchExpanded}"
      elevation="4"
      ref="searchCard"
    >
      <v-card-text>
        <!-- 收缩状态显示的内容 -->
        <div v-if="!isSearchExpanded" class="collapsed-content d-flex justify-space-between align-center" @click.stop="toggleSearchArea">
          <div class="d-flex align-center">
            <v-icon color="white" class="mr-2">mdi-magnify</v-icon>
            <span class="white--text">点击展开搜索</span>
          </div>
          <div class="d-flex align-center">
            <v-chip small dark color="primary" class="mr-2">
              <strong>{{ filteredJobs.length }}</strong><span class="ml-1">个职位</span>
            </v-chip>
            <v-chip v-if="showingRecommended && recommendedJobs.length > 0" 
              small color="success" text-color="white">
              <v-icon x-small left>mdi-star</v-icon>推荐
            </v-chip>
          </div>
        </div>

        <!-- 展开状态显示的内容 -->
        <div v-else @click.stop>
          <v-row>
            <v-col cols="12" md="6" class="d-flex align-center">
              <search-box @search="handleSearch" />
            </v-col>
            
            <v-col cols="12" md="6" class="d-flex align-center justify-end">
              <v-btn icon color="white" class="mr-2" @click="toggleSearchArea" title="收起搜索面板">
                <v-icon>mdi-chevron-up</v-icon>
              </v-btn>
              <v-btn-toggle v-model="viewMode" mandatory dark>
                <v-btn small value="card">
                  <v-icon>mdi-view-grid</v-icon>
                </v-btn>
                <v-btn small value="list">
                  <v-icon>mdi-view-list</v-icon>
                </v-btn>
              </v-btn-toggle>
            </v-col>
          </v-row>
          
          <v-row class="mt-4">
            <v-col cols="12" sm="4" md="4">
              <v-select
                v-model="filters.cities"
                :items="cities"
                label="城市"
                outlined
                dense
                clearable
                multiple
                chips
                small-chips
                deletable-chips
                @change="applyFilters"
                dark
                background-color="rgba(255,255,255,0.1)"
                class="white-label"
              >
                <template v-slot:selection="{ item, index }">
                  <v-chip
                    v-if="index < 2"
                    small
                    close
                    @click:close="removeCity(item)"
                    dark
                  >
                    {{ item }}
                  </v-chip>
                  <span
                    v-if="index === 2"
                    class="white--text caption"
                  >
                    (+{{ filters.cities.length - 2 }} 个城市)
                  </span>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" sm="4" md="4">
              <v-select
                v-model="filters.salary"
                :items="salaryRanges"
                label="薪资范围"
                outlined
                dense
                clearable
                @change="applyFilters"
                dark
                background-color="rgba(255,255,255,0.1)"
                class="white-label"
              ></v-select>
            </v-col>
            
            <v-col cols="12" sm="4" md="4">
              <v-select
                v-model="filters.experience"
                :items="experienceRanges"
                label="工作经验"
                outlined
                dense
                clearable
                @change="applyFilters"
                dark
                background-color="rgba(255,255,255,0.1)"
                class="white-label"
              ></v-select>
            </v-col>
          </v-row>
          
          <v-row>
            <v-col cols="12" class="d-flex flex-wrap align-center">
              <div class="d-flex flex-grow-1 flex-wrap">
                <v-chip-group class="flex-wrap">
                  <v-chip
                    v-for="(value, key) in activeFilters"
                    :key="`${key}-${typeof value === 'object' ? JSON.stringify(value) : value}`"
                    close
                    @click:close="removeFilter(key)"
                    v-if="key !== 'cities'"
                    dark
                  >
                    {{ getFilterLabel(key, value) }}
                  </v-chip>
                  <v-chip
                    v-if="filters.cities && filters.cities.length > 0"
                    close
                    @click:close="removeFilter('cities')"
                    dark
                  >
                    城市: {{ filters.cities.length > 1 ? filters.cities.length + '个城市' : filters.cities[0] }}
                  </v-chip>
                  
                  <!-- 技能标签 -->
                  <template v-if="resumeSkills.length > 0">
                    <v-divider vertical class="mx-2" dark></v-divider>
                    <v-chip
                      v-for="skill in resumeSkills"
                      :key="skill"
                      small
                      close
                      @click:close="removeSkill(skill)"
                      class="mr-1 mb-1"
                      dark
                    >
                      {{ skill }}
                    </v-chip>
                  </template>
                </v-chip-group>
              </div>
              
              <v-btn
                text
                color="white"
                @click="resetFilters"
                :disabled="!hasActiveFilters && !showingRecommended"
              >
                清除筛选
              </v-btn>
            </v-col>
          </v-row>
          
          <!-- 数据统计信息 - 左下角 -->
          <v-row>
            <v-col cols="12" class="d-flex align-center pt-0">
              <div class="d-flex align-center">
                <v-chip small class="mr-2" dark>
                  <strong>{{ filteredJobs.length }}</strong><span class="ml-1">个职位</span>
                </v-chip>
                <v-chip v-if="showingRecommended && recommendedJobs.length > 0" 
                  small color="success" text-color="white" class="mr-2">
                  <v-icon x-small left>mdi-star</v-icon>推荐
                </v-chip>
                <div v-if="allJobs.length > 0" class="text-caption white--text ml-2">
                  {{ dataLoadTime }}
                </div>
              </div>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
    
    <!-- 职位列表 -->
    <div v-if="loading" class="text-center py-5">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-3">加载职位中...</div>
    </div>
    
    <div v-else>
      <!-- 卡片视图 -->
      <v-row v-if="viewMode === 'card'">
        <v-col
          v-for="job in paginatedJobs"
          :key="job.id"
          cols="12"
          sm="6"
          md="4"
        >
          <job-card 
            :job="job" 
            @start-interview="startInterview"
            :company-logo="getCompanyLogo(job.company_logo)"
          />
        </v-col>
      </v-row>
      
      <!-- 列表视图 -->
      <v-card v-else elevation="2">
        <v-data-table
          :headers="headers"
          :items="filteredJobs"
          :items-per-page="pagination.limit"
          :page.sync="pagination.page"
          :options.sync="tableOptions"
          :server-items-length="filteredJobs.length"
          :footer-props="{
            'items-per-page-options': [10, 20, 50],
            'items-per-page-text': '每页显示'
          }"
          class="job-table"
        >
          <template v-slot:item.position_name="{ item }">
            <div class="font-weight-medium">{{ item.position_name }}</div>
          </template>
          
          <template v-slot:item.company_name="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="32" class="mr-2">
                <v-img :src="getCompanyLogo(item.company_logo)"></v-img>
              </v-avatar>
              {{ item.company_name }}
            </div>
          </template>
          
          <template v-slot:item.salary="{ item }">
            <span v-if="item.salary0 > 0 || item.salary1 > 0">
              {{ item.salary0 }}-{{ item.salary1 }}K
            </span>
            <span v-else>面谈</span>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn
              small
              text
              color="primary"
              @click="viewJobDetail(item.id)"
            >
              详情
            </v-btn>
            <v-btn
              small
              text
              color="success"
              @click="startInterview(item.id)"
            >
              分析
            </v-btn>
          </template>
        </v-data-table>
      </v-card>
      
      <!-- 分页 -->
      <div class="text-center pt-5" v-if="viewMode === 'card'">
        <v-pagination
          v-model="pagination.page"
          :length="pagination.totalPages"
          :total-visible="7"
          @input="handlePageChange"
        ></v-pagination>
      </div>
      
      <!-- 无数据提示 -->
      <v-card v-if="filteredJobs.length === 0" class="text-center pa-5" elevation="0">
        <v-icon size="64" color="grey lighten-1">mdi-file-search-outline</v-icon>
        <div class="text-h6 grey--text mt-3">未找到匹配的职位</div>
        <div class="grey--text text--darken-1">尝试调整搜索条件或清除筛选</div>
      </v-card>
    </div>
    
    <!-- 分析确认对话框 -->
    <v-dialog v-model="analysisDialog" max-width="500">
      <v-card class="analysis-dialog-card" flat>
        <v-card-title>开始分析</v-card-title>
        <v-card-text>
          <p>您确定要开始分析"{{ selectedJob ? selectedJob.position_name : '' }}"的岗位信息吗？</p>
          <p class="text-caption grey--text">
            系统将分析岗位要求与您的简历匹配度，并提供针对性的建议和准备方向。
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="analysisDialog = false">取消</v-btn>
          <v-btn 
            color="primary" 
            :loading="analysisLoading"
            @click="goToInterviewHome"
          >
            开始分析
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 加载对话框 -->
    <v-dialog v-model="isLoading" persistent max-width="500">
      <v-card>
        <v-card-text class="text-center pa-5">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <div class="mt-4 text-h6">{{ loadingMessage }}</div>

          <!-- 倒计时显示 -->
          <div v-if="countdownTimer" class="mt-4">
            <v-progress-linear
              :value="((totalWaitTime - remainingTime) / totalWaitTime) * 100"
              color="primary"
              height="8"
              rounded
              class="mb-2"
            ></v-progress-linear>
            <div class="text-body-2 grey--text">
              剩余等待时间: {{ formatTime(remainingTime) }}
            </div>
          </div>

          <!-- 数据接收状态 -->
          <div v-if="countdownTimer" class="mt-4">
            <div class="text-subtitle-2 mb-2">数据接收状态:</div>
            <v-row dense>
              <v-col cols="4" class="text-center">
                <v-icon :color="dataStatus.jobAnalysisResult ? 'success' : 'grey'" size="20">
                  {{ dataStatus.jobAnalysisResult ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                </v-icon>
                <div class="text-caption">岗位分析</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <v-icon :color="dataStatus.originalWorkflowContent ? 'success' : 'grey'" size="20">
                  {{ dataStatus.originalWorkflowContent ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                </v-icon>
                <div class="text-caption">简历分析</div>
              </v-col>
              <v-col cols="4" class="text-center">
                <v-icon :color="dataStatus.starWorkflowData ? 'success' : 'grey'" size="20">
                  {{ dataStatus.starWorkflowData ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                </v-icon>
                <div class="text-caption">STAR分析</div>
              </v-col>
            </v-row>
            <div class="text-caption grey--text mt-2">
              最后检查: {{ lastDataCheck ? formatTime(Math.floor((Date.now() - lastDataCheck) / 1000)) + '前' : '未检查' }}
            </div>
          </div>

          <div class="mt-4">
            <v-btn text color="primary" @click="cancelLoading">
              取消
            </v-btn>
            <v-btn v-if="countdownTimer" text color="info" @click="checkDataStatus" class="ml-2">
              刷新状态
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import JobCard from '@/components/job/JobCard.vue'
import SearchBox from '@/components/job/SearchBox.vue'
import { getJobList, searchJobs, loadLocalJobs } from '@/api/job'
import { getCompanyLogo } from '@/utils/img'
import axios from 'axios'

export default {
  name: 'JobList',
  components: {
    JobCard,
    SearchBox
  },
  data() {
    return {
      loading: true,
      viewMode: 'card',
      allJobs: [], // 存储所有职位数据
      filteredJobs: [], // 存储筛选后的职位数据
      recommendedJobs: [], // 存储基于技能推荐的职位
      selectedJob: null,
      analysisDialog: false,
      analysisLoading: false,
      dataLoadTime: '', // 数据加载时间
      isSearchExpanded: false, // 搜索区域是否展开
      expandTimeout: null, // 用于延迟收缩的定时器
      
      // 技能相关
      resumeSkills: [],
      skillCategories: [], // 技能分类
      categorizedSkills: {}, // 按类别分组的技能
      showingRecommended: false,
      
      // 技能颜色映射
      skillColorMap: {
        'frontend': 'primary', // 前端技能
        'backend': 'indigo', // 后端技能
        'database': 'teal', // 数据库技能
        'ai': 'purple', // AI/机器学习
        'cloud': 'cyan', // 云计算
        'mobile': 'blue', // 移动开发
        'testing': 'amber', // 测试
        'devops': 'deep-orange', // DevOps/运维
        'soft_skills': 'grey', // 软技能
        'default': 'primary' // 默认颜色
      },
      
      // 技术技能与软技能
      technicalSkills: [
        'javascript', 'html', 'css', 'python', 'java', 'c++', 'c#', 'vue', 
        'react', 'angular', 'node.js', 'mysql', 'mongodb', 'redis'
      ],
      softSkills: [
        '沟通能力', '团队协作', '问题解决', '时间管理', '领导力', '创新思维',
        '分析能力', '批判性思维'
      ],
      
      // 表格配置
      tableOptions: {
        page: 1,
        itemsPerPage: 10,
        sortBy: [],
        sortDesc: []
      },
      
      // 筛选选项
      filters: {
        keyword: '',
        cities: [],
        salary: null,
        experience: null
      },
      
      // 分页
      pagination: {
        page: 1,
        limit: 12,
        totalItems: 0,
        totalPages: 0
      },
      
      // 表格头
      headers: [
        { text: '职位名称', value: 'position_name', sortable: true },
        { text: '公司', value: 'company_name', sortable: true },
        { text: '城市', value: 'city', sortable: true },
        { text: '薪资', value: 'salary', sortable: true },
        { text: '学历要求', value: 'education', sortable: true },
        { text: '操作', value: 'actions', sortable: false }
      ],
      
      // 筛选选项数据
      cities: [
        '北京', '上海', '广州', '深圳', '杭州', 
        '南京', '成都', '武汉', '西安', '苏州'
      ],
      salaryRanges: [
        { text: '3k以下', value: '0' },
        { text: '3k-5k', value: '1' },
        { text: '5k-10k', value: '2' },
        { text: '10k-15k', value: '3' },
        { text: '15k-20k', value: '4' },
        { text: '20k以上', value: '5' }
      ],
      experienceRanges: [
        { text: '应届毕业生', value: '0' },
        { text: '1-3年', value: '1' },
        { text: '3-5年', value: '2' },
        { text: '5-10年', value: '3' },
        { text: '10年以上', value: '4' }
      ],
      isLoading: false,
      loadingMessage: '正在加载...',

      // 倒计时相关属性
      countdownTimer: null, // 倒计时定时器
      dataCheckInterval: null, // 数据检查定时器
      remainingTime: 180, // 剩余时间（秒），默认3分钟
      totalWaitTime: 180, // 总等待时间（秒）
      dataStatus: {
        originalWorkflowContent: false,
        jobAnalysisResult: false,
        starWorkflowData: false
      }, // 数据接收状态
      lastDataCheck: null, // 最后一次数据检查时间
    }
  },
  computed: {
    activeFilters() {
      const active = {}
      Object.keys(this.filters).forEach(key => {
        if (this.filters[key] && 
            ((Array.isArray(this.filters[key]) && this.filters[key].length > 0) || 
            (!Array.isArray(this.filters[key]) && this.filters[key]))) {
          active[key] = this.filters[key]
        }
      })
      return active
    },
    
    hasActiveFilters() {
      return Object.keys(this.activeFilters).length > 0 || this.showingRecommended || this.resumeSkills.length > 0;
    },
    
    // 计算当前页的数据
    paginatedJobs() {
      const start = (this.pagination.page - 1) * this.pagination.limit
      const end = start + this.pagination.limit
      return this.filteredJobs.slice(start, end)
    }
  },
  methods: {
    getCompanyLogo(logo) {
      return getCompanyLogo(logo)
    },
    
    // 已删除圆形动画，不再需要createRipple方法
    
    // 搜索区域展开/收缩逻辑
    toggleSearchArea() {
      // 简化后的搜索区域切换逻辑
      this.isSearchExpanded = !this.isSearchExpanded;
      
      // 设置页面滚动
      if (this.isSearchExpanded) {
        document.body.style.overflow = 'auto';
      }
    },
    
    // 处理点击外部区域
    handleOutsideClick(event) {
      if (this.isSearchExpanded && 
          this.$refs.searchCard && this.$refs.searchCard.$el && 
          !this.$refs.searchCard.$el.contains(event.target)) {
        // 切换搜索区域状态
        this.isSearchExpanded = false;
      }
    },
    
    // 处理全局点击事件
    handleGlobalClick(event) {
      // 如果搜索区域已展开且点击的不是搜索卡片内部元素
      // 使用 $el 获取实际的 DOM 元素，因为 $refs.searchCard 是 Vue 组件实例
      if (this.isSearchExpanded && this.$refs.searchCard && this.$refs.searchCard.$el && !this.$refs.searchCard.$el.contains(event.target)) {
        console.log('全局点击事件：点击了搜索区域外部，收起搜索区域');
        
        // 切换搜索区域状态
        this.isSearchExpanded = false;
        
        // 直接使用点击位置创建收缩动画
        if (event && event.clientX && event.clientY) {
          this.createRipple(event.clientX, event.clientY, false);
        }
      }
    },
    

    

    
    // 加载所有职位数据
    async loadAllJobs() {
      this.loading = true;
      try {
        // 尝试从本地JSON加载数据
        const response = await loadLocalJobs();
        
        if (response.code === 200) {
          this.allJobs = response.data.list || [];
          // 设置数据加载时间
          this.dataLoadTime = new Date().toLocaleString();
          // 初始筛选
          this.filterJobs();
          
          // 如果有技能信息，加载推荐岗位
          if (this.resumeSkills && this.resumeSkills.length > 0) {
            await this.loadRecommendedJobs();
          }
        } else {
          // 如果本地加载失败，尝试API请求
          const apiResponse = await searchJobs({
            page: 1,
            pageSize: 1000, // 一次性获取大量数据
            keyword: ''
          });
          
          if (apiResponse.code === 200) {
            this.allJobs = apiResponse.data.list || [];
            this.dataLoadTime = new Date().toLocaleString();
            this.filterJobs();
            
            // 如果有技能信息，加载推荐岗位
            if (this.resumeSkills && this.resumeSkills.length > 0) {
              await this.loadRecommendedJobs();
            }
          } else {
            this.$store.dispatch('snackbar/showMessage', {
              message: apiResponse.message || '加载职位失败',
              color: 'error'
            });
          }
        }
      } catch (error) {
        console.error('加载职位失败:', error);
        this.$store.dispatch('snackbar/showMessage', {
          message: '加载职位失败，请稍后重试',
          color: 'error'
        });
      } finally {
        this.loading = false;
      }
    },
    
    // 加载推荐岗位
    async loadRecommendedJobs() {
      if (!this.resumeSkills || this.resumeSkills.length === 0) {
        console.log('没有提取到技能，无法推荐岗位');
        return;
      }

      console.log('开始加载推荐岗位，技能列表:', this.resumeSkills);
      
      try {
        // 设置超时，确保请求不会无限等待
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('请求超时')), 10000);
        });
        
        // 调用API获取推荐岗位，添加超时处理
        const responsePromise = this.$axios.get('/api/jobs/recommend-by-skills', {
          params: {
            skills: this.resumeSkills.join(',')
          }
        });
        
        // 使用Promise.race确保请求不会超时
        const response = await Promise.race([responsePromise, timeoutPromise]);
        
        if (response.data && response.data.code === 200 && response.data.data) {
          this.recommendedJobs = response.data.data.list || [];
          console.log('推荐岗位API成功，获得职位数量:', this.recommendedJobs.length);

          // 处理技能分类信息
          if (response.data.data.skill_categories) {
            this.skillCategories = response.data.data.skill_categories;
          }

          // 处理分类后的技能信息
          if (response.data.data.display_skills) {
            const displaySkills = response.data.data.display_skills;
            this.categorizedSkills = displaySkills.categorized_skills || {};
          }

          // 如果有推荐岗位，自动切换到推荐模式
          if (this.recommendedJobs.length > 0 && !this.showingRecommended) {
            console.log('切换到推荐模式，显示推荐岗位');
            this.showingRecommended = true;
            this.updateDisplayedJobs();
          } else if (this.recommendedJobs.length === 0) {
            console.log('没有推荐岗位，回退到显示全部岗位');
            // 显示提示信息
            this.$store.dispatch('snackbar/showMessage', {
              content: '未找到与您技能匹配的岗位，显示全部岗位',
              color: 'info'
            });

            // 回退：使用本地职位数据进行简单匹配
            this.fallbackToLocalMatching();
          }
        } else {
          console.log('推荐岗位API返回异常:', response.data);
          // 显示错误信息
          this.$store.dispatch('snackbar/showMessage', {
            content: '获取推荐岗位失败: ' + (response.data && response.data.message ? response.data.message : '未知错误'),
            color: 'warning'
          });
          
          // 回退：使用本地职位数据进行简单匹配
          this.fallbackToLocalMatching();
        }
      } catch (error) {
        console.error('加载推荐岗位失败:', error);
        console.log('推荐API失败，将使用本地匹配');
        // 显示错误信息
        this.$store.dispatch('snackbar/showMessage', {
          content: '加载推荐岗位失败，使用本地匹配',
          color: 'error'
        });
        
        // 回退：使用本地职位数据进行简单匹配
        this.fallbackToLocalMatching();
      }
    },
    
    // 回退方法：使用本地职位数据进行简单匹配
    fallbackToLocalMatching() {
      console.log('开始本地匹配，总职位数:', this.allJobs.length);
      if (!this.allJobs || this.allJobs.length === 0) {
        return;
      }

      // 使用简单的字符串匹配来查找相关职位
      const matchedJobs = this.allJobs.filter(job => {
        // 检查职位名称、公司名称等字段是否包含技能关键词
        return this.resumeSkills.some(skill => {
          const skillLower = skill.toLowerCase();
          const positionName = (job.position_name || '').toLowerCase();
          const companyName = (job.company_name || '').toLowerCase();
          const education = (job.education || '').toLowerCase();
          const welfare = (job.welfare || '').toLowerCase();
          
          return positionName.includes(skillLower) || 
                 companyName.includes(skillLower) || 
                 education.includes(skillLower) || 
                 welfare.includes(skillLower);
        });
      });
      
      console.log('本地匹配结果，匹配职位数:', matchedJobs.length);

      if (matchedJobs.length > 0) {
        this.recommendedJobs = matchedJobs;
        this.showingRecommended = true;
        this.updateDisplayedJobs();

        console.log('使用本地匹配结果，显示推荐职位');
        // 显示提示信息
        this.$store.dispatch('snackbar/showMessage', {
          message: `已找到${matchedJobs.length}个可能相关的职位`,
          color: 'success'
        });
      } else {
        // 不切换到推荐模式，显示全部职位
        this.showingRecommended = false;
        this.filterJobs();
      }
    },
    
    // 切换显示推荐岗位或全部岗位
    toggleRecommendedJobs() {
      this.showingRecommended = !this.showingRecommended;
      this.updateDisplayedJobs();
    },
    
    // 更新显示的岗位列表
    updateDisplayedJobs() {
      if (this.showingRecommended && this.recommendedJobs.length > 0) {
        this.filteredJobs = this.recommendedJobs;
      } else {
        this.filterJobs(); // 使用原有的筛选方法
      }
      
      // 重置分页
      this.pagination.page = 1;
      this.updatePagination();
    },
    
    // 判断是否为技术技能
    isTechnicalSkill(skill) {
      return !this.softSkills.includes(skill.toLowerCase());
    },
    
    // 获取技能对应的颜色
    getSkillColor(skill) {
      const skillLower = skill.toLowerCase();
      
      // 检查是否为软技能
      if (this.softSkills.includes(skillLower)) {
        return 'grey';
      }
      
      // 检查是否为前端技能
      if (['javascript', 'html', 'css', 'vue', 'react', 'angular'].includes(skillLower)) {
        return 'primary';
      }
      
      // 检查是否为后端技能
      if (['python', 'java', 'c++', 'c#', 'go', 'php', 'ruby'].includes(skillLower)) {
        return 'indigo';
      }
      
      // 检查是否为数据库技能
      if (['mysql', 'mongodb', 'redis', 'postgresql', 'sql'].includes(skillLower)) {
        return 'teal';
      }
      
      // 默认颜色
      return 'primary';
    },
    
    // 前端筛选职位数据
    filterJobs() {
      // 如果正在显示推荐岗位，不执行常规筛选
      if (this.showingRecommended && this.recommendedJobs.length > 0) {
        this.filteredJobs = this.recommendedJobs;
        this.updatePagination();
        return;
      }
      
      // 从所有数据中根据筛选条件过滤
      this.filteredJobs = this.allJobs.filter(job => {
        // 关键词筛选
        if (this.filters.keyword && !job.position_name.toLowerCase().includes(this.filters.keyword.toLowerCase())) {
          return false;
        }
        
        // 城市筛选 - 多选
        if (this.filters.cities && this.filters.cities.length > 0 && !this.filters.cities.includes(job.city)) {
          return false;
        }
        
        // 薪资范围筛选
        if (this.filters.salary) {
          const salaryValue = parseInt(this.filters.salary);
          const salary0 = job.salary0 || 0;
          
          // 根据薪资范围筛选
          const salaryRanges = {
            0: [0, 3],
            1: [3, 5],
            2: [5, 10],
            3: [10, 15],
            4: [15, 20],
            5: [20, 50]
          };
          
          const [min, max] = salaryRanges[salaryValue] || [0, 0];
          if (salary0 < min || salary0 > max) {
            return false;
          }
        }
        
        // 工作经验筛选
        if (this.filters.experience) {
          const expValue = parseInt(this.filters.experience);
          const worktime0 = job.worktime0 || 0;
          
          // 根据工作经验范围筛选
          const worktimeRanges = {
            0: [0, 1],
            1: [1, 3],
            2: [3, 5],
            3: [5, 10],
            4: [10, 100]
          };
          
          const [min, max] = worktimeRanges[expValue] || [0, 0];
          if (worktime0 < min || worktime0 > max) {
            return false;
          }
        }
        
        return true;
      });
      
      // 更新分页信息
      this.updatePagination();
    },
    
    // 更新分页信息
    updatePagination() {
      this.pagination.totalItems = this.filteredJobs.length;
      this.pagination.totalPages = Math.ceil(this.pagination.totalItems / this.pagination.limit);
      
      // 如果当前页超出范围，重置为第一页
      if (this.pagination.page > this.pagination.totalPages) {
        this.pagination.page = 1;
      }
    },
    
    handleSearch(searchParams) {
      this.filters.keyword = searchParams.keyword;
      this.pagination.page = 1;
      
      // 使用本地筛选代替API请求
      this.filterJobs();
      
      // 更新URL查询参数
      this.updateUrlParams();
    },
    
    applyFilters() {
      this.pagination.page = 1;
      this.filterJobs();
      
      // 更新URL查询参数
      this.updateUrlParams();
    },
    
    // 从城市多选中移除单个城市
    removeCity(city) {
      const index = this.filters.cities.indexOf(city);
      if (index !== -1) {
        this.filters.cities.splice(index, 1);
        this.applyFilters();
      }
    },
    
    // 从技能标签中移除单个技能
    removeSkill(skill) {
      const index = this.resumeSkills.indexOf(skill);
      if (index !== -1) {
        this.resumeSkills.splice(index, 1);
        
        // 如果移除了最后一个技能标签，退出推荐岗位模式
        if (this.resumeSkills.length === 0) {
          this.showingRecommended = false;
        }
        
        this.applyFilters(); // 重新筛选以应用新的技能列表
        
        // 更新本地存储
        localStorage.setItem('extractedSkills', JSON.stringify(this.resumeSkills));
      }
    },
    
    // 更新URL查询参数
    updateUrlParams() {
      // 更新URL查询参数，保持浏览器历史记录
      const query = {};
      if (this.filters.keyword) query.keyword = this.filters.keyword;
      if (this.filters.cities && this.filters.cities.length > 0) query.cities = this.filters.cities.join(',');
      if (this.filters.salary) query.salary = this.filters.salary;
      if (this.filters.experience) query.experience = this.filters.experience;
      if (this.pagination.page > 1) query.page = this.pagination.page;
      
      // 使用router.replace更新URL但不新增历史记录
      this.$router.replace({ query });
    },
    
    removeFilter(key) {
      if (key === 'cities') {
        this.filters.cities = [];
      } else {
        this.filters[key] = null;
      }
      this.applyFilters();
    },
    
    resetFilters() {
      this.filters.keyword = null;
      this.filters.cities = [];
      this.filters.salary = null;
      this.filters.experience = null;
      // 重置推荐岗位状态
      this.showingRecommended = false;
      // 清除技能标签
      this.resumeSkills = [];
      // 更新本地存储
      localStorage.setItem('extractedSkills', JSON.stringify(this.resumeSkills));
      this.applyFilters();
    },
    
    getFilterLabel(key, value) {
      const labels = {
        keyword: '关键词',
        salary: '薪资',
        experience: '经验'
      };
      
      let displayValue = value;
      
      // 处理选项类型的值
      if (key === 'salary') {
        const salary = this.salaryRanges.find(s => s.value === value);
        if (salary) displayValue = salary.text;
      } else if (key === 'experience') {
        const exp = this.experienceRanges.find(e => e.value === value);
        if (exp) displayValue = exp.text;
      }
      
      return `${labels[key]}: ${displayValue}`;
    },
    
    handlePageChange(page) {
      this.pagination.page = page;
      
      // 更新URL查询参数
      this.updateUrlParams();
      
      // 滚动到顶部
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    viewJobDetail(id) {
      this.$router.push(`/job/detail/${id}`);
    },
    
    startInterview(jobId) {
      // 先验证是否已上传简历
      const resumeUploadData = localStorage.getItem('resumeUploadData');

      if (!resumeUploadData) {
        // 如果没有上传简历，显示提示信息
        this.$store.dispatch('snackbar/showMessage', {
          content: '请先上传简历才能进行分析',
          color: 'warning'
        });

        // 可以选择跳转到简历上传页面
        if (confirm('您需要先上传简历才能进行岗位分析。是否前往简历上传页面？')) {
          this.$router.push('/resume/upload');
        }
        return;
      }

      // 验证resumeUploadData中是否包含提取的文本
      try {
        const resumeData = JSON.parse(resumeUploadData);

        // 检查是否有提取的文本内容
        if (!resumeData.extractedText) {
          // 检查是否是文本提取失败的情况
          if (resumeData.textExtractionFailed) {
            console.warn('简历文本提取失败，但文件已上传');
            this.$store.dispatch('snackbar/showMessage', {
              content: '简历文本提取失败，分析功能可能受限。是否继续？',
              color: 'warning'
            });

            if (confirm('简历文本提取失败，分析功能可能受限。是否继续分析？\n\n点击"确定"继续，点击"取消"重新上传简历。')) {
              // 用户选择继续，使用有限功能
              console.log('用户选择在文本提取失败的情况下继续分析');
            } else {
              this.$router.push('/resume/upload');
              return;
            }
          } else {
            console.warn('resumeUploadData中没有提取的文本内容');
            this.$store.dispatch('snackbar/showMessage', {
              content: '简历数据不完整，请重新上传简历',
              color: 'warning'
            });

            if (confirm('简历数据不完整，是否重新上传简历？')) {
              this.$router.push('/resume/upload');
            }
            return;
          }
        }
      } catch (e) {
        console.error('解析resumeUploadData失败:', e);
        this.$store.dispatch('snackbar/showMessage', {
          content: '简历数据格式错误，请重新上传简历',
          color: 'error'
        });

        if (confirm('简历数据格式错误，是否重新上传简历？')) {
          this.$router.push('/resume/upload');
        }
        return;
      }

      // 已上传简历，继续正常流程
      this.selectedJob = this.allJobs.find(job => job.id === jobId);
      this.analysisDialog = true;
    },
    
    goToInterviewHome() {
      this.analysisDialog = false;
      
      // 跳转到面试分析页面，并传递职位数据
      if (this.selectedJob) {
        // 显示加载对话框并启动倒计时
        this.isLoading = true;
        this.loadingMessage = `正在分析"${this.selectedJob.position_name}"岗位信息...\n等待工作流数据接收 (最多3分钟)`;

        // 启动3分钟倒计时
        this.startCountdown();
        
        // 启动岗位分析API调用（异步进行，不阻塞倒计时）
        this.$axios.post('/api/job/analyze', {
          jobName: this.selectedJob.position_name
        }, {
          timeout: 300000, // 300秒超时
          retry: 0 // 不重试
        })
        .then(response => {
          console.log('岗位分析结果:', response.data);
          if (response.data && response.data.code === 0) {
            // 保存数据到localStorage
            localStorage.setItem('jobAnalysisResult', JSON.stringify(response.data.data));
            console.log('岗位分析数据已保存到localStorage');

            this.$store.dispatch('snackbar/showMessage', {
              message: '岗位分析完成',
              color: 'success'
            });
          } else {
            this.$store.dispatch('snackbar/showMessage', {
              message: response.data.message || '岗位分析返回错误',
              color: 'warning'
            });
          }
        })
        .catch(error => {
          console.error('岗位分析请求失败:', error);
          this.$store.dispatch('snackbar/showMessage', {
            message: '岗位分析请求失败',
            color: 'warning'
          });
        });

        // 显示初始数据状态提示
        const originalContent = localStorage.getItem('originalWorkflowContent');
        const starData = localStorage.getItem('starWorkflowData');

        console.log('初始数据状态检查:');
        console.log('简历数据:', originalContent ? `存在 (${originalContent.length}字符)` : '不存在');
        console.log('STAR数据:', starData ? `存在 (${starData.length}字符)` : '不存在');

        // 如果缺少STAR数据，显示提示
        if (originalContent && !starData) {
          this.$store.dispatch('snackbar/showMessage', {
            message: '未检测到STAR分析数据，等待工作流处理',
            color: 'info'
          });
        }

        // 倒计时机制将自动处理数据等待和检查
        console.log('岗位分析API已启动，倒计时等待工作流数据接收...');
      }
    },
    
    // 取消加载方法
    cancelLoading() {
      this.stopCountdown(); // 停止倒计时
      this.isLoading = false;
      this.$store.dispatch('snackbar/showMessage', {
        content: '已取消加载',
        color: 'info'
      });
    },

    // 开始倒计时
    startCountdown() {
      console.log('开始3分钟倒计时等待工作流数据...');

      // 重置倒计时状态
      this.remainingTime = this.totalWaitTime;
      this.lastDataCheck = Date.now();

      // 初始数据状态检查
      this.checkDataStatus();

      // 启动倒计时定时器（每秒更新）
      this.countdownTimer = setInterval(() => {
        this.remainingTime--;

        if (this.remainingTime <= 0) {
          console.log('倒计时结束，进行最终数据检查');
          this.handleCountdownEnd();
        }
      }, 1000);

      // 启动数据检查定时器（每10秒检查一次）
      this.dataCheckInterval = setInterval(() => {
        this.checkDataStatus();
      }, 10000);

      console.log('倒计时和数据检查定时器已启动');
    },

    // 停止倒计时
    stopCountdown() {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer);
        this.countdownTimer = null;
        console.log('倒计时定时器已清除');
      }

      if (this.dataCheckInterval) {
        clearInterval(this.dataCheckInterval);
        this.dataCheckInterval = null;
        console.log('数据检查定时器已清除');
      }
    },

    // 格式化时间显示
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },

    // 检查数据状态
    checkDataStatus() {
      console.log('检查工作流数据状态...');

      // 更新最后检查时间
      this.lastDataCheck = Date.now();

      // 检查各项数据是否存在
      const originalContent = localStorage.getItem('originalWorkflowContent');
      const jobAnalysisResult = localStorage.getItem('jobAnalysisResult');
      const starWorkflowData = localStorage.getItem('starWorkflowData');

      // 更新数据状态
      const previousStatus = { ...this.dataStatus };
      this.dataStatus.originalWorkflowContent = !!originalContent && originalContent.length > 100;
      this.dataStatus.jobAnalysisResult = !!jobAnalysisResult && jobAnalysisResult.length > 50;
      this.dataStatus.starWorkflowData = !!starWorkflowData && starWorkflowData.length > 50;

      // 检查是否有新数据接收
      const hasNewData = Object.keys(this.dataStatus).some(key =>
        this.dataStatus[key] && !previousStatus[key]
      );

      if (hasNewData) {
        console.log('检测到新的工作流数据接收');
        this.$store.dispatch('snackbar/showMessage', {
          message: '检测到新数据接收',
          color: 'success'
        });
      }

      // 计算已接收的数据数量
      const receivedCount = Object.values(this.dataStatus).filter(status => status).length;
      const totalCount = Object.keys(this.dataStatus).length;

      console.log(`数据接收状态: ${receivedCount}/${totalCount}`);
      console.log('详细状态:', this.dataStatus);

      // 如果所有数据都已接收，自动结束等待
      if (receivedCount === totalCount) {
        console.log('所有工作流数据已接收完成，结束等待');
        this.handleAllDataReceived();

        // 调用 job-resume-workflow 接口
        this.callJobResumeWorkflow();
      }

      return {
        receivedCount,
        totalCount,
        dataStatus: this.dataStatus
      };
    },

    // 处理倒计时结束
    handleCountdownEnd() {
      console.log('3分钟倒计时结束');
      this.stopCountdown();

      // 进行最终数据检查
      const finalStatus = this.checkDataStatus();

      if (finalStatus.receivedCount === finalStatus.totalCount) {
        // 所有数据都已接收
        this.$store.dispatch('snackbar/showMessage', {
          message: '所有工作流数据已接收完成',
          color: 'success'
        });
        this.proceedToAnalysis();
      } else if (finalStatus.receivedCount > 0) {
        // 部分数据已接收
        const missingData = Object.keys(this.dataStatus)
          .filter(key => !this.dataStatus[key])
          .map(key => {
            switch(key) {
              case 'originalWorkflowContent': return '简历分析';
              case 'jobAnalysisResult': return '岗位分析';
              case 'starWorkflowData': return 'STAR分析';
              default: return key;
            }
          });

        this.$store.dispatch('snackbar/showMessage', {
          message: `等待超时，部分数据已接收 (${finalStatus.receivedCount}/${finalStatus.totalCount})`,
          color: 'warning'
        });

        // 询问用户是否继续
        if (confirm(`等待时间已到，部分数据已接收 (${finalStatus.receivedCount}/${finalStatus.totalCount})，缺少：${missingData.join('、')}\n\n是否使用已有数据继续分析？`)) {
          this.proceedToAnalysis();
        } else {
          this.isLoading = false;
        }
      } else {
        // 没有接收到任何数据
        this.$store.dispatch('snackbar/showMessage', {
          message: '等待超时，未接收到工作流数据',
          color: 'error'
        });

        if (confirm('等待时间已到，未接收到任何工作流数据。\n\n是否重新尝试或取消操作？\n\n点击"确定"重新尝试，点击"取消"结束操作。')) {
          // 重新开始倒计时
          this.startCountdown();
        } else {
          this.isLoading = false;
        }
      }
    },

    // 处理所有数据接收完成
    handleAllDataReceived() {
      console.log('所有工作流数据接收完成，自动进入分析页面');
      this.stopCountdown();

      this.$store.dispatch('snackbar/showMessage', {
        message: '所有工作流数据接收完成',
        color: 'success'
      });

      // 延迟1秒后跳转，让用户看到成功消息
      setTimeout(() => {
        this.proceedToAnalysis();
      }, 1000);
    },

    // 调用 job-resume-workflow 接口
    async callJobResumeWorkflow() {
      try {
        console.log('开始调用 job-resume-workflow 接口...');

        // 获取所需的数据
        const originalWorkflowContent = localStorage.getItem('originalWorkflowContent');
        const jobAnalysisResult = localStorage.getItem('jobAnalysisResult');

        if (!originalWorkflowContent || !jobAnalysisResult) {
          console.warn('缺少必要数据，无法调用 job-resume-workflow');
          return;
        }

        // 准备请求数据
        const requestData = {
          userInput: originalWorkflowContent,
          jobSkill: jobAnalysisResult
        };

        console.log('调用 job-resume-workflow，请求数据:', {
          userInputLength: originalWorkflowContent.length,
          jobSkillLength: jobAnalysisResult.length
        });

        // 异步调用接口，不等待响应
        this.$axios.post('/api/interview/job-resume-workflow', requestData, {
          timeout: 300000, // 5分钟超时
          retry: 0 // 不重试
        })
        .then(response => {
          console.log('job-resume-workflow 接口调用成功:', response.data);

          if (response.data && response.data.code === 0) {
            // 保存结果到 localStorage
            localStorage.setItem('jobResumeWorkflowResult', JSON.stringify(response.data.data));
            console.log('job-resume-workflow 结果已保存到 localStorage');

            this.$store.dispatch('snackbar/showMessage', {
              message: '岗位简历匹配分析完成',
              color: 'success'
            });
          } else {
            console.warn('job-resume-workflow 接口返回异常:', response.data);
          }
        })
        .catch(error => {
          console.error('job-resume-workflow 接口调用失败:', error);
          // 不显示错误消息，因为这是后台异步调用
        });

        console.log('job-resume-workflow 接口已异步启动');

      } catch (error) {
        console.error('调用 job-resume-workflow 接口时发生错误:', error);
      }
    },

    // 进入分析页面
    proceedToAnalysis() {
      this.isLoading = false;

      if (this.selectedJob) {
        this.$router.push({
          path: '/interview/analysis',
          query: {
            jobId: this.selectedJob.id,
            jobName: this.selectedJob.position_name,
            companyName: this.selectedJob.company_name,
            city: this.selectedJob.city,
            salary: `${this.selectedJob.salary0}-${this.selectedJob.salary1}K`,
            experience: `${this.selectedJob.worktime0}-${this.selectedJob.worktime1}年`,
            education: this.selectedJob.education
          }
        });
      }
    },

    // 处理localStorage变化
    handleStorageChange(event) {
      if (event.key === 'extractedSkills') {
        console.log('检测到localStorage中技能数据变化:', event.newValue);
        this.loadSkillsFromStorage();
      }
    },

    // 处理自定义技能更新事件
    handleSkillsUpdate() {
      console.log('收到技能更新事件');
      this.loadSkillsFromStorage();
    },

    // 从localStorage加载技能
    loadSkillsFromStorage() {
      try {
        const storedSkills = localStorage.getItem('extractedSkills');
        console.log('重新加载技能数据:', storedSkills);

        if (storedSkills) {
          const newSkills = JSON.parse(storedSkills);
          if (JSON.stringify(newSkills) !== JSON.stringify(this.resumeSkills)) {
            this.resumeSkills = newSkills;
            console.log('技能数据已更新:', this.resumeSkills);

            // 重新加载推荐岗位
            if (this.resumeSkills.length > 0) {
              this.loadRecommendedJobs();
            }
          }
        }
      } catch (e) {
        console.error('重新加载技能数据失败:', e);
      }
    },
  },
  created() {
    // 从URL获取查询参数
    const query = this.$route.query;
    if (query.keyword) this.filters.keyword = query.keyword;
    if (query.cities) this.filters.cities = query.cities.split(',');
    if (query.salary) this.filters.salary = query.salary;
    if (query.experience) this.filters.experience = query.experience;
    if (query.page) this.pagination.page = parseInt(query.page) || 1;
    
    // 从本地存储获取技能信息
    try {
      const storedSkills = localStorage.getItem('extractedSkills');
      console.log('JobList页面读取localStorage中的技能:', storedSkills);

      if (storedSkills) {
        this.resumeSkills = JSON.parse(storedSkills);
        console.log('成功解析技能:', this.resumeSkills);
      } else {
        console.warn('localStorage中没有找到extractedSkills，使用默认技能');
        // 使用默认技能 - 添加前端开发关键词
        this.resumeSkills = ['前端开发', 'javascript', 'html', 'css', 'vue'];
      }
    } catch (e) {
      console.error('解析技能信息失败:', e);
      // 解析失败时也使用默认技能 - 添加前端开发关键词
      this.resumeSkills = ['前端开发', 'javascript', 'html', 'css', 'vue'];
    }

    console.log('JobList页面最终使用的技能:', this.resumeSkills);
    
    // 加载所有职位数据
    this.loadAllJobs();
  },
  
  mounted() {
    // 监听localStorage变化，当技能更新时自动刷新
    window.addEventListener('storage', this.handleStorageChange);

    // 也监听自定义事件（用于同一页面内的更新）
    window.addEventListener('skillsUpdated', this.handleSkillsUpdate);

    // 添加全局点击事件监听器，确保点击事件能够正确传播
    document.addEventListener('click', this.handleGlobalClick);
    console.log('已添加全局点击事件监听器');
    
    // 确保 $refs.searchCard 已正确挂载
    this.$nextTick(() => {
      if (this.$refs.searchCard) {
        console.log('searchCard 已挂载，类型:', typeof this.$refs.searchCard);
        console.log('searchCard.$el 是否存在:', !!this.$refs.searchCard.$el);
      } else {
        console.warn('searchCard 未挂载');
      }
    });
  },
  
  beforeDestroy() {
    // 移除全局点击事件监听器
    document.removeEventListener('click', this.handleGlobalClick);
    console.log('已移除全局点击事件监听器');

    // 移除localStorage监听器
    window.removeEventListener('storage', this.handleStorageChange);
    window.removeEventListener('skillsUpdated', this.handleSkillsUpdate);

    // 清理倒计时定时器
    this.stopCountdown();
    console.log('组件销毁时已清理倒计时定时器');
  },
  watch: {
    '$route.query': {
      handler(query) {
        // 当URL查询参数变化时更新筛选条件
        if (query.keyword !== this.filters.keyword) this.filters.keyword = query.keyword || null;
        if (query.cities) {
          const citiesArray = query.cities.split(',');
          if (JSON.stringify(citiesArray) !== JSON.stringify(this.filters.cities)) {
            this.filters.cities = citiesArray;
          }
        } else if (this.filters.cities.length > 0) {
          this.filters.cities = [];
        }
        if (query.salary !== this.filters.salary) this.filters.salary = query.salary || null;
        if (query.experience !== this.filters.experience) this.filters.experience = query.experience || null;
        if (query.page && parseInt(query.page) !== this.pagination.page) {
          this.pagination.page = parseInt(query.page) || 1;
        }
        
        // 如果路由参数变化，重新筛选数据
        if (this.allJobs.length > 0) {
          this.filterJobs();
        }
      },
      immediate: true
    },
    // 当表格选项改变时更新分页
    tableOptions: {
      handler(val) {
        this.pagination.page = val.page;
        this.pagination.limit = val.itemsPerPage;
        this.updatePagination();
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.job-list-container {
  padding-bottom: 60px;
  position: relative;
  overflow: hidden;
  background-color: white; /* 默认白色背景 */
  min-height: 100vh; /* 确保容器高度足够 */
  transition: background-color 0.5s ease; /* 平滑背景色变化 */
}

.job-list-container.dark-background {
  background-color: rgba(0, 0, 0, 0.95); /* 搜索展开时的黑色背景 */
}

.job-table {
  border-radius: 4px;
}

/* 职位列表卡片和表格样式 */
.job-list-container .v-card,
.job-list-container .v-data-table,
.job-list-container .v-row {
  position: relative;
}

.search-filter-card {
  transition: all 0.6s ease-in-out !important; /* 增加过渡时间 */
  transform: none !important;
  overflow: hidden;
  border-radius: 8px;
  position: relative; /* 确保z-index生效 */
  z-index: 10; /* 高于圆形覆盖层 */
  box-shadow: 0 8px 16px rgba(0,0,0,0.2); /* 增强阴影效果 */
}

.search-filter-card.collapsed {
  max-height: 60px;
  cursor: pointer;
}

.search-filter-card.expanded {
  max-height: 500px;
}

.collapsed-content {
  padding: 8px 0;
  cursor: pointer;
}

.white-label :deep(.v-label) {
  color: white !important;
}

.white-label :deep(.v-icon) {
  color: white !important;
}

.white-label :deep(.v-select__selection) {
  color: white !important;
}

/* 禁用面试确认对话框的悬停效果 */
.analysis-dialog-card {
  transition: none !important;
  transform: none !important;
  animation: none !important;
  box-shadow: 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
}

.analysis-dialog-card:hover {
  transform: none !important;
  box-shadow: 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
}

/* 禁用对话框内部元素的动画效果 */
.analysis-dialog-card * {
  transition: none !important;
  animation: none !important;
  transform: none !important;
}
</style> 