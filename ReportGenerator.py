import ServerRequest
import DatabaseExecute
import datetime

class Reports:
    db = DatabaseExecute.DatabaseExecutions()
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

    def __sumByUser(self, days=7):
        report=""
        lastWeekSum=self.db.genericQuery("Select username, budgetCategory, SUM(cost) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by username, budgetCategory order by username")
        report+=self.__genStringReport("Sum by user", lastWeekSum)
        return report

    def __avgByCategory(self, days):
        report=""
        lastWeekSum=self.db.genericQuery("select budgetCategory, cast(avg(cost) as decimal(10,2)) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by budgetCategory")
        report+=self.__genStringReport("Average by category", lastWeekSum)
        return report

    def WeeklyReport(self):
        report=""
        report+=self.__costsByCategory(7)
        report+=self.__sumByUser(7)
        report+=self.__avgByCategory(31)
        return report

    def SendReports(self):
        if datetime.date.today().weekday() == 4:
            server = ServerRequest.Notifications()
            server.sendEmail("Weekly report",self.WeeklyReport())
            return True
        else:
            return False
        