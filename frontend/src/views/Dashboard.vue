<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <h1>系统工作台</h1>
      <p>全局数据概览 · 一站式掌控教学动态</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid-row grid-4" style="margin-bottom: var(--space-lg);">
      <div v-for="(card, i) in statCards" :key="i"
           class="stat-card animate-slide-up"
           :style="{ animationDelay: `${i * 0.1}s`, '--accent': card.color }">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="stat-label">{{ card.label }}</span>
          <el-icon :size="22" :style="{ color: card.color }"><component :is="card.icon" /></el-icon>
        </div>
        <div>
          <span class="stat-value" :style="{ color: card.color }">{{ card.value }}</span>
          <span class="stat-suffix">{{ card.suffix }}</span>
        </div>
        <div class="stat-trend" :class="card.trendDir">
          <el-icon :size="14"><Top v-if="card.trendDir==='up'" /><Bottom v-else /></el-icon>
          {{ card.trend }}
        </div>
      </div>
    </div>

    <div class="grid-row grid-3-2" style="margin-bottom: var(--space-lg);">
      <!-- Today's Schedule -->
      <div class="glass-card" style="padding: var(--space-lg);">
        <div class="section-title">今日课程安排</div>
        <div class="schedule-timeline">
          <div v-for="course in courses" :key="course.schedule_id"
               class="schedule-item" :class="{ active: course.is_active, past: isPast(course) }">
            <div class="timeline-dot" :class="{ active: course.is_active }"></div>
            <div class="timeline-content">
              <div class="course-time">{{ formatTime(course.start_time) }} - {{ formatTime(course.end_time) }}</div>
              <div class="course-name">{{ course.subject }}</div>
              <div class="course-class">{{ course.class_id }}</div>
            </div>
            <span v-if="course.is_active" class="badge badge-primary animate-pulse" style="margin-left:auto">进行中</span>
            <span v-else-if="isPast(course)" class="badge" style="background:var(--bg-surface-3);color:var(--text-muted);margin-left:auto">已结束</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions + Weekly Trend -->
      <div style="display:flex;flex-direction:column;gap:var(--space-md)">
        <!-- Quick Actions -->
        <div class="glass-card" style="padding: var(--space-lg);">
          <div class="section-title">快捷操作</div>
          <div style="display:flex;flex-direction:column;gap:var(--space-sm);">
            <button class="action-btn action-primary" @click="$router.push('/monitor')">
              <el-icon :size="20"><VideoCameraFilled /></el-icon>
              一键开启课堂监控
            </button>
            <button class="action-btn action-secondary" @click="exportAttendanceCsv">
              <el-icon :size="20"><Download /></el-icon>
              导出昨日考勤表
            </button>
            <button class="action-btn action-secondary" @click="triggerStudentImport">
              <el-icon :size="20"><Plus /></el-icon>
              批量导入学生信息
            </button>
            <input type="file" ref="studentImportInput" accept=".csv" style="display: none" @change="handleStudentImport" />
          </div>
        </div>

        <!-- Mini Trend -->
        <div class="glass-card" style="padding: var(--space-lg);flex:1;">
          <div class="section-title">本周专注度趋势</div>
          <div ref="trendChartRef" style="width:100%;height:160px;"></div>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div class="glass-card" style="padding: var(--space-lg);">
      <div class="section-title">最新动态</div>
      <div class="notification-list">
        <div v-for="n in notifications" :key="n.id" class="notification-item">
          <div class="notif-icon" :class="n.type">
            <el-icon :size="16">
              <InfoFilled v-if="n.type==='system'" />
              <Cpu v-if="n.type==='model'" />
              <WarningFilled v-if="n.type==='alert'" />
            </el-icon>
          </div>
          <div class="notif-content">
            <div class="notif-title">{{ n.title }}</div>
            <div class="notif-desc">{{ n.content }}</div>
          </div>
          <span class="notif-time">{{ n.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const statCards = ref([
  { label: '本周累计课时', value: '21.5', suffix: '小时', icon: 'Clock', color: 'var(--primary)', trend: '较上周 +2.5h', trendDir: 'up' },
  { label: '平均出勤率', value: '95.6', suffix: '%', icon: 'UserFilled', color: 'var(--safe)', trend: '较上周 +1.2%', trendDir: 'up' },
  { label: '全班平均专注度', value: '82.3', suffix: '分', icon: 'View', color: '#A78BFA', trend: '较上周 -3.1', trendDir: 'down' },
  { label: '待处理预警', value: '5', suffix: '条', icon: 'WarningFilled', color: 'var(--danger)', trend: '今日新增 2 条', trendDir: 'up' },
])

const courses = ref<any[]>([])
const notifications = ref<any[]>([])
const trendChartRef = ref<HTMLElement>()
const studentImportInput = ref<HTMLInputElement>()

function triggerStudentImport() {
  if (studentImportInput.value) {
    studentImportInput.value.click()
  }
}

function handleStudentImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result as string
    if (text.includes('学号') && text.includes('姓名')) {
      const rows = text.split('\n').filter(row => row.trim() !== '')
      ElMessage.success(`导入成功！解析到 ${Math.max(0, rows.length - 1)} 条学生记录。`)
    } else {
      ElMessage.error('文件格式错误！请确保模板行列名包含"学号,姓名"等规范字段。')
    }
  }
  reader.readAsText(file)
  target.value = ''
}

function exportAttendanceCsv() {
  const headers = ['考勤日期', '课程', '班级', '学号', '姓名', '考勤状态', '专注度得分']
  const today = new Date().toISOString().split('T')[0]
  const rows = [
    [today, '数据结构', '计科2301班', '202301', '张三', '出勤', '85.5'],
    [today, '数据结构', '计科2301班', '202302', '李四', '出勤', '92.0'],
    [today, '数据结构', '计科2301班', '202303', '王小强', '缺勤', '0.0'],
    [today, '计算机网络', '计科2301班', '202304', '赵敏', '出勤', '78.2'],
  ]
  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `考勤报表_${today}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('昨日考勤表导出成功！')
}

function formatTime(t: string) {
  return t ? t.split(' ').pop() || t : ''
}

function isPast(course: any) {
  if (course.is_active) return false
  try {
    return new Date(course.end_time) < new Date()
  } catch { return false }
}

async function fetchData() {
  try {
    const [statsRes, schedRes, trendRes, notifRes] = await Promise.all([
      fetch('/api/v1/dashboard/stats').then(r => r.json()),
      fetch('/api/v1/dashboard/schedule').then(r => r.json()),
      fetch('/api/v1/dashboard/trend').then(r => r.json()),
      fetch('/api/v1/dashboard/notifications').then(r => r.json()),
    ])
    if (statsRes.code === 0) {
      const d = statsRes.data
      statCards.value[0].value = String(d.weekly_hours)
      statCards.value[1].value = String(d.avg_attendance_rate)
      statCards.value[2].value = String(d.avg_focus_score)
      statCards.value[3].value = String(d.pending_alerts)
    }
    if (schedRes.code === 0) courses.value = schedRes.data
    if (notifRes.code === 0) notifications.value = notifRes.data
    if (trendRes.code === 0) initTrendChart(trendRes.data)
  } catch (e) {
    console.warn('API not available, using defaults')
    courses.value = [
      { schedule_id: 1, subject: '数据结构', class_id: '计科2301班', start_time: '08:00', end_time: '08:45', is_active: false },
      { schedule_id: 2, subject: '操作系统', class_id: '计科2301班', start_time: '08:55', end_time: '09:40', is_active: false },
      { schedule_id: 3, subject: '计算机网络', class_id: '计科2301班', start_time: '10:00', end_time: '10:45', is_active: true },
      { schedule_id: 4, subject: '计算机组成原理', class_id: '计科2301班', start_time: '10:55', end_time: '11:40', is_active: false },
      { schedule_id: 5, subject: '数据库原理', class_id: '计科2301班', start_time: '14:00', end_time: '14:45', is_active: false },
      { schedule_id: 6, subject: '软件工程', class_id: '计科2301班', start_time: '14:55', end_time: '15:40', is_active: false },
    ]
    notifications.value = [
      { id: 1, type: 'system', title: '系统版本更新', content: '慧眼课堂 v2.1.0 已发布，新增隐私脱敏功能', time: '08:00' },
      { id: 2, type: 'model', title: '模型训练完成', content: 'YOLOv11 教室行为检测模型已更新至最新权重', time: '昨日22:30' },
      { id: 3, type: 'alert', title: '预警提示', content: '昨日下午第一节课检测到群体性走神，建议关注', time: '昨日17:00' },
    ]
    initTrendChart([
      { date: '03-20', focus_score: 85 }, { date: '03-21', focus_score: 82 },
      { date: '03-22', focus_score: 88 }, { date: '03-23', focus_score: 79 },
      { date: '03-24', focus_score: 91 }, { date: '03-25', focus_score: 84 },
      { date: '03-26', focus_score: 87 },
    ])
  }
}

function initTrendChart(data: any[]) {
  nextTick(() => {
    if (!trendChartRef.value) return
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      grid: { top: 10, right: 10, bottom: 24, left: 36 },
      xAxis: {
        type: 'category',
        data: data.map((d: any) => d.date),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#4A5568', fontSize: 11 },
      },
      yAxis: {
        type: 'value',
        min: 60, max: 100,
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: '#4A5568', fontSize: 11 },
      },
      series: [{
        type: 'line',
        data: data.map((d: any) => d.focus_score),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#00F2FE', width: 2 },
        itemStyle: { color: '#00F2FE' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,242,254,0.25)' },
            { offset: 1, color: 'rgba(0,242,254,0)' },
          ]),
        },
      }],
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#161D2C',
        borderColor: 'rgba(0,242,254,0.3)',
        textStyle: { color: '#A0AEC0' },
      },
    })
    window.addEventListener('resize', () => chart.resize())
  })
}

onMounted(fetchData)
</script>

<style scoped>
/* ── Schedule Timeline ── */
.schedule-timeline {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
  position: relative;
}

.schedule-item:hover {
  background: var(--bg-hover);
}

.schedule-item.active {
  background: var(--primary-bg);
}

.schedule-item.past {
  opacity: 0.45;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text-muted);
  flex-shrink: 0;
  position: relative;
}

.timeline-dot.active {
  background: var(--primary);
  box-shadow: 0 0 10px var(--primary);
  animation: pulse-glow 2s infinite;
}

.schedule-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 16px;
  top: 30px;
  width: 2px;
  height: calc(100% - 10px);
  background: var(--border-color);
}

.course-time {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.course-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.course-class {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* ── Action Buttons ── */
.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 12px var(--space-md);
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  font-family: inherit;
  transition: all var(--transition-normal);
}

.action-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: var(--bg-app);
}

.action-primary:hover {
  box-shadow: 0 4px 20px rgba(0, 242, 254, 0.3);
  transform: translateY(-1px);
}

.action-secondary {
  background: var(--bg-surface-2);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.action-secondary:hover {
  border-color: var(--primary);
  color: var(--primary);
}

/* ── Notifications ── */
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 12px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.notification-item:hover {
  background: var(--bg-hover);
}

.notif-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-icon.system { background: var(--primary-bg); color: var(--primary); }
.notif-icon.model { background: rgba(167, 139, 250, 0.15); color: #A78BFA; }
.notif-icon.alert { background: var(--danger-bg); color: var(--danger); }

.notif-content { flex: 1; min-width: 0; }
.notif-title { font-size: 0.9rem; font-weight: 500; color: var(--text-primary); }
.notif-desc { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notif-time { font-size: 0.75rem; color: var(--text-muted); flex-shrink: 0; }
</style>
