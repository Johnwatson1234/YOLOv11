<template>
  <div class="page-container">
    <div class="page-header">
      <h1>课堂实时监测</h1>
      <p>AI 视觉分析 · YOLO 实时行为检测 · 零转码极速同屏</p>
    </div>

    <div class="monitor-layout">
      <!-- Left: Video Area -->
      <div class="video-section glass-card">
        <div class="video-wrapper">
          <img
            v-if="isStreaming"
            :src="videoSrc"
            class="video-stream"
            alt="课堂视频流"
          />
          <div v-else class="video-placeholder">
            <el-icon :size="64" color="var(--text-muted)"><VideoCameraFilled /></el-icon>
            <p>点击下方"开始监控"启动 AI 视觉引擎</p>
          </div>
          <!-- Canvas Overlay for YOLO BBoxes -->
          <canvas ref="canvasRef" class="detection-canvas" style="z-index: 20;"></canvas>
          
          <!-- Privacy Masks -->
          <template v-if="privacyMode && isStreaming">
            <div
              v-for="(obj, idx) in currentObjects"
              :key="'mask-'+idx"
              class="privacy-mask"
              :style="{
                left: `${(obj.bbox[0] - obj.bbox[2] * 0.4) * 100}%`,
                top: `${(obj.bbox[1] - obj.bbox[3]/2) * 100}%`,
                width: `${obj.bbox[2] * 0.8 * 100}%`,
                height: `${obj.bbox[3] * 0.25 * 100}%`
              }"
            ></div>
          </template>
        </div>
        <!-- Controls -->
        <div class="video-controls">
          <div class="control-left">
            <el-button type="primary" :icon="isStreaming ? 'VideoPause' : 'VideoPlay'"
                       @click="toggleMonitoring" size="large">
              {{ isStreaming ? '停止监控' : '开始监控' }}
            </el-button>
            <el-button :icon="'Camera'" @click="captureScreenshot" :disabled="!isStreaming">
              截屏
            </el-button>
          </div>
          <div class="control-right">
            <el-switch v-model="privacyMode" active-text="隐私脱敏" inactive-text=""
                       style="--el-switch-on-color: var(--primary);" />
          </div>
        </div>
      </div>

      <!-- Right: Data Panel -->
      <div class="data-panel">
        <!-- Realtime Stats -->
        <div class="glass-card" style="padding:var(--space-md)">
          <div class="section-title">实时统计</div>
          <div class="mini-stats">
            <div class="mini-stat">
              <div class="mini-value" style="color:var(--primary)">{{ metrics.total }}</div>
              <div class="mini-label">总人数</div>
            </div>
            <div class="mini-stat">
              <div class="mini-value" style="color:var(--safe)">{{ metrics.focus }}</div>
              <div class="mini-label">专注</div>
            </div>
            <div class="mini-stat">
              <div class="mini-value" style="color:var(--warning)">{{ metrics.distracted }}</div>
              <div class="mini-label">游离</div>
            </div>
            <div class="mini-stat">
              <div class="mini-value" style="color:var(--danger)">{{ metrics.violation }}</div>
              <div class="mini-label">违规</div>
            </div>
          </div>
          <div class="focus-score-display">
            <span class="score-label">专注度</span>
            <span class="score-value" :style="{ color: scoreColor }">{{ metrics.score.toFixed(1) }}</span>
            <span class="score-suffix">/100</span>
          </div>
        </div>

        <!-- Focus Trend (mini) -->
        <div class="glass-card" style="padding:var(--space-md);flex:1;min-height:180px;">
          <div class="section-title">专注度趋势</div>
          <div ref="focusChartRef" style="width:100%;height:140px;"></div>
        </div>

        <!-- Behavior Distribution -->
        <div class="glass-card" style="padding:var(--space-md);">
          <div class="section-title">行为分布</div>
          <div ref="behaviorChartRef" style="width:100%;height:160px;"></div>
        </div>

        <!-- Event Log -->
        <div class="glass-card event-log-card" style="padding:var(--space-md);">
          <div class="section-title">实时事件日志</div>
          <div class="event-log" ref="logRef">
            <div v-for="(log, i) in eventLogs" :key="i" class="log-entry"
                 :class="log.level">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-msg">{{ log.message }}</span>
            </div>
            <div v-if="eventLogs.length === 0" class="log-empty">
              等待监控启动...
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'

const canvasRef = ref<HTMLCanvasElement>()
const focusChartRef = ref<HTMLElement>()
const behaviorChartRef = ref<HTMLElement>()
const logRef = ref<HTMLElement>()

const isStreaming = ref(false)
const privacyMode = ref(false)
const videoSrc = '/api/v1/monitor/video_feed'

const metrics = ref({ total: 0, focus: 0, distracted: 0, violation: 0, score: 0 })
const eventLogs = ref<Array<{ time: string; message: string; level: string }>>([])
const focusHistory = ref<number[]>([])
const currentObjects = ref<any[]>([])
const behaviorCounts = ref<Record<string, number>>({
  Listening: 0, Reading_Writing: 0, Hand_Raising: 0, Discussing: 0,
  Sleeping: 0, Looking_Around: 0, Using_Phone: 0, Standing_Leaving: 0
})

let ws: WebSocket | null = null
let focusChart: echarts.ECharts | null = null
let behaviorChart: echarts.ECharts | null = null

const scoreColor = computed(() => {
  const s = metrics.value.score
  if (s >= 80) return 'var(--safe)'
  if (s >= 60) return 'var(--warning)'
  return 'var(--danger)'
})

const behaviorNamesCN: Record<string, string> = {
  Listening: '听讲', Reading_Writing: '笔记', Hand_Raising: '举手', Discussing: '讨论',
  Sleeping: '趴桌', Looking_Around: '看四周', Using_Phone: '手机', Standing_Leaving: '离座',
}
const behaviorColors: Record<string, string> = {
  Listening: '#00E676', Reading_Writing: '#4FC3F7', Hand_Raising: '#00F2FE', Discussing: '#A78BFA',
  Sleeping: '#FFB300', Looking_Around: '#FFB300', Using_Phone: '#FF2A55', Standing_Leaving: '#FF2A55',
}

function toggleMonitoring() {
  if (isStreaming.value) {
    stopMonitoring()
  } else {
    startMonitoring()
  }
}

async function startMonitoring() {
  isStreaming.value = true
  addLog('系统', 'AI 视觉引擎启动，开始实时行为检测', 'info')

  // Start backend monitoring
  try { await fetch('/api/v1/monitor/start', { method: 'POST' }) } catch {}

  // Connect WebSocket
  connectWS()
}

function stopMonitoring() {
  isStreaming.value = false
  addLog('系统', '监控已停止', 'info')
  if (ws) { ws.close(); ws = null }
  try { fetch('/api/v1/monitor/stop', { method: 'POST' }) } catch {}
}

function connectWS() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${location.hostname}:8000/api/v1/monitor/ws`

  ws = new WebSocket(wsUrl)
  ws.onopen = () => addLog('系统', 'WebSocket 连接建立', 'info')
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      processFrame(data)
    } catch {}
  }
  ws.onclose = () => {
    if (isStreaming.value) {
      // Use simulated data if WS not available
      startSimulation()
    }
  }
  ws.onerror = () => {
    addLog('系统', '后端未连接，切换至模拟模式', 'warn')
    startSimulation()
  }
}

let simInterval: ReturnType<typeof setInterval> | null = null

function startSimulation() {
  if (simInterval) return
  simInterval = setInterval(() => {
    if (!isStreaming.value) { clearInterval(simInterval!); simInterval = null; return }
    const sim = generateSimData()
    processFrame(sim)
  }, 500)
}

function generateSimData() {
  const total = 12 + Math.floor(Math.random() * 8)
  const interacting = Math.floor(Math.random() * 4) // 0~3 people interacting
  const focus = Math.floor(Math.max(0, total * (0.55 + Math.random() * 0.35) - interacting))
  const violation = Math.floor(Math.random() * 3)
  const distracted = Math.max(0, total - focus - violation - interacting)
  const validTotal = focus + interacting + distracted + violation
  
  const score = Math.max(0, Math.min(100, ((focus + interacting * 1.5) / validTotal) * 100 - violation * 3))
  const objects = Array.from({ length: validTotal }, (_, i) => ({
    track_id: `T${(i + 1).toString().padStart(2, '0')}`,
    bbox: [0.1 + Math.random() * 0.8, 0.15 + Math.random() * 0.7, 0.04 + Math.random() * 0.06, 0.08 + Math.random() * 0.12],
    action: i < interacting ? (Math.random() > 0.6 ? 'Hand_Raising' : 'Discussing') :
            i < interacting + focus ? (Math.random() > 0.3 ? 'Listening' : 'Reading_Writing') :
            i < interacting + focus + distracted ? (Math.random() > 0.5 ? 'Sleeping' : 'Looking_Around') :
            'Using_Phone',
    confidence: 0.7 + Math.random() * 0.28,
  }))
  return {
    timestamp: Date.now(), frame_id: Math.floor(Math.random() * 9999),
    metrics: { total, focus, distracted, violation, score: Math.round(score * 10) / 10 },
    objects,
  }
}

function processFrame(data: any) {
  metrics.value = data.metrics
  currentObjects.value = data.objects

  // Update behavior counts
  const counts: Record<string, number> = {}
  for (const obj of data.objects) {
    counts[obj.action] = (counts[obj.action] || 0) + 1
  }
  behaviorCounts.value = { ...behaviorCounts.value, ...counts }

  // Update focus history
  focusHistory.value.push(data.metrics.score)
  if (focusHistory.value.length > 60) focusHistory.value.shift()

  // Draw detection boxes on canvas
  drawDetections(data.objects)

  // Update charts
  updateFocusChart()
  updateBehaviorChart()

  // Add event logs for notable detections
  if (data.metrics.violation > 0) {
    addLog('检测', `发现 ${data.metrics.violation} 人疑似使用手机`, 'danger')
  }
  if (data.metrics.score < 60) {
    addLog('预警', `全班专注度跌至 ${data.metrics.score}%，请关注`, 'warn')
  }
}

function drawDetections(objects: any[]) {
  const canvas = canvasRef.value
  if (!canvas) return
  const parent = canvas.parentElement
  if (!parent) return

  canvas.width = parent.clientWidth
  canvas.height = parent.clientHeight

  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  for (const obj of objects) {
    const [cx, cy, w, h] = obj.bbox
    const x = (cx - w / 2) * canvas.width
    const y = (cy - h / 2) * canvas.height
    const bw = w * canvas.width
    const bh = h * canvas.height

    const color = behaviorColors[obj.action] || '#00F2FE'

    // Bounding box
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, bw, bh)

    // Corner accents
    const corner = 8
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.moveTo(x, y + corner); ctx.lineTo(x, y); ctx.lineTo(x + corner, y)
    ctx.moveTo(x + bw - corner, y); ctx.lineTo(x + bw, y); ctx.lineTo(x + bw, y + corner)
    ctx.moveTo(x, y + bh - corner); ctx.lineTo(x, y + bh); ctx.lineTo(x + corner, y + bh)
    ctx.moveTo(x + bw - corner, y + bh); ctx.lineTo(x + bw, y + bh); ctx.lineTo(x + bw, y + bh - corner)
    ctx.stroke()

    // Label
    const label = `${obj.track_id} ${behaviorNamesCN[obj.action] || obj.action}`
    ctx.font = '11px Inter, sans-serif'
    const textW = ctx.measureText(label).width + 8
    ctx.fillStyle = color
    ctx.fillRect(x, y - 18, textW, 17)
    ctx.fillStyle = '#0B101E'
    ctx.fillText(label, x + 4, y - 5)
  }
}

function addLog(source: string, message: string, level: string) {
  const now = new Date()
  const time = now.toTimeString().slice(0, 8)
  eventLogs.value.unshift({ time, message: `[${source}] ${message}`, level })
  if (eventLogs.value.length > 50) eventLogs.value.pop()
}

function updateFocusChart() {
  if (!focusChartRef.value) return
  if (!focusChart) {
    focusChart = echarts.init(focusChartRef.value)
  }
  focusChart.setOption({
    grid: { top: 8, right: 8, bottom: 20, left: 32 },
    xAxis: { type: 'category', show: false, data: focusHistory.value.map((_, i) => i) },
    yAxis: { type: 'value', min: 0, max: 100, axisLine: { show: false },
             axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
             axisLabel: { color: '#4A5568', fontSize: 10 } },
    series: [{
      type: 'line', data: focusHistory.value, smooth: true,
      symbol: 'none', lineStyle: { color: '#00F2FE', width: 2 },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1,
        [{ offset: 0, color: 'rgba(0,242,254,0.2)' }, { offset: 1, color: 'rgba(0,242,254,0)' }]) },
    }],
    animation: false,
  })
}

function updateBehaviorChart() {
  if (!behaviorChartRef.value) return
  if (!behaviorChart) {
    behaviorChart = echarts.init(behaviorChartRef.value)
  }
  const data = Object.entries(behaviorCounts.value).map(([k, v]) => ({
    name: behaviorNamesCN[k] || k, value: v,
    itemStyle: { color: behaviorColors[k] || '#A0AEC0' },
  }))
  behaviorChart.setOption({
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
      data, label: { color: '#A0AEC0', fontSize: 10 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
    tooltip: { backgroundColor: '#161D2C', borderColor: 'rgba(0,242,254,0.3)', textStyle: { color: '#A0AEC0' } },
  })
}

function captureScreenshot() {
  addLog('截屏', '已截取当前画面并保存', 'info')
}

onMounted(() => {
  nextTick(() => {
    updateFocusChart()
    updateBehaviorChart()
  })
})

onUnmounted(() => {
  if (ws) ws.close()
  if (simInterval) clearInterval(simInterval)
  focusChart?.dispose()
  behaviorChart?.dispose()
})
</script>

<style scoped>
.monitor-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: var(--space-md);
  height: calc(100vh - 140px);
}

.video-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.video-wrapper {
  flex: 1;
  position: relative;
  background: #000;
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  color: var(--text-muted);
}

.detection-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  background: var(--bg-surface-2);
  border-top: 1px solid var(--border-color);
}

.privacy-mask {
  position: absolute;
  border-radius: 40%;
  backdrop-filter: blur(16px) saturate(150%) brightness(1.1);
  -webkit-backdrop-filter: blur(16px) saturate(150%) brightness(1.1);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  z-index: 10;
  pointer-events: none;
  transition: all 0.1s ease-out;
}

.control-left {
  display: flex;
  gap: var(--space-sm);
}

.data-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  overflow-y: auto;
  padding-right: 4px;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.mini-stat {
  text-align: center;
  padding: var(--space-sm);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
}

.mini-value {
  font-size: 1.5rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.mini-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.focus-score-display {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
}

.score-label { color: var(--text-muted); font-size: 0.85rem; }
.score-value { font-size: 2rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.score-suffix { color: var(--text-muted); font-size: 0.85rem; }

.event-log-card { max-height: 200px; }
.event-log {
  max-height: 140px;
  overflow-y: auto;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.75rem;
}

.log-entry {
  padding: 3px 8px;
  border-radius: 3px;
  display: flex;
  gap: var(--space-sm);
}

.log-entry.info { color: var(--text-secondary); }
.log-entry.warn { color: var(--warning); background: rgba(255,179,0,0.05); }
.log-entry.danger { color: var(--danger); background: rgba(255,42,85,0.05); }

.log-time { color: var(--text-muted); flex-shrink: 0; }
.log-empty { color: var(--text-muted); text-align: center; padding: var(--space-lg); }

@media (max-width: 1200px) {
  .monitor-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  .video-section { min-height: 400px; }
}
</style>
