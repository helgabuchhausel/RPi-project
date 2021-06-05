#!/usr/bin/python3

# IMPORTS
import paho.mqtt.client as mqtt
import time
import random

#INIT VARS
Objects = []
playerAssignments = []
PIDs = []
player1id = 0
player2id = 0
score1 = 0
score2 = 0
CanvasWidth = 600
CanvasHeight = 400
SpeedX = 20
SpeedY = 20
switch = 0

class Player1:
    def __init__(self, name, id, posX, posY, sizeX, sizeY):
        self.id = id
        self.name = "Player1"
        self.posX = posX
        self.posY = posY
        self.sizeX = sizeX
        self.sizeY = sizeY

class Player2:
    def __init__(self, name, id, posX, posY, sizeX, sizeY):
        self.id = id
        self.name = "Player2"
        self.posX = posX
        self.posY = posY
        self.sizeX = sizeX
        self.sizeY = sizeY
        
class Ball:
    def __init__(self, name, id, posX, posY, sizeX, sizeY):
        self.id = id
        self.name = "Ball"
        self.posX = posX
        self.posY = posY
        self.sizeX = sizeX
        self.sizeY = sizeY

def Collision(a, b):
    global Objects
    global switch
    global SpeedX,SpeedY
    if (b.posX in range(a.posX, a.posX+a.sizeX) or b.posX+b.sizeX in range(a.posX, a.posX+a.sizeX)) and (b.posY in range(a.posY, a.posY+a.sizeY) or b.posY+b.sizeY in range(a.posY, a.posY+a.sizeY)):
        if (a.name == "Player1" and b.name == "Ball"):
            SpeedY = 20
            PublishObjects()
            b.posY = b.posY + 30
            b.posY -= SpeedY
        if (a.name == "Player2" and b.name == "Ball"):
            SpeedY = -20
            PublishObjects()
            b.posY = b.posY - 30
            b.posY -= SpeedY

def PubScore(scoreItem,score):
    client.publish("test/message", scoreItem + str(score))

def PublishObjects():
    global Objects
    for o in Objects:
        client.publish("test/message", " "+ str(o.name) + "-" + str(o.id) + ":" + str(o.posY) + ":" + str(o.posX))

def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))
    client.subscribe("test/message")

def on_message(client, userdata, msg):
    global Objects
    global playerAssignments
    global CanvasWidth
    global CanvasHeight
    global Speed
    global switch
    global player1id
    global player2id

    print(" "+str(msg.payload))
    message = msg.payload.decode("utf-8")
    cmd = message.split(":")

    if cmd[0] == "RequestRole":

        if "Player1" not in playerAssignments:
            Objects.append(Player1("Player1", player1id, 200, 50, 150,40))
            playerAssignments.append("Player1")
            PIDs.append("Player1-" + str(player1id))
            client.publish("test/message", "Player1-" + str(player1id))
            player1id += 1
            if player1id > 9:
                for p in range(9):
                    if any(x.id != p for x in Objects):
                        player1id = p
        elif switch == 0:
            switch = 1
            Objects.append(Player2("Player2", player2id, 200, 550, 150,40))
            playerAssignments.append("Player2")
            PIDs.append("Player2-" + str(player2id))
            client.publish("test/message", "Player2-" + str(player2id))
            player2id += 1
            if player2id > 9:
                for p in range(9):
                    if any(x.id != p for x in Objects):
                        player2id = p

    if cmd[0] == "Player1" and cmd[2] == "UP":
        for k in Objects:
            if k.id == int(cmd[1]):
                k.posX-= SpeedY
    if cmd[0] == "Player1" and cmd[2] == "DOWN":
        for k in Objects:
            if k.id == int(cmd[1]):
                k.posX+= SpeedY

    if cmd[0] == "Player2" and cmd[2] == "UP":
        for w in Objects:
            if w.id == int(cmd[1]):
                w.posX-= SpeedY

    if cmd[0] == "Player2" and cmd[2] == "DOWN":
        for w in Objects:
            if w.id == int(cmd[1]):
                w.posX+= SpeedY
                

mqtt.Client.connected_flag=False
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()
client.connect("broker.hivemq.com", 1883, 60)

Objects.append(Ball("Ball", 99, 200, 300, 80,80))

while not client.connected_flag:
    time.sleep(0.5)
    for o in Objects:
        if o.name == "Player1":
            if o.posY > 600: 
                o.posY = 0
            if o.posX >= 400:
                o.posX = 400
            if o.posX <= 0:
                o.posX = 0
#             o.posX += Speed
        if o.name == "Player2":
            if o.posY > 600:
                o.posY = 0
            if o.posX >= 400:
                o.posX = 400
            if o.posX <= 0:
                o.posX = 0
#             o.posY += Speed
        if o.name == "Ball":
            if o.posY >= 600:
                score2 += 5
                PubScore("Score2-",score2)
                o.posX = 200
                o.posY = 300
                SpeedY = -20
            elif o.posY <= 0:
                score1 += 5
                PubScore("Score1-",score1)
                o.posX = 200
                o.posY = 300
                SpeedY = 20    
                
            if o.posX >= 400:
                SpeedX = -20
            elif o.posX <= 0:
                SpeedX = 20
                
            o.posX += SpeedX
            o.posY += SpeedY     
        for i in Objects:
             Collision(i, o)
    PublishObjects()
client.loop_stop()
