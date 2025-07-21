<template>
  <div class="interview-report">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-6 gradient-text">
            <v-icon large color="accent" class="mr-2">mdi-file-chart</v-icon>
            面试报告
          </h1>
        </v-col>
      </v-row>
      
      <div v-if="loading" class="text-center py-5">
        <v-progress-circular indeterminate color="accent" size="64"></v-progress-circular>
        <div class="mt-3 text--primary">加载面试报告中...</div>
      </div>
      
      <!-- 分析报告模式 -->
      <template v-else-if="showAnalysisReport">
        <!-- 面试分析报告标题 -->
        <v-card class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="accent">mdi-chart-line</v-icon>
            AI面试分析报告
          </v-card-title>
          <v-card-text>
            <div class="text-body-1 info--text">
              基于您的简历、岗位要求和面试表现的综合分析报告
            </div>
          </v-card-text>
        </v-card>

        <!-- 面试表现分析 -->
        <v-card v-if="parsedAnalysisData.interviewAnalysis" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="success">mdi-account-star</v-icon>
            面试表现评估
          </v-card-title>
          <v-card-text>
            <div v-if="parsedAnalysisData.interviewAnalysis.评估">
              <v-row>
                <v-col cols="12" md="6">
                  <div class="text-center mb-4">
                    <v-progress-circular
                      :rotate="-90"
                      :size="120"
                      :width="12"
                      :value="parsedAnalysisData.interviewAnalysis.评估.overall_score * 10"
                      :color="getScoreColor(parsedAnalysisData.interviewAnalysis.评估.overall_score * 10)"
                      class="score-circle"
                    >
                      <div class="text-h5 text--primary">{{ parsedAnalysisData.interviewAnalysis.评估.overall_score }}</div>
                      <div class="caption info--text">总分</div>
                    </v-progress-circular>
                  </div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="subtitle-1 font-weight-bold mb-3 text--primary">各维度评分</div>
                  <div v-for="(score, dimension) in getInterviewScores()" :key="dimension" class="mb-2">
                    <div class="d-flex align-center">
                      <div class="mr-3 info--text" style="min-width: 100px;">{{ dimension }}</div>
                      <v-progress-linear
                        :value="score * 10"
                        height="8"
                        rounded
                        :color="getScoreColor(score * 10)"
                        class="flex-grow-1 score-progress"
                      ></v-progress-linear>
                      <div class="ml-3 font-weight-medium text--primary">{{ score }}</div>
                    </div>
                  </div>
                </v-col>
              </v-row>

              <!-- 改进建议 -->
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">改进建议</div>
              <v-list class="transparent-list">
                <v-list-item
                  v-for="(suggestion, index) in parsedAnalysisData.interviewAnalysis.评估.improvement_suggestions"
                  :key="index"
                  class="transparent-list-item"
                >
                  <v-list-item-icon>
                    <v-icon color="warning">mdi-lightbulb-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title class="text--primary">{{ suggestion }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>
        </v-card>

        <!-- STAR分析结果 -->
        <v-card v-if="parsedAnalysisData.starAnalysis" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="orange">mdi-star</v-icon>
            STAR项目分析
          </v-card-title>
          <v-card-text>
            <div v-if="parsedAnalysisData.starAnalysis.projects">
              <v-expansion-panels dark class="custom-panels">
                <v-expansion-panel
                  v-for="(project, index) in parsedAnalysisData.starAnalysis.projects"
                  :key="index"
                  class="custom-panel"
                >
                  <v-expansion-panel-header class="panel-header">
                    <div class="d-flex align-center">
                      <div class="mr-4 orange--text">项目 {{ index + 1 }}</div>
                      <div class="flex-grow-1 text--primary">{{ project.name || '项目分析' }}</div>
                      <v-chip
                        small
                        :color="project.missing_elements && project.missing_elements.length > 0 ? 'warning' : 'success'"
                        text-color="white"
                        class="ml-2"
                      >
                        {{ project.missing_elements && project.missing_elements.length > 0 ? '需完善' : '完整' }}
                      </v-chip>
                    </div>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content class="panel-content">
                    <v-row>
                      <v-col cols="12" md="6">
                        <div class="subtitle-2 font-weight-bold mb-2 text--primary">Situation (情境)</div>
                        <div class="body-2 pa-3 rounded-lg answer-box mb-3">
                          {{ project.situation || '未提供' }}
                        </div>

                        <div class="subtitle-2 font-weight-bold mb-2 text--primary">Task (任务)</div>
                        <div class="body-2 pa-3 rounded-lg answer-box">
                          {{ project.task || '未提供' }}
                        </div>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="subtitle-2 font-weight-bold mb-2 text--primary">Action (行动)</div>
                        <div class="body-2 pa-3 rounded-lg feedback-box mb-3">
                          {{ project.action || '未提供' }}
                        </div>

                        <div class="subtitle-2 font-weight-bold mb-2 text--primary">Result (结果)</div>
                        <div class="body-2 pa-3 rounded-lg reference-box">
                          {{ project.result || '未提供' }}
                        </div>
                      </v-col>
                    </v-row>

                    <v-divider class="my-3 divider-light"></v-divider>

                    <div v-if="project.missing_elements && project.missing_elements.length > 0">
                      <div class="subtitle-2 font-weight-bold mb-2 warning--text">需要完善的要素</div>
                      <v-chip-group>
                        <v-chip
                          v-for="element in project.missing_elements"
                          :key="element"
                          small
                          color="warning"
                          text-color="white"
                        >
                          {{ element }}
                        </v-chip>
                      </v-chip-group>
                    </div>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </v-card-text>
        </v-card>

        <!-- 简历分析结果 -->
        <v-card v-if="parsedAnalysisData.resumeAnalysis" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="primary">mdi-file-document-outline</v-icon>
            简历能力分析
          </v-card-title>
          <v-card-text>
            <!-- 项目核心能力 -->
            <div v-if="parsedAnalysisData.resumeAnalysis.projects">
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">项目核心能力</div>
              <v-row>
                <v-col
                  v-for="(project, index) in parsedAnalysisData.resumeAnalysis.projects"
                  :key="index"
                  cols="12" md="6"
                >
                  <v-card flat class="transparent-card mb-3">
                    <v-card-text class="pa-3">
                      <div class="font-weight-medium primary--text mb-2">{{ project.project_name || `项目 ${index + 1}` }}</div>
                      <div v-if="project.core_competencies">
                        <v-chip-group>
                          <v-chip
                            v-for="competency in project.core_competencies"
                            :key="competency"
                            small
                            color="primary"
                            text-color="white"
                          >
                            {{ competency }}
                          </v-chip>
                        </v-chip-group>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <!-- 技能分类 -->
            <div v-if="parsedAnalysisData.resumeAnalysis.skills">
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">技能分类</div>
              <v-row>
                <v-col
                  v-for="(skillList, category) in parsedAnalysisData.resumeAnalysis.skills"
                  :key="category"
                  cols="12" md="6"
                >
                  <v-card flat class="transparent-card mb-3">
                    <v-card-text class="pa-3">
                      <div class="font-weight-medium success--text mb-2">{{ category }}</div>
                      <v-chip-group>
                        <v-chip
                          v-for="skill in skillList"
                          :key="skill"
                          small
                          color="success"
                          text-color="white"
                        >
                          {{ skill }}
                        </v-chip>
                      </v-chip-group>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- 岗位匹配分析 -->
        <v-card v-if="parsedAnalysisData.jobAnalysis" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="info">mdi-briefcase-check</v-icon>
            岗位匹配分析
          </v-card-title>
          <v-card-text>
            <!-- JD 关键要素 -->
            <div v-if="parsedAnalysisData.jobAnalysis.jobDescription">
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">岗位关键要素</div>

              <!-- 核心职责 -->
              <div v-if="parsedAnalysisData.jobAnalysis.jobDescription.coreResponsibilities" class="mb-4">
                <div class="subtitle-2 font-weight-bold mb-2 primary--text">核心职责</div>
                <v-list class="transparent-list">
                  <v-list-item
                    v-for="(responsibility, index) in parsedAnalysisData.jobAnalysis.jobDescription.coreResponsibilities"
                    :key="index"
                    class="transparent-list-item"
                  >
                    <v-list-item-icon>
                      <v-icon color="primary">mdi-check-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title class="text--primary">{{ responsibility }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>

              <!-- 必备技能 -->
              <div v-if="parsedAnalysisData.jobAnalysis.jobDescription.requiredSkills" class="mb-4">
                <div class="subtitle-2 font-weight-bold mb-2 success--text">必备技能与要求</div>
                <v-row>
                  <!-- 技术要求 -->
                  <v-col cols="12" md="6" v-if="parsedAnalysisData.jobAnalysis.jobDescription.requiredSkills.技术要求">
                    <div class="body-2 font-weight-bold mb-2">技术要求</div>
                    <v-chip-group>
                      <v-chip
                        v-for="skill in parsedAnalysisData.jobAnalysis.jobDescription.requiredSkills.技术要求"
                        :key="skill"
                        small
                        color="success"
                        text-color="white"
                      >
                        {{ skill }}
                      </v-chip>
                    </v-chip-group>
                  </v-col>

                  <!-- 软技能要求 -->
                  <v-col cols="12" md="6" v-if="parsedAnalysisData.jobAnalysis.jobDescription.requiredSkills.软技能要求">
                    <div class="body-2 font-weight-bold mb-2">软技能要求</div>
                    <v-chip-group>
                      <v-chip
                        v-for="skill in parsedAnalysisData.jobAnalysis.jobDescription.requiredSkills.软技能要求"
                        :key="skill"
                        small
                        color="info"
                        text-color="white"
                      >
                        {{ skill }}
                      </v-chip>
                    </v-chip-group>
                  </v-col>
                </v-row>
              </div>

              <!-- 优先考虑项 -->
              <div v-if="parsedAnalysisData.jobAnalysis.jobDescription.preferredQualifications" class="mb-4">
                <div class="subtitle-2 font-weight-bold mb-2 warning--text">优先考虑项</div>
                <v-chip-group>
                  <v-chip
                    v-for="qualification in parsedAnalysisData.jobAnalysis.jobDescription.preferredQualifications"
                    :key="qualification"
                    small
                    color="warning"
                    text-color="white"
                  >
                    {{ qualification }}
                  </v-chip>
                </v-chip-group>
              </div>
            </div>

            <!-- 能力维度映射 -->
            <div v-if="parsedAnalysisData.jobAnalysis.competencyMapping" class="mt-4">
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">能力维度重要性分析</div>
              <v-row>
                <v-col
                  v-for="(competency, index) in parsedAnalysisData.jobAnalysis.competencyMapping"
                  :key="index"
                  cols="12"
                  md="6"
                >
                  <v-card class="pa-3 mb-2" outlined>
                    <div class="d-flex align-center mb-2">
                      <div class="subtitle-2 font-weight-bold flex-grow-1">{{ competency.competency }}</div>
                      <v-chip
                        small
                        :color="getImportanceColor(competency.importance)"
                        text-color="white"
                      >
                        {{ competency.importance }}
                      </v-chip>
                    </div>
                    <div class="body-2 text--secondary">{{ competency.justification }}</div>
                  </v-card>
                </v-col>
              </v-row>
            </div>

            <!-- 能力差距分析 -->
            <div v-if="parsedAnalysisData.jobAnalysis.gapAnalysis" class="mt-4">
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">能力差距评估</div>
              <v-alert
                :type="parsedAnalysisData.jobAnalysis.gapAnalysis.gap_exists ? 'warning' : 'success'"
                outlined
                class="mb-4"
              >
                <div class="font-weight-medium">
                  {{ parsedAnalysisData.jobAnalysis.gapAnalysis.gap_exists ? '存在能力差距' : '能力匹配良好' }}
                </div>
                <div v-if="parsedAnalysisData.jobAnalysis.gapAnalysis.reasons" class="mt-2">
                  <div class="caption">具体原因：</div>
                  <ul class="mt-1">
                    <li v-for="reason in parsedAnalysisData.jobAnalysis.gapAnalysis.reasons" :key="reason">
                      {{ reason }}
                    </li>
                  </ul>
                </div>
                <div class="mt-2">
                  <v-chip
                    small
                    :color="getRiskLevelColor(parsedAnalysisData.jobAnalysis.gapAnalysis.risk_level)"
                    text-color="white"
                  >
                    风险等级: {{ parsedAnalysisData.jobAnalysis.gapAnalysis.risk_level }}
                  </v-chip>
                </div>
              </v-alert>
            </div>

            <!-- 技能匹配判断 -->
            <div v-if="parsedAnalysisData.jobAnalysis.skillsVerdict">
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">技能匹配判断</div>
              <v-alert
                :type="parsedAnalysisData.jobAnalysis.skillsVerdict.verdict ? 'success' : 'error'"
                outlined
              >
                <div class="font-weight-medium">
                  {{ parsedAnalysisData.jobAnalysis.skillsVerdict.verdict ? '技能符合岗位要求' : '技能不完全符合岗位要求' }}
                </div>
                <div v-if="parsedAnalysisData.jobAnalysis.skillsVerdict.reason" class="mt-2">
                  <div class="caption">原因：</div>
                  <div>{{ parsedAnalysisData.jobAnalysis.skillsVerdict.reason }}</div>
                </div>
                <div v-if="parsedAnalysisData.jobAnalysis.skillsVerdict.relation_type" class="mt-2">
                  <v-chip
                    small
                    color="info"
                    text-color="white"
                  >
                    关系类型: {{ parsedAnalysisData.jobAnalysis.skillsVerdict.relation_type }}
                  </v-chip>
                </div>
              </v-alert>
            </div>
          </v-card-text>
        </v-card>

        <!-- 岗位简历匹配结果 -->
        <v-card v-if="parsedAnalysisData.jobResumeMatch" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="purple">mdi-account-check</v-icon>
            岗位简历匹配度分析
          </v-card-title>
          <v-card-text>
            <!-- 能力维度潜在不足分析 -->
            <div v-if="parsedAnalysisData.jobResumeMatch.gapAnalysis">
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">能力维度潜在不足</div>
              <v-alert
                :type="parsedAnalysisData.jobResumeMatch.gapAnalysis.gapExists ? 'warning' : 'success'"
                outlined
                class="mb-4"
              >
                <div class="font-weight-medium">
                  {{ parsedAnalysisData.jobResumeMatch.gapAnalysis.gapExists ? '存在能力差距' : '能力匹配良好' }}
                </div>
                <div v-if="parsedAnalysisData.jobResumeMatch.gapAnalysis.reasons && parsedAnalysisData.jobResumeMatch.gapAnalysis.reasons.length > 0" class="mt-2">
                  <div class="caption">具体原因：</div>
                  <ul class="mt-1">
                    <li v-for="reason in parsedAnalysisData.jobResumeMatch.gapAnalysis.reasons" :key="reason">
                      {{ reason }}
                    </li>
                  </ul>
                </div>
                <div class="mt-2 d-flex align-center">
                  <v-chip
                    small
                    :color="getRiskLevelColor(parsedAnalysisData.jobResumeMatch.gapAnalysis.riskLevel)"
                    text-color="white"
                    class="mr-2"
                  >
                    风险等级: {{ parsedAnalysisData.jobResumeMatch.gapAnalysis.riskLevel }}
                  </v-chip>
                  <v-chip
                    small
                    color="info"
                    text-color="white"
                  >
                    证据质量: {{ parsedAnalysisData.jobResumeMatch.gapAnalysis.evidenceQuality }}
                  </v-chip>
                </div>
              </v-alert>
            </div>

            <!-- 技能匹配判断 -->
            <div v-if="parsedAnalysisData.jobResumeMatch.skillsVerdict">
              <div class="subtitle-1 font-weight-bold mb-3 text--primary">技能匹配判断</div>
              <v-alert
                :type="parsedAnalysisData.jobResumeMatch.skillsVerdict.verdict ? 'success' : 'error'"
                outlined
                class="mb-4"
              >
                <div class="font-weight-medium">
                  {{ parsedAnalysisData.jobResumeMatch.skillsVerdict.verdict ? '技能符合岗位要求' : '技能不完全符合岗位要求' }}
                </div>
                <div v-if="parsedAnalysisData.jobResumeMatch.skillsVerdict.reason" class="mt-2">
                  <div class="caption">原因：</div>
                  <div>{{ parsedAnalysisData.jobResumeMatch.skillsVerdict.reason }}</div>
                </div>
                <div class="mt-2 d-flex align-center">
                  <v-chip
                    small
                    color="info"
                    text-color="white"
                    class="mr-2"
                  >
                    关系类型: {{ parsedAnalysisData.jobResumeMatch.skillsVerdict.relationType }}
                  </v-chip>
                  <v-chip
                    v-if="parsedAnalysisData.jobResumeMatch.skillsVerdict.depthGap"
                    small
                    color="warning"
                    text-color="white"
                  >
                    深度差距: {{ parsedAnalysisData.jobResumeMatch.skillsVerdict.depthGap }}
                  </v-chip>
                </div>
              </v-alert>
            </div>

            <!-- 兼容旧格式 - 匹配度评分 -->
            <div v-if="parsedAnalysisData.jobResumeMatch.matchScore !== undefined">
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="text-center mb-4">
                <v-progress-circular
                  :rotate="-90"
                  :size="120"
                  :width="12"
                  :value="parsedAnalysisData.jobResumeMatch.matchScore"
                  :color="getScoreColor(parsedAnalysisData.jobResumeMatch.matchScore)"
                  class="score-circle"
                >
                  <div class="text-h5 text--primary">{{ parsedAnalysisData.jobResumeMatch.matchScore }}%</div>
                  <div class="caption info--text">匹配度</div>
                </v-progress-circular>
              </div>
            </div>

            <!-- 兼容旧格式 - 技能匹配 -->
            <v-row v-if="parsedAnalysisData.jobResumeMatch.matchedSkills || parsedAnalysisData.jobResumeMatch.unmatchedSkills">
              <!-- 匹配的技能 -->
              <v-col cols="12" md="6" v-if="parsedAnalysisData.jobResumeMatch.matchedSkills">
                <div class="subtitle-2 font-weight-bold mb-2 success--text">匹配技能</div>
                <v-chip-group>
                  <v-chip
                    v-for="skill in parsedAnalysisData.jobResumeMatch.matchedSkills"
                    :key="skill"
                    small
                    color="success"
                    text-color="white"
                  >
                    {{ skill }}
                  </v-chip>
                </v-chip-group>
              </v-col>

              <!-- 不匹配的技能 -->
              <v-col cols="12" md="6" v-if="parsedAnalysisData.jobResumeMatch.unmatchedSkills">
                <div class="subtitle-2 font-weight-bold mb-2 warning--text">待提升技能</div>
                <v-chip-group>
                  <v-chip
                    v-for="skill in parsedAnalysisData.jobResumeMatch.unmatchedSkills"
                    :key="skill"
                    small
                    color="warning"
                    text-color="white"
                  >
                    {{ skill }}
                  </v-chip>
                </v-chip-group>
              </v-col>
            </v-row>

            <!-- 兼容旧格式 - 改进建议 -->
            <div v-if="parsedAnalysisData.jobResumeMatch.suggestions" class="mt-4">
              <v-divider class="my-4 divider-light"></v-divider>
              <div class="subtitle-2 font-weight-bold mb-3 text--primary">改进建议</div>
              <v-list class="transparent-list">
                <v-list-item
                  v-for="(suggestion, index) in parsedAnalysisData.jobResumeMatch.suggestions"
                  :key="index"
                  class="transparent-list-item"
                >
                  <v-list-item-icon>
                    <v-icon color="info">mdi-lightbulb-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title class="text--primary">{{ suggestion }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>
        </v-card>

        <!-- 增强的面试分析 -->
        <v-card v-if="parsedAnalysisData.interviewAnalysis && parsedAnalysisData.interviewAnalysis.questions" class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="deep-purple">mdi-message-question</v-icon>
            详细面试分析
          </v-card-title>
          <v-card-text>
            <!-- 总体统计 -->
            <div class="mb-4">
              <v-row>
                <v-col cols="12" md="4" class="text-center">
                  <div class="text-h4 primary--text">{{ parsedAnalysisData.interviewAnalysis.totalQuestions }}</div>
                  <div class="caption info--text">问题总数</div>
                </v-col>
                <v-col cols="12" md="4" class="text-center">
                  <div class="text-h4 success--text">{{ parsedAnalysisData.interviewAnalysis.summary.averageScore }}</div>
                  <div class="caption info--text">平均分</div>
                </v-col>
                <v-col cols="12" md="4" class="text-center">
                  <div class="text-h4 info--text">{{ parsedAnalysisData.interviewAnalysis.summary.strengths.length }}</div>
                  <div class="caption info--text">优势项</div>
                </v-col>
              </v-row>
            </div>

            <!-- 改进建议总结 -->
            <div v-if="parsedAnalysisData.interviewAnalysis.summary.suggestions && parsedAnalysisData.interviewAnalysis.summary.suggestions.length > 0" class="mb-4">
              <div class="subtitle-2 font-weight-bold mb-2 warning--text">主要改进建议</div>
              <v-list class="transparent-list">
                <v-list-item
                  v-for="(suggestion, index) in parsedAnalysisData.interviewAnalysis.summary.suggestions"
                  :key="index"
                  class="transparent-list-item"
                >
                  <v-list-item-icon>
                    <v-icon color="warning">mdi-lightbulb-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title class="text--primary">{{ suggestion }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </div>

            <!-- 问题详情 -->
            <v-divider class="my-4 divider-light"></v-divider>
            <div class="subtitle-1 font-weight-bold mb-3 text--primary">问题详情</div>
            <v-expansion-panels dark class="custom-panels">
              <v-expansion-panel
                v-for="question in parsedAnalysisData.interviewAnalysis.questions"
                :key="question.index"
                class="custom-panel"
              >
                <v-expansion-panel-header class="panel-header">
                  <div class="d-flex align-center">
                    <div class="mr-4 deep-purple--text">问题 {{ question.index }}</div>
                    <div class="flex-grow-1 text--primary">{{ question.question.substring(0, 50) }}...</div>
                    <v-chip
                      small
                      :color="getScoreColor(question.analysis ? question.analysis.score : 0)"
                      text-color="white"
                      class="ml-2"
                    >
                      {{ question.analysis ? question.analysis.score : 0 }}分
                    </v-chip>
                  </div>
                </v-expansion-panel-header>
                <v-expansion-panel-content class="panel-content">
                  <div class="subtitle-2 font-weight-bold mb-2 white--text">问题</div>
                  <div class="body-2 pa-3 rounded-lg answer-box mb-3">
                    {{ question.question }}
                  </div>

                  <div class="subtitle-2 font-weight-bold mb-2 white--text">回答</div>
                  <div class="body-2 pa-3 rounded-lg feedback-box mb-3">
                    {{ question.answer }}
                  </div>

                  <div v-if="question.analysis" class="mt-3">
                    <!-- 评估详情 -->
                    <div v-if="question.analysis.assessmentDetails" class="mb-3">
                      <div class="subtitle-2 font-weight-bold mb-2 white--text">评估详情</div>
                      <v-row>
                        <v-col cols="12" md="6">
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 white--text" style="min-width: 120px;">专业性和技术准确性</div>
                            <v-progress-linear
                              :value="question.analysis.assessmentDetails.professionalismAndTechnicalAccuracy * 20"
                              height="8"
                              rounded
                              :color="getScoreColor(question.analysis.assessmentDetails.professionalismAndTechnicalAccuracy * 20)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ question.analysis.assessmentDetails.professionalismAndTechnicalAccuracy }}</div>
                          </div>
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 white--text" style="min-width: 120px;">逻辑清晰度和表达</div>
                            <v-progress-linear
                              :value="question.analysis.assessmentDetails.logicalClarityAndExpression * 20"
                              height="8"
                              rounded
                              :color="getScoreColor(question.analysis.assessmentDetails.logicalClarityAndExpression * 20)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ question.analysis.assessmentDetails.logicalClarityAndExpression }}</div>
                          </div>
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 white--text" style="min-width: 120px;">回复完整性</div>
                            <v-progress-linear
                              :value="question.analysis.assessmentDetails.completenessOfResponse * 20"
                              height="8"
                              rounded
                              :color="getScoreColor(question.analysis.assessmentDetails.completenessOfResponse * 20)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ question.analysis.assessmentDetails.completenessOfResponse }}</div>
                          </div>
                        </v-col>
                        <v-col cols="12" md="6">
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 white--text" style="min-width: 120px;">岗位匹配度</div>
                            <v-progress-linear
                              :value="question.analysis.assessmentDetails.jobFit * 20"
                              height="8"
                              rounded
                              :color="getScoreColor(question.analysis.assessmentDetails.jobFit * 20)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ question.analysis.assessmentDetails.jobFit }}</div>
                          </div>
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 white--text" style="min-width: 120px;">实践经验展示</div>
                            <v-progress-linear
                              :value="question.analysis.assessmentDetails.practicalExperienceDemonstration * 20"
                              height="8"
                              rounded
                              :color="getScoreColor(question.analysis.assessmentDetails.practicalExperienceDemonstration * 20)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ question.analysis.assessmentDetails.practicalExperienceDemonstration }}</div>
                          </div>
                        </v-col>
                      </v-row>
                    </div>

                    <!-- 改进建议 -->
                    <div v-if="question.analysis.suggestions && question.analysis.suggestions.length > 0" class="mt-3">
                      <div class="subtitle-2 font-weight-bold mb-2 white--text">改进建议</div>
                      <v-list class="transparent-list">
                        <v-list-item
                          v-for="(suggestion, index) in question.analysis.suggestions"
                          :key="index"
                          class="transparent-list-item"
                        >
                          <v-list-item-icon>
                            <v-icon color="warning">mdi-lightbulb-outline</v-icon>
                          </v-list-item-icon>
                          <v-list-item-content>
                            <v-list-item-title class="white--text">{{ suggestion }}</v-list-item-title>
                          </v-list-item-content>
                        </v-list-item>
                      </v-list>
                    </div>

                    <!-- 反馈信息（如果有） -->
                    <div v-if="question.analysis.feedback" class="mt-3">
                      <div class="subtitle-2 font-weight-bold mb-2 white--text">分析反馈</div>
                      <div class="body-2 pa-3 rounded-lg reference-box">
                        {{ question.analysis.feedback }}
                      </div>
                    </div>
                  </div>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>

        <!-- 操作按钮 -->
        <v-card elevation="0" class="custom-card">
          <v-card-text>
            <div class="text-center">
              <v-btn color="primary" to="/interview/home" class="action-btn mr-4" elevation="0">
                <v-icon left>mdi-home</v-icon>
                返回面试首页
              </v-btn>
              <v-btn color="primary" class="action-btn mr-4" @click="saveReportToDatabase" elevation="0">
                <v-icon left>mdi-content-save</v-icon>
                永久保存
              </v-btn>
              <v-btn color="success" class="action-btn mr-4" @click="exportReportAsJSON" elevation="0">
                <v-icon left>mdi-download</v-icon>
                导出JSON
              </v-btn>
              <v-btn color="info" class="action-btn mr-4" @click="exportReportAsPDF" elevation="0">
                <v-icon left>mdi-file-pdf-box</v-icon>
                导出PDF
              </v-btn>
              <v-btn color="warning" class="action-btn" @click="clearAnalysisData" elevation="0">
                <v-icon left>mdi-delete</v-icon>
                清除数据
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </template>

      <!-- 传统面试报告模式 -->
      <template v-else-if="report">
        <!-- 面试基本信息 -->
        <v-card class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="accent">mdi-information</v-icon>
            基本信息
          </v-card-title>
          
          <v-card-text class="pt-4">
            <v-row>
              <v-col cols="12" md="6">
                <v-list-item three-line class="transparent-list-item">
                  <v-list-item-avatar size="60" class="mr-4 company-avatar">
                    <v-img :src="getCompanyLogo(report.company_logo)"></v-img>
                  </v-list-item-avatar>
                  
                  <v-list-item-content>
                    <v-list-item-title class="text-h6 font-weight-bold white--text">
                      {{ report.position_name }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="mt-1 info--text">
                      <v-icon small class="mr-1">mdi-office-building</v-icon>
                      {{ report.company_name }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle class="info--text">
                      <v-icon small class="mr-1">mdi-map-marker</v-icon>
                      {{ report.city || '未知地区' }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-list two-line class="transparent-list">
                  <v-list-item class="transparent-list-item">
                    <v-list-item-icon>
                      <v-icon color="accent">mdi-calendar</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title class="white--text">面试时间</v-list-item-title>
                      <v-list-item-subtitle class="info--text">{{ formatDate(report.interview_time) }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  
                  <v-list-item class="transparent-list-item">
                    <v-list-item-icon>
                      <v-icon color="accent">mdi-timer</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title class="white--text">面试时长</v-list-item-title>
                      <v-list-item-subtitle class="info--text">{{ report.duration || 0 }}分钟</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  
                  <v-list-item class="transparent-list-item">
                    <v-list-item-icon>
                      <v-icon color="accent">mdi-help-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title class="white--text">问题数量</v-list-item-title>
                      <v-list-item-subtitle class="info--text">{{ report.questions ? report.questions.length : 0 }}题</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        
        <!-- 总体评分 -->
        <v-card class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="success">mdi-star</v-icon>
            总体评分
          </v-card-title>
          
          <v-card-text>
            <v-row align="center" justify="center" class="py-4">
              <v-col cols="12" sm="4" class="text-center">
                <v-progress-circular
                  :rotate="-90"
                  :size="150"
                  :width="15"
                  :value="report.score"
                  :color="getScoreColor(report.score)"
                  class="score-circle"
                >
                  <div class="text-h4 white--text">{{ report.score }}</div>
                  <div class="caption info--text">总分</div>
                </v-progress-circular>
                
                <div class="mt-3 text-subtitle-1 font-weight-medium gradient-text">
                  {{ getScoreLevel(report.score) }}
                </div>
              </v-col>
              
              <v-col cols="12" sm="8">
                <v-card flat class="transparent-card">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" sm="6" v-for="(item, index) in scoreBreakdown" :key="index">
                        <div class="d-flex align-center mb-2">
                          <div class="mr-3 info--text">{{ item.name }}</div>
                          <v-progress-linear
                            :value="item.score"
                            height="10"
                            rounded
                            :color="getScoreColor(item.score)"
                            class="flex-grow-1 score-progress"
                          ></v-progress-linear>
                          <div class="ml-3 font-weight-medium white--text">{{ item.score }}</div>
                        </div>
                      </v-col>
                    </v-row>
                    
                    <v-divider class="my-4 divider-light"></v-divider>
                    
                    <div class="font-weight-bold mb-2 white--text">面试官评语</div>
                    <div class="text-body-1 pa-3 rounded-lg comment-box">
                      {{ report.comment || '本次面试表现良好，继续保持！' }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        
        <!-- 问题详情 -->
        <v-card class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="primary">mdi-comment-question</v-icon>
            问题详情
          </v-card-title>
          
          <v-card-text class="pa-0">
            <v-expansion-panels dark class="custom-panels">
              <v-expansion-panel
                v-for="(question, index) in report.questions"
                :key="index"
                class="custom-panel"
              >
                <v-expansion-panel-header class="panel-header">
                  <div class="d-flex align-center">
                    <div class="mr-4 accent--text">问题 {{ index + 1 }}</div>
                    <div class="flex-grow-1 white--text">{{ question.content }}</div>
                    <v-chip
                      small
                      :color="getScoreColor(question.score)"
                      text-color="white"
                      class="ml-2 score-chip"
                    >
                      {{ question.score }}分
                    </v-chip>
                  </div>
                </v-expansion-panel-header>
                
                <v-expansion-panel-content class="panel-content">
                  <v-card flat class="transparent-card">
                    <v-card-text>
                      <div class="subtitle-1 font-weight-bold mb-2 white--text">您的回答</div>
                      <div class="body-1 pa-3 rounded-lg answer-box">
                        {{ question.answer || '未回答' }}
                      </div>
                      
                      <v-divider class="my-4 divider-light"></v-divider>
                      
                      <div class="subtitle-1 font-weight-bold mb-2 white--text">评分详情</div>
                      <v-row>
                        <v-col cols="12" sm="6" v-for="(criteria, i) in question.criteria || []" :key="i">
                          <div class="d-flex align-center mb-2">
                            <div class="mr-3 info--text">{{ criteria.name }}</div>
                            <v-progress-linear
                              :value="criteria.score"
                              height="8"
                              rounded
                              :color="getScoreColor(criteria.score)"
                              class="flex-grow-1 score-progress"
                            ></v-progress-linear>
                            <div class="ml-3 font-weight-medium white--text">{{ criteria.score }}</div>
                          </div>
                        </v-col>
                      </v-row>
                      
                      <v-divider class="my-4 divider-light"></v-divider>
                      
                      <div class="subtitle-1 font-weight-bold mb-2 white--text">点评</div>
                      <div class="body-1 pa-3 rounded-lg feedback-box">
                        {{ question.feedback || '无点评' }}
                      </div>
                      
                      <v-divider class="my-4 divider-light"></v-divider>
                      
                      <div class="subtitle-1 font-weight-bold mb-2 white--text">参考答案</div>
                      <div class="body-1 pa-3 rounded-lg reference-box">
                        {{ question.reference_answer || '暂无参考答案' }}
                      </div>
                    </v-card-text>
                  </v-card>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>
        
        <!-- 能力分析 -->
        <v-card class="mb-4 custom-card" elevation="0">
          <v-card-title class="card-title">
            <v-icon left color="primary">mdi-chart-arc</v-icon>
            能力分析
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <div class="text-center mb-4">
                  <div class="subtitle-1 font-weight-bold mb-4 white--text">能力雷达图</div>
                  <v-sheet height="300" class="d-flex justify-center radar-chart-container">
                    <!-- 这里可以使用图表库如Chart.js或Echarts绘制雷达图 -->
                    <div class="radar-chart-placeholder d-flex align-center justify-center">
                      <div class="text-center">
                        <v-icon size="64" color="accent">mdi-chart-areaspline</v-icon>
                        <div class="caption accent--text mt-2">能力雷达图</div>
                      </div>
                    </div>
                  </v-sheet>
                </div>
              </v-col>
              
              <v-col cols="12" md="6">
                <div class="subtitle-1 font-weight-bold mb-4 white--text">能力详情</div>
                <v-list class="transparent-list">
                  <v-list-item v-for="(ability, index) in abilities" :key="index" class="ability-item">
                    <v-list-item-icon>
                      <v-icon :color="getScoreColor(ability.score)">{{ ability.icon }}</v-icon>
                    </v-list-item-icon>
                    
                    <v-list-item-content>
                      <v-list-item-title class="white--text">{{ ability.name }}</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-progress-linear
                          :value="ability.score"
                          height="6"
                          rounded
                          :color="getScoreColor(ability.score)"
                          class="mt-1 ability-progress"
                        ></v-progress-linear>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                    
                    <v-list-item-action>
                      <div class="font-weight-medium white--text">{{ ability.score }}</div>
                    </v-list-item-action>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        
        <!-- 改进建议 -->
        <v-card elevation="0" class="custom-card">
          <v-card-title class="card-title">
            <v-icon left color="warning">mdi-lightbulb-on</v-icon>
            改进建议
          </v-card-title>
          
          <v-card-text>
            <v-timeline dense class="custom-timeline">
              <v-timeline-item
                v-for="(suggestion, index) in report.suggestions || defaultSuggestions"
                :key="index"
                small
                :color="getTimelineColor(index)"
                class="timeline-item"
              >
                <div class="font-weight-bold white--text">{{ suggestion.title }}</div>
                <div class="text-body-2 info--text">{{ suggestion.content }}</div>
              </v-timeline-item>
            </v-timeline>
            
            <v-divider class="my-4 divider-light"></v-divider>
            
            <div class="text-center">
              <v-btn color="accent" to="/interview/home" class="action-btn mr-4" elevation="0">
                <v-icon left>mdi-home</v-icon>
                返回面试首页
              </v-btn>
              <v-btn color="success" class="action-btn mr-4" :to="`/job/detail/${report.job_id}`" elevation="0">
                <v-icon left>mdi-briefcase</v-icon>
                查看职位详情
              </v-btn>
              <v-btn color="primary" class="action-btn" @click="retryInterview" elevation="0">
                <v-icon left>mdi-refresh</v-icon>
                重新面试
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </template>
      
      <v-alert
        v-else
        type="warning"
        outlined
        class="mt-4 custom-alert"
      >
        未找到面试报告数据，请确认面试ID是否正确。
        <div class="mt-4">
          <v-btn color="accent" to="/interview/home" class="action-btn" elevation="0">
            <v-icon left>mdi-arrow-left</v-icon>
            返回面试首页
          </v-btn>
        </div>
      </v-alert>
    </v-container>
  </div>
</template>

<script>
import { getInterviewReport } from '@/api/interview'
import { startInterview } from '@/api/interview'
import { analysisParser } from '@/utils/analysisParser'

export default {
  name: 'InterviewReport',
  data() {
    return {
      loading: true,
      report: null,
      // 新增：localStorage分析数据
      analysisData: {
        starWorkflowData: null,
        originalWorkflowContent: null,
        jobAnalysisResult: null,
        jobResumeWorkflowResult: null,
        interviewAnalyses: null
      },
      parsedAnalysisData: {
        starAnalysis: null,
        resumeAnalysis: null,
        jobAnalysis: null,
        jobResumeMatch: null,
        interviewAnalysis: null
      },
      showAnalysisReport: false, // 是否显示分析报告
      scoreBreakdown: [
        { name: '专业知识', score: 85 },
        { name: '沟通能力', score: 78 },
        { name: '逻辑思维', score: 82 },
        { name: '问题解决', score: 75 }
      ],
      abilities: [
        { name: '专业技能', score: 85, icon: 'mdi-code-tags' },
        { name: '沟通表达', score: 78, icon: 'mdi-account-voice' },
        { name: '逻辑思维', score: 82, icon: 'mdi-brain' },
        { name: '团队协作', score: 80, icon: 'mdi-account-group' },
        { name: '学习能力', score: 88, icon: 'mdi-book-open-page-variant' },
        { name: '抗压能力', score: 75, icon: 'mdi-weight-lifter' }
      ],
      defaultSuggestions: [
        {
          title: '加强专业知识',
          content: '建议深入学习相关技术领域的知识，提高专业技能水平。'
        },
        {
          title: '提升沟通表达',
          content: '在回答问题时注意表达的逻辑性和清晰度，避免过于啰嗦或简略。'
        },
        {
          title: '准备具体案例',
          content: '面试中准备更多具体的项目案例和数据，用事实说话更有说服力。'
        },
        {
          title: '关注行业动态',
          content: '多了解行业最新发展趋势和技术动向，展示自己的学习能力和视野。'
        }
      ]
    }
  },
  computed: {
    interviewId() {
      return this.$route.params.id
    }
  },
  created() {
    this.loadAnalysisData()
  },
  methods: {
    // 新增：加载分析数据
    async loadAnalysisData() {
      this.loading = true

      try {
        // 首先尝试从localStorage加载分析数据
        const hasAnalysisData = this.loadLocalStorageData()

        if (hasAnalysisData) {
          console.log('检测到localStorage分析数据，显示分析报告')
          this.showAnalysisReport = true
          this.parseAnalysisData()
        } else {
          console.log('未检测到localStorage分析数据，加载传统面试报告')
          this.showAnalysisReport = false
          await this.fetchInterviewReport()
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        // 降级到传统报告
        this.showAnalysisReport = false
        await this.fetchInterviewReport()
      } finally {
        this.loading = false
      }
    },

    // 新增：从localStorage加载数据
    loadLocalStorageData() {
      try {
        const starData = localStorage.getItem('starWorkflowData')
        const originalContent = localStorage.getItem('originalWorkflowContent')
        const jobAnalysis = localStorage.getItem('jobAnalysisResult')
        const jobResumeResult = localStorage.getItem('jobResumeWorkflowResult')
        const interviewAnalyses = localStorage.getItem('interviewAnalyses')

        console.log('localStorage数据检查:', {
          starData: !!starData,
          originalContent: !!originalContent,
          jobAnalysis: !!jobAnalysis,
          jobResumeResult: !!jobResumeResult,
          interviewAnalyses: !!interviewAnalyses
        })

        // 至少需要有一项数据才显示分析报告
        if (!starData && !originalContent && !jobAnalysis && !interviewAnalyses) {
          return false
        }

        // 解析并存储数据
        this.analysisData = {
          starWorkflowData: starData ? JSON.parse(starData) : null,
          originalWorkflowContent: originalContent || null,
          jobAnalysisResult: jobAnalysis || null,
          jobResumeWorkflowResult: jobResumeResult || null,
          interviewAnalyses: interviewAnalyses ? JSON.parse(interviewAnalyses) : null
        }

        return true
      } catch (error) {
        console.error('解析localStorage数据失败:', error)
        return false
      }
    },

    // 新增：解析分析数据
    parseAnalysisData() {
      try {
        // 解析STAR分析数据 - 参考 InterviewAnalysis.vue 的 getStarAnalysisContent 方法
        if (this.analysisData.starWorkflowData) {
          let starContent = this.getStarAnalysisContent(this.analysisData.starWorkflowData)
          if (starContent) {
            this.parsedAnalysisData.starAnalysis = analysisParser.parseStarAnalysis(starContent)
            console.log('STAR分析解析结果:', this.parsedAnalysisData.starAnalysis)
          }
        }

        // 解析简历分析数据 - 参考 InterviewAnalysis.vue 的 originalContent 计算属性
        if (this.analysisData.originalWorkflowContent) {
          let originalContent = this.getOriginalWorkflowContent(this.analysisData.originalWorkflowContent)
          if (originalContent) {
            this.parsedAnalysisData.resumeAnalysis = analysisParser.parseResumeAnalysis(originalContent)
            console.log('简历分析解析结果:', this.parsedAnalysisData.resumeAnalysis)
          }
        }

        // 解析岗位分析数据
        if (this.analysisData.jobAnalysisResult) {
          // 参考 InterviewAnalysis.vue 的处理方式
          let jobAnalysisContent = this.analysisData.jobAnalysisResult

          // 如果是字符串，尝试解析为 JSON
          if (typeof jobAnalysisContent === 'string') {
            try {
              const parsed = JSON.parse(jobAnalysisContent)
              if (typeof parsed === 'object' && parsed.data && parsed.data.choices && parsed.data.choices[0] && parsed.data.choices[0].delta && parsed.data.choices[0].delta.content) {
                // 处理 API 响应格式
                jobAnalysisContent = parsed.data.choices[0].delta.content
              } else if (typeof parsed === 'object' && parsed.content) {
                // 处理有 content 字段的格式
                jobAnalysisContent = parsed.content
              } else if (typeof parsed === 'string') {
                jobAnalysisContent = parsed
              } else {
                jobAnalysisContent = JSON.stringify(parsed)
              }
            } catch (e) {
              console.log('jobAnalysisResult JSON 解析失败，使用原始字符串:', e)
            }
          } else if (typeof jobAnalysisContent === 'object') {
            // 如果直接是对象，检查是否有嵌套的内容
            if (jobAnalysisContent.data && jobAnalysisContent.data.choices && jobAnalysisContent.data.choices[0] && jobAnalysisContent.data.choices[0].delta && jobAnalysisContent.data.choices[0].delta.content) {
              jobAnalysisContent = jobAnalysisContent.data.choices[0].delta.content
            } else if (jobAnalysisContent.content) {
              jobAnalysisContent = jobAnalysisContent.content
            } else {
              jobAnalysisContent = JSON.stringify(jobAnalysisContent)
            }
          }

          console.log('提取的岗位分析内容:', jobAnalysisContent.substring(0, 200) + '...')
          this.parsedAnalysisData.jobAnalysis = analysisParser.parseJobAnalysis(jobAnalysisContent)
          console.log('岗位分析解析结果:', this.parsedAnalysisData.jobAnalysis)
        }

        // 解析岗位简历匹配数据 - 参考 jobAnalysisResult 的处理方式
        if (this.analysisData.jobResumeWorkflowResult) {
          let jobResumeContent = this.analysisData.jobResumeWorkflowResult

          // 如果是字符串，尝试解析为 JSON
          if (typeof jobResumeContent === 'string') {
            try {
              const parsed = JSON.parse(jobResumeContent)
              if (typeof parsed === 'object' && parsed.data && parsed.data.choices && parsed.data.choices[0] && parsed.data.choices[0].delta && parsed.data.choices[0].delta.content) {
                // 处理 API 响应格式
                jobResumeContent = parsed.data.choices[0].delta.content
              } else if (typeof parsed === 'object' && parsed.content) {
                // 处理有 content 字段的格式
                jobResumeContent = parsed.content
              } else if (typeof parsed === 'string') {
                jobResumeContent = parsed
              } else {
                jobResumeContent = JSON.stringify(parsed)
              }
            } catch (e) {
              console.log('jobResumeWorkflowResult JSON 解析失败，使用原始字符串:', e)
            }
          } else if (typeof jobResumeContent === 'object') {
            // 如果直接是对象，检查是否有嵌套的内容
            if (jobResumeContent.data && jobResumeContent.data.choices && jobResumeContent.data.choices[0] && jobResumeContent.data.choices[0].delta && jobResumeContent.data.choices[0].delta.content) {
              jobResumeContent = jobResumeContent.data.choices[0].delta.content
            } else if (jobResumeContent.content) {
              jobResumeContent = jobResumeContent.content
            } else {
              jobResumeContent = JSON.stringify(jobResumeContent)
            }
          }

          console.log('提取的岗位简历匹配内容:', jobResumeContent.substring(0, 200) + '...')
          this.parsedAnalysisData.jobResumeMatch = analysisParser.parseJobResumeMatch(jobResumeContent)
          console.log('岗位简历匹配解析结果:', this.parsedAnalysisData.jobResumeMatch)
        }

        // 解析面试分析数据
        if (this.analysisData.interviewAnalyses) {
          this.parsedAnalysisData.interviewAnalysis = analysisParser.parseInterviewAnalyses(this.analysisData.interviewAnalyses)
          console.log('面试分析解析结果:', this.parsedAnalysisData.interviewAnalysis)
        }

      } catch (error) {
        console.error('解析分析数据失败:', error)
      }
    },

    // 新增：解析岗位分析数据
    parseJobAnalysisData(jobAnalysisText) {
      try {
        // 解析岗位简历匹配结果
        const gapMatch = jobAnalysisText.match(/评估能力维度潜在不足\s*```json\s*([\s\S]*?)\s*```/)
        const verdictMatch = jobAnalysisText.match(/严格判断简历技能是否符合岗位要求\s*```json\s*([\s\S]*?)\s*```/)

        const result = {}

        if (gapMatch) {
          try {
            result.gapAnalysis = JSON.parse(gapMatch[1])
          } catch (e) {
            console.error('解析能力差距分析失败:', e)
          }
        }

        if (verdictMatch) {
          try {
            result.skillsVerdict = JSON.parse(verdictMatch[1])
          } catch (e) {
            console.error('解析技能判断失败:', e)
          }
        }

        return Object.keys(result).length > 0 ? result : null
      } catch (error) {
        console.error('解析岗位分析数据失败:', error)
        return null
      }
    },

    async fetchInterviewReport() {
      this.loading = true
      try {
        const response = await getInterviewReport(this.interviewId)

        // 检查响应是否成功
        if (response.code === 0 && response.data) {
          this.report = response.data

          // 如果有评分细节，替换默认数据
          if (this.report && this.report.score_breakdown) {
            this.scoreBreakdown = this.report.score_breakdown
          }

          // 如果有能力评估，替换默认数据
          if (this.report && this.report.abilities) {
            this.abilities = this.report.abilities
          }
        } else {
          // API 返回错误或没有数据
          this.report = null
          console.log('面试报告不存在或获取失败:', response.msg || '未知错误')
        }
      } catch (error) {
        console.error('获取面试报告失败:', error)
        this.report = null
        this.$store.dispatch('snackbar/showMessage', {
          message: '获取面试报告失败，请稍后再试',
          color: 'error'
        })
      } finally {
        this.loading = false
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
    
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getScoreColor(score) {
      if (!score) return 'grey'
      if (score >= 90) return 'success'
      if (score >= 75) return 'primary'
      if (score >= 60) return 'warning'
      return 'error'
    },

    getImportanceColor(importance) {
      switch (importance) {
        case '高': return 'error'
        case '中': return 'warning'
        case '低': return 'info'
        default: return 'grey'
      }
    },

    getRiskLevelColor(riskLevel) {
      switch (riskLevel) {
        case 'high': return 'error'
        case 'medium': return 'warning'
        case 'low': return 'success'
        default: return 'grey'
      }
    },

    // 参考 InterviewAnalysis.vue 的 getStarAnalysisContent 方法
    getStarAnalysisContent(starWorkflowData) {
      if (!starWorkflowData) return null;

      // 如果是字符串，尝试解析为 JSON
      if (typeof starWorkflowData === 'string') {
        try {
          starWorkflowData = JSON.parse(starWorkflowData)
        } catch (e) {
          // 如果不是 JSON，直接返回字符串
          return starWorkflowData
        }
      }

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

    // 参考 InterviewAnalysis.vue 的 originalContent 计算属性
    getOriginalWorkflowContent(content) {
      if (!content) return null;

      // 如果是字符串，尝试解析为 JSON
      if (typeof content === 'string') {
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
      }

      // 如果是对象，检查是否有嵌套的内容
      if (typeof content === 'object') {
        if (content.choices && content.choices[0] && content.choices[0].delta && content.choices[0].delta.content) {
          return content.choices[0].delta.content;
        }
        if (content.content) {
          return content.content;
        }
        return JSON.stringify(content, null, 2);
      }

      return content;
    },
    
    getScoreLevel(score) {
      if (!score) return '未评分'
      if (score >= 90) return '优秀'
      if (score >= 80) return '良好'
      if (score >= 70) return '中等'
      if (score >= 60) return '及格'
      return '不及格'
    },
    
    getTimelineColor(index) {
      const colors = ['primary', 'success', 'info', 'warning', 'error', 'purple']
      return colors[index % colors.length]
    },

    // 新增：获取面试评分数据
    getInterviewScores() {
      if (!this.parsedAnalysisData.interviewAnalysis || !this.parsedAnalysisData.interviewAnalysis.评估) {
        return {}
      }

      const evaluation = this.parsedAnalysisData.interviewAnalysis.评估
      const scores = {}

      // 提取各维度评分
      if (evaluation.专业性和技术准确性) scores['专业性'] = evaluation.专业性和技术准确性
      if (evaluation.逻辑清晰度和表达) scores['逻辑表达'] = evaluation.逻辑清晰度和表达
      if (evaluation.回复完整性) scores['完整性'] = evaluation.回复完整性
      if (evaluation.岗位匹配度) scores['匹配度'] = evaluation.岗位匹配度
      if (evaluation.实践经验展示) scores['经验展示'] = evaluation.实践经验展示

      return scores
    },

    // 新增：获取风险等级颜色
    getRiskLevelColor(riskLevel) {
      switch (riskLevel) {
        case 'low': return 'success'
        case 'medium': return 'warning'
        case 'high': return 'error'
        default: return 'info'
      }
    },

    // 新增：清除分析数据
    clearAnalysisData() {
      this.$dialog.confirm({
        title: '确认清除',
        text: '确定要清除所有分析数据吗？此操作不可撤销。',
        confirmText: '确认清除',
        cancelText: '取消'
      }).then((confirmed) => {
        if (confirmed) {
          // 清除localStorage数据
          localStorage.removeItem('starWorkflowData')
          localStorage.removeItem('originalWorkflowContent')
          localStorage.removeItem('jobAnalysisResult')
          localStorage.removeItem('jobResumeWorkflowResult')
          localStorage.removeItem('interviewAnalyses')

          // 重置组件状态
          this.analysisData = {
            starWorkflowData: null,
            originalWorkflowContent: null,
            jobAnalysisResult: null,
            jobResumeWorkflowResult: null,
            interviewAnalyses: null
          }
          this.parsedAnalysisData = {
            starAnalysis: null,
            resumeAnalysis: null,
            jobAnalysis: null,
            jobResumeMatch: null,
            interviewAnalysis: null
          }
          this.showAnalysisReport = false

          this.$store.dispatch('snackbar/showMessage', {
            message: '分析数据已清除',
            color: 'success'
          })

          // 重新加载数据
          this.loadAnalysisData()
        }
      }).catch(() => {
        // 用户取消，不做任何操作
      })
    },

    // 导出JSON格式报告
    exportReportAsJSON() {
      try {
        const reportData = {
          timestamp: new Date().toISOString(),
          reportType: 'comprehensive_interview_analysis',
          analysisData: {
            starAnalysis: this.parsedAnalysisData.starAnalysis,
            resumeAnalysis: this.parsedAnalysisData.resumeAnalysis,
            jobAnalysis: this.parsedAnalysisData.jobAnalysis,
            jobResumeMatch: this.parsedAnalysisData.jobResumeMatch,
            interviewAnalysis: this.parsedAnalysisData.interviewAnalysis
          },
          rawData: {
            starWorkflowData: this.analysisData.starWorkflowData,
            originalWorkflowContent: this.analysisData.originalWorkflowContent,
            jobAnalysisResult: this.analysisData.jobAnalysisResult,
            jobResumeWorkflowResult: this.analysisData.jobResumeWorkflowResult,
            interviewAnalyses: this.analysisData.interviewAnalyses
          }
        }

        const dataStr = JSON.stringify(reportData, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })

        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `面试分析报告_${new Date().toISOString().split('T')[0]}.json`
        link.click()

        this.$store.dispatch('snackbar/showMessage', {
          message: 'JSON报告导出成功',
          color: 'success'
        })
      } catch (error) {
        console.error('导出JSON报告失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '导出JSON报告失败',
          color: 'error'
        })
      }
    },

    // 导出PDF格式报告
    exportReportAsPDF() {
      try {
        // 创建一个新窗口用于打印
        const printWindow = window.open('', '_blank')

        // 生成HTML内容
        const htmlContent = this.generatePrintableHTML()

        printWindow.document.write(htmlContent)
        printWindow.document.close()

        // 等待内容加载完成后打印
        printWindow.onload = () => {
          printWindow.print()
          printWindow.close()
        }

        this.$store.dispatch('snackbar/showMessage', {
          message: 'PDF报告生成中，请在打印对话框中选择"保存为PDF"',
          color: 'info'
        })
      } catch (error) {
        console.error('导出PDF报告失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '导出PDF报告失败',
          color: 'error'
        })
      }
    },

    // 永久保存报告到数据库
    async saveReportToDatabase() {
      try {
        const reportData = {
          reportType: 'comprehensive_interview_analysis',
          title: `面试分析报告_${new Date().toLocaleDateString('zh-CN')}`,
          analysisData: {
            starAnalysis: this.parsedAnalysisData.starAnalysis,
            resumeAnalysis: this.parsedAnalysisData.resumeAnalysis,
            jobAnalysis: this.parsedAnalysisData.jobAnalysis,
            jobResumeMatch: this.parsedAnalysisData.jobResumeMatch,
            interviewAnalysis: this.parsedAnalysisData.interviewAnalysis
          },
          rawData: {
            starWorkflowData: this.analysisData.starWorkflowData,
            originalWorkflowContent: this.analysisData.originalWorkflowContent,
            jobAnalysisResult: this.analysisData.jobAnalysisResult,
            jobResumeWorkflowResult: this.analysisData.jobResumeWorkflowResult,
            interviewAnalyses: this.analysisData.interviewAnalyses
          }
        }

        // 调用后端API保存报告
        const { saveInterviewReport } = await import('@/api/interviewReport')
        const response = await saveInterviewReport(reportData)

        if (response.success) {
          this.$store.dispatch('snackbar/showMessage', {
            message: `报告已永久保存！报告ID: ${response.data.report_id}`,
            color: 'success'
          })

          // 可选：跳转到报告详情页
          // this.$router.push(`/interview/saved-report/${response.data.report_id}`)
        } else {
          throw new Error(response.message || '保存失败')
        }
      } catch (error) {
        console.error('保存报告失败:', error)

        // 如果API调用失败，作为备份保存到localStorage
        try {
          const reportId = Date.now().toString()
          const backupData = {
            reportType: 'comprehensive_interview_analysis',
            timestamp: new Date().toISOString(),
            analysisData: this.parsedAnalysisData,
            rawData: this.analysisData
          }
          localStorage.setItem(`backup_report_${reportId}`, JSON.stringify(backupData))

          this.$store.dispatch('snackbar/showMessage', {
            message: '云端保存失败，已保存到本地备份',
            color: 'warning'
          })
        } catch (backupError) {
          this.$store.dispatch('snackbar/showMessage', {
            message: '保存报告失败',
            color: 'error'
          })
        }
      }
    },

    // 生成可打印的HTML内容
    generatePrintableHTML() {
      const currentDate = new Date().toLocaleDateString('zh-CN')
      const currentTime = new Date().toLocaleTimeString('zh-CN')

      let htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>面试分析报告</title>
          <style>
            body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
            .title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }
            .subtitle { font-size: 14px; color: #666; }
            .section { margin-bottom: 30px; page-break-inside: avoid; }
            .section-title { font-size: 18px; font-weight: bold; color: #333; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-bottom: 15px; }
            .subsection-title { font-size: 16px; font-weight: bold; color: #555; margin: 15px 0 10px 0; }
            .content { margin-left: 20px; }
            .score { font-weight: bold; color: #2196F3; }
            .list-item { margin: 5px 0; padding-left: 20px; }
            .star-section { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .assessment-item { display: flex; justify-content: space-between; margin: 8px 0; }
            .assessment-label { flex: 1; }
            .assessment-score { font-weight: bold; color: #2196F3; }
            @media print { body { margin: 0; } .section { page-break-inside: avoid; } }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="title">面试分析报告</div>
            <div class="subtitle">生成时间: ${currentDate} ${currentTime}</div>
          </div>
      `

      // 面试分析部分
      if (this.parsedAnalysisData.interviewAnalysis) {
        htmlContent += `
          <div class="section">
            <div class="section-title">面试分析总结</div>
            <div class="content">
              <div><strong>问题总数:</strong> ${this.parsedAnalysisData.interviewAnalysis.totalQuestions}</div>
              <div><strong>平均分:</strong> <span class="score">${this.parsedAnalysisData.interviewAnalysis.summary.averageScore}</span></div>
            </div>
        `

        if (this.parsedAnalysisData.interviewAnalysis.questions) {
          this.parsedAnalysisData.interviewAnalysis.questions.forEach((question, index) => {
            htmlContent += `
              <div class="subsection-title">问题 ${index + 1}</div>
              <div class="content">
                <div><strong>问题:</strong> ${question.question}</div>
                <div><strong>回答:</strong> ${question.answer}</div>
                <div><strong>得分:</strong> <span class="score">${question.analysis ? question.analysis.score : 0}</span></div>
              </div>
            `
          })
        }

        htmlContent += `</div>`
      }

      // STAR分析部分
      if (this.parsedAnalysisData.starAnalysis && this.parsedAnalysisData.starAnalysis.projects) {
        htmlContent += `
          <div class="section">
            <div class="section-title">STAR项目分析</div>
        `

        this.parsedAnalysisData.starAnalysis.projects.forEach((project, index) => {
          htmlContent += `
            <div class="star-section">
              <div class="subsection-title">项目 ${index + 1}: ${project.name || '项目分析'}</div>
              <div class="content">
                <div><strong>Situation (情境):</strong> ${project.situation || '未提供'}</div>
                <div><strong>Task (任务):</strong> ${project.task || '未提供'}</div>
                <div><strong>Action (行动):</strong> ${project.action || '未提供'}</div>
                <div><strong>Result (结果):</strong> ${project.result || '未提供'}</div>
              </div>
            </div>
          `
        })

        htmlContent += `</div>`
      }

      htmlContent += `
        </body>
        </html>
      `

      return htmlContent
    },

    async retryInterview() {
      if (!this.report || !this.report.job_id) {
        this.$store.dispatch('snackbar/showMessage', {
          message: '无法重新面试，缺少职位信息',
          color: 'error'
        })
        return
      }
      
      try {
        const response = await startInterview(this.report.job_id)
        const interviewId = response.data.interview_id
        this.$router.push(`/interview/process/${interviewId}`)
      } catch (error) {
        console.error('开始面试失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '开始面试失败，请稍后再试',
          color: 'error'
        })
      }
    }
  }
}
</script>

<style scoped>
.interview-report {
  padding: 20px 0;
}

.custom-card {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px !important;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.custom-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
}

.card-title {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 16px;
}

.transparent-card {
  background: transparent !important;
  box-shadow: none !important;
}

.transparent-list {
  background: transparent !important;
}

.transparent-list-item {
  background: transparent !important;
}

.company-avatar {
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.divider-light {
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.score-circle {
  filter: drop-shadow(0 0 10px rgba(76, 201, 240, 0.5));
}

.score-progress {
  height: 8px !important;
  border-radius: 4px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}

.score-chip {
  font-size: 0.75rem;
}

.comment-box {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #f8f9fa !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.custom-panels {
  background: transparent !important;
}

.custom-panel {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  margin-bottom: 8px;
  border-radius: 8px !important;
  overflow: hidden;
}

.panel-header {
  background: rgba(255, 255, 255, 0.05) !important;
}

.panel-content {
  background: rgba(0, 0, 0, 0.8) !important;
}

.answer-box {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #f8f9fa !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feedback-box {
  background: rgba(76, 201, 240, 0.1) !important;
  color: #f8f9fa !important;
  border: 1px solid rgba(76, 201, 240, 0.2);
}

.reference-box {
  background: rgba(72, 149, 239, 0.1) !important;
  color: #f8f9fa !important;
  border: 1px solid rgba(72, 149, 239, 0.2);
}

.radar-chart-container {
  background: transparent !important;
}

.radar-chart-placeholder {
  width: 100%;
  height: 100%;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.ability-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 0;
}

.ability-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.ability-progress {
  height: 8px !important;
  border-radius: 4px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
}

.custom-timeline {
  background: transparent !important;
}

.timeline-item {
  margin-bottom: 12px;
}

.action-btn {
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-3px);
}

.custom-alert {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #f8f9fa !important;
  border-color: #f72585 !important;
}
</style> 