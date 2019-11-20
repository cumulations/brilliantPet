from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback

gm = generalClass()

mainWeekDictionary={"Day_1":2,"Day_2":3,"Day_3":5,"Day_4":7,"Day_5":11,"Day_6":13,"Day_7":17}


"""
Providing the list of timers that are applied to a machine
"""
def fileterTimeslotsByMachines(machineid,userid):
    
    flagv= -1    
    
    try:

        timesList = TimerSlot.objects.filter(machine_id = machineid, is_deleted = 0)
        return timesList

    except:
        traceback.print_exc()
        gm.errorLog(traceback.format_exc())
        return None

""" 
validating the weeks array to have exactly 7 days and it should have only 0 or 1.
1 for the active date and 0 for non active date
"""
def validateTheWeeks(weekslist):
    
    try:

        if len(weekslist) != 7:
            print("error in the length of weeks array")
            return -1

   
        flagv=1    
        for flagvalue in range(1,8):
            if int(weekslist[flagvalue-1])!=1 and  int(weekslist[flagvalue-1])!=0:
                return -1

            if int(weekslist[flagvalue-1]) == 1:
                flagv=flagv * mainWeekDictionary.get("Day_"+str(flagvalue))
           
        return flagv
    
    except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return -1


def createTimerForMachine(weeklystring,timeinseconds,is_active,machineid):

        try:
            updat=""
            dictio={}
            timer = TimerSlot()

            timer.machine_id= MachineDetails.objects.get(machine_id=machineid)

            if is_active is not None:
                timer.is_active=is_active

            if weeklystring is not None and timeinseconds is not None:
                weekslist=weeklystring.strip(",").split(",")
                weekly_value= validateTheWeeks(weekslist)

                if weekly_value > 0:
                    timer.weeklystring=weeklystring
                    timer.weekly_value=weekly_value
                    timer.timeinseconds=timeinseconds
                    timer.save()
                    return timer

                else:
                    print("error here boss")
                    return None

            else:
                    return None

        except Exception as e:
            traceback.print_exc()
            print("exception here")
            print(e)
            return None


def updateTimerForMachine(weeklystring,timeinseconds,is_active,machineid,timerId,delete_flag):

        try:
            updat=""
            dictio={}
            timer = TimerSlot.objects.get(timerId=timerId)


            timer.machine_id= MachineDetails.objects.get(machine_id=machineid)

            if is_active is not None:
                timer.is_active=is_active

            if delete_flag is not None:
                x=int(delete_flag)

                if x>0:
                    timer.is_deleted=1
                else:
                    timer.is_deleted=0


            if weeklystring is not None and timeinseconds is not None:
                weekslist=weeklystring.strip(",").split(",")
                weekly_value= validateTheWeeks(weekslist)

                if weekly_value > 0:
                    timer.weeklystring=weeklystring
                    timer.weekly_value=weekly_value
                    timer.timeinseconds=timeinseconds
                    timer.save()
                    return timer

                else:
                    print("error here boss")
                    return None

            else:
                    return None

        except Exception as e:
            traceback.print_exc()
            print("exception here")
            print(e)
            return None
