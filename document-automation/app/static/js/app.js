// ドキュメント自動処理システム - フロントエンドロジック

let selectedDocuments = new Set();
let currentDocumentId = null;

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadSystemStatus();
    loadStatistics();
    loadDocuments();
    loadCategories();
    setupEventListeners();
    setupRAGEventListeners();
    loadRAGFilters();
    loadRAGHistory();
    
    // 5秒ごとに統計情報を更新
    setInterval(loadStatistics, 5000);
});

// イベントリスナー設定
function setupEventListeners() {
    document.getElementById('upload-btn').addEventListener('click', uploadFiles);
    document.getElementById('refresh-btn').addEventListener('click', loadDocuments);
    document.getElementById('search-input').addEventListener('input', debounce(loadDocuments, 500));
    document.getElementById('status-filter').addEventListener('change', loadDocuments);
    document.getElementById('category-filter').addEventListener('change', loadDocuments);
    document.getElementById('select-all').addEventListener('change', toggleSelectAll);
    document.getElementById('batch-export-btn').addEventListener('click', batchExport);
    document.getElementById('batch-summary-btn').addEventListener('click', batchSummary);
    document.getElementById('export-markdown-btn').addEventListener('click', exportMarkdown);
    
    // ドラッグ&ドロップの設定
    setupDragAndDrop();
}

// RAG機能のイベントリスナー設定
function setupRAGEventListeners() {
    // 検索ボタン
    const searchBtn = document.getElementById('rag-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', performRAGSearch);
    }
    
    // フィルタボタン
    const filtersBtn = document.getElementById('rag-filters-btn');
    if (filtersBtn) {
        filtersBtn.addEventListener('click', toggleRAGFilters);
    }
    
    // 類似度閾値スライダー
    const similaritySlider = document.getElementById('rag-similarity-threshold');
    if (similaritySlider) {
        similaritySlider.addEventListener('input', updateSimilarityValue);
    }
    
    // Enterキーで検索
    const queryInput = document.getElementById('rag-query');
    if (queryInput) {
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performRAGSearch();
            }
        });
    }
}

// RAG検索実行
async function performRAGSearch() {
    const query = document.getElementById('rag-query').value.trim();
    if (!query) {
        alert('検索クエリを入力してください');
        return;
    }
    
    const searchBtn = document.getElementById('rag-search-btn');
    const originalText = searchBtn.textContent;
    searchBtn.textContent = '🔍 検索中...';
    searchBtn.disabled = true;
    
    try {
        // フィルタ条件を取得
        const filters = getRAGFilters();
        
        // リクエストデータ
        const requestData = {
            query: query,
            filters: filters,
            limit: parseInt(document.getElementById('rag-limit').value),
            similarity_threshold: parseFloat(document.getElementById('rag-similarity-threshold').value)
        };
        
        // API呼び出し
        const response = await fetch('/api/rag/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayRAGResults(result);
        
        // 検索履歴を更新
        loadRAGHistory();
        
    } catch (error) {
        console.error('RAG search error:', error);
        alert('検索中にエラーが発生しました: ' + error.message);
    } finally {
        searchBtn.textContent = originalText;
        searchBtn.disabled = false;
    }
}

// RAG検索結果の表示
function displayRAGResults(result) {
    const resultsDiv = document.getElementById('rag-results');
    const answerDiv = document.getElementById('rag-answer');
    const sourcesDiv = document.getElementById('rag-sources');
    
    // 結果を表示
    resultsDiv.style.display = 'block';
    
    // 回答を表示
    answerDiv.innerHTML = `
        <h6>🤖 AI回答</h6>
        <p>${result.answer}</p>
        <small class="text-muted">
            処理時間: ${result.metadata.processing_time?.toFixed(2)}秒 | 
            参照文書数: ${result.sources.length}件
        </small>
    `;
    
    // ソースを表示
    if (result.sources && result.sources.length > 0) {
        sourcesDiv.innerHTML = `
            <h6>📚 参照文書</h6>
            <div class="list-group">
                ${result.sources.map((source, index) => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${source.filename}</h6>
                            <small>関連度: ${(source.score * 100).toFixed(1)}%</small>
                        </div>
                        <p class="mb-1">${source.text_preview}</p>
                        <small>カテゴリ: ${source.category || '未分類'}</small>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        sourcesDiv.innerHTML = '<p class="text-muted">参照文書が見つかりませんでした。</p>';
    }
}

// RAGフィルタ条件の取得
function getRAGFilters() {
    const filters = {};
    
    // カテゴリフィルタ
    const categorySelect = document.getElementById('rag-category-filter');
    if (categorySelect) {
        const selectedCategories = Array.from(categorySelect.selectedOptions)
            .map(option => option.value)
            .filter(value => value !== '');
        if (selectedCategories.length > 0) {
            filters.categories = selectedCategories;
        }
    }
    
    // ファイル形式フィルタ
    const fileTypeSelect = document.getElementById('rag-file-type-filter');
    if (fileTypeSelect) {
        const selectedFileTypes = Array.from(fileTypeSelect.selectedOptions)
            .map(option => option.value)
            .filter(value => value !== '');
        if (selectedFileTypes.length > 0) {
            filters.file_types = selectedFileTypes;
        }
    }
    
    // 日付範囲フィルタ
    const dateStart = document.getElementById('rag-date-start').value;
    const dateEnd = document.getElementById('rag-date-end').value;
    if (dateStart || dateEnd) {
        filters.date_range = {};
        if (dateStart) filters.date_range.start = dateStart;
        if (dateEnd) filters.date_range.end = dateEnd;
    }
    
    // キーワードフィルタ
    const keywords = document.getElementById('rag-keywords').value.trim();
    if (keywords) {
        filters.keywords = keywords.split(',').map(k => k.trim()).filter(k => k);
    }
    
    return Object.keys(filters).length > 0 ? filters : null;
}

// RAGフィルタの表示/非表示切り替え
function toggleRAGFilters() {
    const collapse = document.getElementById('rag-filters-collapse');
    const btn = document.getElementById('rag-filters-btn');
    
    if (collapse.classList.contains('show')) {
        collapse.classList.remove('show');
        btn.textContent = '🔧 フィルタ設定';
    } else {
        collapse.classList.add('show');
        btn.textContent = '🔧 フィルタを閉じる';
    }
}

// 類似度閾値の表示更新
function updateSimilarityValue() {
    const slider = document.getElementById('rag-similarity-threshold');
    const display = document.getElementById('rag-similarity-value');
    if (slider && display) {
        display.textContent = slider.value;
    }
}

// RAGフィルタオプションの読み込み
async function loadRAGFilters() {
    try {
        const response = await fetch('/api/rag/filters');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const filters = data.filters;
        
        // カテゴリオプションを設定
        const categorySelect = document.getElementById('rag-category-filter');
        if (categorySelect && filters.categories) {
            categorySelect.innerHTML = '<option value="">すべて</option>' +
                filters.categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
        }
        
        // ファイル形式オプションを設定
        const fileTypeSelect = document.getElementById('rag-file-type-filter');
        if (fileTypeSelect && filters.file_types) {
            fileTypeSelect.innerHTML = '<option value="">すべて</option>' +
                filters.file_types.map(type => `<option value="${type}">${type}</option>`).join('');
        }
        
    } catch (error) {
        console.error('Failed to load RAG filters:', error);
    }
}

// RAG検索履歴の読み込み
async function loadRAGHistory() {
    try {
        const response = await fetch('/api/rag/queries?limit=10');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const historyDiv = document.getElementById('rag-history');
        
        if (data.queries && data.queries.length > 0) {
            historyDiv.innerHTML = data.queries.map(query => `
                <div class="list-group-item list-group-item-action" onclick="loadRAGQuery(${query.id})">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${query.query_text.substring(0, 50)}${query.query_text.length > 50 ? '...' : ''}</h6>
                        <small>${new Date(query.created_at).toLocaleString()}</small>
                    </div>
                    <p class="mb-1 text-muted">
                        参照文書: ${query.sources_count}件 | 
                        処理時間: ${query.processing_time?.toFixed(2)}秒
                    </p>
                </div>
            `).join('');
        } else {
            historyDiv.innerHTML = '<p class="text-muted">検索履歴がありません。</p>';
        }
        
    } catch (error) {
        console.error('Failed to load RAG history:', error);
    }
}

// 特定のRAGクエリを読み込み
async function loadRAGQuery(queryId) {
    try {
        const response = await fetch(`/api/rag/queries/${queryId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const query = data.query;
        
        // クエリを入力フィールドに設定
        document.getElementById('rag-query').value = query.query_text;
        
        // 結果を表示
        displayRAGResults({
            answer: query.answer,
            sources: data.sources.map(source => ({
                filename: source.filename,
                category: source.category,
                score: source.similarity_score,
                text_preview: source.text_preview
            })),
            metadata: {
                processing_time: query.processing_time
            }
        });
        
    } catch (error) {
        console.error('Failed to load RAG query:', error);
        alert('クエリの読み込みに失敗しました: ' + error.message);
    }
}

// ドラッグ&ドロップ機能の設定
function setupDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    
    if (!dropZone || !fileInput) {
        console.error('Drop zone or file input not found');
        return;
    }
    
    // ドロップゾーンをクリックするとファイル選択
    dropZone.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drop zone clicked');
        fileInput.click();
    });
    
    // ドラッグオーバー時
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
    });
    
    // ドラッグエンター時
    dropZone.addEventListener('dragenter', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
    });
    
    // ドラッグリーブ時
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        // 子要素から出た時は無視
        if (e.target === dropZone) {
            dropZone.classList.remove('drag-over');
        }
    });
    
    // ドロップ時
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // DataTransferからFileListを作成
            const dataTransfer = new DataTransfer();
            for (let i = 0; i < files.length; i++) {
                dataTransfer.items.add(files[i]);
            }
            fileInput.files = dataTransfer.files;
            updateFileCount(files.length);
            console.log(`${files.length} files dropped`);
        }
    });
    
    // ファイル選択時
    fileInput.addEventListener('change', (e) => {
        const count = e.target.files.length;
        updateFileCount(count);
        console.log(`${count} files selected`);
    });
}

// ファイル数表示更新
function updateFileCount(count) {
    const dropZone = document.getElementById('drop-zone');
    const text = dropZone.querySelector('.drop-text');
    if (count > 0) {
        text.textContent = `${count}個のファイルが選択されました`;
        dropZone.classList.add('has-files');
    } else {
        text.textContent = 'ファイルをドラッグ&ドロップ または クリックして選択';
        dropZone.classList.remove('has-files');
    }
}

// システムステータス読み込み
async function loadSystemStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        // バージョン情報を表示
        if (data.version) {
            document.getElementById('app-version').textContent = data.version;
            document.getElementById('status-version').textContent = data.version;
            if (data.version_name) {
                document.getElementById('version-name').textContent = `(${data.version_name})`;
            }
            if (data.release_date) {
                document.getElementById('release-date').textContent = `リリース日: ${data.release_date}`;
            }
        }
        
        document.getElementById('processing-mode').textContent = data.processing_mode;
        document.getElementById('ocr-engine').textContent = data.ocr_engine;
        document.getElementById('ai-provider').textContent = data.ai_provider;
    } catch (error) {
        console.error('システムステータス読み込みエラー:', error);
    }
}

// 統計情報読み込み
async function loadStatistics() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('total-docs').textContent = data.total_documents;
        document.getElementById('completed-docs').textContent = data.status.completed;
        document.getElementById('processing-docs').textContent = data.status.processing;
        document.getElementById('failed-docs').textContent = data.status.failed;
    } catch (error) {
        console.error('統計情報読み込みエラー:', error);
    }
}

// カテゴリ一覧読み込み
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        
        const select = document.getElementById('category-filter');
        data.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('カテゴリ読み込みエラー:', error);
    }
}

// ドキュメント一覧読み込み
async function loadDocuments() {
    try {
        const search = document.getElementById('search-input').value;
        const status = document.getElementById('status-filter').value;
        const category = document.getElementById('category-filter').value;
        
        let url = '/api/documents?';
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (status) url += `status=${status}&`;
        if (category) url += `category=${encodeURIComponent(category)}&`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('documents-table');
        tbody.innerHTML = '';
        
        if (data.documents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">ドキュメントがありません</td></tr>';
            return;
        }
        
        data.documents.forEach(doc => {
            const row = createDocumentRow(doc);
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('ドキュメント読み込みエラー:', error);
        document.getElementById('documents-table').innerHTML = 
            '<tr><td colspan="6" class="text-center text-danger">読み込みエラー</td></tr>';
    }
}

// ドキュメント行作成
function createDocumentRow(doc) {
    const tr = document.createElement('tr');
    tr.className = 'fade-in';
    
    const statusBadge = `<span class="badge status-${doc.status}">${getStatusText(doc.status)}</span>`;
    const processedAt = doc.processed_at ? new Date(doc.processed_at).toLocaleString('ja-JP') : '-';
    
    tr.innerHTML = `
        <td><input type="checkbox" class="doc-checkbox" data-id="${doc.id}"></td>
        <td>
            <strong>${escapeHtml(doc.filename)}</strong><br>
            <small class="text-muted">${(doc.file_size / 1024).toFixed(1)} KB</small>
        </td>
        <td>${escapeHtml(doc.category || '-')}</td>
        <td>${statusBadge}</td>
        <td><small>${processedAt}</small></td>
        <td>
            <button class="btn btn-sm btn-outline-success" onclick="downloadOriginalFile(${doc.id})">📥</button>
            <button class="btn btn-sm btn-outline-primary" onclick="showDetail(${doc.id})">詳細</button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument(${doc.id})">削除</button>
        </td>
    `;
    
    // チェックボックスイベント
    const checkbox = tr.querySelector('.doc-checkbox');
    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            selectedDocuments.add(doc.id);
        } else {
            selectedDocuments.delete(doc.id);
        }
        updateBatchButtons();
    });
    
    return tr;
}

// ファイルアップロード
async function uploadFiles() {
    const fileInput = document.getElementById('file-input');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('ファイルを選択してください');
        return;
    }
    
    const uploadProgress = document.getElementById('upload-progress');
    const uploadResult = document.getElementById('upload-result');
    
    uploadProgress.style.display = 'block';
    uploadResult.innerHTML = '';
    
    try {
        const formData = new FormData();
        for (const file of files) {
            formData.append('files', file);
        }
        
        const response = await fetch('/api/upload/batch', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        uploadProgress.style.display = 'none';
        
        uploadResult.innerHTML = `
            <div class="alert alert-success">
                アップロード完了: ${data.success}件成功 / ${data.failed}件失敗
            </div>
        `;
        
        if (data.errors.length > 0) {
            const errorList = data.errors.map(e => `<li>${e.filename}: ${e.error}</li>`).join('');
            uploadResult.innerHTML += `
                <div class="alert alert-warning">
                    <strong>エラー:</strong>
                    <ul>${errorList}</ul>
                </div>
            `;
        }
        
        fileInput.value = '';
        updateFileCount(0);  // ファイル選択表示をリセット
        loadStatistics();
        loadDocuments();
        
    } catch (error) {
        uploadProgress.style.display = 'none';
        uploadResult.innerHTML = `<div class="alert alert-danger">アップロードエラー: ${error.message}</div>`;
        fileInput.value = '';
        updateFileCount(0);  // エラー時もファイル選択表示をリセット
    }
}

// ドキュメント詳細表示
async function showDetail(id) {
    currentDocumentId = id;
    try {
        const response = await fetch(`/api/documents/${id}`);
        const doc = await response.json();
        
        const modal = new bootstrap.Modal(document.getElementById('detailModal'));
        document.getElementById('detailModalTitle').textContent = doc.filename;
        
        let keywordsHtml = '';
        if (doc.keywords && doc.keywords.length > 0) {
            keywordsHtml = doc.keywords.map(k => `<span class="badge bg-secondary keyword-badge">${escapeHtml(k)}</span>`).join('');
        }
        
        let metadataHtml = '';
        if (doc.extracted_metadata && Object.keys(doc.extracted_metadata).length > 0) {
            metadataHtml = '<h6>抽出情報</h6><ul>';
            for (const [key, value] of Object.entries(doc.extracted_metadata)) {
                metadataHtml += `<li><strong>${escapeHtml(key)}:</strong> ${escapeHtml(String(value))}</li>`;
            }
            metadataHtml += '</ul>';
        }
        
        document.getElementById('detailModalBody').innerHTML = `
            <h6>基本情報</h6>
            <p><strong>カテゴリ:</strong> ${escapeHtml(doc.category || 'N/A')}</p>
            <p><strong>ステータス:</strong> ${getStatusText(doc.status)}</p>
            <p><strong>処理時間:</strong> ${doc.processing_time ? doc.processing_time.toFixed(2) + '秒' : 'N/A'}</p>
            
            <h6>要約</h6>
            <p>${escapeHtml(doc.summary || '要約なし')}</p>
            
            <h6>キーワード</h6>
            <p>${keywordsHtml || 'なし'}</p>
            
            ${metadataHtml}
            
            <h6>OCRテキスト（抜粋）</h6>
            <div style="max-height: 200px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                <pre style="white-space: pre-wrap; margin: 0;">${escapeHtml((doc.ocr_text || '').substring(0, 1000))}${doc.ocr_text && doc.ocr_text.length > 1000 ? '...' : ''}</pre>
            </div>
        `;
        
        modal.show();
    } catch (error) {
        alert('詳細情報の取得に失敗しました');
    }
}

// 元ファイルダウンロード
async function downloadOriginalFile(id) {
    try {
        // ダウンロードリンクを作成
        const a = document.createElement('a');
        a.href = `/api/documents/${id}/download`;
        a.download = ''; // ブラウザにファイル名を自動決定させる
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch (error) {
        console.error('ダウンロードエラー:', error);
        alert('ファイルのダウンロードに失敗しました');
    }
}

// モーダルから元ファイルダウンロード
async function downloadOriginalFromModal() {
    if (!currentDocumentId) return;
    await downloadOriginalFile(currentDocumentId);
}

// マークダウンエクスポート
async function exportMarkdown() {
    if (!currentDocumentId) return;
    
    try {
        const response = await fetch(`/api/export/${currentDocumentId}/markdown`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `document_${currentDocumentId}.md`;
        a.click();
    } catch (error) {
        alert('エクスポートに失敗しました');
    }
}

// バッチエクスポート（個別マークダウンをZIP）
async function batchExport() {
    if (selectedDocuments.size === 0) return;
    
    try {
        const response = await fetch('/api/export/batch/markdown-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_ids: Array.from(selectedDocuments)
            })
        });
        
        if (!response.ok) {
            throw new Error('エクスポートに失敗しました');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `markdown_export_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert(`✅ ${selectedDocuments.size}件のマークダウンをZIPでエクスポートしました！`);
    } catch (error) {
        console.error('エクスポートエラー:', error);
        alert('エクスポートに失敗しました: ' + error.message);
    }
}

// 元ファイル一括ダウンロード（ZIP）
async function batchDownload() {
    if (selectedDocuments.size === 0) return;
    
    try {
        const response = await fetch('/api/documents/batch/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_ids: Array.from(selectedDocuments)
            })
        });
        
        if (!response.ok) {
            throw new Error('ダウンロードに失敗しました');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `original_files_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert(`✅ ${selectedDocuments.size}件の元ファイルをZIPでダウンロードしました！`);
    } catch (error) {
        console.error('ダウンロードエラー:', error);
        alert('ダウンロードに失敗しました: ' + error.message);
    }
}

// バッチまとめ
async function batchSummary() {
    if (selectedDocuments.size === 0) {
        alert('ファイルを選択してください');
        return;
    }
    
    // システムが自動的にタイトルを生成
    const now = new Date();
    const dateStr = now.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-');
    const title = `統合要約_${dateStr}_${selectedDocuments.size}件`;
    
    // ローディング表示を作成
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'summary-loading';
    loadingDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        color: white;
        font-size: 1.2rem;
    `;
    loadingDiv.innerHTML = `
        <div class="spinner-border text-light mb-3" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
        <div style="text-align: center;">
            <strong>🤖 AI統合要約を生成中...</strong><br>
            <small style="margin-top: 10px; display: block; color: #ccc;">
                選択した ${selectedDocuments.size} 件のファイルを分析しています<br>
                しばらくお待ちください（30秒〜1分程度）
            </small>
        </div>
    `;
    document.body.appendChild(loadingDiv);
    
    try {
        console.log('統合要約リクエスト:', {
            document_ids: Array.from(selectedDocuments),
            title: title
        });
        
        const response = await fetch('/api/export/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_ids: Array.from(selectedDocuments),
                title: title
            })
        });
        
        console.log('レスポンスステータス:', response.status);
        
        if (!response.ok) {
            let errorMessage = 'まとめ生成に失敗しました';
            try {
                const errorData = await response.json();
                console.error('エラーデータ:', errorData);
                
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (errorData.detail && typeof errorData.detail === 'object') {
                    errorMessage = JSON.stringify(errorData.detail);
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                const text = await response.text();
                console.error('エラーレスポンス:', text);
                errorMessage = text || `HTTPエラー ${response.status}`;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log('レスポンスデータ:', data);
        
        if (data.status === 'success' && data.filename && data.summary) {
            // ローディング表示を削除
            const loadingDiv = document.getElementById('summary-loading');
            if (loadingDiv) {
                loadingDiv.remove();
            }
            
            // マークダウンファイルをダウンロード
            const blob = new Blob([data.summary], { type: 'text/markdown; charset=utf-8' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            alert(`✅ 統合要約を生成しました！\n\nファイル名: ${data.filename}\n対象文書数: ${selectedDocuments.size} 件\n\nファイルをダウンロードしました。`);
        } else {
            throw new Error(`レスポンスデータが不正です: ${JSON.stringify(data)}`);
        }
    } catch (error) {
        console.error('バッチまとめエラー:', error);
        
        // ローディング表示を削除
        const loadingDiv = document.getElementById('summary-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
        
        let errorMessage = 'まとめ生成に失敗しました';
        if (error.message) {
            errorMessage += `: ${error.message}`;
        } else if (typeof error === 'string') {
            errorMessage += `: ${error}`;
        } else {
            errorMessage += `: ${JSON.stringify(error)}`;
        }
        
        alert(errorMessage);
    }
}

// ドキュメント削除
async function deleteDocument(id) {
    if (!confirm('本当に削除しますか？')) return;
    
    try {
        await fetch(`/api/documents/${id}`, { method: 'DELETE' });
        alert('削除しました');
        loadStatistics();
        loadDocuments();
    } catch (error) {
        alert('削除に失敗しました');
    }
}

// ユーティリティ関数
function getStatusText(status) {
    const statusMap = {
        'pending': '待機中',
        'processing': '処理中',
        'completed': '完了',
        'failed': 'エラー'
    };
    return statusMap[status] || status;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function toggleSelectAll(e) {
    const checkboxes = document.querySelectorAll('.doc-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = e.target.checked;
        const id = parseInt(cb.dataset.id);
        if (e.target.checked) {
            selectedDocuments.add(id);
        } else {
            selectedDocuments.delete(id);
        }
    });
    updateBatchButtons();
}

function updateBatchButtons() {
    const hasSelection = selectedDocuments.size > 0;
    document.getElementById('batch-download-btn').disabled = !hasSelection;
    document.getElementById('batch-export-btn').disabled = !hasSelection;
    document.getElementById('batch-summary-btn').disabled = !hasSelection;
}

// イベントリスナーの設定
document.addEventListener('DOMContentLoaded', () => {
    // モーダル内の元ファイルダウンロードボタン
    const downloadOriginalBtn = document.getElementById('download-original-btn');
    if (downloadOriginalBtn) {
        downloadOriginalBtn.addEventListener('click', downloadOriginalFromModal);
    }
    
    // バッチ元ファイルダウンロードボタン
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    if (batchDownloadBtn) {
        batchDownloadBtn.addEventListener('click', batchDownload);
    }
});

