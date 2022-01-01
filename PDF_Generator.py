from QueryToString import *
from matplotlib.backends.backend_pdf import PdfPages
from QueryComponents import *

dbQuery = QueryResultComponent()
graph = GraphComponent()
queryStr = QueryStringComponent()

def DailySpending():
    with PdfPages('C:\Temp\image.pdf') as pdf:
        results = dbQuery.ParseQueryStringComponents([
            queryStr.DailySpendingOverMonth()
            ])
        graphTypes=['plot']
        graphTitles=["Daily spending"]
        plot, fig = graph.simpleGraph(results, graphTypes, graphTitles)
        pdf.savefig()
        plot.close()

def CompareMonths():
    with PdfPages('C:\Temp\image.pdf') as pdf:
        results = dbQuery.ParseQueryStringComponents([
            queryStr.FirstToNowBudgets(), 
            queryStr.FirstToNowBudgets(False)
            ])
        graphTypes=['bar', 'bar']
        graphTitles=["Current month", "Last month"]
        plot, fig = graph.simpleGraph(results, graphTypes, graphTitles)
        yLimit = max(max(results[0][0]), max(results[1][0]))
        fig[0].set_ylim(0, yLimit)
        fig[1].set_ylim(0, yLimit)
        pdf.savefig()
        plot.close()

def IncomeVsExpense():
    with PdfPages('C:\Temp\image.pdf') as pdf:
        results = dbQuery.SingleRowResults([
            queryStr.IncomeVsExpense(True),
            queryStr.IncomeVsExpense(False)])
        newResults=[]
        for tup in results:
            newResults.append((tup[0], ("Income", "Expense")))
        graphTypes=['bar', 'bar']
        graphTitles=["Current month", "Last month"]
        plot, fig = graph.simpleGraph(newResults, graphTypes, graphTitles)
        pdf.savefig()
        plot.close()