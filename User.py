from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever
from random import randint

import Tracker
import Sequencer
import User

class User(object):

    _tell = ["multicast","receive","process_msg","multicastLamport","receiveLamport","reciveACK","process_msg_Lamport","setID","init_start","stop_interval","announce"]  #asincron
    _ask = ["joinTracker"]   #sincron
    _ref = ["joinTracker","multicast","multicastLamport","receiveLamport","reciveACK","init_start","announce","stop_interval"]

    def __init__(self):
        self.timeStamp = 0
        self.recivedMessages = {}

        self.recivedMessagesLamport = []
        self.queueMessages = {}

        self.members = {}
        self.value = 0
        self.identification = 0



   #peer send a message to the sequence:
    def multicast(self,message,tracker,sequencer):

        sleep(randint(1,10))
        self.timeStamp = sequencer.sequence()
        self.members = tracker.get_members()
        print "MESSAGE TO SEND: " + str(message)

        for member in self.members:
            sleep(randint(1,10))
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            #print hostUser
            user = hostUser.lookup_url(member, User)
            user.receive(message,self.timeStamp) 
        
    #sequencer use this method to deliver:
    def receive(self, message, timeStampRecived):

        self.recivedMessages.update({timeStampRecived:message})
        print self.id + " : " + str(message) + " -> " + str(timeStampRecived)

    #proces messages by stamp order:    
    def process_msg(self):

        allMessages = False

        while allMessages == False:  
            keys = list(self.recivedMessages.keys()) 
            allMessages = True
            
            if len(keys) > 1: 
                maxTime = max(keys)

                for timeStamp in range(1,maxTime):
                    if timeStamp not in keys:
                        allMessages = False

        if allMessages == True:        
            print self.recivedMessages


    def joinTracker(self,tracker,hostUser):
         tracker.join(self.url,hostUser)   


    ###################################################################################


    def setID(self,identification):
        self.identification = identification


    def multicastLamport(self,message,tracker,sequencer):

        #sleep(randint(1,10))
        self.timeStamp = self.timeStamp + 1

        self.members = tracker.get_members()
        print "MESSAGE TO SEND: " + str(message)

        for member in self.members:
            #sleep(randint(1,10))
            sleep(0.1)
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)
            user.receiveLamport(message,self.timeStamp,self.identification,len(self.members),tracker) 


    def receiveLamport(self, message, timeStampRecived, ide, total, tracker):

        print message + ":    " +  str(timeStampRecived) + ":" + str(ide)

        if not self.recivedMessages.get(timeStampRecived):
            self.values = [" "]*total 

            self.values[ide-1] = message
            self.recivedMessages.update({timeStampRecived : self.values})

        else:
            self.values = self.recivedMessages.get(timeStampRecived)
            self.values[ide-1] = message
            self.recivedMessages.update({timeStampRecived : self.values})

        if self.timeStamp < timeStampRecived:            
            self.timeStamp = (timeStampRecived + 1) 
            
        else:
            self.timeStamp = (self.timeStamp + 1)


        self.members = tracker.get_members()
        #enviar ACK del missatge rebut:
        for member in self.members:
            sleep(0.1)
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)

            if member != self.url:
                sleep(0.1)
                user.reciveACK(message)
        

    def reciveACK(self,message):

        
        #queueMessages -> per contar ACKs per missatge.
        if message not in self.queueMessages:
            self.queueMessages.update({message:1})
            print "ACKS_value: " + message + ": " + str(1)
        else:
            self.value = self.queueMessages.get(message)
            self.value = self.value + 1

            self.queueMessages.update({message: self.value})
            print "ACKS_value: " + message + ": " + str(self.value)

        '''
        #comprobar missatge rebut si te tots els ACKS:
        if self.queueMessages.get(message) >= len(self.members) - 1:
            if message == self.messagesACKs[0]:
                self.recivedMessagesLamport.append(message)
                self.messagesACKs.pop(0)
        else:       
        #comprovar si el primer de la llista ja te tots els ACKS:
            self.acks = self.queueMessages.get(self.messagesACKs[0])

            if self.acks >= len(self.members) - 1:
                self.recivedMessagesLamport.append(self.messagesACKs[0])
                self.messagesACKs.pop(0)
        '''

    def process_msg_Lamport(self):

        self.allMessagesQueue = []
        for keyTime in self.recivedMessages:
            for value in self.recivedMessages.get(keyTime):
                if value != " ":
                    self.allMessagesQueue.append(value)

        
        while len(self.allMessagesQueue) > 0:
            self.acks = self.queueMessages.get(self.allMessagesQueue[0])

            if self.acks >= len(self.members) - 1:
                self.recivedMessagesLamport.append(self.allMessagesQueue[0])
                self.allMessagesQueue.pop(0)

        print "Messages"
        print self.recivedMessagesLamport
    

    def announce(self,tracker):
        tracker.announce(self.url,11)

    #INTERVALS:
    def init_start(self,tracker,hostPeer):
        self.peerAnounce = interval(hostPeer, 3, self.proxy, "announce", tracker)   
        later(70, self.proxy, "stop_interval")

    def stop_interval(self):
        print self.id+": stopping interval"

        self.peerAnounce.set()



