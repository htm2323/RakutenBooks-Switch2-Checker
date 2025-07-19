import os
import time
from urllib import request, parse
import yaml
import json
from slack_sdk import WebClient
import logging

# logフォルダが存在しない場合は作成
os.makedirs('log', exist_ok=True)

# ログ設定
logger = logging.getLogger("switch2_notifier")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("log/switch2_notifier.log", encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

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
        
        try:
            response = request.urlopen(url)
            data = json.loads(response.read().decode('utf-8'))
            logger.info(f"succeeed checking! URL: {url}")
        except Exception as e:
            logger.error(f"楽天API使用時にエラー発生: {e}")
            return

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
                    logger.info(f"不明な在庫状態: {item_info['title']} - 状態: {item_info['availability']}")

                message += "--------------------\n" \
                            "商品名: " + item_info['title'] + "\n" \
                            "商品URL: " + item_info['itemUrl'] + "\n" \
                            "在庫状況: " + availability + "\n" \
                            "価格: " + str(item_info['itemPrice']) + "円\n"
                
            message += "--------------------\n" \
                        "5分ごとにチェックして、何か動きがあればお知らせします！\n"
            
            for user in send_user:
                try:
                    res = self.client.conversations_open(users=user)
                    channel_id = res['channel']['id']
                    self.client.chat_postMessage(
                        channel=channel_id,
                        text=message
                    )
                    logger.info(f"Sending complete! Channel ID: {channel_id}")
                except Exception as e:
                    logger.error(f"Slackメッセージ送信エラー: {e}")
                    logger.info(f"送信しようとしたメッセージ: {message}")
                    debug_message = "Slackメッセージ送信エラー: " + e + "\n" + message

                    res = self.client.conversations_open(users=send_user[0])  # Fallback to first user if error occurs
                    channel_id = res['channel']['id']
                    self.client.chat_postMessage(
                        channel=channel_id,
                        text=debug_message
                    )
                    logger.info(f"Sending complete! Channel ID: {channel_id}")
                    continue
            
            self.first_time = False

        else:
            message = None
            is_first = True
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
                    logger.info(f"不明な在庫状態: {item_info['title']} - 状態: {item_info['availability']}")

                if is_first:
                    message = "📢 Nintendo Switch 2の販売状況に動きがありました！ \n"
                    is_first = False

                message += "--------------------\n" \
                            "商品名: " + item_info['title'] + "\n" \
                            "商品URL: " + item_info['itemUrl'] + "\n" \
                            "在庫状況: " + availability + "\n" \
                            "価格: " + str(item_info['itemPrice']) + "円\n"

            if message is not None:
                message += "--------------------\n" \
                        "以上です。売り切れなければ、5分後にまたお知らせします！\n"
                logger.info(f"Send message: {message}")
                for user in send_user:
                    try:
                        res = self.client.conversations_open(users=user)
                        channel_id = res['channel']['id']
                        self.client.chat_postMessage(
                            channel=channel_id,
                            text=message
                        )
                        logger.info(f"Sending complete! Channel ID: {channel_id}")
                    except Exception as e:
                        logger.error(f"Slackメッセージ送信エラー: {e}")
                        logger.info(f"送信しようとしたメッセージ: {message}")
                        debug_message = "Slackメッセージ送信エラー: " + e + "\n" + message

                        res = self.client.conversations_open(users=send_user[0])  # Fallback to first user if error occurs
                        channel_id = res['channel']['id']
                        self.client.chat_postMessage(
                            channel=channel_id,
                            text=debug_message
                        )
                        logger.info(f"Sending complete! Channel ID: {channel_id}")
                        continue


def main():
    """メイン関数"""
    checker = RakutenStockChecker()
    while True:
        checker.monitor_stock()
        time.sleep(300)  # 5分ごとにチェック

if __name__ == "__main__":
    main()

