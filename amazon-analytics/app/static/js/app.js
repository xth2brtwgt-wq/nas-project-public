// Amazon Analytics Dashboard JavaScript

let categoryChart = null;

// サブフォルダパスを取得（window.SUBFOLDER_PATHが設定されている場合）
const subfolderPath = window.SUBFOLDER_PATH || '';

// APIエンドポイントのパスを生成するヘルパー関数
function apiPath(path) {
    const apiPath = path.startsWith('/') ? path : `/${path}`;
    return `${subfolderPath}${apiPath}`;
}

// Tab switching
document.addEventListener('DOMContentLoaded', function() {
    // Tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // File upload
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
    
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Load initial data
    loadStatistics();
    loadCategories();
    loadImportHistory();
});

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load tab-specific data
    if (tabName === 'purchases') {
        loadPurchases();
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(apiPath('/api/statistics'), {
            credentials: 'include',  // Cookieを含める
            redirect: 'manual'  // リダイレクトを手動で処理
        });
        
        // リダイレクトの場合は処理しない
        if (response.status === 307 || response.status === 302) {
            const location = response.headers.get('Location');
            if (location && location.includes('/login')) {
                console.log('認証が必要です。ログインページにリダイレクトします:', location);
                window.location.href = location;
                return;
            }
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update stats
        document.getElementById('total-spent').textContent = 
            '¥' + data.total_spent.toLocaleString('ja-JP', {maximumFractionDigits: 0});
        document.getElementById('total-purchases').textContent = 
            data.total_purchases.toLocaleString('ja-JP');
        document.getElementById('unique-orders').textContent = 
            data.unique_orders.toLocaleString('ja-JP');
        
        if (data.date_range.start && data.date_range.end) {
            const start = new Date(data.date_range.start).toLocaleDateString('ja-JP');
            const end = new Date(data.date_range.end).toLocaleDateString('ja-JP');
            document.getElementById('date-range').textContent = `${start} - ${end}`;
        }
        
        // Update category chart
        if (data.categories && data.categories.length > 0) {
            updateCategoryChart(data.categories);
        }
        
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

function updateCategoryChart(categories) {
    const ctx = document.getElementById('category-chart');
    
    // Filter out categories with no purchases
    const filteredCategories = categories.filter(cat => cat.total > 0);
    
    const labels = filteredCategories.map(cat => cat.name);
    const data = filteredCategories.map(cat => cat.total);
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384',
                    '#C9CBCF'
                ],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return label + ': ¥' + value.toLocaleString('ja-JP', {maximumFractionDigits: 0});
                        }
                    }
                }
            }
        }
    });
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    if (!file.name.endsWith('.csv')) {
        alert('CSVファイルのみアップロード可能です');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const statusDiv = document.getElementById('upload-status');
    const statusText = statusDiv.querySelector('.status-text');
    const progressFill = statusDiv.querySelector('.progress-fill');
    
    statusDiv.style.display = 'block';
    statusText.textContent = 'アップロード中...';
    progressFill.style.width = '50%';
    
    try {
        const response = await fetch(apiPath('/api/upload'), {
            method: 'POST',
            body: formData,
            credentials: 'include'  // Cookieを含める
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            progressFill.style.width = '100%';
            statusText.textContent = `✓ 成功: ${result.record_count}件のデータをインポートしました`;
            statusText.className = 'status-text status-success';
            
            // Refresh data
            setTimeout(() => {
                loadStatistics();
                loadImportHistory();
                statusDiv.style.display = 'none';
                progressFill.style.width = '0%';
            }, 2000);
        } else {
            throw new Error(result.detail || 'アップロードに失敗しました');
        }
    } catch (error) {
        progressFill.style.width = '100%';
        progressFill.style.background = '#dc3545';
        statusText.textContent = '✗ エラー: ' + error.message;
        statusText.className = 'status-text status-error';
    }
}

async function loadImportHistory() {
    try {
        const response = await fetch(apiPath('/api/import-history'), {
            credentials: 'include'  // Cookieを含める
        });
        const data = await response.json();
        
        const listDiv = document.getElementById('import-history-list');
        
        if (data.history.length === 0) {
            listDiv.innerHTML = '<p style="color: #666;">インポート履歴がありません</p>';
            return;
        }
        
        listDiv.innerHTML = data.history.map(item => `
            <div class="history-item">
                <div><strong>${item.filename}</strong></div>
                <div style="color: #666; font-size: 0.9rem;">
                    ${new Date(item.import_date).toLocaleString('ja-JP')} - 
                    ${item.record_count}件 - 
                    <span class="${item.status === 'success' ? 'status-success' : 'status-error'}">${item.status}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load import history:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(apiPath('/api/categories'), {
            credentials: 'include'  // Cookieを含める
        });
        const data = await response.json();
        
        const select = document.getElementById('category-filter');
        select.innerHTML = '<option value="">全カテゴリ</option>';
        
        data.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name;
            option.textContent = cat.name;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

async function loadPurchases() {
    const category = document.getElementById('category-filter').value;
    
    try {
        let url = apiPath('/api/purchases?limit=50');
        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
        }
        
        const response = await fetch(url, {
            credentials: 'include',  // Cookieを含める
            redirect: 'manual'  // リダイレクトを手動で処理
        });
        
        // リダイレクトの場合は処理しない
        if (response.status === 307 || response.status === 302) {
            const location = response.headers.get('Location');
            if (location && location.includes('/login')) {
                console.log('認証が必要です。ログインページにリダイレクトします:', location);
                window.location.href = location;
                return;
            }
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        const listDiv = document.getElementById('purchases-list');
        
        if (data.items.length === 0) {
            listDiv.innerHTML = '<p style="padding: 20px; text-align: center; color: #666;">購入履歴がありません</p>';
            return;
        }
        
        listDiv.innerHTML = data.items.map(item => `
            <div class="purchase-item">
                <div>
                    <div class="purchase-name">${item.product_name}</div>
                    <div class="purchase-date">${new Date(item.order_date).toLocaleDateString('ja-JP')}</div>
                    ${item.category ? `<span style="background: #ff9900; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8rem;">${item.category}</span>` : ''}
                </div>
                <div style="text-align: center;">数量: ${item.quantity}</div>
                <div class="purchase-price">¥${item.total_owed.toLocaleString('ja-JP', {maximumFractionDigits: 0})}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Failed to load purchases:', error);
    }
}

async function autoClassify() {
    if (!confirm('AI分類を実行しますか？（Gemini APIキーが必要です）')) {
        return;
    }
    
    // ボタンを無効化して処理中状態を表示
    const classifyButton = document.querySelector('button[onclick="autoClassify()"]');
    const originalText = classifyButton.textContent;
    const originalOnclick = classifyButton.onclick;
    
    classifyButton.disabled = true;
    classifyButton.textContent = '🔄 AI分類実行中...';
    classifyButton.onclick = null;
    
    // 進捗表示エリアを作成
    const progressArea = document.createElement('div');
    progressArea.id = 'classification-progress';
    progressArea.style.cssText = `
        margin: 20px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    `;
    progressArea.innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="width: 20px; height: 20px; border: 2px solid #007bff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
            <strong>AI分類を実行中...</strong>
        </div>
        <div id="progress-details" style="color: #666; font-size: 0.9rem;">
            商品を分析してカテゴリを自動分類しています。時間がかかる場合があります。
        </div>
    `;
    
    // スピナーアニメーションのCSSを追加
    if (!document.getElementById('spinner-style')) {
        const style = document.createElement('style');
        style.id = 'spinner-style';
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // 進捗エリアを挿入
    const analysisSection = document.querySelector('.analysis-section');
    analysisSection.appendChild(progressArea);
    
    try {
        const response = await fetch(apiPath('/api/analyze/classify'), {
            method: 'POST',
            credentials: 'include'  // Cookieを含める
        });
        
        const result = await response.json();
        
        if (response.ok) {
            progressArea.innerHTML = `
                <div style="color: #28a745; display: flex; align-items: center;">
                    <span style="font-size: 1.2em; margin-right: 8px;">✅</span>
                    <strong>分類が完了しました！</strong>
                </div>
                <div style="margin-top: 10px; color: #666;">
                    統計データを更新しています...
                </div>
            `;
            
            // 統計データを更新
            await loadStatistics();
            
            // 2秒後に進捗エリアを削除
            setTimeout(() => {
                progressArea.remove();
            }, 2000);
        } else {
            // 日次制限エラーの場合の特別な処理
            if (result.detail && result.detail.includes('Daily quota limit')) {
                throw new Error('Gemini APIの日次制限に達しました。明日までお待ちください。');
            }
            throw new Error(result.detail || '分類に失敗しました');
        }
    } catch (error) {
        // 日次制限エラーの場合は特別な表示
        const isDailyQuotaError = error.message.includes('日次制限');
        
        progressArea.innerHTML = `
            <div style="color: #dc3545; display: flex; align-items: center;">
                <span style="font-size: 1.2em; margin-right: 8px;">${isDailyQuotaError ? '⏰' : '❌'}</span>
                <strong>${isDailyQuotaError ? 'API制限に達しました' : 'エラーが発生しました'}</strong>
            </div>
            <div style="margin-top: 10px; color: #666;">
                ${error.message}
            </div>
            ${isDailyQuotaError ? `
                <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; color: #856404;">
                    <strong>💡 解決方法:</strong><br>
                    • 明日までお待ちください<br>
                    • または、Gemini APIの有料プランにアップグレードしてください
                </div>
            ` : ''}
        `;
    } finally {
        // ボタンを元に戻す
        classifyButton.disabled = false;
        classifyButton.textContent = originalText;
        classifyButton.onclick = originalOnclick;
    }
}

async function analyzeImpulse() {
    const resultsDiv = document.getElementById('impulse-results');
    resultsDiv.innerHTML = `
        <div style="display: flex; align-items: center; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <div style="width: 16px; height: 16px; border: 2px solid #007bff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
            <span>衝動買いパターンを分析中...</span>
        </div>
    `;
    
    try {
        const response = await fetch(apiPath('/api/analyze/impulse'), {
            credentials: 'include'  // Cookieを含める
        });
        const data = await response.json();
        
        if (data.detected_patterns.length === 0) {
            resultsDiv.innerHTML = '<div class="results">衝動買いパターンは検出されませんでした 👍</div>';
            return;
        }
        
        resultsDiv.innerHTML = `
            <div class="results">
                <h4>検出されたパターン: ${data.pattern_count}件</h4>
                ${data.detected_patterns.map(pattern => `
                    <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px;">
                        <strong>${pattern.category}</strong><br>
                        週${pattern.week}: ${pattern.purchase_count}回の購入<br>
                        合計: ¥${pattern.total_amount.toLocaleString('ja-JP', {maximumFractionDigits: 0})}<br>
                        <div style="margin-top: 10px; font-size: 0.9rem; color: #666;">
                            ${pattern.products.slice(0, 3).join(', ')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        resultsDiv.innerHTML = '<div class="results status-error">エラー: ' + error.message + '</div>';
    }
}

async function analyzeRecurring() {
    const resultsDiv = document.getElementById('recurring-results');
    resultsDiv.innerHTML = `
        <div style="display: flex; align-items: center; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <div style="width: 16px; height: 16px; border: 2px solid #007bff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
            <span>定期購入パターンを分析中...</span>
        </div>
    `;
    
    try {
        const response = await fetch(apiPath('/api/analyze/recurring'), {
            credentials: 'include'  // Cookieを含める
        });
        const data = await response.json();
        
        if (data.recurring_purchases.length === 0) {
            resultsDiv.innerHTML = '<div class="results">定期購入パターンは検出されませんでした</div>';
            return;
        }
        
        resultsDiv.innerHTML = `
            <div class="results">
                <h4>定期購入候補: ${data.recurring_purchases.length}件</h4>
                ${data.recurring_purchases.slice(0, 10).map(item => `
                    <div style="margin: 15px 0; padding: 15px; background: white; border-radius: 5px;">
                        <strong>${item.product_name.slice(0, 80)}</strong><br>
                        購入回数: ${item.purchase_count}回<br>
                        平均間隔: ${item.avg_interval_days}日<br>
                        合計支出: ¥${item.total_spent.toLocaleString('ja-JP', {maximumFractionDigits: 0})}
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        resultsDiv.innerHTML = '<div class="results status-error">エラー: ' + error.message + '</div>';
    }
}

async function generateInsights() {
    const year = document.getElementById('insight-year').value;
    const month = document.getElementById('insight-month').value;
    const resultsDiv = document.getElementById('insights-results');
    
    resultsDiv.innerHTML = `
        <div style="display: flex; align-items: center; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <div style="width: 16px; height: 16px; border: 2px solid #007bff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
            <span>AI分析中...（少々お待ちください）</span>
        </div>
    `;
    
    try {
        const response = await fetch(apiPath(`/api/analyze/monthly-insights?year=${year}&month=${month}`), {
            credentials: 'include'  // Cookieを含める
        });
        const data = await response.json();
        
        resultsDiv.innerHTML = `
            <div class="results">
                <h4>${year}年${month}月の分析結果</h4>
                <div style="white-space: pre-wrap; line-height: 1.8;">${data.insights}</div>
            </div>
        `;
        
    } catch (error) {
        resultsDiv.innerHTML = '<div class="results status-error">エラー: ' + error.message + '</div>';
    }
}

