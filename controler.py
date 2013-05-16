#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

TRAY_TOOLTIP = 'MediaPad control'
TRAY_ICON = 'images/lcd.png'

import dbus,gobject,sys
from gobject import *
from dbus.mainloop.glib import DBusGMainLoop
from listeners import *
from displayers import *
from monitor import MediapadMonitor

# Create the threaded mainloop
DBusGMainLoop(set_as_default=True)
mainloop = gobject.MainLoop()
gobject.threads_init()
context = mainloop.get_context()

import glib
glib.set_application_name(TRAY_TOOLTIP)

# The global MediapadMonitor
global monitored
monitored = None

def create_menu_item(menu, label, func=None,icon=''):
    item = wx.MenuItem(menu, -1, label)
    if icon != '':
        item.SetBitmap(wx.Bitmap(icon))
    if func != None:
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class SysTrayMonitor(wx.TaskBarIcon):
  
    def __init__(self,frame):      
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        icon = wx.Icon(TRAY_ICON,wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon, str(TRAY_TOOLTIP))        
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.monitor = None
        self.monitoredItems = []
        
    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        self.menu.SetTitle(TRAY_TOOLTIP)        
        if (monitored == None):
            create_menu_item(self.menu, 'Start monitor', self.on_start,'images/run.png')
        else : 
            for soft in monitored.softwares :                
                item = self.menu.AppendCheckItem(soft.id,str(soft.name.title() +  " is " + soft.state))
                self.menu.Check(item.GetId(),soft.listening)
                self.menu.Bind(wx.EVT_MENU, self.on_check_software,id=item.GetId())
            create_menu_item(self.menu, 'Stop monitor', self.on_stop,'images/stop.png')
        self.menu.AppendSeparator()
        create_menu_item(self.menu, 'Exit', self.on_exit,'images/exit.png')        
        return self.menu   
    
    def on_check_software(self,event):
        for soft in monitored.softwares :
            if soft.id ==  event.GetId():
                if soft.listening == True : 
                    soft.unlisten() 
                else:
                    soft.listen()

    def on_left_down(self, event):                
        print 'This is the Dinovo MediaPad systray'

    def on_start(self, event): 
        if monitored == None :
            from threading import Thread  
            import dbus  
            # Connect to the system bus and session bus
            ses_bus = dbus.SessionBus()
            sys_bus = dbus.SystemBus()  
            try :  
                # Instantiate the mediapad     
                mediapad = MediaPad(sys_bus)            
            except : 
                print "Error while running the mediapad"
         
            try : 
                # Load all listenable softwares in the session
                softwares = {BansheeListened(ses_bus),
                             SkypeListened(ses_bus),
                             RhythmboxListened(ses_bus),
                             TotemListened(ses_bus),
                             EvolutionListened(ses_bus)}
            except : 
                print "Error while running the softwares" 
                
            try :     
                self.monitoring = Thread(target=run_monitor, args=(mediapad,softwares))
                self.monitoring.start()
                #self.trayMon = Thread(target=run_traymonitor, args=())
                #self.trayMon.start()
            except : 
                print "Error while running the monitor"
                
    def on_stop(self, event):
        global monitored
        if monitored != None :  
            monitored.stop()
            monitored = None
                
    def on_exit(self, event):
        self.on_stop(None)
        wx.CallAfter(self.Destroy)

def run_monitor(mediapad,softwares):
    global monitored           
    try : 
        print "Start monitoring..."
        # load the global monitor
        monitored = MediapadMonitor(mediapad,softwares)
        # run monitoring software/displaying to LCD
        monitored.run()    
    except : 
        print "Error while running the monitor"

def run_traymonitor():
    global monitored,menu
    while monitored != None : 
        monitored.monitoredItems = []
        for soft in monitored.softwares : 
            monitored.monitoredItems.Append(item) 
        time.sleep(1)
            
class TaskBarMonitor(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size = (1, 1),
            style=wx.FRAME_NO_TASKBAR|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.tbicon = SysTrayMonitor(self)
        self.Show(True)

class AppMonitor(wx.App):
    def OnInit(self):
        self.SetAppName(TRAY_TOOLTIP)
        frame = TaskBarMonitor(None, -1, TRAY_TOOLTIP)
        frame.SetName(TRAY_TOOLTIP)
        frame.SetTitle(TRAY_TOOLTIP)
        frame.Center(wx.BOTH)
        frame.Show(True)        
        return True

def main(argv=None):
    if argv is None:
        argv = sys.argv
    app = AppMonitor(0)
    app.MainLoop()


if __name__ == '__main__':
    main()    
    mainloop.run()
