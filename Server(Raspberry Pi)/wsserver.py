#!/usr/bin/python3
##############################################################
#                                                            #
#             AutoDoor2(config) For Raspberry Pi             #
#              By Xavier Leff And Julio Machado              #
#                                                            #
##############################################################
# make sure you run this in sudo
from ast import Str
import asyncio
from copy import error
import time
import websockets
import json
import psutil
import subprocess

# global var
logFileLoc = "/home/pi/wsserver.log"

def logs(logStatement: str): # to log operations
    logStatement = f"{time.asctime()}: " + logStatement
    print(logStatement)
    with open(logFileLoc, "a") as logFile:
        logFile.write(logStatement+"\n")

def kill(): # kills autodoor
    for process in psutil.process_iter():
        if process.cmdline() == ['python3', '/home/pi/AutoDoor2.py'] or process.cmdline() == ['python3','AutoDoor2.py']:
            process.kill()

def start(): # Start autodoor
    for process in psutil.process_iter():
        if process.cmdline() == ['python3', '/home/pi/AutoDoor2.py'] or process.cmdline() == ['python3','AutoDoor2.py']:
            process.kill()
    time.sleep(1)
    subprocess.Popen(['nohup','python3', '/home/pi/AutoDoor2.py'],start_new_session=True)


def checkData(config,list):
    prob = []
    for param in list:
        if config[param]== None:
            prob.append(param)
    if len(prob) > 0:
        return f"Missing Fieldß{prob}"
    return False


async def acceptIncomingConnection(websocket):
    try:
        async for message in websocket:
            if "ß" in message:
                arg,data = message.split('ß')
            else:
                arg = message
            try: # cluster fuck of if else
                if arg == "getConfig":
                    with open('/home/pi/config.json',"r") as f:
                        configStr = f.read()
                        await websocket.send(f"configß{configStr}")
                elif arg ==  "updateConfig":
                    print(data)
                    res = checkData(json.loads(data),["starth","endh","startmin","endmin","lstarth","lstartmin","lendh","lendmin","LEDPin","ServoPin","list"])
                    if type(res) == str :
                        logs(res)
                        await websocket.send(res)
                    else:
                        with open('/home/pi/config.json',"w") as f:
                            f.write(data)
                        start()
                        re = "config updated"
                        logs(re)
                        await websocket.send(re)
                        pass
                elif arg ==  "getLogs":
                    with open('/home/pi/AutoDoor2.log',"r") as f:
                        logLines = f.read()
                        await websocket.send(f"Logsß{logLines}")
                        logs("logs sent")
                    pass
                elif arg ==  "stopAutodoor":
                    kill()
                    re = "AutoDoor killed"
                    logs(re)
                    await websocket.send(re)
                    pass
                elif arg ==  "startAutodoor":
                    start()
                    re = "AutoDoor Started"
                    log = re
                    await websocket.send("AutoDoor Started")
                else:
                    re = f"Bad Commandß{arg}"
                    logs(re)
                    await websocket.send(re)
                logs(f"executed {arg}")
            except Exception as err:
                logs(f"Error:[{err}]")
                re = f"Error Executingß{arg}"
                logs(re)
                await websocket.send(re)
    except websockets.exceptions.ConnectionClosedError:
        logs("Connection Closed")

async def main():
    async with websockets.serve(acceptIncomingConnection, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


logs("Starting...")
asyncio.run(main())