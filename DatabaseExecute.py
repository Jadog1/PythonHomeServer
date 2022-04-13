import datetime
import pyodbc 
import os
import ServerRequest
from dotenv import load_dotenv

class DatabaseExecutions():
    server = os.getenv('db_server', "")
    database = os.getenv('db_name', "")
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
    cursor = conn.cursor()
    
    def genericQuery(self, query, isExecution=True, insertValues=[]):
        try:
            if(len(insertValues)==0):
                self.cursor.execute(query) 
            else:
                self.cursor.execute(query, insertValues)
            if(isExecution):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
        except Exception as e:
            self.cursor.execute("Insert into ErrorLog (QueryLog) values (?)", [query])
            self.conn.commit()
            
            notifications=ServerRequest.Notifications()
            notifications.sendEmail("Error!!", e)
            raise Exception('Edward')
            return []

class ServerDatabaseInserts(DatabaseExecutions):
    def parseJsonTableData(self, TableData):
        attrArray=[]
        valueArray =[]
        paramArray=[]
        table=""
        for attr, value in TableData.items():
            if(attr!='_id' and attr!='table'):
                attrArray.append(attr)
                paramArray.append("?")
                valueArray.append(value)
            
            if(attr=='table'):
                table=value
        attrReturn = ",".join(str(x) for x in attrArray)
        paramReturn = ",".join(str(x) for x in paramArray)
        return (table, attrReturn, paramReturn, valueArray)

    def __insertRow(self, TableData):
        parsedData=self.parseJsonTableData(TableData)
        genericInsertStatement="INSERT INTO {} ({}) VALUES ({})"
        genericInsertStatement=genericInsertStatement.format(parsedData[0], parsedData[1], parsedData[2])
        self.cursor.execute(genericInsertStatement, parsedData[3])

    def insertRows(self, ServerRequestInternet):
        try:
            transactions = ServerRequestInternet
            for transaction in transactions:
                self.__insertRow(transaction)
            self.conn.commit()
        except Exception as e:
            notifications=ServerRequest.Notifications()
            notifications.sendEmail("Error!!", str(e))
            raise Exception('Edward')


