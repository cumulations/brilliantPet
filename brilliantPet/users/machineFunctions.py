from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback

gm = generalClass()

def getMachine(data):
    data = gm.cleanData(data)
    try:
       
        if "machine_id" in data and data["machine_id"] not in ["", None]:
            machine = MachineDetails.objects.filter(machine_id=data["machine_id"])
            return machine[0]
        else:
            return None
    except:
        traceback.print_exc()
        gm.errorLog(traceback.format_exc())
        return None


def validateMachineSize(sizeoption):
    mainMachineList=["standard","small","large"]
    if  sizeoption not in mainMachineList:
        return False
    else:
         return True

def validateRollLength(sizeoption):
    mainRollList=["standard","origin"]
    if  sizeoption not in mainRollList:
        return False
    else:
         return True

def validateMachineId(machine_id):
    if machine_id == None or machine_id.isspace():
        return False
    else: 
        return machine_id.isalnum()
    
  

def updateMachine(data,machine_id):
        data = gm.cleanData(data)
        try:
            machine_size= None if "machine_size" not in data else data["machine_size"]
            roll_length = None if "roll_length" not in data else data["roll_length"]

            if validateMachineId(machine_id): 
                
                machine = machine_id.objects.get(machine_id=machine_id)
                if machine != None:

                    if roll_length:
                        if validateRollLength(roll_length):
                            machine.roll_length = roll_length
                        else:
                            print("invalid roll lenth")
                            return None

                    if machine_size: 
                        if validateMachineSize(machine_size):
                            machine.machine_size = machine_size
                        else:
                            print("invalid machine size")
                            return None
                    
                    machine.save()
                else:
                    print("Machine not found")
                    return None



            else:
                print("invalid machine Id")
                return None
            
        except Exception as e:
            traceback.print_exc()
            print("exception here")
            print(e)
            return None
