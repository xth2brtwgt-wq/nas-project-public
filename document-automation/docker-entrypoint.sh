#!/bin/bash
# Dockerコンテナ起動時の権限修正エントリーポイント

# rootユーザーで実行している場合のみ権限を修正
if [ "$(id -u)" = "0" ]; then
    # uploadsディレクトリの権限を確認・修正
    if [ -d "/app/uploads" ]; then
        chmod -R 777 /app/uploads 2>/dev/null || true
        chown -R appuser:appuser /app/uploads 2>/dev/null || true
    fi

    if [ -d "/app/processed" ]; then
        chmod -R 777 /app/processed 2>/dev/null || true
        chown -R appuser:appuser /app/processed 2>/dev/null || true
    fi

    if [ -d "/app/exports" ]; then
        chmod -R 777 /app/exports 2>/dev/null || true
        chown -R appuser:appuser /app/exports 2>/dev/null || true
    fi

    if [ -d "/app/cache" ]; then
        chmod -R 777 /app/cache 2>/dev/null || true
        chown -R appuser:appuser /app/cache 2>/dev/null || true
    fi
    
    # appuserに切り替えて元のコマンドを実行
    exec gosu appuser "$@"
else
    # 既にappuserで実行されている場合
    exec "$@"
fi

