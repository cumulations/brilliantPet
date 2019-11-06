from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback

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
