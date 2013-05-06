----------------------------------------------------------------------------------------------
 Script to interface LCD display of the Logitech diNovo MediaPad (in Gnome environment)
 Thanks to T.Hentenaar to make the game possible 
----------------------------------------------------------------------------------------------

 - Depends on https://github.com/thentenaar/bluez-dinovo
     (Adding support to BlueZ for the Logitech diNovo Mediapad)

 - Use the included Skype4Py python library to interface with Skype

 - /!\ Rhythmbox COMPATIBILITY : Works actually only with Gnome3 via MPRIS2
        (org.gnome.Rhythmbox3/org.mpris.MediaPlayer2.rhythmbox)

----------------------------------------------------------------------------------------------
 - plugin.py       : contains the main loop and manage "out of events" displaying and decisions
 - listeners.py    : contains the class witch listen to open/close softwares events (change_owner)
                   and "change status event" of these softwares while running
 - displayers.py   : contains the class that connect to the LCD and manage displaying of datas
                   from softwares listened
----------------------------------------------------------------------------------------------
 - Actualy support : 
     - Banshee to display "Now playing" informations
     - Rhythmbox to display "Now playing" informations
     - Totem to display "Now playing" informations
     - Skype sound alert if message received and LED display ON
     - Evolution sound alert if mail received and LED display ON
     - Mediaplayers priority : Support display for "concurrent" players playing in the session.
       The player take priority to others every "playing event" on it. 
       It will be the one displayed on the LCD
----------------------------------------------------------------------------------------------
