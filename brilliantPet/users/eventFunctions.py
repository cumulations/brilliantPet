from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback
from django.utils import timezone
from datetime import datetime, timedelta 



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
