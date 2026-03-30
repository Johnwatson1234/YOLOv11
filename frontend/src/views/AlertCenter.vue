<template>
  <div class="page-container">
    <div class="page-header">
      <h1>异常预警中心</h1>
      <p>违规行为追溯 · AI 反馈闭环 · 模型持续优化</p>
    </div>

    <!-- Top Stats -->
    <div class="grid-row grid-4" style="margin-bottom:var(--space-lg)">
      <div class="stat-card">
        <span class="stat-label">今日预警总数</span>
        <span class="stat-value" style="color:var(--primary)">{{ alertStats.total }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">已确认违规</span>
        <span class="stat-value" style="color:var(--danger)">{{ alertStats.confirmed }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">已忽略/误报</span>
        <span class="stat-value" style="color:var(--safe)">{{ alertStats.dismissed }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">误报率</span>
        <span class="stat-value" style="color:var(--warning)">{{ alertStats.false_rate }}%</span>
      </div>
    </div>

    <div class="grid-row grid-3-2">
      <!-- Alert Event Wall -->
      <div>
        <div class="section-title" style="margin-bottom:var(--space-md)">预警事件墙</div>
        <div class="alert-grid">
          <div v-for="event in alertEvents" :key="event.alert_id"
               class="alert-card glass-card" :class="event.severity">
            <!-- Snapshot Area -->
            <div class="alert-snapshot">
              <el-icon :size="40" color="var(--text-muted)"><PictureFilled /></el-icon>
              <span class="alert-type-badge" :class="event.severity">{{ event.alert_type }}</span>
            </div>
            <!-- Info -->
            <div class="alert-info">
              <div class="alert-desc">{{ event.description }}</div>
              <div class="alert-meta">
                <el-icon :size="12"><Clock /></el-icon>
                {{ event.timestamp }}
              </div>
              <div class="alert-meta" v-if="event.student_ids.length">
                <el-icon :size="12"><User /></el-icon>
                涉及 {{ event.student_ids.length }} 名学生
              </div>
            </div>
            <!-- Feedback Buttons -->
            <div class="alert-actions">
              <button class="feedback-btn confirm"
                      :class="{ active: event.confirmed === true }"
                      @click="sendFeedback(event, true)">
                确认违规
              </button>
              <button class="feedback-btn dismiss"
                      :class="{ active: event.confirmed === false }"
                      @click="sendFeedback(event, false)">
                误报忽略
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Rules + Trend -->
      <div style="display:flex;flex-direction:column;gap:var(--space-md)">
        <!-- Alert Rules -->
        <div class="glass-card" style="padding:var(--space-lg)">
          <div class="section-title">️ 预警规则配置</div>
          <div class="rule-list">
            <div v-for="rule in alertRules" :key="rule.rule_id" class="rule-item">
              <div class="rule-info">
                <div class="rule-name">{{ rule.name }}</div>
                <div class="rule-condition">{{ rule.condition }} ≥ {{ rule.threshold }}</div>
              </div>
              <div class="rule-controls">
                <el-input-number v-model="rule.threshold" :min="1" :max="50" size="small"
                                 style="width:80px" />
                <el-switch v-model="rule.enabled" size="small" />
              </div>
            </div>
          </div>
        </div>

        <!-- Alert Trend Chart -->
        <div class="glass-card" style="padding:var(--space-lg);flex:1">
          <div class="section-title">近7日预警趋势</div>
          <div ref="trendChartRef" style="width:100%;height:220px;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const trendChartRef = ref<HTMLElement>()

const alertStats = ref({ total: 0, confirmed: 0, dismissed: 0, pending: 0, false_rate: 0 })
const alertEvents = ref<any[]>([])
const alertRules = ref<any[]>([])

async function fetchData() {
  try {
    const [evRes, ruRes, trRes] = await Promise.all([
      fetch('/api/v1/alert/events').then(r => r.json()),
      fetch('/api/v1/alert/rules').then(r => r.json()),
      fetch('/api/v1/alert/trend').then(r => r.json()),
    ])
    if (evRes.code === 0) {
      alertStats.value = { total: evRes.data.total, confirmed: evRes.data.confirmed,
        dismissed: evRes.data.dismissed, pending: evRes.data.pending, false_rate: evRes.data.false_rate }
      alertEvents.value = evRes.data.events
    }
    if (ruRes.code === 0) alertRules.value = ruRes.data
    if (trRes.code === 0) initTrendChart(trRes.data)
  } catch {
    // Fallback
    alertStats.value = { total: 15, confirmed: 6, dismissed: 3, pending: 6, false_rate: 20 }
    const types = ['群体性趴桌', '多人玩手机', '学生长时间离座', '集体走神', '异常聚集']
    alertEvents.value = types.flatMap((t, i) => Array.from({ length: 3 }, (_, j) => ({
      alert_id: i * 3 + j + 1,
      alert_type: t,
      severity: t.includes('手机') ? 'danger' : 'warning',
      description: `在课堂视频流中检测到${t}行为`,
      timestamp: `2026-03-${25 - j} ${10 + i}:${15 + j * 10}:00`,
      student_ids: Array.from({ length: 1 + j }, (_, k) => `2023${(k + 1).toString().padStart(2, '0')}`),
      confirmed: null,
    })))
    alertRules.value = [
      { rule_id: 1, name: '群体玩手机预警', condition: '同时玩手机人数', threshold: 3, enabled: true },
      { rule_id: 2, name: '群体趴桌预警', condition: '同时趴桌人数', threshold: 5, enabled: true },
      { rule_id: 3, name: '学生离座预警', condition: '离座持续时间(秒)', threshold: 300, enabled: true },
      { rule_id: 4, name: '专注度低预警', condition: '全班专注度低于(%)', threshold: 50, enabled: false },
    ]
    initTrendChart({
      trend: Array.from({ length: 7 }, (_, i) => ({
        date: `03-${20 + i}`, 群体性趴桌: Math.floor(Math.random() * 5), 多人玩手机: Math.floor(Math.random() * 4),
        学生离座: Math.floor(Math.random() * 3), 集体走神: Math.floor(Math.random() * 4),
      })),
      types: ['群体性趴桌', '多人玩手机', '学生离座', '集体走神'],
    })
  }
}

function sendFeedback(event: any, confirmed: boolean) {
  event.confirmed = confirmed
  fetch('/api/v1/alert/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id: event.alert_id, confirmed }),
  }).catch(() => {})
}

function initTrendChart(data: any) {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const colors = ['#FFB300', '#FF2A55', '#E040FB', '#00F2FE']
  chart.setOption({
    grid: { top: 30, right: 10, bottom: 20, left: 30 },
    legend: { data: data.types, textStyle: { color: '#A0AEC0', fontSize: 10 }, top: 0 },
    xAxis: { type: 'category', data: data.trend.map((d: any) => d.date), axisLine: { show: false },
             axisTick: { show: false }, axisLabel: { color: '#4A5568', fontSize: 10 } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false },
             splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
             axisLabel: { color: '#4A5568', fontSize: 10 } },
    series: data.types.map((t: string, i: number) => ({
      name: t, type: 'bar', stack: 'alerts',
      data: data.trend.map((d: any) => d[t] || 0),
      itemStyle: { color: colors[i % colors.length], borderRadius: i === data.types.length - 1 ? [4, 4, 0, 0] : 0 },
      barWidth: 18,
    })),
    tooltip: { trigger: 'axis', backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

onMounted(fetchData)
</script>

<style scoped>
.alert-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-md);
  max-height: calc(100vh - 320px);
  overflow-y: auto;
  padding-right: 4px;
}

.alert-card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all var(--transition-normal);
}

.alert-card.danger { border-color: rgba(255, 42, 85, 0.2); }
.alert-card.warning { border-color: rgba(255, 179, 0, 0.15); }
.alert-card:hover { transform: translateY(-2px); }

.alert-snapshot {
  height: 100px;
  background: var(--bg-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.alert-type-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.alert-type-badge.danger { background: var(--danger-bg); color: var(--danger); }
.alert-type-badge.warning { background: var(--warning-bg); color: var(--warning); }

.alert-info {
  padding: var(--space-md);
  flex: 1;
}

.alert-desc { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: var(--space-sm); }
.alert-meta { font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px; margin-top: 2px; }

.alert-actions {
  display: flex;
  border-top: 1px solid var(--border-color);
}

.feedback-btn {
  flex: 1;
  padding: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: inherit;
  transition: all var(--transition-fast);
  background: transparent;
}

.feedback-btn.confirm { color: var(--safe); }
.feedback-btn.confirm:hover, .feedback-btn.confirm.active { background: var(--safe-bg); }
.feedback-btn.dismiss { color: var(--text-muted); border-left: 1px solid var(--border-color); }
.feedback-btn.dismiss:hover, .feedback-btn.dismiss.active { background: var(--bg-hover); color: var(--warning); }

/* Rules */
.rule-list { display: flex; flex-direction: column; gap: var(--space-sm); }

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.rule-name { font-size: 0.9rem; color: var(--text-primary); font-weight: 500; }
.rule-condition { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }

.rule-controls {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
</style>
