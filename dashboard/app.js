// =============================================================================
// 🌱 环境科学每日仪表盘 - 生产版本 JavaScript
// 
// 重要配置说明：
// 1. 请将下方第8行的 "YOUR_USERNAME" 替换为您的GitHub用户名
// 2. 确保您的GitHub仓库名为 "daily-env-dashboard"  
// 3. 确保GitHub Actions已成功运行并生成数据文件
// =============================================================================

// 🔧 用户配置 - 请修改这里！
const CONFIG = {
  GITHUB_USERNAME: 'greenliumuqing0-sudo',  // 👈 请替换为您的GitHub用户名！
  REPO_NAME: 'daily-env-dashboard',
  DATA_FILE: 'data/dashboard_data.json',

  // 其他设置
  CACHE_DURATION: 10 * 60 * 1000,   // 10分钟缓存
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 2000,                // 2秒重试延迟
  REQUEST_TIMEOUT: 15000            // 15秒请求超时
};

// 动态生成数据获取URL
function getGitHubDataURL() {
  return `https://raw.githubusercontent.com/${CONFIG.GITHUB_USERNAME}/${CONFIG.REPO_NAME}/main/${CONFIG.DATA_FILE}`;
}

// 全局状态管理
let appState = {
  currentData: null,
  isLoading: false,
  lastFetch: null,
  connectionStatus: 'checking',
  retryCount: 0,
  isConfigured: false
};

// 缓存管理
const CACHE_KEY = 'env_dashboard_data';
const CACHE_TIME_KEY = 'env_dashboard_cache_time';

function getCachedData() {
  try {
    const cachedData = localStorage.getItem(CACHE_KEY);
    const cacheTime = localStorage.getItem(CACHE_TIME_KEY);

    if (cachedData && cacheTime) {
      const cacheAge = Date.now() - parseInt(cacheTime);
      if (cacheAge < CONFIG.CACHE_DURATION) {
        console.log(`📦 使用缓存数据，缓存年龄: ${Math.round(cacheAge / 1000)}秒`);
        return JSON.parse(cachedData);
      }
    }
  } catch (error) {
    console.warn('❌ 读取缓存失败:', error);
  }
  return null;
}

function setCachedData(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data));
    localStorage.setItem(CACHE_TIME_KEY, Date.now().toString());
    console.log('💾 数据已缓存');
  } catch (error) {
    console.warn('❌ 缓存保存失败:', error);
  }
}

// 工具函数
function formatDateTime(dateString) {
  try {
    if (!dateString) return '时间未知';

    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '时间格式错误';

    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Australia/Sydney'
    }) + ' AEST';
  } catch (error) {
    console.error('⏰ 时间格式化错误:', error);
    return '时间解析失败';
  }
}

function updateProgress(percentage) {
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  if (progressFill && progressText) {
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${Math.round(percentage)}%`;
  }
}

function updateLoadingMessage(message) {
  const loadingMessage = document.getElementById('loadingMessage');
  if (loadingMessage) {
    loadingMessage.textContent = message;
  }
}

function updateDataStatus(status, message) {
  const dataStatus = document.getElementById('dataStatus');
  const statusText = document.getElementById('statusText');

  if (dataStatus && statusText) {
    // 移除所有状态类
    dataStatus.className = 'status-indicator';
    dataStatus.classList.add(status);
    statusText.textContent = message;
    appState.connectionStatus = status;
  }
}

// 显示/隐藏加载状态
function showLoading() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.classList.remove('hidden');
  }
  appState.isLoading = true;
}

function hideLoading() {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.classList.add('hidden');
  }
  appState.isLoading = false;
}

// 通知系统
function showNotification(message, type = 'info', duration = 5000) {
  const container = document.getElementById('notificationContainer');
  if (!container) return;

  const notification = document.createElement('div');
  notification.className = `notification ${type}`;

  const icon = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }[type] || 'fas fa-info-circle';

  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 0.75rem;">
      <i class="${icon}"></i>
      <span>${message}</span>
    </div>
  `;

  container.appendChild(notification);

  // 自动移除
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, duration);
}

// 检查配置状态
function checkConfiguration() {
  const isConfigured = CONFIG.GITHUB_USERNAME !== 'YOUR_USERNAME';
  appState.isConfigured = isConfigured;

  if (isConfigured) {
    updateDataStatus('checking', '正在连接数据源...');
    hideConfigBanner();
  } else {
    updateDataStatus('offline', '需要配置GitHub用户名');
    document.getElementById('configStatus').textContent = 
      '请在 app.js 第8行将 "YOUR_USERNAME" 替换为您的实际GitHub用户名';
  }

  return isConfigured;
}

// 配置横幅控制
function hideConfigBanner() {
  const banner = document.getElementById('configBanner');
  if (banner) {
    banner.style.display = 'none';
  }
}

function toggleConfigBanner() {
  const banner = document.getElementById('configBanner');
  const chevron = document.getElementById('configChevron');

  if (banner && chevron) {
    const isVisible = banner.style.display !== 'none';
    banner.style.display = isVisible ? 'none' : 'block';
    chevron.className = isVisible ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
  }
}

function showConfigHelp() {
  const help = document.getElementById('configHelp');
  if (help) {
    help.style.display = help.style.display === 'none' ? 'block' : 'none';
  }
}

// 数据获取函数
async function fetchDashboardData() {
  if (!appState.isConfigured) {
    throw new Error('GitHub用户名未配置');
  }

  const url = getGitHubDataURL();
  console.log(`🔗 获取数据: ${url}`);

  updateProgress(10);
  updateLoadingMessage('连接GitHub数据源...');

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT);

  try {
    updateProgress(30);
    updateLoadingMessage('下载数据文件...');

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      }
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    updateProgress(60);
    updateLoadingMessage('解析数据内容...');

    const data = await response.json();

    updateProgress(80);
    updateLoadingMessage('验证数据格式...');

    // 验证数据格式
    if (!data || typeof data !== 'object') {
      throw new Error('数据格式无效');
    }

    updateProgress(100);
    updateLoadingMessage('数据加载完成');

    console.log('✅ 数据获取成功');
    return data;

  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('请求超时，请检查网络连接');
    } else if (error.message.includes('404')) {
      throw new Error('数据文件不存在，请检查GitHub Actions是否已运行');
    } else if (error.message.includes('403')) {
      throw new Error('访问被拒绝，请检查仓库权限设置');
    } else {
      throw error;
    }
  }
}

// 渲染函数
function renderEnvironmentalNews(newsData) {
  const section = document.getElementById('environmentalSection');
  if (!section || !newsData || !Array.isArray(newsData)) return;

  section.innerHTML = '';

  newsData.forEach(news => {
    const card = document.createElement('div');
    card.className = `news-card ${news.category || 'general'}`;

    card.innerHTML = `
      <div class="news-card-header">
        <h3 class="news-card-title">${news.title || '标题未知'}</h3>
        <span class="urgency-badge ${news.urgency || 'medium'}">${news.urgency || 'medium'}</span>
      </div>
      <p class="news-card-description">${news.description || '暂无描述'}</p>
      <div class="news-card-footer">
        <span><i class="fas fa-building"></i> ${news.source || '来源未知'}</span>
        <span><i class="fas fa-calendar"></i> ${news.date || '日期未知'}</span>
      </div>
    `;

    // 添加点击事件
    if (news.link && news.link !== '#') {
      card.style.cursor = 'pointer';
      card.onclick = () => window.open(news.link, '_blank');
    }

    section.appendChild(card);
  });
}

function renderAITools(toolsData) {
  const section = document.getElementById('aiToolsSection');
  if (!section || !toolsData || !Array.isArray(toolsData)) return;

  section.innerHTML = '';

  toolsData.forEach(tool => {
    const card = document.createElement('div');
    card.className = `tool-card ${(tool.category || 'general').toLowerCase()}`;

    card.innerHTML = `
      <div class="tool-card-header">
        <h3 class="tool-card-title">${tool.name || '工具名称未知'}</h3>
        <p class="tool-card-summary">${tool.summary || '描述未提供'}</p>
      </div>
      <div class="tool-card-content">
        <div class="tool-section">
          <div class="tool-section-title">
            <i class="fas fa-lightbulb"></i> 为什么对您有用
          </div>
          <div class="tool-section-text">${tool.usefulness || '实用性信息暂无'}</div>
        </div>
        <div class="tool-section">
          <div class="tool-section-title">
            <i class="fas fa-cogs"></i> 技术与学习价值
          </div>
          <div class="tool-section-text">${tool.technical || '技术信息暂无'}</div>
        </div>
      </div>
      <div class="tool-card-footer">
        <span class="difficulty-badge">${tool.difficulty || '未知难度'}</span>
        <a href="${tool.link || '#'}" target="_blank" class="btn btn--sm btn--primary">
          <i class="fas fa-external-link-alt"></i> 访问工具
        </a>
      </div>
    `;

    section.appendChild(card);
  });
}

function renderOpportunities(opportunitiesData) {
  const section = document.getElementById('opportunitiesSection');
  if (!section || !opportunitiesData || !Array.isArray(opportunitiesData)) return;

  section.innerHTML = '';

  opportunitiesData.forEach(opp => {
    const card = document.createElement('div');
    card.className = 'opportunity-card';

    card.innerHTML = `
      <div class="opportunity-card-header">
        <h3 class="opportunity-card-title">${opp.title || '机会标题未知'}</h3>
        <div class="opportunity-meta">
          <span class="opportunity-type">${opp.type || '类型未知'}</span>
          <span><i class="fas fa-map-marker-alt"></i> ${opp.location || '地点未知'}</span>
        </div>
      </div>
      <p class="opportunity-description">${opp.description || '描述暂无'}</p>
      <div class="opportunity-details">
        <div class="detail-row">
          <span class="detail-label">机构:</span>
          <span class="detail-value">${opp.organization || '未知机构'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">承诺:</span>
          <span class="detail-value">${opp.commitment || '时间待定'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">技能:</span>
          <span class="detail-value">${opp.skills || '技能要求待定'}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">联系:</span>
          <span class="detail-value">${opp.contact || '联系方式待定'}</span>
        </div>
      </div>
      <div class="opportunity-card-footer">
        <a href="${opp.link || '#'}" target="_blank" class="btn btn--sm btn--primary">
          <i class="fas fa-external-link-alt"></i> 了解详情
        </a>
      </div>
    `;

    section.appendChild(card);
  });
}

// 渲染所有数据
function renderDashboard(data) {
  try {
    console.log('🎨 开始渲染仪表盘数据');

    // 更新页面状态
    const lastUpdated = document.getElementById('lastUpdated');
    if (lastUpdated && data.last_updated) {
      lastUpdated.textContent = `最后更新: ${formatDateTime(data.last_updated)}`;
    }

    // 渲染各个部分
    renderEnvironmentalNews(data.environmental_news || []);
    renderAITools(data.ai_tools || []);
    renderOpportunities(data.opportunities || []);

    // 更新统计信息
    const totalItems = document.getElementById('totalItems');
    if (totalItems && data.metadata) {
      const total = data.metadata.total_items || 0;
      totalItems.textContent = `共 ${total} 条最新资讯`;
    }

    console.log('✅ 仪表盘渲染完成');

  } catch (error) {
    console.error('❌ 渲染仪表盘时出错:', error);
    showNotification('数据渲染失败，请刷新页面重试', 'error');
  }
}

// 主要的数据获取和刷新函数
async function refreshDashboard() {
  if (appState.isLoading) {
    console.log('⏳ 正在加载中，忽略重复请求');
    return;
  }

  console.log('🔄 开始刷新仪表盘数据');

  // 检查配置
  if (!checkConfiguration()) {
    showNotification('请先配置GitHub用户名', 'warning');
    return;
  }

  // 设置加载状态
  appState.isLoading = true;
  appState.retryCount = 0;

  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.classList.add('loading');
  }

  showLoading();
  updateDataStatus('checking', '正在获取最新数据...');

  try {
    updateProgress(0);

    // 尝试获取最新数据
    const data = await fetchDashboardData();

    // 成功获取数据
    appState.currentData = data;
    appState.lastFetch = Date.now();

    // 缓存数据
    setCachedData(data);

    // 渲染界面
    renderDashboard(data);

    // 更新状态
    updateDataStatus('online', '数据连接正常');
    showNotification('数据更新成功！', 'success', 3000);

  } catch (error) {
    console.error('❌ 数据获取失败:', error);

    // 尝试使用缓存数据
    const cachedData = getCachedData();
    if (cachedData) {
      console.log('📦 使用缓存数据作为备用');
      appState.currentData = cachedData;
      renderDashboard(cachedData);
      updateDataStatus('offline', '使用缓存数据');
      showNotification('网络连接失败，显示缓存数据', 'warning');
    } else {
      console.log('❌ 无缓存数据可用');
      updateDataStatus('error', '数据获取失败');
      showNotification(`数据获取失败: ${error.message}`, 'error');

      // 显示错误页面或备用内容
      showFallbackContent();
    }

  } finally {
    // 清理加载状态
    appState.isLoading = false;
    if (refreshBtn) {
      refreshBtn.classList.remove('loading');
    }
    hideLoading();
  }
}

function showFallbackContent() {
  // 显示基础的占位内容
  const sections = ['environmentalSection', 'aiToolsSection', 'opportunitiesSection'];

  sections.forEach(sectionId => {
    const section = document.getElementById(sectionId);
    if (section) {
      section.innerHTML = `
        <div class="placeholder-card">
          <div class="placeholder-content">
            <i class="fas fa-exclamation-triangle placeholder-icon" style="color: var(--warning);"></i>
            <p><strong>数据获取失败</strong></p>
            <p>请检查GitHub仓库配置和网络连接</p>
            <button class="btn btn--sm btn--secondary" onclick="refreshDashboard()" style="margin-top: 1rem;">
              <i class="fas fa-retry"></i> 重试
            </button>
          </div>
        </div>
      `;
    }
  });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 仪表盘应用初始化');

  // 检查配置
  checkConfiguration();

  // 尝试初始加载
  if (appState.isConfigured) {
    // 首先尝试使用缓存数据进行快速渲染
    const cachedData = getCachedData();
    if (cachedData) {
      console.log('📦 使用缓存数据进行初始渲染');
      renderDashboard(cachedData);
      updateDataStatus('online', '显示缓存数据');
    }

    // 然后获取最新数据
    setTimeout(() => {
      refreshDashboard();
    }, 500);
  } else {
    updateDataStatus('offline', '等待配置GitHub用户名');
    showFallbackContent();
  }

  console.log('✅ 仪表盘初始化完成');
});

// 全局函数，供HTML调用
window.refreshDashboard = refreshDashboard;
window.toggleConfigBanner = toggleConfigBanner;
window.showConfigHelp = showConfigHelp;
window.hideConfigBanner = hideConfigBanner;

// 定期检查数据新鲜度
setInterval(() => {
  if (appState.lastFetch && appState.isConfigured) {
    const age = Date.now() - appState.lastFetch;
    if (age > 30 * 60 * 1000) { // 30分钟
      console.log('⏰ 数据较老，建议刷新');
      updateDataStatus('warning', '数据可能已过时，建议刷新');
    }
  }
}, 5 * 60 * 1000); // 每5分钟检查一次
