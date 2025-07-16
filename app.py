import time
from urllib import request, parse
import yaml
import json
from slack_sdk import WebClient

# params.yamlを読み込み
with open('params.yaml', 'r', encoding='utf-8') as f:
    params = yaml.safe_load(f)
SLACK_BOT_USER_OAUTH_TOKEN = params['SLACK_BOT_USER_OAUTH_TOKEN']
SLACK_APP_LEVEL_TOKEN = params['SLACK_APP_LEVEL_TOKEN']

rakuten_app_id = params['rakuten-api-app-id']
check_urls = params['check-url']
send_user = params['send_user']

class RakutenStockChecker:
    def __init__(self):
        self.rakuten_app_id = rakuten_app_id
        self.check_urls = check_urls
        self.first_time = True
            
        self.client = WebClient(token=SLACK_BOT_USER_OAUTH_TOKEN)
    
    def monitor_stock(self):
        base_url = 'https://app.rakuten.co.jp/services/api/BooksGame/Search/20170404?'

        format = 'json'
        title = 'Nintendo Switch 2（日本語・国内専用）'
        # title = 'バナンザ' # for test
        hardware = 'Nintendo Switch 2'
        label = '任天堂'
        booksGenreId = '006'
        outOfStockFlag = '1'

        url = base_url + 'applicationId=' + self.rakuten_app_id + \
              '&format=' + format + \
              '&title=' + parse.quote(title) + \
              '&hardware=' + parse.quote(hardware) + \
              '&label=' + parse.quote(label) + \
              '&booksGenreId=' + booksGenreId + \
              '&outOfStockFlag=' + outOfStockFlag
        
        print(f"URL: {url}")
        response = request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))

        if self.first_time:
            self.first_time = False
            message = "これから楽天ブックスの Nintendo Switch 2 の販売状況をお知らせします。よろしくお願いします。\n" \
                      "現在の販売状況は以下の通りです。\n"
            
            for item in data['Items']:
                item_info = item['Item']

                if item_info['availability'] == "11":
                    availability = '注文できない'
                elif item_info['availability'] == "5":
                    availability = '予約受付中'
                elif item_info['availability'] == "1":
                    availability = '在庫あり'
                else:
                    availability = '不明な状態　要チェック！'

                message += "--------------------\n" \
                            "商品名: " + item_info['title'] + "\n" \
                            "商品URL: " + item_info['itemUrl'] + "\n" \
                            "在庫状況: " + availability + "\n" \
                            "価格: " + str(item_info['itemPrice']) + "円\n"
                
            message += "--------------------\n" \
                        "5分ごとにチェックして、何か動きがあればお知らせします！\n"
            
            for user in send_user:
                res = self.client.conversations_open(users=user)
                channel_id = res['channel']['id']
                print(f"Channel ID: {channel_id}")
                self.client.chat_postMessage(
                    channel=channel_id,
                    text=message
                )
            
            self.first_time = False

        else:
            message = None
            is_changed = False
            for item in data['Items']:
                item_info = item['Item']

                if item_info['availability'] == "11":
                    availability = '注文できない'
                    continue
                elif item_info['availability'] == "5":
                    availability = '予約受付中'
                elif item_info['availability'] == "1":
                    availability = '在庫あり'
                else:
                    availability = '不明な状態　要チェック！'

                if not is_changed:
                    message = "Nintendo Switch 2の販売状況に動きがありました！ \n"

                message += "--------------------\n" \
                            "商品名: " + item_info['title'] + "\n" \
                            "商品URL: " + item_info['itemUrl'] + "\n" \
                            "在庫状況: " + availability + "\n" \
                            "価格: " + str(item_info['itemPrice']) + "円\n"
            
                message += "--------------------\n" \
                        "以上です。売り切れなければ、5分後にまたお知らせします！\n"

            for user in send_user:
                res = self.client.conversations_open(users=user)
                channel_id = res['channel']['id']
                print(f"Channel ID: {channel_id}")
                self.client.chat_postMessage(
                    channel=channel_id,
                    text=message
                )


def main():
    """メイン関数"""
    # try:
    #     # Socket Modeでアプリを起動
    #     logger.info("Slack Bot を起動しています...")
    # handler = SocketModeHandler(app, SLACK_APP_LEVEL_TOKEN)
    # handler.start()
    # except Exception as e:
    #     logger.error(f"アプリ起動エラー: {e}")
    checker = RakutenStockChecker()
    while True:
        checker.monitor_stock()
        time.sleep(30)  # 5分ごとにチェック

if __name__ == "__main__":
    main()

