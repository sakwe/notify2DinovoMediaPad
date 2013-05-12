#!/usr/bin/python

# This part contains the listeners 
#---------------------------------

from displayers import *
from email.header import decode_header

#------------------------------------
# OS constants for sofware management
#------------------------------------

# Banshee
URI_FOR_BANSHEE = "org.bansheeproject.Banshee"
URI_FOR_BANSHEE_PLAYER = "org.bansheeproject.Banshee.PlayerEngine"
PATH_TO_BANSHEE_PLAYER = "/org/bansheeproject/Banshee/PlayerEngine"
EVENT_FOR_BANSHEE_STATE = "StateChanged"

# Rhythmbox via MPRIS2
URI_MPRIS_FOR_RHYTHMBOX = 'org.mpris.MediaPlayer2.rhythmbox'
PATH_FOR_MPRIS_MEDIAPLAYER = '/org/mpris/MediaPlayer2'
URI_MPRIS_FOR_PLAYER = 'org.mpris.MediaPlayer2.Player'
URI_DBUS_PROP = 'org.freedesktop.DBus.Properties'
EVENT_FOR_RHYTHMBOX_STATE = "PropertiesChanged"

# Totem
URI_FOR_TOTEM = "org.gnome.Totem"
URI_FOR_TOTEM_PLAYER = "org.gnome.Totem"
PATH_TO_TOTEM_PLAYER = "/org/gnome/Totem"
EVENT_FOR_TOTEM_STATE = "StatusChange"

# Skype
URI_FOR_SKYPE = "com.Skype.API"
PATH_TO_SKYPE = "/com/Skype"
URI_FOR_SKYPE_CLIENT = "com.Skype.API.Client"
PATH_TO_SKYPE_CLIENT = "/com/Skype/Client"
EVENT_FOR_SKYPE_STATE = "Notify"

# Evolution
URI_FOR_EVOLUTION = "org.gnome.Evolution"
URI_FOR_EVOLUTION_CLIENT = "org.gnome.evolution.mail.dbus.Signal"
PATH_TO_EVOLUTION_CLIENT = "/org/gnome/evolution"
EVENT_FOR_EVOLUTION_STATE = "Newmail"


#----------------------------------------
# Classes for working data representation
#----------------------------------------
class MediaData :     
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.album = ""
        self.lenght = 0
        self.position = 0
        
class MessageData :     
    def __init__(self):
        self.sender = ""
        self.message = ""


#----------------------------------------
# Main Class Model for software we listen
#----------------------------------------
class SoftwareListened() : 
       
    priorityGlobal = 0

    def __init__(self,session_bus):
        self.name = "unsupported software"        
        self.state = "undefined"
        self.type = "undefined" 
        self.state = "undefined"
        self.mediapad = None
        self.app = None
        self.prox = None
        self.loopNumber = 0
        self.priority = 0
        self.session_bus = session_bus
        self.setting()
    
    def setting(self) :
        self.data = None
              
    def listen(self):
        print 'Can\' listen ' + self.name
     
    def ownerChanged(self,new_owner):
        if new_owner == '':
            self.app = None
            self.statusChanged("stopped")
        else:
            self.listen()
            self.statusChanged("waiting")
            
    def statusChanged(self,status):
        self.loopNumber = 0
        self.state = status
        self.getData()
        # If the software is a mediaplayer playing, set it to the highest priority
        if self.state == "playing" : 
            SoftwareListened.priorityGlobal = SoftwareListened.priorityGlobal + 1
            self.priority = SoftwareListened.priorityGlobal
        if self.mediapad != None :
            self.writeData()  
        # If the software is a message 
        print self.name.title() + " state changed: %s" % self.state.title() 
          
    def writeData(self):
        if self.mediapad != None : 
            self.mediapad.writeData(self)
        else : 
            print "Error : Mediapad can't display " + self.state.title() + " for " + self.name.title() 
        
#-----------------------------------------------
# SoftwareListened overwrite for Banshee support        
#-----------------------------------------------
class BansheeListened(SoftwareListened):

    def setting(self):
        self.name = "banshee"
        self.type = "media"
        self.data =  MediaData()
        self.session_bus.watch_name_owner(URI_FOR_BANSHEE,self.ownerChanged)
                  
    def listen(self):
        self.app = self.session_bus.get_object(URI_FOR_BANSHEE, PATH_TO_BANSHEE_PLAYER)
        self.session_bus.add_signal_receiver(self.statusChanged, dbus_interface=URI_FOR_BANSHEE_PLAYER,signal_name=EVENT_FOR_BANSHEE_STATE)
               
    def getData(self):
        if self.app != None : 
            try :
                self.state = self.app.GetCurrentState()
                currentTrack = self.app.GetCurrentTrack()
                if currentTrack.has_key(u'album-artist'):
                    self.data.artist = str(currentTrack[u'album-artist'])
                if currentTrack.has_key(u'album'):
                    self.data.album = str(currentTrack[u'album'])
                if currentTrack.has_key(u'name'):
                    self.data.title = str(currentTrack[u'name'])
                self.data.position = self.app.GetPosition()    
                self.data.lenght = self.app.GetLength()
            except : 
                self.state = "waiting"            
                print "Error with DBUS Banshee... Will try next loop" 

#-------------------------------------------------
# SoftwareListened overwrite for Rhythmbox support        
#-------------------------------------------------
class RhythmboxListened(SoftwareListened):

    def setting(self):
        self.name = "rhythmbox"
        self.type = "media"
        self.data =  MediaData()
        self.data.uri = None
        self.session_bus.watch_name_owner(URI_MPRIS_FOR_RHYTHMBOX,self.ownerChanged)
                    
    def listen(self):
        import dbus
        self.prox = self.session_bus.get_object(URI_MPRIS_FOR_RHYTHMBOX, PATH_FOR_MPRIS_MEDIAPLAYER)
        self.app = dbus.Interface(self.prox, URI_DBUS_PROP)
        self.app.connect_to_signal(EVENT_FOR_RHYTHMBOX_STATE,self.propertiesChanged)    
   
    def propertiesChanged(self,interface, changed_props, invalidated_props):
            self.state = self.app.Get(URI_MPRIS_FOR_PLAYER, 'PlaybackStatus').lower()
            self.statusChanged(self.state)
                
    def getData(self):
        if self.app != None : 
            try :
                self.state = self.app.Get(URI_MPRIS_FOR_PLAYER, 'PlaybackStatus').lower()
                song = self.app.Get(URI_MPRIS_FOR_PLAYER, 'Metadata')
                if song.has_key(u'xesam:albumArtist'):
                    self.data.artist = str(song[u'xesam:albumArtist'])
                if song.has_key(u'xesam:album'):
                    self.data.album = str(song[u'xesam:album'])
                if song.has_key(u'xesam:title'):
                    self.data.title = str(song[u'xesam:title'])
                if song.has_key(u'mpris:length'):
                    self.data.lenght = int(song[u'mpris:length']) / 1000
                try :  
                    self.data.position = int(self.app.Get(URI_MPRIS_FOR_PLAYER, 'Position')) / 1000
                except : 
                    self.data.position = self.data.lenght
            except : 
                self.state = "waiting"            
                print "Error with DBUS Rhythmbox via MPRIS... Will try next loop" 
 

#-----------------------------------------------
# SoftwareListened overwrite for Totem support        
#-----------------------------------------------
class TotemListened(SoftwareListened):

    def setting(self):
        self.name = "totem"
        self.type = "media"
        self.data =  MediaData()
        self.status = ["playing","paused","stopped"]
        self.session_bus.watch_name_owner("org.mpris.Totem",self.ownerChanged)
                  
    def listen(self):
        import dbus
        self.prox = self.session_bus.get_object("org.mpris.Totem", "/Player")
        self.app =  dbus.Interface(self.prox, dbus_interface="org.freedesktop.MediaPlayer")
        self.session_bus.add_signal_receiver(self.propertiesChanged, dbus_interface="org.freedesktop.MediaPlayer",signal_name=EVENT_FOR_TOTEM_STATE)  
                
    def propertiesChanged(self,status):
        if self.app != None : 
            self.state = self.status[self.app.GetStatus()[0]]
            self.statusChanged(self.state)
    
    def getData(self):
        try : 
            if self.app != None : 
                self.state = self.status[self.app.GetStatus()[0]]
                currentTrack = self.app.GetMetadata()
                if currentTrack.has_key('artist'):
                    self.data.artist = str(currentTrack['artist'])
                if currentTrack.has_key('album'):
                    self.data.album = str(currentTrack['album'])
                if currentTrack.has_key('title'):
                    self.data.title = str(currentTrack['title'])
                if currentTrack.has_key('time') :
                    if str(currentTrack['time']) != '' :
                        self.data.lenght = int(currentTrack['time'])
                    else : 
                        self.data.lenght = 0
                self.data.position = int(self.app.PositionGet())
            else :
                self.app = None                 
        except : 
            self.app = None
            self.state = "waiting"
            print "Error with DBUS Totem via MPRIS... Will try next loop" 

    
#---------------------------------------------
# SoftwareListened overwrite for Skype support        
#---------------------------------------------
class SkypeEvents:
    def __init__(self,soft):
        self.soft = soft    
    def MessageStatus(self,mess,status):
        self.soft.statusChanged(status.lower())

class SkypeListened(SoftwareListened):

    def setting(self):
        import Skype4Py 
        self.name = "skype"
        self.type = "message"
        self.data =  MessageData()
        self.session_bus.watch_name_owner(URI_FOR_SKYPE,self.ownerChanged)
        self.event_skype = Skype4Py.Skype(Events=SkypeEvents(self))
        self.appev = self.event_skype.Application('Skype4Py')
                    
    def listen(self):
        import Skype4Py
        time.sleep(2)
        try : 
            self.event_skype = Skype4Py.Skype(Events=SkypeEvents(self))
            self.event_skype.Attach()
            self.appev = self.event_skype.Application('Skype4Py')
            self.appev.Create()     
        except : 
            print "Error while listening for Skype... Waiting 2 sec and try again."
            time.sleep(2)
            self.listen()
              
    def getData(self):
        self.data.message = self.data.message # TODO : Refresh data from skype


#-------------------------------------------------
# SoftwareListened overwrite for Evolution support        
#-------------------------------------------------
class EvolutionListened(SoftwareListened):

    def setting(self):
        self.name = "evolution"
        self.type = "mail"
        self.data =  MessageData()
        self.session_bus.watch_name_owner(URI_FOR_EVOLUTION,self.ownerChanged)
            
    def listen(self):
        self.session_bus.add_signal_receiver(self.on_evolution_new_mail, dbus_interface=URI_FOR_EVOLUTION_CLIENT,signal_name=EVENT_FOR_EVOLUTION_STATE) 
    
    def on_evolution_new_mail(self,path, folder, foo, uid, sender, subject):
        self.statusChanged("received")
        self.data.sender = sender
        self.data.message = subject
    
    def getData(self):
        self.data.message = self.data.message # TODO : Refresh data from evolution
              
                   
            

