<template>
  <div class="page-container">
    <div class="page-header">
      <h1>学生个人画像</h1>
      <p>因材施教 · 微观个体分析 · 行为趋势追踪</p>
    </div>

    <div class="profile-layout">
      <!-- Left: Student List -->
      <div class="student-list-panel glass-card">
        <div style="padding:var(--space-md)">
          <el-input v-model="searchKeyword" placeholder="搜索学生姓名/学号"
                    :prefix-icon="'Search'" clearable @input="searchStudents" />
        </div>
        <div class="student-list" ref="listRef">
          <div v-for="s in studentList" :key="s.student_id"
               class="student-item" :class="{ active: selectedId === s.student_id }"
               @click="selectStudent(s.student_id)">
            <div class="student-avatar">
              <el-icon :size="20"><User /></el-icon>
            </div>
            <div class="student-info">
              <div class="student-name">{{ s.name }}</div>
              <div class="student-id">{{ s.student_id }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Profile Detail -->
      <div class="profile-detail" v-if="profile">
        <!-- Info Card -->
        <div class="glass-card info-card">
          <div class="info-header">
            <div class="avatar-large">
              <el-icon :size="36"><User /></el-icon>
            </div>
            <div class="info-text">
              <h2>{{ profile.name }}</h2>
              <p>{{ profile.student_id }} · {{ profile.class_id }}</p>
            </div>
          </div>
          <div class="info-stats">
            <div class="info-stat">
              <span class="info-stat-value" style="color:var(--safe)">{{ profile.attendance_rate }}%</span>
              <span class="info-stat-label">出勤率</span>
            </div>
            <div class="info-stat">
              <span class="info-stat-value" style="color:var(--primary)">{{ profile.avg_focus_score }}</span>
              <span class="info-stat-label">平均专注度</span>
            </div>
            <div class="info-stat">
              <span class="info-stat-value" style="color:#A78BFA">A+</span>
              <span class="info-stat-label">综合评级</span>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid-row grid-2" style="margin-top:var(--space-md)">
          <!-- Radar Chart -->
          <div class="glass-card" style="padding:var(--space-lg)">
            <div class="section-title">能力评估雷达图</div>
            <div class="radar-legend">
              <span class="legend-item"><span class="legend-dot" style="background:var(--primary)"></span>个人</span>
              <span class="legend-item"><span class="legend-dot" style="background:rgba(167,139,250,0.6)"></span>班级平均</span>
            </div>
            <div ref="radarChartRef" style="width:100%;height:240px;"></div>
          </div>

          <!-- Trend Line -->
          <div class="glass-card" style="padding:var(--space-lg)">
            <div class="section-title">近30天专注度趋势</div>
            <div ref="trendChartRef" style="width:100%;height:280px;"></div>
          </div>
        </div>

        <!-- Behavior Stats + Recent -->
        <div class="grid-row grid-2" style="margin-top:var(--space-md)">
          <!-- Behavior bar -->
          <div class="glass-card" style="padding:var(--space-lg)">
            <div class="section-title">行为频次统计</div>
            <div ref="behaviorBarRef" style="width:100%;height:220px;"></div>
          </div>

          <!-- Recent Records -->
          <div class="glass-card" style="padding:var(--space-lg)">
            <div class="section-title">最近课堂记录</div>
            <el-table :data="profile.recent_records" style="width:100%" size="small"
                      :header-cell-style="{background:'var(--bg-surface-2)',color:'var(--text-primary)',fontSize:'12px'}"
                      :row-style="{background:'var(--bg-surface)'}">
              <el-table-column prop="date" label="日期" width="95" />
              <el-table-column prop="subject" label="科目" width="60" />
              <el-table-column prop="focus_score" label="专注度" width="70">
                <template #default="{ row }">
                  <span :style="{ color: row.focus_score >= 80 ? 'var(--safe)' : row.focus_score >= 60 ? 'var(--warning)' : 'var(--danger)' }">
                    {{ row.focus_score }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="main_behavior" label="主要行为" />
            </el-table>
          </div>
        </div>
      </div>

      <div v-else class="profile-empty glass-card">
        <el-icon :size="64" color="var(--text-muted)"><User /></el-icon>
        <p>请从左侧列表选择一位学生</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const searchKeyword = ref('')
const studentList = ref<any[]>([])
const selectedId = ref('')
const profile = ref<any>(null)

const radarChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const behaviorBarRef = ref<HTMLElement>()

const behaviorNamesCN: Record<string, string> = {
  Listening: '听讲', Reading_Writing: '笔记', Hand_Raising: '举手', Discussing: '讨论',
  Sleeping: '趴桌', Looking_Around: '看四周', Using_Phone: '手机', Standing_Leaving: '离座',
}
const behaviorColors: Record<string, string> = {
  Listening: '#00E676', Reading_Writing: '#4FC3F7', Hand_Raising: '#00F2FE', Discussing: '#A78BFA',
  Sleeping: '#FFB300', Looking_Around: '#FF9800', Using_Phone: '#FF2A55', Standing_Leaving: '#E040FB',
}

async function searchStudents() {
  try {
    const res = await fetch(`/api/v1/student/list?keyword=${searchKeyword.value}`).then(r => r.json())
    if (res.code === 0) studentList.value = res.data
  } catch {
    const names = ['张三','李四','王五','赵六','孙七','周八','吴九','郑十','刘一','陈二',
                   '林小明','黄小丽','杨晓红','何大伟','马云飞']
    const kw = searchKeyword.value.toLowerCase()
    studentList.value = names
      .filter(n => !kw || n.includes(kw))
      .map((n, i) => ({ student_id: `2023${(i+1).toString().padStart(2,'0')}`, name: n, class_id: '计科2301班' }))
  }
}

async function selectStudent(id: string) {
  selectedId.value = id
  try {
    const res = await fetch(`/api/v1/student/profile/${id}`).then(r => r.json())
    if (res.code === 0) profile.value = res.data
  } catch {
    // Fallback profile
    const s = studentList.value.find(s => s.student_id === id) || { name: '未知', student_id: id, class_id: '计科2301班' }
    profile.value = {
      ...s,
      attendance_rate: (88 + Math.random() * 12).toFixed(1),
      avg_focus_score: (70 + Math.random() * 22).toFixed(1),
      radar_data: {
        student: { focus: 85, interaction: 70, discipline: 90, endurance: 75, attendance: 95 },
        class_avg: { focus: 78, interaction: 72, discipline: 85, endurance: 70, attendance: 94 },
      },
      trend_data: Array.from({ length: 30 }, (_, i) => ({
        date: `${String(Math.floor((26 - 29 + i) > 0 ? 3 : 2)).padStart(2,'0')}-${String(((26 - 29 + i + 31) % 31) || 1).padStart(2,'0')}`,
        score: 65 + Math.random() * 30, class_avg: 72 + Math.random() * 13,
      })),
      behavior_stats: { Listening: 450, Reading_Writing: 200, Hand_Raising: 85, Discussing: 120, Sleeping: 45, Looking_Around: 60, Using_Phone: 12, Standing_Leaving: 8 },
      recent_records: Array.from({ length: 5 }, (_, i) => ({
        date: `03-${26 - i}`, subject: ['数据结构','操作系统','计算机网络','计算机组成原理','数据库原理'][i],
        focus_score: (65 + Math.random() * 30).toFixed(1), main_behavior: ['专注听讲','频繁举手','偶有走神','积极讨论','认真记笔记'][i],
      })),
    }
  }
  nextTick(() => { initRadar(); initTrend(); initBehaviorBar() })
}

function initRadar() {
  if (!radarChartRef.value || !profile.value?.radar_data) return
  const chart = echarts.init(radarChartRef.value)
  const dims = ['focus', 'interaction', 'discipline', 'endurance', 'attendance']
  const dimNames = ['专注力', '互动活跃度', '纪律性', '抗疲劳度', '出勤稳定性']
  const rd = profile.value.radar_data
  chart.setOption({
    radar: {
      indicator: dimNames.map(n => ({ name: n, max: 100 })),
      axisName: { color: '#A0AEC0', fontSize: 11 },
      splitArea: { areaStyle: { color: ['rgba(0,242,254,0.02)', 'rgba(0,242,254,0.04)'] } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
    },
    series: [{
      type: 'radar',
      data: [
        { value: dims.map(d => rd.student[d]), name: '个人', areaStyle: { color: 'rgba(0,242,254,0.15)' },
          lineStyle: { color: '#00F2FE', width: 2 }, itemStyle: { color: '#00F2FE' } },
        { value: dims.map(d => rd.class_avg[d]), name: '班级平均', areaStyle: { color: 'rgba(167,139,250,0.1)' },
          lineStyle: { color: 'rgba(167,139,250,0.6)', width: 1.5, type: 'dashed' }, itemStyle: { color: '#A78BFA' } },
      ],
    }],
    tooltip: { backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

function initTrend() {
  if (!trendChartRef.value || !profile.value?.trend_data) return
  const chart = echarts.init(trendChartRef.value)
  const data = profile.value.trend_data
  chart.setOption({
    grid: { top: 20, right: 15, bottom: 25, left: 35 },
    legend: { data: ['个人', '班级平均'], textStyle: { color: '#A0AEC0', fontSize: 11 }, top: 0, right: 0 },
    xAxis: { type: 'category', data: data.map((d: any) => d.date), axisLine: { show: false }, axisTick: { show: false },
             axisLabel: { color: '#4A5568', fontSize: 10, interval: 4 } },
    yAxis: { type: 'value', min: 50, max: 100, axisLine: { show: false }, axisTick: { show: false },
             splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } }, axisLabel: { color: '#4A5568', fontSize: 10 } },
    series: [
      { name: '个人', type: 'line', data: data.map((d: any) => d.score.toFixed ? d.score.toFixed(1) : d.score), smooth: true, symbol: 'none',
        lineStyle: { color: '#00F2FE', width: 2 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1,
          [{ offset: 0, color: 'rgba(0,242,254,0.2)' }, { offset: 1, color: 'rgba(0,242,254,0)' }]) } },
      { name: '班级平均', type: 'line', data: data.map((d: any) => d.class_avg.toFixed ? d.class_avg.toFixed(1) : d.class_avg), smooth: true, symbol: 'none',
        lineStyle: { color: '#A78BFA', width: 1.5, type: 'dashed' } },
    ],
    tooltip: { trigger: 'axis', backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

function initBehaviorBar() {
  if (!behaviorBarRef.value || !profile.value?.behavior_stats) return
  const chart = echarts.init(behaviorBarRef.value)
  const stats = profile.value.behavior_stats
  const entries = Object.entries(stats)
  chart.setOption({
    grid: { top: 10, right: 20, bottom: 5, left: 80 },
    xAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false },
             splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } }, axisLabel: { color: '#4A5568' } },
    yAxis: { type: 'category', data: entries.map(([k]) => behaviorNamesCN[k] || k),
             axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#A0AEC0', fontSize: 11 } },
    series: [{
      type: 'bar', data: entries.map(([k, v]) => ({ value: v, itemStyle: { color: behaviorColors[k] || '#A0AEC0', borderRadius: [0, 4, 4, 0] } })),
      barWidth: 16,
    }],
    tooltip: { backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

onMounted(async () => {
  await searchStudents()
  if (studentList.value.length > 0) {
    await selectStudent(studentList.value[0].student_id)
  }
})
</script>

<style scoped>
.profile-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--space-md);
  height: calc(100vh - 140px);
}

.student-list-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.student-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-sm) var(--space-sm);
}

.student-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}

.student-item:hover { background: var(--bg-hover); }
.student-item.active { background: var(--primary-bg); }

.student-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--bg-surface-3);
  display: flex; align-items: center; justify-content: center;
  color: var(--text-muted); flex-shrink: 0;
}

.student-item.active .student-avatar {
  background: rgba(0,242,254,0.15); color: var(--primary);
}

.student-name { font-size: 0.9rem; color: var(--text-primary); font-weight: 500; }
.student-id { font-size: 0.75rem; color: var(--text-muted); }

.profile-detail { overflow-y: auto; }

.info-card {
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.info-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.avatar-large {
  width: 60px; height: 60px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #A78BFA);
  display: flex; align-items: center; justify-content: center;
  color: var(--bg-app);
}

.info-text h2 { font-size: 1.3rem; color: var(--text-primary); }
.info-text p { color: var(--text-muted); font-size: 0.9rem; }

.info-stats {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-md);
  background: var(--bg-surface-2); border-radius: var(--radius-sm); padding: var(--space-md);
}

.info-stat { text-align: center; }
.info-stat-value { font-size: 1.5rem; font-weight: 700; display: block; }
.info-stat-label { font-size: 0.75rem; color: var(--text-muted); }

.profile-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: var(--space-md); color: var(--text-muted);
}

.radar-legend {
  display: flex; gap: var(--space-md); justify-content: center;
  margin-bottom: var(--space-sm); font-size: 0.8rem; color: var(--text-muted);
}
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }

@media (max-width: 1200px) {
  .profile-layout { grid-template-columns: 200px 1fr; }
}
</style>
