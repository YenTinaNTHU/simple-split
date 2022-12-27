from googleAPIs import GoogleAPIClient
import pandas as pd

class GoogleSheets(GoogleAPIClient):
    def __init__(self) -> None:
        # 呼叫 GoogleAPIClient.__init__()，並提供 serviceName, version, scope
        super().__init__(
            'sheets',
            'v4',
            ['https://www.googleapis.com/auth/spreadsheets'],
        )
    def addWorksheet(self, spreadsheetId: str, title:str):
        request_body = {
            'requests':[{
                'addSheet': {
                    'properties':{
                        'title': title,
                        'index': 0,
                        'sheetType': 'GRID',
                        'hidden': False
                    }
                }
            }]
        }
        response = self.googleAPIService.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=request_body
        ).execute()
        return 0
    
    def getSheetId(self, spreadsheetId: str, title: str):
        sheet_metadata = self.googleAPIService.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
        properties = sheet_metadata.get('sheets')
        for item in properties:
            if item.get("properties").get('title') == title:
                return (item.get("properties").get('sheetId'))
        return 1
    
    def deleteWorksheet(self, spreadsheetId: str, title: str):
        sheetId = self.getSheetId(spreadsheetId, title)
        request_body = {
            'requests':[{
                'deleteSheet': {
                    'sheetId': sheetId
                }
            }]
        }
        self.googleAPIService.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=request_body
        ).execute()
        return 0

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

    def deleteWorksheetRow(self, spreadsheetId: str, range: str, startIndex:int, endIndex:int):
        sheetId = self.getSheetId(spreadsheetId, range)
        request_body = {
            'requests':[{
                'deleteDimension':{
                    'range':{
                        'sheetId':sheetId,
                        'dimension':'ROWS',
                        'startIndex': startIndex,
                        'endIndex': endIndex,
                    }
                }
            }]
        }
        self.googleAPIService.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=request_body,
        ).execute()
        return 0

if __name__ == '__main__':
    new_col = 'test'
    myWorksheet = GoogleSheets()

    print(myWorksheet.addWorksheet(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        title='test'
    ))
    
    print(myWorksheet.appendWorksheet(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        range='test',
        df=pd.DataFrame(data={'col1': [1, 2, 3, 4,5], 'col2': [1,2,3,4,5]})
    ))
        
    print(myWorksheet.deleteWorksheetRow(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        range='test',
        startIndex=1,
        endIndex=4
    ))
    
    print(myWorksheet.deleteWorksheet(
        spreadsheetId='1rAse3CL3uO_sfMRh1g9YRg_4POeeLi10SMv3467EeIw',
        title='test'
    ))