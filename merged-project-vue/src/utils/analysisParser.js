/**
 * 分析数据解析工具
 * 支持多种AI生成格式的智能解析和美化显示
 */

/**
 * 简历分析数据解析器
 */
export class ResumeAnalysisParser {
  constructor() {
    // 项目核心能力的多种匹配模式
    this.projectPatterns = [
      // 模式1: 新格式 - 项目体现的核心能力
      /项目体现的核心能力：\s*```json\s*([\s\S]*?)\s*```/,
      // 模式2: 新格式 - 项目体现的核心能力（无冒号）
      /项目体现的核心能力\s*```json\s*([\s\S]*?)\s*```/,
      // 模式3: 标准JSON格式
      /```json\s*([\s\S]*?)\s*```/,
      // 模式4: 项目分析格式
      /项目分析[：:]\s*```json\s*([\s\S]*?)\s*```/,
      // 模式5: 核心能力格式
      /核心能力[：:]\s*```json\s*([\s\S]*?)\s*```/
    ];

    // 技能分类的多种匹配模式
    this.skillsPatterns = [
      // 模式1: 新格式 - 简历技能项JSON
      /简历技能项：\s*```json\s*([\s\S]*?)\s*```/,
      // 模式2: 新格式 - 简历技能项（无冒号）
      /简历技能项\s*```json\s*([\s\S]*?)\s*```/,
      // 模式3: 标准化技能列表
      /### 标准化技能列表及分类\s*([\s\S]*?)(?=\n###|\n---|\n```|$)/,
      // 模式4: 技能清单
      /## 技能清单\s*([\s\S]*?)(?=\n##|\n---|\n```|$)/,
      // 模式5: 技能分类
      /技能分类[：:]\s*([\s\S]*?)(?=\n##|\n---|\n```|$)/,
      // 模式6: 简历技能项 - 支持markdown包装
      /简历技能项[：:]\s*```markdown\s*([\s\S]*?)\s*```/,
      // 模式7: 简历技能项 - 直接格式
      /简历技能项[：:]\s*([\s\S]*?)(?=\n##|\n---|\n```|$)/
    ];
  }

  /**
   * 清理和预处理内容
   * @param {string} content - 原始内容
   * @returns {string} 清理后的内容
   */
  cleanContent(content) {
    if (!content) return content;

    // 移除可能的转义字符问题
    let cleaned = content;

    // 处理常见的转义字符问题
    cleaned = cleaned.replace(/\\n/g, '\n');
    cleaned = cleaned.replace(/\\"/g, '"');
    cleaned = cleaned.replace(/\\\\/g, '\\');

    // 移除可能的BOM字符
    cleaned = cleaned.replace(/^\uFEFF/, '');

    return cleaned;
  }

  /**
   * 解析简历分析内容
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析后的结构化数据
   */
  parse(content) {
    if (!content) return null;

    try {
      console.log('开始解析简历分析内容，长度:', content.length);
      
      // 尝试解析项目核心能力
      const projectData = this.parseProjectData(content);
      if (!projectData) {
        console.log('项目数据解析失败');
        return null;
      }

      // 尝试解析技能分类
      const skillsData = this.parseSkillsData(content);
      
      // 合并结果
      const result = { ...projectData };
      if (skillsData) {
        result.skills = skillsData;
      }

      console.log('简历分析解析成功:', result);
      return result;
    } catch (e) {
      console.error('简历分析解析失败:', e);
      return null;
    }
  }

  /**
   * 解析项目数据
   * @param {string} content - 原始内容
   * @returns {Object|null} 项目数据
   */
  parseProjectData(content) {
    // 清理内容
    const cleanedContent = this.cleanContent(content);

    // 尝试多种模式匹配
    for (const pattern of this.projectPatterns) {
      const match = cleanedContent.match(pattern);
      if (match) {
        try {
          // 进一步清理匹配到的JSON字符串
          let jsonString = match[1].trim();
          jsonString = this.cleanContent(jsonString);

          const jsonData = JSON.parse(jsonString);
          console.log('项目数据解析成功，使用模式:', pattern.source);

          // 验证新格式数据结构
          if (jsonData.projects && Array.isArray(jsonData.projects)) {
            console.log('检测到新格式项目数据，项目数量:', jsonData.projects.length);
            return jsonData;
          }

          // 兼容旧格式
          if (jsonData.project_name || jsonData.core_competencies) {
            console.log('检测到旧格式项目数据');
            return jsonData;
          }

          // 其他格式也返回
          return jsonData;
        } catch (e) {
          console.log('JSON解析失败，尝试下一个模式:', e.message);
          console.log('原始匹配内容前100字符:', match[1].substring(0, 100));
          continue;
        }
      }
    }

    // 如果所有模式都失败，尝试直接解析整个内容为JSON
    try {
      const directParsed = JSON.parse(this.cleanContent(content));
      if (directParsed.projects || directParsed.project_name) {
        console.log('直接JSON解析成功');
        return directParsed;
      }
    } catch (e) {
      console.log('直接JSON解析失败:', e.message);
    }

    return null;
  }

  /**
   * 解析技能数据
   * @param {string} content - 原始内容
   * @returns {Object|null} 技能数据
   */
  parseSkillsData(content) {
    // 尝试多种模式匹配
    for (const pattern of this.skillsPatterns) {
      const match = content.match(pattern);
      if (match) {
        const skillsText = match[1];

        // 尝试解析新格式的JSON技能数据
        if (pattern.source.includes('json')) {
          try {
            const jsonSkills = JSON.parse(skillsText);
            console.log('技能JSON数据解析成功，使用模式:', pattern.source);

            // 检查是否是新格式（包含standardized_skills）
            if (jsonSkills.standardized_skills) {
              console.log('检测到新格式技能数据');
              return this.parseNewSkillsFormat(jsonSkills);
            }

            // 兼容其他JSON格式
            return jsonSkills;
          } catch (e) {
            console.log('技能JSON解析失败，尝试Markdown解析:', e.message);
          }
        }

        // 尝试解析Markdown格式
        const skills = this.parseSkillsFromMarkdown(skillsText);
        if (skills && Object.keys(skills).length > 0) {
          console.log('技能数据解析成功，使用模式:', pattern.source);
          return skills;
        }
      }
    }

    return null;
  }

  /**
   * 从Markdown文本解析技能分类
   * @param {string} skillsText - 技能文本
   * @returns {Object} 技能分类对象
   */
  parseSkillsFromMarkdown(skillsText) {
    const skills = {};
    const lines = skillsText.split('\n');
    let currentCategory = null;

    lines.forEach(line => {
      line = line.trim();

      // 跳过空行和分隔符
      if (!line || line === '---' || line.startsWith('```')) {
        return;
      }

      // 匹配分类标题（支持多种格式）
      if (line.match(/^#{2,4}\s+/) || line.match(/^\*\*.*\*\*$/)) {
        currentCategory = line.replace(/^#{2,4}\s+/, '').replace(/^\*\*(.*)\*\*$/, '$1').trim();
        if (currentCategory) {
          skills[currentCategory] = [];
        }
      }
      // 匹配技能项目
      else if (line.startsWith('- ') && currentCategory) {
        const skill = line.replace('- ', '').trim();
        if (skill) {
          skills[currentCategory].push(skill);
        }
      }
      // 匹配其他格式的技能项目
      else if (line.match(/^[•·*]\s+/) && currentCategory) {
        const skill = line.replace(/^[•·*]\s+/, '').trim();
        if (skill) {
          skills[currentCategory].push(skill);
        }
      }
      // 匹配说明文本（跳过）
      else if (line.match(/^\d+\.\s+\*\*/) || line.startsWith('2. **优化建议**')) {
        // 跳过说明和建议部分
        return;
      }
    });

    return skills;
  }

  /**
   * 解析新格式的技能数据
   * @param {Object} skillsData - 包含standardized_skills和unmatched_skills的对象
   * @returns {Object} 处理后的技能数据
   */
  parseNewSkillsFormat(skillsData) {
    const result = {};

    // 处理标准化技能
    if (skillsData.standardized_skills) {
      console.log('处理标准化技能数据');
      Object.assign(result, skillsData.standardized_skills);
    }

    // 处理未匹配技能，将其添加到相应分类中
    if (skillsData.unmatched_skills && Array.isArray(skillsData.unmatched_skills)) {
      console.log('处理未匹配技能数据，数量:', skillsData.unmatched_skills.length);

      skillsData.unmatched_skills.forEach(skill => {
        if (skill.category && skill.standardized) {
          const category = skill.category;

          // 如果分类不存在，创建它
          if (!result[category]) {
            result[category] = [];
          }

          // 添加标准化后的技能名称
          if (!result[category].includes(skill.standardized)) {
            result[category].push(skill.standardized);
          }
        }
      });
    }

    console.log('新格式技能数据处理完成:', result);
    return result;
  }
}

/**
 * STAR分析数据解析器
 */
export class StarAnalysisParser {
  constructor() {
    // 新格式JSON匹配模式
    this.jsonPatterns = [
      // 模式1: STAR JSON格式
      /STAR\s*```json\s*([\s\S]*?)\s*```/,
      // 模式2: 直接JSON格式
      /```json\s*([\s\S]*?)\s*```/
    ];
  }

  /**
   * 清理和预处理内容
   * @param {string} content - 原始内容
   * @returns {string} 清理后的内容
   */
  cleanContent(content) {
    if (!content) return content;

    // 移除可能的转义字符问题
    let cleaned = content;

    // 处理常见的转义字符问题
    cleaned = cleaned.replace(/\\n/g, '\n');
    cleaned = cleaned.replace(/\\"/g, '"');
    cleaned = cleaned.replace(/\\\\/g, '\\');

    // 移除可能的BOM字符
    cleaned = cleaned.replace(/^\uFEFF/, '');

    return cleaned;
  }

  /**
   * 解析STAR分析内容
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析后的结构化数据
   */
  parse(content) {
    if (!content) return null;

    try {
      console.log('开始解析STAR分析内容，长度:', content.length);

      // 优先尝试解析新格式JSON
      const jsonResult = this.parseNewStarFormat(content);
      if (jsonResult) {
        console.log('新格式STAR分析解析成功');
        return jsonResult;
      }

      console.log('新格式解析失败');
      return null;
    } catch (e) {
      console.error('STAR分析解析失败:', e);
      return null;
    }
  }

  /**
   * 解析新格式STAR数据
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析后的数据
   */
  parseNewStarFormat(content) {
    // 清理内容
    const cleanedContent = this.cleanContent(content);

    // 尝试匹配JSON格式
    for (const pattern of this.jsonPatterns) {
      const match = cleanedContent.match(pattern);
      if (match) {
        try {
          // 进一步清理匹配到的JSON字符串
          let jsonString = match[1].trim();
          jsonString = this.cleanContent(jsonString);

          const jsonData = JSON.parse(jsonString);
          console.log('STAR JSON数据解析成功，使用模式:', pattern.source);

          // 验证新格式数据结构 - star_projects数组
          if (jsonData.star_projects && Array.isArray(jsonData.star_projects)) {
            console.log('检测到新格式STAR数据，项目数量:', jsonData.star_projects.length);
            return this.transformStarProjectsData(jsonData);
          }

          // 兼容旧格式
          if (jsonData.revised_description && jsonData.elements) {
            console.log('检测到旧格式STAR数据');
            return this.transformNewStarData(jsonData);
          }

          return jsonData;
        } catch (e) {
          console.log('STAR JSON解析失败，尝试下一个模式:', e.message);
          console.log('原始匹配内容前100字符:', match[1].substring(0, 100));
          continue;
        }
      }
    }

    // 如果所有模式都失败，尝试直接解析整个内容
    try {
      const directParsed = JSON.parse(this.cleanContent(content));
      if (directParsed.star_projects || directParsed.revised_description) {
        console.log('STAR直接JSON解析成功');
        return directParsed;
      }
    } catch (e) {
      console.log('STAR直接JSON解析失败:', e.message);
    }

    return null;
  }

  /**
   * 转换新格式STAR项目数据为显示格式
   * @param {Object} starData - 包含star_projects的数据
   * @returns {Object} 转换后的数据
   */
  transformStarProjectsData(starData) {
    const projects = starData.star_projects.map((project, index) => {
      return {
        name: '项目 ' + (index + 1),
        period: '',
        situation: project.situation || '',
        task: project.task || '',
        action: this.formatActionData(project.action),
        result: this.formatResultData(project.result),
        technical_depth: (project.action && project.action.technical_depth) || 'medium',
        quantified_metrics: (project.result && project.result.quantified) || [],
        qualitative_impact: (project.result && project.result.qualitative) || '',
        missing_elements: this.identifyMissingElements(project),
        improvement_suggestions: [],
        elements: {
          Situation: { text: project.situation, is_original: !this.hasNeedsSupplement(project.situation) },
          Task: { text: project.task, is_original: !this.hasNeedsSupplement(project.task) },
          Action: {
            text: this.formatActionData(project.action),
            is_original: !this.hasNeedsSupplement(this.formatActionData(project.action)),
            technical_depth: project.action && project.action.technical_depth
          },
          Result: {
            text: this.formatResultData(project.result),
            is_original: !this.hasNeedsSupplement(this.formatResultData(project.result)),
            is_quantified: project.result && project.result.quantified && project.result.quantified.length > 0,
            metrics: (project.result && project.result.quantified && project.result.quantified.map(q => q.metric + ': ' + q.change)) || []
          }
        }
      };
    });

    return { projects };
  }

  /**
   * 格式化Action数据
   * @param {Object} action - Action对象
   * @returns {string} 格式化后的文本
   */
  formatActionData(action) {
    if (!action) return '';

    let result = action.primary || '';

    if (action.supporting && Array.isArray(action.supporting)) {
      const supportingText = action.supporting.join('、');
      if (supportingText) {
        result += result ? '；辅助行动：' + supportingText : supportingText;
      }
    }

    return result;
  }

  /**
   * 格式化Result数据
   * @param {Object} result - Result对象
   * @returns {string} 格式化后的文本
   */
  formatResultData(result) {
    if (!result) return '';

    let resultText = '';

    // 添加量化结果
    if (result.quantified && Array.isArray(result.quantified)) {
      const quantifiedTexts = result.quantified.map(q => {
        if (q.change && q.change !== 'N/A') {
          return q.metric + q.change;
        } else if (q.after) {
          return q.metric + '达到' + q.after;
        }
        return q.metric + '：' + (q.after || '');
      });
      resultText = quantifiedTexts.join('，');
    }

    // 添加定性影响
    if (result.qualitative) {
      resultText += resultText ? '；' + result.qualitative : result.qualitative;
    }

    return resultText;
  }

  /**
   * 检查文本是否包含[需补充]标记
   * @param {string} text - 要检查的文本
   * @returns {boolean} 是否包含需补充标记
   */
  hasNeedsSupplement(text) {
    if (!text) return true;
    return text.includes('[需补充]');
  }

  /**
   * 识别缺失要素
   * @param {Object} project - 项目数据
   * @returns {Array} 缺失要素列表
   */
  identifyMissingElements(project) {
    const missing = [];

    if (!project.situation || this.hasNeedsSupplement(project.situation)) {
      missing.push('Situation');
    }
    if (!project.task || this.hasNeedsSupplement(project.task)) {
      missing.push('Task');
    }
    if (!project.action || !project.action.primary || this.hasNeedsSupplement(project.action.primary)) {
      missing.push('Action');
    }
    if (!project.result || (!project.result.quantified && !project.result.qualitative) ||
        this.hasNeedsSupplement(project.result.qualitative)) {
      missing.push('Result');
    }

    return missing;
  }

  /**
   * 解析量化指标数据
   * @param {Array} quantifiedArray - 量化指标数组
   * @returns {Array} 处理后的量化指标
   */
  parseQuantifiedResults(quantifiedArray) {
    if (!Array.isArray(quantifiedArray)) return [];

    return quantifiedArray.map(metric => {
      const processed = {
        metric: metric.metric || '',
        before: metric.before || '',
        after: metric.after || '',
        change: metric.change || '',
        hasBaseline: metric.before && !metric.before.includes('[需补充]'),
        isValid: metric.after && !metric.after.includes('[需补充]'),
        changeType: this.getChangeType(metric.change),
        displayValue: this.formatMetricDisplay(metric)
      };

      return processed;
    });
  }

  /**
   * 获取变化类型（增长/下降/无变化）
   * @param {string} change - 变化值
   * @returns {string} 变化类型
   */
  getChangeType(change) {
    if (!change || change === 'N/A') return 'none';

    if (change.includes('+') || change.includes('增') || change.includes('提升')) {
      return 'increase';
    } else if (change.includes('-') || change.includes('降') || change.includes('减少')) {
      return 'decrease';
    }

    return 'none';
  }

  /**
   * 格式化指标显示
   * @param {Object} metric - 指标对象
   * @returns {string} 格式化后的显示文本
   */
  formatMetricDisplay(metric) {
    if (metric.change && metric.change !== 'N/A') {
      return metric.metric + ': ' + metric.before + ' → ' + metric.after + ' (' + metric.change + ')';
    } else if (metric.after) {
      return metric.metric + ': ' + metric.after;
    }
    return metric.metric + ': ' + (metric.before || '');
  }

  /**
   * 获取技术深度标识
   * @param {string} depth - 技术深度级别
   * @returns {Object} 技术深度信息
   */
  getTechnicalDepthInfo(depth) {
    const depthMap = {
      'low': { label: '基础', color: 'success', icon: 'mdi-circle' },
      'medium': { label: '中等', color: 'warning', icon: 'mdi-circle-double' },
      'high': { label: '高级', color: 'error', icon: 'mdi-circle-triple' }
    };

    return depthMap[depth] || depthMap['medium'];
  }

  /**
   * 转换旧格式STAR数据为显示格式（兼容性方法）
   * @param {Object} starData - 旧格式STAR数据
   * @returns {Object} 转换后的数据
   */
  transformNewStarData(starData) {
    const elements = starData.elements || {};
    const project = {
      name: '项目STAR分析',
      period: '',
      situation: (elements.Situation && elements.Situation.text) || '',
      task: (elements.Task && elements.Task.text) || '',
      action: (elements.Action && elements.Action.text) || '',
      result: (elements.Result && elements.Result.text) || '',
      revised_description: starData.revised_description || '',
      missing_elements: starData.missing_elements || [],
      improvement_suggestions: starData.improvement_suggestions || [],
      elements: elements,
      technical_depth: 'medium',
      quantified_metrics: [],
      qualitative_impact: ''
    };

    return { projects: [project] };
  }
}

/**
 * 通用分析数据解析器
 */
export class AnalysisDataParser {
  constructor() {
    this.resumeParser = new ResumeAnalysisParser();
    this.starParser = new StarAnalysisParser();
  }

  /**
   * 解析简历分析数据
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析结果
   */
  parseResumeAnalysis(content) {
    return this.resumeParser.parse(content);
  }

  /**
   * 解析STAR分析数据
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析结果
   */
  parseStarAnalysis(content) {
    return this.starParser.parse(content);
  }

  /**
   * 解析岗位分析数据
   * @param {string} content - 文本内容
   * @returns {Object|null} 解析结果
   */
  parseJobAnalysis(content) {
    if (!content || typeof content !== 'string') return null;

    try {
      console.log('开始解析岗位分析内容，长度:', content.length);

      const result = {};

      // 解析 JD 关键要素
      const jdMatch = content.match(/JD关键要素\s*```json\s*([\s\S]*?)\s*```/);
      if (jdMatch) {
        try {
          const jdData = JSON.parse(jdMatch[1]);
          result.jobDescription = {
            coreResponsibilities: jdData.核心职责 || jdData.core_responsibilities || [],
            requiredSkills: jdData.必备技能与要求 || jdData.required_skills || {},
            preferredQualifications: jdData.优先考虑项 || jdData.preferred_qualifications || []
          };
          console.log('JD关键要素解析成功');
        } catch (e) {
          console.error('解析JD关键要素失败:', e);
        }
      }

      // 解析能力维度映射
      const competencyMatch = content.match(/能力维度映射\s*```json\s*([\s\S]*?)\s*```/);
      if (competencyMatch) {
        try {
          const competencyData = JSON.parse(competencyMatch[1]);
          result.competencyMapping = competencyData.map(item => ({
            competency: item.competency,
            importance: item.importance,
            justification: item.justification,
            importanceLevel: this.getImportanceLevel(item.importance)
          }));
          console.log('能力维度映射解析成功');
        } catch (e) {
          console.error('解析能力维度映射失败:', e);
        }
      }

      // 解析能力差距分析（如果存在）
      const gapMatch = content.match(/评估能力维度潜在不足\s*```json\s*([\s\S]*?)\s*```/);
      if (gapMatch) {
        try {
          result.gapAnalysis = JSON.parse(gapMatch[1]);
          console.log('能力差距分析解析成功');
        } catch (e) {
          console.error('解析能力差距分析失败:', e);
        }
      }

      // 解析技能判断（如果存在）
      const verdictMatch = content.match(/严格判断简历技能是否符合岗位要求\s*```json\s*([\s\S]*?)\s*```/);
      if (verdictMatch) {
        try {
          result.skillsVerdict = JSON.parse(verdictMatch[1]);
          console.log('技能判断解析成功');
        } catch (e) {
          console.error('解析技能判断失败:', e);
        }
      }

      console.log('岗位分析解析完成:', result);
      return Object.keys(result).length > 0 ? result : null;
    } catch (error) {
      console.error('岗位分析解析失败:', error);
      return null;
    }
  }

  /**
   * 获取重要性级别的数值
   * @param {string} importance - 重要性描述
   * @returns {number} 重要性级别 (1-3)
   */
  getImportanceLevel(importance) {
    switch (importance) {
      case '高': return 3;
      case '中': return 2;
      case '低': return 1;
      default: return 2;
    }
  }

  /**
   * 解析岗位简历匹配结果
   * @param {string} content - 原始内容
   * @returns {Object|null} 解析结果
   */
  parseJobResumeMatch(content) {
    if (!content) return null;

    try {
      console.log('开始解析岗位简历匹配内容，长度:', content.length);

      const result = {};

      // 解析能力维度潜在不足
      const gapMatch = content.match(/评估能力维度潜在不足\s*```json\s*([\s\S]*?)\s*```/);
      if (gapMatch) {
        try {
          const gapData = JSON.parse(gapMatch[1]);
          result.gapAnalysis = {
            gapExists: gapData.gap_exists,
            reasons: gapData.reasons || [],
            evidenceQuality: gapData.evidence_quality,
            riskLevel: gapData.risk_level
          };
          console.log('能力维度潜在不足解析成功');
        } catch (e) {
          console.error('解析能力维度潜在不足失败:', e);
        }
      }

      // 解析严格判断简历技能是否符合岗位要求
      const verdictMatch = content.match(/严格判断简历技能是否符合岗位要求\s*```json\s*([\s\S]*?)\s*```/);
      if (verdictMatch) {
        try {
          const verdictData = JSON.parse(verdictMatch[1]);
          result.skillsVerdict = {
            verdict: verdictData.verdict,
            reason: verdictData.reason,
            relationType: verdictData.relation_type,
            depthGap: verdictData.depth_gap
          };
          console.log('技能判断解析成功');
        } catch (e) {
          console.error('解析技能判断失败:', e);
        }
      }

      // 兼容旧格式 - 解析匹配度评分
      const scoreMatch = content.match(/匹配度[：:]?\s*(\d+(?:\.\d+)?)[%％]?/);
      if (scoreMatch) {
        result.matchScore = parseFloat(scoreMatch[1]);
        console.log('匹配度评分解析成功:', result.matchScore);
      }

      // 兼容旧格式 - 解析匹配的技能
      const matchedSkillsMatch = content.match(/匹配技能[：:]\s*([\s\S]*?)(?=\n##|\n不匹配|\n建议|$)/);
      if (matchedSkillsMatch) {
        result.matchedSkills = this.parseSkillsList(matchedSkillsMatch[1]);
        console.log('匹配技能解析成功');
      }

      // 兼容旧格式 - 解析不匹配的技能
      const unmatchedSkillsMatch = content.match(/不匹配技能[：:]\s*([\s\S]*?)(?=\n##|\n建议|$)/);
      if (unmatchedSkillsMatch) {
        result.unmatchedSkills = this.parseSkillsList(unmatchedSkillsMatch[1]);
        console.log('不匹配技能解析成功');
      }

      // 兼容旧格式 - 解析改进建议
      const suggestionsMatch = content.match(/建议[：:]\s*([\s\S]*?)(?=\n##|$)/);
      if (suggestionsMatch) {
        result.suggestions = this.parseSuggestionsList(suggestionsMatch[1]);
        console.log('改进建议解析成功');
      }

      console.log('岗位简历匹配解析完成:', result);
      return Object.keys(result).length > 0 ? result : null;
    } catch (error) {
      console.error('岗位简历匹配解析失败:', error);
      return null;
    }
  }

  /**
   * 解析面试分析数据
   * @param {Array} analyses - 面试分析数组
   * @returns {Object|null} 解析结果
   */
  parseInterviewAnalyses(analyses) {
    if (!analyses || !Array.isArray(analyses)) return null;

    try {
      console.log('开始解析面试分析数据，数量:', analyses.length);

      const result = {
        totalQuestions: analyses.length,
        questions: [],
        summary: {
          averageScore: 0,
          strengths: [],
          weaknesses: [],
          overallFeedback: ''
        }
      };

      let totalScore = 0;
      const allSuggestions = [];

      analyses.forEach((analysis, index) => {
        const questionData = {
          index: index + 1,
          question: analysis.question || '',
          answer: analysis.answer || '',
          timestamp: analysis.timestamp || '',
          sessionId: analysis.sessionId || '',
          questionIndex: analysis.questionIndex || 0,
          analysis: this.parseQuestionAnalysis(analysis.analysis)
        };

        if (questionData.analysis && questionData.analysis.score) {
          totalScore += questionData.analysis.score;
        }

        if (questionData.analysis && questionData.analysis.suggestions) {
          allSuggestions.push(...questionData.analysis.suggestions);
        }

        result.questions.push(questionData);
      });

      // 计算平均分
      result.summary.averageScore = analyses.length > 0 ? Math.round(totalScore / analyses.length) : 0;

      // 汇总改进建议
      result.summary.suggestions = [...new Set(allSuggestions)].slice(0, 8);

      console.log('面试分析解析完成:', result);
      return result;
    } catch (error) {
      console.error('面试分析解析失败:', error);
      return null;
    }
  }

  /**
   * 解析单个问题的分析结果
   * @param {Object|string} analysis - 分析结果
   * @returns {Object|null} 解析后的分析结果
   */
  parseQuestionAnalysis(analysis) {
    if (!analysis) return null;

    try {
      let analysisObj = analysis;

      // 如果是字符串，尝试解析为JSON
      if (typeof analysis === 'string') {
        try {
          analysisObj = JSON.parse(analysis);
        } catch (e) {
          // 如果不是JSON，尝试从文本中提取信息
          return this.parseAnalysisFromText(analysis);
        }
      }

      // 处理嵌套的 analysis 结构
      if (analysisObj.analysis) {
        analysisObj = analysisObj.analysis;
      }

      let assessmentData = null;
      let score = 0;
      let suggestions = [];

      // 处理英文格式的评估数据
      if (analysisObj.assessment) {
        assessmentData = analysisObj.assessment;
        score = assessmentData.overall_score || 0;
        suggestions = assessmentData.improvement_suggestions || [];
      }
      // 处理中文格式的评估数据
      else if (analysisObj.评估) {
        assessmentData = analysisObj.评估;
        score = assessmentData.overall_score || 0;
        suggestions = assessmentData.improvement_suggestions || [];
      }
      // 直接的分析对象
      else {
        assessmentData = analysisObj;
        score = analysisObj.score || analysisObj.overall_score || 0;
        suggestions = analysisObj.suggestions || analysisObj.improvement_suggestions || analysisObj.建议 || [];
      }

      // 标准化分析对象
      const result = {
        score: score,
        suggestions: suggestions,
        feedback: analysisObj.feedback || analysisObj.评价 || '',
        assessmentDetails: assessmentData ? {
          professionalismAndTechnicalAccuracy: assessmentData.professionalism_and_technical_accuracy || assessmentData.专业性和技术准确性 || 0,
          logicalClarityAndExpression: assessmentData.logical_clarity_and_expression || assessmentData.逻辑清晰度和表达 || 0,
          completenessOfResponse: assessmentData.completeness_of_response || assessmentData.回复完整性 || 0,
          jobFit: assessmentData.job_fit || assessmentData.岗位匹配度 || 0,
          practicalExperienceDemonstration: assessmentData.practical_experience_demonstration || assessmentData.实践经验展示 || 0
        } : null
      };

      console.log('解析单个问题分析成功:', result);
      return result;
    } catch (error) {
      console.error('解析问题分析失败:', error);
      return null;
    }
  }

  /**
   * 从文本中解析分析信息
   * @param {string} text - 分析文本
   * @returns {Object} 解析结果
   */
  parseAnalysisFromText(text) {
    const result = {
      score: 0,
      strengths: [],
      weaknesses: [],
      feedback: text,
      suggestions: []
    };

    // 尝试提取分数
    const scoreMatch = text.match(/(?:分数|得分|评分)[：:]?\s*(\d+)/);
    if (scoreMatch) {
      result.score = parseInt(scoreMatch[1]);
    }

    // 尝试提取优势
    const strengthsMatch = text.match(/(?:优势|优点|亮点)[：:]\s*([\s\S]*?)(?=\n(?:不足|缺点|建议)|$)/);
    if (strengthsMatch) {
      result.strengths = this.extractListItems(strengthsMatch[1]);
    }

    // 尝试提取不足
    const weaknessesMatch = text.match(/(?:不足|缺点|问题)[：:]\s*([\s\S]*?)(?=\n(?:建议|总结)|$)/);
    if (weaknessesMatch) {
      result.weaknesses = this.extractListItems(weaknessesMatch[1]);
    }

    return result;
  }

  /**
   * 解析技能列表
   * @param {string} text - 技能文本
   * @returns {Array} 技能数组
   */
  parseSkillsList(text) {
    if (!text) return [];

    return this.extractListItems(text);
  }

  /**
   * 解析建议列表
   * @param {string} text - 建议文本
   * @returns {Array} 建议数组
   */
  parseSuggestionsList(text) {
    if (!text) return [];

    return this.extractListItems(text);
  }

  /**
   * 从文本中提取列表项
   * @param {string} text - 文本内容
   * @returns {Array} 列表项数组
   */
  extractListItems(text) {
    if (!text) return [];

    const items = [];
    const lines = text.split('\n');

    lines.forEach(line => {
      line = line.trim();

      // 跳过空行
      if (!line) return;

      // 移除列表标记
      line = line.replace(/^[•·*\-+]\s*/, '');
      line = line.replace(/^\d+\.\s*/, '');

      if (line) {
        items.push(line);
      }
    });

    return items;
  }

  /**
   * 格式化内容用于显示
   * @param {string} content - 原始内容
   * @returns {string} 格式化后的内容
   */
  formatContent(content) {
    if (!content) return '';

    return content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  }
}

// 创建单例实例
export const analysisParser = new AnalysisDataParser();
