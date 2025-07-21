<template>
  <div class="ai-resume-generator">
    <div class="generator-content">
      <div class="top-spacing"></div>
      <transition name="slide-fade" mode="out-in">
        <div v-if="generating" key="generating" class="generation-progress">
          <div class="progress-container text-center">
            <v-progress-circular
              indeterminate
              size="86"
              width="6"
              color="white"
              class="mb-4"
            ></v-progress-circular>
            
            <h2 class="text-h4 font-weight-medium white--text mb-4">AI正在生成简历</h2>
            
            <div class="generation-steps">
              <v-stepper 
                v-model="currentStep" 
                vertical 
                non-linear 
                class="generation-stepper"
                dark
              >
                <!-- 第一步 -->
                <v-stepper-step
                  :key="'step-1'"
                  :complete="currentStep > 1"
                  :step="1"
                  color="white"
                >
                  <span class="white--text">{{ generationSteps[0].title }}</span>
                  <small class="white--text">{{ generationSteps[0].subtitle }}</small>
                </v-stepper-step>

                <v-stepper-content
                  :key="'content-1'"
                  :step="1"
                  class="px-0"
                >
                  <div class="white--text text-body-2">{{ generationSteps[0].description }}</div>
                </v-stepper-content>

                <!-- 第二步 -->
                <v-stepper-step
                  :key="'step-2'"
                  :complete="currentStep > 2"
                  :step="2"
                  color="white"
                >
                  <span class="white--text">{{ generationSteps[1].title }}</span>
                  <small class="white--text">{{ generationSteps[1].subtitle }}</small>
                </v-stepper-step>

                <v-stepper-content
                  :key="'content-2'"
                  :step="2"
                  class="px-0"
                >
                  <div class="white--text text-body-2">{{ generationSteps[1].description }}</div>
                </v-stepper-content>

                <!-- 第三步 -->
                <v-stepper-step
                  :key="'step-3'"
                  :complete="currentStep > 3"
                  :step="3"
                  color="white"
                >
                  <span class="white--text">{{ generationSteps[2].title }}</span>
                  <small class="white--text">{{ generationSteps[2].subtitle }}</small>
                </v-stepper-step>

                <v-stepper-content
                  :key="'content-3'"
                  :step="3"
                  class="px-0"
                >
                  <div class="white--text text-body-2">{{ generationSteps[2].description }}</div>
                </v-stepper-content>

                <!-- 第四步 -->
                <v-stepper-step
                  :key="'step-4'"
                  :complete="currentStep > 4"
                  :step="4"
                  color="white"
                >
                  <span class="white--text">{{ generationSteps[3].title }}</span>
                  <small class="white--text">{{ generationSteps[3].subtitle }}</small>
                </v-stepper-step>

                <v-stepper-content
                  :key="'content-4'"
                  :step="4"
                  class="px-0"
                >
                  <div class="white--text text-body-2">{{ generationSteps[3].description }}</div>
                </v-stepper-content>
              </v-stepper>
            </div>
          </div>
        </div>
        
        <div v-else-if="generationComplete" key="complete" class="generation-complete">
          <div class="text-center">
            <v-icon size="86" color="white">mdi-check-circle</v-icon>
            <h2 class="text-h4 font-weight-medium white--text mt-4 mb-6">简历生成完成！</h2>

            <!-- 技能提取进度提示 -->
            <div v-if="processingSkills" class="mt-3 mb-6">
              <v-progress-linear
                indeterminate
                color="primary"
                height="2"
              ></v-progress-linear>
              <p class="text-caption white--text mt-2">
                正在分析生成的简历内容，提取技能信息...
              </p>
            </div>

            <!-- 技能提取完成提示 -->
            <div v-if="skillsExtracted && extractedSkillsCount > 0" class="mt-3 mb-6">
              <v-chip
                color="success"
                text-color="white"
                small
              >
                <v-icon left small>mdi-check</v-icon>
                已提取 {{ extractedSkillsCount }} 项技能
              </v-chip>
            </div>

            <v-btn
              color="primary"
              dark
              x-large
              min-width="200"
              elevation="4"
              @click="previewResume"
              class="preview-btn"
              :loading="processingSkills"
              :disabled="processingSkills"
            >
              <v-icon left v-if="!processingSkills">mdi-eye</v-icon>
              <v-icon left v-if="processingSkills">mdi-brain</v-icon>
              {{ processingSkills ? '正在分析...' : '预览简历' }}
            </v-btn>
          </div>
        </div>
        
        <div v-else key="form" class="generation-form">
          
          <v-form ref="form" v-model="formValid" @submit.prevent="startGeneration">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.name"
                  label="姓名"
                  outlined
                  dark
                  color="white"
                  :rules="nameRules"
                  prepend-inner-icon="mdi-account"
                  class="input-field white--text"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.education"
                  :items="educationLevels"
                  label="最高学历"
                  outlined
                  dark
                  color="white"
                  :rules="requiredRules"
                  prepend-inner-icon="mdi-school"
                  class="input-field white--text"
                  dense
                  menu-props="auto, offsetY"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-combobox
                  v-model="formData.skills"
                  :items="skillOptions"
                  label="技能标签"
                  outlined
                  dark
                  color="white"
                  chips
                  multiple
                  small-chips
                  :rules="skillsRules"
                  prepend-inner-icon="mdi-lightning-bolt"
                  class="input-field white--text"
                  dense
                  menu-props="auto, offsetY"
                ></v-combobox>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="formData.experience"
                  label="工作经历(简要描述)"
                  outlined
                  dark
                  color="white"
                  auto-grow
                  rows="4"
                  :rules="requiredRules"
                  prepend-inner-icon="mdi-briefcase"
                  class="input-field white--text"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" class="text-center">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      color="primary darken-1"
                      dark
                      x-large
                      width="220"
                      height="54"
                      elevation="4"
                      type="submit"
                      :disabled="!formValid"
                      v-bind="attrs"
                      v-on="on"
                      class="generate-btn"
                    >
                      <v-icon left>mdi-robot</v-icon>
                      生成简历
                    </v-btn>
                  </template>
                  <span>AI将根据您的信息生成专业简历</span>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-form>
          
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { generateResume, processResumeWithStar } from '@/api/resume'

export default {
  name: 'AiResumeGenerator',
  data() {
    return {
      formValid: false,
      generating: false,
      generationComplete: false,
      currentStep: 1,
      stepInterval: null,
      processingSkills: false,  // 是否正在处理技能提取
      skillsExtracted: false,   // 技能是否已提取完成
      extractedSkillsCount: 0,  // 提取的技能数量
      
      formData: {
        name: '',
        education: '',
        skills: [],
        experience: ''
      },
      
      educationLevels: [
        '高中',
        '大专',
        '本科',
        '硕士',
        '博士'
      ],
      
      skillOptions: [
        'Java', 'Python', 'JavaScript', 'C++', 'C#', 'Go', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Docker', 'Kubernetes',
        'AWS', 'Azure', 'Google Cloud', 'Linux', 'Windows', 'MacOS', 'Git', 'GitHub', 'GitLab',
        'RESTful API', 'GraphQL', 'WebSocket', 'Microservices', 'DevOps', 'CI/CD', 'TDD', 'Agile',
        '数据分析', '机器学习', '深度学习', '人工智能', '大数据', '云计算', '网络安全', '区块链',
        'UI设计', 'UX设计', '产品管理', '项目管理', '沟通能力', '团队协作', '问题解决', '创新思维'
      ],
      
      generationSteps: [
        {
          title: '分析个人信息',
          subtitle: '正在处理',
          description: '正在分析您提供的基本信息，确定简历的基本结构...'
        },
        {
          title: '匹配职业技能',
          subtitle: '即将开始',
          description: '根据您的技能标签匹配相关职业能力描述...'
        },
        {
          title: '丰富工作经历',
          subtitle: '等待中',
          description: '基于您的经历描述，生成详细的职责和成就...'
        },
        {
          title: '优化简历格式',
          subtitle: '等待中',
          description: '根据行业标准调整简历结构和格式...'
        }
      ],
      
      // 表单验证规则
      nameRules: [
        v => !!v || '姓名不能为空',
        v => (v && v.length <= 20) || '姓名不能超过20个字符'
      ],
      requiredRules: [
        v => !!v || '此字段不能为空'
      ],
      skillsRules: [
        v => v.length > 0 || '请至少添加一个技能标签'
      ]
    }
  },
  methods: {
    startGeneration() {
      if (!this.formValid) {
        this.$refs.form.validate()
        return
      }
      
      this.generating = true
      this.currentStep = 1
      
      // 声明变量存储API请求状态和结果
      let apiResponse = null;
      let apiError = null;
      let apiCompleted = false;
      
      // 立即开始API调用，不等待动画完成
      generateResume(this.formData)
        .then(response => {
          apiResponse = response;
          apiCompleted = true;
          
          // 如果动画已经完成，处理API结果
          if (this.currentStep >= this.generationSteps.length) {
            this.processApiResult(apiResponse);
          }
        })
        .catch(error => {
          apiError = error;
          apiCompleted = true;
          
          // 如果动画已经完成，处理API错误
          if (this.currentStep >= this.generationSteps.length) {
            this.handleGenerationError(apiError.message || '网络错误');
          }
        });
      
      // 创建步骤进度更新定时器
      this.stepInterval = setInterval(() => {
        if (this.currentStep < this.generationSteps.length) {
          this.currentStep++;
          
          // 更新步骤状态
          this.generationSteps[this.currentStep - 2].subtitle = '已完成';
          this.generationSteps[this.currentStep - 1].subtitle = '正在处理';
          
          if (this.currentStep < this.generationSteps.length) {
            this.generationSteps[this.currentStep].subtitle = '即将开始';
          }
        } else {
          // 动画完成
          clearInterval(this.stepInterval);
          this.generationSteps[this.generationSteps.length - 1].subtitle = '已完成';
          
          // 如果API已完成，处理结果
          if (apiCompleted) {
            if (apiError) {
              this.handleGenerationError(apiError.message || '网络错误');
            } else {
              this.processApiResult(apiResponse);
            }
          }
          // 如果API尚未完成，保持加载状态，等待API完成
        }
      }, 2000);
    },
    
    // 错误处理方法
    handleGenerationError(errorMessage) {
      this.generating = false
      clearInterval(this.stepInterval)
      
      // 显示错误信息
      this.$store.dispatch('snackbar/showMessage', {
        message: `简历生成失败: ${errorMessage}`,
        color: 'error'
      })
      
      // 发送错误事件
      this.$emit('generation-error', errorMessage)
    },

    // 处理生成的简历内容（文本提取和技能分析）
    async processGeneratedResume(resumeData) {
      console.log('开始处理生成的简历内容:', resumeData);

      // 如果已经有技能信息，则不需要重新设置处理状态
      if (!resumeData.skills || resumeData.skills.length === 0) {
        // 设置处理状态
        this.processingSkills = true;
        this.skillsExtracted = false;
        this.extractedSkillsCount = 0;
      }

      try {
        let textContent = null;
        let extractedSkills = [];

        // 检查生成的内容类型
        if (resumeData.generatedContent && typeof resumeData.generatedContent === 'string') {
          // 检查是否为URL链接（docx下载链接）
          if (resumeData.generatedContent.startsWith('http') || resumeData.isLink) {
            console.log('检测到文档链接，但后端已处理，跳过重复下载:', resumeData.generatedContent);

            // 如果后端已经返回了实体信息，说明已经提取过文本了
            // 我们可以从实体信息中构造一个简单的文本用于STAR分析
            if (resumeData.entities) {
              textContent = this.constructTextFromEntities(resumeData.entities);
              console.log('从实体信息构造的文本长度:', textContent ? textContent.length : 0);
            } else {
              console.log('没有实体信息，跳过文本处理');
              textContent = null;
            }
          } else {
            // 如果是普通字符串，直接使用
            textContent = resumeData.generatedContent;
            console.log('使用字符串简历内容，长度:', textContent.length);
          }
        } else if (resumeData.generatedContent && typeof resumeData.generatedContent === 'object') {
          // 如果是JSON对象，转换为文本
          textContent = this.extractTextFromResumeJson(resumeData.generatedContent);
          console.log('从JSON简历中提取的文本长度:', textContent ? textContent.length : 0);
        }

        if (textContent && textContent.length > 50) {
          // 检查是否已经有技能信息（从后端返回）
          if (resumeData.skills && resumeData.skills.length > 0) {
            console.log('使用已有的技能信息，跳过技能提取:', resumeData.skills.length);
            extractedSkills = resumeData.skills;
          } else {
            // 需要进行技能提取
            if (resumeData.generatedContent && resumeData.generatedContent.startsWith('http')) {
              // 文档链接情况：尝试从localStorage获取已提取的技能
              try {
                const storedSkills = localStorage.getItem('extractedSkills');
                if (storedSkills) {
                  extractedSkills = JSON.parse(storedSkills);
                  console.log('从localStorage获取到技能:', extractedSkills);
                }
              } catch (e) {
                console.warn('获取存储的技能失败:', e);
              }

              // 如果没有获取到技能，使用文本内容调用技能提取
              if (!extractedSkills || extractedSkills.length === 0) {
                extractedSkills = await this.extractSkillsFromText(textContent);
              }
            } else {
              // 非文档链接情况：需要调用技能提取API
              extractedSkills = await this.extractSkillsFromText(textContent);
            }

            // 更新技能提取状态
            if (extractedSkills && extractedSkills.length > 0) {
              // 保存技能到本地存储
              localStorage.setItem('extractedSkills', JSON.stringify(extractedSkills));

              this.skillsExtracted = true;
              this.extractedSkillsCount = extractedSkills.length;

              // 触发技能更新事件
              window.dispatchEvent(new CustomEvent('skillsUpdated', {
                detail: { skills: extractedSkills }
              }));

              console.log('技能提取完成，数量:', extractedSkills.length);
            }
          }

          // 调用STAR分析（与ResumeUploader.vue相同的逻辑）
          try {
            console.log('开始STAR分析...');
            const starResponse = await processResumeWithStar(textContent);

            if (starResponse.data && starResponse.data.data && starResponse.data.data.starAnalysis) {
              localStorage.setItem('starWorkflowData', JSON.stringify(starResponse.data.data.starAnalysis));
              console.log('已保存STAR分析结果到localStorage');
            }
          } catch (e) {
            console.error('STAR分析失败:', e.message);
          }
        }

        // 完成处理
        this.processingSkills = false;

        // 构建完整的结果数据
        const finalResumeData = {
          ...resumeData,
          skills: extractedSkills,
          textContent: textContent
        };

        // 发送完成事件
        this.$emit('generation-complete', finalResumeData);

        // 显示成功消息
        this.$store.dispatch('snackbar/showMessage', {
          message: '简历生成和分析完成！',
          color: 'success'
        });

      } catch (error) {
        console.error('处理生成的简历失败:', error);
        this.processingSkills = false;

        // 即使处理失败，也发送基本的完成事件
        this.$emit('generation-complete', resumeData);

        this.$store.dispatch('snackbar/showMessage', {
          message: '简历生成成功，但后续分析失败',
          color: 'warning'
        });
      }
    },

    // 从文档URL提取文本内容
    async extractTextFromDocumentUrl(documentUrl) {
      try {
        console.log('开始从文档URL提取文本:', documentUrl);

        // 首先下载文档
        const response = await this.$axios.get(documentUrl, {
          responseType: 'blob',
          timeout: 60000
        });

        console.log('文档下载成功，大小:', response.data.size);

        // 创建FormData，模拟文件上传
        const formData = new FormData();

        // 根据URL判断文件类型
        let fileName = 'generated_resume.docx';
        if (documentUrl.includes('.pdf')) {
          fileName = 'generated_resume.pdf';
        } else if (documentUrl.includes('.doc')) {
          fileName = 'generated_resume.doc';
        }

        formData.append('file', response.data, fileName);
        formData.append('extract_text', 'true');

        // 调用文本提取API
        const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';
        console.log('调用文本提取API:', `${baseURL}/extract_text`);

        const textResponse = await this.$axios.post(
          `${baseURL}/extract_text`,
          formData,
          {
            timeout: 60000,
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );

        console.log('文本提取API响应:', textResponse.data);

        if (textResponse.data && textResponse.data.success && textResponse.data.data) {
          const extractedText = textResponse.data.data.text;

          // 如果API返回了技能信息，保存到localStorage
          if (textResponse.data.data.skills && textResponse.data.data.skills.length > 0) {
            localStorage.setItem('extractedSkills', JSON.stringify(textResponse.data.data.skills));
            console.log('从文档提取API获取到技能:', textResponse.data.data.skills);
          }

          console.log('成功提取文本，长度:', extractedText ? extractedText.length : 0);
          return extractedText;
        } else {
          console.warn('文本提取API返回异常:', textResponse.data);
          return null;
        }

      } catch (error) {
        console.error('从文档URL提取文本失败:', error);
        return null;
      }
    },

    // 从文本内容提取技能
    async extractSkillsFromText(textContent) {
      try {
        console.log('开始从文本提取技能，文本长度:', textContent.length);

        const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';

        // 创建FormData，模拟文件上传的格式
        const formData = new FormData();
        const textBlob = new Blob([textContent], { type: 'text/plain' });
        formData.append('file', textBlob, 'generated_resume.txt');
        formData.append('extract_text', 'true');

        const textResponse = await this.$axios.post(
          `${baseURL}/extract_text`,
          formData,
          { timeout: 30000 }
        );

        console.log('技能提取API响应:', textResponse.data);

        if (textResponse.data && textResponse.data.success && textResponse.data.data) {
          if (textResponse.data.data.skills && textResponse.data.data.skills.length > 0) {
            console.log('成功提取技能:', textResponse.data.data.skills);
            return textResponse.data.data.skills;
          }
        }

        return [];
      } catch (e) {
        console.error('技能提取失败:', e.message);
        return [];
      }
    },

    // 从实体信息构造文本内容用于STAR分析
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

        // 添加用户输入的表单数据
        text += `工作经历：${this.formData.experience || ''} `;

        console.log('从实体信息构造的文本:', text);
        return text.trim();
      } catch (e) {
        console.error('从实体信息构造文本失败:', e);
        return '';
      }
    },

    // 从JSON格式的简历中提取文本内容
    extractTextFromResumeJson(resumeJson) {
      try {
        let text = '';

        // 递归提取JSON中的所有文本内容
        const extractText = (obj) => {
          if (typeof obj === 'string') {
            text += obj + ' ';
          } else if (typeof obj === 'object' && obj !== null) {
            if (Array.isArray(obj)) {
              obj.forEach(item => extractText(item));
            } else {
              Object.values(obj).forEach(value => extractText(value));
            }
          }
        };

        extractText(resumeJson);
        return text.trim();
      } catch (e) {
        console.error('从JSON提取文本失败:', e);
        return '';
      }
    },

    previewResume() {
      this.$emit('preview-resume')
    },
    
    resetForm() {
      this.generating = false
      this.generationComplete = false
      this.processingSkills = false
      this.skillsExtracted = false
      this.extractedSkillsCount = 0
      this.$refs.form.reset()

      // 重置步骤状态
      this.generationSteps.forEach((step, index) => {
        if (index === 0) {
          step.subtitle = '正在处理'
        } else if (index === 1) {
          step.subtitle = '即将开始'
        } else {
          step.subtitle = '等待中'
        }
      })
    },

    // 新增方法，处理API返回结果
    processApiResult(response) {
      if (response.data && response.data.code === 0) {
        this.generating = false;
        this.generationComplete = true;

        // 打印API返回数据，用于调试
        console.log('API返回数据:', response.data);

        // 检查是否有简历内容
        if (response.data.data && response.data.data.resume) {
          const resumeJson = response.data.data.resume;
          const entities = response.data.data.entities; // 获取后端返回的实体识别结果

          // 检查是否有links数组，提取第一个链接作为主要下载链接
          let mainDownloadLink = null;
          let allLinks = [];

          if (resumeJson.links && Array.isArray(resumeJson.links) && resumeJson.links.length > 0) {
            const firstLink = resumeJson.links[0];
            if (firstLink.word_url) {
              mainDownloadLink = firstLink.word_url;
            }
            allLinks = resumeJson.links;
          }

          // 发送完成事件，包含生成的简历内容
          const resumeData = {
            ...this.formData,
            generatedContent: mainDownloadLink || resumeJson, // 使用主要下载链接或原始JSON
            isLink: !!mainDownloadLink, // 如果有下载链接则标记为链接
            downloadLink: mainDownloadLink,
            allLinks: allLinks,
            resumeJson: resumeJson, // 保留原始JSON数据
            entities: entities // 添加实体识别结果
          };

          // 如果有预览图，添加预览图
          if (allLinks.length > 0 && allLinks[0].img_url) {
            resumeData.preview = allLinks[0].img_url;
          }

          // 如果后端已经返回了技能信息，直接使用
          if (entities && entities.skills && entities.skills.length > 0) {
            console.log('使用后端返回的技能信息:', entities.skills);

            // 保存技能到localStorage
            localStorage.setItem('extractedSkills', JSON.stringify(entities.skills));

            // 更新界面状态
            this.skillsExtracted = true;
            this.extractedSkillsCount = entities.skills.length;

            // 触发技能更新事件
            window.dispatchEvent(new CustomEvent('skillsUpdated', {
              detail: { skills: entities.skills }
            }));

            // 添加技能信息到resumeData
            resumeData.skills = entities.skills;
          }

          // 开始处理生成的简历内容（文本提取和技能分析）
          this.processGeneratedResume(resumeData);

        } else if (response.data.data && response.data.data.raw_response) {
          // 处理解码失败的情况
          console.error('简历解码失败:', response.data.data.error);
          this.$store.dispatch('snackbar/showMessage', {
            message: '简历生成成功，但解码失败，请联系管理员',
            color: 'warning'
          });

          // 仍然发送完成事件，但标记有错误
          this.$emit('generation-complete', {
            ...this.formData,
            generatedContent: '简历生成成功，但解码失败，请联系管理员',
            hasError: true,
            errorDetails: response.data.data.error
          });
        } else {
          // 处理没有简历内容的情况
          this.handleGenerationError('返回数据格式不正确');
        }
      } else {
        // 处理错误
        this.handleGenerationError(response.data ? response.data.message : '生成失败');
      }
    },
  },
  beforeDestroy() {
    // 清除计时器
    if (this.stepInterval) {
      clearInterval(this.stepInterval)
    }
  }
}
</script>

<style scoped>
.ai-resume-generator {
  width: 100%;
  height: 100%;
  color: white;
  background-color: #212121;
  padding: 0;
  margin: 0;
  border-radius: 0;
  border: none;
  outline: none;
  overflow: hidden;
}

.generator-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #212121;
  border: none;
  outline: none;
}

/* 顶部间距，避免被导航栏遮挡 */
.top-spacing {
  height: 64px;
  width: 100%;
  background-color: #212121;
}

/* 输入字段样式 */
.input-field {
  backdrop-filter: blur(8px);
  background-color: #212121;
}

.input-field :deep(.v-input__slot) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.input-field:hover :deep(.v-input__slot) {
  border-color: rgba(255, 255, 255, 0.4) !important;
}

/* 修复表单背景 */
:deep(.v-form) {
  background-color: #212121;
}

:deep(.v-card) {
  background-color: #212121 !important;
  box-shadow: none !important;
}

:deep(.v-list-item) {
  background-color: transparent !important;
}

/* 生成按钮样式 */
.generate-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: white !important; /* 确保文字颜色为白色 */
}

/* 按钮禁用状态样式 */
.generate-btn.v-btn--disabled {
  color: rgba(255, 255, 255, 0.7) !important; /* 半透明白色，表示禁用状态 */
  opacity: 0.8;
}

/* 确保禁用状态下的文字仍然可见 */
.generate-btn.v-btn--disabled .v-btn__content {
  color: rgba(255, 255, 255, 0.7) !important;
}

.generate-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: 0.5s;
}

.generate-btn:hover::after {
  left: 100%;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

/* 预览按钮样式 */
.preview-btn {
  transform: scale(1);
  transition: all 0.3s ease;
  color: white !important;
}

.preview-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

/* 生成进度样式 */
.generation-progress {
  padding: 20px;
  background-color: #212121;
}

.generation-stepper {
  background: transparent !important;
  max-width: 500px;
  margin: 0 auto;
}

.generation-stepper :deep(.v-stepper__content) {
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  margin-left: 12px;
}

.generation-stepper :deep(.v-stepper__step__step) {
  background-color: rgba(255, 255, 255, 0.2) !important;
}

.generation-stepper :deep(.v-stepper__step__step.primary) {
  background-color: white !important;
}

/* 提示卡片样式 */
.tips-card {
  border-radius: 12px;
  backdrop-filter: blur(8px);
  background-color: rgba(255, 255, 255, 0.1) !important;
  border: none !important;
}

/* 动画效果 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}

.slide-fade-enter,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* 响应式调整 */
@media (max-width: 960px) {
  .generator-content {
    padding: 16px;
  }
  
  .top-spacing {
    height: 56px; /* 移动端导航栏通常较小 */
  }
}

@media (max-width: 600px) {
  .generation-steps {
    padding: 0;
  }
}
</style> 