# importing the required module
import matplotlib.pyplot as plt
import DatabaseExecute as db #My custom module with a class for querying on company database
from QueryToString import *

#Initiate defaults
microsoftSQL=db.DatabaseExecutions()
#Setup query and main logic
query='''
select sum(cost) as total, DATEPART(WEEK, date) as week
from Finance where date >= \''''+str(beginningOfYear)+'''\'
group by DATEPART(WEEK, date)
order by DATEPART(WEEK, date)
'''
firstDayOfMonth=todaysDate.replace(day=1)
query2='''
select sum(cost), Day(date) as created_day
from Finance where date >=\''''+str(firstDayOfMonth)+'''\'
group by Day(date)
order by Day(date) desc
'''
query3='''
select sum(cost), DATEPART(WEEK, date)
from Finance where date >= \''''+str(beginningOfYear)+'''\' and budgetCategory='Bills'
group by DATEPART(WEEK, date)
order by DATEPART(WEEK, date)
'''
queryAvgMonthlyCost='''
select AVG(cost)
from (
select sum(cost) as cost from Finance group by DATEPART(MONTH, date)
) sumMonthlyCost
'''
queryYearMonthlyView=query.replace("DATEPART(WEEK, date)", "DATEPART(MONTH, date)")

#Query and get results
microsoftSQL.startConnection()
results = microsoftSQL.manualQuery(query)
results_monthView=microsoftSQL.manualQuery(query2)
results_onlyBills = microsoftSQL.manualQuery(query3)
results_AvgMonthlyCost = microsoftSQL.manualQuery(queryAvgMonthlyCost)
results_AllMonthsView = microsoftSQL.manualQuery(queryYearMonthlyView)
microsoftSQL.closeConnection()

#set up all x,y coords
y=[WeekNumberTo_MMDD(item[0]) for item in results]
x=[item[1] for item in results]
yBills=[WeekNumberTo_MMDD(item[0]) for item in results_onlyBills]
xBills=[item[1] for item in results_onlyBills]
yMonth=[item[0] for item in results_monthView]
xMonth=[item[1] for item in results_monthView]
yYearMonth=[MonthNumberTo_MM(item[0]) for item in results_AllMonthsView]
xYearMonth=[item[1] for item in results_AllMonthsView]

#Setup custom variables to display custom data
maxHeight=max(yYearMonth)
maxHeightMonth=max(yMonth)
sumYearlyReview=getCurrency(sum(y))
sumMonthlyReview=sum(yMonth)
percentageOfAverageMonthUsed=int((sumMonthlyReview/results_AvgMonthlyCost[0][0])*100)
sumMonthlyReview=getCurrency(sumMonthlyReview)+" ("+str(percentageOfAverageMonthUsed)+"%)"

#Make the grid and subplots
fig1, f1_axes = plt.subplots(ncols=1, nrows=3, figsize=(12, 7), constrained_layout=True)
#Plot the coordinates
f1_axes[0].plot(xYearMonth, yYearMonth)
f1_axes[1].plot(x, y, 'b-', xBills, yBills, 'ro')
f1_axes[2].plot(xMonth, yMonth)
#Set the titles
f1_axes[0].set_title('Year view (monthly)')
f1_axes[1].set_title('Year view (weekly)')
f1_axes[2].set_title('This month')
#Set custom text
f1_axes[0].text(0, float(maxHeight)/1.25, str(sumYearlyReview))
f1_axes[2].text(1, float(maxHeightMonth)/1.25, str(sumMonthlyReview))
#Set all labels
for axes in f1_axes:
    axes.set_xlabel("Time period")
    axes.set_ylabel("Money spent")
plt.show()