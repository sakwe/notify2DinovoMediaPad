#!/usr/bin/python
import time

# This part contains the LCD displayer class
#-------------------------------------------


# OS constants for sofware managing
#----------------------------------

# LCD Media Pad in OS
URI_FOR_LCD = 'com.hentenaar.Dinovo.MediaPad'
PATH_FOR_LCD ='/com/hentenaar/Dinovo/MediaPad'
# Display modes 
LCD_DISP_MODE_INIT = 0x01 # Initialize the line 
LCD_DISP_MODE_BUF1 = 0x10 # Display the first buffer on the line 
LCD_DISP_MODE_BUF2 = 0x11 # ... 2nd buffer 
LCD_DISP_MODE_BUF3 = 0x12 # ... 3rd buffer 
LCD_DISP_MODE_SCROLL = 0x20 # Scroll by one buffer 
LCD_DISP_MODE_SCROLL2 = 0x02 # ... by 2 buffers 
LCD_DISP_MODE_SCROLL3 = 0x03 # ... by 3 buffers 

# Class for LCD managing
#------------------------
class MediaPad:
       
    # Initialisise mediapad object and wait for it in system bus
    def __init__(self):
        import dbus
        self.system_bus = dbus.SystemBus()
        self.system_bus.watch_name_owner(URI_FOR_LCD,self.ownerChanged)
        self.loopNumber = 0
        self.lcd = None
        self.clockMode = False
    
    # Connect mediapad object to system bus
    def ownerChanged(self,new_owner):
        import dbus
        if new_owner == '':
            self.lcd = None
            print 'MediaPad is disconnected. Waiting...'
        else:
            self.device = self.system_bus.get_object(URI_FOR_LCD,PATH_FOR_LCD)
            self.lcd = dbus.Interface(self.device,URI_FOR_LCD)
            self.lcd.WriteText('Gnome linked ;-)')  
            self.lcd.BlinkOrBeep(2,0)
            print 'MediaPad is connected'
    
    # Clean the LCD and display clock
    def ClearScreen(self):
        if self.clockMode == False : 
            self.clockMode = True
            self.lcd.ClearScreen()
                
    # Load a line to line buffers of the LCD (3X16 chars per line)
    def loadLine(self,lineno,text):
        i = 1
        # Parse the text data into the 3 buffers
        while (text != '' and i <= 3) : 
            buf = text
            if (len(text) > 16):
                buf = text[0:15] 
                text = text[16:len(text)-1]
            if (len(buf) <= 16): 
                buf = buf + " "
            self.lcd.WriteBuffer((((lineno * 3) - 3) + i - 1),'{:<16}'.format(buf))        
            i=i+1 
    
    # Receive an write order from a software object -> dispatch to correct writer
    def writeData(self,soft):
        # If the LCD is on clock mode, clean the LCD
        if self.clockMode == True : 
            self.lcd.WriteText(" ")
            self.clockMode = False
        if soft.type == "media" :
            self.writeMedia(soft)
        elif soft.type == "message" or soft.type == "mail":  
            self.writeMessage(soft)      
           
    # Write media data to the LCD (title/artist/album/progress bar/status/resting time)     
    def writeMedia(self,soft):
        # TITLE/album/artist
        soft.loopNumber = soft.loopNumber + 1
        if soft.state == "playing" : 
            # Load all items we want to display
            items = {soft.data.title,soft.data.artist,soft.data.album}
            lines = []
            for item in items :  
                # Split all words in the item               
                words = (item).split(" ")
                line = ""
                for word in words : 
                    # 
                    if len(line + word + " " ) > 16 : 
                        # 3 lines = display during 3 loop (3sec) 
                        lines.append(line)
                        lines.append(line)
                        lines.append(line)
                        line = word + " "
                    else : 
                        line = line + word + " " 
                if line != "" :
                    # 3 lines = display during 3 loop (3sec) 
                    lines.append(line)
                    lines.append(line)
                    lines.append(line)
    
            if soft.loopNumber > len(lines) : 
                soft.loopNumber = 1 
            if soft.loopNumber <= len(lines) :
                self.loadLine(1,'{:<8}'.format(lines[soft.loopNumber - 1]))
        # On pause/stop/waiting : display all datas on one line and let the mediapad scroll by itself
        else : 
            self.loadLine(1,'{:<8}'.format(soft.data.title + " - " + soft.data.artist + " [" + soft.data.album + "]"))
        
        # POSITION (progressbar)
        if soft.data.lenght != 0 : 
            sixteen = round((float(soft.data.position)/float(soft.data.lenght))*16,0)
        else : 
            sixteen = 0
        loadBar = ""
        for i in range(0,16):
            if i == int(sixteen) and soft.data.lenght != 0 :
                loadBar = loadBar + "\x16"
            else : 
                loadBar = loadBar + "-"
        self.loadLine(2,loadBar)  
        
        # POSITION (state + position)
        s= '{:<8}'.format(soft.state.title())
        # Diplay elpased time if lengh is not disponible
        if soft.data.lenght != 0 : 
            secondes = (float(soft.data.lenght) - float(soft.data.position)) / 1000
        else : 
            secondes = float(soft.data.position) / 1000
        minutes = int(secondes / 60)
        secondes = secondes%60            
        s = s + '{:>8}'.format(str(int(minutes)).zfill(2) + ":" + str(int(secondes)).zfill(2))
        self.loadLine(3,s)
        self.lcd.SetDisplayMode(LCD_DISP_MODE_SCROLL,LCD_DISP_MODE_BUF1,LCD_DISP_MODE_BUF1);
            
    # Light indicators, beep and blink / Reset indicators    
    def writeMessage(self,soft):
        self.loopNumber = self.loopNumber + 1
        if soft.type == "message" : 
            indic = 2   # chat indicator
            beep = 1    # short beep
        else : 
            indic = 1   # mail indicator
            beep = 2    # beep sound            
        # If received, alert
        if soft.state=="received":
            self.lcd.SetIndicator(indic,1)
            self.lcd.BlinkOrBeep(1,beep)  
        # When read/sent, hide indicators and led light      
        elif soft.state=="read":
            self.lcd.SetIndicator(indic,0)
            self.lcd.BlinkOrBeep(0,0)
        elif soft.state=="sent":
            self.lcd.SetIndicator(indic,0)
            self.lcd.BlinkOrBeep(0,0)            
        
        
        