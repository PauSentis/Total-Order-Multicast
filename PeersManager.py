from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever


import Tracker
import Sequencer
import User

if __name__ == '__main__':

    set_context()

    messages = ["ARNAU", "PAU" , "SD", "TASK2"]
    users = 5
    usersProxies = []*users

    #User Host
    h = create_host('http://127.0.0.1:1240')

    #Tracker Host
    host = h.lookup_url('http://127.0.0.1:1220', Host)
    tracker = host.lookup_url('http://127.0.0.1:1220/TrackerID', Tracker.Tracker)

    #Sequencer Host
    host2 = h.lookup_url('http://127.0.0.1:1230', Host)
    sequencer = host2.lookup_url('http://127.0.0.1:1230/SequencerID', Sequencer.Sequencer)


    for val in range(1,users):
        sleep(0.1)
        user = h.spawn("user" + str(val), User.User)
        user.joinTracker(tracker,h)
        user.setID(val)
        usersProxies.append(user)
        user.init_start(tracker,h)
    
    for val in range(1,users):
        sleep(0.3)
        usersProxies[val-1].multicast(messages[val-1],tracker,sequencer)
        #usersProxies[val-1].multicastLamport(messages[val-1],tracker,sequencer)

    sleep(60)

    for user in usersProxies:
        sleep(0.1)

        user.process_msg()
        #user.process_msg_Lamport()
    
    sleep(1)

    serve_forever()