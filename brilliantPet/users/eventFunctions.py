from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback
from django.utils import timezone
from datetime import datetime, timedelta 
from django.db.models import  F


mainFlagDictionary={"pee":2,"poop":3,"dog":5,"error":7,"healthissue":11}
eventList =["LOOKIN","PAD_ADVANCE","DEVICE_ERROR","ANIMAL_DETECTION"]



gm = generalClass()

def getEvent(data):
    data = gm.cleanData(data)
    try:
       
        if "eventid" in data and data["eventid"] not in ["", None]:
            event = events.objects.filter(eventid=data["eventid"])
            return event[0]
        else:
            return None
    except:
        traceback.print_exc()
        gm.errorLog(traceback.format_exc())
        return None

"""
this function gets you the event for a given timestamp and size
"""

def getEventByTimestampAndSize(data):
    data = gm.cleanData(data)
    ihour=-10

    try:
        if "machine_id" in data and data["machine_id"] not in ["", None]:
            if "timestamp" in data and data["timestamp"] not in ["", None]:
                if "imagesize" in data and data["imagesize"] not in ["", None]:
                    event = events.objects.filter(
                                type=data["type"],
                                machine_id=data["machine_id"],
                                date__gt=(timezone.now()+timedelta(hours=ihour)),
                                value__contains="\"ts\": "+str(data["timestamp"]).strip()
                            )
                    return event[0]
        return None
    except:
        traceback.print_exc()
        gm.errorLog(traceback.format_exc())
        return None

def updateEvent(data,eventid):
        data = gm.cleanData(data)
        try:
            isflageged= None if "isflagged" not in data else data["isflagged"]
            note = None if "note" not in data else data["note"]
            tags= None if "tags" not in data else data["tags"]

            
            updat=""
            dictio={}
            event = events.objects.get(eventid=eventid)

            if isflageged:
                event.isflagged = isflageged

            if note:                   
                event.note = note

            if tags:
                mainlist=["poop","pee","dog","error","healthissue"]
                tagslist=tags.strip(",").split(",")
                tagslist=set(tagslist)
                le = len([x for x in tagslist if x.lower().strip() not in mainlist])
                # toBeAdded = []
                # discarded = []
                # for x in tagslist:
                #     x = x.strip().lower()
                #     if x in mainlist:
                #         toBeAdded.append(x)
                #     else:
                #         discarded.append(x)


                if le == 0:
                    event.tags = ",".join(set(tagslist))
                else:
                    print("invalid tag")
                    return None

    
                event.save()

            return event
            
        except Exception as e:
            traceback.print_exc()
            print("exception here")
            print(e)
            return None


def fileterEventsByMachines(userid,startDate,endDate,machinelist,typelist,flagslist):
    
    flagv= -1    
    myuserid=userid
    print(userid)
    print(startDate)
    print(endDate)
    print(machinelist)
    print(typelist)
    print(flagslist)

    try:
        if typelist is None or len(typelist)  <1:
            typelist=eventList

        if flagslist is not None and len(flagslist)  >= 1:
            flagv=1    
            for flagvalue in flagslist:
                if len(flagvalue.strip()) > 0:
                    flagv=flagv * mainFlagDictionary.get(flagvalue)

        """
        if the machines are not sent then the all the machines under the user would be selected
        """
        if machinelist is None or len(machinelist) < 1:
            userMachines = MachineDetails.objects.filter(userid = myuserid, isremoved = 0)
            machinelist=[]

            for m in userMachines:
                machinelist.append(m.machine_id)

        print("quering for "+userid+ " for types  "+str(typelist) + "for machines "+str(machinelist) )

        if flagv > 0:
            print("the value of flag is "+str(flagv))
            event = events.objects.all().annotate(
                    delta=F('tag_value')%flagv).filter(userid = userid,
                    type__in=typelist,
                    machine_id__in=machinelist,
                    delta=0,
                    date__range = (startDate, endDate)).order_by("-date")
               
        else: 
            print("the value of flag is "+str(flagv))
            event = events.objects.filter(userid = userid,
                        type__in=typelist,
                        date__range = (startDate, endDate),
                        machine_id__in=machinelist).order_by("-date")
        return event
        
    except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return None


def validateEventTypeFalgLists(machinelist,typelist,flagslist):
    
    print(machinelist)

    try:
        
        if len(machinelist) < 1 or len(typelist) < 1 or len(flagslist) < 1:
            print("error in the length of params")
            return False


        typelen=len([ty for ty in typelist if ty not in eventList ])
        if typelen > 0:
            print("error in typelen")
            return False

        flaglen=len([fl for fl in flagslist if  mainFlagDictionary.get(fl) == None  ])
        if flaglen > 0:
            print("error in flag")
            return False
        
        machilen=len( [mch for mch in machinelist if mch== None or mch.isspace()== True ] )
        if machilen > 0:
            print("error in machine"+str(machilen))
            return False

        return True
    
    except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return None


def getTheMonthlyEventsCountBasedOnType(evtype):

    try:
        resultset = events.objects.raw('''Select 1 as eventid, Date(`date`) as event_date, count(eventid) as event_count from users_events
        where type = 'ANIMAL_DETECTION' and  `date` > Date(DATE_SUB(now(),interval 24 MONTH)) 
                                    group by Date(`date`)''')
        return resultset

    except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return None     


