import ServerRequest
import DatabaseExecute
import datetime

class Reports:
    db = DatabaseExecute.DatabaseExecutions()
    dayOfWeek=datetime.date.today().weekday()
    #Generate the report to a consistent format
    def __genStringReport(self, reportName, queryData):
        report="<b>"+reportName+"</b>\n----------------\n"
        for val in queryData:
            if(len(val)==2):
                report+=str(val[0]) + ": $" + str(val[1])+"\n"
            elif(len(val)==1):
                report+="$"+str(val[0])
            else:
                report+=str(val[0]) + ", " + str(val[1])+ ": $" + str(val[2])+"\n"
        return report+"<br>"

    def __totalSumOfCosts(self, days=7):
        lastWeekSum=self.db.genericQuery("select sum(cost) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) and username!='BatchClient'")
        return self.__genStringReport("Total cost", lastWeekSum)

    def __costsByCategory(self, days=7):
        lastWeekSum=self.db.genericQuery("Select budgetCategory, cost from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by budgetCategory, cost order by cost desc ")
        return self.__genStringReport("All costs by category", lastWeekSum)

    #Send a sum by user, given the amount of days
    def __sumByUser(self, days=7):
        lastWeekSum=self.db.genericQuery("Select username, budgetCategory, SUM(cost) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by username, budgetCategory order by username")
        return self.__genStringReport("Sum by user", lastWeekSum)

    #Send an average by category, given the amount of days. This is safe method as it can handle averages of dates prior to historical data
    def __avgByCategory_SAFE(self, days=7):
        lastWeekSum=self.db.genericQuery("select budgetCategory, cast(avg(cost) as decimal(10,2)) from (select budgetCategory, sum(cost) as cost, DATEDIFF(week, GETDATE(), date) as WeekNumber, date from Finance group by budgetCategory, date) as b where date>DATEADD(day, -"+str(days)+", GETDATE())  group by budgetCategory")
        return self.__genStringReport("Average by category", lastWeekSum)

    def __avgByCategory(self, days=31):
        lastWeekSum=self.db.genericQuery("select budgetCategory, cast(sum(cost)/("+str(days)+"/7) as decimal(10,2)) from Finance where date>DATEADD(day, -"+str(days)+", GETDATE()) group by budgetCategory")
        return self.__genStringReport("Average by category for month (Weekly view)", lastWeekSum)

    def __donationTotals(self, daysSinceLastChurchDonation):
        lastWeekSum=self.db.genericQuery("select sum(cost) from Finance where date>DATEADD(day, -"+str(daysSinceLastChurchDonation)+", GETDATE()) and budgetCategory='Donation'")
        return self.__genStringReport("Sum of donations for month", lastWeekSum)

    #Abstracted report of data to send
    def WeeklyReport(self):
        report=""
        report+=self.__totalSumOfCosts(self.dayOfWeek)
        report+=self.__costsByCategory(self.dayOfWeek)
        return report

    def MonthlyReport(self):
        report=""
        report+=self.__totalSumOfCosts(31)
        report+=self.__sumByUser(31)
        report+=self.__avgByCategory(31)
        return report

    def DonationReport(self, daysSinceLastChurchDonation):
        return self.__donationTotals(daysSinceLastChurchDonation)

    def SendReports(self):
        reportSent=True
        server = ServerRequest.Notifications()
        daysSinceLastChurchDonation=int(self.db.genericQuery("select DATEDIFF(day, lastDay.date, CONVERT(DATE, GETDATE())) from (select TOP 1 date from Finance where budgetCategory='Church' and username!='BatchClient' order by date desc) lastDay;")[0][0])
        if(daysSinceLastChurchDonation>30):
            server.sendEmail("Submit donation!", "It has been <b>"+str(daysSinceLastChurchDonation)+"</b> since last donation")
        
        if self.dayOfWeek == 4:
            server.sendEmail("Weekly report",self.WeeklyReport())
        elif self.dayOfWeek == 5:
            server.sendEmail("Monthly report",self.MonthlyReport())
        elif self.dayOfWeek == 6:
            server.sendEmail("Donation report",self.DonationReport(daysSinceLastChurchDonation))
        else:
            reportSent=False
        return reportSent
        