from locale import normalize
from typing import Match, Tuple
import matplotlib.pyplot as plt
import DatabaseExecute1 as db #My custom module with a class for querying on company database
from QueryToString import *
from matplotlib.backends.backend_pdf import PdfPages

def getN_OfList(n, type='number'):
    if(n == 0 or type=='number'):
        return lambda value: [item[n] for item in value]
    else:
        if(type=='string'):
            return lambda value: [item[n][0:5] for item in value]
        elif (type=='WeekNo'):
            return lambda value: [WeekNumberTo_MMDD(item[n]) for item in value]
        elif (type=='MonthNo'):
            return lambda value: [MonthNumberTo_MM(item[n]) for item in value]
        
def basicArray_NLists(n, type='number'):
    listLambda = []
    for i in range(n):
        listLambda.append(getN_OfList(i-1, type))
    return listLambda

class QueryStringComponent():
    date_firstOfLastMonth=str(todaysDate.replace(day=1, month=todaysDate.month-1))
    date_MonthAgo=str(todaysDate.replace(month=todaysDate.month-1))
    date_firstOfCurrentMonth=str(todaysDate.replace(day=1))

    def FirstToNowBudgets(self, currentDate=True):
        query='''
        select sum(Total) as total, BudgetCategory 
        from FinanceExpense
        where CreatedAt between \'XXFirstDate\' and \'XXSecondDate\' 
        group by BudgetCategory 
        order by sum(Total) desc;
        '''
        if(currentDate):
            query=query.replace("XXFirstDate", self.date_firstOfCurrentMonth)
            query=query.replace("XXSecondDate", str(todaysDate))
        else:
            query=query.replace("XXFirstDate", self.date_firstOfLastMonth)
            query=query.replace("XXSecondDate", self.date_MonthAgo)

        return (query, basicArray_NLists(2, 'string'))

    def FirstToNowSubBudgets(self, currentDate=True):
        query='''
        select sum(Total) as total, case when SubBudgetCategory!='' then SubBudgetCategory else BudgetCategory end 
        from FinanceExpense
        where CreatedAt between \'XXFirstDate\' and \'XXSecondDate\'
        group by SubBudgetCategory, BudgetCategory
        order by sum(Total) desc;
        '''
        if(currentDate):
            query=query.replace("XXFirstDate", self.date_firstOfCurrentMonth)
            query=query.replace("XXSecondDate", str(todaysDate))
        else:
            query=query.replace("XXFirstDate", self.date_firstOfLastMonth)
            query=query.replace("XXSecondDate", self.date_MonthAgo)
        return (query, basicArray_NLists(2, 'string'))

    def CostsOverYear(self, partAtWeek=True):
        query='''
        select sum(Total) as total, DATEPART(WEEK, CreatedAt) as week
        from FinanceExpense where CreatedAt >= \''''+str(beginningOfYear)+'''\'
        group by DATEPART(WEEK, CreatedAt)
        order by DATEPART(WEEK, CreatedAt)
        '''
        if(partAtWeek==False):
            query.replace("DATEPART(WEEK, date)", "DATEPART(MONTH, date)")
        return (query, basicArray_NLists(2, ('WeekNo' if partAtWeek else 'Monthno')))

    def AverageMonthlyCost(self):
        query='''
        select AVG(Total)
        from (
        select sum(Total) as Total from FinanceExpense group by DATEPART(MONTH, CreatedAt)
        ) sumMonthlyCost
        '''
        return (query, basicArray_NLists(1))
        
    def QueryByCategory(self, categories, budgetType='BudgetCategory', partAtWeek=True):
        query='''
        select sum(Total), DATEPART(WEEK, CreatedAt)
        from FinanceExpense where CreatedAt >= \''''+str(beginningOfYear)+'''\' and XXTYPE XXBUDGET
        group by DATEPART(WEEK, CreatedAt)
        order by DATEPART(WEEK, CreatedAt)
        '''
        query.replace("XXTYPE", budgetType)
        if(type(categories)==list):
            query=query.replace("XXBUDGET", '=\''+categories+'\'')
        else:
            categories = [('\''+category+'\'') for category in categories]
            query=query.replace("XXBUDGET", 'IN ('+categories.join(",")+')')

        if(partAtWeek==False):
            query=query.replace("DATEPART(WEEK, CreatedAt)", "DATEPART(MONTH, CreatedAt)")
        return (query, basicArray_NLists(2, ('WeekNo' if partAtWeek else 'Monthno')))

    def DailySpendingOverMonth(self):
        query='''
        select sum(Total), Day(CreatedAt) as created_day
        from FinanceExpense where CreatedAt >=\''''+str(self.date_firstOfCurrentMonth)+'''\'
        group by Day(CreatedAt)
        order by Day(CreatedAt) desc
        '''

        return (query, basicArray_NLists(2))
    

class GraphComponent():
    def simpleGraph(self, QueryResults, type=[], titles=[], ):
        i=0
        if(len(type)!=len(QueryResults)):
            type = ["plot" for i in range(len(QueryResults))]
        if(len(titles)!=len(QueryResults)):
            titles = ["" for i in range(len(QueryResults))]
        fig1, f1_axes = plt.subplots(ncols=1, nrows=len(QueryResults), figsize=(12, 7), constrained_layout=True)
        for graph in QueryResults:
            currentAxis = (f1_axes if len(QueryResults)==1 else f1_axes[i])
            if(type[i]=='pie'):
                percentSum = [item/sum(graph[0]) for item in graph[0]]
                currentAxis.pie(percentSum, labels=graph[1], autopct='%1.1f%%', normalize=True)
            elif(type[i]=='bar'):
                barResult=currentAxis.bar(graph[1], graph[0])
                currentAxis.bar_label(barResult, padding=3)
            else:
                if(len(graph)==2):
                    currentAxis.plot(graph[1], graph[0])
                else:
                    currentAxis.plot(graph[0])
            currentAxis.set_title(titles[i])

            i+=1
        return plt, f1_axes


class QueryResultComponent():
    microsoftSQL=db.DatabaseExecutions()

    def ParseQueryStringComponents(self, components):
        if(type(components)!=list):
            components = [components]
        self.microsoftSQL.startConnection()
        results = []
        for component in components:
            tupleResult = tuple()
            queryResult = self.microsoftSQL.manualQuery(component[0])
            for dataPoints in component[1]:
                returnedList = dataPoints(queryResult)
                if(len(returnedList)>1):
                    tupleResult = ((tuple(returnedList)), ) + tupleResult
                else:
                    tupleResult = tuple(returnedList)
            results.append(tupleResult)

        self.microsoftSQL.closeConnection()
        return results

