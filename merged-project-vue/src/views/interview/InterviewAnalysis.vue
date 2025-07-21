<template>
  <div class="interview-analysis-container">
    <v-container fluid>
      <!-- 沉浸式面试横幅 -->
      <v-row v-if="jobInfo && (parsedJobAnalysisData || originalContent)">
        <v-col cols="12">
          <v-card
            class="mb-4 interview-banner"
            elevation="8"
            :style="{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }"
          >
            <v-card-text class="pa-6">
              <v-row align="center">
                <v-col cols="12" md="8">
                  <div class="d-flex align-center mb-2">
                    <v-icon size="32" color="white" class="mr-3">mdi-rocket-launch</v-icon>
                    <div>
                      <div class="text-h5 font-weight-bold mb-1">🎯 准备好开始AI深度面试了吗？</div>
                      <div class="text-body-1 opacity-90">
                        基于 <strong>{{ jobInfo.jobName }}</strong> 岗位和您的简历深度分析，生成专业面试问题
                      </div>
                    </div>
                  </div>
                  <div class="d-flex align-center mt-3">
                    <v-chip color="rgba(255,255,255,0.2)" text-color="white" small class="mr-2">
                      <v-icon left small>mdi-brain</v-icon>
                      X1智能问题生成
                    </v-chip>
                    <v-chip color="rgba(255,255,255,0.2)" text-color="white" small class="mr-2">
                      <v-icon left small>mdi-database-search</v-icon>
                      5模块数据分析
                    </v-chip>
                    <v-chip color="rgba(255,255,255,0.2)" text-color="white" small class="mr-2">
                      <v-icon left small>mdi-target</v-icon>
                      STAR经历验证
                    </v-chip>
                    <v-chip color="rgba(255,255,255,0.2)" text-color="white" small>
                      <v-icon left small>mdi-chart-line</v-icon>
                      技能缺口分析
                    </v-chip>
                  </div>
                </v-col>
                <v-col cols="12" md="4" class="text-center">
                  <v-btn
                    color="white"
                    class="primary--text font-weight-bold px-8 py-3"
                    x-large
                    rounded
                    elevation="4"
                    @click="startImmersiveInterview"
                    :loading="starLoading || deepInterviewLoading"
                    :disabled="deepInterviewLoading"
                  >
                    <v-icon left size="24">mdi-brain</v-icon>
                    开始AI深度面试
                  </v-btn>
                  <div class="text-caption mt-2 opacity-75">
                    {{ getLoadingMessage() }}
                  </div>

                  <!-- 深度面试等待状态 -->
                  <div v-if="deepInterviewLoading" class="mt-4">
                    <v-progress-linear
                      :value="((totalWaitTime - remainingTime) / totalWaitTime) * 100"
                      color="primary"
                      height="6"
                      rounded
                      class="mb-2"
                    ></v-progress-linear>
                    <div class="text-body-2 grey--text">
                      剩余等待时间: {{ formatTime(remainingTime) }}
                    </div>
                    <v-btn
                      text
                      color="primary"
                      small
                      @click="stopDeepInterviewCountdown"
                      class="mt-2"
                    >
                      取消等待
                    </v-btn>
                  </div>

                  <!-- DeepSeek 面试问题生成状态 -->
                  <div v-if="questionGenerationLoading" class="mt-4">
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="24"
                      width="3"
                      class="mb-2"
                    ></v-progress-circular>
                    <div class="text-body-2 grey--text">
                      正在生成深度面试问题...
                    </div>
                    <div class="text-caption grey--text mt-1">
                      基于5个数据模块进行AI分析
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-card class="mb-4" elevation="2">
            <v-card-title class="primary--text">
              <v-icon left color="primary">mdi-file-search</v-icon>
              岗位分析结果
              <v-spacer></v-spacer>
              <v-chip v-if="jobInfo" color="primary" small>{{ jobInfo.jobName }}</v-chip>
            </v-card-title>
            
            <v-card-text>
              <!-- 岗位基本信息 -->
              <v-row v-if="jobInfo" class="mb-4">
                <v-col cols="12" md="6">
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon color="primary">mdi-office-building</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>公司名称</v-list-item-title>
                        <v-list-item-subtitle>{{ jobInfo.companyName }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon color="primary">mdi-map-marker</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>工作地点</v-list-item-title>
                        <v-list-item-subtitle>{{ jobInfo.city }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon color="primary">mdi-currency-cny</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>薪资范围</v-list-item-title>
                        <v-list-item-subtitle>{{ jobInfo.salary }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                    
                    <v-list-item>
                      <v-list-item-icon>
                        <v-icon color="primary">mdi-school</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title>学历要求</v-list-item-title>
                        <v-list-item-subtitle>{{ jobInfo.education }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>
              
              <!-- 加载状态 -->
              <div v-if="loading" class="text-center py-5">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="64"
                ></v-progress-circular>
                <div class="mt-3">正在加载岗位分析结果...</div>
              </div>
              
              <!-- 错误状态 -->
              <div v-else-if="error" class="text-center py-5">
                <v-icon size="64" color="error">mdi-alert-circle</v-icon>
                <div class="mt-3 text-h6">加载失败</div>
                <div class="text-body-2 grey--text">{{ error }}</div>
                <v-btn color="primary" class="mt-4" @click="fetchAnalysisData">
                  重新加载
                </v-btn>
              </div>
              
              <!-- 分析结果 -->
              <div v-else-if="analysisData" class="analysis-content">
                <v-tabs v-model="activeTab" background-color="transparent" grow>
                  <v-tab>
                    <v-icon left>mdi-file-document-outline</v-icon>
                    岗位分析
                  </v-tab>
                  <v-tab>
                    <v-icon left>mdi-chart-bar</v-icon>
                    技能匹配
                  </v-tab>
                  <v-tab>
                    <v-icon left>mdi-lightbulb-outline</v-icon>
                    面试建议
                  </v-tab>
                  <v-tab>
                    <v-icon left>mdi-file-document-multiple</v-icon>
                    简历分析
                  </v-tab>
                  <v-tab>
                    <v-icon left>mdi-star-outline</v-icon>
                    STAR分析
                  </v-tab>
                </v-tabs>

                <v-tabs-items v-model="activeTab" class="mt-4">
                  <!-- 岗位分析 -->
                  <v-tab-item>
                    <v-card flat>
                      <v-card-text>
                        <!-- 优先显示结构化数据 -->
                        <div v-if="parsedJobAnalysisData" class="job-analysis-data">
                          <div class="d-flex justify-space-between align-center mb-4">
                            <h3 class="text-h6 primary--text">
                              <v-icon left color="primary">mdi-briefcase-search</v-icon>
                              岗位分析结果
                            </h3>
                            <div>
                              <v-btn color="primary" small outlined @click="refreshJobAnalysis">
                                <v-icon left small>mdi-refresh</v-icon>
                                刷新
                              </v-btn>
                            </div>
                          </div>

                          <!-- JD关键要素 -->
                          <v-card v-if="parsedJobAnalysisData.核心职责" class="mb-4" outlined>
                            <v-card-title class="pb-2">
                              <v-icon left color="primary">mdi-clipboard-list</v-icon>
                              核心职责
                            </v-card-title>
                            <v-card-text>
                              <v-list dense>
                                <v-list-item
                                  v-for="(responsibility, index) in parsedJobAnalysisData.核心职责"
                                  :key="index"
                                  class="px-0"
                                >
                                  <v-list-item-avatar>
                                    <v-avatar size="24" color="primary">
                                      <span class="white--text caption">{{ index + 1 }}</span>
                                    </v-avatar>
                                  </v-list-item-avatar>
                                  <v-list-item-content>
                                    <v-list-item-title class="text-wrap">
                                      {{ responsibility }}
                                    </v-list-item-title>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-card-text>
                          </v-card>

                          <!-- 必备技能与要求 -->
                          <v-card v-if="parsedJobAnalysisData.必备技能与要求" class="mb-4" outlined>
                            <v-card-title class="pb-2">
                              <v-icon left color="success">mdi-check-circle</v-icon>
                              必备技能与要求
                            </v-card-title>
                            <v-card-text>
                              <v-row>
                                <v-col
                                  v-for="(requirements, category) in parsedJobAnalysisData.必备技能与要求"
                                  :key="category"
                                  cols="12" md="4"
                                >
                                  <div class="requirement-category">
                                    <h4 class="mb-2 text-subtitle-1 font-weight-bold">
                                      <v-icon left small :color="getRequirementCategoryColor(category)">
                                        {{ getRequirementCategoryIcon(category) }}
                                      </v-icon>
                                      {{ category }}
                                    </h4>
                                    <v-list dense>
                                      <v-list-item
                                        v-for="(requirement, index) in requirements"
                                        :key="index"
                                        class="px-0 py-1"
                                      >
                                        <v-list-item-avatar>
                                          <v-icon small :color="getRequirementCategoryColor(category)">
                                            mdi-circle-small
                                          </v-icon>
                                        </v-list-item-avatar>
                                        <v-list-item-content>
                                          <v-list-item-title class="text-wrap caption">
                                            {{ requirement }}
                                          </v-list-item-title>
                                        </v-list-item-content>
                                      </v-list-item>
                                    </v-list>
                                  </div>
                                </v-col>
                              </v-row>
                            </v-card-text>
                          </v-card>

                          <!-- 优先考虑项 -->
                          <v-card v-if="parsedJobAnalysisData.优先考虑项" class="mb-4" outlined>
                            <v-card-title class="pb-2">
                              <v-icon left color="warning">mdi-star</v-icon>
                              优先考虑项
                            </v-card-title>
                            <v-card-text>
                              <div class="priority-items">
                                <v-chip
                                  v-for="(item, index) in parsedJobAnalysisData.优先考虑项"
                                  :key="index"
                                  class="ma-1"
                                  color="warning"
                                  outlined
                                  small
                                >
                                  <v-icon left small>mdi-star-outline</v-icon>
                                  {{ item }}
                                </v-chip>
                              </div>
                            </v-card-text>
                          </v-card>

                          <!-- 能力维度映射 -->
                          <v-card v-if="parsedJobAnalysisData.dimensions" class="mb-4" outlined>
                            <v-card-title class="pb-2">
                              <v-icon left color="info">mdi-chart-radar</v-icon>
                              能力维度映射
                            </v-card-title>
                            <v-card-text>
                              <v-list>
                                <v-list-item
                                  v-for="(dimension, index) in parsedJobAnalysisData.dimensions"
                                  :key="index"
                                  class="px-0"
                                >
                                  <v-list-item-avatar>
                                    <v-avatar :color="getImportanceColor(dimension.importance)" size="32">
                                      <v-icon dark small>{{ getImportanceIcon(dimension.importance) }}</v-icon>
                                    </v-avatar>
                                  </v-list-item-avatar>
                                  <v-list-item-content>
                                    <v-list-item-title class="font-weight-medium">
                                      {{ dimension.competency }}
                                      <v-chip
                                        :color="getImportanceColor(dimension.importance)"
                                        x-small
                                        class="ml-2"
                                      >
                                        {{ dimension.importance }}
                                      </v-chip>
                                    </v-list-item-title>
                                    <v-list-item-subtitle class="text-wrap">
                                      {{ dimension.justification }}
                                    </v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-card-text>
                          </v-card>
                        </div>

                        <!-- 如果没有结构化数据，显示原始内容 -->
                        <div v-else-if="analysisContent" class="analysis-report">
                          <v-alert type="info" outlined class="mb-4">
                            <div class="font-weight-bold mb-2">📄 原始分析内容</div>
                            <div>结构化数据解析失败，显示原始分析内容</div>
                          </v-alert>
                          <div v-html="formattedAnalysisContent"></div>
                        </div>

                        <!-- 都没有时显示无数据提示 -->
                        <div v-else class="text-center py-5">
                          <v-icon size="64" color="grey lighten-1">mdi-file-search</v-icon>
                          <div class="mt-3 text-h6">暂无岗位分析</div>
                          <v-btn color="primary" class="mt-3" @click="fetchAnalysisData">
                            <v-icon left>mdi-refresh</v-icon>
                            重新加载
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>
                  
                  <!-- 技能匹配 -->
                  <v-tab-item>
                    <v-card flat>
                      <v-card-text>
                        <div v-if="skillsMatch && skillsMatch.length > 0" class="skills-match">
                          <v-list>
                            <v-list-item v-for="(skill, index) in skillsMatch" :key="index">
                              <v-list-item-content>
                                <v-list-item-title>{{ skill.name }}</v-list-item-title>
                                <v-list-item-subtitle>
                                  <v-progress-linear
                                    :value="skill.match * 100"
                                    :color="getMatchColor(skill.match)"
                                    height="20"
                                    striped
                                  >
                                    <template v-slot:default="{ value }">
                                      <strong>{{ Math.ceil(value) }}%</strong>
                                    </template>
                                  </v-progress-linear>
                                </v-list-item-subtitle>
                              </v-list-item-content>
                            </v-list-item>
                          </v-list>
                        </div>
                        <div v-else class="text-center py-5">
                          <v-icon size="64" color="grey lighten-1">mdi-chart-bar</v-icon>
                          <div class="mt-3 text-h6">暂无技能匹配数据</div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>
                  
                  <!-- 面试建议 -->
                  <v-tab-item>
                    <v-card flat>
                      <v-card-text>
                        <div v-if="interviewTips && interviewTips.length > 0" class="interview-tips">
                          <v-timeline dense>
                            <v-timeline-item
                              v-for="(tip, index) in interviewTips"
                              :key="index"
                              :color="getTipColor(index)"
                              small
                            >
                              <div class="font-weight-medium">{{ tip.title }}</div>
                              <div class="text-body-2">{{ tip.content }}</div>
                            </v-timeline-item>
                          </v-timeline>
                        </div>
                        <div v-else class="text-center py-5">
                          <v-icon size="64" color="grey lighten-1">mdi-lightbulb-outline</v-icon>
                          <div class="mt-3 text-h6">暂无面试建议</div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>
                  
                  <!-- 简历分析 -->
                  <v-tab-item>
                    <v-card flat>
                      <v-card-text>
                        <div v-if="parsedOriginalContent" class="resume-analysis">
                          <div class="d-flex justify-space-between align-center mb-4">
                            <h3 class="text-h6 primary--text">
                              <v-icon left color="primary">mdi-account-star</v-icon>
                              简历能力分析
                            </h3>
                            <v-btn color="primary" small outlined @click="reloadOriginalContent">
                              <v-icon left small>mdi-refresh</v-icon>
                              重新加载
                            </v-btn>
                          </div>



                          <!-- 项目核心能力 - 新格式支持 -->
                          <div v-if="parsedOriginalContent.projects" class="mb-4">
                            <v-card
                              v-for="(project, projectIndex) in parsedOriginalContent.projects"
                              :key="projectIndex"
                              class="mb-4"
                              outlined
                            >
                              <v-card-title class="pb-2">
                                <v-icon left color="success">mdi-rocket-launch</v-icon>
                                {{ project.project_name }}
                              </v-card-title>
                              <v-card-subtitle class="pt-0">
                                项目体现的核心能力
                              </v-card-subtitle>
                              <v-card-text>
                                <v-list dense>
                                  <v-list-item
                                    v-for="(competency, index) in project.core_competencies"
                                    :key="index"
                                    class="px-0"
                                  >
                                    <v-list-item-avatar>
                                      <v-avatar size="32" :color="getCompetencyColor(index)">
                                        <v-icon dark small>{{ getCompetencyIcon(competency.competency) }}</v-icon>
                                      </v-avatar>
                                    </v-list-item-avatar>
                                    <v-list-item-content>
                                      <v-list-item-title class="font-weight-medium">
                                        {{ competency.competency }}
                                      </v-list-item-title>
                                      <v-list-item-subtitle class="text-wrap">
                                        {{ competency.evidence }}
                                      </v-list-item-subtitle>
                                    </v-list-item-content>
                                  </v-list-item>
                                </v-list>
                              </v-card-text>
                            </v-card>
                          </div>

                          <!-- 项目核心能力 - 原格式兼容 -->
                          <v-card v-else-if="parsedOriginalContent.project_name" class="mb-4" outlined>
                            <v-card-title class="pb-2">
                              <v-icon left color="success">mdi-rocket-launch</v-icon>
                              项目体现的核心能力
                            </v-card-title>
                            <v-card-subtitle class="pt-0">
                              {{ parsedOriginalContent.project_name }}
                            </v-card-subtitle>
                            <v-card-text>
                              <v-list dense>
                                <v-list-item
                                  v-for="(competency, index) in parsedOriginalContent.core_competencies"
                                  :key="index"
                                  class="px-0"
                                >
                                  <v-list-item-avatar>
                                    <v-avatar size="32" :color="getCompetencyColor(index)">
                                      <v-icon dark small>{{ getCompetencyIcon(competency.competency) }}</v-icon>
                                    </v-avatar>
                                  </v-list-item-avatar>
                                  <v-list-item-content>
                                    <v-list-item-title class="font-weight-medium">
                                      {{ competency.competency }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle class="text-wrap">
                                      {{ competency.evidence }}
                                    </v-list-item-subtitle>
                                  </v-list-item-content>
                                </v-list-item>
                              </v-list>
                            </v-card-text>
                          </v-card>

                          <!-- 技能分类展示 -->
                          <v-card v-if="parsedOriginalContent.skills" class="mb-4" outlined>
                            <v-card-title>
                              <v-icon left color="info">mdi-tools</v-icon>
                              技能清单
                            </v-card-title>
                            <v-card-text>
                              <v-row>
                                <v-col
                                  v-for="(skillGroup, category) in parsedOriginalContent.skills"
                                  :key="category"
                                  cols="12" md="6"
                                >
                                  <div class="skill-category">
                                    <h4 class="mb-2 text-subtitle-1 font-weight-bold">
                                      <v-icon left small :color="getSkillCategoryColor(category)">
                                        {{ getSkillCategoryIcon(category) }}
                                      </v-icon>
                                      {{ category }}
                                    </h4>
                                    <div class="skill-chips">
                                      <v-chip
                                        v-for="skill in skillGroup"
                                        :key="skill"
                                        small
                                        class="ma-1"
                                        :color="getSkillCategoryColor(category)"
                                        outlined
                                      >
                                        {{ skill }}
                                      </v-chip>
                                    </div>
                                  </div>
                                </v-col>
                              </v-row>
                            </v-card-text>
                          </v-card>

                          <!-- STAR原则项目描述 -->
                          <v-card v-if="parsedOriginalContent.star" class="mb-4" outlined>
                            <v-card-title>
                              <v-icon left color="warning">mdi-star-four-points</v-icon>
                              STAR原则项目描述
                            </v-card-title>
                            <v-card-text>
                              <v-timeline dense>
                                <v-timeline-item
                                  v-for="(item, key) in parsedOriginalContent.star"
                                  :key="key"
                                  :color="getStarColor(key)"
                                  small
                                >
                                  <template v-slot:icon>
                                    <v-icon dark small>{{ getStarIcon(key) }}</v-icon>
                                  </template>
                                  <div class="font-weight-medium mb-1">{{ getStarTitle(key) }}</div>
                                  <div class="text-body-2" v-html="formatStarContent(item)"></div>
                                </v-timeline-item>
                              </v-timeline>
                            </v-card-text>
                          </v-card>
                        </div>

                        <!-- 原始文本显示 -->
                        <div v-else-if="originalContent" class="original-content-wrapper">
                          <div class="d-flex justify-space-between align-center mb-3">
                            <h3 class="text-h6 primary--text">
                              <v-icon left color="primary">mdi-file-document-outline</v-icon>
                              简历分析原始内容
                            </h3>
                            <v-btn color="primary" small outlined @click="reloadOriginalContent">
                              <v-icon left small>mdi-refresh</v-icon>
                              重新加载
                            </v-btn>
                          </div>
                          <v-card outlined>
                            <v-card-text>
                              <v-alert type="info" outlined dense class="mb-3">
                                数据解析失败，显示原始分析内容
                              </v-alert>
                              <div class="original-content">
                                <pre>{{ originalContent }}</pre>
                              </div>
                            </v-card-text>
                          </v-card>
                        </div>

                        <!-- 无数据状态 -->
                        <div v-else class="text-center py-5">
                          <v-icon size="64" color="grey lighten-1">mdi-file-document-multiple</v-icon>
                          <div class="mt-3 text-h6">暂无简历分析</div>
                          <v-btn color="primary" class="mt-3" @click="reloadOriginalContent">
                            <v-icon left>mdi-refresh</v-icon>
                            尝试加载
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>

                  <!-- STAR分析 -->
                  <v-tab-item>
                    <v-card flat>
                      <v-card-text>
                        <div v-if="analysisData && analysisData.starWorkflow">
                          <div class="d-flex justify-space-between align-center mb-4">
                            <h3 class="text-h6 primary--text">
                              <v-icon left color="orange">mdi-star</v-icon>
                              STAR分析结果
                            </h3>
                            <v-btn color="primary" small outlined @click="refreshStarAnalysis">
                              <v-icon left small>mdi-refresh</v-icon>
                              刷新
                            </v-btn>
                          </div>



                          <!-- 结构化STAR项目展示 -->
                          <div v-if="parsedStarAnalysisData && parsedStarAnalysisData.projects" class="star-projects">
                            <v-card
                              v-for="(project, index) in parsedStarAnalysisData.projects"
                              :key="index"
                              class="mb-6"
                              outlined
                              elevation="2"
                            >
                              <v-card-title class="pb-2">
                                <v-icon left color="orange">mdi-briefcase-star</v-icon>
                                {{ project.name }}
                                <v-spacer></v-spacer>
                                <!-- 技术深度标识 -->
                                <v-chip
                                  v-if="project.technical_depth"
                                  :color="getTechnicalDepthColor(project.technical_depth)"
                                  small
                                  outlined
                                  class="mr-2"
                                >
                                  <v-icon left small>{{ getTechnicalDepthIcon(project.technical_depth) }}</v-icon>
                                  {{ getTechnicalDepthLabel(project.technical_depth) }}
                                </v-chip>
                                <v-chip color="orange" small outlined v-if="project.period">
                                  {{ project.period }}
                                </v-chip>
                              </v-card-title>

                              <v-card-text>
                                <!-- 量化指标概览 -->
                                <div v-if="project.quantified_metrics && project.quantified_metrics.length > 0" class="mb-4">
                                  <v-card outlined class="pa-3" color="success lighten-5">
                                    <div class="text-subtitle-1 font-weight-bold mb-3">
                                      <v-icon left color="success">mdi-chart-line</v-icon>
                                      量化成果概览
                                    </div>
                                    <v-row>
                                      <v-col
                                        v-for="(metric, metricIndex) in project.quantified_metrics"
                                        :key="metricIndex"
                                        cols="12" md="6"
                                      >
                                        <div class="metric-card">
                                          <div class="text-subtitle-2 font-weight-medium mb-1">
                                            {{ metric.metric }}
                                          </div>
                                          <div class="d-flex align-center">
                                            <div class="metric-values flex-grow-1">
                                              <span v-if="metric.before && !metric.before.includes('[需补充]')" class="text-caption grey--text">
                                                基线: {{ metric.before }}
                                              </span>
                                              <div class="text-h6 font-weight-bold" :class="getMetricChangeColor(metric.change)">
                                                {{ metric.after }}
                                              </div>
                                            </div>
                                            <div v-if="metric.change && metric.change !== 'N/A'" class="metric-change ml-2">
                                              <v-chip
                                                :color="getMetricChangeColor(metric.change)"
                                                small
                                                :outlined="!metric.change.includes('+')"
                                              >
                                                <v-icon left small>{{ getMetricChangeIcon(metric.change) }}</v-icon>
                                                {{ metric.change }}
                                              </v-chip>
                                            </div>
                                          </div>
                                        </div>
                                      </v-col>
                                    </v-row>
                                  </v-card>
                                </div>

                                <!-- STAR四个部分的展示 -->
                                <v-timeline dense>
                                  <!-- Situation -->
                                  <v-timeline-item color="primary" small>
                                    <template v-slot:icon>
                                      <v-icon dark small>mdi-map-marker</v-icon>
                                    </template>
                                    <div class="font-weight-medium mb-2">
                                      Situation (情境)
                                      <v-chip v-if="project.elements && project.elements.Situation && !project.elements.Situation.is_original"
                                              x-small color="orange" class="ml-2">
                                        AI补全
                                      </v-chip>
                                      <v-chip v-if="hasNeedsSupplement(project.situation)"
                                              x-small color="warning" class="ml-2">
                                        需补充
                                      </v-chip>
                                    </div>
                                    <div class="text-body-2" v-html="formatStarContent(project.situation || '暂无数据')"></div>
                                  </v-timeline-item>

                                  <!-- Task -->
                                  <v-timeline-item color="success" small>
                                    <template v-slot:icon>
                                      <v-icon dark small>mdi-clipboard-list</v-icon>
                                    </template>
                                    <div class="font-weight-medium mb-2">
                                      Task (任务)
                                      <v-chip v-if="project.elements && project.elements.Task && !project.elements.Task.is_original"
                                              x-small color="orange" class="ml-2">
                                        AI补全
                                      </v-chip>
                                      <v-chip v-if="hasNeedsSupplement(project.task)"
                                              x-small color="warning" class="ml-2">
                                        需补充
                                      </v-chip>
                                    </div>
                                    <div class="text-body-2" v-html="formatStarContent(project.task || '暂无数据')"></div>
                                  </v-timeline-item>

                                  <!-- Action -->
                                  <v-timeline-item color="info" small>
                                    <template v-slot:icon>
                                      <v-icon dark small>mdi-run</v-icon>
                                    </template>
                                    <div class="font-weight-medium mb-2">
                                      Action (行动)
                                      <v-chip v-if="project.elements && project.elements.Action && !project.elements.Action.is_original"
                                              x-small color="orange" class="ml-2">
                                        AI补全
                                      </v-chip>
                                      <v-chip v-if="project.elements && project.elements.Action && project.elements.Action.technical_depth"
                                              x-small :color="getTechnicalDepthColor(project.elements.Action.technical_depth)" class="ml-2">
                                        {{ getTechnicalDepthLabel(project.elements.Action.technical_depth) }}
                                      </v-chip>
                                      <v-chip v-if="hasNeedsSupplement(project.action)"
                                              x-small color="warning" class="ml-2">
                                        需补充
                                      </v-chip>
                                    </div>
                                    <div class="text-body-2" v-html="formatStarContent(project.action || '暂无数据')"></div>
                                  </v-timeline-item>

                                  <!-- Result -->
                                  <v-timeline-item color="warning" small>
                                    <template v-slot:icon>
                                      <v-icon dark small>mdi-trophy</v-icon>
                                    </template>
                                    <div class="font-weight-medium mb-2">
                                      Result (结果)
                                      <v-chip v-if="project.elements && project.elements.Result && !project.elements.Result.is_original"
                                              x-small color="orange" class="ml-2">
                                        AI补全
                                      </v-chip>
                                      <v-chip v-if="project.elements && project.elements.Result && project.elements.Result.is_quantified"
                                              x-small color="success" class="ml-2">
                                        已量化
                                      </v-chip>
                                      <v-chip v-if="hasNeedsSupplement(project.result)"
                                              x-small color="warning" class="ml-2">
                                        需补充
                                      </v-chip>
                                    </div>
                                    <div class="text-body-2" v-html="formatStarContent(project.result || '暂无数据')"></div>

                                    <!-- 定性影响 -->
                                    <div v-if="project.qualitative_impact" class="mt-2">
                                      <div class="text-caption grey--text mb-1">定性影响:</div>
                                      <div class="text-body-2 font-italic">{{ project.qualitative_impact }}</div>
                                    </div>
                                  </v-timeline-item>
                                </v-timeline>

                                <!-- 缺失要素提示 -->
                                <div v-if="project.missing_elements && project.missing_elements.length > 0" class="mb-4">
                                  <v-alert type="warning" outlined dense>
                                    <div class="font-weight-bold mb-2">
                                      <v-icon left>mdi-alert-circle</v-icon>
                                      缺失要素
                                    </div>
                                    <v-chip
                                      v-for="element in project.missing_elements"
                                      :key="element"
                                      small
                                      class="ma-1"
                                      color="warning"
                                      outlined
                                    >
                                      {{ element }}
                                    </v-chip>
                                  </v-alert>
                                </div>

                                <!-- 改进建议 -->
                                <div v-if="project.improvement_suggestions && project.improvement_suggestions.length > 0" class="mb-4">
                                  <v-card outlined class="pa-3">
                                    <div class="text-subtitle-1 font-weight-bold mb-2">
                                      <v-icon left color="info">mdi-lightbulb-outline</v-icon>
                                      改进建议
                                    </div>
                                    <v-list dense>
                                      <v-list-item
                                        v-for="(suggestion, index) in project.improvement_suggestions"
                                        :key="index"
                                        class="px-0"
                                      >
                                        <v-list-item-avatar>
                                          <v-avatar size="24" color="info">
                                            <span class="white--text caption">{{ index + 1 }}</span>
                                          </v-avatar>
                                        </v-list-item-avatar>
                                        <v-list-item-content>
                                          <v-list-item-title class="text-wrap">
                                            {{ suggestion }}
                                          </v-list-item-title>
                                        </v-list-item-content>
                                      </v-list-item>
                                    </v-list>
                                  </v-card>
                                </div>
                              </v-card-text>
                            </v-card>
                          </div>

                        </div>

                        <!-- 原始STAR分析内容展示（解析失败时的降级方案） -->
                        <div v-else-if="getStarAnalysisContent(analysisData.starWorkflow)" class="mb-4">
                          <v-card outlined class="pa-4">
                            <div class="text-subtitle-1 font-weight-bold mb-3">
                              <v-icon left color="primary">mdi-text-box-outline</v-icon>
                              STAR分析原始内容
                            </div>
                            <v-alert type="info" outlined dense class="mb-3">
                              数据解析失败，显示原始分析内容
                            </v-alert>
                            <div class="star-content" v-html="formatStarContent(getStarAnalysisContent(analysisData.starWorkflow))"></div>
                          </v-card>
                        </div>

                        <!-- 无STAR分析数据时的提示 -->
                        <div v-else class="text-center py-5">
                          <v-icon size="64" color="grey lighten-1">mdi-star-off</v-icon>
                          <div class="mt-3 text-h6">暂无STAR分析</div>
                          <div class="text-body-2 grey--text mb-3">请先上传简历以获取STAR分析结果</div>
                          <v-btn color="primary" @click="callStarWorkflow" :loading="starLoading">
                            <v-icon left>mdi-star</v-icon>
                            生成STAR分析
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-tab-item>


                </v-tabs-items>
              </div>
              
              <!-- 无数据状态 -->
              <div v-else class="text-center py-5">
                <v-icon size="64" color="grey lighten-1">mdi-file-search-outline</v-icon>
                <div class="mt-3 text-h6">暂无分析数据</div>
                <div class="text-body-2 grey--text">请先选择一个岗位进行分析</div>
                <v-btn color="primary" class="mt-4" to="/job/list">
                  浏览岗位
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { analysisParser } from '@/utils/analysisParser';

export default {
  name: 'InterviewAnalysis',
  data() {
    return {
      loading: true,
      error: null,
      jobInfo: null,
      analysisData: null,
      activeTab: 0,
      starLoading: false,

      // 深度面试等待相关属性
      deepInterviewLoading: false,
      deepInterviewLoadingMessage: '',
      countdownTimer: null,
      dataCheckInterval: null,
      remainingTime: 180, // 剩余时间（秒），默认3分钟
      totalWaitTime: 180, // 总等待时间（秒）
      dataStatus: {
        jobResumeWorkflowResult: false
      },

      // DeepSeek 面试问题生成相关
      interviewQuestions: null,
      questionGenerationLoading: false
    };
  },
  computed: {
    analysisContent() {
      if (!this.analysisData) return '';

      // 只显示岗位分析数据，不合并其他内容
      if (this.analysisData.jobAnalysis) {
        const jobAnalysis = this.analysisData.jobAnalysis;

        // 尝试从不同的数据结构中获取content
        let content = null;
        if (jobAnalysis.data && jobAnalysis.data.choices &&
            jobAnalysis.data.choices[0] &&
            jobAnalysis.data.choices[0].delta &&
            jobAnalysis.data.choices[0].delta.content) {
          content = jobAnalysis.data.choices[0].delta.content;
        } else if (jobAnalysis.data && jobAnalysis.data.content) {
          content = jobAnalysis.data.content;
        } else if (jobAnalysis.content) {
          content = jobAnalysis.content;
        } else if (typeof jobAnalysis === 'string') {
          try {
            const parsed = JSON.parse(jobAnalysis);
            if (parsed.data && parsed.data.choices &&
                parsed.data.choices[0] &&
                parsed.data.choices[0].delta &&
                parsed.data.choices[0].delta.content) {
              content = parsed.data.choices[0].delta.content;
            } else if (parsed.content) {
              content = parsed.content;
            } else {
              content = jobAnalysis;
            }
          } catch (e) {
            content = jobAnalysis;
          }
        }

        // 确保返回字符串
        if (content !== null && content !== undefined) {
          return typeof content === 'string' ? content : String(content);
        }
      }

      // 如果没有找到任何内容，返回原始数据的字符串表示
      return JSON.stringify(this.analysisData, null, 2);
    },
    
    formattedAnalysisContent() {
      if (!this.analysisContent) return '';

      // 确保analysisContent是字符串类型
      let content = this.analysisContent;
      if (typeof content !== 'string') {
        content = String(content);
      }

      // 将换行符转换为HTML换行
      return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // 处理Markdown加粗
        .replace(/\*(.*?)\*/g, '<em>$1</em>'); // 处理Markdown斜体
    },
    
    originalContent() {
      // 从localStorage获取原始content内容，支持多种格式
      try {
        const content = localStorage.getItem('originalWorkflowContent');
        if (!content) return null;

        // 尝试解析为JSON格式的API响应
        try {
          const jsonData = JSON.parse(content);

          // 格式1: {choices: [{delta: {content: "..."}}]}
          if (jsonData.choices && jsonData.choices[0] && jsonData.choices[0].delta && jsonData.choices[0].delta.content) {
            console.log('检测到API响应格式，提取content');
            return jsonData.choices[0].delta.content;
          }

          // 格式2: {code: 0, choices: [{delta: {content: "..."}}]}
          if (jsonData.code === 0 && jsonData.choices && jsonData.choices[0] && jsonData.choices[0].delta && jsonData.choices[0].delta.content) {
            console.log('检测到完整API响应格式，提取content');
            return jsonData.choices[0].delta.content;
          }

          // 格式3: 直接的content字符串
          if (jsonData.content) {
            console.log('检测到content字段');
            return jsonData.content;
          }

          // 如果是其他JSON格式，转换为字符串
          console.log('未识别的JSON格式，转换为字符串');
          return JSON.stringify(jsonData, null, 2);
        } catch (e) {
          // 不是JSON格式，直接返回原始字符串
          console.log('不是JSON格式，返回原始字符串');
          return content;
        }
      } catch (e) {
        console.error('获取原始content内容失败:', e);
        return null;
      }
    },

    parsedOriginalContent() {
      // 使用新的解析器解析原始工作流内容
      if (!this.originalContent) return null;

      try {
        console.log('原始内容长度:', this.originalContent.length);
        console.log('原始内容前200字符:', this.originalContent.substring(0, 200));

        console.log('使用新解析器解析简历分析内容');
        const result = analysisParser.parseResumeAnalysis(this.originalContent);

        if (result) {
          console.log('新解析器解析成功:', result);
          return result;
        }

        // 如果新解析器失败，尝试旧的解析逻辑作为降级方案
        console.log('新解析器失败，尝试降级解析');
        return this.fallbackParseOriginalContent();
      } catch (e) {
        console.error('解析原始工作流内容失败:', e);
        return null;
      }
    },

    parsedJobAnalysisData() {
      // 解析岗位分析数据
      if (!this.analysisData || !this.analysisData.jobAnalysis) {
        console.log('岗位分析数据不存在:', this.analysisData);
        return null;
      }

      try {
        const jobAnalysis = this.analysisData.jobAnalysis;
        console.log('原始岗位分析数据:', jobAnalysis);

        // 尝试从不同的数据结构中获取content
        let content = null;
        if (jobAnalysis.data && jobAnalysis.data.choices &&
            jobAnalysis.data.choices[0] &&
            jobAnalysis.data.choices[0].delta &&
            jobAnalysis.data.choices[0].delta.content) {
          content = jobAnalysis.data.choices[0].delta.content;
          console.log('从 data.choices[0].delta.content 获取内容');
        } else if (jobAnalysis.data && jobAnalysis.data.content) {
          content = jobAnalysis.data.content;
          console.log('从 data.content 获取内容');
        } else if (jobAnalysis.content) {
          content = jobAnalysis.content;
          console.log('从 content 获取内容');
        } else if (typeof jobAnalysis === 'string') {
          try {
            const parsed = JSON.parse(jobAnalysis);
            if (parsed.data && parsed.data.choices &&
                parsed.data.choices[0] &&
                parsed.data.choices[0].delta &&
                parsed.data.choices[0].delta.content) {
              content = parsed.data.choices[0].delta.content;
              console.log('从解析后的 data.choices[0].delta.content 获取内容');
            } else if (parsed.content) {
              content = parsed.content;
              console.log('从解析后的 content 获取内容');
            } else {
              content = jobAnalysis;
              console.log('直接使用字符串内容');
            }
          } catch (e) {
            content = jobAnalysis;
            console.log('JSON解析失败，直接使用字符串内容');
          }
        } else {
          // 尝试直接使用jobAnalysis作为数据
          console.log('尝试直接使用jobAnalysis作为结构化数据');
          if (jobAnalysis.核心职责 || jobAnalysis['核心职责']) {
            console.log('发现直接的结构化数据');
            const result = { ...jobAnalysis };

            // 如果有dimensions数组，直接使用
            if (jobAnalysis.dimensions) {
              result.dimensions = jobAnalysis.dimensions;
            }

            return result;
          }
        }

        console.log('提取的内容:', content ? content.substring(0, 200) + '...' : 'null');

        if (!content) {
          console.log('无法提取内容');
          return null;
        }

        // 解析JD关键要素
        const jdMatch = content.match(/JD关键要素\s*```json\s*([\s\S]*?)\s*```/);
        if (jdMatch) {
          console.log('找到JD关键要素匹配');
          const jdData = JSON.parse(jdMatch[1]);
          const result = { ...jdData };

          // 解析能力维度映射
          const dimensionsMatch = content.match(/能力维度映射\s*```json\s*([\s\S]*?)\s*```/);
          if (dimensionsMatch) {
            console.log('找到能力维度映射匹配');
            const dimensionsData = JSON.parse(dimensionsMatch[1]);
            result.dimensions = dimensionsData.dimensions;
          }

          console.log('解析后的岗位分析数据:', result);
          return result;
        } else {
          console.log('未找到JD关键要素匹配，尝试直接解析JSON');
          // 尝试直接解析整个content为JSON
          try {
            const directParsed = JSON.parse(content);
            if (directParsed.核心职责 || directParsed['核心职责']) {
              console.log('直接解析JSON成功');
              return directParsed;
            }
          } catch (e) {
            console.log('直接解析JSON失败:', e.message);
          }
        }

        console.log('所有解析方法都失败');
        return null;
      } catch (e) {
        console.error('解析岗位分析数据失败:', e);
        return null;
      }
    },
    
    skillsMatch() {
      // 从分析数据中提取技能匹配信息
      if (!this.analysisData) return [];
      
      const skills = [];
      
      // 从localStorage获取提取的技能
      try {
        const extractedSkills = localStorage.getItem('extractedSkills');
        if (extractedSkills) {
          const parsedSkills = JSON.parse(extractedSkills);
          console.log('从localStorage获取到的技能:', parsedSkills);
          
          if (Array.isArray(parsedSkills) && parsedSkills.length > 0) {
            // 为每个技能生成匹配度
            parsedSkills.forEach(skill => {
              if (typeof skill === 'string') {
                // 根据技能在分析内容中的出现频率计算匹配度
                let match = 0.5; // 默认匹配度
                
                if (this.analysisContent) {
                  // 简单计算：如果技能在分析内容中出现，增加匹配度
                  const regex = new RegExp(skill, 'gi');
                  const occurrences = (this.analysisContent.match(regex) || []).length;
                  
                  // 根据出现次数调整匹配度，最高1.0
                  match = Math.min(0.5 + (occurrences * 0.1), 1.0);
                }
                
                skills.push({
                  name: skill,
                  match: match
                });
              }
            });
          }
        }
      } catch (e) {
        console.error('解析技能数据失败:', e);
      }
      
      // 如果没有从localStorage获取到技能，尝试从分析内容中提取
      if (skills.length === 0 && this.analysisContent) {
        // 尝试从分析内容中提取技能
        const skillMatches = this.analysisContent.match(/技能[：:]\s*([\w\s,，]+)/gi);
        if (skillMatches) {
          skillMatches.forEach(match => {
            const skillList = match.replace(/技能[：:]\s*/i, '').split(/[,，]/);
            skillList.forEach(skill => {
              const trimmedSkill = skill.trim();
              if (trimmedSkill) {
                // 检查是否已存在该技能
                const existingSkill = skills.find(s => s.name.toLowerCase() === trimmedSkill.toLowerCase());
                if (!existingSkill) {
                  skills.push({
                    name: trimmedSkill,
                    match: Math.random() * 0.3 + 0.7 // 模拟70%-100%的匹配度
                  });
                }
              }
            });
          });
        }
        
        // 尝试匹配更多技能模式
        const moreSkillPatterns = [
          /掌握([\w\s,，]+)等/gi,
          /熟悉([\w\s,，]+)等/gi,
          /精通([\w\s,，]+)等/gi,
          /了解([\w\s,，]+)等/gi,
          /使用([\w\s,，]+)等/gi
        ];
        
        moreSkillPatterns.forEach(pattern => {
          const matches = this.analysisContent.match(pattern);
          if (matches) {
            matches.forEach(match => {
              const extractedText = match.replace(/[掌握|熟悉|精通|了解|使用]/g, '').replace(/等$/, '');
              const skillList = extractedText.split(/[,，]/);
              
              skillList.forEach(skill => {
                const trimmedSkill = skill.trim();
                if (trimmedSkill && trimmedSkill.length > 1) {
                  // 检查是否已存在该技能
                  const existingSkill = skills.find(s => s.name.toLowerCase() === trimmedSkill.toLowerCase());
                  if (!existingSkill) {
                    skills.push({
                      name: trimmedSkill,
                      match: Math.random() * 0.4 + 0.6 // 模拟60%-100%的匹配度
                    });
                  }
                }
              });
            });
          }
        });
      }
      
      // 按匹配度排序
      return skills.sort((a, b) => b.match - a.match);
    },
    
    interviewTips() {
      // 从分析数据中提取面试建议
      // 这里是一个简单的模拟，实际应用中需要根据API返回的数据结构进行调整
      if (!this.analysisContent) return [];

      // 尝试从分析内容中提取建议信息
      const tips = [];
      const sections = this.analysisContent.split(/\n\n|\r\n\r\n/);

      sections.forEach(section => {
        if (section.includes('建议') || section.includes('准备') || section.includes('提示')) {
          const lines = section.split(/\n|\r\n/);
          if (lines.length > 0) {
            tips.push({
              title: lines[0],
              content: lines.slice(1).join(' ')
            });
          }
        }
      });

      // 如果没有找到建议，返回一些默认建议
      if (tips.length === 0 && this.jobInfo) {
        return [
          {
            title: '研究公司背景',
            content: `在面试前详细了解${this.jobInfo.companyName}的业务、文化和最新动态。`
          },
          {
            title: '准备技能展示',
            content: '准备具体的项目案例，展示你的技能如何解决实际问题。'
          },
          {
            title: '准备问题',
            content: '准备几个关于职位和公司的问题，显示你的兴趣和求知欲。'
          }
        ];
      }

      return tips;
    },

    parsedStarAnalysisData() {
      // 使用新的解析器解析STAR分析数据
      if (!this.analysisData || !this.analysisData.starWorkflow) return null;

      const starContent = this.getStarAnalysisContent(this.analysisData.starWorkflow);
      if (!starContent) return null;

      try {
        console.log('使用新解析器解析STAR分析内容');
        const result = analysisParser.parseStarAnalysis(starContent);

        if (result) {
          console.log('新STAR解析器解析成功:', result);
          return result;
        }

        // 如果新解析器失败，返回null
        console.log('新STAR解析器失败');
        return null;
      } catch (e) {
        console.error('STAR分析解析失败:', e);
        return null;
      }
    }
  },
  methods: {
    // 开始沉浸式面试
    async startImmersiveInterview() {
      if (!this.jobInfo) {
        this.$store.dispatch('snackbar/showMessage', {
          message: '请先选择一个岗位进行分析',
          color: 'warning'
        })
        return
      }

      // 首先检查jobResumeWorkflowResult是否存在
      const jobResumeWorkflowResult = localStorage.getItem('jobResumeWorkflowResult')

      if (!jobResumeWorkflowResult) {
        // 如果不存在，启动等待机制
        this.deepInterviewLoading = true
        this.deepInterviewLoadingMessage = '等待岗位简历匹配分析完成...'
        this.startDeepInterviewCountdown()
        return
      }

      // 如果存在，直接进行深度面试
      this.proceedWithDeepInterview()
    },

    // 启动深度面试倒计时等待
    startDeepInterviewCountdown() {
      console.log('开始等待jobResumeWorkflowResult数据...')

      // 重置倒计时状态
      this.remainingTime = this.totalWaitTime

      // 初始数据状态检查
      this.checkJobResumeWorkflowStatus()

      // 启动倒计时定时器（每秒更新）
      this.countdownTimer = setInterval(() => {
        this.remainingTime--

        if (this.remainingTime <= 0) {
          console.log('等待超时，进行最终检查')
          this.handleDeepInterviewCountdownEnd()
        }
      }, 1000)

      // 启动数据检查定时器（每5秒检查一次）
      this.dataCheckInterval = setInterval(() => {
        this.checkJobResumeWorkflowStatus()
      }, 5000)

      console.log('深度面试等待定时器已启动')
    },

    // 检查jobResumeWorkflowResult状态
    checkJobResumeWorkflowStatus() {
      const jobResumeWorkflowResult = localStorage.getItem('jobResumeWorkflowResult')
      const hasData = !!jobResumeWorkflowResult && jobResumeWorkflowResult.length > 50

      if (hasData && !this.dataStatus.jobResumeWorkflowResult) {
        console.log('检测到jobResumeWorkflowResult数据')
        this.dataStatus.jobResumeWorkflowResult = true

        this.$store.dispatch('snackbar/showMessage', {
          message: '岗位简历匹配分析完成，开始生成深度面试问题',
          color: 'success'
        })

        // 停止等待，开始深度面试
        this.stopDeepInterviewCountdown()
        this.proceedWithDeepInterview()
      }

      return hasData
    },

    // 停止深度面试倒计时
    stopDeepInterviewCountdown() {
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
      }

      if (this.dataCheckInterval) {
        clearInterval(this.dataCheckInterval)
        this.dataCheckInterval = null
      }

      this.deepInterviewLoading = false
    },

    // 处理深度面试倒计时结束
    handleDeepInterviewCountdownEnd() {
      console.log('深度面试等待超时')
      this.stopDeepInterviewCountdown()

      const hasData = this.checkJobResumeWorkflowStatus()

      if (hasData) {
        this.proceedWithDeepInterview()
      } else {
        this.$store.dispatch('snackbar/showMessage', {
          message: '等待超时，jobResumeWorkflowResult数据未准备完成，将使用基础面试模式',
          color: 'warning'
        })
        this.navigateToBasicInterview()
      }
    },

    // 执行深度面试流程
    async proceedWithDeepInterview() {
      // 显示加载状态
      this.questionGenerationLoading = true
      this.$store.dispatch('snackbar/showMessage', {
        message: '正在生成深度面试问题，请稍候...',
        color: 'info'
      })

      try {
        // 收集5个数据模块
        const dataModules = this.collectDataModulesForDeepInterview()

        // 验证数据完整性
        const missingModules = this.validateDataModules(dataModules)
        if (missingModules.length > 0) {
          this.$store.dispatch('snackbar/showMessage', {
            message: `缺少必要数据模块: ${missingModules.join(', ')}，将使用基础面试模式`,
            color: 'warning'
          })

          // 使用基础面试模式
          this.navigateToBasicInterview()
          return
        }

        // 调用 DeepSeek API 生成面试问题
        const questions = await this.generateInterviewQuestions(dataModules)

        if (questions && questions.success) {
          // 保存生成的问题到 localStorage
          localStorage.setItem('deepseekInterviewQuestions', JSON.stringify(questions))

          this.$store.dispatch('snackbar/showMessage', {
            message: '深度面试问题生成成功！',
            color: 'success'
          })

          // 跳转到面试页面
          this.navigateToDeepInterview(questions)
        } else {
          throw new Error('面试问题生成失败')
        }

      } catch (error) {
        console.error('生成深度面试问题失败:', error)

        this.$store.dispatch('snackbar/showMessage', {
          message: '深度面试问题生成失败，将使用基础面试模式',
          color: 'error'
        })

        // 降级到基础面试模式
        this.navigateToBasicInterview()
      } finally {
        this.questionGenerationLoading = false
      }
    },

    // 收集深度面试所需的5个数据模块
    collectDataModulesForDeepInterview() {
      const dataModules = {}

      try {
        // 1. starWorkflowData (项目STAR结构) - 确保是文本数据
        const starWorkflowData = localStorage.getItem('starWorkflowData')
        if (starWorkflowData) {
          try {
            // 如果是JSON，尝试提取文本内容
            const parsed = JSON.parse(starWorkflowData)
            if (typeof parsed === 'object' && parsed.content) {
              dataModules.starWorkflowData = parsed.content
            } else if (typeof parsed === 'string') {
              dataModules.starWorkflowData = parsed
            } else {
              dataModules.starWorkflowData = JSON.stringify(parsed)
            }
          } catch {
            // 如果不是JSON，直接使用
            dataModules.starWorkflowData = starWorkflowData
          }
        }

        // 2. jobAnalysisResult (岗位要求) - 确保是文本数据
        const jobAnalysisResult = localStorage.getItem('jobAnalysisResult')
        if (jobAnalysisResult) {
          try {
            const parsed = JSON.parse(jobAnalysisResult)
            if (typeof parsed === 'object' && parsed.content) {
              dataModules.jobAnalysisResult = parsed.content
            } else if (typeof parsed === 'string') {
              dataModules.jobAnalysisResult = parsed
            } else {
              dataModules.jobAnalysisResult = JSON.stringify(parsed)
            }
          } catch {
            dataModules.jobAnalysisResult = jobAnalysisResult
          }
        }

        // 3. originalWorkflowContent (简历能力项) - 确保是文本数据
        const originalWorkflowContent = localStorage.getItem('originalWorkflowContent')
        if (originalWorkflowContent) {
          try {
            const parsed = JSON.parse(originalWorkflowContent)
            if (typeof parsed === 'object' && parsed.content) {
              dataModules.originalWorkflowContent = parsed.content
            } else if (typeof parsed === 'string') {
              dataModules.originalWorkflowContent = parsed
            } else {
              dataModules.originalWorkflowContent = JSON.stringify(parsed)
            }
          } catch {
            dataModules.originalWorkflowContent = originalWorkflowContent
          }
        }

        // 4. jobResumeWorkflowResult (评估结果) - 确保是文本数据
        const jobResumeWorkflowResult = localStorage.getItem('jobResumeWorkflowResult')
        if (jobResumeWorkflowResult) {
          try {
            const parsed = JSON.parse(jobResumeWorkflowResult)
            if (typeof parsed === 'object' && parsed.content) {
              dataModules.jobResumeWorkflowResult = parsed.content
            } else if (typeof parsed === 'string') {
              dataModules.jobResumeWorkflowResult = parsed
            } else {
              dataModules.jobResumeWorkflowResult = JSON.stringify(parsed)
            }
          } catch {
            dataModules.jobResumeWorkflowResult = jobResumeWorkflowResult
          }
        }

        // 5. resumeUploadData (简历文本) - 确保是文本数据
        const resumeUploadData = localStorage.getItem('uploadResult')
        if (resumeUploadData) {
          try {
            const uploadResult = JSON.parse(resumeUploadData)
            if (uploadResult && uploadResult.text) {
              dataModules.resumeUploadData = uploadResult.text
            } else if (typeof uploadResult === 'string') {
              dataModules.resumeUploadData = uploadResult
            } else {
              dataModules.resumeUploadData = dataModules.originalWorkflowContent || '简历文本数据'
            }
          } catch {
            dataModules.resumeUploadData = resumeUploadData
          }
        } else {
          dataModules.resumeUploadData = dataModules.originalWorkflowContent || '简历文本数据'
        }

        console.log('收集到的数据模块:', {
          starWorkflowData: !!dataModules.starWorkflowData,
          jobAnalysisResult: !!dataModules.jobAnalysisResult,
          originalWorkflowContent: !!dataModules.originalWorkflowContent,
          jobResumeWorkflowResult: !!dataModules.jobResumeWorkflowResult,
          resumeUploadData: !!dataModules.resumeUploadData
        })

        return dataModules

      } catch (error) {
        console.error('收集数据模块失败:', error)
        return {}
      }
    },

    // 验证数据模块完整性
    validateDataModules(dataModules) {
      const requiredModules = [
        'starWorkflowData',
        'jobAnalysisResult',
        'originalWorkflowContent',
        'jobResumeWorkflowResult',
        'resumeUploadData'
      ]

      const missingModules = []

      for (const module of requiredModules) {
        if (!dataModules[module] || dataModules[module].trim() === '') {
          missingModules.push(module)
        }
      }

      return missingModules
    },

    // 调用 DeepSeek API 生成面试问题
    async generateInterviewQuestions(dataModules) {
      try {
        const response = await this.$axios.post('/deepseek/generate/interview-question', {
          job_position: this.jobInfo.jobName || '软件开发工程师',
          star_workflow_data: dataModules.starWorkflowData || '',
          job_analysis_result: dataModules.jobAnalysisResult || '',
          original_workflow_content: dataModules.originalWorkflowContent || '',
          job_resume_workflow_result: dataModules.jobResumeWorkflowResult || '',
          resume_upload_data: dataModules.resumeUploadData || ''
        })

        console.log('DeepSeek API 响应:', response.data)

        if (response.data && response.data.code === 0) {
          return response.data.data
        } else {
          throw new Error((response.data && response.data.msg) || '面试问题生成失败')
        }
      } catch (error) {
        console.error('调用 DeepSeek API 失败:', error)
        throw error
      }
    },

    // 跳转到深度面试页面
    navigateToDeepInterview(questions) {
      // 标记为深度面试模式
      localStorage.setItem('interviewMode', 'deep')

      this.$router.push({
        path: '/interview/immersive',
        query: {
          jobName: this.jobInfo.jobName,
          companyName: this.jobInfo.companyName,
          mode: 'deep',
          difficulty: 'advanced'
        }
      })
    },

    // 获取加载消息
    getLoadingMessage() {
      if (this.questionGenerationLoading) {
        return '正在生成深度面试问题...'
      } else if (this.deepInterviewLoading) {
        return this.deepInterviewLoadingMessage
      } else {
        return '基于5个数据模块的智能问题生成'
      }
    },



    // 导航到基础面试模式
    navigateToBasicInterview() {
      localStorage.setItem('interviewMode', 'basic') // 标记为基础面试模式

      this.$router.push({
        path: '/interview/immersive',
        query: {
          jobName: this.jobInfo.jobName,
          companyName: this.jobInfo.companyName,
          mode: 'comprehensive',
          difficulty: 'intermediate'
        }
      })
    },

    // 降级解析方法 - 简历分析
    fallbackParseOriginalContent() {
      try {
        // 首先尝试解析新格式的简历分析数据（用户提供的JSON格式）
        const newFormatMatch = this.originalContent.match(/项目体现的核心能力：\s*```json\s*([\s\S]*?)\s*```/);
        if (newFormatMatch) {
          const projectData = JSON.parse(newFormatMatch[1]);
          const result = { ...projectData };

          // 解析技能分类 - 新格式
          const skillsMarkdownMatch = this.originalContent.match(/### 标准化技能列表及分类\s*([\s\S]*?)(?=\n###|\n---|\n```|$)/);
          if (skillsMarkdownMatch) {
            const skillsText = skillsMarkdownMatch[1];
            const skills = this.parseSkillsFromNewMarkdown(skillsText);
            result.skills = skills;
          }

          return result;
        }

        // 尝试解析JSON格式的数据（原有格式）
        const jsonMatch = this.originalContent.match(/```json\s*([\s\S]*?)\s*```/);
        if (jsonMatch) {
          const jsonData = JSON.parse(jsonMatch[1]);
          return jsonData;
        }

        return null;
      } catch (e) {
        console.error('降级解析失败:', e);
        return null;
      }
    },



    fetchAnalysisData() {
      this.loading = true;
      this.error = null;
      
      // 从localStorage获取所有相关的分析结果
      try {
        // 获取岗位分析结果
        const jobAnalysisData = localStorage.getItem('jobAnalysisResult');
        
        // 获取职位推荐工作流数据
        const jobRecommendWorkflowData = localStorage.getItem('jobRecommendWorkflowData');
        
        // 获取上传的简历数据
        const uploadResultData = localStorage.getItem('uploadResult');
        
        // 获取AI生成的简历数据
        const aiGeneratedResumeData = localStorage.getItem('aiGeneratedResumeData');
        
        // 获取原始工作流内容
        const originalWorkflowContent = localStorage.getItem('originalWorkflowContent');

        // 获取STAR工作流分析结果
        const starWorkflowData = localStorage.getItem('starWorkflowData');

        console.log('获取到的数据源：', {
          jobAnalysisData: !!jobAnalysisData,
          jobRecommendWorkflowData: !!jobRecommendWorkflowData,
          uploadResultData: !!uploadResultData,
          aiGeneratedResumeData: !!aiGeneratedResumeData,
          originalWorkflowContent: !!originalWorkflowContent,
          starWorkflowData: !!starWorkflowData
        });
        
        // 合并所有分析数据
        const mergedData = {
          jobAnalysis: jobAnalysisData ? JSON.parse(jobAnalysisData) : null,
          jobRecommendWorkflow: jobRecommendWorkflowData ? JSON.parse(jobRecommendWorkflowData) : null,
          uploadResult: uploadResultData ? JSON.parse(uploadResultData) : null,
          aiGeneratedResume: aiGeneratedResumeData ? JSON.parse(aiGeneratedResumeData) : null,
          originalContent: originalWorkflowContent,
          starWorkflow: starWorkflowData ? JSON.parse(starWorkflowData) : null
        };
        
        console.log('合并后的分析数据:', mergedData);
        
        // 设置分析数据
        if (mergedData.jobAnalysis || mergedData.resumeWorkflow || mergedData.jobRecommendWorkflow || mergedData.originalContent || mergedData.starWorkflow) {
          this.analysisData = mergedData;
          this.loading = false;
        }
      } catch (e) {
        console.error('解析存储的分析数据失败:', e);
        this.error = '无法加载分析数据，请重试';
        this.loading = false;
      }
    },
    
    
    getMatchColor(match) {
      if (match >= 0.8) return 'success';
      if (match >= 0.6) return 'info';
      if (match >= 0.4) return 'warning';
      return 'error';
    },
    
    getTipColor(index) {
      const colors = ['primary', 'success', 'info', 'warning', 'error'];
      return colors[index % colors.length];
    },

    reloadOriginalContent() {
      try {
        const content = localStorage.getItem('originalWorkflowContent');
        console.log('localStorage中的原始内容:', content ? content.substring(0, 500) : 'null');

        if (content) {
          // 如果analysisData不存在，创建一个新对象
          if (!this.analysisData) {
            this.analysisData = {};
          }
          this.analysisData.originalContent = content;

          // 强制重新计算
          this.$forceUpdate();

          this.$store.dispatch('snackbar/showMessage', {
            message: '简历分析数据加载成功',
            color: 'success'
          });
        } else {
          this.$store.dispatch('snackbar/showMessage', {
            message: '无法加载简历分析数据，localStorage中不存在相关数据',
            color: 'error'
          });
        }
      } catch (e) {
        console.error('重新加载简历分析数据失败:', e);
        this.$store.dispatch('snackbar/showMessage', {
          message: '简历分析数据加载失败，请重试',
          color: 'error'
        });
      }
    },

    // 保留一个简化的技能解析方法供降级使用
    parseSkillsFromNewMarkdown(skillsText) {
      const skills = {};
      const lines = skillsText.split('\n');
      let currentCategory = null;

      lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('#### ')) {
          currentCategory = line.replace('#### ', '');
          skills[currentCategory] = [];
        } else if (line.startsWith('- ') && currentCategory) {
          const skill = line.replace('- ', '');
          if (skill) {
            skills[currentCategory].push(skill);
          }
        }
      });

      return skills;
    },

    // 获取能力图标
    getCompetencyIcon(competency) {
      const iconMap = {
        '技术实践能力': 'mdi-code-tags',
        '问题解决能力': 'mdi-puzzle',
        '项目管理能力': 'mdi-clipboard-check',
        '沟通能力': 'mdi-account-voice',
        '团队协作': 'mdi-account-group',
        '学习能力': 'mdi-school'
      };
      return iconMap[competency] || 'mdi-star';
    },

    // 获取能力颜色
    getCompetencyColor(index) {
      const colors = ['primary', 'success', 'info', 'warning', 'error', 'purple'];
      return colors[index % colors.length];
    },

    // 获取技能分类图标
    getSkillCategoryIcon(category) {
      const iconMap = {
        '编程语言': 'mdi-code-braces',
        '框架': 'mdi-cube-outline',
        '工具': 'mdi-tools',
        '软技能': 'mdi-account-heart',
        '数据库': 'mdi-database',
        '云服务': 'mdi-cloud'
      };
      return iconMap[category] || 'mdi-tag';
    },

    // 获取技能分类颜色
    getSkillCategoryColor(category) {
      const colorMap = {
        '编程语言': 'primary',
        '框架': 'success',
        '工具': 'info',
        '软技能': 'warning',
        '数据库': 'error',
        '云服务': 'purple'
      };
      return colorMap[category] || 'grey';
    },

    // 获取STAR标题
    getStarTitle(key) {
      const titleMap = {
        'situation': 'Situation (情境)',
        'task': 'Task (任务)',
        'action': 'Action (行动)',
        'result': 'Result (结果)'
      };
      return titleMap[key] || key;
    },

    // 获取STAR图标
    getStarIcon(key) {
      const iconMap = {
        'situation': 'mdi-map-marker',
        'task': 'mdi-clipboard-list',
        'action': 'mdi-run',
        'result': 'mdi-trophy'
      };
      return iconMap[key] || 'mdi-star';
    },

    // 获取STAR颜色
    getStarColor(key) {
      const colorMap = {
        'situation': 'primary',
        'task': 'success',
        'action': 'info',
        'result': 'warning'
      };
      return colorMap[key] || 'grey';
    },

    // 格式化STAR内容
    formatStarContent(content) {
      if (!content) return '';

      // 确保content是字符串类型
      if (typeof content !== 'string') {
        content = String(content);
      }

      return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
    },

    // 获取需求分类图标
    getRequirementCategoryIcon(category) {
      const iconMap = {
        '技术要求': 'mdi-code-tags',
        '软技能要求': 'mdi-account-heart',
        '经验要求': 'mdi-briefcase',
        '学历要求': 'mdi-school',
        '语言要求': 'mdi-translate'
      };
      return iconMap[category] || 'mdi-check-circle';
    },

    // 获取需求分类颜色
    getRequirementCategoryColor(category) {
      const colorMap = {
        '技术要求': 'primary',
        '软技能要求': 'success',
        '经验要求': 'info',
        '学历要求': 'warning',
        '语言要求': 'purple'
      };
      return colorMap[category] || 'grey';
    },

    // 获取重要性图标
    getImportanceIcon(importance) {
      const iconMap = {
        '高': 'mdi-alert-circle',
        '中': 'mdi-information',
        '低': 'mdi-minus-circle'
      };
      return iconMap[importance] || 'mdi-help-circle';
    },

    // 获取重要性颜色
    getImportanceColor(importance) {
      const colorMap = {
        '高': 'error',
        '中': 'warning',
        '低': 'success'
      };
      return colorMap[importance] || 'grey';
    },

    // 获取技术深度标签
    getTechnicalDepthLabel(depth) {
      const labelMap = {
        'low': '基础',
        'medium': '中等',
        'high': '高级'
      };
      return labelMap[depth] || '中等';
    },

    // 获取技术深度颜色
    getTechnicalDepthColor(depth) {
      const colorMap = {
        'low': 'success',
        'medium': 'warning',
        'high': 'error'
      };
      return colorMap[depth] || 'warning';
    },

    // 获取技术深度图标
    getTechnicalDepthIcon(depth) {
      const iconMap = {
        'low': 'mdi-circle',
        'medium': 'mdi-circle-double',
        'high': 'mdi-circle-triple'
      };
      return iconMap[depth] || 'mdi-circle-double';
    },

    // 获取指标变化颜色
    getMetricChangeColor(change) {
      if (!change || change === 'N/A') return 'grey';

      if (change.includes('+') || change.includes('增') || change.includes('提升')) {
        return 'success';
      } else if (change.includes('-') || change.includes('降') || change.includes('减少')) {
        return 'error';
      }

      return 'info';
    },

    // 获取指标变化图标
    getMetricChangeIcon(change) {
      if (!change || change === 'N/A') return 'mdi-minus';

      if (change.includes('+') || change.includes('增') || change.includes('提升')) {
        return 'mdi-trending-up';
      } else if (change.includes('-') || change.includes('降') || change.includes('减少')) {
        return 'mdi-trending-down';
      }

      return 'mdi-trending-neutral';
    },

    // 检查是否包含需补充标记
    hasNeedsSupplement(text) {
      if (!text) return false;
      return text.includes('[需补充]');
    },

    // 刷新岗位分析数据
    refreshJobAnalysis() {
      // 强制重新计算
      this.$forceUpdate();

      this.$store.dispatch('snackbar/showMessage', {
        content: '岗位分析数据已刷新',
        color: 'info'
      });
    },

    // 刷新STAR分析数据
    refreshStarAnalysis() {
      // 强制重新计算
      this.$forceUpdate();

      this.$store.dispatch('snackbar/showMessage', {
        content: 'STAR分析数据已刷新',
        color: 'info'
      });
    },



    getStarAnalysisContent(starWorkflowData) {
      // 从STAR工作流数据中提取分析内容
      if (!starWorkflowData) return null;

      // 如果有data.choices数组，从第一个choice的delta.content中获取内容
      if (starWorkflowData.data && starWorkflowData.data.choices && starWorkflowData.data.choices.length > 0) {
        const choice = starWorkflowData.data.choices[0];
        if (choice.delta && choice.delta.content) {
          return choice.delta.content;
        }
      }

      // 如果有choices数组，从第一个choice的delta.content中获取内容
      if (starWorkflowData.choices && starWorkflowData.choices.length > 0) {
        const choice = starWorkflowData.choices[0];
        if (choice.delta && choice.delta.content) {
          return choice.delta.content;
        }
      }

      // 兼容旧的数据结构
      if (starWorkflowData.star_analysis) {
        return starWorkflowData.star_analysis;
      }

      // 如果是字符串类型，直接返回
      if (typeof starWorkflowData === 'string') {
        return starWorkflowData;
      }

      return null;
    },



    async callStarWorkflow() {
      // 调用STAR工作流API
      this.starLoading = true;

      try {
        // 获取简历文本内容
        const originalContent = localStorage.getItem('originalWorkflowContent');
        if (!originalContent) {
          this.$store.dispatch('snackbar/showMessage', {
            message: '未找到简历内容，请先上传简历',
            color: 'error'
          });
          return;
        }

        console.log('开始调用STAR工作流API，文本长度:', originalContent.length);



        if (response.data.code === 0) {
          // 保存STAR分析结果到localStorage
          localStorage.setItem('starWorkflowData', JSON.stringify(response.data));

          // 更新当前分析数据
          if (!this.analysisData) {
            this.analysisData = {};
          }
          this.analysisData.starWorkflow = response.data;

          this.$store.dispatch('snackbar/showMessage', {
            message: 'STAR分析完成',
            color: 'success'
          });

          console.log('STAR工作流分析成功:', response.data);
        } else {
          throw new Error(response.data.message || 'STAR分析失败');
        }
      } catch (error) {
        console.error('STAR工作流调用失败:', error);
        this.$store.dispatch('snackbar/showMessage', {
          message: `STAR分析失败: ${error.message || error}`,
          color: 'error'
        });
      } finally {
        this.starLoading = false;
      }
    },

    // 格式化时间显示
    formatTime(seconds) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }
  },
  created() {
    // 从URL查询参数获取岗位信息
    const query = this.$route.query;
    if (query.jobId) {
      this.jobInfo = {
        jobId: query.jobId,
        jobName: query.jobName || '未知职位',
        companyName: query.companyName || '未知公司',
        city: query.city || '未知',
        salary: query.salary || '未知',
        experience: query.experience || '未知',
        education: query.education || '未知'
      };
    }

    // 获取分析数据
    this.fetchAnalysisData();
  },

  beforeDestroy() {
    // 清理深度面试等待定时器
    this.stopDeepInterviewCountdown();
    console.log('InterviewAnalysis组件销毁时已清理定时器');
  }
};
</script>

<style scoped>
.interview-analysis-container {
  padding: 20px 0;
}

.analysis-content {
  min-height: 400px;
}

.analysis-report {
  line-height: 1.6;
  white-space: pre-line;
}

.skills-match {
  max-width: 600px;
  margin: 0 auto;
}

.interview-tips {
  max-width: 800px;
  margin: 0 auto;
}

.original-content {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  font-family: monospace;
  max-height: 600px;
  overflow-y: auto;
}

.original-content pre {
  margin: 0;
}

/* 简历分析样式 */
.resume-analysis {
  max-width: 100%;
}

.skill-category {
  margin-bottom: 16px;
}

.skill-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.requirement-category {
  margin-bottom: 16px;
}

.priority-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 岗位分析样式 */
.job-analysis-data {
  max-width: 100%;
}

.original-content-wrapper,
.original-data-wrapper {
  max-width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .skill-chips {
    justify-content: center;
  }

  .priority-items {
    justify-content: center;
  }
}

/* 深色样式覆盖 */
:deep(.v-tabs-slider) {
  background-color: var(--v-primary-base) !important;
}

:deep(.v-tab--active) {
  color: var(--v-primary-base) !important;
}

/* 卡片样式增强 */
:deep(.v-card--outlined) {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

/* 列表项样式 */
:deep(.v-list-item__title) {
  line-height: 1.4;
}

:deep(.v-list-item__subtitle) {
  line-height: 1.3;
  opacity: 0.7;
}

/* 时间线样式 */
:deep(.v-timeline-item__body) {
  padding-left: 16px;
}

/* 芯片样式 */
:deep(.v-chip--outlined) {
  border-width: 1px;
}

/* STAR项目样式 */
.star-projects .metric-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.star-projects .metric-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.star-projects .metric-values {
  min-width: 0;
}

.star-projects .metric-change {
  flex-shrink: 0;
}

/* 量化指标概览样式 */
.star-projects .v-card.success.lighten-5 {
  border-left: 4px solid #4caf50;
}

/* 需补充标记高亮 */
.star-projects .text-body-2:has-text([需补充]) {
  background: rgba(255, 193, 7, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  border-left: 3px solid #ffc107;
}

/* 时间线样式优化 */
.star-projects .v-timeline-item .v-timeline-item__body {
  padding-bottom: 16px;
}

:deep(.v-chip--small) {
  font-size: 12px;
}

/* 禁用当前页面的卡片悬浮效果 */
.interview-analysis-container :deep(.v-card:hover) {
  transform: none !important;
  box-shadow: inherit !important;
}

/* STAR项目展示样式 */
.star-projects {
  max-width: 100%;
}

.star-projects .v-card {
  transition: all 0.3s ease;
}

.star-projects .v-card:hover {
  transform: none !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12) !important;
}

/* 时间线样式增强 */
:deep(.v-timeline-item__body) {
  padding-left: 24px;
  padding-bottom: 16px;
}

:deep(.v-timeline-item__divider) {
  min-width: 40px;
}

/* 项目卡片样式 */
.star-projects :deep(.v-card-title) {
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.star-projects :deep(.v-chip) {
  font-size: 11px;
  height: 24px;
}

/* 简历分析项目样式 */
.resume-analysis :deep(.v-card-title) {
  background: linear-gradient(45deg, #f5f5f5, #fafafa);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.resume-analysis :deep(.v-list-item__subtitle) {
  line-height: 1.4;
  margin-top: 4px;
}
</style> 