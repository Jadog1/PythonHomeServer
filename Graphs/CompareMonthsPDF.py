
import matplotlib.pyplot as plt
import DatabaseExecute as db #My custom module with a class for querying on company database
from QueryToString import *
from matplotlib.backends.backend_pdf import PdfPages

#Initiate defaults
microsoftSQL=db.DatabaseExecutions()
currentMonth='''
select sum(cost) as total, budgetCategory 
from Finance
where date between \''''+str(todaysDate.replace(day=1))+'''\' and \''''+str(todaysDate)+'''\' 
group by budgetCategory 
order by sum(cost) desc;
'''
previousMonth='''
select sum(cost) as total, budgetCategory 
from Finance
where date between \' '''+str(todaysDate.replace(day=1, month=todaysDate.month-1))+'''\' and \''''+str(todaysDate.replace(month=todaysDate.month-1))+'''\' 
group by budgetCategory 
order by sum(cost) desc;
'''
subBudgetCurrentMonth='''
select sum(cost) as total, case when subBudgetCategory!='' then subBudgetCategory else budgetCategory end 
from Finance
where date between \''''+str(todaysDate.replace(day=1))+'''\' and \''''+str(todaysDate)+'''\' 
group by subBudgetCategory, budgetCategory
order by sum(cost) desc;
'''
subBudgetLastMonth='''
select sum(cost) as total, case when subBudgetCategory!='' then subBudgetCategory else budgetCategory end 
from Finance
where date between \''''+str(todaysDate.replace(day=1, month=todaysDate.month-1))+'''\' and \''''+str(todaysDate.replace(month=todaysDate.month-1))+'''\' 
group by subBudgetCategory, budgetCategory
order by sum(cost) desc;
'''
microsoftSQL.startConnection()
thisMonthResults=microsoftSQL.manualQuery(currentMonth)
lastMonthResults=microsoftSQL.manualQuery(previousMonth)
subBudgetResults=microsoftSQL.manualQuery(subBudgetCurrentMonth)
subBudgetLastMonthResults=microsoftSQL.manualQuery(subBudgetLastMonth)
microsoftSQL.closeConnection()

sum1=[item[0] for item in thisMonthResults]
labels1=[item[1][0:5] for item in thisMonthResults]
sum2=[item[0] for item in lastMonthResults]
labels2=[item[1][0:5] for item in lastMonthResults]
sum3=[item[0] for item in subBudgetResults]
labels3=[item[1][0:5] for item in subBudgetResults]
sum4=[item[0] for item in subBudgetLastMonthResults]
labels4=[item[1][0:5] for item in subBudgetLastMonthResults]


maxBudgetSpending=max(max(sum1), max(sum2))
maxSubBudgetSpending=max(max(sum3), max(sum4))
percentSum3 = [item/sum(sum3) for item in sum3]
percentSum4 = [item/sum(sum4) for item in sum4]

with PdfPages('C:\Temp\multipage_pdf.pdf') as pdf:
    fig1, f1_axes = plt.subplots(ncols=2, nrows=2, figsize=(14, 7), constrained_layout=True)
    #Plot the coordinates
    f1_axes[0, 0].bar(labels1, sum1)
    f1_axes[0, 1].bar(labels2, sum2)
    f1_axes[1, 0].pie(percentSum3, labels=labels3, autopct='%1.1f%%')
    f1_axes[1, 1].pie(percentSum4, labels=labels4, autopct='%1.1f%%')
    #Set the titles
    f1_axes[0, 0].set_title('Budget this month')
    f1_axes[0, 1].set_title('Budget last month')
    f1_axes[1, 0].set_title('Sub budgets this month')
    f1_axes[1, 1].set_title('Sub budgets last month')
    #Set custom text
    f1_axes[0, 0].set_ylim(0, maxBudgetSpending)
    f1_axes[0, 1].set_ylim(0, maxBudgetSpending)
    #f1_axes[1, 0].set_ylim(0, maxSubBudgetSpending)
    #f1_axes[1, 1].set_ylim(0, maxSubBudgetSpending)
    f1_axes[0, 0].text(0, float(maxBudgetSpending)/1.25, str(sum(sum1)))
    f1_axes[0, 1].text(1, float(maxBudgetSpending)/1.25, str(sum(sum2)))
    
    pdf.savefig()
    plt.close()