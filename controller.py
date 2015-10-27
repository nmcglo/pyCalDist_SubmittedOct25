import unittest
from model import Calendar
from promptHelper import addEventParsing
from promptHelper import deleteEventParsing
from cyrusbus import Bus
from EventTypeEnum import EventType
import pickle
import os


import algHelper

__author__ = 'Mark Plagge'

#UserEvent: THESE are what go into the logs. Store a type, the local time of the user that submitted it stored in T_i[i,i], 
#           the event itself and the id of the user 

# CONTROLLLER NEEDS NEW FEATURES


class process(object):

    def __init__(self, uid, uRank, nprocs):
        self.lamportClock = 0
        self.uid = uid
        self.theCalendar = Calendar(uid)
        self.tt = [[0 for j in range(nprocs)]for i in range(nprocs)]
        self.log = []
        self.uRank = uRank
        self.nprocs = nprocs
        # self.pid = pid

    def prompt(self):
        input() #THIS GETS RID OF THE FIRST THING THAT THE USER INPUT TO BRING UP THE PROMPT FROM THREADSERVER
        prompt1 = "1. View your calendar\n"
        prompt2 = "2. Add an event to your local calendar\n"
        prompt3 = "3. Delete an event from your calendar\n"
        prompt0 = "0. Test Event Send\n"
        prompt4 = "4. Print Your TimeTable\n"
        prompt5 = "5. Print your Log\n"

        print(prompt0 + prompt1 + prompt2 + prompt3 + prompt4 + prompt5)
        choice = int(input("What would you like to do?\n"))

        if choice == 1: #Print the events in the calendar
            print('This calendar has the following events in it:')

            numEvents = len(self.theCalendar.cal)

            for i in range(0,numEvents):
                print('\t%i. '%(i) + str(self.theCalendar.cal[i]))
            print('------------\n\nPress Return for Prompt')

        elif choice == 2: #Add event to calendar
            newEvent = addEventParsing(self)
            parts = newEvent.participants
            outboundEvents = []

            algHelper.alginsert(self,newEvent)

            for i in parts:
                if i is not self.uid:
                    algHelper.algsend(self,i) #Notify of the new insert that concerns them

            print('------------\n\nPress Return for Prompt')
            return outboundEvents
        elif choice == 3: #Remove event from calendar
            eventToDelete = deleteEventParsing(self.theCalendar)
            parts = eventToDelete.participants


            algHelper.algdelete(self,eventToDelete)

            #move to algdelete
            # for i in range(0,len(parts)):
            #     if i is not self.uid:
            #         algHelper.algsend(self,parts[i]) #Notify of the new delete that concerns them

            print('------------\n\nPress Return for Prompt')

        elif choice == 0:
            newEvent = addEventParsing(self,True)
            parts = newEvent.participants
            outboundEvents = []

            algHelper.alginsert(self,newEvent)

            for i in parts:
                if i is not self.uid:
                    print('about to algsend')
                    algHelper.algsend(self,i) #Notify of the new insert that concerns them

            print('------------\n\nPress Return for Prompt')
            return outboundEvents

        elif choice == 4:
            print('The current Time Table for YOU is:')
            print(self.tt)

            print('------------\n\nPress Return for Prompt')

        elif choice == 5:
            print('Your local log is:')
            for eR in self.log:
                print(eR)
    # def sendMsg(self, msg):
    #     otherIP = '127.0.0.1'
    #     PORT = 9999
    #
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #
    #     sock.sendto(msg, (otherIP,PORT))

    def recvMsg(self,msg):
        algHelper.algrec(self,msg)

        # #CONFLICT RESOLUTION - WRONG - COMMENTING OUT FOR NOW OCT-23
        # if msg.type == EventType.insert:
        #     #update TT
        #     #insert event into cal from each partial log:
        #     print("Here we are")
        #     did_insert, conflicts, removed = self.theCalendar.insertEvent(msg.event)
        #     if did_insert and len(removed) is not 0:
        #         print("Conflicting entries were removed.")
        #     elif did_insert:
        #         print("inserted event")
        #     else:
        #         print("Did not insert. Conflicts with event ", list(map(lambda conflict:str(conflict),conflicts)))
        #
        # elif msg.type == EventType.delete:
        #     print("Delete event")
        #     self.theCalendar.deleteEvent(msg.event)
        #
        # else:
        #     print("This shouldn't happen, an eventType was left Unassigned")
        return True


    def updateLamportClock(self):
        self.lamportClock += 1
        self.tt[self.uid][self.uid] += 1
        self.saveProc()

    def updateTT(self,msg):
        remID = msg.sourceID
        i = self.uid

        for j in range(0,self.nprocs):
            self.tt[i][j] = max(self.tt[i][j], msg.tt[remID][j])

        self.tt = list(map(lambda x,y:max(x,y),self.tt,msg.tt)) 
        self.saveProc()

    def updateLog(self,msg):
        i = self.uid
        newLogEntry = algHelper.UserEvent(msg.type, self.tt[i][i],msg.event,i)
        self.log.append(newLogEntry)
        self.saveProc()
        
        # self.log.append(msg.type, msg.event)

    def hasrec(self,record,k):
        # print('k=',k,'recuid=',record.uid)
        # print(self.tt)
        
        return self.tt[k][record.uid] >= record.Tiii
      

    def saveProc(self):
        #bin
        with open("controller_state.bin", mode='wb') as file:
            pickle.dump(self,file)
        with open("human_readable_state.txt",mode='w') as file:
            dat = "Lamport Clock:" + str(self.lamportClock) + "\n"
            dat += "--TT--\n" + str(self.tt)
            dat += "\nLog:\n"
            for logEntry in self.log:
                dat += str(logEntry) + "\n"
            file.writelines(dat)
def loadProcFromFile():
    proc = False
    if os.path.isfile('controller_state.bin'):
        with open('controller_state.bin', mode='rb') as file:
            proc = pickle.load(file)
    return proc

    # def eventHandler(self, msg):
    #     self.updateLamportClock()
    #
    #     # if msg.sourceID == self.uid or msg.sourceID == self.uid:
    #     if msg.sourceID == self.uid:
    #         localEvent(msg)
    #     else:
    #         remoteEvent(msg)


class TestController(unittest.TestCase):
     def setUp(self):
         self.process1 = process(1, 2)
         self.process2 = process(2,2)
         pass

     def testJava(self):
         pass


def busTester(self,  text):
    print(str(text))

if __name__ == "__main__":
    bus = Bus()
    bus.subscribe("tester",busTester)
    bus.publish("tester",text="Hi there!")
