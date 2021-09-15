import ServerRequest
import DatabaseExecute
import ReportGenerator
import os
from dotenv import load_dotenv
load_dotenv()


#Get modules and throw into local object
request=ServerRequest.Requests()
notifications=ServerRequest.Notifications()
dbInserts=DatabaseExecute.ServerDatabaseInserts()
reports = ReportGenerator.Reports()

#Run some error detection to determine if microsoft sql server is up, and if the server is running
errorDetected=""
try:
    dbInserts.genericQuery("SELECT @@version;")
except:
    errorerrorDetected+="Microsoft SQL Server currently down, please fix!\n"
if(request.serverIsRunning()==False):
    errorDetected+="Detected server not running!"

if(errorDetected==""):
    #Run logic for backing up data
    returnedJson=request.getTransactions()
    if(len(returnedJson)!=0):
        try:
            dbInserts.insertRows(returnedJson)
            request.dropTransactions("Data backed up, dropping...")
            print("Completed backing up data")
        except Exception as e:
            print("Error occured while performing backup.\nJson: " + str(returnedJson) + "\nError:" + str(e))
    else:
        print("No transactions were created")

    #Run logic for sending reminders
    notes = dbInserts.genericQuery("select note from Note where date<=Cast(GETDATE() as DATE)")
    if(len(notes) > 0):
        compiledNotes=""
        for note in notes:
            compiledNotes += (str(note[0])+"\n")
        try:
            notifications.sendEmail("Jadon ("+str(len(notes))+")", compiledNotes)
            dbInserts.genericQuery("delete from Note where date<=Cast(GETDATE() as DATE)", False)
            print("Completed sending emails and removing reminders")
        except Exception as e:
            print("Unable to successfully email and/or delete notes, " + str(e))
    else:
        print("No notes to send at this time")

    if (reports.SendReports()):
        print("Report sent!")
    else:
        print("No report sent")

else:
    print(errorDetected)
    notifications.sendEmail("Error", errorDetected, True)
    