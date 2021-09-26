import datetime
import pyodbc 
import os
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
        except:
            self.cursor.execute("Insert into ErrorLog (QueryLog) values ("+query+"), " + str(insertValues))
            self.conn.commit()
            print("Error on query. Logged: ", query)
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
        self.genericQuery(genericInsertStatement, False, parsedData[3])

    def insertRows(self, ServerRequest):
        transactions = ServerRequest
        for transaction in transactions:
            self.__insertRow(transaction)


