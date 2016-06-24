#######################################
#                                     #
#       HOW TO SHARE DATA BETWEEN     #
#        PYTHON THREADS ON WEIO       #
#                                     #
#######################################

# Simple standalone application, no web interface
# Description: Reads digital potentiometer from pin 25 to blink LED slower or
# faster at digital pin 20.
# Threads potentiometer and blinky are like individual mini programs. Share data between them using shared variables.
# In this case shared object is shared.val
# In most of cases this usage will work. If sync problems are encountered use lock library to lock

from weioLib.weio import *

ledPin = 20
potentiometerPin = 25

def setup():

    # Attaches sensor function to infinite loop
    attach.process(blinky)

    # Attaches sensor function to infinite loop
    attach.process(potentiometer)

    # Instanciate shared objects
    sharedVar[0] = 0

def potentiometer() :

    while True :

        # Update shared.val with analogRead on potentiometerPin
        sharedVar[0] = analogRead(potentiometerPin)

        # Print value of potentiometerPin on console
        print "VALUE ON PIN ",potentiometerPin,":  ", sharedVar[0]

        # Do nothing during 0.5 seconds
        delay(500)

def blinky() :

    while True :

        # write HIGH value on ledPin
        digitalWrite(ledPin, HIGH)

        # wait in this state during shared.val value
        delay(sharedVar[0])

        # write LOW value on ledPin
        digitalWrite(ledPin, LOW)

        # wait in this state during new shared.val value
        delay(sharedVar[0])
