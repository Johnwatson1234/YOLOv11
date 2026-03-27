"""LLM service for AI-generated post-class evaluation reports."""


# Default LLM evaluation template (Chinese)
REPORT_TEMPLATE = """
【系统指派】：你是资深的教育心理学与教学质量督导专家。请根据以下截取的课堂监测数据，为授课教师生成一段300字以内的复盘建议。
【课程背景】：科目：{subject}；时间段：{course_time}。
【教学重难点】（老师输入项）：{teaching_focus}
【行为数据快照】：实到{total_students}人。前20分钟听讲/记笔记占比及专注度为 {early_focus}%；后20分钟专注度跌落至 {late_focus}%（其中{distracted_count}人出现不同程度的"趴桌"或"左顾右盼"，防抖已过滤误判）。
【输出要求】：不得机械罗列数据。请以人性和心理学视角直指异常节点成因，并给出具体的引导与节奏分配策略。
"""


def generate_report_local(
    subject: str = "数据结构",
    course_time: str = "14:00-14:45",
    teaching_focus: str = "本节课后20分钟开始攻坚立体几何，逻辑密度大",
    total_students: int = 45,
    early_focus: float = 92.0,
    late_focus: float = 65.0,
    distracted_count: int = 15,
) -> str:
    """
    Generate a locally-crafted evaluation report when LLM API is not available.
    Returns a structured Chinese evaluation text.
    """
    # Determine severity
    drop = early_focus - late_focus
    if drop > 25:
        severity = "显著"
        suggestion_prefix = "课堂前后专注度落差极大"
    elif drop > 15:
        severity = "明显"
        suggestion_prefix = "课堂中后段出现疲劳走神趋势"
    else:
        severity = "轻微"
        suggestion_prefix = "整体课堂状态较为平稳"

    # Time-based analysis
    time_parts = course_time.split("-")
    hour = int(time_parts[0].split(":")[0]) if time_parts else 14
    if 13 <= hour <= 15:
        time_analysis = "此时间段（午后第一节）正处于人体生物节律的低谷期，学生血糖与多巴胺水平偏低，犯困概率显著上升。"
    elif 7 <= hour <= 9:
        time_analysis = "此时间段（上午第一节）学生精力相对充沛，但部分学生因来校仓促可能状态不佳。"
    else:
        time_analysis = "此时间段学生整体状态中等，需根据具体课程内容灵活调节节奏。"

    report = f"""📊 课堂质量诊断报告

🔍 核心发现：
{suggestion_prefix}。课堂前20分钟专注度高达{early_focus}%，表现优秀；然而后20分钟专注度{severity}下降至{late_focus}%，共有{distracted_count}名学生出现走神或趴桌行为（已排除防抖误判数据）。

🧠 成因分析：
1. 时间因素：{time_analysis}
2. 内容因素：教学重难点"{teaching_focus}"涉及较高的逻辑密度与抽象思维负荷，当连续讲授超过15分钟时，认知资源消耗会导致边际注意力急剧递减。
3. 群体效应：当走神学生比例超过20%时，周围同学容易受到"从众松懈"的心理暗示，形成负面连锁反应。

💡 优化建议：
1. 【节奏切分】建议在第20分钟（注意力拐点前）插入2-3分钟的课堂互动——例如小组讨论、随机提问或一道即时练习题，打断连续被动接收的疲劳积累。
2. 【难度阶梯】将高密度逻辑推导拆解为"直觉引导→分步验证→归纳总结"三段式，降低单次认知跳跃幅度。
3. 【关注后排】后排区域是走神高发区，适当进行走动式教学，利用空间压迫感重新唤起注意力。
4. 【正向激励】对课堂前半段表现优秀的学生给予即时口头表扬，利用多巴胺正反馈机制维持群体专注。

📈 总体评价：
本节{subject}课前半段教学效果{'' if early_focus >= 85 else '尚可，但仍有提升空间；'}{'优秀，' if early_focus >= 85 else ''}后半段需重点关注课堂节奏调控与学生注意力维持策略。建议下次课在high-density知识点前预埋互动锚点。"""

    return report


async def generate_report_with_llm(
    api_url: str,
    api_key: str,
    subject: str,
    course_time: str,
    teaching_focus: str,
    total_students: int,
    early_focus: float,
    late_focus: float,
    distracted_count: int,
) -> str:
    """
    Call external LLM API to generate report.
    Falls back to local generation if API call fails.
    """
    if not api_url or not api_key:
        return generate_report_local(
            subject, course_time, teaching_focus,
            total_students, early_focus, late_focus, distracted_count
        )

    prompt = REPORT_TEMPLATE.format(
        subject=subject,
        course_time=course_time,
        teaching_focus=teaching_focus or "未填写",
        total_students=total_students,
        early_focus=early_focus,
        late_focus=late_focus,
        distracted_count=distracted_count,
    )

    # Try calling external LLM
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"[WARN] LLM API call failed: {e}, using local generation.")

    return generate_report_local(
        subject, course_time, teaching_focus,
        total_students, early_focus, late_focus, distracted_count
    )
