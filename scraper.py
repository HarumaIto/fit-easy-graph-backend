import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import logging # ロギングモジュールをインポート
from datetime import datetime, timedelta

# ロギング設定の追加
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOGIN_URL = 'https://join.fiteasy.jp/mypage/login'
TARGET_URL = 'https://join.fiteasy.jp/mypage/congestion_list'

# ヘッダー情報の強化: 最新のChrome User-Agentを使用し、より多くのヘッダーを追加
# ご自身のブラウザのUser-Agentと、Fiteasyログイン時のリクエストヘッダーを開発者ツールで確認し、
# 必要に応じてさらに追加・更新してください。
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36', # 最新のUser-Agentに更新
    'Referer': LOGIN_URL,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none', # ログインページへの初回アクセスは 'none'
    'Sec-Fetch-User': '?1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

load_dotenv()

class FitEasySession:
    """FitEasyのログインセッションを管理するクラス"""
    
    def __init__(self):
        self.session = None
        self.login_time = None
        self.session_timeout = timedelta(hours=2)  # セッションタイムアウト時間（2時間）
        self.email = os.getenv("FITEASY_EMAIL")
        self.password = os.getenv("FITEASY_PASSWORD")
        
        if not self.email or not self.password:
            logging.error("環境変数 FITEASY_EMAIL または FITEASY_PASSWORD が設定されていません。")
            raise Exception("環境変数 FITEASY_EMAIL または FITEASY_PASSWORD が設定されていません。")
    
    def is_session_valid(self):
        """セッションが有効かどうかをチェック"""
        if self.session is None or self.login_time is None:
            return False
        
        # セッションがタイムアウトしているかチェック
        if datetime.now() - self.login_time > self.session_timeout:
            logging.info("セッションがタイムアウトしました。")
            return False
        
        return True
    
    def login(self):
        """FitEasyにログインしてセッションを確立"""
        logging.info("新しいセッションでログインを開始します。")
        
        login_payload = {
            'emailOrMemberID': self.email,
            'password': self.password,
        }

        self.session = requests.Session()
        logging.info(f"ログインページにGETリクエストを送信中: {LOGIN_URL}")
        
        try:
            response_get_login = self.session.get(LOGIN_URL, headers=HEADERS)
            response_get_login.raise_for_status()
            logging.info(f"ログインページGET成功: ステータスコード {response_get_login.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"ログインページGETリクエストでエラー: {e}")
            if e.response is not None:
                logging.error(f"ステータスコード: {e.response.status_code}")
                logging.error(f"レスポンスヘッダー: {e.response.headers}")
                logging.error(f"レスポンスボディ: {e.response.text}")
            raise

        soup_login = BeautifulSoup(response_get_login.text, 'html.parser')
        csrf_token_input = soup_login.find('input', {'name': '_token'})
        if csrf_token_input:
            csrf_token = csrf_token_input['value']
            login_payload['_token'] = csrf_token
            logging.info(f"CSRFトークンを取得しました: {csrf_token}")
        else:
            logging.error("CSRFトークンが見つかりませんでした。ログインフォームのHTML構造を確認してください。")
            raise Exception("CSRFトークンが見つかりませんでした。")

        logging.info(f"ログインPOSTリクエストを送信中: {LOGIN_URL}")
        post_headers = HEADERS.copy()
        post_headers['Sec-Fetch-Site'] = 'same-origin'

        try:
            response_login = self.session.post(LOGIN_URL, data=login_payload, headers=post_headers)
            response_login.raise_for_status()
            logging.info(f"ログインPOST成功: ステータスコード {response_login.status_code}")
            logging.info(f"ログイン後のURL: {response_login.url}")
        except requests.exceptions.RequestException as e:
            logging.error(f"ログインPOSTリクエストでエラー: {e}")
            if e.response is not None:
                logging.error(f"ステータスコード: {e.response.status_code}")
                logging.error(f"レスポンスヘッダー: {e.response.headers}")
                logging.error(f"レスポンスボディ: {e.response.text}")
            raise

        # ログイン失敗条件の確認
        if response_login.url == LOGIN_URL or "ログイン失敗" in response_login.text or "メールアドレス、または会員IDとパスワードの組み合わせが間違っています" in response_login.text:
            logging.error("ログインに失敗しました。認証情報、またはログインリクエストのデータを確認してください。")
            raise Exception("ログインに失敗しました。認証情報、またはログインリクエストのデータを確認してください。")

        # ログイン成功時刻を記録
        self.login_time = datetime.now()
        logging.info("ログインが成功しました。セッションを保存しました。")
    
    def get_session(self):
        """有効なセッションを取得（必要に応じて再ログイン）"""
        if not self.is_session_valid():
            logging.info("セッションが無効です。再ログインします。")
            self.login()
        else:
            logging.info("既存のセッションを使用します。")
        
        return self.session
    
    def fetch_congestion_data(self, target_name="イオンタウン弥富店"):
        """指定された店舗の混雑情報を取得"""
        session = self.get_session()
        
        logging.info(f"目的のページにGETリクエストを送信中: {TARGET_URL}")
        target_headers = HEADERS.copy()
        target_headers['Sec-Fetch-Site'] = 'same-origin'

        try:
            response_target = session.get(TARGET_URL, headers=target_headers)
            response_target.raise_for_status()
            logging.info(f"目的ページGET成功: ステータスコード {response_target.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"目的ページGETリクエストでエラー: {e}")
            if e.response is not None:
                logging.error(f"ステータスコード: {e.response.status_code}")
                logging.error(f"レスポンスヘッダー: {e.response.headers}")
                logging.error(f"レスポンスボディ: {e.response.text}")
            raise

        soup_target = BeautifulSoup(response_target.text, 'html.parser')
        logging.info(f"FitEasyのHTML解析を開始: 対象店舗 '{target_name}'")

        for ttl_div in soup_target.find_all('div', class_='p-congestionInfo__ttl'):
            if ttl_div.get_text(strip=True) == target_name:
                cont_div = ttl_div.find_next_sibling('div', class_='p-congestionInfo__cont')
                if cont_div:
                    for child in cont_div.find_all(True, recursive=False):
                        class_list = child.get('class')
                        if class_list and len(class_list) > 1:
                            m = re.search(r'(\d+)$', class_list[1])
                            if m:
                                level = int(m.group(1))
                                logging.info(f"店舗 '{target_name}' の混雑レベル: {level}")
                                return {
                                    "gym_name": target_name,
                                    "level": level
                                }
                            else:
                                logging.warning(f"店舗 '{target_name}' の2つ目のクラス名に数字が見つかりませんでした。クラス名: {class_list}")
                                raise Exception("2つ目のクラス名に数字が見つかりませんでした。")
                else:
                    logging.warning(f"店舗 '{target_name}' のp-congestionInfo__contが見つかりませんでした。")
                    raise Exception(f"{target_name}のp-congestionInfo__contが見つかりませんでした。")
        logging.warning(f"店舗 '{target_name}' がHTMLに見つかりませんでした。")
        raise Exception(f"{target_name}が見つかりませんでした。")

# グローバルなセッションインスタンス
_fit_easy_session = None

def get_fit_easy_session():
    """FitEasySessionのシングルトンインスタンスを取得"""
    global _fit_easy_session
    if _fit_easy_session is None:
        _fit_easy_session = FitEasySession()
    return _fit_easy_session

def fetch_congestion_info(target_name="イオンタウン弥富店"):
    """既存の関数との互換性を保つためのラッパー関数"""
    session_manager = get_fit_easy_session()
    return session_manager.fetch_congestion_data(target_name)

def fetch_multiple_congestion_info(target_names=None):
    """複数の店舗の混雑情報を一度のログインで取得"""
    if target_names is None:
        target_names = ["イオンタウン弥富店"]
    
    session_manager = get_fit_easy_session()
    results = []
    
    for target_name in target_names:
        try:
            result = session_manager.fetch_congestion_data(target_name)
            results.append(result)
            logging.info(f"店舗 '{target_name}' の情報取得完了")
        except Exception as e:
            logging.error(f"店舗 '{target_name}' の情報取得エラー: {e}")
            results.append({
                "gym_name": target_name,
                "level": None,
                "error": str(e)
            })
    
    return results
