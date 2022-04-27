
#!/usr/bin/python3
##############################################################
#                                                            #
#                 AutoDoor2 For Raspberry Pi                 #
#              By Xavier Leff And Julio Machado              #
#                                                            #
##############################################################
#This file is responsible for opening and closing the door by dirctly interacting with the servo, works in conjunction with AutoDoorC2 with acts as a way to interface with the terminal application at Mr. Rao's computer
from re import T
import RPi.GPIO as GPIO #May be commented out since testing on windows machine
from time import sleep
import string
import json 
import threading
import struct
import time

configFile = "config.json"

Mouse = open( "/dev/input/mice", "r+b", 0)

Scanner = open( "/dev/input/by-id/usb-Scanner_Joystick_in_FS_Mode_00000000011C-event-kbd", "r+b", 0)

keycodes={0:'RESERVED',1:'ESC',2:'1',3:'2',4:'3',5:'4',6:'5',7:'6',8:'7',9:'8',10:'9',11:'0',12:'-',13:'=',14:'BACKSPACE',15:'\t',16:'Q',17:'W',18:'E',19:'R',20:'T',21:'Y',22:'U',23:'I',24:'O',25:'P',26:'[',27:']',28:'\n',29:'LEFTCTRL',30:'A',31:'S',32:'D',33:'F',34:'G',35:'H',36:'J',37:'K',38:'L',39:';',40:"'",41:'`',42:'LEFTSHIFT',43:'/',44:'Z',45:'X',46:'C',47:'V',48:'B',49:'N',50:'M',51:',',52:'.',53:'\\',54:'RIGHTSHIFT',55:'*',56:'LEFTALT',57:' ',58:'CAPSLOCK',59:'F1',60:'F2',61:'F3',62:'F4',63:'F5',64:'F6',65:'F7',66:'F8',67:'F9',68:'F10'}

modKeyMap={'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')','/':'?','.':'>',',':'<',';':':',"'":'"',']':'}','[':'{','=':'+','-':'_','`':'~'}

upperAlphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"
lowerAlphabet = "qwertyuiopasdfghjklzxcvbnm"

ScannerData = None
MouseData = False

def initialize() -> list:
    #Reads config file config.json
    with open(configFile, "r") as configFileHandler:
        configRaw = configFileHandler.read()
    #Loads file into JSON
    config = json.loads(configRaw)
    #Defines values from config.json
    LEDPin = config["LEDPin"]
    ServoPin = config["ServoPin"]
    logFileLoc = config["logFile"]
    schoolStartHour = config["starth"]
    schoolEndHour = config["endh"]
    schoolStartMinute = config["startmin"]
    schoolEndMinute = config["endmin"]
    lunchStartHour = config["lstarth"]
    lunchEndHour = config["lendh"]
    lunchStartMinute = config["lstartmin"]
    lunchEndMinute = config["lendmin"]
    students = config["list"]
    
    #Cleanse student list by removing non-printable characters
    students = list(filter(lambda x: x in string.printable, students))
    #As this will return a list with each separate character, everything needs to be concateneted together, will also strip out charage returns for linux windows new line compatability
    #Starting and ending new lines are also stipped here, along with splitting of \n to provide a just list of student numbers
    students = "".join(students).replace("\r", "").strip().split(",")

    #Creates a list of values to be used later in the program like student numbers and the admin key
    initalizedValues = [students, LEDPin, ServoPin, logFileLoc, schoolStartHour, schoolEndHour, schoolStartMinute, schoolEndMinute, lunchStartHour, lunchEndHour, lunchStartMinute, lunchEndMinute]
    
    return initalizedValues

def log(logStatement: str):
    logStatement = f"{time.asctime()}: " + logStatement
    print(logStatement)
    with open(logFileLoc, "a") as logFile:
        logFile.write(logStatement+"\n")

def openDoor():
    try:
        GPIO.output(LEDPin, GPIO.HIGH) #led on
        SERVO.ChangeDutyCycle(4) # servo on
        sleep(2) 
        GPIO.output(LEDPin, GPIO.LOW) #led off
        SERVO.ChangeDutyCycle(2) # servo closing
        sleep(0.1)
        SERVO.ChangeDutyCycle(0) # servo full close
    except Exception as e:
        log(f"{e}")
        GPIO.output(LEDPin, GPIO.LOW)

def ScannerFunc():
    global ScannerData
    toggle = False # shift key toggle
    array = "" # stores final output
    while True:
        if ScannerData == None:
            try:
                data = Scanner.read(16)
                unpacked = struct.unpack('2I2HI',data) #Good luck (https://docs.python.org/3/library/struct.html#format-characters)
                organized = (unpacked[2],unpacked[3],unpacked[4])
                if organized[0] == 1 and (organized[1] == 54 or organized[1] == 42): # checks shift key press
                    if organized[2] == 1: # checks shift key
                        toggle = True
                    else:
                        toggle = False
                elif organized[0] == 1 and organized[2] == 1: 
                    key = keycodes.get(organized[1]) # gets key pressed
                    if key in upperAlphabet: # converts caps to lower
                        key = key.lower()
                    if toggle == True: # if shift is active use modmap
                        if key in lowerAlphabet:
                            key = key.upper()
                        else:
                            key = modKeyMap[key]
                    if organized[1] == 28: # checks enter key
                        ScannerData = array
                        array = ""
                    else: #puts keys into array
                        array += key
            except:
                Loop = True
                log("Scanner Malfunctioned")
                while Loop:
                    try:
                        data = Scanner.read(16)
                        Loop = False
                    except:
                        pass

        

def MouseFunc():
    global MouseData
    while True:
        data = Mouse.read(3)  # Reads the 3 bytes 
        unpacked = struct.unpack('3b',data)  #Unpacks the bytes to integers
        if MouseData == False:
            if unpacked == (9,0,0): # check left click
                MouseData = True
        else:
            data = None


def checkTime(timeOfAttempt) -> bool:
    timeHour = timeOfAttempt.tm_hour
    timeMinute = timeOfAttempt.tm_min
    dayOfAttempt = timeOfAttempt.tm_wday

    #Checks if it's a weekday and returns false if it's a weekend
    if not dayOfAttempt in schoolDays:
        return False

    # checks hour
    if schoolStartHour <= timeHour <= schoolEndHour:
        #checks if time = start time
        if timeHour == schoolStartHour:
            # checks if min > start min
            if schoolStartMinute <= timeMinute:
                return True
            return False
        #check if time = end time
        if timeHour == schoolEndHour:
            # checks if min > start min
            if schoolEndMinute > timeMinute:
                return True
            return False
        # checks if its lunch hour
        if lunchStartHour <= timeHour <= lunchEndHour:
            # check if min is within lunch
            if lunchStartMinute <= timeMinute < lunchEndMinute:
                return False
        return True
    else:
        return False

def Main():
    global ScannerData;global MouseData
    log("Starting...")
    while True:
        if ScannerData != None :
            if type(ScannerData) == str:
                if ScannerData != "":
                    if ScannerData in students:
                        #Check time to ensure student is comming into class at the correct time
                        timeOfAttempt = time.localtime()
                        #timeOfAttempt = "7:25"
                        if checkTime(timeOfAttempt):
                            #Open Door
                            GPIO.output(LEDPin, GPIO.HIGH)
                            #Generate log statement and log entry
                            log(f"User [{ScannerData}] Valid")
                            openDoor()
                        else:
                            log(f"Out of time scan by [{ScannerData}]")
                    else:
                        log(f"User [{ScannerData}] Invalid")
            ScannerData = None;MouseData = False
        elif MouseData :
            log("Mouse Opened Door")
            openDoor()
            ScannerData = None;MouseData = False

students, LEDPin, ServoPin, logFileLoc, schoolStartHour, schoolEndHour, schoolStartMinute, schoolEndMinute, lunchStartHour, lunchEndHour, lunchStartMinute, lunchEndMinute = initialize()
GPIO.setmode(GPIO.BCM)
GPIO.setup(ServoPin, GPIO.OUT) #SERVO
GPIO.setup(LEDPin, GPIO.OUT) #LED
GPIO.output(LEDPin, GPIO.LOW)
SERVO = GPIO.PWM(ServoPin, 50)
SERVO.start(0)
allProcesses = []
schoolDays = [0,1,2,3,4] #Weekdays 0=mon, 1=tue, 2=wed, 3=thu 4=fri


ScannerThread = threading.Thread(target=ScannerFunc, args=())
MouseThread = threading.Thread(target=MouseFunc, args=())

ScannerThread.start()
MouseThread.start()

while True:
    try:
        Main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit(0)

