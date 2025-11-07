# 📋 Nginx Proxy Manager - WebSocket設定まとめ

**作成日**: 2025-11-02  
**対象**: 各サービスのWebSocket設定の必要性をまとめたドキュメント

---

## ✅ WebSocket設定が必要なサービス（3つ）

### 1. nas-dashboard-monitoring（`/monitoring`）

- **技術**: FastAPI WebSocket
- **用途**: リアルタイムメトリクス更新
- **設定**: **必須**

**設定方法**:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

---

### 2. meeting-minutes-byc（`/meetings`）

- **技術**: Flask-SocketIO（Socket.IO）
- **用途**: リアルタイム進捗表示（音声文字起こし処理の進捗）
- **設定**: **必須**

**設定方法**:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

---

### 3. youtube-to-notion（`/youtube`）

- **技術**: Flask-SocketIO（Socket.IO）
- **用途**: リアルタイム進捗表示（動画処理の進捗）
- **設定**: **必須**

**設定方法**:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

---

## ❌ WebSocket設定が不要なサービス（3つ）

### 1. nas-dashboard（`/`）

- **技術**: Flask（標準HTTPのみ）
- **用途**: ダッシュボード表示
- **設定**: 不要

---

### 2. amazon-analytics（`/analytics`）

- **技術**: Flask（標準HTTPのみ）
- **用途**: Amazon分析ダッシュボード
- **設定**: 不要

---

### 3. document-automation（`/documents`）

- **技術**: Flask（標準HTTPのみ）
- **用途**: 文書自動処理
- **設定**: 不要

---

## 📋 設定一覧表

| サービス | Location | WebSocket設定 | 技術 |
|---------|----------|-------------|------|
| nas-dashboard | `/` | ❌ 不要 | Flask（HTTPのみ） |
| amazon-analytics | `/analytics` | ❌ 不要 | Flask（HTTPのみ） |
| document-automation | `/documents` | ❌ 不要 | Flask（HTTPのみ） |
| nas-dashboard-monitoring | `/monitoring` | ✅ **必須** | FastAPI WebSocket |
| meeting-minutes-byc | `/meetings` | ✅ **必須** | Flask-SocketIO（Socket.IO） |
| youtube-to-notion | `/youtube` | ✅ **必須** | Flask-SocketIO（Socket.IO） |

---

## 🎯 設定手順（簡易版）

### WebSocket設定が必要なサービス

以下の3つのサービスのLocationを追加する際に、**歯車アイコン（⚙️）**をクリックして「Custom Nginx configuration」に上記の設定を記述してください：

1. `/monitoring`（nas-dashboard-monitoring）
2. `/meetings`（meeting-minutes-byc）
3. `/youtube`（youtube-to-notion）

### WebSocket設定が不要なサービス

以下の3つのサービスのLocationを追加する際は、基本設定のみでOKです：

1. `/`（nas-dashboard）
2. `/analytics`（amazon-analytics）
3. `/documents`（document-automation）

---

## ⚠️ 注意事項

### WebSocket設定を忘れた場合

WebSocket設定が必要なサービスで設定を忘れた場合、以下の問題が発生します：

- **nas-dashboard-monitoring**: リアルタイムメトリクス更新が動作しない
- **meeting-minutes-byc**: リアルタイム進捗表示が動作しない
- **youtube-to-notion**: リアルタイム進捗表示が動作しない

### 確認方法

各サービスの動作確認時に、以下を確認してください：

1. **ブラウザの開発者ツール（F12）を開く**
2. **「Network」タブ → 「WS」フィルタを選択**
3. **WebSocket接続が確立されていることを確認**
   - ステータス: `101 Switching Protocols`
   - 接続が確立されていれば成功

---

## 📝 まとめ

- **WebSocket設定が必要**: 3サービス（nas-dashboard-monitoring、meeting-minutes-byc、youtube-to-notion）
- **WebSocket設定が不要**: 3サービス（nas-dashboard、amazon-analytics、document-automation）

**すべてのWebSocket設定は、各Locationの詳細設定（歯車アイコン）で「Custom Nginx configuration」に記述します。**

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

