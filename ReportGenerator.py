import ServerRequest
import DatabaseExecute
import datetime

class Reports:
    db = DatabaseExecute.DatabaseExecutions()
    #Generate the report to a consistent format
    def __genStringReport(self, reportName, queryData):
        report="<b>"+reportName+"</b>\n----------------\n"
        for val in queryData:
            if(len(val)==2):
                report+=str(val[0]) + ": $" + str(val[1])+"\n"
            else:
                report+=str(val[0]) + ", " + str(val[1])+ ": $" + str(val[2])+"\n"
        return report+"<br>"

    def __costsByCategory(self, days=7):
        report=""
        lastWeekSum=self.db.genericQuery("Select budgetCategory, cost from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by budgetCategory, cost order by cost desc ")
        report+=self.__genStringReport("All costs by category", lastWeekSum)
        return report

    #Send a sum by user, given the amount of days
    def __sumByUser(self, days=7):
        report=""
        lastWeekSum=self.db.genericQuery("Select username, budgetCategory, SUM(cost) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by username, budgetCategory order by username")
        report+=self.__genStringReport("Sum by user", lastWeekSum)
        return report

    #Send an average by category, given the amount of days
    def __avgByCategory(self, days=7):
        report=""
        lastWeekSum=self.db.genericQuery("select budgetCategory, cast(avg(cost) as decimal(10,2)) from (select budgetCategory, sum(cost) as cost, DATEDIFF(week, GETDATE(), date) as WeekNumber, date from Finance group by budgetCategory, date) as b where date>DATEADD(day, -"+str(days)+", GETDATE())  group by budgetCategory")
        report+=self.__genStringReport("Average by category", lastWeekSum)
        return report

    #Abstracted report of data to send
    def WeeklyReport(self):
        report=""
        report+=self.__costsByCategory(7)
        report+=self.__sumByUser(7)
        report+=self.__avgByCategory(31)
        return report

    def SendReports(self):
        if datetime.date.today().weekday() == 4:
            #Add the constants and tag them as by batch client if method hasn't been run in last 6 days
            if(len(self.db.genericQuery("select * from Finance where date>DATEADD(day, -6, GETDATE()) and budgetCategory='Church'"))==0):
                queryData=self.db.genericQuery("select name, monthlyCost from FinanceConstants")
                for data in queryData:
                    self.db.genericQuery("insert into Finance (username, budgetCategory, cost, date, notes) values (?, ?, ?, ?, ?)", False, ['BatchClient', data[0], float(data[1])/4, datetime.date.today(), 'These are sent from batch client'])
            server = ServerRequest.Notifications()
            server.sendEmail("Weekly report",self.WeeklyReport())
            return True
        else:
            return False
        