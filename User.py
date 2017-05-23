from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever
from random import randint

import Tracker
import Sequencer
import User

class User(object):

    _tell = ["multicast","receive","process_msg","multicastLamport","receiveLamport","reciveACK","process_msg_Lamport"]  #asincron
    _ask = ["joinTracker"]   #sincron
    _ref = ["joinTracker","multicast","multicastLamport","receiveLamport","reciveACK"]

    def __init__(self):
        self.timeStamp = 0
        self.recivedMessages = {}
        self.recivedMessagesLamport = []
        self.queueMessages = {}
        self.messagesACKs = []
        self.members = {}
        self.value = 0

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




    ###################################################################################


    def multicastLamport(self,message,tracker,sequencer):

        sleep(randint(1,10))
        self.timeStamp = self.timeStamp + 1
        self.members = tracker.get_members()
        print "MESSAGE TO SEND: " + str(message)

        for member in self.members:
            sleep(randint(1,10))
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)
            user.receiveLamport(message,self.timeStamp) 


    def reciveACK(self,message):
        #print self.queueMessages

        if message not in self.queueMessages:
            self.queueMessages.update({message:1})
            print "ACKS_value: " + message + ": " + str(1)
        else:
            self.value = self.queueMessages.get(message)
            self.value = self.value + 1
            self.queueMessages.update({message: self.value })
            print "ACKS_value: " + message + ": " + str(self.value)

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
        

    def receiveLamport(self, message, timeStampRecived):

        #guardar missatge amb el timeStamp local a la cua:
        if self.timeStamp < timeStampRecived:

            #self.queueMessages.update({message:self.timeStamp})
            print self.id + " : " + str(message)
            self.messagesACKs.append(message)

            self.timeStamp = timeStampRecived + 1 
            
        else:
            print self.id + " : " + str(message) 
            self.messagesACKs.append(message)

            self.timeStamp = self.timeStamp + 1


        #enviar ACK del missatge rebut:
        for member in self.members:
            sleep(0.1)
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)

            if member != self.url:
                user.reciveACK(message)


    def process_msg_Lamport(self):

        while len(self.messagesACKs) > 0:
            self.acks = self.queueMessages.get(self.messagesACKs[0])

            if self.acks >= len(self.members) - 1:
                self.recivedMessagesLamport.append(self.messagesACKs[0])
                self.messagesACKs.pop(0)


        print "Messages"
        print self.recivedMessagesLamport       








