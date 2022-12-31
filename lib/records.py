import pandas as pd
#import pygsheets
import matplotlib.pyplot as plt
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
            type = 'UPDATE_RECORD'
            pass
        elif str3[0]=='還錢':
            event='還錢'
            money="-"+str3[1]
            type = 'UPDATE_RECORD'
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


def creat(new_id:int,user_id:str, user_name:str, users_list:list,event:str,amount:int,list1:list,time:str,test:str, sheetID, sheetRange):

    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    df_add = pd.DataFrame({'id': new_id,'user_id': user_id, 'payer': user_name,'event': event,'amount':amount,'time':time },index=[new_id])

    if list1==[]:
        user_number=len(users_list)
        everyone_money=int(amount)//int(user_number)
        
        i=0
        if i <len(users_list):
            new_df = df_add
            new_df[users_list[i]]= everyone_money
            i+=1

        new_df[user_id]=  int(amount)-int(everyone_money*(user_number-1))
        merged_df = df.append(new_df)
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )

    else:
        new_df=df_add 
        user_number=len(users_list)
        i=0
        allothermoney=0
        for i in range(len(users_list)):
            new_df[users_list[i]]= 0

            k=0
            for k in range(len(list1)):
                userid = list1[k].split(' ')[0]
                usermoney = list1[k].split(' ')[1]
                user_realid=return_userid_byname(userid,sheetID,test)
                if user_realid=='error':
                    new_id= -1
                    return str(new_id)
                if users_list[i]==user_realid:
                    allothermoney=int(allothermoney)+int(usermoney)
                    new_df[users_list[i]]= usermoney

                k=+1
            i+=1
        new_df[user_id]= int(amount)-int(allothermoney)
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

def df_to_png(df:pd.DataFrame()):
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    fig, ax =plt.subplots(1,1)
    data=df.values.tolist()
    column_labels=df.columns
    ax.axis('off')
    ax.table(cellText=data,colLabels=column_labels,loc="center")
    plt.savefig('static/table.png',dpi=200)
    return 0

if __name__ == '__main__':
    df = getRecords('1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw', 'records_<group_id>')
    df_to_png(df)