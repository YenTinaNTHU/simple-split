from lib.googleAPIs import GoogleAPIClient
import pandas as pd

class GoogleSheets(GoogleAPIClient):
    def __init__(self) -> None:
        # 呼叫 GoogleAPIClient.__init__()，並提供 serviceName, version, scope
        super().__init__(
            'sheets',
            'v4',
            ['https://www.googleapis.com/auth/spreadsheets'],
        )

    def getWorksheet(self, spreadsheetId: str, range: str):
        request = self.googleAPIService.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=range,
        )
        result = request.execute()['values']
        header = result[0]
        del result[0]
        return pd.DataFrame(result, columns=header)

    def clearWorksheet(self, spreadsheetId: str, range: str):
        self.googleAPIService.spreadsheets().values().clear(
            spreadsheetId=spreadsheetId,
            range=range,
        ).execute()
        return 0

    def setWorksheet(self, spreadsheetId: str, range: str, df: pd.DataFrame):
        self.clearWorksheet(spreadsheetId, range)
        self.googleAPIService.spreadsheets().values().update(
            spreadsheetId=spreadsheetId,
            range=range,
            valueInputOption='USER_ENTERED',
            body={
                'majorDimension': 'ROWS',
                'values': df.T.reset_index().T.values.tolist()
            },
        ).execute()
        return 0

    def appendWorksheet(self, spreadsheetId: str, range: str, df: pd.DataFrame):
        self.googleAPIService.spreadsheets().values().append(
            spreadsheetId=spreadsheetId,
            range=range,
            valueInputOption='USER_ENTERED',
            body={
                'majorDimension': 'ROWS',
                'values': df.values.tolist()
            },
        ).execute()
        return 0
    
    def addWorksheetColumn(self, spreadsheetId: str, range: str, df: pd.DataFrame):
        self.googleAPIService.spreadsheets().values().append(
            spreadsheetId=spreadsheetId,
            range=range,
            valueInputOption='USER_ENTERED',
            body={
                'majorDimension': 'COLUMNS',
                'values': df.values.tolist()
            },
        ).execute()
        return 0

if __name__ == '__main__':
    new_col = 'test'
    myWorksheet = GoogleSheets()
    print(myWorksheet.setWorksheet(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        range='工作表1',
        df=pd.DataFrame(
            {'uid': [1,2,3,4],
            'name': ['Amy','Bella','Candy','Diana'],
            'asset': [800,-400,-1000,600],
            new_col: [0,0,0,0]
            }
        )
    ))

    print(myWorksheet.appendWorksheet(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        range='工作表1',
        df=pd.DataFrame(
            {'uid': [5],
            'name': ['Ella'],
            'asset': [0],
            }
        )
    ))