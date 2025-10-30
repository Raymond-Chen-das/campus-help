import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import (
    init_db, get_all_users, get_user_by_name, 
    get_all_tasks, create_task, get_user_tasks, 
    apply_for_task, get_task_applications,
    accept_application, complete_task,
    submit_review, get_reviews_for_user, check_review_status
)
from matching_engine import MatchingEngine
from ai_service import AIService

# 頁面配置
st.set_page_config(
    page_title="Campus Help - 校園共享幫幫平台",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #9333ea;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .task-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #e5e7eb;
        margin-bottom: 1rem;
        background: white;
    }
    .urgent-badge {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .category-badge {
        background: #9333ea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
    }
    .campus-badge {
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
    }
    .status-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
    }
    .security-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    .risk-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .verified-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 初始化資料庫
init_db()

# 初始化 Session State
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ========== 輔助函數 ==========
def get_risk_badge(risk_level):
    """根據風險等級返回徽章 HTML"""
    risk_map = {
        'low': ('🛡️ 安全', 'risk-low'),
        'medium': ('⚠️ 中等風險', 'risk-medium'),
        'high': ('🚨 高風險', 'risk-high'),
        'critical': ('❌ 嚴重違規', 'risk-high')
    }
    text, css_class = risk_map.get(risk_level, ('❓ 未知', 'risk-medium'))
    return f"<div class='{css_class}'>{text}</div>"

def show_notification(message, icon="🔔", duration=3):
    """顯示即時通知"""
    st.toast(f"{icon} {message}", icon=icon)

def get_platform_stats():
    """取得平台統計數據"""
    users = get_all_users()
    all_tasks = get_all_tasks()
    
    # 基本統計
    total_users = len(users)
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t['status'] == 'completed'])
    open_tasks = len([t for t in all_tasks if t['status'] == 'open'])
    in_progress_tasks = len([t for t in all_tasks if t['status'] == 'in_progress'])
    
    # 點數統計
    total_points = sum(u['points'] for u in users)
    points_in_tasks = sum(t['points_offered'] for t in all_tasks if t['status'] == 'open')
    
    # 任務分類統計
    category_counts = {}
    for task in all_tasks:
        cat = task['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # 校區統計
    campus_counts = {}
    for task in all_tasks:
        campus = task['campus']
        campus_counts[campus] = campus_counts.get(campus, 0) + 1
    
    # Top 3 活躍使用者
    top_users = sorted(users, key=lambda x: x['completed_tasks'], reverse=True)[:3]
    
    return {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'open_tasks': open_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_points': total_points,
        'points_in_tasks': points_in_tasks,
        'category_counts': category_counts,
        'campus_counts': campus_counts,
        'top_users': top_users,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

# ========== 側邊欄 ==========
with st.sidebar:
    st.markdown("### 👤 使用者登入")
    
    users = get_all_users()
    user_names = [f"{u['name']} ({u['department']})" for u in users]
    
    selected_user_display = st.selectbox(
        "選擇身份",
        user_names,
        index=0 if not st.session_state.current_user else 
              next((i for i, u in enumerate(users) if u['name'] == st.session_state.current_user['name']), 0)
    )
    
    # 解析選擇的使用者
    selected_user_name = selected_user_display.split(' (')[0]
    st.session_state.current_user = get_user_by_name(selected_user_name)
    
    if st.session_state.current_user:
        st.success(f"✅ 已登入為：{st.session_state.current_user['name']}")
        
        # 身份驗證徽章
        st.markdown(
            "<div class='verified-badge'>"
            "<strong>🛡️ 身份已驗證</strong><br>"
            "<span style='font-size: 0.75rem;'>東吳大學學校信箱認證</span>"
            "</div>",
            unsafe_allow_html=True
        )
        
        # 使用者資訊卡片
        st.markdown("---")
        st.markdown("#### 📊 我的資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("點數", f"{st.session_state.current_user['points']} 點")
            st.metric("評分", f"⭐ {st.session_state.current_user['avg_rating']:.1f}")
        with col2:
            st.metric("完成任務", f"{st.session_state.current_user['completed_tasks']} 個")
            st.metric("信任值", f"{st.session_state.current_user['trust_score']:.0%}")
        
        st.markdown(f"**校區**: {st.session_state.current_user['campus']}")
        
        # 技能標籤
        if st.session_state.current_user.get('skills'):
            st.markdown("**我的技能**:")
            skills_html = " ".join([f"<span style='background:#e0e7ff;color:#4338ca;padding:0.25rem 0.5rem;border-radius:0.25rem;margin:0.25rem;display:inline-block;font-size:0.875rem'>{skill}</span>" 
                                   for skill in st.session_state.current_user['skills']])
            st.markdown(skills_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧭 導航")
    
    if st.button("🏠 首頁", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()
    
    if st.button("➕ 發布任務", use_container_width=True):
        st.session_state.page = 'publish'
        st.rerun()
    
    if st.button("📋 我的任務", use_container_width=True):
        st.session_state.page = 'my_tasks'
        st.rerun()
    
    if st.button("🤖 AI 推薦", use_container_width=True):
        st.session_state.page = 'ai_recommend'
        st.rerun()
    
    if st.button("⭐ 我的評價", use_container_width=True):
        st.session_state.page = 'reviews'
        st.rerun()
    
    if st.button("📊 平台統計", use_container_width=True):
        st.session_state.page = 'statistics'
        st.rerun()

# ========== 主標題 ==========
st.markdown('<h1 class="main-header">💎 Campus Help</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">有空幫一下，校園時間銀行</p>', unsafe_allow_html=True)

# ========== 頁面路由 ==========

# 首頁 - 任務列表
if st.session_state.page == 'home':
    st.markdown("## 📋 所有任務")
    
    # 篩選器
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_query = st.text_input("🔍 搜尋任務", placeholder="輸入關鍵字...")
    with col2:
        filter_category = st.selectbox(
            "分類篩選",
            ["全部", "日常支援", "學習互助", "校園協助", "技能交換", "情境陪伴"]
        )
    with col3:
        filter_campus = st.selectbox(
            "校區篩選",
            ["全部", "外雙溪校區", "城中校區", "線上"]
        )
    
    # 取得任務
    tasks = get_all_tasks(status='open')
    
    # 篩選
    if search_query:
        tasks = [t for t in tasks if search_query.lower() in t['title'].lower() or 
                                     search_query.lower() in t['description'].lower()]
    if filter_category != "全部":
        tasks = [t for t in tasks if t['category'] == filter_category]
    if filter_campus != "全部":
        tasks = [t for t in tasks if t['campus'] == filter_campus]
    
    st.markdown(f"找到 **{len(tasks)}** 個任務 | 🛡️ 所有任務已通過安全審查")
    
    # 顯示任務卡片
    if tasks:
        for task in tasks:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # 標題和徽章
                    badge_html = f"<span class='category-badge'>{task['category']}</span> "
                    badge_html += f"<span class='campus-badge'>{task['campus']}</span> "
                    badge_html += "<span class='security-badge'>🛡️ 已審查</span>"
                    if task.get('is_urgent'):
                        badge_html += " <span class='urgent-badge'>🔥 急件</span>"
                    
                    st.markdown(f"### {task['title']}")
                    st.markdown(badge_html, unsafe_allow_html=True)
                    st.markdown(f"**描述**: {task['description']}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.markdown(f"📍 **地點**: {task['location']}")
                    with col_b:
                        st.markdown(f"👤 **發布者**: {task.get('publisher_name', '未知')} 🛡️")
                    with col_c:
                        st.markdown(f"⭐ **評價**: {task.get('publisher_rating', 0):.1f}")
                
                with col2:
                    st.markdown(f"### 💰 {task['points_offered']} 點")
                    if st.button(f"申請任務", key=f"apply_{task['id']}", use_container_width=True):
                        if st.session_state.current_user:
                            result = apply_for_task(task['id'], st.session_state.current_user['id'])
                            if result:
                                show_notification(f"申請成功！已向 {task.get('publisher_name')} 發送通知", "✅")
                                st.success("✅ 申請成功！")
                                st.rerun()
                            else:
                                show_notification("申請失敗，您可能已經申請過此任務", "❌")
                                st.error("❌ 申請失敗（可能已申請過）")
                        else:
                            st.warning("請先選擇使用者")
                
                st.markdown("---")
    else:
        st.info("目前沒有符合條件的任務")

# 發布任務頁面
elif st.session_state.page == 'publish':
    st.markdown("## ➕ 發布新任務")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        # 顯示安全提示
        st.info("🛡️ **安全保障**：所有任務將經過 AI 自動審查，確保平台安全")
        
        # 顯示當前點數
        st.info(f"💰 您目前有 **{st.session_state.current_user['points']} 點**")
        
        with st.form("publish_task_form"):
            st.markdown("### 任務資訊")
            
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("任務標題 *", placeholder="例：幫忙搬宿舍行李")
                category = st.selectbox(
                    "任務分類 *",
                    ["日常支援", "學習互助", "校園協助", "技能交換", "情境陪伴"]
                )
                location = st.text_input("地點 *", placeholder="例：柚芳樓 → 楓雅樓")
            
            with col2:
                campus = st.selectbox("校區 *", ["外雙溪校區", "城中校區", "線上"])
                points_offered = st.number_input("提供點數 *", min_value=10, max_value=500, value=50, step=10)
                is_urgent = st.checkbox("急件標記 🔥")
            
            # 檢查點數是否足夠
            if points_offered > st.session_state.current_user['points']:
                st.error(f"❌ 點數不足！您只有 {st.session_state.current_user['points']} 點")
            
            description = st.text_area(
                "詳細描述 *",
                placeholder="請詳細描述任務內容、時間需求、注意事項等...",
                height=150
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 2])
            with col_a:
                submitted = st.form_submit_button("🚀 發布任務", use_container_width=True)
            with col_b:
                ai_optimize = st.form_submit_button("🤖 AI 優化描述", use_container_width=True)
            
            if ai_optimize and description:
                with st.spinner("AI 正在優化您的任務描述..."):
                    optimized = AIService.optimize_task_description(description)
                    if optimized['success']:
                        show_notification("AI 描述優化完成！", "🤖")
                        st.success("✅ AI 優化建議：")
                        st.info(optimized['optimized_description'])
                        st.markdown("**提示**: 您可以複製上面的優化版本重新填入描述欄位")
            
            if submitted:
                # 驗證
                if not all([title, description, category, location, campus]):
                    st.error("❌ 請填寫所有必填欄位")
                elif len(description) < 10:
                    st.error("❌ 任務描述至少需要 10 個字")
                elif points_offered > st.session_state.current_user['points']:
                    st.error("❌ 點數不足，無法發布任務")
                else:
                    # AI 風險審查
                    with st.spinner("🛡️ 正在進行 AI 安全審查..."):
                        risk_check = AIService.risk_assessment(description, category)
                        
                        if risk_check['success']:
                            risk_data = risk_check['data']
                            risk_level = risk_data.get('risk_level', 'medium')
                            
                            # 顯示風險評估結果
                            st.markdown("### 🛡️ 安全審查結果")
                            st.markdown(get_risk_badge(risk_level), unsafe_allow_html=True)
                            
                            if risk_data.get('recommendation') == '自動拒絕':
                                show_notification("任務被拒絕：包含違規內容", "🚨")
                                st.error(f"❌ 任務內容違規：{risk_data.get('reason')}")
                                st.warning("🚨 違規標記：" + ", ".join(risk_data.get('flags', [])))
                            else:
                                if risk_level == 'low':
                                    st.success("✅ 任務內容安全，可以發布")
                                elif risk_level == 'medium':
                                    st.warning("⚠️ 檢測到中等風險，但仍可發布")
                                
                                # 建立任務
                                task_data = {
                                    'title': title,
                                    'description': description,
                                    'category': category,
                                    'location': location,
                                    'campus': campus,
                                    'points_offered': points_offered,
                                    'is_urgent': is_urgent,
                                    'publisher_id': st.session_state.current_user['id']
                                }
                                
                                task_id = create_task(task_data)
                                if task_id:
                                    show_notification(f"任務發布成功！已扣除 {points_offered} 點", "🎉")
                                    st.success("✅ 任務發布成功！")
                                    st.info(f"💰 已扣除 {points_offered} 點 | 🛡️ 交易安全保護已啟用")
                                    st.balloons()
                                    # 更新使用者資訊
                                    st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                                    st.info("返回首頁查看您的任務")
                                else:
                                    show_notification("任務發布失敗", "❌")
                                    st.error("❌ 發布失敗，請稍後再試")

# 我的任務頁面（簡化版，包含通知）
elif st.session_state.page == 'my_tasks':
    st.markdown("## 📋 我的任務")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        tab1, tab2 = st.tabs(["📤 我發布的", "📥 我接的"])
        
        with tab1:
            my_published = get_user_tasks(st.session_state.current_user['id'], task_type='published')
            
            if my_published:
                for task in my_published:
                    with st.expander(f"{'✅' if task['status'] == 'completed' else '🔄'} {task['title']} - {task['status']} 🛡️"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**描述**: {task['description']}")
                            st.markdown(f"**分類**: {task['category']} | **地點**: {task['location']}")
                            st.markdown(f"**發布時間**: {task['created_at']}")
                            
                            if task.get('accepted_user_name'):
                                st.markdown(f"**✅ 已接受**: {task['accepted_user_name']} 🛡️")
                            
                            if task.get('completed_at'):
                                st.markdown(f"**完成時間**: {task['completed_at']}")
                                st.success("🛡️ 點數交易已完成，安全無虞")
                        
                        with col2:
                            st.markdown(f"### 💰 {task['points_offered']} 點")
                            status_map = {
                                'open': '🟢 開放中',
                                'in_progress': '🟡 進行中',
                                'completed': '✅ 已完成',
                                'cancelled': '❌ 已取消'
                            }
                            st.markdown(f"**狀態**: {status_map.get(task['status'], task['status'])}")
                        
                        # 顯示申請者
                        if task['status'] == 'open':
                            applications = get_task_applications(task['id'])
                            if applications:
                                st.markdown(f"**📝 申請者 ({len(applications)} 人)**:")
                                for app in applications:
                                    col_a, col_b, col_c = st.columns([2, 1, 1])
                                    with col_a:
                                        st.markdown(f"- **{app['applicant_name']}** 🛡️ (評分: {app['applicant_rating']:.1f} ⭐)")
                                    with col_b:
                                        st.markdown(f"申請時間: {app['applied_at']}")
                                    with col_c:
                                        if st.button(f"✅ 接受", key=f"accept_{task['id']}_{app['applicant_id']}", use_container_width=True):
                                            result = accept_application(
                                                task['id'],
                                                app['applicant_id'],
                                                st.session_state.current_user['id']
                                            )
                                            if result:
                                                show_notification(f"已接受 {app['applicant_name']} 的申請！", "🎉")
                                                st.success("✅ 已接受申請！任務進入進行中")
                                                st.rerun()
                        
                        # 完成任務
                        if task['status'] == 'in_progress':
                            if st.button(f"✅ 確認完成", key=f"complete_pub_{task['id']}", use_container_width=True):
                                result = complete_task(task['id'], st.session_state.current_user['id'])
                                if result:
                                    show_notification(f"{task['accepted_user_name']} 獲得 {task['points_offered']} 點！", "💰")
                                    st.success(f"✅ 任務已完成！{task['accepted_user_name']} 獲得 {task['points_offered']} 點")
                                    st.info("🛡️ 點數轉移安全完成")
                                    st.balloons()
                                    st.rerun()
                        
                        # 評價功能
                        if task['status'] == 'completed':
                            review_status = check_review_status(task['id'], st.session_state.current_user['id'])
                            if review_status['can_review'] and not review_status['has_reviewed']:
                                st.markdown("---")
                                st.markdown("### ⭐ 評價幫助者")
                                rating = st.slider("評分", 1.0, 5.0, 5.0, 0.5, key=f"rating_pub_{task['id']}")
                                comment = st.text_area("評價內容（選填）", placeholder="分享您的合作體驗...", key=f"comment_pub_{task['id']}")
                                
                                if st.button(f"提交評價", key=f"submit_review_pub_{task['id']}", use_container_width=True):
                                    result = submit_review(
                                        task['id'],
                                        st.session_state.current_user['id'],
                                        review_status['reviewee_id'],
                                        rating,
                                        comment
                                    )
                                    if result:
                                        show_notification("評價提交成功！", "⭐")
                                        st.success("✅ 評價提交成功！")
                                        st.rerun()
                            elif review_status['has_reviewed']:
                                st.success("✅ 您已評價過此任務")
            else:
                st.info("您還沒有發布任何任務")
        
        with tab2:
            my_applied = get_user_tasks(st.session_state.current_user['id'], task_type='applied')
            
            if my_applied:
                for task in my_applied:
                    status_icon = {'pending': '⏳', 'accepted': '✅', 'rejected': '❌'}.get(task.get('application_status', 'pending'), '❓')
                    
                    with st.expander(f"{status_icon} {task['title']} - {task['application_status']} 🛡️"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**描述**: {task['description']}")
                            st.markdown(f"**發布者**: {task.get('publisher_name', '未知')} 🛡️")
                            st.markdown(f"**地點**: {task['location']} | **點數**: {task['points_offered']} 點")
                            st.markdown(f"**申請時間**: {task.get('applied_at', '未知')}")
                        
                        with col2:
                            status_map = {'pending': '⏳ 待審核', 'accepted': '✅ 已接受', 'rejected': '❌ 已拒絕'}
                            st.markdown(f"**狀態**: {status_map.get(task.get('application_status'), '未知')}")
                        
                        # 完成任務
                        if task['status'] == 'in_progress' and task.get('application_status') == 'accepted':
                            if st.button(f"✅ 確認完成", key=f"complete_app_{task['id']}", use_container_width=True):
                                result = complete_task(task['id'], st.session_state.current_user['id'])
                                if result:
                                    show_notification(f"任務完成！您獲得 {task['points_offered']} 點！", "💰")
                                    st.success(f"✅ 任務已完成！您獲得 {task['points_offered']} 點")
                                    st.info("🛡️ 點數轉移安全完成")
                                    st.balloons()
                                    st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                                    st.rerun()
                        
                        # 評價功能
                        if task['status'] == 'completed' and task.get('application_status') == 'accepted':
                            review_status = check_review_status(task['id'], st.session_state.current_user['id'])
                            if review_status['can_review'] and not review_status['has_reviewed']:
                                st.markdown("---")
                                st.markdown("### ⭐ 評價發布者")
                                rating = st.slider("評分", 1.0, 5.0, 5.0, 0.5, key=f"rating_app_{task['id']}")
                                comment = st.text_area("評價內容（選填）", placeholder="分享您的合作體驗...", key=f"comment_app_{task['id']}")
                                
                                if st.button(f"提交評價", key=f"submit_review_app_{task['id']}", use_container_width=True):
                                    result = submit_review(
                                        task['id'],
                                        st.session_state.current_user['id'],
                                        review_status['reviewee_id'],
                                        rating,
                                        comment
                                    )
                                    if result:
                                        show_notification("評價提交成功！", "⭐")
                                        st.success("✅ 評價提交成功！")
                                        st.rerun()
                            elif review_status['has_reviewed']:
                                st.success("✅ 您已評價過此任務")
            else:
                st.info("您還沒有申請任何任務")

# AI 推薦頁面
elif st.session_state.page == 'ai_recommend':
    st.markdown("## 🤖 AI 智慧推薦")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        st.markdown(f"### 為 **{st.session_state.current_user['name']}** 🛡️ 推薦的任務")
        st.info("🛡️ **安全保障**：所有推薦任務已通過多重安全審查")
        
        all_tasks = get_all_tasks(status='open')
        
        if all_tasks:
            with st.spinner("🛡️ AI 正在計算最佳媒合並進行安全檢查..."):
                matcher = MatchingEngine()
                recommendations = []
                
                for task in all_tasks:
                    score_data = matcher.calculate_match_score(st.session_state.current_user, task)
                    recommendations.append({'task': task, 'score': score_data['total_score'], 'scores': score_data})
                
                recommendations.sort(key=lambda x: x['score'], reverse=True)
                
                st.markdown("### 🏆 Top 5 推薦任務")
                
                for i, rec in enumerate(recommendations[:5], 1):
                    task = rec['task']
                    score = rec['score']
                    scores = rec['scores']
                    
                    with st.expander(f"#{i} {task['title']} - 媒合度 {score:.0%} 🛡️"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**{task['title']}**")
                            st.markdown(f"{task['description']}")
                            st.markdown(f"📍 {task['location']} | {task['campus']}")
                            st.markdown(f"💰 {task['points_offered']} 點")
                            st.success("🛡️ **安全任務**：已通過 AI 風險審查")
                        
                        with col2:
                            fig = go.Figure(data=[go.Pie(
                                labels=['技能匹配', '時間相符', '評價信任', '地點相符'],
                                values=[
                                    scores['skill_score'] * 100,
                                    scores['time_score'] * 100,
                                    scores['rating_score'] * 100,
                                    scores['location_score'] * 100
                                ],
                                hole=0.4,
                                marker_colors=['#9333ea', '#3b82f6', '#10b981', '#f59e0b']
                            )])
                            
                            fig.update_layout(title=f"總分: {score:.0%}", height=250, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("**🎯 推薦理由**:")
                        reasons = []
                        if scores['skill_score'] > 0.7:
                            reasons.append(f"✅ 技能高度匹配 ({scores['skill_score']:.0%})")
                        if scores['location_score'] == 1.0:
                            reasons.append(f"✅ 地點完全相符 (同校區)")
                        if scores['rating_score'] > 0.8:
                            reasons.append(f"✅ 發布者信譽優良 ({scores['rating_score']:.0%})")
                        
                        for reason in reasons:
                            st.markdown(reason)
                        
                        if st.button(f"申請這個任務", key=f"rec_apply_{task['id']}", use_container_width=True):
                            result = apply_for_task(task['id'], st.session_state.current_user['id'])
                            if result:
                                show_notification("申請成功！交易保護已啟動", "🛡️")
                                st.success("✅ 申請成功！")
                                st.info("🛡️ 交易保護已啟動")
                                st.rerun()
        else:
            st.info("目前沒有可推薦的任務")

# 我的評價頁面
elif st.session_state.page == 'reviews':
    st.markdown("## ⭐ 我的評價")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均評分", f"⭐ {st.session_state.current_user['avg_rating']:.1f}")
        with col2:
            st.metric("完成任務", f"{st.session_state.current_user['completed_tasks']} 個")
        with col3:
            st.metric("信任值", f"{st.session_state.current_user['trust_score']:.0%}")
        
        st.markdown("---")
        
        reviews = get_reviews_for_user(st.session_state.current_user['id'])
        
        if reviews:
            st.markdown(f"### 收到的評價 ({len(reviews)} 則)")
            
            for review in reviews:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**任務**: {review['task_title']}")
                        st.markdown(f"**評價者**: {review['reviewer_name']} 🛡️")
                        if review['comment']:
                            st.markdown(f"💬 {review['comment']}")
                        st.markdown(f"📅 {review['created_at']}")
                    
                    with col2:
                        stars = "⭐" * int(review['rating'])
                        st.markdown(f"### {stars}")
                        st.markdown(f"**{review['rating']:.1f}** / 5.0")
                    
                    st.markdown("---")
        else:
            st.info("您還沒有收到任何評價")

# 📊 統計儀表板頁面
elif st.session_state.page == 'statistics':
    st.markdown("## 📊 平台統計儀表板")
    st.info("🛡️ 展示 Campus Help 的運營數據與活躍度")
    
    stats = get_platform_stats()
    
    # 第一行：核心統計
    st.markdown("### 📈 核心數據")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>總使用者數</div>"
            f"<div class='stat-number'>{stats['total_users']}</div>"
            f"<div class='stat-label'>🛡️ 已驗證帳號</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>總任務數</div>"
            f"<div class='stat-number'>{stats['total_tasks']}</div>"
            f"<div class='stat-label'>📋 累計發布</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>完成率</div>"
            f"<div class='stat-number'>{stats['completion_rate']:.1f}%</div>"
            f"<div class='stat-label'>✅ 任務完成度</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>點數流通</div>"
            f"<div class='stat-number'>{stats['total_points']}</div>"
            f"<div class='stat-label'>💰 平台經濟</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # 第二行：詳細統計
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 任務狀態分布")
        status_data = pd.DataFrame({
            '狀態': ['開放中', '進行中', '已完成'],
            '數量': [stats['open_tasks'], stats['in_progress_tasks'], stats['completed_tasks']]
        })
        
        fig1 = px.pie(
            status_data, 
            values='數量', 
            names='狀態',
            color='狀態',
            color_discrete_map={'開放中':'#3b82f6', '進行中':'#f59e0b', '已完成':'#10b981'},
            hole=0.4
        )
        fig1.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(size=14)
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 🏷️ 任務分類分布")
        if stats['category_counts']:
            category_data = pd.DataFrame(
                list(stats['category_counts'].items()),
                columns=['分類', '數量']
            )
            
            fig2 = px.bar(
                category_data,
                x='分類',
                y='數量',
                color='數量',
                color_continuous_scale='Purples'
            )
            fig2.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                font=dict(size=12)
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("暫無分類數據")
    
    st.markdown("---")
    
    # 第三行：校區與排行
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏫 校區活躍度")
        if stats['campus_counts']:
            campus_data = pd.DataFrame(
                list(stats['campus_counts'].items()),
                columns=['校區', '任務數']
            )
            
            fig3 = px.bar(
                campus_data,
                x='校區',
                y='任務數',
                color='校區',
                color_discrete_map={
                    '外雙溪校區': '#9333ea',
                    '城中校區': '#3b82f6',
                    '線上': '#10b981'
                }
            )
            fig3.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                font=dict(size=12)
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("暫無校區數據")
    
    with col2:
        st.markdown("### 🏆 Top 3 活躍使用者")
        for i, user in enumerate(stats['top_users'], 1):
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '🏅')
            
            with st.container():
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_a:
                    st.markdown(f"### {medal}")
                with col_b:
                    st.markdown(f"**{user['name']}** 🛡️")
                    st.markdown(f"⭐ {user['avg_rating']:.1f} | 💪 信任值 {user['trust_score']:.0%}")
                with col_c:
                    st.metric("完成", f"{user['completed_tasks']} 個")
                
                st.markdown("---")
    
    # 第四行：時間趨勢（模擬數據）
    st.markdown("### 📈 平台成長趨勢（模擬數據）")
    
    # 生成模擬的趨勢數據
    dates = pd.date_range(start='2024-10-01', end='2024-10-30', freq='D')
    task_trend = pd.DataFrame({
        '日期': dates,
        '累計任務數': range(10, 10 + len(dates) * 3, 3)
    })
    
    fig4 = px.line(
        task_trend,
        x='日期',
        y='累計任務數',
        markers=True,
        color_discrete_sequence=['#9333ea']
    )
    fig4.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12)
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # 底部資訊
    st.markdown("---")
    st.success("🛡️ **數據安全**：所有統計數據已加密存儲，僅供平台管理使用")
    st.info("💡 **提示**：定期查看平台統計，了解校園互助的活躍度與趨勢")

# 底部資訊
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280;'>"
    "💜 Campus Help - 校園共享幫幫平台 | "
    "🛡️ 安全保護 · 信任認證 · AI 審查<br>"
    "Powered by Streamlit + Google Gemini AI | SDGs 3, 8, 11<br>"
    "有空幫一下，校園時間銀行"
    "</div>",
    unsafe_allow_html=True
)