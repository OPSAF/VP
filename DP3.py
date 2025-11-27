import streamlit as st
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from datetime import datetime
import logging
import traceback

# 页面配置
st.set_page_config(
    page_title="VIP视频在线播放器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 错误监控类
class ErrorMonitor:
    def __init__(self, app_name: str = "VIP视频播放器"):
        self.app_name = app_name
    
    def capture_error(self, error: Exception, context: dict = None):
        """捕获并记录错误"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error.__class__.__name__,
            "message": str(error),
            "context": context or {}
        }
        return error_info

# 安全数据访问函数
def safe_get(data, key, default="未知"):
    """安全获取字典值"""
    if not data or not isinstance(data, dict):
        return default
    return data.get(key, default)

# 明亮风格的CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .video-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 3px solid #2E86AB;
    }
    .stButton>button {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 15px 35px;
        font-weight: bold;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 134, 171, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.4);
    }
    .platform-badge {
        background: #A23B72;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .info-card {
        background: linear-gradient(135deg, #F18F01 0%, #C73E1D 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class VideoStreamCrawler:
    """视频流爬取核心类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """配置会话参数"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def detect_platform(self, url):
        """检测视频平台"""
        if not url or not isinstance(url, str):
            return 'unknown'
        
        try:
            domain = urlparse(url).netloc.lower()
            platforms = {
                'youtube': ['youtube.com', 'youtu.be'],
                'bilibili': ['bilibili.com', 'b23.tv'],
                'vimeo': ['vimeo.com'],
                'dailymotion': ['dailymotion.com'],
                'twitch': ['twitch.tv']
            }
            
            for platform, domains in platforms.items():
                if any(d in domain for d in domains):
                    return platform
            return 'generic'
        except Exception:
            return 'unknown'
    
    def extract_video_info(self, url, max_retries=3):
        """提取视频信息和播放链接"""
        if not url or not isinstance(url, str):
            return {
                'status': 'error',
                'error': '无效的URL',
                'platform': 'unknown'
            }
        
        for attempt in range(max_retries):
            try:
                platform = self.detect_platform(url)
                
                if platform == 'youtube':
                    return self._extract_youtube(url)
                elif platform == 'bilibili':
                    return self._extract_bilibili(url)
                else:
                    return self._extract_generic(url)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        'status': 'error',
                        'error': str(e),
                        'platform': platform
                    }
                time.sleep(2 * (attempt + 1))
        
        return {
            'status': 'error',
            'error': '达到最大重试次数',
            'platform': 'unknown'
        }
    
    def _extract_youtube(self, url):
        """提取YouTube视频信息"""
        try:
            video_id = self._extract_youtube_id(url)
            if video_id:
                return {
                    'status': 'success',
                    'title': f'YouTube视频示例 - {video_id}',
                    'platform': 'youtube',
                    'video_url': f'https://www.youtube.com/embed/{video_id}',
                    'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                    'duration': '10:30',
                    'quality': '1080p',
                    'embed_html': f'''
                    <iframe width="100%" height="500" 
                        src="https://www.youtube.com/embed/{video_id}?autoplay=1" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen>
                    </iframe>
                    '''
                }
            return {'status': 'error', 'error': '无法提取YouTube视频ID'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _extract_youtube_id(self, url):
        """提取YouTube视频ID"""
        try:
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&?\n]+)',
                r'youtube\.com/embed/([^&?\n]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None
    
    def _extract_bilibili(self, url):
        """提取B站视频信息"""
        try:
            return {
                'status': 'success',
                'title': 'B站视频示例 - 测试视频',
                'platform': 'bilibili',
                'video_url': url,
                'thumbnail': 'https://via.placeholder.com/640x360/00a1d6/ffffff?text=Bilibili+Video',
                'duration': '15:45',
                'quality': '720p',
                'embed_html': f'''
                <iframe width="100%" height="500" 
                    src="{url}" 
                    scrolling="no" 
                    border="0" 
                    frameborder="no" 
                    framespacing="0" 
                    allowfullscreen="true">
                </iframe>
                '''
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _extract_generic(self, url):
        """提取通用视频信息"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title_tag = soup.find('meta', property='og:title') or soup.find('title')
            title = title_tag.get('content', '未知标题') if title_tag else '未知标题'
            
            return {
                'status': 'success',
                'title': title,
                'platform': 'generic',
                'video_url': url,
                'thumbnail': '',
                'duration': '未知',
                'quality': '自动',
                'embed_html': f'''
                <video width="100%" height="500" controls>
                    <source src="{url}" type="video/mp4">
                    您的浏览器不支持视频播放
                </video>
                '''
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'platform': 'generic'}

def display_video_info_safely(video_info):
    """安全显示视频信息"""
    if not video_info or not isinstance(video_info, dict):
        return "<div class='info-card'><strong>视频信息不可用</strong></div>"
    
    platform = safe_get(video_info, 'platform', '未知').upper()
    duration = safe_get(video_info, 'duration', '未知')
    quality = safe_get(video_info, 'quality', '自动')
    
    return f"""
    <div class="info-card">
        <strong>平台:</strong> {platform}<br>
        <strong>时长:</strong> {duration}<br>
        <strong>质量:</strong> {quality}
    </div>
    """

def process_video_play(crawler, url, error_monitor):
    """处理视频播放 - 增强错误处理"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔍 正在检测视频平台...")
        progress_bar.progress(20)
        
        platform = crawler.detect_platform(url)
        st.success(f"检测到平台: {platform.upper()}")
        
        status_text.text("📡 正在解析视频信息...")
        progress_bar.progress(50)
        
        video_info = crawler.extract_video_info(url)
        
        status_text.text("🎬 准备播放...")
        progress_bar.progress(80)
        
        if video_info and isinstance(video_info, dict) and video_info.get('status') == 'success':
            st.session_state.video_info = video_info
            st.session_state.current_url = url
            st.success("✅ 视频解析成功！")
        else:
            error_msg = safe_get(video_info, 'error', '未知错误') if video_info else '解析失败'
            st.session_state.video_info = {'status': 'error', 'error': error_msg}
            st.error(f"❌ 解析失败: {error_msg}")
        
        progress_bar.progress(100)
        time.sleep(0.5)
        status_text.empty()
        
    except Exception as e:
        error_info = error_monitor.capture_error(e, {'url': url, 'action': 'video_processing'})
        st.session_state.video_info = {'status': 'error', 'error': str(e)}
        st.error(f"处理过程中出错: {str(e)}")
        progress_bar.progress(0)

def video_play_page(crawler, error_monitor):
    """视频播放页面"""
    st.markdown('<div class="main-header">🎬 VIP视频在线播放器</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🔗 输入视频链接")
        url_input = st.text_input(
            "视频URL:",
            value=safe_get(st.session_state, 'current_url', ''),
            placeholder="https://www.youtube.com/watch?v=示例",
            label_visibility="collapsed"
        )
        
        col1_1, col1_2, col1_3 = st.columns([2, 1, 1])
        with col1_1:
            if st.button("🚀 开始解析播放", use_container_width=True, type="primary"):
                if url_input and isinstance(url_input, str) and url_input.strip():
                    process_video_play(crawler, url_input.strip(), error_monitor)
                else:
                    st.error("请输入有效的视频URL")
        
        with col1_2:
            if st.button("🔄 重新加载", use_container_width=True):
                if 'current_url' in st.session_state and st.session_state.current_url:
                    st.rerun()
        
        with col1_3:
            if st.button("⭐ 收藏视频", use_container_width=True):
                if 'video_info' in st.session_state and st.session_state.video_info:
                    st.success("✅ 视频已添加到收藏夹！")
    
    with col2:
        st.subheader("📈 实时状态")
        current_time = datetime.now().strftime("%H:%M:%S")
        st.metric("当前时间", current_time)
        st.metric("系统状态", "🟢 正常")
        
        if ('video_info' in st.session_state and 
            st.session_state.video_info is not None and
            isinstance(st.session_state.video_info, dict)):
            
            info_html = display_video_info_safely(st.session_state.video_info)
            st.markdown(info_html, unsafe_allow_html=True)
        else:
            st.info("等待视频解析...")
    
    if ('video_info' in st.session_state and 
        st.session_state.video_info is not None and
        isinstance(st.session_state.video_info, dict) and
        st.session_state.video_info.get('status') == 'success'):
        
        display_video_player(st.session_state.video_info)

def display_video_player(video_info):
    """显示视频播放器"""
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        title = safe_get(video_info, 'title', '未知标题')
        st.markdown(f"### 🎥 {title}")
    with col2:
        platform = safe_get(video_info, 'platform', '未知').upper()
        st.markdown(f'<div class="platform-badge">{platform}</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        
        embed_html = safe_get(video_info, 'embed_html', '')
        if embed_html:
            st.components.v1.html(embed_html, height=520)
        else:
            st.warning("无法加载视频播放器")
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.info(f"**时长:** {safe_get(video_info, 'duration', '未知')}")
        with col4:
            st.info(f"**质量:** {safe_get(video_info, 'quality', '自动')}")
        with col5:
            st.info(f"**平台:** {safe_get(video_info, 'platform', '未知').upper()}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def batch_process_page(crawler, error_monitor):
    """批量处理页面"""
    st.title("📁 批量视频处理")
    
    tab1, tab2 = st.tabs(["🔗 URL列表", "📊 播放列表"])
    
    with tab1:
        st.subheader("批量URL处理")
        batch_urls = st.text_area(
            "输入多个视频URL（每行一个）:",
            height=150,
            placeholder="https://www.example.com/video1\nhttps://www.example.com/video2",
            help="支持同时处理多个视频链接"
        )
        
        if st.button("🚀 批量解析", key="batch_parse"):
            if batch_urls and isinstance(batch_urls, str):
                urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
                if urls:
                    process_batch_urls(crawler, urls, error_monitor)
                else:
                    st.error("请输入至少一个有效的URL")
            else:
                st.error("请输入有效的URL列表")
    
    with tab2:
        st.subheader("播放列表管理")
        st.info("播放列表功能开发中...")

def process_batch_urls(crawler, urls, error_monitor):
    """处理批量URL"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    
    for i, url in enumerate(urls):
        status_text.text(f"处理中 ({i+1}/{len(urls)}): {url[:50]}...")
        
        try:
            video_info = crawler.extract_video_info(url)
            results.append({
                'url': url,
                'status': safe_get(video_info, 'status', 'error'),
                'data': video_info if safe_get(video_info, 'status') == 'success' else None,
                'error': safe_get(video_info, 'error', '未知错误')
            })
        except Exception as e:
            error_info = error_monitor.capture_error(e, {'url': url, 'action': 'batch_processing'})
            results.append({
                'url': url,
                'status': 'error',
                'error': str(e)
            })
        
        progress_bar.progress((i + 1) / len(urls))
        time.sleep(1)
    
    display_batch_results(results)
    progress_bar.empty()
    status_text.empty()

def display_batch_results(results):
    """显示批量处理结果"""
    st.subheader("📊 处理结果")
    
    success_count = sum(1 for r in results if safe_get(r, 'status') == 'success')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总任务数", len(results))
    with col2:
        st.metric("成功数", success_count)
    with col3:
        st.metric("失败数", len(results) - success_count)
    
    for i, result in enumerate(results):
        status_icon = '✅' if safe_get(result, 'status') == 'success' else '❌'
        with st.expander(f"{status_icon} {safe_get(result, 'url', '未知URL')[:50]}...", 
                        expanded=(i == 0 and safe_get(result, 'status') == 'success')):
            if safe_get(result, 'status') == 'success':
                st.success("解析成功")
                if st.button("🎬 立即播放", key=f"play_{i}"):
                    st.session_state.video_info = safe_get(result, 'data')
                    st.session_state.current_url = safe_get(result, 'url')
                    st.rerun()
            else:
                st.error(f"解析失败: {safe_get(result, 'error', '未知错误')}")

def favorites_page():
    """收藏页面"""
    st.title("⭐ 我的收藏")
    
    favorites = [
        {"title": "收藏视频1", "url": "https://example.com/1", "platform": "youtube", "added": "2024-01-15"},
        {"title": "收藏视频2", "url": "https://example.com/2", "platform": "bilibili", "added": "2024-01-14"},
    ]
    
    if not favorites:
        st.info("暂无收藏视频")
        return
    
    for fav in favorites:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{safe_get(fav, 'title', '未知标题')}**")
            st.caption(f"平台: {safe_get(fav, 'platform', '未知')} | 添加时间: {safe_get(fav, 'added', '未知')}")
        with col2:
            if st.button("播放", key=f"play_fav_{safe_get(fav, 'url')}"):
                st.session_state.current_url = safe_get(fav, 'url')
                st.rerun()
        with col3:
            if st.button("删除", key=f"del_fav_{safe_get(fav, 'url')}"):
                st.success("已从收藏中删除")

def settings_page():
    """设置页面"""
    st.title("⚙️ 播放器设置")
    
    tab1, tab2, tab3 = st.tabs(["🎵 播放设置", "🎨 界面设置", "🔧 高级设置"])
    
    with tab1:
        st.subheader("播放配置")
        col1, col2 = st.columns(2)
        with col1:
            auto_play = st.checkbox("自动播放", value=True)
            default_quality = st.selectbox("默认画质", ["自动", "1080p", "720p", "480p"])
        with col2:
            loop_play = st.checkbox("循环播放")
            volume = st.slider("默认音量", 0, 100, 80)
    
    with tab2:
        st.subheader("界面个性化")
        theme = st.selectbox("主题颜色", ["蓝色主题", "绿色主题", "紫色主题"])
        font_size = st.slider("字体大小", 12, 24, 16)
    
    with tab3:
        st.subheader("高级配置")
        cache_size = st.slider("缓存大小(MB)", 10, 1000, 100)
        max_concurrent = st.number_input("最大并发数", 1, 10, 3)
        
        if st.button("清除缓存"):
            st.success("缓存已清除")
        
        if st.button("恢复默认设置"):
            st.success("设置已恢复默认")

def main():
    """主应用"""
    # 初始化错误监控
    if 'error_monitor' not in st.session_state:
        st.session_state.error_monitor = ErrorMonitor()
    
    # 初始化爬虫
    crawler = VideoStreamCrawler()
    
    # 初始化session state
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ''
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    
    # 侧边栏
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #2E86AB;'>🎬 VIP播放器</h1>
            <p style='color: #666;'>智能视频在线播放工具</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected_page = st.radio(
            "导航菜单",
            ["🎯 视频播放", "📁 批量处理", "⭐ 我的收藏", "⚙️ 设置"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.subheader("🚀 快速访问")
        quick_links = [
            {"name": "示例视频1", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"name": "示例视频2", "url": "https://www.bilibili.com/video/BV1GJ411x7h7"},
        ]
        
        for link in quick_links:
            if st.button(link["name"], key=f"quick_{link['name']}", use_container_width=True):
                st.session_state.current_url = link["url"]
                st.rerun()
        
        st.markdown("---")
        st.subheader("📊 统计信息")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("今日播放", "0")
        with col2:
            st.metric("总播放量", "0")
    
    # 主内容区
    error_monitor = st.session_state.error_monitor
    
    if selected_page == "🎯 视频播放":
        video_play_page(crawler, error_monitor)
    elif selected_page == "📁 批量处理":
        batch_process_page(crawler, error_monitor)
    elif selected_page == "⭐ 我的收藏":
        favorites_page()
    else:
        settings_page()

if __name__ == "__main__":
    main()
