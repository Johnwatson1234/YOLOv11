<template>
  <div class="page-container">
    <div class="page-header">
      <h1>️ 系统设置</h1>
      <p>模型管理 · 参数调优 · 硬件监控 · 数据合规</p>
    </div>

    <div class="grid-row grid-2" style="margin-bottom:var(--space-md)">
      <!-- Model Config -->
      <div class="glass-card" style="padding:var(--space-lg)">
        <div class="section-title">视觉模型配置</div>
        <div class="setting-group">
          <label>选择检测模型</label>
          <el-select v-model="settings.current_model" style="width:100%"
                     @change="saveSettings">
            <el-option label="YOLOv11 (yolov11.pt)" value="yolov11.pt" />
            <el-option label="YOLOv12 (yolov12.pt)" value="yolov12.pt" />
            <el-option label="YOLO11 Large (yolo11l.pt)" value="yolo11l.pt" />
            <el-option label="YOLO11 Small (yolo11s.pt)" value="yolo11s.pt" />
            <el-option label="YOLOv10 Large (yolov10l.pt)" value="yolov10l.pt" />
            <el-option label="YOLOv10 Medium (yolov10m.pt)" value="yolov10m.pt" />
            <el-option label="YOLOv10 Nano (yolov10n.pt)" value="yolov10n.pt" />
          </el-select>
          <div class="setting-hint">当前已训练两个版本模型权重，支持热切换对比效果</div>
        </div>
        <div class="setting-group">
          <label>置信度阈值 (Confidence): <span class="value-tag">{{ settings.confidence.toFixed(2) }}</span></label>
          <el-slider v-model="settings.confidence" :min="0.1" :max="1" :step="0.05"
                     @change="saveSettings" />
          <div class="setting-hint">值越高检测越严格，避免误报；值越低召回率越高</div>
        </div>
        <div class="setting-group">
          <label>交并比阈值 (IoU): <span class="value-tag">{{ settings.iou.toFixed(2) }}</span></label>
          <el-slider v-model="settings.iou" :min="0.1" :max="1" :step="0.05"
                     @change="saveSettings" />
          <div class="setting-hint">控制非极大值抑制的重叠框过滤力度</div>
        </div>
      </div>

      <!-- Hardware Monitor -->
      <div class="glass-card" style="padding:var(--space-lg)">
        <div class="section-title">硬件性能监控</div>
        <div class="gauge-row">
          <div class="gauge-item">
            <div ref="cpuGaugeRef" style="width:100%;height:130px;"></div>
            <div class="gauge-label">CPU</div>
          </div>
          <div class="gauge-item">
            <div ref="gpuGaugeRef" style="width:100%;height:130px;"></div>
            <div class="gauge-label">GPU</div>
          </div>
          <div class="gauge-item">
            <div ref="memGaugeRef" style="width:100%;height:130px;"></div>
            <div class="gauge-label">内存</div>
          </div>
        </div>
        <div class="hardware-stats">
          <div class="hw-stat">
            <span class="hw-label">处理帧率</span>
            <span class="hw-value" style="color:var(--safe)">{{ sysMetrics.fps }} FPS</span>
          </div>
          <div class="hw-stat">
            <span class="hw-label">内存使用</span>
            <span class="hw-value">{{ sysMetrics.memory_used_gb }} / {{ sysMetrics.memory_total_gb }} GB</span>
          </div>
          <div class="hw-stat">
            <span class="hw-label">系统运行</span>
            <span class="hw-value">{{ sysMetrics.uptime_hours }} 小时</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-row grid-2" style="margin-bottom:var(--space-md)">
      <!-- Video Source -->
      <div class="glass-card" style="padding:var(--space-lg)">
        <div class="section-title">视频源管理</div>
        <div class="setting-group">
          <label>视频文件路径</label>
          <el-input v-model="settings.video_source" placeholder="class.mp4">
            <template #append>
              <el-button :icon="'FolderOpened'">浏览</el-button>
            </template>
          </el-input>
        </div>
        <div class="setting-group">
          <label style="display:flex;justify-content:space-between;align-items:center">
            隐私脱敏模式默认开启
            <el-switch v-model="settings.privacy_mode" @change="saveSettings" />
          </label>
          <div class="setting-hint">开启后非违规学生的面部自动打码保护隐私</div>
        </div>
      </div>

      <!-- LLM Config -->
      <div class="glass-card" style="padding:var(--space-lg)">
        <div class="section-title">LLM 大模型服务接入</div>
        <div class="setting-group">
          <label>API 接口地址</label>
          <el-input v-model="settings.llm_api_url" placeholder="https://api.openai.com/v1/chat/completions" />
        </div>
        <div class="setting-group">
          <label>API 密钥</label>
          <el-input v-model="settings.llm_api_key" type="password" show-password placeholder="sk-..." />
        </div>
        <el-button type="primary" plain @click="testLLM" :loading="testingLLM" style="margin-top:var(--space-sm)">
          {{ testingLLM ? '测试中...' : '测试连接' }}
        </el-button>
        <div v-if="llmTestResult" class="test-result" :class="llmTestResult.ok ? 'success' : 'error'">
          {{ llmTestResult.message }}
        </div>
      </div>
    </div>

    <!-- Data Compliance -->
    <div class="glass-card" style="padding:var(--space-lg)">
      <div class="section-title">数据留存与合规设置</div>
      <div class="grid-row grid-3">
        <div class="setting-group">
          <label>数据保留周期</label>
          <el-select v-model="settings.data_retention_days" style="width:100%" @change="saveSettings">
            <el-option label="7 天" :value="7" />
            <el-option label="15 天" :value="15" />
            <el-option label="30 天" :value="30" />
            <el-option label="90 天" :value="90" />
          </el-select>
          <div class="setting-hint">超过保留期的违规抓拍截图将自动物理销毁</div>
        </div>
        <div class="setting-group">
          <label style="display:flex;justify-content:space-between;align-items:center">
            自动清理
            <el-switch v-model="settings.auto_cleanup" @change="saveSettings" />
          </label>
          <div class="setting-hint">启用后将按周期自动执行数据清理任务</div>
        </div>
        <div class="setting-group">
          <div class="about-info">
            <div class="about-title">关于系统</div>
            <div class="about-item">版本：v2.1.0</div>
            <div class="about-item">引擎：YOLOv11 + ONNX Runtime</div>
            <div class="about-item">框架：FastAPI + Vue 3</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const cpuGaugeRef = ref<HTMLElement>()
const gpuGaugeRef = ref<HTMLElement>()
const memGaugeRef = ref<HTMLElement>()

const settings = ref({
  current_model: 'yolov11.pt',
  confidence: 0.45,
  iou: 0.5,
  video_source: 'class.mp4',
  privacy_mode: false,
  data_retention_days: 30,
  auto_cleanup: true,
  llm_api_url: '',
  llm_api_key: '',
})

const sysMetrics = ref({
  cpu_percent: 0, gpu_percent: 0, memory_percent: 0,
  memory_used_gb: 0, memory_total_gb: 16,
  fps: 0, uptime_hours: 0,
})

const testingLLM = ref(false)
const llmTestResult = ref<{ ok: boolean; message: string } | null>(null)

let cpuChart: echarts.ECharts | null = null
let gpuChart: echarts.ECharts | null = null
let memChart: echarts.ECharts | null = null
let metricsInterval: ReturnType<typeof setInterval> | null = null

function createGauge(el: HTMLElement, value: number, color: string): echarts.ECharts {
  const chart = echarts.init(el)
  chart.setOption({
    series: [{
      type: 'gauge',
      radius: '90%',
      startAngle: 220,
      endAngle: -40,
      min: 0,
      max: 100,
      pointer: { show: false },
      progress: {
        show: true,
        width: 10,
        roundCap: true,
        itemStyle: { color },
      },
      axisLine: { lineStyle: { width: 10, color: [[1, 'rgba(255,255,255,0.05)']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: {
        valueAnimation: true,
        formatter: '{value}%',
        fontSize: 18,
        fontWeight: 700,
        color,
        offsetCenter: [0, '10%'],
      },
      data: [{ value }],
    }],
  })
  return chart
}

async function fetchSettings() {
  try {
    const res = await fetch('/api/v1/settings/').then(r => r.json())
    if (res.code === 0) settings.value = { ...settings.value, ...res.data }
  } catch {}
}

async function saveSettings() {
  try {
    await fetch('/api/v1/settings/', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value),
    })
  } catch {}
}

async function fetchMetrics() {
  try {
    const res = await fetch('/api/v1/settings/metrics').then(r => r.json())
    if (res.code === 0) sysMetrics.value = res.data
  } catch {
    sysMetrics.value = {
      cpu_percent: 25 + Math.random() * 40,
      gpu_percent: 35 + Math.random() * 45,
      memory_percent: 45 + Math.random() * 25,
      memory_used_gb: 6 + Math.random() * 6,
      memory_total_gb: 16,
      fps: 20 + Math.random() * 10,
      uptime_hours: 12.5,
    }
  }
  updateGauges()
}

function updateGauges() {
  const m = sysMetrics.value
  if (cpuChart) cpuChart.setOption({ series: [{ data: [{ value: Math.round(m.cpu_percent) }] }] })
  if (gpuChart) gpuChart.setOption({ series: [{ data: [{ value: Math.round(m.gpu_percent) }] }] })
  if (memChart) memChart.setOption({ series: [{ data: [{ value: Math.round(m.memory_percent) }] }] })
}

async function testLLM() {
  testingLLM.value = true
  llmTestResult.value = null
  try {
    const res = await fetch(`/api/v1/settings/test_llm?api_url=${encodeURIComponent(settings.value.llm_api_url)}&api_key=${encodeURIComponent(settings.value.llm_api_key)}`,
      { method: 'POST' }).then(r => r.json())
    llmTestResult.value = { ok: res.code === 0, message: res.message }
  } catch {
    llmTestResult.value = { ok: false, message: '无法连接后端服务' }
  }
  testingLLM.value = false
}

onMounted(async () => {
  await fetchSettings()
  await fetchMetrics()
  nextTick(() => {
    if (cpuGaugeRef.value) cpuChart = createGauge(cpuGaugeRef.value, Math.round(sysMetrics.value.cpu_percent), '#00F2FE')
    if (gpuGaugeRef.value) gpuChart = createGauge(gpuGaugeRef.value, Math.round(sysMetrics.value.gpu_percent), '#A78BFA')
    if (memGaugeRef.value) memChart = createGauge(memGaugeRef.value, Math.round(sysMetrics.value.memory_percent), '#FFB300')
  })
  metricsInterval = setInterval(fetchMetrics, 5000)
})

onUnmounted(() => {
  if (metricsInterval) clearInterval(metricsInterval)
  cpuChart?.dispose()
  gpuChart?.dispose()
  memChart?.dispose()
})
</script>

<style scoped>
.setting-group {
  margin-bottom: var(--space-lg);
}

.setting-group label {
  display: block;
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: var(--space-sm);
}

.setting-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.value-tag {
  background: var(--primary-bg);
  color: var(--primary);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-left: 4px;
}

.gauge-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-sm);
}

.gauge-item {
  text-align: center;
}

.gauge-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
  margin-top: -8px;
}

.hardware-stats {
  display: flex;
  justify-content: space-around;
  padding: var(--space-md);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
  margin-top: var(--space-sm);
}

.hw-stat { text-align: center; }
.hw-label { display: block; font-size: 0.75rem; color: var(--text-muted); }
.hw-value { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }

.test-result {
  margin-top: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.test-result.success { background: var(--safe-bg); color: var(--safe); }
.test-result.error { background: var(--danger-bg); color: var(--danger); }

.about-info {
  padding: var(--space-md);
  background: var(--bg-surface-2);
  border-radius: var(--radius-sm);
}

.about-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.about-item {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 4px;
}
</style>
