import foursquare
import os

# 作成したアプリの情報を設定
CLIENT_ID = os.environ['FORSQUARE_CLIENT_ID']
CLIENT_SECRET = os.environ['FORSQUARE_CLIENT_SECRET']
REDIRECT_URI = "http://localhost/"

# clientオブジェクトを作成
client = foursquare.Foursquare(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

# アプリの認証
auth_uri = client.oauth.auth_url()
print(auth_uri)

# 表示されたauth_uriにブラウザからアクセスし、URIの「?code=」の後から「#」の前までの文字列を入力
code=input("INPUT CODE:")
# アクセストークンを取得
access_token = client.oauth.get_token(code)
print(access_token)
