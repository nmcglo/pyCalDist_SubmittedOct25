__author__ = 'plaggm'
import datetime
from collections import namedtuple
import unittest
import pickle
import random
import jsonpickle
import json
import numpy as np

from UserRankEnum import UserRank

busyT = namedtuple('busyT', ['start', 'end'])
emp = namedtuple('emp', ['firstName', 'lastName'])


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object


def DateTimeDecoder(timeList):
    timeList = map(lambda i: int(i), timeList)
    return datetime.datetime(*timeList)


class CalEvent(object):
    #BEWARE: Missuse of class variables - all calevent instances will share these values - not sure if reassigning in init will fix that
    # startTS = datetime.datetime.now()
    # endTS = datetime.datetime.now()
    # eventRange = ''
    # uRank = UserRank.unassigned
    # uid = 0

    # participants = []
    # insertTime = ""
    # eventName = "You didn't change the event name you dingbat"

    def __init__(self, eventName = "not a real eventName", startTS=datetime.datetime.now(), endTS=datetime.datetime.now(),
                 uid=-1, uRank=UserRank.unassigned, participants=[],
                 insertTime=datetime.datetime.now()):

        assert isinstance(startTS, datetime.datetime)
        assert isinstance(endTS, datetime.datetime)
        # Slow, but easy to work with checks:
        # assert uRank in self.ranks.keys()
        self.eventName = eventName

        self.uRank = uRank
        self.uid = uid
        # self.uName = emp(firstName=firstName, lastName=lastName)
        self.startTS = startTS
        self.endTS = endTS

        # self.eventRange = busyT(start=self.startTS, end=self.endTS)
        self.participants = participants
        self.insertTime = insertTime

    @property
    def uName(self):
        #return emp(uid = self.uid)
        return self.uid
        # return emp(firstName=self.firstName, lastName=self.lastName)

    @property
    def eventRange(self):
        return busyT(start=self.startTS, end=self.endTS)

    def __str__(self):
        title = 'Title: ' + str(self.eventName) + ', '
        start = 'Start: ' + str(self.startTS) + ', '
        end = 'End: ' + str(self.endTS) + ', '
        priority = 'Priority: ' + str(self.uRank) + ', '
        owner = 'Owner: ' + str(self.uid) + ', '
        parts = 'Participants: ' + str(self.participants) +', '
        insert = 'Insert Time: ' + str(self.insertTime)

        return   title + start + end + priority + owner + parts + insert


    def __eq__(self, other):
        """

        :type other: CalEvent
        """
        assert isinstance(other.uName, object)
        return (isinstance(other, self.__class__)
                and self.uName == other.uName
                and self.uRank == other.uRank
                and self.eventRange == other.eventRange
                and self.participants == other.participants)

    def __contains__(self, item):
        if isinstance(item, emp):
            return self.uName == emp.uid
            # return self.uName.firstName == emp.firstName and self.uName.lastName == emp.lastName

    def __lt__(self, other):
        if not isinstance(other,CalEvent):
            return NotImplemented
        if(self == other):
            return 0
        else:
            return self.startTS < other.startTS

    def compareRank(self, other):
        # assert userRank in self.ranks.keys()
        return self.uRank < other.uRank

    def compareAge(self, other):
        """

        :param other: the other cal entry
        :return: was this entry added before the other entry?(Is this entry newer?)
        """
        return self.insertTime - other.insertTime < datetime.timedelta(seconds=1)

    def calculateOverlap(self, othCal):
        assert isinstance(othCal, CalEvent)
        return self.eventRange.start < othCal.eventRange.end and othCal.eventRange.start < self.eventRange.end

        # mStart = max(self.eventRange.start, othCal.eventRange.start)
        #
        # mEnd = max(self.eventRange.end, othCal.eventRange.end)
        # return (mEnd - mStart)

    def willEventConflict(self, othCal):
        assert isinstance(othCal, CalEvent)
        overlap = self.calculateOverlap(othCal)
        #assert isinstance(overlap, datetime.timedelta)

        collab = False

        # for part in othCal.participants:
        #     collab = collab or int(self.uName) == int(part)

        for participant in self.participants:
            for oPart in othCal.participants:
                collab = collab or int(participant) == int(oPart)


        return (overlap and collab)


    def shouldAcquiesce(self, othCal):
        # compare and contrast the other item. Need more complex system
        assert isinstance(othCal, CalEvent)
        return (self != othCal or
                (self.willEventConflict(othCal)
                 and (self.compareRank(othCal) or othCal.compareAge(self))
                 )
                )

    def tostring(self, **kwargs):
        # return super().__str__(**kwargs)(self):

        output = ""
        for attr, value in self.__dict__.items():
            output = output + " " + str(attr) + ":" + str(value) + " "
        output += "\n"
        return output

    def default(o):
        if type(o) is datetime.date or type(o) is datetime.datetime:
            return o.isoformat()

    def toJSON(self):

        output = ""
        elements = self.__dict__
        elements["startTS"] = self.startTS
        elements["endTS"] = self.endTS
        elements["insertTime"] = self.insertTime
        return json.dumps(elements, cls=DateTimeEncoder, sort_keys=True, indent=2, separators=(',',': '))

    def fromJSON(self, text):
        result = jsonpickle.loads(text)

        result["startTS"] = DateTimeDecoder(result["startTS"])
        result["endTS"] = DateTimeDecoder(result["endTS"])
        result["insertTime"] = DateTimeDecoder(result["insertTime"])
        # bt1 = DateTimeDecoder(result["eventRange"][0])
        # bt2 = DateTimeDecoder(result["eventRange"][1])
        # result["eventRange"] = busyT(start=bt1, end=bt2)
        self.__dict__ = result
        return result


# CalEVT Factory from JSON or maybe strings. Cheats a lot.
def genCalEvt(text):
    cc = CalEvent()
    cc.fromJSON(text)
    return cc


class Calendar(object):
    myUID = 0
    fileName = str(myUID) + "_caldata.csv"

    cal = []
    caltxts = []

    def __init__(self, username=0):
        if (username != ""):
            self.myUID = username
            self.fileName = str(self.myUID) + "_caldata"
            self.hrfn = "hum_" + str(self.myUID) + "_caldata.json"
            self.mrfn = "dat_" + str(self.myUID) + "_caldata.dat"
            self.cal = []
            self.caltxts = []

    def __eq__(self, other):

        itms = True
        for evt in self.cal:
            matchedone = False

            for ote in other.cal:
                matchedone = matchedone or (evt == ote)

            itms = itms and matchedone
        return (isinstance(other, Calendar)
                and self.myUID == other.myUID
                and self.fileName == other.fileName
                and itms
                )

    def __str__(self, **kwargs):
        strout = "Calendar for %s:\n"+ str(self.myUID)
        strout += map(lambda evt: str(evt) + "\n", self.cal)
        return strout


    def saveCal(self):
        # pickled = []
        # for row in self.cal:
        #    pickled.append(jsonpickle.encode(row))
        # file = open(self.fileName, 'w')
        # for row in pickled:
        #    file.write(row)
        # file.close()
        self.cal.sort()
        with open(self.mrfn, 'wb') as f:
            pickle.dump(self.cal, f, pickle.HIGHEST_PROTOCOL)

        with open(self.hrfn, 'w') as f:
            self.caltxts = list(self.cal)
            btext = map(lambda i: i.toJSON(), self.caltxts)
            self.caltxts = list(btext)
            bigDict = dict(self.__dict__)
            del (bigDict["cal"])

            js1 = json.dumps(bigDict, indent=4, sort_keys=True)
            f.writelines(js1)
            # print("JS1 ---------- \n" + js1 + "\n----------------------")
        return js1

    def loadCal(self):
        # file = open(self.fileName, 'r')
        # fdat = file.readlines()
        # print(fdat)
        # self.caltxts = np.loadtxt(self.filename,delimiter=",",dtype=str)
        # file.close()
        # self.cal = []
        # for row in fdat:
        #    self.cal.append(jsonpickle.decode(row))

        with open(self.mrfn, 'rb') as ctf:
            self = pickle.load(ctf)

        jsLoaded = createCal(fileName=self.hrfn)
        assert (self == jsLoaded)
        self = jsLoaded

    def addEntry(self, calevt):
        isOverlap = False
        overlaps = []

        #CONFLICT RESOLUTION
        for event in self.cal:
            if (event.willEventConflict(calevt)):
                isOverlap = True
                overlaps.append(event)

        #         if (event.shouldAcquiesce(calevt)):
        #             acqs.append(event)
        # if (len(acqs) == len(overlaps)) and overlap == True:
        #     print('overlap uh oh OH NO NO NO NO up')
        #     # I know this is slow, but it is easier to understand
        #     for removes in overlaps:
        #         self.cal.remove(removes)
        #     self.cal.append(calevt)

        print('found %i conflicts'%len(overlaps))
        self.cal.append(calevt)
        return isOverlap, overlaps

    def removeEntry(self, calevt):

        x = self.cal.remove(calevt)
        # self.saveCal()
        return x

    def insertEvent(self, calevt):
        if isinstance(calevt,str):
            calevt = genCalEvt(calevt)
        result = self.addEntry(calevt)
        self.saveCal()
        return result

    def deleteEvent(self, calevt):
        if isinstance(calevt,str):
            calevt = genCalEvt(calevt)
        result = self.removeEntry(calevt)
        self.saveCal()
        return result

    def hasEvent(self,evt):
        return (evt in self.cal)

    def toJSON(self):
        self.saveCal()



#########FACTORY FOR FILE/IO #####
# Factory Pattern for init from JSON or File:
# Note: Actual class may not include any factory pattern.

class CalGenerator(object):
    def __init__(self, source="FILE", type="JSON", fileName="", stream="", uuid=""):
        self.source = source
        self.fileName = fileName
        self.stream = stream
        self.type = type
        self.uuid = uuid
        if uuid is not "":
            tmpc = Calendar(uuid)
            if type is "JSON":
                self.fileName = tmpc.hrfn
            else:
                self.fileName = tmpc.mrfn

    def getGen(self):
        if self.type is "JSON":
            return self.initFromJSON

    def initFromJSON(self, jsSrc):
        if self.source is "FILE":
            self.ldd = jsonpickle.loads(jsSrc.read())
        if self.source is "NETWORK":
            self.ldd = jsonpickle.loads(jsSrc)
        self.newCal = Calendar(self.ldd["myUID"])
        evtList = list(map(lambda cvt: genCalEvt(cvt), self.ldd["caltxts"]))
        for evt in evtList:
            self.newCal.addEntry(evt)
        return self.newCal

    def initFromBin(self):
        self.newCal = Calendar("EMPTY")
        self.newCal.fileName = self.fileName
        self.newCal.loadCal()
        return self.newCal

    def initCalFromFile(self):
        if self.type is "JSON":
            with open(self.fileName, 'r') as jsfile:
                self.initFromJSON(jsfile)
        else:
            if self.source is "FILE":
                self.initFromBin()
        return self.newCal


def createCal(source="FILE", type="JSON", fileName="", stream="", uuid=""):
    gen = CalGenerator(source, type, fileName, stream, uuid)
    return gen.initCalFromFile()


class wuLog:
    def _init__(self):
        self.log = []

    def addLogEntry(self, clock, evtType, calvt):
        pass

class wuTT:
    def __init__(self, nps=3, myID=0):
        self.matrix = np.zeros(nps)

class TestCalEvents(unittest.TestCase):
    def wrd(self):

        return datetime.datetime(random.randint(1970, 2014),
                                 random.randint(1, 10),
                                 random.randint(1, 20))

    def setUp(self):

        import itertools

        startDates = []
        endDates = []

        fns = ["bob", "john", "ringo", "Paul", "Conan", "Mike"]
        lns = ["Mario", "Luigi", "Walker", "LaQuarius", "Edmond", "Aadams"]
        rnks = ["pleb", "midLevel", "CEO"]

        self.events = []
        fullNames = [fns, lns]
        self.employeeList = []

        for list in itertools.product(*fullNames):
            self.employeeList.append(list)
        # going to use about 50% overlap events for test:
        startD = 1
        startE = 4
        for _ in range((int(len(self.employeeList) / 2))):
            startDates.append(datetime.datetime(2016, 1, startD,
                                                random.randint(1, 10),
                                                random.randint(1, 5),
                                                random.randint(1, 50)))
            endDates.append(datetime.datetime(2016, 1, startE,
                                              random.randint(1, 10),
                                              random.randint(1, 5),
                                              random.randint(1, 50)))
            startD += 1
            startE += 1
        for _ in range((len(self.employeeList))):
            sd = (self.wrd())
            startDates.append(sd)
            endDates.append(sd + datetime.timedelta(5))

        for i in range(len(self.employeeList)):
            self.events.append(CalEvent(startDates[i], endDates[i], self.employeeList[i][0],
                                        self.employeeList[i][1], random.choice(rnks), "NONE"))
        self.startDates = startDates
        self.endDates = endDates

    def testMatrix(self):
        mat = wuTT(myID = 0)
        x = 0
        for i in mat.matrix:
            for j in mat.matrix:
                assert(j == 0)
                x += 1
        assert(x == (3 * 3))
        #assert(len(mat.matrix) == 0)


    def testCalOverlap(self):
        start1 = datetime.datetime(2015, 1, 1)
        end1 = datetime.datetime(2015, 1, 5)
        start2 = datetime.datetime(2015, 1, 4)
        end2 = datetime.datetime(2015, 1, 6)
        event1 = CalEvent(start1, end1, "Bob", "Smith", "pleb", "NOBODY")
        event2 = CalEvent(start2, end2, "Bob", "Smith", "pleb", "NOBODY")
        self.assertTrue(event1.willEventConflict(event2))
        event2 = CalEvent(start2, end2, "Ed", "Smith", "pleb", [emp(firstName="Bob", lastName="Smith")])
        self.assertTrue(event1.willEventConflict(event2))

    def testEq(self):
        extras = []
        for i in range(0, len(self.events)):
            assert (self.events[i] == self.events[i])

    def testLoadSave(self):
        cald = Calendar("tester")
        cald.cal = self.events
        cald.saveCal()
        events = cald.cal
        cald.loadCal()

        for evt in events:
            matchedone = False
            matchedMore = True
            for ote in cald.cal:
                if (matchedone):
                    matchedMore = evt == ote
                matchedone = matchedone or (evt == ote)
            assert (matchedone)

        # print("Output text test")
        cald.cal[0].tostring()

    def testAddRemove(self):
        calTest = Calendar("addRemoveTester")
        loadTester = Calendar("addRemoveTester")
        loadTester.fileName = calTest.fileName
        for evt in self.events:
            calTest.insertEvent(evt)
            loadTester.loadCal()
            assert (calTest == loadTester)
        size = len(calTest.cal)
        for evt in self.events:
            calTest.removeEntry(evt)
            loadTester.loadCal()
            size -= 1
            assert (calTest == loadTester)
            assert (len(calTest.cal) == size)

    def testEvtJSON(self):
        evt = CalEvent(self.startDates[0], self.endDates[0], "JsonBob", "TesterBob", "pleb", "NONE")
        evt2 = CalEvent(self.startDates[0], self.endDates[0], "JsonBob", "TesterBob", "pleb", "NONE",
                        insertTime=evt.insertTime)
        res = evt.toJSON()
        evt2.fromJSON(res)
        assert (evt == evt2)

    def testCreateFromJSON(self):
        calTest = Calendar("jsonTester")
        loadTester = Calendar("jsonTester")
        for evt in self.events:
            calTest.insertEvent(evt)
            loadTester = createCal(uuid="jsonTester")
            assert (calTest == loadTester)

        print("CC1912")

    def testEqCont(self):

        evt1 = CalEvent(self.startDates[1], self.endDates[1], self.employeeList[0][0], self.employeeList[0][1], "pleb",
                        [emp(firstName="Bob", lastName="faucet")])
        evt2 = CalEvent(self.startDates[1], self.endDates[1], self.employeeList[0][0], self.employeeList[0][1], "pleb",
                        [emp(firstName="Bob", lastName="faucet")])
        assert (evt1 == evt2)

        cal1 = Calendar("t1")
        cal2 = Calendar("t1")
        cal1.cal = self.events
        cal2.cal = self.events
        assert (cal1 == cal2)

    def testToString(self):
        evt1 = CalEvent(self.startDates[1], self.endDates[1], self.employeeList[0][0], self.employeeList[0][1], "pleb",
                        [emp(firstName="Bob", lastName="faucet")])
        print(evt1)
        cal1 = Calendar("Test User")
        print(cal1)
