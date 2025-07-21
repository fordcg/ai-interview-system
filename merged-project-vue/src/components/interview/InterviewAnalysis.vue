<template>
  <div class="interview-analysis">
    <v-card class="mb-4" elevation="2">
      <v-card-title class="primary--text">
        <v-icon left color="primary">mdi-chart-line</v-icon>
        面试表现分析
      </v-card-title>
      
      <v-card-text>
        <div v-if="loading" class="text-center py-5">
          <v-progress-circular
            indeterminate
            color="primary"
            size="50"
          ></v-progress-circular>
          <div class="mt-3">正在分析面试数据...</div>
        </div>
        
        <div v-else>
          <!-- 总体评分 -->
          <div class="text-center mb-6">
            <v-progress-circular
              :value="analysis.overallScore"
              color="success"
              size="100"
              width="10"
            >
              {{ analysis.overallScore }}
            </v-progress-circular>
            <h2 class="mt-2">总体评分</h2>
            <div class="text-subtitle-1 grey--text">
              {{ getScoreLevel(analysis.overallScore) }}
            </div>
          </div>
          
          <!-- 能力雷达图 -->
          <div class="mb-6">
            <h3 class="mb-3">能力评估</h3>
            <v-card outlined class="pa-3">
              <canvas ref="radarChart" height="250"></canvas>
            </v-card>
          </div>
          
          <!-- 详细分析 -->
          <div class="mb-6">
            <h3 class="mb-3">详细分析</h3>
            <v-expansion-panels>
              <v-expansion-panel
                v-for="(category, index) in analysis.categories"
                :key="index"
              >
                <v-expansion-panel-header>
                  <div class="d-flex align-center">
                    <span>{{ category.name }}</span>
                    <v-spacer></v-spacer>
                    <v-chip
                      small
                      :color="getScoreColor(category.score)"
                      text-color="white"
                      class="ml-2"
                    >
                      {{ category.score }}分
                    </v-chip>
                  </div>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <div v-html="category.analysis"></div>
                  
                  <v-divider class="my-3"></v-divider>
                  
                  <div class="font-weight-bold">优势:</div>
                  <ul>
                    <li v-for="(strength, i) in category.strengths" :key="`str-${i}`">
                      {{ strength }}
                    </li>
                  </ul>
                  
                  <div class="font-weight-bold mt-2">改进建议:</div>
                  <ul>
                    <li v-for="(improvement, i) in category.improvements" :key="`imp-${i}`">
                      {{ improvement }}
                    </li>
                  </ul>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
          
          <!-- 关键词分析 -->
          <div class="mb-6">
            <h3 class="mb-3">关键词分析</h3>
            <v-card outlined class="pa-3">
              <div class="keyword-cloud">
                <v-chip
                  v-for="(keyword, index) in analysis.keywords"
                  :key="index"
                  :color="getKeywordColor(keyword.weight)"
                  text-color="white"
                  class="ma-1"
                  :x-large="keyword.weight > 0.8"
                  :large="keyword.weight > 0.5 && keyword.weight <= 0.8"
                  :small="keyword.weight <= 0.5"
                >
                  {{ keyword.text }}
                </v-chip>
              </div>
            </v-card>
          </div>
          
          <!-- 情感分析 -->
          <div class="mb-6">
            <h3 class="mb-3">情感分析</h3>
            <v-card outlined class="pa-3">
              <div class="d-flex justify-space-between align-center mb-3">
                <div>积极度</div>
                <div>{{ (analysis.sentiment.positive * 100).toFixed(1) }}%</div>
              </div>
              <v-progress-linear
                :value="analysis.sentiment.positive * 100"
                color="success"
                height="10"
              ></v-progress-linear>
              
              <div class="d-flex justify-space-between align-center mt-4 mb-3">
                <div>消极度</div>
                <div>{{ (analysis.sentiment.negative * 100).toFixed(1) }}%</div>
              </div>
              <v-progress-linear
                :value="analysis.sentiment.negative * 100"
                color="error"
                height="10"
              ></v-progress-linear>
              
              <div class="d-flex justify-space-between align-center mt-4 mb-3">
                <div>中性度</div>
                <div>{{ (analysis.sentiment.neutral * 100).toFixed(1) }}%</div>
              </div>
              <v-progress-linear
                :value="analysis.sentiment.neutral * 100"
                color="info"
                height="10"
              ></v-progress-linear>
            </v-card>
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
  name: "InterviewAnalysis",
  props: {
    interviewId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      analysis: null,
      radarChart: null
    };
  },
  mounted() {
    // 模拟加载数据
    setTimeout(() => {
      this.analysis = this.getMockAnalysisData();
      this.loading = false;
      
      // 在下一个DOM更新周期后初始化图表
      this.$nextTick(() => {
        this.initRadarChart();
      });
    }, 1500);
  },
  methods: {
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
    
    getKeywordColor(weight) {
      if (weight > 0.8) return 'primary';
      if (weight > 0.6) return 'teal';
      if (weight > 0.4) return 'cyan';
      if (weight > 0.2) return 'light-blue';
      return 'blue-grey';
    },
    
    initRadarChart() {
      // 注意：这里假设已经引入了Chart.js
      // 实际使用时需要确保Chart.js已经被正确引入
      if (window.Chart && this.$refs.radarChart) {
        const ctx = this.$refs.radarChart.getContext('2d');
        
        // 从分析数据中提取雷达图所需数据
        const labels = this.analysis.categories.map(cat => cat.name);
        const data = this.analysis.categories.map(cat => cat.score);
        
        this.radarChart = new window.Chart(ctx, {
          type: 'radar',
          data: {
            labels: labels,
            datasets: [{
              label: '能力评分',
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
    
    getMockAnalysisData() {
      // 模拟分析数据
      return {
        overallScore: 85,
        categories: [
          {
            name: '专业知识',
            score: 88,
            analysis: '候选人展示了扎实的专业知识基础，能够清晰地解释复杂概念，并将理论与实践相结合。',
            strengths: [
              '对核心概念有深入理解',
              '能够举例说明理论应用',
              '术语使用准确专业'
            ],
            improvements: [
              '可以进一步拓展跨领域知识',
              '建议关注最新行业动态和技术发展'
            ]
          },
          {
            name: '逻辑思维',
            score: 82,
            analysis: '候选人的回答结构清晰，论证有力，能够从多个角度分析问题。',
            strengths: [
              '思路清晰，逻辑连贯',
              '善于分析问题根本原因'
            ],
            improvements: [
              '有时结论过于仓促，可以更全面考虑各种可能性',
              '建议增强批判性思维能力'
            ]
          },
          {
            name: '沟通表达',
            score: 90,
            analysis: '候选人表达流畅，语言精准，能够根据问题难度调整解释方式，确保面试官理解。',
            strengths: [
              '语言表达清晰准确',
              '善于使用比喻和类比解释复杂概念',
              '回答简洁有力，直击要点'
            ],
            improvements: [
              '可以适当控制语速，给听者更多思考空间'
            ]
          },
          {
            name: '实践经验',
            score: 78,
            analysis: '候选人有一定的实践经验，能够结合实际案例回答问题，但在某些领域的经验深度有限。',
            strengths: [
              '能够分享具体工作案例',
              '理解理论到实践的转化过程'
            ],
            improvements: [
              '建议积累更多不同场景下的实践经验',
              '可以更深入地分析项目中遇到的挑战和解决方案'
            ]
          },
          {
            name: '创新能力',
            score: 75,
            analysis: '候选人在解决问题时展示了一定的创新思维，但可以更加大胆和开放。',
            strengths: [
              '能够提出非常规解决方案',
              '愿意尝试新方法和工具'
            ],
            improvements: [
              '建议培养更开放的思维模式',
              '可以多关注跨领域的创新案例，寻找灵感'
            ]
          },
          {
            name: '团队协作',
            score: 85,
            analysis: '候选人展示了良好的团队意识，理解协作的重要性，能够有效地在团队中发挥作用。',
            strengths: [
              '重视团队成员的贡献和意见',
              '善于在团队中分享知识和经验',
              '能够处理团队冲突'
            ],
            improvements: [
              '可以进一步提升领导力和影响力',
              '建议学习更多团队激励技巧'
            ]
          }
        ],
        keywords: [
          { text: '专业', weight: 0.95 },
          { text: '分析能力', weight: 0.87 },
          { text: '沟通', weight: 0.82 },
          { text: '解决方案', weight: 0.78 },
          { text: '团队合作', weight: 0.75 },
          { text: '创新', weight: 0.72 },
          { text: '实践经验', weight: 0.68 },
          { text: '学习能力', weight: 0.65 },
          { text: '技术熟练度', weight: 0.62 },
          { text: '适应性', weight: 0.58 },
          { text: '领导力', weight: 0.55 },
          { text: '时间管理', weight: 0.52 },
          { text: '压力应对', weight: 0.48 },
          { text: '批判思维', weight: 0.45 },
          { text: '自信', weight: 0.42 },
          { text: '积极态度', weight: 0.38 }
        ],
        sentiment: {
          positive: 0.65,
          negative: 0.15,
          neutral: 0.20
        }
      };
    }
  },
  beforeDestroy() {
    // 销毁图表实例
    if (this.radarChart) {
      this.radarChart.destroy();
    }
  }
};
</script>

<style scoped>
.interview-analysis {
  max-width: 900px;
  margin: 0 auto;
}

.keyword-cloud {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  padding: 10px;
}
</style> 