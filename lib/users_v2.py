import pandas as pd
from lib.googleSheets import GoogleSheets

def addUser_updatesheet2(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
   
    # check if the user is in list
    if user_id in users_list:
        new_users_list = users_list
        # print("old")
        # print(new_users_list)
    else:
        myWorksheet = GoogleSheets()
        df = myWorksheet.getWorksheet(sheetID, sheetRange)
        df[user_name] = 0
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df )

def deleUser_updatesheet2(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)
    df=df.drop(user_name,axis=1)
    # print(df)
    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df )

def addUser(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    new_users_list = []
    new_user = 0
    # check if the user is in list
    if user_id in users_list:
        new_users_list = users_list
        # print("old")
        # print(new_users_list)
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

        # print("new")
        # print(merged_df)

        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=merged_df )

    # return new_users_list
    return {'new_users_list':new_users_list,'newuser':new_user}

# TODO update user's names

# delete user
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
        # print("有加入分帳")
        i = 0
        if i <len(users_list):
            if df.at[i, "name"]== user_name:
                # print("users_list and df index is the same")
                # print(df.at[i, "current_asset"])
                if df.at[i, "current_asset"]== '0':
                    new_df = df.drop([i], axis=0)
                    new_users_list = users_list.remove(user_id)
                    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=new_df )
                    case=2
                    # print("delete done!")
                else:
                    case=3
                    # print("你還欠錢!")
            
            i+=1
        return {'new_users_list':new_users_list,'case':case}
    else:
        case=4
        # print("沒有加入分帳")
        return {'new_users_list':new_users_list,'case':case}

# update current_asset
def count_current_asset(user_id:str, user_name:str, users_list:list, sheetID, sheetRange):
    # new_users_list = users_list
    case=0
    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)   

    # print("yes in the googlesheet")
    all_current_asset = df[user_name]
    sum=0
    # userid = str(user_id)
    for i in range(len(df.index)):
        sum=int(all_current_asset[i])+sum
    # print(sum)
    return int(sum)

def update_current_asset(current_asset:int,user_id:str, user_name:str, users_list:list, sheetID, sheetRange):

    myWorksheet = GoogleSheets()
    df = myWorksheet.getWorksheet(sheetID, sheetRange)   
    df_update=df
    # all_current_asset = df[user_name]
    index=0
    all_current_asset = df["name"]
    # userid = str(user_id)
    for i in range(len(df.index)):
        if(all_current_asset[i] == user_name ):
            index=i-1
        # print(user_name)
        # print(all_current_asset[i])
    update =current_asset
    # print(current_asset)
    df_update.iloc[index,2 ] = update
    # print(df_update)
    myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df_update )
    # return {'account_current_asset':sum}
