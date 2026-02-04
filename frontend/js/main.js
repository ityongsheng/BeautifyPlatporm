document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const loginCard = document.getElementById('login-card');
    const onboardingCard = document.getElementById('onboarding-card');
    const mainApp = document.getElementById('main-app');
    const modal = document.getElementById('product-modal');
    const modalBody = document.getElementById('modal-body-content');

    const sections = {
        home: document.getElementById('section-home'),
        rankings: document.getElementById('section-rankings'),
        chat: document.getElementById('section-chat'),
        profile: document.getElementById('section-profile')
    };

    const navLinks = {
        home: document.getElementById('nav-home'),
        rankings: document.getElementById('nav-rankings'),
        chat: document.getElementById('nav-chat'),
        profile: document.getElementById('nav-profile')
    };

    // --- State ---
    let currentUser = { id: 1, username: '美妆达人', skinType: 'normal' };
    let chartInstance = null;

    // --- Init ---
    initNavigation();
    initChat();
    initModal();
    initHomeInteractions();

    // --- Login Flow ---
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        btn.textContent = '验证中...';
        currentUser.username = document.getElementById('username').value || '美妆达人';

        // Sync username to banner
        document.querySelectorAll('.user-name-span').forEach(el => el.textContent = currentUser.username);

        setTimeout(() => {
            loginCard.style.display = 'none';
            onboardingCard.style.display = 'block';
        }, 600);
    });

    // --- Onboarding Quiz ---
    document.querySelectorAll('.choice-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.choice-item').forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            currentUser.skinType = item.dataset.value;
        });
    });

    document.querySelector('.next-step').addEventListener('click', () => {
        const selected = document.querySelector('.choice-item.selected');
        if (!selected) return alert('请选择您的肤质');

        onboardingCard.style.display = 'none';
        mainApp.style.display = 'flex';
        document.getElementById('user-skin-tag').textContent = selected.querySelector('span').textContent;

        loadRecommendations();
    });

    // --- Navigation Logic ---
    function initNavigation() {
        Object.keys(navLinks).forEach(key => {
            navLinks[key].addEventListener('click', (e) => {
                e.preventDefault();
                switchSection(key);
            });
        });
    }

    function switchSection(key) {
        Object.values(sections).forEach(s => s.style.display = 'none');
        Object.values(navLinks).forEach(l => l.classList.remove('active'));

        sections[key].style.display = 'block';
        navLinks[key].classList.add('active');

        if (key === 'chat') sections[key].querySelector('.chat-container').style.display = 'flex';
        if (key === 'rankings') loadRankings();
        if (key === 'profile') loadProfile();
    }
    window.switchSection = switchSection;

    function initHomeInteractions() {
        const tabs = document.querySelectorAll('.tab-item');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                // Simulate filtering
                loadRecommendations();
            });
        });
    }

    // --- Data Fetching & Rendering ---
    async function loadRecommendations() {
        const list = document.getElementById('product-list');
        list.innerHTML = '<div class="product-card"><div class="product-info">分析匹配中...</div></div>';

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/recommend/?user_id=${currentUser.id}`);
            const data = await response.json();
            if (data.recommendations) {
                renderProducts(data.recommendations, 'product-list');
            } else {
                renderMockProducts();
            }
        } catch (err) {
            console.error('API Error:', err);
            renderMockProducts();
        }
    }

    async function loadRankings() {
        const list = document.getElementById('ranking-list');
        list.innerHTML = '<p>榜单加载中...</p>';
        try {
            const response = await fetch('http://127.0.0.1:8000/api/rankings/');
            const data = await response.json();
            renderRankings(data);
        } catch (err) {
            console.error('Rankings Error:', err);
        }
    }

    async function loadProfile() {
        document.getElementById('profile-name').textContent = currentUser.username;
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/user-stats/?user_id=${currentUser.id}`);
            const data = await response.json();
            document.getElementById('profile-skin-badge').textContent = data.skin_type;
            renderRadarChart(data.stats);
        } catch (err) {
            console.error('Profile Error:', err);
        }
    }

    function renderProducts(items, containerId) {
        const list = document.getElementById(containerId);
        list.innerHTML = items.map(p => `
            <div class="product-card" onclick="window.openProductDetail(${p.id || 0})">
                <div class="product-img">🧴</div>
                <div class="product-info">
                    <div class="product-title">${p.title}</div>
                    <div class="product-reason">${p.reason || '热门甄选'}</div>
                    <div style="margin-top: 10px; font-weight: bold; color: var(--accent-color)">
                        ${p.score ? '匹配度: ' + Math.round(p.score * 100) + '%' : '人气热度: 99+'}
                    </div>
                </div>
            </div>
        `).join('');
    }

    function renderRankings(items) {
        const list = document.getElementById('ranking-list');
        list.innerHTML = items.map((p, index) => `
            <div class="ranking-item" onclick="window.openProductDetail(${p.id})">
                <div class="rank-number">${index + 1}</div>
                <div class="rank-img">💄</div>
                <div class="rank-info">
                    <div class="product-title">${p.title}</div>
                    <div class="rank-badge">${p.category}</div>
                </div>
                <div class="rank-score" style="color: var(--accent-color); font-weight:700">评分 ${p.rating_avg}</div>
            </div>
        `).join('');
    }

    function renderMockProducts() {
        const mock = [
            { id: 1, title: '特安舒缓修复霜', reason: '针对您的敏感肤质，该产品含有积雪草成分，显著降低泛红。', score: 0.98 },
            { id: 2, title: '玻尿酸深层补水精华', reason: '检测到由于干燥引起的屏障受损，高浓度B5有助于长效保湿。', score: 0.92 }
        ];
        renderProducts(mock, 'product-list');
    }

    // --- eCharts Radar Chart ---
    function renderRadarChart(stats) {
        if (!chartInstance) {
            chartInstance = echarts.init(document.getElementById('skin-radar-chart'));
        }
        const option = {
            radar: {
                indicator: [
                    { name: '水分', max: 100 },
                    { name: '油分', max: 100 },
                    { name: '敏感度', max: 100 },
                    { name: '弹性', max: 100 },
                    { name: '光泽', max: 100 }
                ],
                splitArea: { show: false }
            },
            series: [{
                type: 'radar',
                data: [{
                    value: [stats.moisture, stats.oil, stats.sensitivity, stats.elasticity, stats.shining],
                    name: '肤质分析',
                    areaStyle: { color: 'rgba(248, 201, 201, 0.5)' },
                    lineStyle: { color: '#f8c9c9' },
                    itemStyle: { color: '#f8c9c9' }
                }]
            }]
        };
        chartInstance.setOption(option);
    }

    // --- Modal Logic ---
    function initModal() {
        document.querySelector('.close-modal').onclick = () => modal.style.display = 'none';
        window.onclick = (event) => { if (event.target == modal) modal.style.display = 'none'; };
    }

    window.openProductDetail = async (id) => {
        if (id === 0) return;
        modal.style.display = 'flex';
        modalBody.innerHTML = '<h3>加载详情中...</h3>';
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/product/${id}/`);
            const p = await response.json();
            modalBody.innerHTML = `
                <div class="detail-img">🧴</div>
                <h2>${p.title}</h2>
                <div class="detail-tags">
                    <span class="tag">品牌: ${p.brand}</span>
                    <span class="tag">分类: ${p.category}</span>
                    <span class="tag">价格: ¥${p.price}</span>
                </div>
                <div class="ai-reason-box">
                    <h4>✨ AI 深度解析</h4>
                    <p><strong>适合肤质：</strong>${p.suitable_skin}</p>
                    <p><strong>核心成分：</strong>${p.ingredients}</p>
                    <p style="margin-top: 10px;"><strong>功效建议：</strong>${p.efficacy}</p>
                </div>
            `;
        } catch (err) {
            modalBody.innerHTML = '<h3>加载详情失败</h3>';
        }
    };

    // --- AI Chat Logic ---
    function initChat() {
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-chat');
        const msgContainer = document.getElementById('chat-messages');

        const sendMessage = async () => {
            const text = input.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            input.value = '';

            const loadingId = 'ai-loading-' + Date.now();
            addMessage('医生正在思考...', 'ai', loadingId);

            try {
                const response = await fetch('http://127.0.0.1:8000/api/chat/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                document.getElementById(loadingId).textContent = data.reply || 'AI 暂时断线了，请稍后再试。';
            } catch (err) {
                document.getElementById(loadingId).textContent = '模型连接失败，请确认后端服务器已启动。';
            }
        };

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());

        function addMessage(text, role, id) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            if (id) div.id = id;
            div.textContent = text;
            msgContainer.appendChild(div);
            msgContainer.scrollTop = msgContainer.scrollHeight;
        }
    }
});
