<template>
  <div class="saved-reports">
    <v-container>
      <div class="d-flex align-center mb-6">
        <v-icon left color="primary" size="32">mdi-folder-multiple</v-icon>
        <h1 class="text-h4 font-weight-bold text--primary">我的面试报告</h1>
      </div>

      <!-- 统计信息 -->
      <v-row class="mb-6">
        <v-col cols="12" md="3">
          <v-card class="text-center pa-4" color="primary" dark>
            <v-icon size="48" class="mb-2">mdi-file-document-multiple</v-icon>
            <div class="text-h4 font-weight-bold">{{ stats.total_reports || 0 }}</div>
            <div class="text-subtitle-1">总报告数</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="9">
          <v-card class="pa-4">
            <div class="text-h6 mb-3">报告类型分布</div>
            <v-chip-group>
              <v-chip
                v-for="stat in stats.type_stats"
                :key="stat.type"
                color="accent"
                text-color="white"
                small
              >
                {{ getReportTypeName(stat.type) }}: {{ stat.count }}
              </v-chip>
            </v-chip-group>
          </v-card>
        </v-col>
      </v-row>

      <!-- 报告列表 -->
      <v-card>
        <v-card-title>
          <v-icon left>mdi-format-list-bulleted</v-icon>
          报告列表
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="refreshReports">
            <v-icon left>mdi-refresh</v-icon>
            刷新
          </v-btn>
        </v-card-title>

        <v-data-table
          :headers="headers"
          :items="reports"
          :loading="loading"
          :server-items-length="pagination.total"
          :options.sync="options"
          @update:options="loadReports"
          class="elevation-0"
        >
          <template v-slot:item.title="{ item }">
            <div class="font-weight-medium">{{ item.title }}</div>
          </template>

          <template v-slot:item.report_type="{ item }">
            <v-chip small color="info" text-color="white">
              {{ getReportTypeName(item.report_type) }}
            </v-chip>
          </template>

          <template v-slot:item.created_at="{ item }">
            <div class="text-caption">{{ formatDate(item.created_at) }}</div>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="viewReport(item)" color="primary">
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn icon small @click="downloadReport(item)" color="success">
              <v-icon>mdi-download</v-icon>
            </v-btn>
            <v-btn icon small @click="deleteReport(item)" color="error">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card>

      <!-- 删除确认对话框 -->
      <v-dialog v-model="deleteDialog" max-width="400">
        <v-card>
          <v-card-title>确认删除</v-card-title>
          <v-card-text>
            确定要删除报告"{{ selectedReport?.title }}"吗？此操作不可撤销。
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="deleteDialog = false">取消</v-btn>
            <v-btn color="error" @click="confirmDelete">删除</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { getInterviewReportList, getInterviewReportStats, deleteInterviewReport } from '@/api/interviewReport'

export default {
  name: 'SavedReports',
  data() {
    return {
      reports: [],
      stats: {},
      loading: false,
      deleteDialog: false,
      selectedReport: null,
      pagination: {
        total: 0,
        page: 1,
        per_page: 10
      },
      options: {},
      headers: [
        { text: '报告标题', value: 'title', sortable: false },
        { text: '类型', value: 'report_type', sortable: false },
        { text: '创建时间', value: 'created_at', sortable: true },
        { text: '操作', value: 'actions', sortable: false, width: '150px' }
      ]
    }
  },
  
  async created() {
    await this.loadStats()
    await this.loadReports()
  },

  methods: {
    async loadStats() {
      try {
        const response = await getInterviewReportStats()
        if (response.success) {
          this.stats = response.data
        }
      } catch (error) {
        console.error('加载统计信息失败:', error)
      }
    },

    async loadReports() {
      this.loading = true
      try {
        const params = {
          page: this.options.page || 1,
          per_page: this.options.itemsPerPage || 10
        }
        
        const response = await getInterviewReportList(params)
        if (response.success) {
          this.reports = response.data.reports
          this.pagination = response.data.pagination
        }
      } catch (error) {
        console.error('加载报告列表失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '加载报告列表失败',
          color: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    async refreshReports() {
      await this.loadStats()
      await this.loadReports()
    },

    viewReport(report) {
      // 跳转到报告详情页，使用保存的数据
      this.$router.push({
        name: 'InterviewReport',
        params: { id: 'saved' },
        query: { reportId: report.id }
      })
    },

    downloadReport(report) {
      try {
        const dataStr = JSON.stringify(report, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `${report.title}.json`
        link.click()
        
        this.$store.dispatch('snackbar/showMessage', {
          message: '报告下载成功',
          color: 'success'
        })
      } catch (error) {
        console.error('下载报告失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '下载报告失败',
          color: 'error'
        })
      }
    },

    deleteReport(report) {
      this.selectedReport = report
      this.deleteDialog = true
    },

    async confirmDelete() {
      try {
        const response = await deleteInterviewReport(this.selectedReport.id)
        if (response.success) {
          this.$store.dispatch('snackbar/showMessage', {
            message: '报告删除成功',
            color: 'success'
          })
          await this.refreshReports()
        }
      } catch (error) {
        console.error('删除报告失败:', error)
        this.$store.dispatch('snackbar/showMessage', {
          message: '删除报告失败',
          color: 'error'
        })
      } finally {
        this.deleteDialog = false
        this.selectedReport = null
      }
    },

    getReportTypeName(type) {
      const typeMap = {
        'comprehensive_interview_analysis': '综合面试分析',
        'star_analysis': 'STAR分析',
        'resume_analysis': '简历分析',
        'job_analysis': '岗位分析'
      }
      return typeMap[type] || type
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
    }
  }
}
</script>

<style scoped>
.saved-reports {
  padding: 20px 0;
}
</style>
