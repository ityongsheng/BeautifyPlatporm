const API_BASE = 'http://127.0.0.1:8000/api/admin';

async function fetchStats() {
    const res = await fetch(`${API_BASE}/stats/`);
    const data = await res.json();
    renderCTR(data.ctr_data);
    renderAICost(data.ai_usage);
    renderUserDist(data.user_distribution);
}

function renderCTR(data) {
    const chart = echarts.init(document.getElementById('ctr-chart'));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.dates, axisLine: { lineStyle: { color: '#64748b' } } },
        yAxis: { type: 'value', axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#334155' } } },
        series: [{
            data: data.values,
            type: 'line',
            smooth: true,
            color: '#38bdf8',
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(56, 189, 248, 0.3)' },
                    { offset: 1, color: 'rgba(56, 189, 248, 0)' }
                ])
            }
        }]
    });
}

function renderAICost(data) {
    const chart = echarts.init(document.getElementById('ai-cost-chart'));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { textStyle: { color: '#ccc' }, bottom: 0 },
        xAxis: { type: 'category', data: ['一', '二', '三', '四', '五', '六', '日'], axisLine: { lineStyle: { color: '#64748b' } } },
        yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#334155' } } },
        series: [
            { name: 'Token消耗', type: 'bar', stack: 'total', data: data.daily_usage, color: '#0ea5e9' },
            { name: '延迟 (ms)', type: 'line', yAxisIndex: 0, data: [200, 450, 300, 800, 600, 1100, data.avg_latency], color: '#f59e0b' }
        ]
    });
}

function renderUserDist(data) {
    const chart = echarts.init(document.getElementById('user-dist-chart'));
    chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 10, borderColor: '#1e293b', borderWidth: 2 },
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' } },
            data: data
        }]
    });
}

async function fetchLogs() {
    const res = await fetch(`${API_BASE}/logs/`);
    const logs = await res.json();
    const tbody = document.querySelector('#log-table tbody');
    tbody.innerHTML = logs.map(l => `
        <tr>
            <td><strong>${l.user}</strong><br><small style="opacity:0.5">${l.created_at}</small></td>
            <td>${l.input}</td>
            <td>
                <div id="ai-res-${l.id}">${l.response}</div>
                ${l.is_corrected ? `<span class="corrected-tag">✓ 已纠偏: ${l.corrected_response}</span>` : ''}
            </td>
            <td>
                <button class="correction-btn" onclick="correctLog(${l.id})">纠偏</button>
            </td>
        </tr>
    `).join('');
}

async function correctLog(id) {
    const correction = prompt("请输入正确或优化的AI回答：");
    if (!correction) return;

    const res = await fetch(`${API_BASE}/logs/${id}/correct/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correction })
    });

    if (res.ok) {
        alert("纠偏记录成功！");
        fetchLogs();
    }
}

// Initial Load
fetchStats();
fetchLogs();
setInterval(fetchStats, 60000); // 1 min refresh
