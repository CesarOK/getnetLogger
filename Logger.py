# This is a logger for the Getnet API development enviroment.
# by Cesar Cara pycurl

import sched, time, base64, zlib, json
from StringIO import StringIO

ClientID = "45bd882c-8321-42e1-ac53-feb8aaf071ea"
ClientSecret = "ff491be0-fee7-4890-8c6a-7df85ac1a41e"
encodedB64 = base64.b64encode(ClientID + ':' + ClientSecret)

s = sched.scheduler(time.time, time.sleep)
def touchGetnet(sc): 
	print "Doing stuff..."
	# getnet.authenticate()
	# getnet.touch(microService)
	s.enter(5, 1, touchGetnet, (sc,))

s.enter(5, 1, touchGetnet, (s,))
s.run()
