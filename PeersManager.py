from pyactor.context import set_context, create_host, sleep, shutdown, interval, later, Host, serve_forever


import Tracker
import Sequencer
import User


if __name__ == '__main__':

    set_context()

    messages = {1:["ARNAU","H","E","L","L","O"], 2:["PAU","W","O","R","L","D"] , 3:["SD","Lamport oh yeah!"], 4:["TASK2"]}
    users = 5
    usersProxies = []*users

    #User Host
    h = create_host('http://127.0.0.1:1240')

    #Tracker Host
    host = h.lookup_url('http://127.0.0.1:1220', Host)
    tracker = host.lookup_url('http://127.0.0.1:1220/TrackerID', Tracker.Tracker)

    #Sequencer Host
    host2 = h.lookup_url('http://127.0.0.1:1230', Host)



    for val in range(1,users):
        sleep(0.1)
        user = h.spawn("user" + str(val), User.User)
        user.joinTracker(tracker,h)
        user.setID(val)
        user.setHosts(h,host2)
        user.setTracker(tracker)
        usersProxies.append(user)
        user.init_start(h)

    for val in range(1,users):
        sleep(0.3)
        ms = messages.get(val)
        for m in ms:
            usersProxies[val-1].multicast(m)
            #usersProxies[val-1].multicastLamport(m)

    sleep(30)

    for user in usersProxies:
        sleep(0.1)

        user.process_msg()
        #user.process_msg_Lamport()

    sleep(1)

    serve_forever()
