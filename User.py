from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever
from random import randint

import Tracker
import Sequencer
import User

class User(object):

    _tell = ["multicast","receive","process_msg"]  #asincron
    _ask = ["joinTracker"]   #sincron
    _ref = ["joinTracker","multicast"]

    def __init__(self):
        self.timeStamp = 0
        self.recivedMessages = {}

   #peer send a message to the sequence:
    def multicast(self,message,tracker,sequencer):

        sleep(randint(1,10))
        self.timeStamp = sequencer.sequence()
        members = tracker.get_members()
        print "MESSAGE TO SEND: " + str(message)

        for member in members:
            sleep(randint(1,10))
            #get USER PROXY & HOST PROXY
            hostUser = members.get(member)
            user = hostUser.lookup_url(member, User)
            user.receive(message,self.timeStamp) 
        
    #sequencer use this method to deliver:
    def receive(self, message, timeStampRecived):

        self.recivedMessages.update({timeStampRecived:message})
        print self.id + " : " + str(message) + " -> " + str(timeStampRecived)

    #proces messages by stamp order:    
    def process_msg(self):

        allMessages = True
        keys = list(self.recivedMessages.keys())

        if len(keys) > 1: 
            maxTime = max(keys)

            for timeStamp in range(1,maxTime):
                if timeStamp not in keys:
                    allMessages = False

            if allMessages == True:        
                print self.recivedMessages

    def joinTracker(self,tracker,hostUser):
         tracker.join(self.url,hostUser)   
