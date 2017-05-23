from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever

import Tracker
import Sequencer
import User


if __name__ == '__main__':

    set_context()

    #User Host
    h = create_host('http://127.0.0.1:1242')
    user = h.spawn("user3", User.User)

    #Tracker Host
    host = h.lookup_url('http://127.0.0.1:1220', Host)
    tracker = host.lookup_url('http://127.0.0.1:1220/TrackerID', Tracker.Tracker)
    
    user.joinTracker(tracker,h)

    #Sequencer Host
    host2 = h.lookup_url('http://127.0.0.1:1230', Host)
    sequencer = host2.lookup_url('http://127.0.0.1:1230/SequencerID', Sequencer.Sequencer)

    #user.multicast("SD",tracker,sequencer)
    user.multicastLamport("SD",tracker,sequencer)
    
    sleep(60)
    #user.process_msg()
    user.process_msg_Lamport()

    sleep(1)
    serve_forever()