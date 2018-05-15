# This is a logger for the Getnet API development enviroment.
# by Cesar Cara

import sched, time, base64, zlib, json, pycurl
from StringIO import StringIO

def openJsonFile(file_name):
	with open(file_name) as f:
		data = json.load(f)
	return data

class getnet():
	"""docstring for getnet"""
	def __init__(self, url):
		self.url = url
		self.auth_token = 'not received'
		self.number_token = 'not received'

	def insertNumberToken(self, data):
		data['number_token'] = self.number_token		
		return data

	def authenticate(self, client_id, client_secret):
		encodedB64 = base64.b64encode(client_id + ':' + client_secret)

		curlBuffer = StringIO()
		c = pycurl.Curl()
		c.setopt(c.URL, self.url + '/auth/oauth/v2/token')
		c.setopt(c.HTTPHEADER, ["Authorization: Basic {}".format(encodedB64), 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8'])
		c.setopt(c.WRITEDATA, curlBuffer)
		c.setopt(c.POSTFIELDS, 'scope=oob&grant_type=client_credentials')
		c.perform()
		c.close()

		self.auth_token = json.loads(curlBuffer.getvalue())['access_token']
		curlBuffer.close()

		pass

	def renewCardToken(self):
		curlBuffer = StringIO()
		c = pycurl.Curl()
		c.setopt(pycurl.URL, self.url + '/v1/tokens/card')
		c.setopt(pycurl.HTTPHEADER, ["content-type: application/json", "Authorization: Bearer {}".format(self.auth_token)])
		c.setopt(c.WRITEDATA, curlBuffer)
		c.setopt(pycurl.POSTFIELDS, '{"card_number": "5155901222280001"}')
		c.perform()
		c.close()

		decompressed = zlib.decompressobj(16+zlib.MAX_WBITS)
		self.number_token = json.loads(decompressed.decompress(curlBuffer.getvalue()))['number_token']
		curlBuffer.close()

		pass


	def post(self, endpoint, payload):
		payload = json.dumps(self.insertNumberToken(payload))
		print payload

		curlBuffer = StringIO()
		c = pycurl.Curl()
		c.setopt(pycurl.URL, self.url + endpoint)
		c.setopt(pycurl.HTTPHEADER, ["content-type: application/json", "Authorization: Bearer {}".format(self.auth_token)])
		c.setopt(c.WRITEDATA, curlBuffer)
		c.setopt(pycurl.POSTFIELDS, payload)
		c.perform()
		c.close()

		response = curlBuffer.getvalue()
		curlBuffer.close()

		return response

client_id = "45bd882c-8321-42e1-ac53-feb8aaf071ea"
client_secret = "ff491be0-fee7-4890-8c6a-7df85ac1a41e"
seller_id = "d3e530cb-6c4f-465d-87a2-290db7e701a5"

api = getnet('https://api-homologacao.getnet.com.br')
s = sched.scheduler(time.time, time.sleep)

def touchGetnet(sc): 
	print "Doing stuff..."
	api.authenticate(client_id, client_secret)
	api.renewCardToken()
	print api.post('/v1/cards/verification', openJsonFile('card_verify.json'))
	api.renewCardToken()
	print api.post('/v1/payments/credit', openJsonFile('credit.json'))
	s.enter(10, 1, touchGetnet, (sc,))

s.enter(5, 1, touchGetnet, (s,))
s.run()
