<template>
  <div class="interview-report">
    <v-card class="mb-4" elevation="2">
      <v-card-title class="primary--text d-flex justify-space-between">
        <div>
          <v-icon left color="primary">mdi-file-document</v-icon>
          面试报告
        </div>
        <v-btn 
          color="primary" 
          outlined 
          small
          @click="printReport"
        >
          <v-icon left>mdi-printer</v-icon>
          打印报告
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <div v-if="loading" class="text-center py-5">
          <v-progress-circular
            indeterminate
            color="primary"
            size="50"
          ></v-progress-circular>
          <div class="mt-3">正在生成面试报告...</div>
        </div>
        
        <div v-else ref="reportContent">
          <!-- 报告头部 -->
          <div class="report-header text-center mb-6">
            <h1 class="text-h4 font-weight-bold primary--text">面试评估报告</h1>
            <div class="text-subtitle-1 mt-2">报告编号: {{ report.id }}</div>
            <div class="text-subtitle-1">生成日期: {{ formatDate(report.createdAt) }}</div>
          </div>
          
          <!-- 基本信息 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">基本信息</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">姓名:</div>
                    <div>{{ report.candidateName }}</div>
                  </div>
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">应聘职位:</div>
                    <div>{{ report.position }}</div>
                  </div>
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">面试类型:</div>
                    <div>{{ report.interviewType }}</div>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">面试时长:</div>
                    <div>{{ report.duration }} 分钟</div>
                  </div>
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">题目数量:</div>
                    <div>{{ report.questionCount }} 题</div>
                  </div>
                  <div class="d-flex mb-2">
                    <div class="font-weight-medium" style="width: 100px">完成情况:</div>
                    <div>{{ report.completionRate }}%</div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          
          <!-- 总体评价 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">总体评价</v-card-title>
            <v-card-text>
              <div class="d-flex flex-column flex-md-row align-center mb-4">
                <v-progress-circular
                  :value="report.overallScore"
                  color="success"
                  size="100"
                  width="10"
                  class="mr-md-6 mb-4 mb-md-0"
                >
                  {{ report.overallScore }}
                </v-progress-circular>
                
                <div>
                  <div class="text-h6 mb-2">{{ getScoreLevel(report.overallScore) }}</div>
                  <div v-html="report.overallComment"></div>
                </div>
              </div>
              
              <v-divider class="my-4"></v-divider>
              
              <div class="font-weight-bold mb-2">主要优势:</div>
              <ul>
                <li v-for="(strength, index) in report.strengths" :key="`str-${index}`">
                  {{ strength }}
                </li>
              </ul>
              
              <div class="font-weight-bold mt-4 mb-2">需要提升:</div>
              <ul>
                <li v-for="(improvement, index) in report.improvements" :key="`imp-${index}`">
                  {{ improvement }}
                </li>
              </ul>
            </v-card-text>
          </v-card>
          
          <!-- 能力评估 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">能力评估</v-card-title>
            <v-card-text>
              <div class="mb-4">
                <canvas ref="skillsChart" height="250"></canvas>
              </div>
              
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>能力维度</th>
                      <th>得分</th>
                      <th>评价</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(skill, index) in report.skills" :key="index">
                      <td>{{ skill.name }}</td>
                      <td>
                        <v-chip
                          small
                          :color="getScoreColor(skill.score)"
                          text-color="white"
                        >
                          {{ skill.score }}
                        </v-chip>
                      </td>
                      <td>{{ skill.comment }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
          
          <!-- 问题回答分析 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">问题回答分析</v-card-title>
            <v-card-text>
              <v-expansion-panels>
                <v-expansion-panel
                  v-for="(question, index) in report.questions"
                  :key="index"
                >
                  <v-expansion-panel-header>
                    <div class="d-flex align-center">
                      <span>问题 {{ index + 1 }}: {{ question.title }}</span>
                      <v-spacer></v-spacer>
                      <v-chip
                        small
                        :color="getScoreColor(question.score)"
                        text-color="white"
                        class="ml-2"
                      >
                        {{ question.score }}分
                      </v-chip>
                    </div>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <div class="font-weight-medium mb-2">问题内容:</div>
                    <div class="mb-4">{{ question.content }}</div>
                    
                    <div class="font-weight-medium mb-2">回答内容:</div>
                    <div class="mb-4">{{ question.answer }}</div>
                    
                    <div class="font-weight-medium mb-2">点评:</div>
                    <div v-html="question.comment"></div>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </v-card>
          
          <!-- 建议与反馈 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">建议与反馈</v-card-title>
            <v-card-text>
              <div v-html="report.suggestions"></div>
              
              <v-divider class="my-4"></v-divider>
              
              <div class="font-weight-bold mb-2">职业发展建议:</div>
              <ul>
                <li v-for="(suggestion, index) in report.careerSuggestions" :key="`sug-${index}`">
                  {{ suggestion }}
                </li>
              </ul>
              
              <div class="font-weight-bold mt-4 mb-2">学习资源推荐:</div>
              <v-chip-group>
                <v-chip
                  v-for="(resource, index) in report.learningResources"
                  :key="index"
                  color="primary"
                  outlined
                  class="ma-1"
                >
                  {{ resource }}
                </v-chip>
              </v-chip-group>
            </v-card-text>
          </v-card>
          
          <!-- 面试官评语 -->
          <v-card outlined class="mb-6">
            <v-card-title class="subtitle-1">面试官评语</v-card-title>
            <v-card-text>
              <div class="interviewer-comment">
                <div class="font-italic mb-2">"{{ report.interviewerComment }}"</div>
                <div class="text-right">
                  <span class="font-weight-medium">{{ report.interviewerName }}</span>
                  <span class="ml-2 grey--text">{{ report.interviewerTitle }}</span>
                </div>
              </div>
            </v-card-text>
          </v-card>
          
          <!-- 报告尾部 -->
          <div class="report-footer text-center mt-6 grey--text">
            <div>此报告由系统智能生成，仅供参考</div>
            <div>© {{ new Date().getFullYear() }} 职位与面试系统</div>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
// 假设已经引入了Chart.js库
// import Chart from 'chart.js'

export default {
  name: "InterviewReport",
  props: {
    interviewId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      report: null,
      skillsChart: null
    };
  },
  mounted() {
    // 模拟加载数据
    setTimeout(() => {
      this.report = this.getMockReportData();
      this.loading = false;
      
      // 在下一个DOM更新周期后初始化图表
      this.$nextTick(() => {
        this.initSkillsChart();
      });
    }, 1500);
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getScoreLevel(score) {
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '中等';
      if (score >= 60) return '及格';
      return '需要提高';
    },
    
    getScoreColor(score) {
      if (score >= 90) return 'success';
      if (score >= 80) return 'light-green';
      if (score >= 70) return 'amber';
      if (score >= 60) return 'orange';
      return 'error';
    },
    
    initSkillsChart() {
      // 注意：这里假设已经引入了Chart.js
      // 实际使用时需要确保Chart.js已经被正确引入
      if (window.Chart && this.$refs.skillsChart) {
        const ctx = this.$refs.skillsChart.getContext('2d');
        
        // 从报告数据中提取图表所需数据
        const labels = this.report.skills.map(skill => skill.name);
        const data = this.report.skills.map(skill => skill.score);
        
        this.skillsChart = new window.Chart(ctx, {
          type: 'radar',
          data: {
            labels: labels,
            datasets: [{
              label: '能力得分',
              data: data,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
          },
          options: {
            scale: {
              ticks: {
                beginAtZero: true,
                max: 100
              }
            }
          }
        });
      } else {
        console.error('Chart.js not loaded or canvas element not found');
      }
    },
    
    printReport() {
      const printContent = this.$refs.reportContent.innerHTML;
      const originalContent = document.body.innerHTML;
      
      const printStyles = `
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 20px;
          }
          .report-header {
            text-align: center;
            margin-bottom: 30px;
          }
          h1 {
            color: #1976d2;
          }
          .v-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            page-break-inside: avoid;
          }
          .v-card-title {
            background-color: #f5f5f5;
            padding: 15px;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
          }
          .v-card-text {
            padding: 15px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
          }
          .report-footer {
            text-align: center;
            margin-top: 30px;
            color: #757575;
            font-size: 12px;
          }
          @media print {
            .v-btn, .v-expansion-panel-header::after {
              display: none !important;
            }
            .v-expansion-panel-content {
              display: block !important;
            }
          }
        </style>
      `;
      
      document.body.innerHTML = printStyles + printContent;
      window.print();
      document.body.innerHTML = originalContent;
    },
    
    getMockReportData() {
      // 模拟报告数据
      return {
        id: 'IR-' + Math.floor(Math.random() * 10000),
        createdAt: new Date().toISOString(),
        candidateName: '张三',
        position: '前端开发工程师',
        interviewType: '技术面试',
        duration: 45,
        questionCount: 10,
        completionRate: 100,
        overallScore: 85,
        overallComment: '候选人展示了扎实的技术基础和良好的沟通能力，对前端开发有深入理解。在解决问题时思路清晰，能够提供有效的解决方案。建议进一步提升在复杂项目管理和团队协作方面的经验。',
        strengths: [
          '扎实的JavaScript基础知识和框架使用经验',
          '良好的代码质量意识和问题解决能力',
          '清晰的沟通表达和技术讲解能力',
          '对新技术有持续学习的热情'
        ],
        improvements: [
          '大型项目架构设计经验有待提升',
          '性能优化策略可以进一步深入',
          '团队协作和技术管理经验需要加强'
        ],
        skills: [
          {
            name: '专业知识',
            score: 88,
            comment: '对前端技术栈有全面了解，基础扎实'
          },
          {
            name: '问题解决',
            score: 85,
            comment: '能够分析问题并提供有效解决方案'
          },
          {
            name: '代码能力',
            score: 82,
            comment: '编码规范，结构清晰，但复杂场景处理有待提升'
          },
          {
            name: '学习能力',
            score: 90,
            comment: '展示了较强的学习意愿和能力，跟进技术发展'
          },
          {
            name: '沟通表达',
            score: 87,
            comment: '表达清晰，能够准确传达技术概念'
          },
          {
            name: '团队协作',
            score: 78,
            comment: '理解团队协作的重要性，但实际经验有限'
          }
        ],
        questions: [
          {
            title: '前端性能优化',
            content: '请详细描述你在项目中使用过的前端性能优化策略。',
            answer: '我在项目中主要采用了以下性能优化策略：1. 资源压缩与合并，减少HTTP请求；2. 使用懒加载技术延迟加载非关键资源；3. 实现组件级别的代码分割；4. 利用浏览器缓存机制；5. 优化关键渲染路径；6. 使用服务端渲染提升首屏加载速度。',
            score: 85,
            comment: '回答全面，涵盖了多个性能优化维度，但缺少具体的实施案例和效果数据。建议在回答类似问题时，结合实际项目经验，提供优化前后的对比数据，更有说服力。'
          },
          {
            title: 'React组件设计',
            content: '如何设计一个高复用性、高性能的React组件？',
            answer: '设计高复用性、高性能的React组件需要考虑：1. 单一职责原则，组件功能专一；2. 使用Props进行配置，提高灵活性；3. 合理使用React.memo和useMemo避免不必要的重渲染；4. 将复杂逻辑抽离为自定义Hook；5. 使用Context管理跨层级数据；6. 采用TypeScript增强类型安全性。',
            score: 90,
            comment: '回答非常全面，展示了对React组件设计的深入理解，特别是在性能优化方面的考量很到位。能够结合React特性和软件设计原则，是一个很好的回答。'
          },
          {
            title: '前端安全',
            content: '前端开发中需要注意哪些安全问题？如何防范？',
            answer: '前端安全主要包括：1. XSS攻击，通过输入验证和输出编码防范；2. CSRF攻击，使用CSRF Token和SameSite Cookie属性；3. 点击劫持，设置X-Frame-Options头部；4. 敏感数据保护，避免在前端存储敏感信息；5. 依赖包安全，定期更新并审计第三方库。',
            score: 82,
            comment: '回答覆盖了主要的前端安全问题，但对每种安全问题的防范措施可以更加详细。例如，对于XSS的防范，可以具体说明内容安全策略(CSP)的实施方法。'
          }
        ],
        suggestions: '根据面试表现，建议候选人可以在以下方面进一步提升：<br>1. 深入学习前端架构设计，特别是大型应用的模块化和状态管理策略<br>2. 加强性能优化实践，学习更多工具化和自动化的性能监测方法<br>3. 参与更多团队协作项目，提升在多人协作环境中的工作经验',
        careerSuggestions: [
          '考虑参与开源项目，提升技术影响力',
          '关注前端工程化和自动化测试领域的发展',
          '学习一些后端知识，向全栈开发方向发展'
        ],
        learningResources: [
          'React高级模式与最佳实践',
          '前端性能优化实战',
          '现代JavaScript深度解析',
          'Web安全防护指南',
          '前端架构设计'
        ],
        interviewerComment: '这位候选人技术基础扎实，思维清晰，沟通能力强，是一位很有潜力的前端开发人才。虽然在大型项目经验上还有所欠缺，但学习能力强，相信能够快速成长。推荐进入下一轮面试。',
        interviewerName: '李四',
        interviewerTitle: '高级前端开发工程师'
      };
    }
  },
  beforeDestroy() {
    // 销毁图表实例
    if (this.skillsChart) {
      this.skillsChart.destroy();
    }
  }
};
</script>

<style scoped>
.interview-report {
  max-width: 900px;
  margin: 0 auto;
}

.interviewer-comment {
  background-color: #f5f5f5;
  border-left: 4px solid #1976d2;
  padding: 16px;
  border-radius: 4px;
}

@media print {
  .v-btn {
    display: none !important;
  }
}
</style> 