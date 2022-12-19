import pandas as pd
from lib.googleSheets import GoogleSheets

def addUser(user_id:str, users_list:list, sheetID, sheetRange):
    new_users_list = []
    # check if the user is in list
    if user_id in users_list:
        new_users_list = users_list
    else:
        # 1. add user id to list
        new_users_list = users_list
        new_users_list.append(user_id)
        # 2. update google sheet
        myWorksheet = GoogleSheets()
        df = myWorksheet.getWorksheet(sheetID, sheetRange)
        df[user_id] = 0
        myWorksheet.setWorksheet( spreadsheetId=sheetID, range=sheetRange, df=df )

    # return new user list
    return new_users_list

# TODO update user's names

