# 慧眼课堂 (ClassVision) — 智能教学评估系统 全栈实现方案

基于项目文档，构建一个完整可运行的智能教学评估系统。前端使用 Vue 3 + TypeScript + Vite + Element Plus + ECharts，后端使用 FastAPI + YOLO 推理，实现 7 个功能完备、界面精美的页面。

> [!IMPORTANT]
> **关键设计决策：**
> 1. 由于当前无数据库/Redis/InfluxDB，后端采用 **内存模拟 + JSON 文件持久化** 方案，所有业务数据在内存中运行，可无外部依赖即刻启动。
> 2. YOLO 推理使用已有的 [best_1200_pre.pt](file:///d:/AData/san/%E8%AE%A1%E8%AE%BE/YOLOv12/best_1200_pre.pt) 模型权重，通过 ultralytics 库加载。
> 3. 视频源使用本地 [class.mp4](file:///d:/AData/san/%E8%AE%A1%E8%AE%BE/YOLOv12/class.mp4)，后端拆帧推理后通过 WebSocket 推送坐标数据。
> 4. 前端视频播放使用 HTTP 视频流，Canvas 叠加层绘制检测框（零转码方案）。

## Proposed Changes

### Backend (FastAPI)

#### [NEW] [backend/](file:///d:/AData/san/计设/YOLOv12/backend/)
Complete backend directory with the following structure:

```
backend/
├── main.py              # FastAPI 入口，CORS，路由注册
├── requirements.txt     # Python 依赖
├── config.py            # 全局配置（模型路径、视频路径等）
├── routers/
│   ├── dashboard.py     # 工作台 API
│   ├── monitor.py       # 课堂监测 API + WebSocket
│   ├── attendance.py    # 考勤 API
│   ├── report.py        # 课后评估 API
│   ├── student.py       # 学生画像 API
│   ├── alert.py         # 异常预警 API
│   └── settings.py      # 系统设置 API
├── services/
│   ├── yolo_service.py  # YOLO 推理引擎（加载模型、逐帧检测）
│   ├── video_service.py # 视频流处理（拆帧、流式分发）
│   ├── data_service.py  # 模拟数据服务（内存数据存储）
│   └── llm_service.py   # LLM 评语生成代理
└── models/
    └── schemas.py       # Pydantic 数据模型
```

**核心功能：**
- YOLO 推理：加载 [.pt](file:///d:/AData/san/%E8%AE%A1%E8%AE%BE/YOLOv12/best_1200_pre.pt) 模型，对 [class.mp4](file:///d:/AData/san/%E8%AE%A1%E8%AE%BE/YOLOv12/class.mp4) 逐帧检测 6 种行为
- WebSocket 推送：实时推送检测结果（相对坐标、行为标签、专注度得分）
- REST API：为 7 个页面提供数据接口
- 视频流：HTTP 端点提供视频流供前端播放
- 专注度计算：基于文档公式实现加权评分

---

### Frontend (Vue 3 + Vite)

#### [NEW] [frontend/](file:///d:/AData/san/计设/YOLOv12/frontend/)
Complete frontend directory:

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/index.ts
│   ├── styles/
│   │   └── global.css         # 深空极智主题 + 全局样式
│   ├── composables/
│   │   ├── useWebSocket.ts    # WebSocket 连接管理
│   │   └── useTransition.ts   # 数字缓动动画
│   ├── components/
│   │   ├── AppLayout.vue      # 侧边栏 + 主内容布局
│   │   ├── StatCard.vue       # 数据卡片组件
│   │   ├── VideoCanvas.vue    # 视频 + Canvas 叠加组件
│   │   └── ScrollingLog.vue   # 滚动日志组件
│   └── views/
│       ├── Dashboard.vue      # P1: 系统工作台
│       ├── Monitor.vue        # P2: 课堂监测
│       ├── Attendance.vue     # P3: 智能考勤
│       ├── Report.vue         # P4: 课后评估
│       ├── StudentProfile.vue # P5: 学生个人画像
│       ├── AlertCenter.vue    # P6: 异常预警中心
│       └── Settings.vue       # P7: 系统设置
```

---

### 7 个页面详细功能设计

#### Page 1: 系统工作台 (Dashboard)
- **顶部数据卡片行（4 张）：** 带数字缓动动画的统计卡 — 本周累计课时、平均出勤率(%)、全班平均专注度、待处理预警数
- **今日课程时间轴：** 左侧垂直时间轴显示当天排课，当前课程高亮脉冲动效，已结束课程灰显
- **快捷操作区：** 三个大按钮"一键开启监控"、"导出昨日考勤"、"录入新学生"，hover 渐变发光效果
- **最新动态列表：** 系统通知/模型更新日志，带时间戳和类型图标
- **ECharts 迷你图：** 本周每日专注度趋势迷你折线图

#### Page 2: 课堂监测 (Real-time Monitoring)
- **左侧视频监控区（60% 宽度）：**
  - `<video>` 元素播放后端推送的视频流
  - 透明 Canvas 叠加层，根据 WebSocket 数据绘制检测框（绿/黄/红三色语义）
  - 底部控制台：开始/暂停/截屏按钮 + 隐私脱敏模式开关
- **右侧数据面板（40% 宽度）：**
  - 实时统计卡片：总人数、专注人数、游离人数、专注度得分（带心跳动效）
  - ECharts 实时折线图：专注度 5 分钟滚动窗口
  - 行为分布环形图：6 种行为实时占比
  - 滚动事件日志：终端风格的实时检测事件流

#### Page 3: 智能考勤 (Smart Attendance)
- **顶部统计区：** 三个环形进度图 — 应到/实到/缺勤，中间显示数字
- **考勤状态表格：** Element Plus 表格，列包含：学号、姓名、班级、状态标签（✅已签到/❌缺勤/⚠️迟到）、签到时间、操作（手动修改状态下拉）
- **未知人员面板：** 右侧卡片区展示未识别人脸抓拍缩略图，支持手动关联学生
- **顶部操作栏：** 日期选择器 + 班级筛选 + 课程筛选 + 导出 Excel 按钮
- **考勤趋势图：** 底部 ECharts 柱状图展示近 7 天出勤率对比

#### Page 4: 课后评估 (Post-class Report)
- **课程选择器：** 顶部下拉选择历史课程记录
- **专注度时间轴曲线：** ECharts 面积折线图，X 轴为 45 分钟课程时间，Y 轴为专注度百分比，带渐变填充
- **行为分布图：** 饼图/环形图展示整堂课 6 种行为占比
- **课堂热力图：** 展示不同时间段各行为的强度分布
- **AI 智能评语区：**
  - 左侧：教师输入区（科目、教学重难点、备注）
  - 右侧：AI 生成的评语展示区，打字机逐字显示效果
  - 底部：重新生成 + 复制 + 导出 PDF 按钮
- **关键节点标注：** 折线图上自动标注专注度骤降的时间点

#### Page 5: 学生个人画像 (Student Profile)
- **左侧面板：** 搜索栏 + 学生列表（头像、姓名、学号），可滚动
- **右侧详情区：**
  - 信息卡片：头像、姓名、学号、班级、历史出勤率
  - 雷达图：5 维能力评估（专注力、互动活跃度、纪律性、抗疲劳度、出勤稳定性），叠加班级平均基准线
  - 趋势折线图：近 30 天专注度变化，叠加班级平均线
  - 行为偏好统计：柱状图展示该生各行为频次
  - 最近课堂记录表格：日期/课程/专注度/行为摘要

#### Page 6: 异常预警中心 (Alert & Security)
- **顶部统计栏：** 今日预警总数、已处理、未处理、误报率
- **预警规则配置：** 可折叠面板，自定义触发条件（如"玩手机人数 > 3 触发严重预警"）
- **预警事件墙：** 瀑布流/网格卡片布局，每张卡片包含：
  - 抓拍截图缩略图
  - 预警类型标签（色彩编码）
  - 时间戳 + 涉及学生
  - ✅确认违规 / ❌误报忽略 按钮（AI 反馈闭环）
- **预警详情弹窗：** 点击卡片弹出大图 + 完整信息 + 操作按钮
- **预警趋势图：** ECharts 柱状图展示近 7 天各类预警频次

#### Page 7: 系统设置 (Settings & Model Config)
- **模型配置区：**
  - 模型选择下拉：yolov11.pt / yolov12.pt（best_1200_pre.pt）
  - 置信度阈值滑块（0.1 ~ 1.0）
  - IoU 阈值滑块（0.1 ~ 1.0）
  - 实时预览：当前模型信息 + 参数效果说明
- **视频源管理：** 文件路径输入 + 上传 + 预览缩略图
- **硬件性能监控：**
  - CPU/GPU/内存使用率仪表盘（ECharts gauge）
  - 实时 FPS 显示
  - 系统运行时长
- **LLM 服务配置：** API 地址输入 + API Key 密码框 + 连接测试按钮
- **数据合规设置：**
  - 数据保留周期选择（7/15/30/90 天）
  - 自动清理开关
  - 隐私脱敏默认开关
- **关于系统：** 版本号、技术栈信息

## Verification Plan

### Automated Tests
1. **后端启动测试：**
   ```bash
   cd d:\AData\san\计设\YOLOv12\backend
   pip install -r requirements.txt
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   验证：访问 `http://localhost:8000/docs` 能看到 Swagger 文档

2. **前端构建测试：**
   ```bash
   cd d:\AData\san\计设\YOLOv12\frontend
   npm install
   npm run dev
   ```
   验证：访问 `http://localhost:5173` 能看到完整界面

### Manual Verification (Browser)
1. 使用浏览器工具访问前端页面，逐一检查 7 个页面的布局、动画、交互
2. 验证 WebSocket 连接是否能实时推送 YOLO 检测数据
3. 验证视频播放 + Canvas 检测框叠加效果
4. 检查深色主题配色是否符合设计规范
