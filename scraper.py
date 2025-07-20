import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

LOGIN_URL = 'https://join.fiteasy.jp/mypage/login'
TARGET_URL = 'https://join.fiteasy.jp/mypage/congestion_list'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Referer': LOGIN_URL,
    'Content-Type': 'application/x-www-form-urlencoded'
}

load_dotenv()

def fetch_congestion_info(target_name="イオンタウン弥富店"):
    # 認証情報は環境変数から取得
    email = os.environ.get("FITEASY_EMAIL")
    password = os.environ.get("FITEASY_PASSWORD")
    if not email or not password:
        raise Exception("環境変数 FITEASY_EMAIL または FITEASY_PASSWORD が設定されていません。")

    login_payload = {
        'emailOrMemberID': email,
        'password': password,
    }

    session = requests.Session()
    response_get_login = session.get(LOGIN_URL, headers=HEADERS)
    response_get_login.raise_for_status()
    soup_login = BeautifulSoup(response_get_login.text, 'html.parser')
    csrf_token_input = soup_login.find('input', {'name': '_token'})
    if csrf_token_input:
        csrf_token = csrf_token_input['value']
        login_payload['_token'] = csrf_token
    else:
        raise Exception("CSRFトークンが見つかりませんでした。")

    response_login = session.post(LOGIN_URL, data=login_payload, headers=HEADERS)
    response_login.raise_for_status()

    if response_login.url == LOGIN_URL or "ログイン失敗" in response_login.text:
        raise Exception("ログインに失敗しました。認証情報、またはログインリクエストのデータを確認してください。")

    response_target = session.get(TARGET_URL, headers=HEADERS)
    response_target.raise_for_status()
    soup_target = BeautifulSoup(response_target.text, 'html.parser')

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
                            return {
                                "gym_name": target_name,
                                "level": level
                            }
                        else:
                            raise Exception("2つ目のクラス名に数字が見つかりませんでした。")
            else:
                raise Exception(f"{target_name}のp-congestionInfo__contが見つかりませんでした。")
    raise Exception(f"{target_name}が見つかりませんでした。")