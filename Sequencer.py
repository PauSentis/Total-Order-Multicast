from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever
from random import randint
import Tracker


class Sequencer(object):

    _tell = ["setTimeStamp"]  #asincron
    _ask = ["sequence"]   #sincron
    _ref = []


    def __init__(self):
        self.timeStamp = 0

    #Give timeStamp when request:
    def sequence(self):
        self.timeStamp = self.timeStamp + 1
        return self.timeStamp

    def setTimeStamp(self, time):
        self.timeStamp = time

if __name__ == '__main__':

    set_context()

    #Sequencer Host
    h = create_host('http://127.0.0.1:1230')
    sequencer = h.spawn("SequencerID", Sequencer)
    serve_forever()
