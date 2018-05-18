# This is a logger for the Getnet API development enviroment.
# by Cesar Cara

import sched, time, datetime, base64, zlib, json, pycurl
from StringIO import StringIO
from collections import OrderedDict

client_id = "45bd882c-8321-42e1-ac53-feb8aaf071ea"
client_secret = "ff491be0-fee7-4890-8c6a-7df85ac1a41e"
seller_id = "d3e530cb-6c4f-465d-87a2-290db7e701a5"

def openJson(file_name):
	data = json.load(open(file_name), object_pairs_hook=OrderedDict)
	return data

def isGzip(header):
	header = header.split('\n')
	if 'Content-Encoding: gzip\r' in header:
		return True
	return False

def is200(header):
	header = header.split('\n')
	if 'HTTP/1.1 200 OK\r' in header:
		return True
	return False

def log(file_name, data):
	file = open(file_name,'a')

	if is200(data[0]):
		file.close()
		return

	file.write("\n\n==========================================================\n")
	file.write(str(datetime.datetime.now()))
	file.write("\n===========================\n")
	file.write("\n")
	file.write(data[0])
	file.write(data[1])

	file.close()
	return

class getnet():
	"""docstring for getnet"""
	def __init__(self, url):
		self.url = url
		self.auth_token = 'not received'
		self.number_token = 'not received'

	def insertNumberToken(self, data):
		if 'number_token' in data:
			for key in data.keys():
					if key == 'number_token':
						data[key] = self.number_token
						pass
			return data

		data['credit']['card']['number_token'] = self.number_token
		return data

	def authenticate(self, client_id, client_secret):
		encodedB64 = base64.b64encode(client_id + ':' + client_secret)

		curlBuffer = StringIO()
		headerBuffer = StringIO()
		
		try:
			c = pycurl.Curl()
			c.setopt(c.URL, self.url + '/auth/oauth/v2/token')
			c.setopt(c.HTTPHEADER, ["Authorization: Basic {}".format(encodedB64), 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8'])
			c.setopt(c.WRITEHEADER, headerBuffer)
			c.setopt(c.WRITEDATA, curlBuffer)
			c.setopt(c.POSTFIELDS, 'scope=oob&grant_type=client_credentials')
			c.perform()
			c.close()
			
		except ValueError:
			print "Problem runing curl"

		self.auth_token = json.loads(curlBuffer.getvalue())['access_token']
		curlBuffer.close()
		headerBuffer.close()
		pass

	def renewCardToken(self):
		curlBuffer = StringIO()
		headerBuffer = StringIO()
		
		try:
			c = pycurl.Curl()
			c.setopt(pycurl.URL, self.url + '/v1/tokens/card')
			c.setopt(pycurl.HTTPHEADER, ["content-type: application/json", "Authorization: Bearer {}".format(self.auth_token)])
			c.setopt(c.WRITEHEADER, headerBuffer)
			c.setopt(c.WRITEDATA, curlBuffer)
			c.setopt(pycurl.POSTFIELDS, '{"card_number": "5155901222280001"}')
			c.perform()
			c.close()
			
		except ValueError:
			print "Problem runing curl"

		if isGzip(headerBuffer.getvalue()):
			decompressed = zlib.decompressobj(16+zlib.MAX_WBITS)
			self.number_token = json.loads(decompressed.decompress(curlBuffer.getvalue()))['number_token']

		curlBuffer.close()
		headerBuffer.close()
		pass


	def post(self, endpoint, payload):
		payload = json.dumps(self.insertNumberToken(payload))

		dataBuffer = StringIO()
		headerBuffer = StringIO()

		try:
			c = pycurl.Curl()
			c.setopt(pycurl.URL, self.url + endpoint)
			c.setopt(pycurl.HTTPHEADER, ["content-type: application/json", "Authorization: Bearer {}".format(self.auth_token)])
			c.setopt(c.WRITEHEADER, headerBuffer)
			c.setopt(c.WRITEDATA, dataBuffer)
			c.setopt(pycurl.POSTFIELDS, payload)
			c.perform()
			c.close()
			
		except ValueError:
			print "Problem runing curl"

		header = headerBuffer.getvalue()

		if isGzip(headerBuffer.getvalue()):
			response = zlib.decompressobj(16+zlib.MAX_WBITS)
			dataBuffer.close()
			headerBuffer.close()
			return header, response

		response = dataBuffer.getvalue()
		dataBuffer.close()
		headerBuffer.close()
		return header, response

api = getnet('https://api-homologacao.getnet.com.br')
s = sched.scheduler(time.time, time.sleep)

def touchGetnet(sc): 
	api.authenticate(client_id, client_secret)
	api.renewCardToken()
	log('API_log', api.post('/v1/cards/verification', openJson('card_verify.json')))
	api.renewCardToken()
	log('API_log', api.post('/v1/payments/credit', openJson('credit.json')))
	s.enter(150, 1, touchGetnet, (sc,))

s.enter(5, 1, touchGetnet, (s,))
s.run()
