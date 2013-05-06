#!/usr/bin/python

# Contains the main loop and manage "out of events" displaying and decisions

import dbus,gobject,time,sys,atexit
from threading import Thread
from gobject import * 
from dbus.mainloop.glib import DBusGMainLoop
# Import listeners Class for software to support
from listeners import *

# Create the threaded mainloop
DBusGMainLoop(set_as_default=True)
mainloop = gobject.MainLoop()
gobject.threads_init()
context = mainloop.get_context()
   
# Instantiate the mediapad     
mediapad = MediaPad()

# Load all listenable softwares in the session
softwares = {SkypeListened(),BansheeListened(),RhythmboxListened(),TotemListened(),EvolutionListened()}

# Function for main loop watching and "constant displaying" (out of event control)
def display(softwares,mediapad):
    time.sleep(2.0)
    # Main loop waiting for mediapad (listen for connection)
    while 1 : 
        if mediapad.lcd != None :  
            # When mediapad is connected... 
            for software in softwares :
                # Connect the soft to the actual mediapad instance
                software.mediapad = mediapad
            # and begin refresh display...  
            pausedMode = False          
            while mediapad.lcd :
                # Search for the priority media software
                best = 0
                prioritySoft = None
                for software in softwares :
                    # Get softwares only with "playing" state (out of event control)
                    if software.state == "playing":
                        # Get the actual best priority software playing
                        if software.priority > best : 
                            best = software.priority
                            prioritySoft = software
                            pausedMode = False
                # If no software is playing, look for one paused
                if prioritySoft == None : 
                    for software in softwares :
                        # Get softwares only with "paused" state (out of event control)
                        if software.state == "paused" and pausedMode == False :
                            # Get the actual best priority software paused
                            if software.priority > best : 
                                best = software.priority
                                prioritySoft = software 
                                # set pausedMode so don't refresh paused display till new playing
                                pausedMode = True           
                # If we found something to display...           
                if prioritySoft != None : 
                    # Get/refresh the data from the soft
                    prioritySoft.getData() 
                    # Write it to the LCD
                    prioritySoft.writeData()
                # No player is playing or paused, no "pausedMode", so clear the LCD
                elif pausedMode == False: 
                    mediapad.ClearScreen()
                # Wait 1 second and then, refresh 
                time.sleep(1.0)
        else : 
            # If no mediapad found or disconnected, wait 2 seconds and try again
            time.sleep(2.0)

# Run general displaying function in separated thread
t = Thread(target=display, args=(softwares,mediapad))
t.start()


# Run the main loop
mainloop.run()


    



