#!/usr/bin/python

# Contains the class that use listeners classes (sofwares) and the display class (mediapad)

class MediapadMonitor():

    def __init__(self,mediapad,softwares):
        import dbus
        # Connect to the system bus and session bus 
        self.ses_bus = dbus.SessionBus()
        self.sys_bus = dbus.SystemBus()        
        self.mediapad = mediapad       
        self.softwares = softwares
        self.prioritySoft = None
        self.running = False

    def stop(self):
        print "Stop monitoring..."
        self.running = False
        # Unlisten all sofwares
        for software in self.softwares :
            software.unlisten()
            software.mediapad = None
        if self.mediapad.lcd != None :
            self.mediapad.ClearScreen()
        
    def watch(self):
        # Connect the soft to the actual mediapad instance
        for software in self.softwares :
            software.mediapad = self.mediapad
        # and begin refresh display...  
        self.pausedMode = False  
        # Search for the priority media software
        best = 0
        
        for software in self.softwares :
            # Get received messages/mails
            if software.state == "received":
                software.writeData()
            
            # Get softwares only with "playing" state
            if software.state == "playing" or software.state == "loading" or software.state == "loaded":
                # Get the actual best priority software playing
                if software.priority > best : 
                    best = software.priority
                    self.prioritySoft = software
                    self.pausedMode = False
                    
        # If no software is playing, look for one paused
        if self.prioritySoft == None : 
            for software in self.softwares :
                # Get softwares only with "paused" state (out of event control)
                if software.state == "paused" and self.pausedMode == False :
                    # Get the actual best priority software paused
                    if software.priority > best : 
                        best = software.priority
                        self.prioritySoft = software 
                        # set pausedMode so don't refresh paused display till new playing
                        self.pausedMode = True  
                                
        # If we found something to display...           
        if self.prioritySoft != None : 
            # Get/refresh the data from the soft
            self.prioritySoft.getData() 
            # Write it to the LCD
            self.prioritySoft.writeData()
            
        # No player is playing or paused, no "pausedMode", so clear the LCD
        elif self.pausedMode == False: 
            self.mediapad.ClearScreen()
                

    # Method for main loop watching and "constant displaying" (out of event control)
    def run(self):
        import time
        self.running = True
        time.sleep(2.0)

        # Main loop waiting for mediapad (listen for connection)
        while self.running == True: 
            if self.mediapad.lcd != None :  
                self.watch()
                time.sleep(1.0)
            else : 
                # If no mediapad found or disconnected, wait 2 seconds and try again
                time.sleep(2.0)
                
        print "Monitoring stopped"


    



