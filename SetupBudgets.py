
class Reports:
    db = DatabaseExecute.DatabaseExecutions()
    #Add the constants and tag them as by batch client if method hasn't been run in last 6 days
    def assignBudgets(self):
        if(len(self.db.genericQuery("select * from Finance where date>DATEADD(day, -6, GETDATE()) and budgetCategory='Church'"))==0):
            queryData=self.db.genericQuery("select name, monthlyCost from FinanceConstants")
            for data in queryData:
                self.db.genericQuery("insert into Finance (username, budgetCategory, cost, date, notes) values (?, ?, ?, ?, ?)", False, ['BatchClient', data[0], float(data[1])/4, datetime.date.today(), 'These are sent from batch client'])
