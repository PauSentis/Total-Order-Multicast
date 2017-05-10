from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, serve_forever

class Tracker(object):

    _tell = ["join","leave"]  #asincron
    _ask = ["get_members"]   #sincron
    _ref = ["join","get_members"]

    def __init__(self):
        self.members = {}
        
    def join(self,userURL,host):

        #users are saved by their URL
        self.members.update({userURL:host})
        print "JOINED:"
        print userURL

    def leave(self,userURL):
        self.members.pop(userURL,None)

    def get_members(self):
        return self.members

if __name__ == '__main__':

    set_context()

    #Tracker Host
    h = create_host('http://127.0.0.1:1220')
    tracker = h.spawn("TrackerID" , Tracker)  
    serve_forever()


