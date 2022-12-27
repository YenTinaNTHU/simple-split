from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import JoinEvent, LeaveEvent
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction

import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, './lib')
from googleSheets import GoogleSheets
from groups import *
from users import *
from records import *

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# all data should be recorded at google sheet
# these are just for testing
group_id = ""
user_ids = []

@app.route("/callback", methods=['Post'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    # the global variables
    global group_id
    
    newcoming_text = "謝謝邀請我這個機器人來至此群組！！我會盡力為大家服務的～"
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text)
        )
    addGroup(event.source.group_id, event.reply_token)
    print(f'line bot join the group {event.source.group_id}')
    # member_ids_res = line_bot_api.get_group_member_ids(group_id)
    # print(member_ids_res)

@handler.add(LeaveEvent)
def handle_leave(event):
    print("leave")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # the global variables
    global user_ids

    # since our account have not been verified yet, we cannot get all group member by group id
    # so we should add the member when they send message
    user_id = event.source.user_id
    # take user name
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    # user_ids = addUser(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表1')

    m_text = event.message.text

    type = checkMessageType(m_text)

    # TODO: records' CRUD
    if type == 'CREATE_RECORD':
        pass
    if type == 'READ_RECORD':
        pass
    if type == 'UPDATE_RECORD':
        pass
    if type == 'DELETE_RECORD':
        pass

    # TODO: members' CRUD

    if m_text == '記帳':
        #count current asset
        current_asset = count_current_asset(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表2')
        #update user_google_sheet
        update_current_asset(current_asset,user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表1')
        # TODO: maybe we can try LIFF
        pass
    if m_text == '加入分帳':
        # TODO add member
        # {'new_users_list':new_users_list,'newuser':new_user}
        addUser_updatesheet2(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表2')
        add = addUser(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表1')
        new_users_list=add['new_users_list']
        isnew_user=add['newuser']
        if isnew_user==0:
            message = TextSendMessage(
                    text = "你已經在行列之中了喔!"
                    )
            line_bot_api.reply_message(event.reply_token, message)
        elif isnew_user ==1:
            message = TextSendMessage(
                    text = "成功加入"
                    )
            line_bot_api.reply_message(event.reply_token, message)
        pass
    if m_text == '退出分帳':
        # TODO delete member
        # 需要還錢才能退出
        delete = deleteUser(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表1')
        new_users_list=delete['new_users_list']
        delecase=delete['case']
        if delecase==1:
            message = TextSendMessage(
                text = "目前沒有人在分帳行列中"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==2:
            deleUser_updatesheet2(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange='工作表2')
            message = TextSendMessage(
                text = "退出成功"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==3:
            message = TextSendMessage(
                text = "失敗 你還欠錢!"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==4:
            message = TextSendMessage(
                text = "你沒有加入分帳行列喔!"
                )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            print("Something error")
    
    if m_text == '分帳':
        # TODO 顯示大家目前的欠款情形
        pass

    if m_text == '還錢':
        # TODO 應該跟記帳差不多
        pass

    if m_text == '那誰付錢':
        # '根據我的經驗，我推薦<user_name>付錢'
        pass

    if m_text == '@文字' :
        try:
            message = TextSendMessage(
                text = "使用方法：\n選擇收錢、還錢......"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage( text = "error"))
    if m_text == '@快速選單':
        try:
            message = TextSendMessage(
                text = "請選擇服務",
                quick_reply = QuickReply(
                    items = [
                        QuickReplyButton(
                            action = MessageAction(label='分帳', text='@文字')
                        ),
                        QuickReplyButton(
                            action = MessageAction(label='還錢', text='還錢')
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage( text = "error"))

if __name__ == '__main__':
    app.run(port=5002)