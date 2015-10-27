__author__ = 'Neil'
import datetime
from model import Calendar
from model import CalEvent
#DEFUNCT

#because I don't know where I would put this, controller > process? UPDATE: 10-18-2015, NOW LOCATED IN PROCESS



def execute(theCalendar):

    #Testing calendar here: remove once this is integrated with a process
    # theCalendar = Calendar('NeilUser')

    # start1 = datetime.datetime(2015,11,16,hour = 11, minute = 50)
    # end1 = datetime.datetime(2015,11,16,hour = 12,minute=50)

    # start2 = datetime.datetime(2015,11,16,hour = 13, minute = 50)
    # end2 = datetime.datetime(2015,11,16,hour = 14,minute=50)

    # start3 = datetime.datetime(2015,11,16,hour = 16, minute = 50)
    # end3 = datetime.datetime(2015,11,16,hour = 20,minute=50)


    # theCalendar.cal.append(CalEvent(start1, end1,invitees=['Neil', 'Mark']))
    # theCalendar.cal.append(CalEvent(start2, end2,invitees=['Neil', 'Mark']))
    # theCalendar.cal.append(CalEvent(start3, end3,invitees=['Neil', 'Mark']))


    prompt1 = '1. Add an event to your local calendar\n'
    prompt2 = '2. Delete an event from your local calendar\n'

    print (prompt1 + prompt2)
    choice = int(input('What would you like to do?\n'))

    if choice == 1:
        newEvent = addEventParsing()
        # print (newEvent)

    elif choice == 2:
        deleteEventParsing(theCalendar)


    # print(theCalendar.cal)


def addEventParsing():
    addWelcome = 'Okay! You\'re going to add an event\n'
    getMonth = 'What month? (mm)\n'
    getDay = 'What Day? (dd)\n'
    getYear = 'What Year? (yyyy)\n'

    getStartTime = 'What is the start time? (24h hhmm)\n'
    getEndTime = 'What is the end time? (24h hhmm)\n'

    getName = 'What is the name of this event?\n'

    getNumParticipants = 'How many participants? (int)\n'


    print (addWelcome)
    month = int(input(getMonth))
    day = int(input(getDay))
    year = int(input(getYear))

    startTime = input(getStartTime)
    endTime = input(getEndTime)

    startDateTime = datetime.datetime(year,month,day, hour = int(startTime[:2]), minute = int(startTime[2:4]))

    endDateTime = datetime.datetime(year,month,day, hour = int(endTime[:2]), minute = int(endTime[2:4]))


    eventName = input(getName)

    numParticipants = int(input(getNumParticipants))

    participants = []
    for i in range(0,numParticipants):
        singlePart = input('Enter participant %i ID.\n'%(i+1))
        participants.append(singlePart)


    print (participants)
    newEvent = model.CalEvent(startDateTime, endDateTime, invitees = participants)
    return newEvent #Return calendar event


def deleteEventParsing(theCalendar):
    deleteWelcome = 'Okay! You\'re going to delete an event\n'

    print('This calendar has the following events in it:\n')

    numEvents = len(theCalendar.cal)

    for i in range(0,numEvents):
        print('%i. '%(i+1) + str(theCalendar.cal[i]))

    choice = int(input('Which event do you want to delete? (number)'))

    theCalendar.cal.pop(choice-1)



if __name__ == "__main__":
    execute()
