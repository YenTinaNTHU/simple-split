from flask import Flask
app = Flask(__name__)

from datetime import datetime
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
SERVER_URL = os.getenv('SERVER_URL ')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# all data should be recorded at google sheet
# these are just for testing
group_id = ""
user_ids = []
recordnumber = 1

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
    newcoming_text = "謝謝邀請我這個機器人來至此群組！！我會盡力為大家服務的～\n\n請加我好友並輸入「加入分帳」以使用分帳功能\n\n若欲查詢功能列表請輸入「功能」"
    line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=newcoming_text)
        )
    addGroup(event.source.group_id)
    print(f'line bot join the group {event.source.group_id}')
    # member_ids_res = line_bot_api.get_group_member_ids(group_id)
    # print(member_ids_res)

@handler.add(LeaveEvent)
def handle_leave(event):
    deleteGroup(event.source.group_id)
    print(f'line bot leave the group {event.source.group_id}')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # since our account have not been verified yet, we cannot get all group member by group id
    # so we should add the member when they send message
    user_id = event.source.user_id
    # take user name
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    group_id = event.source.group_id
    print(group_id)
    sheet_user="users_"+group_id 
    sheet_record="records_"+group_id

    m_text = event.message.text

    # check if active
    if not isActive(group_id):
        if m_text == '開啟極簡分帳':
            message = TextSendMessage(text = "感謝大家願意再次開啟極簡分帳！我會盡力為大家服務的～\n\n若欲查詢功能列表請輸入\n「功能」")
            line_bot_api.reply_message(event.reply_token, message)
            setActive(group_id, True)
            print('line bot is active')
        return
    
    if m_text == '功能':
        message = TextSendMessage(
            text = "功能：\n\n記帳\n查詢\n分帳\n付款人推薦\n還錢\n收錢\n退出\n開啟機器人\n關閉機器人\n移除機器人\n\n慾查詢功能使用方法請輸入\n「功能名稱+方法」\n例:記帳方法"
        )
        line_bot_api.reply_message(event.reply_token, message)    
    elif m_text == '記帳方法':
        message = TextSendMessage(
            text = "由付款人輸入\n\n平分:\n\n請輸入\n「記帳\n項目 總金額」\n\n按金額分:\n\n請輸入\n「記帳\n項目 總金額\n@欠款人 欠款金額」\n\n按比例分:\n\n請輸入\n「記帳\n項目 總金額\n@欠款人 比例」"
        )
        line_bot_api.reply_message(event.reply_token, message)    
    elif m_text == '查詢方法':
        message = TextSendMessage(
            text = "這將會印出目前的記帳款項\n\n請輸入\n「查詢」"
        )
        line_bot_api.reply_message(event.reply_token, message)  
    elif m_text == '分帳方法':
        message = TextSendMessage(
            text = "這將會顯示目前的欠款情形\n\n請輸入\n「分帳」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '付款人推薦方法':
        message = TextSendMessage(
            text = "這將會依據目前欠款最多的人進行推薦\n\n請輸入\n「那誰付錢」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '還錢方法':
        message = TextSendMessage(
            text = "若欲還錢請輸入\n「還錢 還款金額」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '收錢方法':
        message = TextSendMessage(
            text = "若欲收錢請輸入\n「收錢 收款金額」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '退出方法':
        message = TextSendMessage(
            text = "若欲退出分帳列表請輸入\n「退出分帳」\n\n這將會導致您無法再使用分帳功能"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '開啟機器人方法':
        message = TextSendMessage(
            text = "若機器人處於關閉狀態欲開啟請輸入\n「開啟極簡分帳」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '關閉機器人方法':
        message = TextSendMessage(
            text = "若欲關閉機器人請輸入\n「關閉極簡分帳」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    elif m_text == '移除機器人方法':
        message = TextSendMessage(
            text = "若欲將機器人移出群組請輸入\n「刪除極簡分帳」"
        )
        line_bot_api.reply_message(event.reply_token, message) 
    else:
        pass

    checkrecord = checkMessageType(m_text)
    type=checkrecord['type']
    events=checkrecord['event']
    amount=checkrecord['amount']
    list1=checkrecord['list1']
    money=checkrecord['money']
    deleid=checkrecord['deleid']

    global recordnumber
    time=datetime.now()
    if type == 'CREATE_RECORD':
        print('CREATE_RECORD')
        tmp=creat(recordnumber,user_id, user_name, user_ids,events,amount,list1,str(time) ,sheetRange2=sheet_user, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        
        if tmp=="-1":
            message = TextSendMessage(
                        text = "每位使用者都須先加入分帳喔"
                        )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            message = TextSendMessage(
                        text = "第 "+tmp+" 筆資料記帳成功"
                        )
            line_bot_api.reply_message(event.reply_token, message)
            recordnumber=recordnumber+1
            alluser_update(user_ids,sheetID=GOOGLE_SHEET_ID, sheetRange1=sheet_user,sheetRange2=sheet_record)
        pass
    
    if type == 'READ_RECORD':
        pass
    if type == 'UPDATE_RECORD':
        update(recordnumber,user_id, user_name, user_ids,events,money,str(time) ,sheet_user, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        message = TextSendMessage(
                    text = "更新成功"
                    )
        line_bot_api.reply_message(event.reply_token, message)
        recordnumber=recordnumber+1
        alluser_update(user_ids,sheetID=GOOGLE_SHEET_ID, sheetRange1=sheet_user,sheetRange2=sheet_record)
        print('UPDATE_RECORD')
        pass
    if type == 'DELETE_RECORD':
        delet(deleid,sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        message = TextSendMessage(
                    text = "第 "+str(deleid)+" 筆資料刪除成功"
                    )
        line_bot_api.reply_message(event.reply_token, message)
        alluser_update(user_ids,sheetID=GOOGLE_SHEET_ID, sheetRange1=sheet_user,sheetRange2=sheet_record)
        print('DELETE_RECORD')
        pass

    if m_text == '查詢':
        df = getRecords(sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        message = TextSendMessage(
            text = df.to_string(header=False, index=False)
            )
        line_bot_api.reply_message(event.reply_token, message)
        # message = ImageSendMessage(original_content_url = ngrok_url + "/static/" + event.message.id + ".png", preview_image_url = ngrok_url + "/static/" + event.message.id + ".png")
        print('read record')

    
    if m_text == '記帳':
        #count current asset
        current_asset = count_current_asset(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        # update user_google_sheet
        update_current_asset(current_asset,user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_user)
        pass
    elif m_text == '加入分帳':
        addUser_updatesheet2(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
        add = addUser(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_user)
        new_users_list=add['new_users_list']
        isnew_user=add['newuser']
        if isnew_user==0:
            message = TextSendMessage(
                    text = user_name+"已經在行列之中了喔!"
                    )
            line_bot_api.reply_message(event.reply_token, message)
        elif isnew_user ==1:
            message = TextSendMessage(
                    text = user_name+"成功加入"
                    )
            line_bot_api.reply_message(event.reply_token, message)
        elif isnew_user ==2:
            message = TextSendMessage(
                    text = user_name+"更改名字成功"
                    )
            line_bot_api.reply_message(event.reply_token, message)
        pass
    elif m_text == '退出分帳':
        delete = deleteUser(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_user)
        new_users_list=delete['new_users_list']
        delecase=delete['case']
        if delecase==1:
            message = TextSendMessage(
                text = "目前沒有人在分帳行列中"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==2:
            deleUser_updatesheet2(user_id, user_name, user_ids, sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_record)
            message = TextSendMessage(
                text = user_name+"退出成功"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==3:
            message = TextSendMessage(
                text = user_name+"退出失敗 你還欠錢!"
                )
            line_bot_api.reply_message(event.reply_token, message)
        elif delecase==4:
            message = TextSendMessage(
                text = user_name+"沒有加入分帳行列喔!"
                )
            line_bot_api.reply_message(event.reply_token, message)
        else:
            print("Something error")
    
    elif m_text == '分帳':
        # TODO 顯示大家目前的欠款情形
        return_asset = return_current_asset(sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_user)
        payerlist1=return_asset['payerlist1']
        payerlist2=return_asset['payerlist2']
        message = TextSendMessage(
                text = "目前欠款情形\n"
                +"\n"
                +"欠錢的人\n"+payerlist2
                +"\n"
                +"拿錢的人\n"+payerlist1
                )
        line_bot_api.reply_message(event.reply_token, message)
        pass

    
    elif m_text == '刪除極簡分帳':
        leaving_text = "再見了各位..."
        line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text=leaving_text)
            )
        line_bot_api.leave_group(event.source.group_id)

    elif m_text == '那誰付錢':
        recommend = recommend_payer(sheetID=GOOGLE_SHEET_ID, sheetRange=sheet_user)
        message = TextSendMessage(
                    text = "根據我的經驗，我推薦"+recommend+"付錢"
                    )
        line_bot_api.reply_message(event.reply_token, message)
        pass

    elif m_text == '關閉極簡分帳':
        setActive(group_id, False)
        message = TextSendMessage(text = "已關閉極簡分帳，若要再次開啟請輸入「開啟即減分帳」。")
        line_bot_api.reply_message(event.reply_token, message)
        print('line bot close')

    elif m_text == '@文字' :
        try:
            message = TextSendMessage(
                text = "使用方法：\n選擇收錢、還錢......"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage( text = "error"))
    elif m_text == '@快速選單':
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
    else:
        pass

if __name__ == '__main__':
    app.run(port=5002)