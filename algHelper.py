# from controller import UserEvent
from EventTypeEnum import EventType

import asyncio
import json
import jsonpickle
import model

global outQueue
outQueue = asyncio.Queue()

class Message():
    def __init__(self,sourceID,destID,TT,partLog):
        # self.type = typev
        # self.event = event
        # self.lamportClock = clock
        self.destID = destID
        self.sourceID = sourceID
        self.tt = TT
        self.partLog = partLog
    def toJSON(self):
        elements = self.__dict__
        elements['destID'] = self.destID
        elements['sourceID'] = self.sourceID
        elements['tt'] = self.tt
        tojsonPL = []
        for eR in self.partLog:
            # print("DOGE LOGE: " , eR)
            tojsonPL.append(eR.toJSON())
        elements['partLog'] = tojsonPL
        return json.dumps(elements)

def messageFromJSON(JSON):
    partlog = []
    content = jsonpickle.loads(JSON)
    for userevt in content['partLog']:

        partlog.append(UserEventfromJSON(userevt))

    return Message(content['sourceID'],content['destID'],content['tt'],partlog)




class UserEvent(object):
    # eventType = EventType.unassigned #EventType enum, insert, delete, or unassigned
    # Tiii = 0 #Time of T_i[i,i]
    # calevt = [] #CalEvent Type
    # uid = -1 #ID of the user
    def __init__(self, eventType, Tiii, theEvent, uid):
        self.eventType = eventType
        self.Tiii = Tiii
        self.calevt = theEvent
        self.uid = uid
        self.eventName = theEvent.eventName
#
# #   We know that calendar events have unique names, it's good enough to just say "insert <name of event>, T_i[i,i], i" in the log.
# #   Is it possible to allow for this to be used in the human readable log?
    def __str__(self):
         return str(self.eventType.name) + ' ' + self.eventName + ', ' + 'T_i[i,i] = ' + str(self.Tiii) + ', UID = ' + str(self.uid)

    def toJSON(self):
        content = self.__dict__
        content["eventType"] = self.eventType
        content["eventName"] = self.eventName
        content["Tiii"] = self.Tiii
        # print(type(self.calevt))
        if type(self.calevt) is model.CalEvent:
            content['calevt'] = self.calevt.toJSON()
        else:
            content['calevt'] = self.calevt
        content['uid'] = self.uid
        return json.dumps(content)

def UserEventfromJSON( JSON):
    content = jsonpickle.loads(JSON)
    calvt = model.genCalEvt(content['calevt'])

    eventTypeInt = content['eventType']

    eventTypeNew = EventType.unassigned
    if eventTypeInt is 1:
        eventTypeNew = EventType.insert
    elif eventTypeInt is 2:
        eventTypeNew = EventType.delete

    print(calvt)
    event = UserEvent(eventTypeNew,content['Tiii'],calvt,content['uid'])
    return event
    #You didn't return anything here.







def alginsert(proc, newEvent):
    print('reached alginsert')
    proc.updateLamportClock()
    tiii = proc.lamportClock
    logEntry = UserEvent(EventType.insert, tiii, newEvent, proc.uid)

    proc.log.append(logEntry)
    isConflicts, conflictingEvents = proc.theCalendar.insertEvent(newEvent)

    if isConflicts:
        for event in conflictingEvents:
            algdelete(proc,event)

    proc.saveProc()


def algdelete(proc, theEvent):
    print('reached algdelete')
    proc.updateLamportClock()
    tiii = proc.lamportClock
    logEntry = UserEvent(EventType.delete, tiii, theEvent, proc.uid)

    proc.log.append(logEntry)
    proc.theCalendar.deleteEvent(theEvent)
    proc.saveProc()

    parts = theEvent.participants

    for i in parts:
        if i is not proc.uid:
            print('sending delete to ', str(i))
            algsend(proc,i) #Notify of the new delete that concerns them


def algsend(proc, otherID):
    print('reached algsend')
    k = int(otherID)
    Ti = proc.tt
    proc.saveProc()
    NP = []
    for eR in proc.log:
        # print('record in the log yes')
        if not proc.hasrec(eR, k):
            # print(k,'has no record of an event, addint to log')
            NP.append(eR)

    theMessage = Message(proc.uid,otherID,Ti,NP)

    outQueue.put_nowait(theMessage)

        # SEND INTERMESSAGE CONTAINING PARTIAL LOG, TI TO OTHER


def algrec(proc, msg):
    print('reached algrec')
    NPk = msg.partLog
    Tk = msg.tt

    NE = []

    for fR in NPk:

        if (not proc.hasrec(fR, proc.uid)):
            NE.append(fR)

    for eR in NE:
        theEvent = eR.calevt

        if not proc.theCalendar.hasEvent(theEvent):
            # We know the calendar doesnt have the event in it
            # Now we need to know if there is a delete record for this event in the new log
            deleteInRecordNE = False
            for rec in NE:
                if rec.eventType == EventType.delete and rec.calevt == theEvent:
                    deleteInRecordNE = True  # There's a delte record for this event in the new log!
                    break
            if not deleteInRecordNE:
                # alginsert(proc,eR.calevt)
                isConflicts, conflictingEvents = proc.theCalendar.insertEvent(eR.calevt)
                proc.log.append(eR)
                proc.updateLamportClock()
                if isConflicts:
                    for event in conflictingEvents:
                        algdelete(proc,event)


        else:
            if eR.eventType == EventType.delete:
                # algdelete(proc,eR.calevt)
                proc.theCalendar.deleteEvent(eR.calevt)
                proc.log.append(eR)
                proc.updateLamportClock()

    proc.updateTT(msg)
    


    updatedLog = []
    for eR in proc.log + NE:
        doesExistNodeWithoutKnowledge = False
        for j in range(0, proc.nprocs):
            if not (proc.hasrec(eR, j)):
                doesExistNodeWithoutKnowledge = True
                break

        if doesExistNodeWithoutKnowledge:
            updatedLog.append(eR)

    proc.log = updatedLog
    proc.saveProc()# Save hard drive record
