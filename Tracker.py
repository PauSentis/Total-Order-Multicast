from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, serve_forever

class Tracker(object):

    _tell = ["join","leave","announce","trackerTimeCheck","init_start","stop_interval","init"]  #asincron
    _ask = ["get_members"]   #sincron
    _ref = ["join","get_members","announce"]


    def __init__(self):
        self.members = {}
        self.times = {}

    def join(self,userURL,host):

        #users are saved by their URL
        self.members.update({userURL:host})
        print "JOINED:"
        print userURL

    def leave(self,userURL):
        self.members.pop(userURL,None)

    def get_members(self):
        return self.members

    def announce(self,peer,time):
        print "AN: " + peer + " time: " + str(time)
        self.times.update({peer:time})

    def trackerTimeCheck(self):
        deadPeers = []

        for peer in self.members:
            #print peer +" TIME: " + str(self.times[peer])
            self.announce(peer,self.times[peer] - 1)

            if self.times[peer] < 1:

                hostUser = self.members[peer]

                #print peer
                #print hostUser
                #peerPrx = hostUser.lookup_url(peer, User)
                #peerPrx.stop_interval()

                deadPeers.append(peer)

        for peer in deadPeers:
            self.members.pop(peer)
            print "KIKED: " + peer

    #INTERVALS:
    def init_start(self):
        self.timeCheck = interval(h,1, self.proxy, "trackerTimeCheck")
        later(300, self.proxy, "stop_interval")

    def stop_interval(self):
        print "Tracker: stopping interval"
        self.timeCheck.set()

if __name__ == '__main__':

    set_context()

    #Tracker Host
    h = create_host('http://127.0.0.1:1220')
    tracker = h.spawn("TrackerID" , Tracker)

    tracker.init_start()

    serve_forever()
