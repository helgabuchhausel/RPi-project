#!/usr/bin/python3

#IMPORTS
import tkinter as tk
from PIL import ImageTk, Image
import time
from threading import Thread
import paho.mqtt.client as mqtt
import sys

venster = tk.Tk()

# MQTT TOPIC SETTINGS
broker = "broker.hivemq.com"
port = 1883
topic = "test/message"

# WINDOW SETTINGS
canvasHeight = 400
canvasWeight = 600
  
# TITLE 
text = tk.Label(venster, text="PONG MULTIPLAYER !")
text.pack()

#SCORE LABEL
scorelabel = tk.Label(venster, text="SCORE OF GAME")
scorelabel.pack()

#GAME OVER LABEL
gameOverLabel = tk.Label(venster, text="GAME OVER")
gameOverLabel.pack()

updateguibool = True
currentScore = ""
currentScore2 = ""
gameOver = ""

try:
    paddle1Image = ImageTk.PhotoImage(Image.open("paddle.PNG"))
    paddle2Image = ImageTk.PhotoImage(Image.open("paddle.PNG"))
    ballImage = ImageTk.PhotoImage(Image.open("ball.png"))
except:
    print("Error occured while setting images...")

canvas = tk.Canvas(venster, width=canvasWeight, height=canvasHeight)
canvas.pack()


def CloseInterface():
    try:
        global Gameobject, currentScore, updateguibool, currentScore2
        for i in Gameobjects:
            Gameobjects.remove(i)
        currentScore = "Score1 reset"
        currentScore2 = "Score2 reset"
        updateguibool = True
    except:
        print("Error closing user interface...")


ExitButton = tk.Button(venster, text="RESET UI", command=CloseInterface)
ExitButton.pack()

Gameobjects = []


class Gameobject():
    def __init__(self, iid, ix, iy, itype):
        self.type = itype
        self.di = iid
        self.x = ix
        self.y = iy


def draw(object):
    if (object.type == "Player1"):
        return canvas.create_image(object.x, object.y, image=paddle1Image)
    elif (object.type == "Player2"):
        return canvas.create_image(object.x, object.y, image=paddle2Image)
    elif (object.type == "Ball"):
        return canvas.create_image(object.x, object.y, image=ballImage)

def RemoveFromGame(idtosnap):
    print("id:", idtosnap, " got snapped.")
    global Gameobjects
    for i in Gameobjects:
        if (i.di == idtosnap):
            Gameobjects.remove(i)


def AddToGame(newgameobj):
    print(newgameobj.type, " Player joined with id:", newgameobj.di)
    global Gameobjects
    Gameobjects.append(newgameobj)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic)


def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    print(message)
    global Gameobjects, updateguibool
    ptype = message.split(':')[0].split('-')[0]
    ptype = ptype.join(ptype.split())
    if (ptype == "Player1" or ptype == "Player2" or ptype == "Ball"):
        try:
            mes = message.split(':')[2]
        except:
            mes = "mama"
        if(mes.isnumeric()):
            pid = ptype + message.split(':')[0].split('-')[1]
            px = message.split(':')[1]
            py = message.split(':')[2]
            playerbestaat = False
            for i in Gameobjects:
                if (i.di == pid):
                    playerbestaat = True
            if (playerbestaat):
                for i in Gameobjects:
                    if (i.di == pid):
                        i.x = int(px)
                        i.y = int(py)
            else:
                AddToGame(Gameobject(pid, px, py, ptype))
            updateguibool = True
    if (ptype == "Score1"):
        global currentScore, gameOver
        currentScore = "Score Player1 : " + message.split('-')[1]
        if(message.split('-')[1] == str(50)):
            gameOver = "GAME OVER PLAYER 1 WON !!"
            updateguibool = True
            time.sleep(3)
            venster.destroy()
        updateguibool = True

    if (ptype == "Score2"):
        global currentScore2 
        currentScore2 = "Score Player2 : " + message.split('-')[1]
        if(message.split('-')[1] == str(50)):
            gameOver = "GAME OVER PLAYER 2 WON !! EXITING IN 3 SECONDS"
            updateguibool = True
            time.sleep(3)
            venster.destroy()
        updateguibool = True

def listener():
    client = mqtt.Client()
    client.connect(broker, port, 60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()


def Update():
    global updateguibool
    while(True):
        venster.update()
        if (updateguibool):
            scorelabel.configure(text=currentScore + " " + currentScore2)
            gameOverLabel.configure(text=gameOver) 
            canvas.delete("all")
            for i in Gameobjects:
                draw(i)
            updateguibool = False


joblistener = Thread(target=listener)
joblistener.start()
Update()
