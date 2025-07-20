import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import logging # ロギングモジュールをインポート

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

def fetch_congestion_info(target_name="イオンタウン弥富店"):
    email = os.getenv("FITEASY_EMAIL")
    password = os.getenv("FITEASY_PASSWORD")
    if not email or not password:
        logging.error("環境変数 FITEASY_EMAIL または FITEASY_PASSWORD が設定されていません。")
        raise Exception("環境変数 FITEASY_EMAIL または FITEASY_PASSWORD が設定されていません。")

    login_payload = {
        'emailOrMemberID': email,
        'password': password,
    }

    session = requests.Session()
    logging.info(f"ログインページにGETリクエストを送信中: {LOGIN_URL}")
    try:
        response_get_login = session.get(LOGIN_URL, headers=HEADERS)
        response_get_login.raise_for_status() # 2xx以外のステータスコードで例外を発生
        logging.info(f"ログインページGET成功: ステータスコード {response_get_login.status_code}")
        logging.info(f"レスポンスヘッダー: {response_get_login.headers}")
        logging.info(f"レスポンスボディの一部 (最初の500文字): {response_get_login.text[:500]}")
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
    # POSTリクエスト時にはRefererをLOGIN_URL、Sec-Fetch-Siteを'same-origin'にするなど調整が必要な場合がある
    post_headers = HEADERS.copy()
    post_headers['Sec-Fetch-Site'] = 'same-origin' # フォーム送信時は通常'same-origin'

    try:
        response_login = session.post(LOGIN_URL, data=login_payload, headers=post_headers)
        response_login.raise_for_status()
        logging.info(f"ログインPOST成功: ステータスコード {response_login.status_code}")
        logging.info(f"ログイン後のURL: {response_login.url}")
        logging.info(f"レスポンスヘッダー: {response_login.headers}")
        logging.info(f"レスポンスボディの一部 (最初の500文字): {response_login.text[:500]}")
    except requests.exceptions.RequestException as e:
        logging.error(f"ログインPOSTリクエストでエラー: {e}")
        if e.response is not None:
            logging.error(f"ステータスコード: {e.response.status_code}")
            logging.error(f"レスポンスヘッダー: {e.response.headers}")
            logging.error(f"レスポンスボディ: {e.response.text}")
        raise

    # ログイン失敗条件の強化
    if response_login.url == LOGIN_URL or "ログイン失敗" in response_login.text or "メールアドレス、または会員IDとパスワードの組み合わせが間違っています" in response_login.text:
        logging.error("ログインに失敗しました。認証情報、またはログインリクエストのデータを確認してください。")
        raise Exception("ログインに失敗しました。認証情報、またはログインリクエストのデータを確認してください。")

    logging.info(f"目的のページにGETリクエストを送信中: {TARGET_URL}")
    # 目的ページアクセス時のヘッダー調整
    target_headers = HEADERS.copy()
    target_headers['Referer'] = response_login.url # ログイン後のURLを参照元とする
    target_headers['Sec-Fetch-Site'] = 'same-origin' # 同一サイト内遷移なので'same-origin'

    try:
        response_target = session.get(TARGET_URL, headers=target_headers)
        response_target.raise_for_status()
        logging.info(f"目的ページGET成功: ステータスコード {response_target.status_code}")
        logging.info(f"レスポンスヘッダー: {response_target.headers}")
        logging.info(f"レスポンスボディの一部 (最初の500文字): {response_target.text[:500]}")
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
