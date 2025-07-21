<template>
  <div class="resume-uploader">
    <div 
      class="upload-zone" 
      :class="{
        'drop-active': isDragActive,
        'upload-success': uploadSuccess,
        'upload-error': uploadError
      }"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover.prevent
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <input 
        ref="fileInput"
        type="file"
        class="hidden-input"
        @change="handleFileChange"
        accept=".pdf,.doc,.docx"
      />

      <transition name="icon-fade" mode="out-in">
        <div v-if="uploadSuccess" key="success" class="upload-icon-container">
          <v-icon size="64" color="success">mdi-check-circle</v-icon>
          <h3 class="text-h5 success--text font-weight-medium mt-2">上传成功</h3>
        </div>
        <div v-else-if="uploadError" key="error" class="upload-icon-container">
          <v-icon size="64" color="error">mdi-alert-circle</v-icon>
          <h3 class="text-h5 error--text font-weight-medium mt-2">上传失败</h3>
          <p class="text-body-2 error--text">{{ errorMessage }}</p>
        </div>
        <div v-else-if="uploading" key="loading" class="upload-icon-container">
          <v-progress-circular
            indeterminate
            size="64"
            width="4"
            color="primary"
          ></v-progress-circular>
          <h3 class="text-h5 primary--text font-weight-medium mt-4">正在上传...</h3>
          <p class="text-body-2 mt-2">请稍候</p>
        </div>
        <div v-else key="upload" class="upload-icon-container">
          <v-icon size="64" color="primary" class="upload-icon animated-icon">{{ isDragActive ? 'mdi-file-upload' : 'mdi-cloud-upload-outline' }}</v-icon>
          <h3 class="text-h5 font-weight-medium mt-2">{{ isDragActive ? '释放以上传文件' : '点击或拖放文件至此处' }}</h3>
          <p class="text-body-1 text-medium-emphasis mt-2">支持 PDF、Word 格式，最大 5MB</p>
        </div>
      </transition>
    </div>

    <div class="file-details mt-6" v-if="selectedFile && !uploading && !uploadSuccess">
      <v-card flat class="file-card">
        <v-card-text class="pa-4">
          <div class="d-flex align-center">
            <v-icon 
              class="mr-3" 
              :color="getFileIconColor(selectedFile.name)"
            >
              {{ getFileIcon(selectedFile.name) }}
            </v-icon>
            <div class="file-info flex-grow-1">
              <div class="font-weight-medium">{{ selectedFile.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
            <v-btn icon small @click="clearFile">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-text>
      </v-card>

      <div class="text-center mt-6">
        <v-btn 
          color="primary" 
          :loading="uploading" 
          @click="uploadFile"
          height="44"
          min-width="180"
          elevation="2"
        >
          <v-icon left>mdi-cloud-upload</v-icon>
          上传简历
        </v-btn>
      </div>
    </div>

    <div class="file-details mt-6" v-if="uploadSuccess">
      <div class="text-center">
        <v-btn
          color="primary"
          @click="continueToNextStep"
          height="44"
          min-width="180"
          elevation="2"
          :loading="processingSkills"
          :disabled="processingSkills"
        >
          <v-icon left v-if="!processingSkills">mdi-arrow-right</v-icon>
          <v-icon left v-if="processingSkills">mdi-brain</v-icon>
          {{ processingSkills ? '正在提取技能...' : '继续' }}
        </v-btn>

        <!-- 技能提取进度提示 -->
        <div v-if="processingSkills" class="mt-3">
          <v-progress-linear
            indeterminate
            color="primary"
            height="2"
          ></v-progress-linear>
          <p class="text-caption text--secondary mt-2">
            正在分析简历内容，提取技能信息...
          </p>
        </div>

        <!-- 技能提取完成提示 -->
        <div v-if="skillsExtracted && extractedSkillsCount > 0" class="mt-3">
          <v-chip
            color="success"
            text-color="white"
            small
          >
            <v-icon left small>mdi-check</v-icon>
            已提取 {{ extractedSkillsCount }} 项技能
          </v-chip>
        </div>
      </div>
    </div>

    <v-slide-y-transition>
      <div class="upload-tips mt-6" v-if="!uploadSuccess">
        <h4 class="text-subtitle-1 font-weight-medium mb-3">上传须知</h4>
        <v-list dense class="transparent">
          <v-list-item>
            <v-list-item-icon class="mr-2">
              <v-icon color="success">mdi-check-circle</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>支持PDF、Word格式</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item>
            <v-list-item-icon class="mr-2">
              <v-icon color="success">mdi-check-circle</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>文件大小不超过5MB</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          
          <v-list-item>
            <v-list-item-icon class="mr-2">
              <v-icon color="success">mdi-check-circle</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>建议使用PDF格式保证格式一致性</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </div>
    </v-slide-y-transition>
  </div>
</template>

<script>
import { uploadResumeFile, processResumeWithStar } from '@/api/resume';
import { clearResumeData } from '@/utils/localStorage';

export default {
  name: 'ResumeUploader',
  data() {
    return {
      selectedFile: null,
      isDragActive: false,
      uploading: false,
      uploadSuccess: false,
      uploadError: false,
      errorMessage: '',
      fileUrl: '',  // 上传后的文件URL
      processResult: null,  // 处理结果
      uploadTimeout: null,   // 上传超时计时器
      processingSkills: false,  // 是否正在处理技能提取
      skillsExtracted: false,   // 技能是否已提取完成
      extractedSkillsCount: 0   // 提取的技能数量
    }
  },
  methods: {
    handleDragEnter(e) {
      e.preventDefault()
      this.isDragActive = true
    },
    
    handleDragLeave(e) {
      e.preventDefault()
      this.isDragActive = false
    },
    
    handleDrop(e) {
      e.preventDefault()
      this.isDragActive = false
      
      const files = e.dataTransfer.files
      if (files.length) {
        this.processFile(files[0])
      }
    },
    
    triggerFileInput() {
      if (!this.uploading) {
        this.$refs.fileInput.click()
      }
    },
    
    handleFileChange(e) {
      const files = e.target.files
      if (files.length) {
        this.processFile(files[0])
      }
    },
    
    processFile(file) {
      // 开始新的简历上传流程时，清理之前的简历相关数据
      clearResumeData();
      console.log('开始新的简历上传，已清理旧的简历数据');

      // 检查文件类型
      const acceptedTypes = ['.pdf', '.doc', '.docx', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const fileType = file.type
      const fileName = file.name
      
      const isValidType = acceptedTypes.some(type => {
        return fileType.includes(type) || fileName.endsWith(type)
      })
      
      if (!isValidType) {
        this.showError('文件格式不支持，请上传PDF或Word文档')
        return
      }
      
      // 检查文件大小
      if (file.size > 5 * 1024 * 1024) { // 5MB
        this.showError('文件大小超过5MB，请压缩后再上传')
        return
      }
      
      this.selectedFile = file
      this.uploadError = false
      this.errorMessage = ''
    },
    
    async uploadFile() {
      if (!this.selectedFile) {
        this.showError('请先选择文件')
        return
      }
      
      this.uploading = true
      this.uploadError = false
      
      try {
        // 上传文件
        const response = await uploadResumeFile(this.selectedFile)
        
        if (response.data && response.data.success) {
          this.uploadSuccess = true
          this.fileUrl = response.data.data.url

          // 设置技能处理状态
          this.processingSkills = true
          this.skillsExtracted = false
          this.extractedSkillsCount = 0

          // 保存文件URL，确保它是正确的
          console.log('文件上传成功，URL:', this.fileUrl)

          // 触发上传成功事件
          this.$emit('upload-success', {
            file: this.selectedFile,
            url: this.fileUrl,
            size: this.selectedFile.size
          })

          // 设置30秒超时，如果工作流处理时间过长，自动继续
          this.uploadTimeout = setTimeout(() => {
            console.warn('工作流处理超时，自动继续到下一步')
            this.processingSkills = false  // 超时时停止处理状态
            this.continueToNextStep()
          }, 30000)

          // 在后台异步处理工作流，不阻塞用户界面
          this.processWorkflowAsync(this.fileUrl)
        } else {
          this.showError((response.data && response.data.message) || '上传失败')
          this.$emit('upload-error', response.data)
        }
      } catch (error) {
        console.error('上传失败:', error)
        this.uploading = false
        this.showError('上传失败，请重试')
        this.$emit('upload-error', error)
      }
    },
    
    // 异步处理工作流的方法
    async processWorkflowAsync(fileUrl) {
      // 确保使用实际上传的文件URL
      if (!fileUrl) {
        console.error('错误：文件URL为空');
        return;
      }

      console.log('开始处理工作流，文件URL:', fileUrl);

      // 初始化resumeUploadData变量
      let resumeUploadData = {};
      try {
        // 尝试从localStorage获取现有数据
        const existingData = localStorage.getItem('resumeUploadData');
        if (existingData) {
          resumeUploadData = JSON.parse(existingData);
        }
      } catch (e) {
        console.warn('无法解析localStorage中的resumeUploadData，使用新对象:', e);
        resumeUploadData = {};
      }
      
      try {
        // 检查工作流服务器是否运行
        try {
          // 先尝试访问工作流服务器根路径，检查是否在线
          await this.$axios.get('http://localhost:8000/', { timeout: 3000 });
          console.log('工作流服务器在线，继续处理');
        } catch (e) {
          console.warn('工作流服务器可能未运行，跳过工作流处理:', e.message);
          this.processResult = {
            success: true,
            message: '文件已上传，但工作流服务器未启动',
            data: null
          };
          return;
        }
        
        // 尝试提取文本内容（如果是PDF文件）
        let textContent = null;
        let extractedSkills = [];
        const fileName = this.selectedFile && this.selectedFile.name ? this.selectedFile.name.toLowerCase() : '';
        if (fileName.endsWith('.pdf') || fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
          try {
            console.log('尝试提取文本内容...');
            
            // 创建一个FormData对象，用于提取文本
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('extract_text', 'true');
            
            // 调用API提取文本
            const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';
            console.log('调用文本提取API:', `${baseURL}/extract_text`);

            const textResponse = await this.$axios.post(
              `${baseURL}/extract_text`,
              formData,
              { timeout: 30000 }
            );

            console.log('文本提取API响应:', textResponse.data);

            if (textResponse.data && textResponse.data.success && textResponse.data.data) {
              if (textResponse.data.data.text) {
                textContent = textResponse.data.data.text;
                resumeUploadData.extractedText = textContent;
                localStorage.setItem('resumeUploadData', JSON.stringify(resumeUploadData));
                console.log(`成功提取文本内容，长度: ${textContent.length} 字符`);
                console.log(`文本预览: ${textContent.substring(0, 100)}...`);
              } else {
                console.warn('API返回成功但没有文本内容');
              }
              
              // 保存提取的技能信息
              if (textResponse.data.data.skills && textResponse.data.data.skills.length > 0) {
                extractedSkills = textResponse.data.data.skills;
                console.log('成功提取技能:', extractedSkills);
                console.log('技能提取是通过resume_ner.py中的extract_structured_info方法完成的');

                // 保存技能到本地存储，以便在其他页面使用
                localStorage.setItem('extractedSkills', JSON.stringify(extractedSkills));

                // 更新技能提取状态
                this.processingSkills = false;
                this.skillsExtracted = true;
                this.extractedSkillsCount = extractedSkills.length;

                // 立即更新processResult，确保技能信息可用
                this.processResult = {
                  success: true,
                  message: '技能提取完成',
                  data: textResponse.data.data,
                  skills: extractedSkills
                };
                console.log('已更新processResult，包含技能信息:', this.processResult);

                // 触发自定义事件通知其他组件技能已更新
                window.dispatchEvent(new CustomEvent('skillsUpdated', {
                  detail: { skills: extractedSkills }
                }));

                console.log('技能提取完成，继续执行STAR分析...');
              } else {
                console.warn('未提取到技能信息');

                // 更新技能提取状态（即使没有技能也算完成）
                this.processingSkills = false;
                this.skillsExtracted = true;
                this.extractedSkillsCount = 0;

                // 即使没有技能，也要设置processResult
                this.processResult = {
                  success: true,
                  message: '文本提取完成，但未识别到技能',
                  data: textResponse.data.data,
                  skills: []
                };
              }
            } else {
              console.warn('API返回异常:', textResponse.data);
            }
          } catch (e) {
            console.error('文本提取失败:', e.message);

            // 停止技能处理状态
            this.processingSkills = false;
            this.skillsExtracted = false;
            this.extractedSkillsCount = 0;

            // 显示错误信息
            this.$store.dispatch('snackbar/showMessage', {
              content: '文本提取失败，请检查文件格式或重新上传',
              color: 'error'
            });
            // 设置错误状态
            this.processResult = {
              success: false,
              message: `文本提取失败: ${e.message}`,
              data: null
            };
            return; // 直接返回，不再继续处理
          }
        }
        
        // 使用processResumeWithStar函数同时处理简历分析和STAR分析
        console.log('使用processResumeWithStar同时处理简历分析和STAR分析...');
        console.log('传递提取的文本内容，长度:', textContent ? textContent.length : 0);
        
        const response = await processResumeWithStar(textContent);
        
        console.log('简历和STAR分析处理结果:', response.data);
           
        // 检查并保存STAR分析结果
        if (response.data && response.data.data && response.data.data.starAnalysis) {
          localStorage.setItem('starWorkflowData', JSON.stringify(response.data.data.starAnalysis));
          console.log('已保存STAR分析结果到localStorage');
        }
        
        // 更新processResult，保留已有的技能信息
        const existingSkills = this.processResult ? this.processResult.skills : extractedSkills;
        this.processResult = {
          success: true,
          message: '文件处理完成',
          data: response.data,
          skills: existingSkills || extractedSkills
        };

        // 确保技能处理状态已完成
        if (this.processingSkills) {
          this.processingSkills = false;
          this.skillsExtracted = true;
        }

        // 处理完成后立即继续到下一步
        console.log('工作流处理完成，立即继续到下一步');
        this.continueToNextStep();

      } catch (error) {
        console.error('工作流处理失败:', error);

        // 使用宽容的错误处理
        this.processResult = {
          success: true,  // 仍然标记为成功，让用户可以继续
          message: '文件已上传，但工作流处理可能不完整',
          data: null,
          error: error.message
        };

        // 即使处理失败也继续到下一步
        console.log('工作流处理失败，但仍继续到下一步');
        this.continueToNextStep();
      }
    },
    
    // 从工作流响应中提取技能信息
    extractSkillsFromWorkflowResponse(responseData) {
      try {
        // 检查是否有工作流响应
        if (!responseData || !responseData.data) {
          return [];
        }
        
        // 检查是否有工作流响应的content字段
        let content = null;
        if (responseData.data.workflow_response && responseData.data.workflow_response.content) {
          content = responseData.data.workflow_response.content;
        } else if (responseData.workflow_response && responseData.workflow_response.content) {
          content = responseData.workflow_response.content;
        }
        
        if (content) {
          return this.extractSkillsFromContent(content);
        }
        
        return [];
      } catch (e) {
        console.error('提取技能信息时出错:', e);
        return [];
      }
    },
    
    // 从内容中提取技能信息
    extractSkillsFromContent(content) {
      try {
        console.log('尝试从content中提取技能信息');
        const skills = [];
        
        // 查找JSON内容
        const jsonMatches = content.match(/```json\s*([\s\S]*?)\s*```/g);
        if (jsonMatches) {
          for (const match of jsonMatches) {
            try {
              // 提取JSON内容
              const jsonContent = match.replace(/```json\s*|\s*```/g, '');
              const parsedJson = JSON.parse(jsonContent);
              
              // 检查不同可能的技能字段
              if (parsedJson.skills && Array.isArray(parsedJson.skills)) {
                skills.push(...parsedJson.skills);
              }
              
              // 检查编程语言等具体技能分类
              const skillCategories = [
                '编程语言', '工具与开发环境', '云平台与分布式技术', '认证与资质'
              ];
              
              for (const category of skillCategories) {
                if (parsedJson[category] && Array.isArray(parsedJson[category])) {
                  skills.push(...parsedJson[category]);
                }
              }
              
              // 检查core_competencies结构
              if (parsedJson.core_competencies && Array.isArray(parsedJson.core_competencies)) {
                for (const comp of parsedJson.core_competencies) {
                  if (comp.competency) {
                    skills.push(comp.competency);
                  }
                }
              }
            } catch (jsonError) {
              console.warn('解析JSON内容失败:', jsonError);
            }
          }
        }
        
        // 查找Markdown列表
        const mdListMatches = content.match(/- ([^\n]+)/g);
        if (mdListMatches) {
          for (const match of mdListMatches) {
            // 提取列表项内容
            const item = match.replace(/- /, '').trim();
            // 只添加看起来像技能的项 (不超过5个单词，不是句子)
            if (item && item.split(' ').length <= 5 && !item.endsWith('.')) {
              skills.push(item);
            }
          }
        }
        
        // 使用Set去重
        return [...new Set(skills)];
      } catch (e) {
        console.error('从内容中提取技能出错:', e);
        return [];
      }
    },
    
    clearFile() {
      this.selectedFile = null
      this.$refs.fileInput.value = ''
      
      // 清除超时计时器
      if (this.uploadTimeout) {
        clearTimeout(this.uploadTimeout)
        this.uploadTimeout = null
      }
    },
    
    showError(message) {
      this.uploadError = true
      this.errorMessage = message
      
      // 3秒后自动清除错误
      setTimeout(() => {
        this.uploadError = false
        this.errorMessage = ''
      }, 3000)
    },
    
    continueToNextStep() {
      // 清除超时计时器
      if (this.uploadTimeout) {
        clearTimeout(this.uploadTimeout)
        this.uploadTimeout = null
      }

      // 确保提取的技能信息可用
      let extractedSkills = [];
      try {
        // 优先从localStorage获取技能信息（最可靠的来源）
        const storedSkills = localStorage.getItem('extractedSkills');
        if (storedSkills) {
          extractedSkills = JSON.parse(storedSkills);
          console.log('从localStorage获取到技能信息:', extractedSkills);
        }

        // 如果localStorage中没有，尝试从processResult中获取
        if ((!extractedSkills || !extractedSkills.length) && this.processResult && this.processResult.skills) {
          extractedSkills = this.processResult.skills;
          console.log('从processResult获取到技能信息:', extractedSkills);
        }

        // 如果还是没有，尝试从processResult.data中获取
        if ((!extractedSkills || !extractedSkills.length) && this.processResult && this.processResult.data && this.processResult.data.skills) {
          extractedSkills = this.processResult.data.skills;
          console.log('从processResult.data获取到技能信息:', extractedSkills);
        }
      } catch (e) {
        console.error('获取技能信息失败:', e);
      }

      // 构建结果对象，确保包含技能信息
      const result = this.processResult || {};

      // 无论是否有技能，都要构建完整的结果对象
      if (!result.result) {
        result.result = {};
      }

      // 如果有技能信息，添加到结果对象中
      if (extractedSkills && extractedSkills.length > 0) {
        result.skills = extractedSkills;
        result.result.skills = extractedSkills;
        console.log('准备发送给父组件的结果对象(含技能):', result);
        console.log('技能数量:', extractedSkills.length);
      } else {
        console.warn('未能找到有效的技能信息，将发送空技能数组');
        result.skills = [];
        result.result.skills = [];
      }

      // 发送事件给父组件
      const emitData = {
        file: this.selectedFile,
        url: this.fileUrl,
        result: result,
        skills: extractedSkills // 直接添加技能字段，确保父组件可以访问
      };

      console.log('发送给父组件的完整数据:', emitData);
      this.$emit('continue', emitData);
    },
    
    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      
      switch (ext) {
        case 'pdf':
          return 'mdi-file-pdf-box'
        case 'doc':
        case 'docx':
          return 'mdi-file-word-box'
        default:
          return 'mdi-file-document-outline'
      }
    },
    
    getFileIconColor(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      
      switch (ext) {
        case 'pdf':
          return 'error'
        case 'doc':
        case 'docx':
          return 'primary'
        default:
          return 'grey'
      }
    },
    
    formatFileSize(size) {
      if (size < 1024) {
        return size + ' B'
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB'
      } else {
        return (size / (1024 * 1024)).toFixed(2) + ' MB'
      }
    }
  }
}
</script>

<style scoped>
.resume-uploader {
  width: 100%;
}

.upload-zone {
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background-color: rgba(0, 0, 0, 0.01);
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
}

.upload-zone:hover {
  border-color: var(--v-primary-base);
  background-color: rgba(var(--v-primary-base), 0.02);
  transform: translateY(-2px);
}

.drop-active {
  border-color: var(--v-primary-base);
  background-color: rgba(var(--v-primary-base), 0.05);
  transform: scale(1.02);
}

.upload-success {
  border-color: var(--v-success-base);
  background-color: rgba(var(--v-success-base), 0.05);
}

.upload-error {
  border-color: var(--v-error-base);
  background-color: rgba(var(--v-error-base), 0.05);
}

.hidden-input {
  position: absolute;
  top: -9999px;
  left: -9999px;
  visibility: hidden;
}

.upload-icon-container {
  text-align: center;
  padding: 20px;
  width: 100%;
}

.animated-icon {
  animation-duration: 1s;
  animation-fill-mode: both;
  animation-iteration-count: infinite;
}

.drop-active .animated-icon {
  animation-name: bounce;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

/* 图标过渡动画 */
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.3s ease;
}

.icon-fade-enter,
.icon-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 文件卡片 */
.file-card {
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.file-info {
  min-width: 0;
}

.file-info div:first-child {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 