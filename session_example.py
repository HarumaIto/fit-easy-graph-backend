#!/usr/bin/env python3
"""
セッション継続機能の使用例
"""

import time
from scraper import get_fit_easy_session, fetch_multiple_congestion_info

def example_session_reuse():
    """セッション再利用の例"""
    print("=== セッション継続機能のデモ ===")
    
    # セッションマネージャーを取得
    session_manager = get_fit_easy_session()
    
    # 初回アクセス（ログインが実行される）
    print("\n1. 初回データ取得:")
    result1 = session_manager.fetch_congestion_data("イオンタウン弥富店")
    print(f"結果: {result1}")
    
    # 2回目のアクセス（既存セッションを再利用）
    print("\n2. 2回目のデータ取得 (セッション再利用):")
    result2 = session_manager.fetch_congestion_data("イオンタウン弥富店")
    print(f"結果: {result2}")
    
    # セッション状態の確認
    print(f"\n3. セッション状態:")
    print(f"セッション有効: {session_manager.is_session_valid()}")
    print(f"ログイン時刻: {session_manager.login_time}")
    
    # 複数店舗の情報を一度に取得
    print("\n4. 複数店舗の情報取得:")
    # 実際の店舗名に合わせて変更してください
    target_stores = ["イオンタウン弥富店"]  # 他の店舗名があれば追加
    results = fetch_multiple_congestion_info(target_stores)
    for result in results:
        print(f"  {result}")

def example_multiple_requests():
    """短時間で複数回リクエストする例"""
    print("\n=== 短時間での複数リクエスト例 ===")
    
    for i in range(3):
        print(f"\n--- リクエスト {i+1} ---")
        try:
            session_manager = get_fit_easy_session()
            result = session_manager.fetch_congestion_data("イオンタウン弥富店")
            print(f"成功: {result}")
            
            # セッション再利用の確認
            if session_manager.is_session_valid():
                print("✓ 既存セッションを再利用")
            else:
                print("! 新しいセッションでログイン")
                
        except Exception as e:
            print(f"エラー: {e}")
        
        # 少し間隔を空ける
        if i < 2:
            print("3秒待機...")
            time.sleep(3)

if __name__ == "__main__":
    try:
        example_session_reuse()
        example_multiple_requests()
    except Exception as e:
        print(f"実行エラー: {e}")
        print("環境変数 FITEASY_EMAIL と FITEASY_PASSWORD が設定されているか確認してください。")
