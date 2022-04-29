from ast import Str
import asyncio
from copy import error
from re import S
import websockets
import json
import psutil
import subprocess

def kill():
    for process in psutil.process_iter():
        if process.cmdline() == ['python3', '/home/pi/AutoDoor/AutoDoor2.py']:
            process.kill()
        if process.cmdline() == ['python3','AutoDoor2.py']:
            process.kill()

def start():
    for process in psutil.process_iter():
        if process.cmdline() == ['python3', '/home/pi/AutoDoor/AutoDoor2.py']:
            process.kill()
        if process.cmdline() == ['python3','AutoDoor2.py']:
            process.kill()
    subprocess.Popen(['nohup','python3', '/home/pi/AutoDoor/AutoDoor2.py'],start_new_session=True)


def checkData(config,list):
    prob = []
    for param in list:
        if config[param]!= None:
            prob.append(param)
    if len(prob) >0:
        return f"Missing Field::{prob}"
    return False


async def acceptIncomingConnection(websocket):
    try:
        async for message in websocket:
            if "::" in message:
                arg,data = message.split('::')
            else:
                arg = message
            try:
                if arg ==  "updateConfig":
                    mesConfig = json.loads(data)
                    res = checkData(mesConfig,["schoolStartTime","schoolEndTime","lunchStartTime","lunchEndTime","starth","endh","startmin","endmin","lstarth","lstartmin","lendh","lendmin","LEDPin","ServoPin","list"])
                    if type(res) == str :
                        websocket.send(res)
                        return
                    with open('../AutoDoor/config.json',"w") as f:
                        f.write(mesConfig)
                    await websocket.send("config updated")
                    pass
                elif arg ==  "updateTime":
                    mesConfig = json.loads(data)
                    res = checkData(mesConfig,["schoolStartTime","schoolEndTime","lunchStartTime","lunchEndTime","starth","endh","startmin","endmin","lstarth","lstartmin","lendh","lendmin"])
                    if type(res) == str :
                        websocket.send(res)
                        return
                    with open('../AutoDoor/config.json',"r") as f:
                        configStr = f.read()
                        config = json.loads(configStr)
                        mesConfig["LEDPin"] = config["LEDPin"]
                        mesConfig["ServoPin"] = config["ServoPin"]
                        mesConfig["list"] = config["list"]
                    with open('../AutoDoor/config.json',"w") as f:
                        f.write(mesConfig)
                    await websocket.send("Time Updated") 
                    pass
                elif arg ==  "updateStudents":
                    mesConfig = json.loads(data)
                    res = checkData(mesConfig,["schoolStartTime","schoolEndTime","lunchStartTime","lunchEndTime","starth","endh","startmin","endmin","lstarth","lstartmin","lendh","lendmin"])
                    if type(res) == str :
                        websocket.send(res)
                        return
                    with open('../AutoDoor/config.json',"r") as f:
                        configStr = f.read()
                        config = json.loads(configStr)
                        config['list'] = mesConfig['list']
                    with open('../AutoDoor/config.json',"w") as f:
                        f.write(config)
                    await websocket.send("students updated")
                    pass
                elif arg ==  "getLogs":
                    with open('../AutoDoor/AutoDoor2.log',"r") as f:
                        log = f.read()
                        pass
                    await websocket.send(f"Logs::{log.encode()}")
                    pass
                elif arg ==  "stopAutodoor":
                    kill()
                    await websocket.send("AutoDoor killed")
                    pass
                elif arg ==  "startAutodoor":
                    start()
                    await websocket.send("AutoDoor Started")
                else:
                    await websocket.send(f"Bad Command::{arg}")
                print(f"executed {arg}")
            except error:
                print(error)
                await websocket.send(f"Error Executing::{arg}")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection Closed")

async def main():
    async with websockets.serve(acceptIncomingConnection, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


print("Starting...")
asyncio.run(main())