import pandas as pd
from lib.googleSheets import GoogleSheets

def addUser_updatesheet2(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
   
    # check if the user is in list
    if user_id in users_list:
        new_users_list = users_list
    else:
        myWorksheet = GoogleSheets()
        df = myWorksheet.getWorksheet(sheetID, sheetRange)
        df[user_name] = 0
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df )

def deleUser_updatesheet2(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    df=df.drop(user_name,axis=1)
    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df )

def addUser(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    new_users_list = []
    new_user = 0
    # check if the user is in list
    if user_id in users_list:
        new_users_list = users_list
    else:
        # 1. add user id to list
        new_users_list = users_list
        new_users_list.append(user_id)
        new_user = 1

        # 2. update google sheet
        user_number=len(new_users_list)
        df_add = pd.DataFrame({'user_id': user_id, 'name': user_name,'current_asset': int(0) },index=[user_number])

        myWorksheet = GoogleSheets()
        df = myWorksheet.getWorksheet(sheetID, sheetRange)
        merged_df = df.append(df_add)
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )

    return {'new_users_list':new_users_list,'newuser':new_user}

def deleteUser(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    new_users_list = []
    case=0
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)

    if len(users_list)==0:
        new_users_list = users_list
        case=1
        return {'new_users_list':new_users_list,'case':case}
    
    if user_id in users_list:
        i = 0
        if i <len(users_list):
            if df.at[i, "name"]== user_name:
                if df.at[i, "current_asset"]== '0':
                    new_df = df.drop([i], axis=0)
                    new_users_list = users_list.remove(user_id)
                    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=new_df )
                    case=2
                else:
                    case=3
            
            i+=1
        return {'new_users_list':new_users_list,'case':case}
    else:
        case=4
        return {'new_users_list':new_users_list,'case':case}

# update current_asset
def count_current_asset(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    case=0
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)   
    all_current_asset = df[user_name]
    sum=0

    for i in range(len(df.index)):
        sum=int(all_current_asset[i])+sum
    return int(sum)

def update_current_asset(current_asset:int,user_id:str, user_name:str, users_list:list, sheetID, sheetRange):

    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)   
    df_update=df
    index=0
    all_current_asset = df["name"]
    for i in range(len(df.index)):
        if(all_current_asset[i] == user_name ):
            index=i-1
    update =current_asset
    df_update.iloc[index,2 ] = update
    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df_update )

#recommend payer
def recommend_payer(sheetID, sheetRange):
    payer=''
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)   
    worst_current_asset=0
    df_current_asset = df["current_asset"]
    df_name = df["name"]
    
    for i in range(len(df.index)):
        if(int(df_current_asset[i]) <= worst_current_asset):
            payer=df_name[i]
            worst_current_asset=int(df_current_asset[i])
    return payer

#recommend payer
def return_current_asset(sheetID, sheetRange):
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange) 

    df_current_asset = df["current_asset"]
    df_name = df["name"]
    payerlist1=[]
    list1=''
    payerlist2=[]
    list2=''
    for i in range(len(df.index)):
        if(int(df_current_asset[i]) <= 0):
            payerlist1.append(df_name[i])
            payerlist1.append(df_current_asset[i])
            list1=list1+df_name[i]+' : '+df_current_asset[i]+'元\n'
        else:
            payerlist2.append(df_name[i])
            payerlist2.append(df_current_asset[i])
            # list2='\n'.join(payerlist2)
            list2=list2+df_name[i]+' : '+df_current_asset[i]+'元\n'
    
    print(list1)
    # print('------------------------')
    print(list2)
    # return {'payerlist1':payerlist1,'payerlist2':payerlist2}
    return {'payerlist1':list1,'payerlist2':list2}