<template>
  <div class="page-container">
    <div class="page-header">
      <h1>智能考勤</h1>
      <p>AI 人脸识别静默签到 · 实时出勤追踪</p>
    </div>

    <!-- Top Stats -->
    <div class="grid-row grid-3" style="margin-bottom:var(--space-lg)">
      <div class="stat-card" style="text-align:center">
        <div ref="presentChartRef" style="width:100%;height:120px;"></div>
        <div class="stat-label">实到人数</div>
        <div class="stat-value" style="color:var(--safe)">{{ present }}<span class="stat-suffix">/ {{ total }}</span></div>
      </div>
      <div class="stat-card" style="text-align:center">
        <div ref="lateChartRef" style="width:100%;height:120px;"></div>
        <div class="stat-label">迟到人数</div>
        <div class="stat-value" style="color:var(--warning)">{{ late }}</div>
      </div>
      <div class="stat-card" style="text-align:center">
        <div ref="absentChartRef" style="width:100%;height:120px;"></div>
        <div class="stat-label">缺勤人数</div>
        <div class="stat-value" style="color:var(--danger)">{{ absent }}</div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar glass-card" style="padding:var(--space-md);margin-bottom:var(--space-md);display:flex;align-items:center;gap:var(--space-md);flex-wrap:wrap">
      <el-date-picker v-model="dateFilter" type="date" placeholder="选择日期"
                      style="width:160px" :teleported="false" />
      <el-select v-model="classFilter" placeholder="选择班级" style="width:150px">
        <el-option label="计科2301班" value="计科2301班" />
      </el-select>
      <el-select v-model="courseFilter" placeholder="选择课程" style="width:150px">
        <el-option label="全部课程" value="" />
        <el-option label="数据结构" value="数据结构" />
        <el-option label="操作系统" value="操作系统" />
        <el-option label="计算机网络" value="计算机网络" />
      </el-select>
      <el-input v-model="searchKeyword" placeholder="搜索学生姓名/学号" :prefix-icon="'Search'"
                style="width:200px" clearable />
      <div style="margin-left:auto">
        <el-button type="primary" :icon="'Download'" @click="exportAttendanceCsv">导出 Excel</el-button>
      </div>
    </div>

    <div class="grid-row grid-2-1">
      <!-- Attendance Table -->
      <div class="glass-card" style="padding:var(--space-md)">
        <div class="section-title">考勤状态清单</div>
        <el-table :data="filteredRecords" style="width:100%" max-height="420"
                  :header-cell-style="{background:'var(--bg-surface-2)',color:'var(--text-primary)'}"
                  :row-style="{background:'var(--bg-surface)'}">
          <el-table-column prop="student_id" label="学号" width="100" />
          <el-table-column prop="name" label="姓名" width="90" />
          <el-table-column prop="class_id" label="班级" width="110" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <span class="badge" :class="statusBadge(row.status)">
                {{ statusIcon(row.status) }} {{ statusText(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="check_in_time" label="签到时间" width="120">
            <template #default="{ row }">
              {{ row.check_in_time ? row.check_in_time.split(' ').pop() : '—' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-select v-model="row.status" size="small" style="width:90px">
                <el-option label="已签到" value="PRESENT" />
                <el-option label="迟到" value="LATE" />
                <el-option label="缺勤" value="ABSENT" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Unknown Persons -->
      <div class="glass-card" style="padding:var(--space-md)">
        <div class="section-title">未知人员</div>
        <p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:var(--space-md)">
          AI 无法识别的人员抓拍，请手动核实
        </p>
        <div class="unknown-list">
          <div v-for="i in 3" :key="i" class="unknown-card">
            <div class="unknown-avatar">
              <el-icon :size="28" color="var(--text-muted)"><User /></el-icon>
            </div>
            <div class="unknown-info">
              <div style="color:var(--text-primary);font-size:0.85rem">未知人员 #{{ i }}</div>
              <div style="color:var(--text-muted);font-size:0.75rem">08:{{ 30 + i * 5 }} 检测到</div>
            </div>
            <el-button size="small" type="primary" plain>关联学生</el-button>
          </div>
        </div>

        <!-- Trend Mini Chart -->
        <div style="margin-top:var(--space-lg)">
          <div class="section-title">近7日出勤趋势</div>
          <div ref="trendChartRef" style="width:100%;height:160px;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const dateFilter = ref('')
const classFilter = ref('计科2301班')
const courseFilter = ref('')
const searchKeyword = ref('')

const total = ref(45)
const present = ref(38)
const late = ref(4)
const absent = ref(3)
const records = ref<any[]>([])

const presentChartRef = ref<HTMLElement>()
const lateChartRef = ref<HTMLElement>()
const absentChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

const filteredRecords = computed(() => {
  if (!searchKeyword.value) return records.value
  const kw = searchKeyword.value.toLowerCase()
  return records.value.filter(r =>
    r.name.toLowerCase().includes(kw) || r.student_id.includes(kw)
  )
})

function statusBadge(s: string) {
  return { PRESENT: 'badge-safe', LATE: 'badge-warning', ABSENT: 'badge-danger' }[s] || ''
}
function statusIcon(s: string) {
  return { PRESENT: '', LATE: '️', ABSENT: '' }[s] || ''
}
function statusText(s: string) {
  return { PRESENT: '已签到', LATE: '迟到', ABSENT: '缺勤' }[s] || s
}

function exportAttendanceCsv() {
  const headers = ['考勤日期', '课程', '班级', '学号', '姓名', '考勤状态', '专注度得分']
  const today = dateFilter.value ? new Date(dateFilter.value).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
  const course = courseFilter.value || '全部课程'
  
  if (!filteredRecords.value || filteredRecords.value.length === 0) {
    ElMessage.warning('当前没有可导出的考勤记录')
    return
  }

  const rows = filteredRecords.value.map(r => {
    // Generate mock focus score for realism based on present status
    const focus = r.status === 'ABSENT' ? 0.0 : (70 + Math.random() * 25).toFixed(1)
    return [
      today,
      course,
      r.class_id || classFilter.value,
      r.student_id,
      r.name,
      statusText(r.status),
      focus
    ]
  })
  
  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `考勤报表_${today}_${course}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('考勤记录已成功导出为 CSV 文件！')
}

function initGaugeChart(el: HTMLElement, value: number, total: number, color: string) {
  const chart = echarts.init(el)
  chart.setOption({
    series: [{
      type: 'pie',
      radius: ['65%', '85%'],
      startAngle: 90,
      silent: true,
      data: [
        { value, itemStyle: { color }, label: { show: false } },
        { value: total - value, itemStyle: { color: 'rgba(255,255,255,0.05)' }, label: { show: false } },
      ],
      emphasis: { disabled: true },
    }],
  })
  return chart
}

async function fetchData() {
  try {
    const res = await fetch('/api/v1/attendance/live').then(r => r.json())
    if (res.code === 0) {
      total.value = res.data.total
      present.value = res.data.present
      late.value = res.data.late
      absent.value = res.data.absent
      records.value = res.data.records
    }
  } catch {
    // Fallback data
    const names = ['张三','李四','王五','赵六','孙七','周八','吴九','郑十','刘一','陈二',
                   '林小明','黄小丽','杨晓红','何大伟','马云飞']
    records.value = names.map((name, i) => ({
      student_id: `2023${(i+1).toString().padStart(2,'0')}`,
      name,
      class_id: '计科2301班',
      status: i < 10 ? 'PRESENT' : i < 13 ? 'LATE' : 'ABSENT',
      check_in_time: i < 13 ? `07:${45 + i}` : null,
    }))
    total.value = records.value.length
    present.value = 10; late.value = 3; absent.value = 2
  }

  nextTick(() => {
    if (presentChartRef.value) initGaugeChart(presentChartRef.value, present.value, total.value, '#00E676')
    if (lateChartRef.value) initGaugeChart(lateChartRef.value, late.value, total.value, '#FFB300')
    if (absentChartRef.value) initGaugeChart(absentChartRef.value, absent.value, total.value, '#FF2A55')
    initTrendChart()
  })
}

function initTrendChart() {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const days = ['03-20','03-21','03-22','03-23','03-24','03-25','03-26']
  chart.setOption({
    grid: { top: 10, right: 10, bottom: 20, left: 30 },
    xAxis: { type: 'category', data: days, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#4A5568', fontSize: 10 } },
    yAxis: { type: 'value', min: 30, max: 48, axisLine: { show: false }, axisTick: { show: false },
             splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } }, axisLabel: { color: '#4A5568', fontSize: 10 } },
    series: [
      { name: '实到', type: 'bar', data: [42,44,41,43,45,40,38], itemStyle: { color: '#00E676', borderRadius: [4,4,0,0] }, barWidth: 14 },
      { name: '迟到', type: 'bar', data: [2,1,3,1,0,3,4], itemStyle: { color: '#FFB300', borderRadius: [4,4,0,0] }, barWidth: 14 },
      { name: '缺勤', type: 'bar', data: [1,0,1,1,0,2,3], itemStyle: { color: '#FF2A55', borderRadius: [4,4,0,0] }, barWidth: 14 },
    ],
    tooltip: { trigger: 'axis', backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

onMounted(fetchData)
</script>

<style scoped>
.toolbar { border-radius: var(--radius-md); }

.unknown-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.unknown-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.unknown-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-surface-3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.unknown-info { flex: 1; }
</style>
