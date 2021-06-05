#!/usr/bin/python3

# IMPORTS
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

try:
    playerId = None
    playerAssigned = None
    leds = [13,19,26]
    down = 27
    up = 22

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(down,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(up,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    for l in leds:
        GPIO.setup(l,GPIO.OUT)

    def resetleds():
        for l in leds:
            GPIO.output(l,0)

    def button_callback(channel):
        print(channel)
        global playerAssigned
        global playerId

        if playerAssigned == "Player1":
            if channel == 27:
                console.publish("test/message",playerAssigned + ":" + playerId + ":UP")
            elif channel == 22:
                console.publish("test/message",playerAssigned + ":" + playerId + ":DOWN")
        elif playerAssigned == "Player2":
            if channel == 27:
                console.publish("test/message",playerAssigned + ":" + playerId + ":UP")
            elif channel == 22:
                console.publish("test/message",playerAssigned + ":" + playerId + ":DOWN")

    GPIO.add_event_detect(27,GPIO.FALLING,callback=button_callback,bouncetime=100)
    GPIO.add_event_detect(22,GPIO.FALLING,callback=button_callback,bouncetime=100)

    #WHEN CONNECTED AUTO ASSIGNMENT OF PLAYERS WILL TAKE PLACE
    def on_connect (client,userdata,flags,rc):
        print ("Connected with result code " + str(rc))
        console.subscribe("test/message")
        console.publish("test/message", "RequestRole")
        print ("Requesting Role...")

#     MQTT ON MESSAGE RECEIVED
    def on_message (client,userdata,msg):
        global playerId
        global playerAssigned
        message = msg.payload.decode("utf-8")
        if playerId == None and message != "RequestRole":
            print(message)
            playerId = message.split('-')[1]
            playerAssigned = message.split('-')[0]
            if playerAssigned == "Player1":
                resetleds()
                GPIO.output(19,1)
                print ("ASSIGNED PLAYER : Player1")
            elif playerAssigned == "Player2":
                resetleds()
                GPIO.output(13,1)
                print ("ASSIGNED PLAYER : Player2")

    # MQTT SETTINGS
    console = mqtt.Client() 
    console.on_connect = on_connect
    console.on_message = on_message
    console.connect("broker.hivemq.com", 1883,60)
    console.loop_forever()

except KeyboardInterrupt:
    print ("Exiting...")
finally:
    GPIO.cleanup()
