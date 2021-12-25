import ServerRequest
import DatabaseExecute
import datetime
from PDF_Generator import *

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
        lastWeekSum=self.db.genericQuery("select sum(Total) from FinanceExpense where CreatedAt>DATEADD(day, -"+str(days)+", GETDATE())")
        return self.__genStringReport("Total cost", lastWeekSum)

    def __costsByCategory(self, days=7):
        lastWeekSum=self.db.genericQuery("Select BudgetCategory, Total from FinanceExpense where CreatedAt>DATEADD(day, -"+str(days)+", GETDATE()) group by BudgetCategory, Total order by Total desc ")
        return self.__genStringReport("All costs by category", lastWeekSum)

    #Send a sum by user, given the amount of days
    def __sumByUser(self, days=7):
        lastWeekSum=self.db.genericQuery("Select BuyerCategory, BudgetCategory, SUM(cost) from FinanceExpense where CreatedAt>DATEADD(day, -"+str(days)+", GETDATE()) group by BuyerCategory, BudgetCategory order by BuyerCategory")
        return self.__genStringReport("Sum by user", lastWeekSum)

    #Send an average by category, given the amount of days. This is safe method as it can handle averages of dates prior to historical data
    def __avgByCategory_SAFE(self, days=7):
        lastWeekSum=self.db.genericQuery("select BudgetCategory, cast(avg(cost) as decimal(10,2)) from (select BudgetCategory, sum(Total) as cost, DATEDIFF(week, GETDATE(), CreatedAt) as WeekNumber, CreatedAt from FinanceExpense group by BudgetCategory, CreatedAt) as b where CreatedAt>DATEADD(day, -"+str(days)+", GETDATE())  group by BudgetCategory")
        return self.__genStringReport("Average by category", lastWeekSum)

    def __avgByCategory(self, days=31):
        lastWeekSum=self.db.genericQuery("select BudgetCategory, cast(sum(Total)/("+str(days)+"/7) as decimal(10,2)) from FinanceExpense where CreatedAt>DATEADD(day, -"+str(days)+", GETDATE()) group by BudgetCategory")
        return self.__genStringReport("Average by category for month (Weekly view)", lastWeekSum)

    #Get all recorded dates which probably need to send a notification
    def __FinanceUpdates(self):
        ExpensesPastDueReport = "<b>Finance updates!</b>\n----------------\n"
        ExpensesPastUpdate = self.db.genericQuery('''
        select DATEDIFF(day, CreatedAt, CONVERT(DATE, GETDATE())) as daysSincePaid, matched.BudgetCategory, matched.SubBudgetCategory, ReliantOnBudgetCategory, ReliantOnSubBudgetCategory
        from FinanceUpdate fu
        Cross apply
                (select Top 1 CreatedAt, FrequencyOfDays, BudgetCategory, SubBudgetCategory
                from FinanceExpense fe
	            where fu.BudgetCategory=fe.BudgetCategory and fu.SubBudgetCategory=fe.SubBudgetCategory
	            order by CreatedAt desc
	            ) matched
        where DATEDIFF(day, CreatedAt, CONVERT(DATE, GETDATE()))>matched.FrequencyOfDays;
	  ''')
        for expense in ExpensesPastUpdate:
            if(expense[3]!=''):
                query='''
                select Sum(Total) from FinanceExpense fe 
                join FinanceUpdate fu on fe.BudgetCategory = fe.BudgetCategory and fu.SubBudgetCategory=fe.SubBudgetCategory
                where fe.BudgetCategory='XXBUDG' and fe.SubBudgetCategory='XXSUBBUDG' and 
                      fu.BudgetCategory='XXBUDG' and fu.SubBudgetCategory='XXSUBBUDG' and fe.CreatedAt>DateAdd(day, -1*fu.FrequencyOfDays, GETDATE())
                '''
                query.replace('XXBUDG', expense[3])
                query.replace('XXSUBBUDG', expense[4])
                ReliantCategoryTotals=self.db.genericQuery(query)[0][0]
                ExpensesPastDueReport=ExpensesPastDueReport+"Total remaining: $"+str(ReliantCategoryTotals)
            ExpensesPastDueReport=ExpensesPastDueReport+""


    def __donationTotals(self, daysSinceLastChurchDonation):
        lastWeekSum=self.db.genericQuery("select sum(Total) from FinanceExpense where CreatedAt>DATEADD(day, -"+str(daysSinceLastChurchDonation)+", GETDATE()) and BudgetCategory='Donation'")
        return self.__genStringReport("Sum of donations for month", lastWeekSum)

    def __donationReminder(self, daysSinceLastChurchDonation):
        lastWeekSum=self.db.genericQuery("select 850-sum(Total) from FinanceExpense where CreatedAt>DATEADD(day, -"+str(daysSinceLastChurchDonation)+", GETDATE()) and BudgetCategory='Donation'")
        return self.__genStringReport("Remainder owed", lastWeekSum)

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
        daysSinceLastChurchDonation=int(self.db.genericQuery("select DATEDIFF(day, lastDay.CreatedAt, CONVERT(DATE, GETDATE())) from (select TOP 1 CreatedAt from FinanceExpense where BudgetCategory='Church' order by CreatedAt desc) lastDay;")[0][0])
        if(daysSinceLastChurchDonation>30):
            server.sendEmail("Submit donation!", "It has been <b>"+str(daysSinceLastChurchDonation)+"</b> days since last donation\n"+self.__donationReminder(daysSinceLastChurchDonation))
        
        if self.dayOfWeek == 1:
            DailySpending()
            server.PDF_to_JPG("image.pdf")
            server.sendEmailAttachment("Daily spending report", "Daily report")
            server.clearTempStorage()
        elif self.dayOfWeek == 2:
            CompareMonths()
            server.PDF_to_JPG("image.pdf")
            server.sendEmailAttachment("Monthly compare", "Monthly report")
            server.clearTempStorage()
        elif self.dayOfWeek == 4:
            server.sendEmail("Weekly report",self.WeeklyReport())
        elif self.dayOfWeek == 5:
            server.sendEmail("Monthly report",self.MonthlyReport())
        elif self.dayOfWeek == 6:
            server.sendEmail("Donation report",self.DonationReport(daysSinceLastChurchDonation))
        else:
            reportSent=False
        return reportSent
        