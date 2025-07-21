<template>
  <div class="split-screen-container">
    <!-- 左侧白色区域 - 上传简历 -->
    <div 
      class="split-side white-side" 
      :class="{ 
        'active': activeArea === 'upload', 
        'inactive': activeArea === 'ai',
        'hidden': hasResume && activeArea === 'ai'
      }"
      @click="setActiveArea('upload')"
    >
      <div class="side-content">
        <div class="side-icon" :class="{'minimized': activeArea === 'upload'}" v-if="activeArea !== 'upload'">
          <v-icon size="64" color="primary" class="mb-4">mdi-cloud-upload-outline</v-icon>
          <h2 class="text-h4 font-weight-medium">上传简历</h2>
          <p class="text-subtitle-1 text-medium-emphasis mt-2">上传您现有的简历文件</p>
        </div>
        
        <animated-popup 
          :visible="activeArea === 'upload'"
          position="center"
          :closable="false"
          content-class="upload-popup"
          class="popup-container"
        >
          <resume-uploader @upload-success="onUploadSuccess" @continue="goToJobSelection" />
        </animated-popup>
      </div>
      
      <!-- 初始状态下的点击提示 -->
      <div v-if="!hasInteracted && activeArea === null" class="click-hint white-hint">
        <v-icon color="primary" size="28" class="mb-1">mdi-gesture-tap</v-icon>
        <p class="text-caption">点击选择</p>
      </div>
    </div>
    
    <!-- 右侧黑色区域 - AI生成简历 -->
    <div 
      class="split-side black-side" 
      :class="{ 
        'active': activeArea === 'ai', 
        'inactive': activeArea === 'upload',
        'fullscreen': hasResume && activeArea === 'ai'
      }"
      @click="setActiveArea('ai')"
    >
      <div class="side-content">
        <div class="side-icon" :class="{'minimized': activeArea === 'ai'}" v-if="activeArea !== 'ai'">
          <v-icon size="64" color="white" class="mb-4">mdi-robot-outline</v-icon>
          <h2 class="text-h4 font-weight-medium white--text">AI生成简历</h2>
          <p class="text-subtitle-1 text-medium-emphasis mt-2 white--text">使用AI智能生成专业简历</p>
        </div>
        
        <animated-popup 
          :visible="activeArea === 'ai'"
          position="center"
          :closable="false"
          content-class="ai-popup"
          inner-class="popup-dark no-padding full-black"
          class="popup-container"
        >
          <ai-resume-generator @generation-complete="onGenerationComplete" @preview-resume="showPreview = true" />
        </animated-popup>
      </div>
      
      <!-- 初始状态下的点击提示 -->
      <div v-if="!hasInteracted && activeArea === null" class="click-hint black-hint">
        <v-icon color="white" size="28" class="mb-1">mdi-gesture-tap</v-icon>
        <p class="text-caption white--text">点击选择</p>
      </div>
    </div>
    
    <!-- 简历预览弹窗 -->
    <v-dialog v-model="showPreview" max-width="800" persistent>
      <v-card class="resume-preview-card">
        <v-card-title class="headline d-flex justify-space-between align-center">
          <div class="d-flex align-center">
            <v-icon color="primary" class="mr-2">mdi-file-document-check</v-icon>
            <span>简历预览</span>
          </div>
          <div>
            <v-btn icon class="mr-2" @click="editResume" color="primary">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon @click="downloadResume" color="success">
              <v-icon>mdi-download</v-icon>
            </v-btn>
            <v-btn icon @click="showPreview = false" color="error">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-title>
        <v-card-text>
          <v-alert
            type="success"
            outlined
            icon="mdi-check-circle"
            class="mb-6"
          >
            您的简历已准备就绪！现在可以进行下一步操作。
          </v-alert>
          
          <div class="resume-preview-container">
            <!-- 如果是链接，显示链接 -->
            <div v-if="isResumeLink" class="text-center my-6">
              <v-alert
                type="info"
                outlined
                icon="mdi-link-variant"
                class="mb-4"
              >
                您的简历已生成，可通过以下链接下载：
              </v-alert>
              
              <!-- 简历预览图 -->
              <div v-if="resumePreviewImage" class="resume-preview-image-container mb-4">
                <v-img
                  :src="resumePreviewImage"
                  max-height="400"
                  contain
                  class="resume-preview-image"
                ></v-img>
              </div>
              
              <!-- 下载按钮 -->
              <v-btn
                color="primary"
                large
                :href="resumeData.generatedContent"
                target="_blank"
                class="mb-4"
              >
                <v-icon left>mdi-download</v-icon>
                下载简历
              </v-btn>
              
              <!-- 如果有多个模板，显示所有模板 -->
              <div v-if="hasMultipleTemplates" class="resume-templates mt-6">
                <h3 class="text-h6 mb-4">其他模板</h3>
                <v-row>
                  <v-col 
                    v-for="(link, index) in resumeData.allLinks" 
                    :key="index"
                    cols="12" sm="6" md="4"
                    class="d-flex flex-column align-center"
                  >
                    <v-img
                      :src="link.img_url"
                      height="150"
                      contain
                      class="mb-2"
                    ></v-img>
                    <v-btn
                      small
                      outlined
                      color="primary"
                      :href="link.word_url"
                      target="_blank"
                    >
                      模板 {{ index + 1 }}
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </div>
            
            <!-- 如果是文本内容，显示简历内容 -->
            <div v-else class="text-center my-6">
              <v-img
                v-if="!resumeContent"
                src="@/assets/images/resume-preview.png"
                max-height="400"
                contain
                class="resume-preview-image"
              ></v-img>
              
              <!-- 简历文本内容 -->
              <div v-else class="resume-text-content">
                <v-card outlined class="pa-4 text-left">
                  <pre class="resume-text">{{ resumeContent }}</pre>
                </v-card>
              </div>
            </div>
          </div>
          
          <div class="text-center mt-8">
            <v-btn 
              color="primary" 
              x-large 
              @click="goToNextStep"
              height="50"
              min-width="220"
            >
              <v-icon left>mdi-check</v-icon>
              满意，下一步
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
    
    <!-- 加载推荐职位的加载遮罩 -->
    <v-dialog
      v-model="isLoadingJobs"
      persistent
      max-width="350"
      content-class="loading-dialog"
    >
      <v-card color="primary" dark>
        <v-card-text class="text-center py-5">
          <v-progress-circular
            indeterminate
            size="70"
            width="5"
            color="white"
            class="mb-3"
          ></v-progress-circular>
          <div class="text-h6 white--text">正在获取推荐职位...</div>
          <div v-if="retryCount > 0" class="subtitle-1 amber--text mt-1">
            已等待 {{ retryCount }} 次检查
          </div>
          <div class="text-subtitle-2 grey--text text--lighten-1 mt-2">
            请耐心等待工作流处理完成，这可能需要一些时间
          </div>
        </v-card-text>
        <v-card-actions class="justify-center pb-5">
          <v-btn
            color="white"
            text
            @click="cancelLoading"
          >
            <v-icon left small>mdi-close</v-icon>
            取消并跳过
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- 页面标题 -->
    <div class="page-title">
      <div class="d-flex align-center">
        <v-icon size="28" color="white" class="mr-3">mdi-file-document-edit-outline</v-icon>
        <v-chip color="primary" small outlined class="white--text">第一步</v-chip>
      </div>
    </div>
    
    <!-- 分隔线 -->
    <div class="split-line"></div>
    
    <!-- 删除初始选择提示 -->
  </div>
</template>

<script>
import { parseTime } from '@/utils/utils'
import AnimatedPopup from '@/components/common/AnimatedPopup.vue'
import ResumeUploader from '@/components/common/ResumeUploader.vue'
import AiResumeGenerator from '@/components/common/AiResumeGenerator.vue'

export default {
  name: 'ResumePreparation',
  components: {
    AnimatedPopup,
    ResumeUploader,
    AiResumeGenerator
  },
  data() {
    return {
      activeArea: null,
      showPreview: false,
      hasInteracted: false,
      hasResume: false,
      resumeFile: null,
      resumeData: null,
      isLoadingJobs: false, // 加载推荐职位的状态变量
      retryCount: 0, // 重试次数计数器
      extractedSkills: [], // 存储提取的技能列表
    }
  },
  computed: {
    userId() {
      return this.$store.state.user.userId
    },
    isResumeLink() {
      return this.resumeData && this.resumeData.generatedContent && this.resumeData.generatedContent.startsWith('http');
    },
    resumeContent() {
      return this.resumeData ? this.resumeData.generatedContent : null;
    },
    resumePreviewImage() {
      return this.resumeData && this.resumeData.preview ? this.resumeData.preview : null;
    },
    hasMultipleTemplates() {
      return this.resumeData && this.resumeData.allLinks && this.resumeData.allLinks.length > 0;
    }
  },
  methods: {
    onMouseEnter(area) {
      // 移除鼠标移入选择功能
    },
    
    setActiveArea(area) {
      if (this.activeArea === area) return
      
      // 触发进入动画
      this.activeArea = area
      this.hasInteracted = true
    },
    
    // 新增：获取推荐职位方法
    async getRecommendedJobs(skills, education, experience) {
      this.isLoadingJobs = true;
      this.retryCount = 0; // 重置检查计数器
      
      // 初始化轮询设置
      let pollInterval = 3000; // 初始轮询间隔3秒
      let maxPollInterval = 10000; // 最大轮询间隔10秒
      let pollTimer = null;
      let requestId = null; // 用于存储工作流ID
      
      try {
        // 显示加载消息
        this.$store.dispatch('snackbar/showMessage', {
          message: '正在启动简历分析，请稍候...',
          color: 'info'
        });
        
        // 准备请求参数
        const params = {
          skills: Array.isArray(skills) ? skills : [],
          education: education || '',
          experience: experience || ''
        };
        
        console.log('提交推荐职位请求参数:', params);
        
        // 发送一次请求启动工作流
        const response = await this.$axios.post('/api/resume/recommend_jobs', params, {
          timeout: 60000, // 60秒超时
        });
        
        // 保存初始响应数据到localStorage
        if (response && response.data) {
          try {
            localStorage.setItem('jobRecommendationWorkflow', JSON.stringify(response.data));
            console.log('已保存职位推荐工作流初始数据:', response.data);
          } catch (e) {
            console.error('保存职位推荐工作流数据失败:', e);
          }
        }
        
        // 检查初始响应
        if (response.data) {
          // 如果直接返回成功结果
          if (response.data.code === 0) {
            console.log('获取推荐职位成功(直接返回):', response.data);
            this.handleSuccessResult(response.data, params.skills);
            return true;
          } 
          // 如果返回请求ID，需要轮询检查
          else if (response.data.request_id || response.data.task_id) {
            requestId = response.data.request_id || response.data.task_id;
            console.log(`工作流已提交，请求ID: ${requestId}，开始轮询检查状态`);
            
            // 开始轮询检查
            return await this.pollJobRecommendationStatus(requestId, params.skills, pollInterval, maxPollInterval);
          }
          // 如果直接返回错误
          else {
            const errorMsg = response.data.message || '获取推荐职位失败';
            console.error('获取推荐职位失败:', errorMsg);
            
            this.$store.dispatch('snackbar/showMessage', {
              message: errorMsg,
              color: 'error'
            });
            
            // 结束加载
            this.isLoadingJobs = false;
            return false;
          }
        } else {
          throw new Error('服务器未返回有效响应');
        }
      } catch (error) {
        console.error('获取推荐职位出错:', error);
        
        this.$store.dispatch('snackbar/showMessage', {
          message: '获取推荐职位失败: ' + (error.message || '未知错误'),
          color: 'error'
        });
        
        this.isLoadingJobs = false;
        return false;
      }
    },
    
    // 轮询检查工作流状态
    async pollJobRecommendationStatus(requestId, skills, pollInterval, maxPollInterval) {
      if (!requestId) {
        console.error('没有请求ID，无法轮询');
        
        // 即使没有请求ID，也尝试获取默认推荐
        console.log('尝试获取默认推荐职位');
        this.$store.dispatch('snackbar/showMessage', {
          message: '无法获取推荐职位ID，使用默认推荐',
          color: 'warning'
        });
        
        // 保存技能到本地存储（即使为空）
        if (Array.isArray(skills)) {
          localStorage.setItem('extractedSkills', JSON.stringify(skills));
        }
        
        this.isLoadingJobs = false;
        this.$router.push('/job/list');
        return false;
      }
      
      // 轮询函数
      const checkStatus = () => {
        return new Promise(resolve => {
          const poll = async () => {
            this.retryCount++; // 增加检查计数
            
            try {
              console.log(`正在检查工作流状态，第 ${this.retryCount} 次检查，请求ID: ${requestId}`);
              
              // 更新加载提示
              this.$store.dispatch('snackbar/showMessage', {
                message: `正在等待职位推荐结果，请耐心等待...`,
                color: 'info'
              });
              
              // 发送状态检查请求
              const statusResponse = await this.$axios.get('/api/resume/check_recommendation', {
                params: { request_id: requestId },
                timeout: 10000
              });
              
              console.log('状态检查响应:', statusResponse.data);
              
              // 检查状态响应
              if (statusResponse.data) {
                // 如果工作流已完成
                if (
                  (statusResponse.data.code === 0 && statusResponse.data.data && statusResponse.data.data.status === 'completed') ||
                  // 兼容可能直接返回结果的情况
                  (statusResponse.data.code === 0 && statusResponse.data.data && statusResponse.data.data.jobs)
                ) {
                  console.log('工作流已完成，获取结果:', statusResponse.data);
                  
                  // 保存最终的工作流结果数据到localStorage
                  try {
                    localStorage.setItem('jobRecommendationResult', JSON.stringify(statusResponse.data));
                    console.log('已保存职位推荐最终结果数据:', statusResponse.data);
                  } catch (e) {
                    console.error('保存职位推荐结果数据失败:', e);
                  }
                  
                  // 处理成功结果
                  this.handleSuccessResult(statusResponse.data, skills);
                  resolve(true);
                  return;
                }
                // 如果工作流正在进行中
                else if (statusResponse.data.data && (
                  statusResponse.data.data.status === 'processing' || 
                  statusResponse.data.data.status === 'pending' ||
                  statusResponse.data.data.status === 'running'
                )) {
                  console.log(`工作流正在处理中 (${statusResponse.data.data.status})，继续等待...`);
                  
                  // 增加轮询间隔（但不超过最大值）
                  pollInterval = Math.min(pollInterval * 1.2, maxPollInterval);
                  
                  // 继续轮询
                  setTimeout(poll, pollInterval);
                }
                // 如果工作流失败
                else if (statusResponse.data.data && (
                  statusResponse.data.data.status === 'failed' ||
                  statusResponse.data.data.status === 'error'
                )) {
                  console.error('工作流处理失败:', statusResponse.data.message || '未知错误');
                  
                  this.$store.dispatch('snackbar/showMessage', {
                    message: `推荐职位生成失败: ${statusResponse.data.message || '未知错误'}`,
                    color: 'error'
                  });
                  
                  // 保存技能到本地存储（即使工作流失败）
                  if (Array.isArray(skills)) {
                    localStorage.setItem('extractedSkills', JSON.stringify(skills));
                  }
                  
                  // 尽管失败，仍然跳转到列表页面，可能会显示所有职位
                  this.isLoadingJobs = false;
                  this.$router.push('/job/list');
                  resolve(false);
                }
                // 其他情况继续轮询
                else {
                  console.log(`工作流状态未知或无法识别，继续等待...`, statusResponse.data);
                  setTimeout(poll, pollInterval);
                }
              } else {
                console.error('检查状态时未收到有效响应');
                
                // 继续轮询，不放弃
                setTimeout(poll, pollInterval);
              }
            } catch (error) {
              console.error('检查工作流状态出错:', error);
              
              // 在连续多次出错后考虑跳过
              if (this.retryCount > 10) {
                console.warn('多次检查失败，跳过等待');
                
                // 保存技能到本地存储
                if (Array.isArray(skills)) {
                  localStorage.setItem('extractedSkills', JSON.stringify(skills));
                }
                
                this.$store.dispatch('snackbar/showMessage', {
                  message: '无法获取推荐职位，显示所有职位',
                  color: 'warning'
                });
                
                this.isLoadingJobs = false;
                this.$router.push('/job/list');
                resolve(false);
                return;
              }
              
              // 继续轮询，不放弃
              setTimeout(poll, pollInterval);
            }
          };
          
          // 开始第一次轮询
          poll();
        });
      };
      
      // 开始轮询
      return await checkStatus();
    },
    
    // 处理成功结果
    handleSuccessResult(data, skills) {
      console.log('处理推荐职位结果:', data);
      
      // 如果有技能信息，保存到本地存储
      if (Array.isArray(skills) && skills.length > 0) {
        localStorage.setItem('extractedSkills', JSON.stringify(skills));
        console.log('已保存技能到本地存储:', skills);
      } else {
        console.log('没有技能信息可保存');
        localStorage.setItem('extractedSkills', JSON.stringify([]));
      }
      
      // 根据数据结构的不同，提取职位信息
      let jobsCount = 0;
      let jobsData = null;
      
      if (data.data) {
        // 尝试从不同可能的数据结构中提取职位
        if (data.data.jobs && Array.isArray(data.data.jobs)) {
          jobsData = data.data.jobs;
          jobsCount = jobsData.length;
        } else if (data.data.list && Array.isArray(data.data.list)) {
          jobsData = data.data.list;
          jobsCount = jobsData.length;
        } else if (data.data.count !== undefined) {
          jobsCount = data.data.count;
        }
        
        // 如果有职位数据，可以存储到本地
        if (jobsData) {
          console.log(`提取到${jobsCount}个推荐职位数据:`, jobsData);
          // 可以存储推荐的职位信息供职位列表页面使用
          // localStorage.setItem('recommendedJobs', JSON.stringify(jobsData));
        }
      }
      
      // 显示成功消息
      if (jobsCount > 0) {
        this.$store.dispatch('snackbar/showMessage', {
          message: `已获取${jobsCount}个推荐职位，即将跳转`,
          color: 'success'
        });
      } else {
        console.log('未找到推荐职位或无法确定职位数量');
        
        // 显示提示信息，仍然跳转
        this.$store.dispatch('snackbar/showMessage', {
          message: '未找到推荐职位，显示全部职位',
          color: 'info'
        });
      }
      
      // 重置计数并关闭加载状态
      this.retryCount = 0;
      this.isLoadingJobs = false;
      
      // 跳转到职位列表页面
      this.$router.push('/job/list');
    },
    
    onUploadSuccess(file) {
      this.resumeFile = file;
      this.hasResume = true;

      // 保存原始上传结果数据到localStorage，合并现有数据
      try {
        // 获取现有的resumeUploadData
        let resumeUploadData = {};
        const existingData = localStorage.getItem('resumeUploadData');
        if (existingData) {
          try {
            resumeUploadData = JSON.parse(existingData);
          } catch (e) {
            console.warn('解析现有resumeUploadData失败，创建新的:', e);
          }
        }

        // 合并上传信息，保留可能已存在的extractedText等字段
        resumeUploadData = {
          ...resumeUploadData,  // 保留现有数据（如extractedText）
          ...file,              // 添加新的上传信息
          uploadTime: new Date().toISOString()  // 添加上传时间戳
        };

        localStorage.setItem('resumeUploadData', JSON.stringify(resumeUploadData));
        console.log('已保存简历上传数据到本地存储:', resumeUploadData);
      } catch (e) {
        console.error('保存上传数据到localStorage失败:', e);
      }
      
      // 检查上传结果是否包含所需的解析数据
      if (file && file.result && (file.result.skills || file.result.education || file.result.work_experience)) {
        console.log('简历上传并解析成功，包含有效的技能/教育/经验数据');
        this.$store.dispatch('snackbar/showMessage', {
          content: '简历上传成功并完成解析！',
          color: 'success'
        })
      } else {
        console.warn('简历上传成功，但没有提取到完整的解析数据');
        this.$store.dispatch('snackbar/showMessage', {
          content: '简历已上传，但未能提取详细信息，可能影响职位推荐',
          color: 'warning'
        })
      }
      
      // 不再自动切换到AI生成简历区域，因为我们将直接跳转到职业选择界面
    },
    
    // 处理continue事件，等待技能提取完成后再跳转到职业选择界面
    async goToJobSelection(uploadResult) {
      console.log('继续到职位选择页面，上传结果:', uploadResult);
      console.log('上传结果完整结构:', JSON.stringify(uploadResult, null, 2));
      
      // 保存上传结果
      this.uploadResult = uploadResult;
      this.hasResume = true;
      
      // 显示等待提示
      this.$store.dispatch('snackbar/showMessage', {
        content: '正在提取简历技能，请稍候...',
        color: 'info'
      });
      
      // 设置加载状态
      this.loading = true;
      
      // 提取简历中的技能、教育和经验信息
      let skills = [];
      let education = '';
      let experience = '';
      
      // 轮询等待技能提取完成的函数
      const waitForSkillsExtraction = async () => {
        // 最大尝试次数和间隔
        const maxAttempts = 10;
        const interval = 1000; // 1秒
        let attempts = 0;
        
        return new Promise((resolve) => {
          const checkSkills = async () => {
            attempts++;
            console.log(`第${attempts}次尝试提取技能...`);
            
            // 尝试从不同位置提取技能信息
            if (uploadResult && uploadResult.result) {
              console.log('上传结果中包含简历解析结果:', uploadResult.result);
              
              if (uploadResult.result.skills && uploadResult.result.skills.length > 0) {
                skills = uploadResult.result.skills;
                this.extractedSkills = [...skills]; // 保存到组件状态
                console.log('成功从result.skills提取技能:', skills);
              } else if (uploadResult.result.entities && uploadResult.result.entities.skills) {
                // 尝试从 entities 结构中提取
                skills = uploadResult.result.entities.skills;
                this.extractedSkills = [...skills];
                console.log('成功从result.entities.skills提取技能:', skills);
              } else if (uploadResult.content && typeof uploadResult.content === 'string') {
                // 尝试解析content字段
                try {
                  const parsedContent = JSON.parse(uploadResult.content);
                  if (parsedContent.skills && Array.isArray(parsedContent.skills)) {
                    skills = parsedContent.skills;
                    this.extractedSkills = [...skills];
                    console.log('成功从content解析提取技能:', skills);
                  } else if (parsedContent.entities && parsedContent.entities.skills) {
                    skills = parsedContent.entities.skills;
                    this.extractedSkills = [...skills];
                    console.log('成功从content.entities解析提取技能:', skills);
                  }
                } catch (e) {
                  console.warn('无法解析content字段:', e);
                }
              } else {
                console.log('未从上传结果中提取到技能信息');
              }
              
              // 提取教育和经验信息类似...
              if (uploadResult.result.education) {
                education = Array.isArray(uploadResult.result.education) 
                  ? uploadResult.result.education.join(', ')
                  : uploadResult.result.education;
                console.log('提取的教育信息:', education);
              }
              
              if (uploadResult.result.work_experience) {
                experience = Array.isArray(uploadResult.result.work_experience)
                  ? uploadResult.result.work_experience.join(', ')
                  : uploadResult.result.work_experience;
                console.log('提取的工作经验:', experience);
              }
            } else if (uploadResult && uploadResult.content) {
              // 如果没有result，尝试从content字段解析
              console.log('尝试从content字段解析数据:', uploadResult.content);
              try {
                const parsedContent = JSON.parse(uploadResult.content);
                console.log('解析后的content数据:', parsedContent);
                
                if (parsedContent.skills && Array.isArray(parsedContent.skills)) {
                  skills = parsedContent.skills;
                  this.extractedSkills = [...skills];
                  console.log('成功从content提取技能:', skills);
                } else if (parsedContent.entities && parsedContent.entities.skills) {
                  skills = parsedContent.entities.skills;
                  this.extractedSkills = [...skills];
                  console.log('成功从content.entities提取技能:', skills);
                }
              } catch (e) {
                console.warn('无法解析content字段:', e);
              }
            }
            
            // 不再从原始工作流内容中提取技能
            // 原代码已移除
            
            // 如果仍然没有提取到技能，但日志显示有17个技能，尝试手动解析
            if (!skills.length && uploadResult) {
              console.log('尝试从完整的uploadResult对象中查找技能数据');
              // 遍历对象所有键
              Object.keys(uploadResult).forEach(key => {
                const value = uploadResult[key];
                if (Array.isArray(value) && value.length > 0) {
                  console.log(`检查数组字段 ${key}:`, value);
                  if (key.toLowerCase().includes('skill') || (value.length === 17)) {
                    skills = value;
                    this.extractedSkills = [...skills];
                    console.log(`从字段 ${key} 推断为技能数组:`, skills);
                  }
                } else if (value && typeof value === 'object') {
                  console.log(`检查对象字段 ${key}`);
                }
              });
            }
            
            // 如果已经提取到技能或者达到最大尝试次数，则完成
            if (skills.length > 0 || attempts >= maxAttempts) {
              // 保存技能到本地存储
              localStorage.setItem('extractedSkills', JSON.stringify(skills));
              console.log('已保存技能到本地存储:', skills);
              resolve(skills);
            } else {
              // 否则继续尝试
              setTimeout(checkSkills, interval);
            }
          };
          
          // 开始第一次检查
          checkSkills();
        });
      };
      
      // 首先检查localStorage中是否已有技能数据
      let extractedSkills = [];
      try {
        const storedSkills = localStorage.getItem('extractedSkills');
        if (storedSkills) {
          extractedSkills = JSON.parse(storedSkills);
          console.log('从localStorage读取到技能数据:', extractedSkills);
        }
      } catch (e) {
        console.error('读取localStorage技能数据失败:', e);
      }

      // 如果localStorage中没有技能数据，则等待技能提取完成
      if (extractedSkills.length === 0) {
        console.log('localStorage中没有技能数据，等待技能提取...');
        extractedSkills = await waitForSkillsExtraction();
      } else {
        console.log('使用localStorage中的技能数据，跳过等待');
      }

      this.loading = false;
      
      // 显示提示信息
      if (extractedSkills.length > 0) {
        this.$store.dispatch('snackbar/showMessage', {
          content: `成功提取${extractedSkills.length}项技能，即将推荐相关职位`,
          color: 'success'
        });
      } else {
        this.$store.dispatch('snackbar/showMessage', {
          content: '未提取到技能信息，将显示所有职位',
          color: 'info'
        });
      }
      
      // 跳转到职位列表页面
      this.$router.push('/job/list');
    },
    
    onGenerationComplete(data) {
      this.resumeData = data
      this.hasResume = true
      
      console.log('简历生成完成，数据:', data);
      
      // 保存AI简历生成的完整数据到localStorage
      try {
        localStorage.setItem('aiGeneratedResumeData', JSON.stringify(data));
        console.log('已保存AI生成的简历数据到本地存储');
      } catch (e) {
        console.error('保存AI生成的简历数据失败:', e);
      }
      
      this.$store.dispatch('snackbar/showMessage', {
        content: 'AI简历生成成功！',
        color: 'success'
      })
    },
    
    formatDate(date) {
      return parseTime(date, '{y}-{m}-{d}')
    },
    
    editResume() {
      // 编辑简历逻辑
      this.$store.dispatch('snackbar/showMessage', {
        content: '简历编辑功能正在开发中',
        color: 'info'
      })
    },
    
    downloadResume() {
      // 下载简历逻辑
      this.$store.dispatch('snackbar/showMessage', {
        content: '简历下载功能正在开发中',
        color: 'info'
      })
    },
    
    goToNextStep() {
      // 显示加载状态
      this.$store.dispatch('snackbar/showMessage', {
        message: '正在处理简历...',
        color: 'info'
      })
      
      // 调用API处理简历
      this.processResumeDoc()
        .then(response => {
          if (response.data && response.data.code === 0) {
            // 处理成功
            this.$store.dispatch('snackbar/showMessage', {
              message: '简历处理成功！',
              color: 'success'
            })
            
            // 提取实体信息
            let skills = [];
            let education = '';
            let experience = '';
            
            // 保存实体信息到store（如果有store的话）
            if (response.data.data && response.data.data.entities) {
              console.log('提取的实体信息:', response.data.data.entities)
              
              // 从实体中提取技能、教育和经验信息
              if (response.data.data.entities.skills) {
                skills = response.data.data.entities.skills;
                this.extractedSkills = [...skills]; // 保存到组件状态
                console.log('成功提取技能:', skills);
              } else {
                console.log('未提取到技能信息');
              }
              
              if (response.data.data.entities.education) {
                education = Array.isArray(response.data.data.entities.education) 
                  ? response.data.data.entities.education.join(', ')
                  : response.data.data.entities.education;
                console.log('提取的教育信息:', education);
              }
              
              if (response.data.data.entities.experience) {
                experience = Array.isArray(response.data.data.entities.experience)
                  ? response.data.data.entities.experience.join(', ')
                  : response.data.data.entities.experience;
                console.log('提取的工作经验:', experience);
              }
            } else {
              console.warn('响应中没有实体信息');
            }
            
            // 保存技能到本地存储
            localStorage.setItem('extractedSkills', JSON.stringify(skills));
            console.log('已保存技能到本地存储，准备跳转:', skills);
            
            // 显示提示信息
            if (skills.length > 0) {
              this.$store.dispatch('snackbar/showMessage', {
                content: `已提取${skills.length}项技能，即将推荐相关职位`,
                color: 'success'
              });
            } else {
              this.$store.dispatch('snackbar/showMessage', {
                content: '未提取到技能信息，将显示所有职位',
                color: 'info'
              });
            }
            
            // 关闭预览
            this.showPreview = false
            
            // 直接跳转到职位列表页面，让JobList.vue负责获取推荐职位
            this.$router.push('/job/list');
          } else {
            // 处理失败
            this.$store.dispatch('snackbar/showMessage', {
              content: response.data ? response.data.message : '简历处理失败',
              color: 'error'
            })
          }
        })
        .catch(error => {
          // 处理错误
          this.$store.dispatch('snackbar/showMessage', {
            content: '简历处理失败: ' + (error.message || '未知错误'),
            color: 'error'
          })
        })
    },
    
    processResumeDoc() {
      // 导入API函数
      const { processResumeWorkflow } = require('@/api/resume')

      // 优先使用文本内容，如果没有则使用链接
      let textContent = '';
      let resumeUrl = '';

      // 检查是否有文本内容
      if (this.resumeData && this.resumeData.textContent) {
        textContent = this.resumeData.textContent;
        console.log('使用简历文本内容，长度:', textContent.length);
      } else if (this.resumeData && this.resumeData.entities) {
        // 从实体信息构造文本
        textContent = this.constructTextFromEntities(this.resumeData.entities);
        console.log('从实体信息构造文本，长度:', textContent.length);
      }

      // 如果有文本内容，使用文本模式
      if (textContent && textContent.length > 50) {
        console.log('使用文本内容调用工作流API');
        return processResumeWorkflow(textContent, true).then(response => {
          // 保存原始工作流内容到localStorage
          if (response && response.data) {
            try {
              // 提取和保存原始content内容
              let originalContent = null;
              if (response.data.data && response.data.data.originalWorkflowContent) {
                originalContent = response.data.data.originalWorkflowContent;
              } else if (response.data.data && response.data.data.content) {
                originalContent = response.data.data.content;
              } else if (response.data.data) {
                originalContent = response.data.data;
              }

              if (originalContent) {
                localStorage.setItem('originalWorkflowContent', JSON.stringify(originalContent));
                console.log('已保存原始工作流内容到localStorage');
              }
            } catch (e) {
              console.error('保存原始工作流内容失败:', e);
            }
          }
          return response;
        });
      } else {
        // 否则使用链接模式
        if (this.resumeData && this.resumeData.generatedContent && this.resumeData.generatedContent.startsWith('http')) {
          resumeUrl = this.resumeData.generatedContent;
        } else if (this.resumeData && this.resumeData.downloadLink) {
          resumeUrl = this.resumeData.downloadLink;
        }

        console.log('使用简历链接调用工作流API:', resumeUrl);
        return processResumeWorkflow(resumeUrl, false).then(response => {
          // 保存原始工作流内容到localStorage
          if (response && response.data) {
            try {
              // 提取和保存原始content内容
              let originalContent = null;
              if (response.data.data && response.data.data.originalWorkflowContent) {
                originalContent = response.data.data.originalWorkflowContent;
              } else if (response.data.data && response.data.data.content) {
                originalContent = response.data.data.content;
              } else if (response.data.data) {
                originalContent = response.data.data;
              }

              if (originalContent) {
                localStorage.setItem('originalWorkflowContent', JSON.stringify(originalContent));
                console.log('已保存原始工作流内容到localStorage');
              }
            } catch (e) {
              console.error('保存原始工作流内容失败:', e);
            }
          }
          return response;
        });
      }
    },

    // 从实体信息构造文本内容
    constructTextFromEntities(entities) {
      try {
        let text = '';

        // 添加基本信息
        if (entities.name && entities.name.length > 0) {
          text += `姓名：${entities.name.join('、')} `;
        }

        if (entities.education && entities.education.length > 0) {
          text += `教育背景：${entities.education.join('、')} `;
        }

        if (entities.major && entities.major.length > 0) {
          text += `专业：${entities.major.join('、')} `;
        }

        if (entities.organization && entities.organization.length > 0) {
          text += `工作单位：${entities.organization.join('、')} `;
        }

        if (entities.title && entities.title.length > 0) {
          text += `职位：${entities.title.join('、')} `;
        }

        if (entities.skills && entities.skills.length > 0) {
          text += `技能：${entities.skills.join('、')} `;
        }

        console.log('从实体信息构造的文本:', text);
        return text.trim();
      } catch (e) {
        console.error('从实体信息构造文本失败:', e);
        return '';
      }
    },

    cancelLoading() {
      this.isLoadingJobs = false;
      this.retryCount = 0; // 重置重试次数
      
      // 确保保存已提取的技能（如果有的话）
      if (this.extractedSkills && this.extractedSkills.length > 0) {
        localStorage.setItem('extractedSkills', JSON.stringify(this.extractedSkills));
        console.log('取消加载时保存已提取技能:', this.extractedSkills);
      } else {
        localStorage.setItem('extractedSkills', JSON.stringify([]));
        console.log('取消加载时未检测到已提取技能，保存空数组');
      }
      
      this.$store.dispatch('snackbar/showMessage', {
        message: '已取消加载推荐职位，跳过此步骤。',
        color: 'info'
      });
      this.$router.push('/job/list'); // 跳转到职位列表页面
    }
  },
  mounted() {
    // 初始化状态，不设置默认活动区域，保持两侧各占一半
    this.hasInteracted = false
    this.activeArea = null
    
    // 移除鼠标移动事件监听
    
    // 组件销毁时移除事件监听
    this.$once('hook:beforeDestroy', () => {
      document.body.style.cursor = ''
    })
  }
}
</script>

<style scoped>
.split-screen-container {
  position: relative;
  width: 100%;
  height: 100vh; /* 使用视口高度单位，确保填满整个视口 */
  display: flex;
  overflow: hidden;
  margin: 0;
  padding: 0;
  position: fixed; /* 固定位置，防止滚动 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 新增：加载对话框样式 */
.loading-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.loading-dialog :deep(.v-card) {
  border-radius: 16px;
}

/* 分屏两侧共同样式 */
.split-side {
  position: relative;
  height: 100%;
  transition: all 0.8s cubic-bezier(0.65, 0, 0.35, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 白色区域样式 */
.white-side {
  background-color: #ffffff;
  width: 50%;
  box-shadow: 5px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

/* 黑色区域样式 */
.black-side {
  background-color: #212121;
  width: 50%;
  z-index: 1;
}

/* 活动状态样式 - 只有在activeArea不为null时才应用 */
.split-side.active {
  width: 70%;
  cursor: default;
}

.split-side.inactive {
  width: 30%;
  cursor: pointer;
}

/* 内容样式 */
.side-content {
  width: 100%;
  max-width: 900px;
  padding: 0 40px;
  position: relative;
  transition: all 0.5s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow-y: auto; /* 允许内容在需要时垂直滚动 */
  overflow-x: hidden; /* 防止水平滚动 */
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

/* 隐藏滚动条但保留功能 */
.side-content::-webkit-scrollbar {
  display: none;
}

.side-icon {
  text-align: center;
  transition: all 0.8s cubic-bezier(0.68, -0.6, 0.32, 1.6);
  transform: translateY(0);
}

.side-icon.minimized {
  transform: translateY(-40vh);
  opacity: 0.2;
}

.inactive .side-icon {
  transform: scale(0.8);
}

/* 分隔线 */
.split-line {
  position: absolute;
  left: 50%;
  top: 0;
  height: 100%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  z-index: 10;
  transform: translateX(-50%);
  pointer-events: none;
  transition: opacity 0.5s ease;
  opacity: 0; /* 默认隐藏 */
}

.split-screen-container:hover .split-line {
  opacity: 0;
}

/* 弹出框容器 */
.popup-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  max-height: 100vh; /* 限制最大高度 */
  overflow: visible; /* 允许内容溢出 */
}

.upload-popup, .ai-popup {
  width: 100%;
  max-width: 700px;
}

.ai-popup {
  overflow: hidden;
  border-radius: 0;
}

/* 页面标题 */
.page-title {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 10;
}

/* 简历预览弹窗 */
.resume-preview-card {
  border-radius: 12px;
  overflow: hidden;
}

.resume-preview-container {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 16px;
}

.resume-preview-image {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.resume-preview-image-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* 响应式调整 */
@media (max-width: 960px) {
  .split-screen-container {
    flex-direction: column;
    height: 100vh; /* 保持100vh高度 */
    position: fixed; /* 确保固定位置 */
  }
  
  .split-side {
    width: 100% !important;
    height: 50vh;
  }
  
  .white-side {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  .split-side.active {
    height: 70vh;
  }
  
  .split-side.inactive {
    height: 30vh;
  }
  
  .side-icon.minimized {
    transform: translateY(-20vh);
  }
  
  .side-content {
    padding: 20px;
    overflow-y: auto; /* 确保在移动端也能滚动 */
  }
  
  .page-title {
    background-color: rgba(0, 0, 0, 0.7);
    padding: 10px;
    border-radius: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    text-align: center;
    top: 10px; /* 调整顶部位置 */
  }
  
  .split-line {
    left: 0;
    top: 50%;
    width: 100%;
    height: 1px;
    transform: translateY(-50%);
  }
}

@media (max-width: 600px) {
  .split-side {
    height: 50vh; /* 固定高度 */
    min-height: unset; /* 移除最小高度限制 */
  }
  
  .side-content {
    padding: 16px;
  }
  
  .page-title h1 {
    font-size: 1.5rem;
  }
}

/* 上传成功后的样式 */
.split-side.hidden {
  width: 0 !important;
  opacity: 0;
  overflow: hidden;
}

.split-side.fullscreen {
  width: 100% !important;
}

/* 点击提示样式 */
.click-hint {
  position: absolute;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  animation: pulse 2s infinite;
  z-index: 5;
}

.white-hint {
  color: var(--v-primary-base);
}

.black-hint {
  color: white;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}

/* 简历预览相关样式 */
.resume-text-content {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 4px;
}

.resume-text {
  white-space: pre-wrap;
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

.resume-link {
  word-break: break-all;
  max-width: 100%;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}
</style> 