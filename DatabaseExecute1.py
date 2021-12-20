import datetime
import pyodbc 
import os
from dotenv import load_dotenv

class DatabaseExecutions():
    server = os.getenv('db_server', "")
    database = os.getenv('db_name', "")
    conn = None
    cursor = None
    
    def startConnection(self):
        self.conn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';Trusted_Connection=yes;')
        self.cursor=self.conn.cursor()

    def genericQuery(self, query, insertValues=[], isExecution=True):
        self.startConnection()
        result = self.manualQuery(query,insertValues, isExecution)
        self.closeConnection()

        return result

    def manualQuery(self, query, insertValues=[], isExecution=True):
        try:
            if(len(insertValues)==0):
                self.cursor.execute(query) 
            else:
                self.cursor.execute(query, insertValues)
            if(isExecution):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
        except BaseException as err:
            self.cursor.execute("Insert into ErrorLog (QueryLog) values (?) ", query)
            self.conn.commit()
            print("Error on query. Logged: ", query)
            return []
    
    def closeConnection(self):
        self.conn.close()
        #self.cursor.close()

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


