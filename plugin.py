#!/usr/bin/python

###############################
# OBSOLETE STAND ALONE PLUGIN ! 
#
# WILL BE REPLACED BY OPTIONAL RUNNING OF controler.py
#
# RUN controler.py instead
###############################

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

# Connect to the system bus and session bus
ses_bus = dbus.SessionBus()
sys_bus = dbus.SystemBus()


# Instantiate the mediapad
mediapad = MediaPad(sys_bus)

# Load all listenable softwares in the session
softwares = {BansheeListened(ses_bus),SkypeListened(ses_bus),RhythmboxListened(ses_bus),TotemListened(ses_bus),EvolutionListened(ses_bus)}

# Function for main loop watching and "constant displaying" (out of event control)
def display(softwares,mediapad):
    # Main loop waiting for mediapad (listen for connection)
    while 1 :
        if mediapad.lcd != None :
            
            # When mediapad is connected...
            for software in softwares :
                # Connect the soft to the actual mediapad instance
                software.mediapad = mediapad
                             
            # and begin refresh display...
            pausedMode = False
            while mediapad.lcd != None :
                # Search for the priority media software
                best = 0
                prioritySoft = None
                for software in softwares :
                    # Get received messages/mails
                    if software.state == "received":
                        software.writeData()
                    
                    # Get softwares only with "playing" state (out of event control)
                    if software.state == "playing" or software.state == "loading" or software.state == "loaded":
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
                    mediapad.lcd.SetScreenMode(3)
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