from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever, Proxy
from random import randint

import Tracker
import Sequencer
import User

class User(object):

    _tell = ["multicast","receive","process_msg","multicastLamport","receiveLamport","reciveACK","process_msg_Lamport","setID","init_start","stop_interval","announce","newSequencer","bully"]  #asincron
    _ask = ["joinTracker","setHosts","setTracker","getMaxTimeStamp","getBullyOn"]   #sincron
    _ref = ["joinTracker","setTracker"]

    def __init__(self):
        self.timeStamp = 0
        self.recivedMessages = {}

        self.recivedMessagesLamport = []
        self.queueMessages = {}

        self.hostSelf = Host
        self.hostSequencer = Host
        self.sequencer = Proxy
        self.tracker = Proxy

        self.bullyON = False
        self.toSend = []

        self.members = {}
        self.value = 0
        self.identification = 0

    def setHosts(self, hostSelf, hostSequencer):
        self.hostSelf = hostSelf
        self.hostSequencer = hostSequencer

        #This if is for testing bully with user5
        if not self.identification == 5:
            self.sequencer = self.hostSequencer.lookup_url('http://127.0.0.1:1230/SequencerID', Sequencer.Sequencer)

    def setTracker(self, tracker):
        self.tracker = tracker


    def bully(self, message):
        self.bullyON = True
        election = True

        usersProxies = []

        print self.id+" on bully"

        for member in self.members:
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)
            usersProxies.append(user)
            if user != self.proxy:
                if user.getBullyOn():
                    if  self.identification < int(member[26:]):
                        election = False
                        break

        if election:
            print self.id+": I'm create new Sequencer"
            s = "Sequencer"+str(randint(1,1000))
            h = create_host('http://127.0.0.1:1231')
            sequencer = h.spawn(s, Sequencer.Sequencer)

            timeStamps = []
            for member in usersProxies:
                if member != self.proxy:
                    try:
                        timeStamps.append(member.getMaxTimeStamp())
                    except:
                        pass
                else:
                    self.getMaxTimeStamp()

            time=max(timeStamps)
            sequencer.setTimeStamp(time)

            for member in self.members:
                hostUser = self.members.get(member)
                user = hostUser.lookup_url(member, User)
                user.newSequencer(s)


    def getMaxTimeStamp(self):
        if self.recivedMessages:
          return max(self.recivedMessages.keys(), key=int)
        else:
          return 0


    def newSequencer(self, s):
        host2 = self.hostSelf.lookup_url('http://127.0.0.1:1231', Host)
        self.sequencer = host2.lookup_url('http://127.0.0.1:1231/'+str(s), Sequencer.Sequencer)
        print self.id+' has new Sequencer'
        for message in self.toSend:
            self.multicast(message)
        self.toSend = []


    def getBullyOn(self):
        return self.bullyON


    def joinTracker(self,tracker,hostUser):
         tracker.join(self.url,hostUser)


    def setID(self,identification):
        self.identification = identification



   #peer send a message to the sequence:
    def multicast(self,message):

        sleep(randint(1,10)/10)
        self.members = self.tracker.get_members()
        try:
            self.timeStamp = self.sequencer.sequence()
            print self.id+" SEND: " + str(message)

            for member in self.members:
                sleep(randint(1,10)/10)
                #get USER PROXY & HOST PROXY
                hostUser = self.members.get(member)
                #print hostUser
                user = hostUser.lookup_url(member, User)
                user.receive(message,self.timeStamp)
        except:
            self.toSend.append(message)
            if not self.bullyON:
                trobat = False
                for member in self.members:
                    hostUser = self.members.get(member)
                    user = hostUser.lookup_url(member, User)
                    if user != self.proxy:
                        if user.getBullyOn():
                            trobat = True

                if not trobat:
                    self.bully(message)


    #sequencer use this method to deliver:
    def receive(self, message, timeStampRecived):
        self.recivedMessages.update({timeStampRecived:message})
        print self.id + " has recived: " + str(message) + " -> " + str(timeStampRecived)


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
            print 'Massages of '+self.id+' are: '+ str(self.recivedMessages)



    ###################################################################################



    def multicastLamport(self,message):

        #sleep(randint(1,10))
        self.timeStamp = self.timeStamp + 1

        self.members = self.tracker.get_members()
        print "MESSAGE TO SEND: " + str(message)

        for member in self.members:
            #sleep(randint(1,10))
            sleep(0.1)
            #get USER PROXY & HOST PROXY
            hostUser = self.members.get(member)
            user = hostUser.lookup_url(member, User)
            user.receiveLamport(message,self.timeStamp,self.identification,len(self.members))


    def receiveLamport(self, message, timeStampRecived, ide, total):
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


        self.members = self.tracker.get_members()
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


    def announce(self):
        self.tracker.announce(self.url,11)


    #INTERVALS:
    def init_start(self,hostPeer):
        self.peerAnounce = interval(hostPeer, 3, self.proxy, "announce")
        later(300, self.proxy, "stop_interval")


    def stop_interval(self):
        print self.id+": stopping interval"
        self.peerAnounce.set()
