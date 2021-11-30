from flask import Flask, request, abort, render_template,redirect
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
	UnfollowEvent, FollowEvent
)
import os
import gspread
import oauth2client
import linebot
import datetime

import BadPush

#アクセスキーの取得
app = Flask(__name__)

#BOTの認証。Heroku環境で設定済み。
# YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
# YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi("wTK1FUq7YT+6R6mv+gw2WSwUqee3rk4RKgKSOLR+mquDRaYOvIztvgJoO1DBzDZ7ilpXpEuxCNrCO230IokzphUHs1dFhnEAapeTKGgwlFCp3G77QUlgzmD1hp2fgi57Gs8Dr8eTsrLvj2tPuvor0wdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("4baa838b574403306f55f93c8c032e2b")

@app.route("/")
def hello_world():
	return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

@handler.add(FollowEvent)
def handle_follow(event):
	"""
	友だち追加したときのイベント。
	UsersDBにID、アクティビティを追加。
	"""
	UserID = event.source.user_id
	line_bot_api.reply_message(event.reply_token,
		[
			TextSendMessage(text='minatoJBSC【公式】です。\n友達追加ありがとうございます!!'),
			TextSendMessage(text='これからは練習の休み、遅刻の連絡はこのアカウントからお願いします。'),
			TextSendMessage(text='本日の練習をお休みする場合は「休み」、遅れて参加の場合は「遅刻」と送信して下さい。')
		]
	)

	UserID = event.source.user_id
	BadPush.add(UserID)
	line_bot_api.reply_message(event.reply_token,
		[
			TextSendMessage(text='minatoJBSC【公式】です。\n友達追加ありがとうございます!!'),
			TextSendMessage(text='これからは練習の休み、遅刻の連絡はこのアカウントからお願いします。'),
			TextSendMessage(text='本日の練習をお休みする場合は「休み」、遅れて参加の場合は「遅刻」と送信して下さい。')
		]
	)

@handler.add(UnfollowEvent)
def handle_unfollow(event):
	"""
	ブロックされた時のイベント。
	UsersDBのIDとアクティビティを削除。
	"""
	UserID = event.source.user_id
	BadPush.remove(UserID)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	"""
	UserｓのActivityによって条件分岐。
	noneQuestionがデフォルト→メニューを表示。
	waitQestionが質問待ち状態→次に入力されたテキストが質問になる。
	"""
	UserID = event.source.user_id
	text = event.message.text
	activity = BadPush.checkActivity(UserID)

	if activity == "初期状態":
		if (text =="休み")or(text =="休")or(text =="やすみ"):
			BadPush.changeActivity(UserID,"休み遅刻")
			BadPush.changeStatus(UserID,"休み")
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='お休みですね。\n理由を選択して送信して下さい。\n「家庭都合」、「体調不良」、「怪我」、「その他」')
				]
			)
		elif (text =="遅刻")or(text =="遅")or(text =="ちこく"):
			BadPush.changeActivity(UserID,"休み遅刻")
			BadPush.changeStatus(UserID,"遅刻")
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='遅刻ですね。\n到着予定時間(見込)を送信して下さい。')
				]
			)
		else:
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='申し訳ありませんその言葉は理解しかねます。\n「休み」もしくは「遅刻」と送信して下さい。')
				]
			)
	elif activity == "休み遅刻":
		ChildStat = BadPush.getStatus(UserID)
		if (ChildStat =="休み"):
			if (text =="家庭都合")or(text =="体調不良")or(text =="怪我")or(text =="その他"):
				BadPush.changeActivity(UserID,"選手名")
				BadPush.changeReason(UserID,text)
				line_bot_api.reply_message(event.reply_token,
					[
						TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
					]
				)
			else:
				line_bot_api.reply_message(event.reply_token,
					[
						TextSendMessage(text='お休みの理由を選択して送信して下さい。\n「家庭都合」、「体調不良」、「怪我」、「その他」')
					]
				)
		elif (ChildStat =="遅刻"):
			BadPush.changeActivity(UserID,"選手名")
			BadPush.changeReason(UserID,text)
			line_bot_api.reply_message(event.reply_token,
					[
						TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
					]
				)
	elif activity == "選手名":
		BadPush.changePlayer(UserID,text)
		BadPush.changeActivity(UserID,"補足")
		line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text='その他補足事項等があれば入力し送信して下さい。\n特になければ「なし」で送信して下さい。')
			]
		)
	elif activity == "補足":
		BadPush.changeRemarks(UserID,text)
		BadPush.changeActivity(UserID,"最終状態")
		Status_text = BadPush.getStatus(UserID)
		Reason_text = BadPush.getReason(UserID)
		Player_text = BadPush.getPlayer(UserID)
		Remarks_text = BadPush.getRemarks(UserID)
		line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text=Player_text+"\n"+Status_text+":"+Reason_text+"\n"+Remarks_text),
				TextSendMessage(text="上記で登録します。よろしければ「はい」を、訂正がある場合は「いいえ」を送信して下さい。")
			]
		)
	elif activity =="最終状態":
		if ( text == 'はい'):
			BadPush.changeActivity(UserID,"初期状態")
			Status_text = BadPush.getStatus(UserID)
			Reason_text = BadPush.getReason(UserID)
			Player_text = BadPush.getPlayer(UserID)
			Remarks_text = BadPush.getRemarks(UserID)
			to = "U2beb3645d43471171df9ef7886968c39"

			messages = TextSendMessage(text=Player_text+"\n"+Status_text+":"+Reason_text+"\n"+Remarks_text)
			line_bot_api.multicast(to, messages=messages)
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text = '連絡を受け付けました。ありがとうございました。'),
					TextSendMessage(text='本日の練習をお休みする場合は「休み」、遅れて参加の場合は「遅刻」と送信して下さい。')
				]
			)
		elif (text == 'いいえ'):
			BadPush.changeActivity(UserID,"初期状態")
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text = 'お手数ですが初めからやり直して下さい。'),
					TextSendMessage(text='本日の練習をお休みする場合は「休み」、遅れて参加の場合は「遅刻」と送信して下さい。')
				]
			)
		else:
			Status_text = BadPush.getStatus(UserID)
			Reason_text = BadPush.getReason(UserID)
			Player_text = BadPush.getPlayer(UserID)
			Remarks_text = BadPush.getRemarks(UserID)
			d_today = datetime.date.today()
			send_message = d_today+"\n"+Player_text+"\n"+Status_text+":"+Reason_text+"\n"+Remarks_text
			line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text=send_message),
					TextSendMessage(text="上記で登録します。よろしければ「はい」を、訂正がある場合は「いいえ」を送信して下さい。")
				]
			)
			line_bot_api.push_message(to, messages=send_message)

if __name__ == "__main__":
	port = int(os.getenv("PORT",5000))
	app.run(host="0.0.0.0", port=port)
