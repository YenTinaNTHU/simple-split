import pandas as pd
from googleSheets import GoogleSheets

import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def addGroup(group_id: str, reply_token:str):
    # add meta data
    sheet = GoogleSheets()
    sheet.appendWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        range='global',
        df=pd.DataFrame(
            {
                'group_id': [group_id],
                'reply_token': [reply_token],
            }
        )
    )
    # create new sheets
    users_col = ['user_id', 'name', 'current_asset']
    records_col = ['id', 'user_id', 'payer', 'event', 'amount']

    sheet.addWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        title=f'users_{group_id}'
    )
    sheet.appendWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'users_{group_id}',
        df=pd.DataFrame([users_col])
    )
    sheet.addWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        title=f'records_{group_id}'
    )
    sheet.appendWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'records_{group_id}',
        df=pd.DataFrame([records_col])
    )

    return 0



def deleteGroup(group_id:str):
    sheet = GoogleSheets()
    # delete new sheet
    sheet.deleteWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        title=f'records_{group_id}'
    )
    sheet.deleteWorksheet(
        spreadsheetId=GOOGLE_SHEET_ID,
        title=f'users_{group_id}'
    )

    # delete meta data
    df = sheet.getWorksheet(spreadsheetId=GOOGLE_SHEET_ID, range='global')
    idx = df['group_id'].loc[lambda x: x==group_id].index[0]
    token = df['reply_token'][idx]
    sheet.deleteWorksheetRow(
        spreadsheetId=GOOGLE_SHEET_ID,
        range='global',
        idx=int(idx)
    )
    return token


if __name__ == '__main__':
    print(
        addGroup(
            group_id='000000a',
            reply_token='1111111'
        )
    )
    print(
        addGroup(
            group_id='000001b',
            reply_token='222222'
        )
    )
    print(
        deleteGroup(
            group_id='000000a',
        )
    )
