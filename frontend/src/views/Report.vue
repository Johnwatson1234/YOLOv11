<template>
  <div class="page-container">
    <div class="page-header">
      <h1>课后评估报告</h1>
      <p>AI 智能分析 · 专注度时间轴 · 大语言模型评语生成</p>
    </div>

    <!-- Course Selector -->
    <div class="glass-card" style="padding:var(--space-md);margin-bottom:var(--space-md);display:flex;align-items:center;gap:var(--space-md);flex-wrap:wrap">
      <span style="color:var(--text-primary);font-weight:500">选择课程：</span>
      <el-select v-model="selectedCourse" style="width:280px" @change="loadReport">
        <el-option v-for="c in courseHistory" :key="c.schedule_id"
                   :label="`${c.date} ${c.subject} (${c.time_range})`"
                   :value="c.schedule_id" />
      </el-select>
      <div style="margin-left:auto;display:flex;gap:var(--space-sm)">
        <span class="badge badge-primary">平均专注度: {{ reportData.avg_focus }}%</span>
        <span class="badge badge-safe">实到: {{ reportData.total_students }}人</span>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid-row grid-3-2" style="margin-bottom:var(--space-md)">
      <!-- Focus Curve with Knowledge Correlation -->
      <div class="glass-card" style="padding:var(--space-lg); display: flex; flex-direction: column;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-sm)">
          <div class="section-title" style="margin-bottom:0">知识点与专注度时序联动</div>
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            accept=".ppt,.pptx"
            @change="handlePptUpload"
          >
            <el-button type="primary" :icon="Upload" size="small">上传课件分析</el-button>
          </el-upload>
        </div>

        <div v-if="isParsingPpt" style="flex:1;min-height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;">
          <el-icon class="is-loading" :size="36" color="var(--primary-color)"><Loading /></el-icon>
          <span style="color:var(--text-secondary);font-size:0.9rem;">正在结构化解析课件知识点，生成联动视图...</span>
        </div>
        
        <div v-show="!isParsingPpt" ref="focusCurveRef" style="width:100%;min-height:280px;"></div>

        <div v-if="parsedPpt && !isParsingPpt" class="ppt-summary" style="margin-top:var(--space-sm);padding:12px 16px;background:rgba(0,242,254,0.05);border-radius:var(--radius-md);border:1px solid rgba(0,242,254,0.1)">
          <p style="color:var(--text-primary);margin-bottom:6px;font-size:0.9rem;display:flex;align-items:center;gap:6px">
            <el-icon color="#00F2FE"><Document /></el-icon>
            <b>已解析课件：</b>{{ parsedPpt.name }}
          </p>
          <p style="color:var(--text-secondary);font-size:0.85rem;line-height:1.5;margin:0">
            <b>AI 诊断：</b>在讲解 <b>【{{ parsedPpt.hardestPoint }}】</b> 时，班级平均专注度出现明显下降（降至 <b>{{ parsedPpt.lowestFocus }}%</b>）。建议后续教学在此处增加互动练习，或者拆解知识点难度。
          </p>
        </div>
      </div>
      <!-- Behavior Pie -->
      <div class="glass-card" style="padding:var(--space-lg)">
        <div class="section-title">行为分布统计</div>
        <div ref="behaviorPieRef" style="width:100%;height:280px;"></div>
      </div>
    </div>

    <!-- Heatmap & Leaderboard -->
    <div class="grid-row grid-2" style="margin-bottom:var(--space-md)">
      <!-- Heatmap -->
      <div class="glass-card" style="padding:var(--space-lg);">
        <div class="section-title">行为时段热力图</div>
        <div ref="heatmapRef" style="width:100%;height:280px;"></div>
      </div>
      
      <!-- Interaction Leaderboard -->
      <div class="glass-card" style="padding:var(--space-lg);">
        <div class="section-title">课堂互动积极性排行 (Top 5)</div>
        <el-table :data="leaderboardData" style="width:100%;height:280px" size="small"
                  :header-cell-style="{background:'var(--bg-surface-2)',color:'var(--text-primary)', borderBottom:'1px solid var(--border-color)'}"
                  :row-style="{background:'transparent'}">
          <el-table-column type="index" label="排名" width="60" align="center">
            <template #default="{ $index }">
              <span v-if="$index===0" style="color:#FFD700;font-size:1.2rem;font-weight:bold">1</span>
              <span v-else-if="$index===1" style="color:#C0C0C0;font-size:1.2rem;font-weight:bold">2</span>
              <span v-else-if="$index===2" style="color:#CD7F32;font-size:1.2rem;font-weight:bold">3</span>
              <span v-else>{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="handRaises" label="举手" align="center" width="60" />
          <el-table-column prop="discussionTime" label="讨论活跃度" align="center" />
          <el-table-column prop="score" label="互动分" align="center" width="70">
            <template #default="{ row }">
              <span style="color:var(--primary);font-weight:bold">{{ row.score }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- AI Report Generator -->
    <div class="glass-card" style="padding:var(--space-lg)">
      <div class="section-title">AI 智能评语生成器</div>
      <div class="ai-report-layout">
        <!-- Input area -->
        <div class="report-input">
          <div class="input-group">
            <label>课程科目</label>
            <el-input v-model="reportForm.subject" placeholder="数据结构" />
          </div>
          <div class="input-group">
            <label>上课时段</label>
            <el-input v-model="reportForm.course_time" placeholder="14:00-14:45" />
          </div>
          <div class="input-group">
            <label>教学重难点（关键上下文）</label>
            <el-input v-model="reportForm.teaching_focus" type="textarea" :rows="3"
                      placeholder="例如：本节课后20分钟开始攻坚TTL门电路工作原理，电路分析较枯燥" />
          </div>
          <el-button type="primary" :loading="isGenerating" @click="generateReport"
                     style="width:100%;margin-top:var(--space-sm)">
            {{ isGenerating ? '正在生成AI评语...' : '生成 AI 智能评语' }}
          </el-button>
        </div>
        <!-- Output area -->
        <div class="report-output">
          <div v-if="aiReport" class="report-text">
            <div v-for="(char, i) in displayedChars" :key="i" class="char-appear" v-html="char === '\n' ? '<br>' : char"></div>
          </div>
          <div v-else class="report-placeholder">
            <el-icon :size="48" color="var(--text-muted)"><ChatLineRound /></el-icon>
            <p>填写左侧信息后点击生成，AI 将给出个性化课堂诊断报告</p>
          </div>
          <div v-if="aiReport" class="report-actions">
            <el-button size="small" :icon="'CopyDocument'" @click="copyReport">复制报告</el-button>
            <el-button size="small" :icon="'Refresh'" @click="generateReport">重新生成</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { Upload, Loading, Document } from '@element-plus/icons-vue'

const focusCurveRef = ref<HTMLElement>()
const behaviorPieRef = ref<HTMLElement>()
const heatmapRef = ref<HTMLElement>()

const isParsingPpt = ref(false)
const parsedPpt = ref<any>(null)

function handlePptUpload(uploadFile: any) {
  if (!uploadFile) return
  isParsingPpt.value = true
  
  // mock parsing delay
  setTimeout(() => {
    isParsingPpt.value = false
    parsedPpt.value = {
      name: uploadFile.name || '第3章_门电路.pptx',
      hardestPoint: 'TTL门电路内部工作原理',
      lowestFocus: 52.4
    }
    updateFocusCurveWithPpt()
  }, 1500)
}

function updateFocusCurveWithPpt() {
  if (!focusCurveRef.value) return
  const chart = echarts.getInstanceByDom(focusCurveRef.value)
  if (!chart) return

  const option = chart.getOption() as any
  if (!option || !option.series || !option.series[0]) return

  option.series[0].markArea = {
    itemStyle: {
      color: 'rgba(255, 179, 0, 0.05)'
    },
    label: {
      position: 'insideTopLeft',
      color: '#FFB300',
      fontSize: 11,
      padding: [4, 8]
    },
    data: [
      [
        { name: '回顾逻辑代数\n(状态佳)', xAxis: "0'" },
        { xAxis: "12'" }
      ],
      [
        { name: '二极管/三极管开关特性\n(互动多)', xAxis: "12'", itemStyle: { color: 'rgba(0, 242, 254, 0.08)' }, label: { color: '#00F2FE' } },
        { xAxis: "25'" }
      ],
      [
        { name: 'TTL门电路工作原理\n(专注度低谷)', xAxis: "25'", itemStyle: { color: 'rgba(255, 42, 85, 0.08)' }, label: { color: '#FF2A55' } },
        { xAxis: "38'" }
      ],
      [
        { name: 'CMOS门电路对比', xAxis: "38'", itemStyle: { color: 'rgba(167, 139, 250, 0.08)' }, label: { color: '#A78BFA' } },
        { xAxis: "45'" }
      ]
    ]
  }

  chart.setOption(option)
}

const selectedCourse = ref(1)
const courseHistory = ref<any[]>([])
const reportData = ref<any>({ avg_focus: 0, total_students: 45, focus_curve: [], behavior_distribution: {}, heatmap_data: [], heatmap_behaviors: [] })

const reportForm = ref({ subject: '数字电路', course_time: '14:00-14:45', teaching_focus: '' })
const aiReport = ref('')
const displayedChars = ref<string[]>([])
const isGenerating = ref(false)

const behaviorNamesCN: Record<string, string> = {
  Listening: '专注听讲', Reading_Writing: '阅读/笔记', Hand_Raising: '举手发言', Discussing: '积极讨论',
  Sleeping: '低头/趴桌', Looking_Around: '左顾右盼', Using_Phone: '玩手机', Standing_Leaving: '起立/离开',
}
const behaviorColors: Record<string, string> = {
  Listening: '#00E676', Reading_Writing: '#4FC3F7', Hand_Raising: '#00F2FE', Discussing: '#A78BFA',
  Sleeping: '#FFB300', Looking_Around: '#FF9800', Using_Phone: '#FF2A55', Standing_Leaving: '#E040FB',
}

const leaderboardData = ref<any[]>([
  { name: '王梦琪', handRaises: 8, discussionTime: '12 分钟', score: 95 },
  { name: '刘宇航', handRaises: 6, discussionTime: '10 分钟', score: 92 },
  { name: '陈思宇', handRaises: 5, discussionTime: '11 分钟', score: 89 },
  { name: '张子轩', handRaises: 4, discussionTime: '8 分钟', score: 85 },
  { name: '林心语', handRaises: 4, discussionTime: '6 分钟', score: 82 },
])

async function loadCourseHistory() {
  try {
    const res = await fetch('/api/v1/report/history').then(r => r.json())
    if (res.code === 0) courseHistory.value = res.data
  } catch {
    courseHistory.value = [
      { schedule_id: 1, subject: '数据结构', date: '2026-03-26', time_range: '14:00-14:45', avg_focus: 78.5 },
      { schedule_id: 2, subject: '操作系统', date: '2026-03-25', time_range: '08:55-09:40', avg_focus: 85.2 },
      { schedule_id: 3, subject: '计算机网络', date: '2026-03-24', time_range: '10:00-10:45', avg_focus: 82.1 },
    ]
  }
}

async function loadReport() {
  parsedPpt.value = null
  isParsingPpt.value = false

  try {
    const res = await fetch(`/api/v1/report/data/${selectedCourse.value}`).then(r => r.json())
    if (res.code === 0) reportData.value = res.data
  } catch {
    // Generate fallback data
    const curve = Array.from({ length: 46 }, (_, i) => ({
      minute: i, score: Math.max(40, Math.min(100, 90 - i * 0.5 + (Math.random() - 0.5) * 15))
    }))
    reportData.value = {
      avg_focus: 78.5, total_students: 45, focus_curve: curve,
      behavior_distribution: { Listening: 48, Reading_Writing: 15, Hand_Raising: 12, Discussing: 9, Sleeping: 6, Looking_Around: 5, Using_Phone: 3, Standing_Leaving: 2 },
      heatmap_data: Array.from({ length: 72 }, () => [Math.floor(Math.random() * 10) * 5, Math.floor(Math.random() * 8), Math.floor(Math.random() * 15)]),
      heatmap_behaviors: ['举手', '讨论', '听讲', '笔记', '趴桌', '左顾盼', '玩手机', '起立离开'],
    }
  }
  nextTick(() => { initFocusCurve(); initBehaviorPie(); initHeatmap() })
}

function initFocusCurve() {
  if (!focusCurveRef.value) return
  const chart = echarts.init(focusCurveRef.value)
  const data = reportData.value.focus_curve || []
  // Find drop points
  const markPoints: any[] = []
  for (let i = 1; i < data.length; i++) {
    if (data[i].score < data[i - 1].score - 8) {
      markPoints.push({ coord: [data[i].minute, data[i].score], value: '↓骤降', itemStyle: { color: '#FF2A55' } })
    }
  }
  chart.setOption({
    grid: { top: 20, right: 20, bottom: 30, left: 40 },
    xAxis: { type: 'category', data: data.map((d: any) => `${d.minute}'`), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#4A5568', interval: 4 } },
    yAxis: { type: 'value', min: 30, max: 105, axisLine: { show: false }, axisTick: { show: false },
             splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } }, axisLabel: { color: '#4A5568' } },
    series: [{
      type: 'line', data: data.map((d: any) => d.score), smooth: true, symbol: 'none',
      lineStyle: { color: '#00F2FE', width: 2.5 },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{ offset: 0, color: 'rgba(0,242,254,0.3)' }, { offset: 1, color: 'rgba(0,242,254,0)' }]) },
      markPoint: { data: markPoints, symbolSize: 40, label: { fontSize: 10 } },
      markLine: { data: [{ type: 'average', name: '平均', lineStyle: { color: '#A78BFA', type: 'dashed' } }], label: { color: '#A78BFA' } },
    }],
    tooltip: { trigger: 'axis', backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' },
               formatter: (p: any) => `第 ${p[0].axisValue} 分钟<br/>专注度: <b style="color:#00F2FE">${p[0].value.toFixed(1)}%</b>` },
  })
}

function initBehaviorPie() {
  if (!behaviorPieRef.value) return
  const chart = echarts.init(behaviorPieRef.value)
  const dist = reportData.value.behavior_distribution || {}
  const data = Object.entries(dist).map(([k, v]) => ({
    name: behaviorNamesCN[k] || k, value: v,
    itemStyle: { color: behaviorColors[k] || '#A0AEC0' },
  }))
  chart.setOption({
    series: [{
      type: 'pie', radius: ['35%', '65%'], center: ['50%', '50%'], data,
      label: { color: '#A0AEC0', fontSize: 11, formatter: '{b}\n{d}%' },
      emphasis: { itemStyle: { shadowBlur: 15, shadowColor: 'rgba(0,0,0,0.4)' } },
    }],
    tooltip: { backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

function initHeatmap() {
  if (!heatmapRef.value) return
  const chart = echarts.init(heatmapRef.value)
  const hd = reportData.value.heatmap_data || []
  const yLabels = reportData.value.heatmap_behaviors || []
  const xLabels = Array.from({ length: 10 }, (_, i) => `${i * 5}'`)
  chart.setOption({
    grid: { top: 10, right: 20, bottom: 30, left: 80 },
    xAxis: { type: 'category', data: xLabels, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#4A5568' } },
    yAxis: { type: 'category', data: yLabels, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#A0AEC0' } },
    visualMap: { min: 0, max: 15, show: false,
      inRange: { color: ['rgba(0,242,254,0.05)', 'rgba(0,242,254,0.2)', '#00F2FE', '#FFB300', '#FF2A55'] } },
    series: [{ type: 'heatmap', data: hd, progressive: 0, emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 1 } } }],
    tooltip: { backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

async function generateReport() {
  isGenerating.value = true
  aiReport.value = ''
  displayedChars.value = []

  try {
    const res = await fetch('/api/v1/report/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...reportForm.value, schedule_id: selectedCourse.value }),
    }).then(r => r.json())
    if (res.code === 0) {
      aiReport.value = res.data.report_text
    }
  } catch {
    aiReport.value = `课堂质量诊断报告\n\n核心发现：\n课堂前半程在讲解"二极管与三极管的开关特性"时全班专注度高达95%，互动积极；然而在第 25 分钟进入"TTL门电路内部工作原理"环节时专注度骤降至52.4%，共有12名学生出现走神或趴桌行为。\n\n成因分析：\n1. "TTL门电路"涉及大量的晶体管级电路分析，较为枯燥抽象。\n2. 连续的理论推导超过15分钟，学生注意力出现生理性疲劳。\n\n优化建议：\n1. 建议在讲解TTL工作状态时，增加 Multisim 等仿真软件的动画演示，将抽象电路具象化。\n2. 增加设问环节：例如提问"为什么输入端悬空相当于接高电平？"以重新唤起学生注意力。\n3. 适当在讲台区域进行走动式教学，增加与后排学生的目光交流。`
  }

  // Typewriter effect
  isGenerating.value = false
  const chars = Array.from(aiReport.value)
  for (let i = 0; i < chars.length; i++) {
    await new Promise(r => setTimeout(r, 15))
    displayedChars.value.push(chars[i])
  }
}

function copyReport() {
  navigator.clipboard.writeText(aiReport.value)
}

onMounted(async () => {
  await loadCourseHistory()
  await loadReport()
})
</script>

<style scoped>
.ai-report-layout {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: var(--space-lg);
  margin-top: var(--space-md);
}

.report-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-group label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.report-output {
  background: var(--bg-surface-2);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  min-height: 250px;
  display: flex;
  flex-direction: column;
}

.report-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  color: var(--text-muted);
  text-align: center;
}

.report-text {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  overflow-y: auto;
  max-height: 300px;
}

.report-actions {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--border-color);
}

.char-appear {
  display: inline;
  animation: countUp 0.1s ease;
}

@media (max-width: 1200px) {
  .ai-report-layout { grid-template-columns: 1fr; }
}
</style>
