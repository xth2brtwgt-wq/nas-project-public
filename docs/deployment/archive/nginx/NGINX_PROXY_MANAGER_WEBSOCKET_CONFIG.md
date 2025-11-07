# 🔌 Nginx Proxy Manager - WebSocket設定ガイド

**作成日**: 2025-11-02  
**対象**: Nginx Proxy ManagerでWebSocketを有効化する方法

---

## 📋 問題

Nginx Proxy ManagerのCustom Locations設定画面で「Websockets Support」の設定が見当たらない。

---

## 🔍 確認方法

### 方法1: Custom Locationsの詳細設定を確認

1. **各Locationの右側にある歯車アイコン（⚙️）をクリック**

2. **詳細設定パネルが開く**

3. **「Websockets Support」のチェックボックスを確認**
   - チェックボックスがあれば、**nas-dashboard-monitoring**のLocationで有効化

---

### 方法2: Proxy Hostの「Advanced」タブで設定

Custom Locationsの詳細設定に「Websockets Support」がない場合：

1. **Proxy Hostの「Advanced」タブをクリック**

2. **「Custom Nginx Configuration」セクションに以下を追加**:

```nginx
# WebSocket設定（/monitoring 用）
location /monitoring/ws {
    proxy_pass http://192.168.68.110:3002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**注意**: この方法は、Custom Locationsを使用している場合は不要な場合があります。

---

### 方法3: Custom Locationsの詳細設定（歯車アイコン）で設定

1. **`/monitoring`のLocationの歯車アイコン（⚙️）をクリック**

2. **詳細設定パネルが開く**（「Custom Nginx configuration」テキストエリアが表示される）

3. **「Custom Nginx configuration」テキストエリアに以下を追加**:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

4. **「Save」をクリック**

**注意**: Nginx Proxy Managerのバージョンによっては、「Websockets Support」のチェックボックスが表示されない場合があります。この場合、「Custom Nginx configuration」に直接設定を記述する必要があります。

---

## ✅ 推奨される設定方法

### ステップ1: Custom Locationsの詳細設定を確認

1. **`/monitoring`のLocationの右側の歯車アイコン（⚙️）をクリック**

2. **詳細設定パネルを開く**

3. **「Websockets Support」のチェックボックスを探す**
   - あれば、チェックを入れて有効化
   - なければ、次のステップへ

---

### ステップ2: Advanced設定を追加（必要に応じて）

詳細設定に「Websockets Support」がない場合：

1. **歯車アイコンの詳細設定パネルで「Advanced」セクションを探す**

2. **「Advanced」セクションに以下を追加**:

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

3. **「Save」をクリック**

---

## 🧪 テスト方法

### ステップ1: WebSocket接続をテスト

```bash
# WebSocket接続をテスト（wscatを使用）
wscat -c wss://yoshi-nas-sys.duckdns.org:8443/monitoring/ws

# または、ブラウザの開発者ツールで確認
# Networkタブ → WSフィルタ → WebSocket接続を確認
```

### ステップ2: nas-dashboard-monitoringの動作確認

1. **ブラウザでアクセス**:
   ```
   https://yoshi-nas-sys.duckdns.org:8443/monitoring
   ```

2. **開発者ツール（F12）を開く**

3. **「Network」タブを開く**

4. **「WS」フィルタを選択**

5. **WebSocket接続が確立されていることを確認**
   - ステータス: `101 Switching Protocols`
   - 接続が確立されていれば成功

---

## ⚠️ 注意事項

### WebSocketが必要なサービス

- ✅ **nas-dashboard-monitoring**: WebSocketを使用（必須）
- ❌ **その他のサービス**: WebSocketを使用しない（設定不要）

### 設定が不要な場合

ほとんどのサービスはWebSocketを使用しないため、設定は不要です。

**WebSocket設定が必要なのは、nas-dashboard-monitoringのみ**です。

---

## 🔧 トラブルシューティング

### WebSocket接続が失敗する場合

**原因**: WebSocket設定が正しくない

**対処法**:
1. Custom Locationsの詳細設定（歯車アイコン）で「Websockets Support」を有効化
2. または、「Advanced」セクションにWebSocket設定を追加
3. Nginx Proxy Managerを再起動（設定が反映されない場合）

### 詳細設定パネルが開かない場合

**原因**: JavaScriptのエラーまたはブラウザの問題

**対処法**:
1. ブラウザのキャッシュをクリア
2. 別のブラウザで試す
3. Nginx Proxy Managerを再起動

---

## 📝 まとめ

### 設定手順

1. **各Locationの右側の歯車アイコン（⚙️）をクリック**
2. **詳細設定パネルで「Websockets Support」を確認**
3. **nas-dashboard-monitoringのLocationで有効化**
4. **「Save」をクリック**

### 設定が不要な場合

- WebSocketを使用しないサービス（amazon-analytics、document-automationなど）は、設定不要
- とりあえず設定を進めて、問題が発生したら後で対応

---

**作成日**: 2025-11-02  
**更新日**: 2025-11-02  
**作成者**: AI Assistant

