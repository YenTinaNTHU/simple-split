import pandas as pd
#import pygsheets
from users import *
from googleSheets import GoogleSheets

def checkMessageType(msg:str):
    str1=msg.replace("@", "")
    str2 = str1.split('\n')
    lenstr=len(str2)
    deleid=0
    money=0
    event=''
    amount=0
    list1=[]

    if lenstr==1:
        # other function、還錢、收錢、刪除
        str3 = str1.split(' ')
        if str3[0]=='刪除記帳':
            deleid=str3[1]
            type = 'DELETE_RECORD'
            pass
        elif str3[0]=='收錢':
            event='收錢'
            money=str3[1]
            type = 'CREATE_RECORD'
            pass
        elif str3[0]=='還錢':
            event='還錢'
            money="-"+str3[1]
            type = 'CREATE_RECORD'
            pass
        else:
            type = 'error'
            pass

    elif lenstr==2:
        # 平分
        str3 = str2[1].split(' ')
        if str2[0]=='記帳':
            event=str3[0]
            amount=str3[1]
            type = 'CREATE_RECORD'
            pass

    elif lenstr>=3:
        # 照金額分
        str3 = str2[1].split(' ')
        if str2[0]=='記帳':
            event=str3[0]
            amount=str3[1]
            list1=str2[2:]
            type = 'CREATE_RECORD'
            pass
    pass

    return {'type':type,'event':event,'amount':amount,'list1':list1,'money':money,'deleid':deleid}


def creat(new_id:int,user_id:str, user_name:str, users_list:list,event:str,amount:int,list1:list,time:str,sheetRange2, sheetID, sheetRange, group_id):
    myWorksheet = GoogleSheets()
    # update record num
    global_df = myWorksheet.getWorksheet(sheetID, 'global')
    global_df.loc[global_df.group_id==group_id, 'record_num'] = new_id
    myWorksheet.setWorksheet(spreadsheetId=sheetID, range='global', df=global_df)

    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    df_add = pd.DataFrame({'id': new_id,'user_id': user_id, 'payer': user_name,'event': event,'amount':amount,'time':time },index=[new_id])

    if list1==[]:
        user_number=len(users_list)
        everyone_money=int(amount)//int(user_number)
        
        i=0
        for i in range(len(users_list)):
            new_df = df_add
            new_df[users_list[i]]= everyone_money
            i+=1

        new_df[user_id]=  0-int(everyone_money*(user_number-1))
        merged_df = df.append(new_df)
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )

    else:
        new_df=df_add 
        user_number=len(users_list)
        i=0
        allothermoney=0
        print(list1)
        for i in range(len(users_list)):
            new_df[users_list[i]]= 0
        i+=1

        k=0
        for k in range(len(list1)):
            tmpmoney= list1[k].split(' ')
            username = tmpmoney[0]
            usermoney = tmpmoney[1]
            print(username)
            print(usermoney)
            df_user = myWorksheet.getWorksheet(sheetID, sheetRange2)
            user_realid='error'
            # print(df_user)
            for i in range(len(df_user.index)):
                if df_user['name'][i] == username:
                    user_realid= df_user['user_id'][i]

            if user_realid=='error':
                new_id= -1
                return str(new_id)

            allothermoney=int(allothermoney)+int(usermoney)
            new_df[user_realid]= usermoney
            print("usermoney:"+usermoney)
            k=+1
            
        new_df[user_id]= 0-int(allothermoney)
        merged_df = df.append(new_df)
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )
    return str(new_id)

def delet(deleid,sheetID, sheetRange):

    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    i=0
    for i in range(len(df.index)):
        if int(deleid) == int(df['id'][i]):
            df_del=df.drop(index=[i])
            myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df_del )


def update(new_id:int,user_id:str, user_name:str, users_list:list,event:str,money:int,time:str,test:str, sheetID, sheetRange):

    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    df_add = pd.DataFrame({'id': new_id,'user_id': user_id, 'payer': user_name,'event':event ,'amount':money,'time':time },index=[new_id])

    new_df=df_add 
    i=0
    for i in range(len(users_list)):
        new_df[users_list[i]]= 0

        if users_list[i]==user_id:
            new_df[users_list[i]]= money
        i+=1

    merged_df = df.append(new_df)
    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )

def getRecords(sheetID:str, sheetRange:str):
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    data_df = df.loc[:, ['id','payer','event','amount']]
    return data_df

def getRecordsNumber(sheetID:str, group_id):
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, 'global')
    record_num = int((df.loc[df.group_id==group_id,'record_num']).values[0])
    return record_num

# if __name__ == '__main__':
#     print(
#         getRecordsNumber(
#             sheetID='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
#             sheetRange='records_<group_id>'
#             )
#         )