# ✅ ダッシュボード外部アクセス対応サマリー

**作成日**: 2025-11-04  
**目的**: ダッシュボードからのサービスアクセスと内部ロジックの外部アクセス対応状況を確認

---

## ✅ 対応状況

### 1. ダッシュボードからのサービスリンク生成

**実装済み**: `get_dynamic_services()`関数で外部アクセス判定を行い、外部URLを生成

**動作**:
- 外部アクセス時（`https://yoshi-nas-sys.duckdns.org:8443`）:
  - 各サービスへのリンク: `https://yoshi-nas-sys.duckdns.org:8443/analytics` など
- 内部アクセス時（`http://192.168.68.110:9001`）:
  - 各サービスへのリンク: `http://192.168.68.110:8001` など（直接ポート）

**判定ロジック**:
```python
is_external_access = (
    current_port == '8443' or 
    hostname == 'yoshi-nas-sys.duckdns.org' or
    (current_port and current_port.startswith('844'))
)
```

### 2. 認証リダイレクトURL

**実装済み**: `get_dashboard_login_url()`関数で外部URLを返す

**動作**:
- すべてのアクセス: `https://yoshi-nas-sys.duckdns.org:8443/login` にリダイレクト
- 環境変数`NAS_EXTERNAL_ACCESS_URL`で外部URLを変更可能

**簡略化済み**: ローカルアクセスを想定しないため、常に外部URLを返す

---

## 🔍 確認手順

### ステップ1: ダッシュボードのサービスリンクを確認

外部からダッシュボードにアクセス（`https://yoshi-nas-sys.duckdns.org:8443`）:

1. **ダッシュボードにログイン**
2. **サービスカードの「アクセス」ボタンを確認**
3. **各サービスのURLが外部URL（`https://yoshi-nas-sys.duckdns.org:8443/...`）になっているか確認**

**期待されるURL**:
- Amazon Analytics: `https://yoshi-nas-sys.duckdns.org:8443/analytics`
- Document Automation: `https://yoshi-nas-sys.duckdns.org:8443/documents`
- NAS Monitoring: `https://yoshi-nas-sys.duckdns.org:8443/monitoring`
- Meeting Minutes: `https://yoshi-nas-sys.duckdns.org:8443/meetings`
- YouTube to Notion: `https://yoshi-nas-sys.duckdns.org:8443/youtube`

### ステップ2: 認証リダイレクトを確認

各サービスに直接アクセス（認証なし）:

1. **ダッシュボードにログインしていない状態で**、各サービスにアクセス
2. **ログインページにリダイレクトされることを確認**
3. **リダイレクト先のURLが外部URL（`https://yoshi-nas-sys.duckdns.org:8443/login`）になっているか確認**

### ステップ3: ダッシュボードからサービスへの遷移を確認

1. **ダッシュボードにログイン**
2. **サービスカードの「アクセス」ボタンをクリック**
3. **各サービスの画面が表示されることを確認**
4. **ブラウザのアドレスバーでURLが外部URL（`https://yoshi-nas-sys.duckdns.org:8443/...`）になっているか確認**

---

## 📝 実装詳細

### ダッシュボードのサービスリンク生成

```python
def get_dynamic_services():
    """リクエストのホスト名を使用して動的にサービスURLを生成"""
    base_url = get_base_url()
    # 外部アクセス判定
    is_external_access = (
        current_port == '8443' or 
        hostname == 'yoshi-nas-sys.duckdns.org' or
        (current_port and current_port.startswith('844'))
    )
    
    # 外部アクセスの場合はCustom Locationパスを使用
    if is_external_access and service_id in custom_location_mapping:
        custom_location_path = custom_location_mapping[service_id]
        service_config_copy['url'] = f"{scheme}://{hostname}:{port}{custom_location_path}"
```

### 認証リダイレクトURL

```python
def get_dashboard_login_url(request=None) -> str:
    """ダッシュボードのログインページURLを取得"""
    # 環境変数で外部URLが設定されている場合はそれを使用
    external_url = os.getenv('NAS_EXTERNAL_ACCESS_URL', 'https://yoshi-nas-sys.duckdns.org:8443')
    login_url = f'{external_url}/login'
    return login_url
```

---

## ✅ 対応完了

- ✅ ダッシュボードからのサービスリンク生成（外部アクセス時に対応）
- ✅ 認証リダイレクトURL（常に外部URLを返す）
- ✅ 各サービスの認証機能（外部URLにリダイレクト）

---

## 🔧 注意事項

### ローカルアクセスについて

現在の実装では、**ローカルアクセス（内部ネットワークから直接アクセス）を想定していません**。

- すべてのアクセスは外部URL（`https://yoshi-nas-sys.duckdns.org:8443`）経由で行う必要があります
- 内部ネットワークから直接アクセスする場合も、外部URLを使用してください

### 環境変数設定

外部URLを変更する場合、環境変数`NAS_EXTERNAL_ACCESS_URL`を設定：

```bash
# .envファイルに追加
NAS_EXTERNAL_ACCESS_URL=https://yoshi-nas-sys.duckdns.org:8443
```

---

**作成日**: 2025-11-04  
**更新日**: 2025-11-04  
**作成者**: AI Assistant

