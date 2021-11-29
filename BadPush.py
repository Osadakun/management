from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import random

scopes = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
json_file = 'linebot.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scopes=scopes)

# スプレッドシート用クライアントの準備
client = gspread.authorize(credentials)
SPREADSHEET_KEY = '9b898ec51baca23f18443c68f29b392b7d9a6b60'
worksheet = client.open_by_key(SPREADSHEET_KEY).sheet1

def add(userID):
	num = worksheet.cell(1,1).value
	num = int(num)
	try:
		worksheet.update_cell(num+1, 1, str(num))
		worksheet.update_cell(num+1, 2, userID)
		worksheet.update_cell(num+1, 3, "初期状態")
		worksheet.update_cell(num+1, 4, "休み/遅刻")
		worksheet.update_cell(num+1, 5, "理由/時間")
		worksheet.update_cell(num+1, 6, "選手名")
		worksheet.update_cell(num+1, 7, "備考")
		worksheet.update_cell(1, 1, str(num+1))
	except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
		ran = random.randrange(0,4)
		sleep(ran)


def remove(UserID):
	num = worksheet.cell(1,1).value
	num = int(num)
	cell = worksheet.find(UserID)
	row = cell.row

def checkActivity(UserID):
	cell = worksheet.find(UserID)
	activity = worksheet.cell(cell.row, 3).value
	return activity

def changeActivity(UserID,activity):
	cell = worksheet.find(UserID)
	for _ in range(10):			# 最大10回実行
		try:
			worksheet.update_cell(cell.row, 3, activity)
		except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
			ran = random.randrange(0,4)
			sleep(ran)
		else:					# 例外が発生しなかった場合、for を break
			break

def changeStatus(UserID,ChildStatus):
	cell = worksheet.find(UserID)
	for _ in range(10):			# 最大10回実行
		try:
			worksheet.update_cell(cell.row, 4, ChildStatus)
		except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
			ran = random.randrange(0,4)
			sleep(ran)
		else:					# 例外が発生しなかった場合、for を break
			break

def getStatus(UserID):
	cell = worksheet.find(UserID)
	ChildStatus = worksheet.cell(cell.row, 4).value
	return ChildStatus

def changeReason(UserID,Reason):
	cell = worksheet.find(UserID)
	for i in range(10):			# 最大10回実行
		try:
			worksheet.update_cell(cell.row, 5, Reason)
		except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
			ran = random.randrange(0,4)
			sleep(ran)
		else:					# 例外が発生しなかった場合、for を break
			break

def getReason(UserID):
	cell = worksheet.find(UserID)
	Reason = worksheet.cell(cell.row, 5).value
	return Reason

def changePlayer(UserID,PlayerName):
	cell = worksheet.find(UserID)
	for _ in range(10):			# 最大10回実行
		try:
			worksheet.update_cell(cell.row, 6, PlayerName)
		except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
			ran = random.randrange(0,4)
			sleep(ran)
		else:					# 例外が発生しなかった場合、for を break
			break

def getPlayer(UserID):
	cell = worksheet.find(UserID)
	PlayerName = worksheet.cell(cell.row, 6).value
	return PlayerName

def changeRemarks(UserID,Remarks):
	cell = worksheet.find(UserID)
	for i in range(10):			# 最大10回実行
		try:
			worksheet.update_cell(cell.row, 7, Remarks)
		except Exception as e:	# 例外発生時は0～4秒の時間待ち。同期ずらし。
			ran = random.randrange(0,4)
			sleep(ran)
		else:					# 例外が発生しなかった場合、for を break
			break

def getRemarks(UserID):
	cell = worksheet.find(UserID)
	Remarks = worksheet.cell(cell.row, 7).value
	return Remarks
