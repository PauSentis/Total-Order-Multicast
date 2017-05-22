from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever
from random import randint

import Tracker
import Sequencer
import User

class User(object):

    _tell = ["multicast","receive","process_msg","multicastLamport","receiveLamport","reciveACK"]  #asincron
    _ask = ["joinTracker"]   #sincron
    _ref = ["joinTracker","multicast","multicastLamport","receiveLamport","reciveACK"]

    def __init__(self):
        self.timeStamp = 0
        self.recivedMessages = {}
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

        print "Messages"
        print self.recivedMessages

        '''
        allMessages = True
        keys = list(self.recivedMessages.keys())

        if len(keys) > 1: 
            maxTime = max(keys)

            for timeStamp in range(1,maxTime):
                if timeStamp not in keys:
                    allMessages = False

            if allMessages == True:        
                print self.recivedMessages
        '''

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

        #si es el primer cop que ens arriba un missatge els afegim:
        if message not in self.messagesACKs:
            self.messagesACKs.append(message)

        if message not in self.queueMessages:
            self.queueMessages.update({message:1})
            print "ACKS_value: " + message + ": " + str(1)
        else:
            self.value = self.queueMessages.get(message)

            self.queueMessages.update({message: (self.value + 1)})
            print "ACKS_value: " + message + ": " + str((self.value + 1))

        #comprobar missatge rebut si te tots els ACKS:
        if self.queueMessages.get(message) == len(self.members):
            if message == self.messagesACKs[0]:
                self.recivedMessages.update({message: ""})
                self.messagesACKs.pop(0)

        #comprovar si el primer de la llista ja te tots els ACKS:
        acks = self.queueMessages.get(self.messagesACKs[0])

        if acks >= len(self.members):
            self.recivedMessages.update({self.messagesACKs[0]: ""})
            self.messagesACKs.pop(0)
        

    def receiveLamport(self, message, timeStampRecived):

        #guardar missatge amb el timeStamp local a la cua:
        if self.timeStamp < timeStampRecived:

            self.queueMessages.update({message:self.timeStamp})
            print self.id + " : " + str(message)

            self.timeStamp = timeStampRecived + 1 
            
        else:
            self.queueMessages.update({message:self.timeStamp})
            print self.id + " : " + str(message) 

            self.timeStamp = self.timeStamp + 1


        #enviar ACK del missatge rebut:
        #print "members:" + str(self.members)
        for member in self.members:
            sleep(0.5)
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)

            user.reciveACK(message)











