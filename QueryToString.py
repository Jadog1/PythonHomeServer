import datetime
import locale


todaysDate=datetime.date.today()
currentYear=todaysDate.year
beginningOfYear=datetime.date(currentYear, 1, 1)
locale.setlocale( locale.LC_ALL, '' )
def WeekNumberTo_MMDD(weekNo):
    return datetime.datetime.strptime(str(todaysDate.year)+'-W'+str(weekNo) + '-1', "%Y-W%W-%w").date().strftime('%m-%d')

def MonthNumberTo_MM(monthNo):
    return todaysDate.replace(month=monthNo).strftime('%b')

def getCurrency(value):
    return locale.currency(value, grouping=True)