import time
import socket 
import configparser
import re
import sys
import user_agent

bg=''
G = bg+'\033[32m'
O = bg+'\033[33m'
GR = bg+'\033[37m'
R = bg+'\033[31m'



class injector():
	def __init__(self):
		pass

	def conf(self):
		config = configparser.ConfigParser()
		try:
			config.read_file(open('settings.ini'))
		except Exception as e:
			self.logs(e)
		return config

	def getpayload(self,config):
		payload = config['config']['payload']
		return payload 

	def proxy(self,config):
	    proxyhost = config['config']['proxyip']
	    proxyport = int(config['config']['proxyport'])
	    return [proxyhost,proxyport]
	def conn_mode(self,config):
		mode = config['mode']['connection_mode']
		return mode

	def auto_rep(self,config):
		result = config['config']['auto_replace']
		return result
	


	def payloadformating(self,payload,**kwargs):

		host, port = kwargs["kwargs"]["SSH"].split(':')[0],kwargs["kwargs"]["SSH"].split(':')[1]
		proxy_ip,proxy_port = kwargs["kwargs"]["PROXY"].split(':')[0],kwargs["kwargs"]["PROXY"].split(':')[1]
		User_Agent = user_agent.generate_user_agent()
		
		payload = payload.replace('[crlf]','\r\n')
		payload = payload.replace('[crlf*2]','\r\n\r\n')
		payload = payload.replace('[cr]','\r')
		payload = payload.replace('[lf]','\n')
		payload = payload.replace('[protocol]','HTTP/1.0')
		payload = payload.replace('[ua]',User_Agent)  
		payload = payload.replace('[raw]',f'CONNECT {kwargs["kwargs"]["SSH"]}  HTTP/1.0\r\n\r\n')
		payload = payload.replace('[real_raw]',f'CONNECT {kwargs["kwargs"]["SSH"]} HTTP/1.0\r\n\r\n') 
		payload = payload.replace('[netData]',f'CONNECT {kwargs["kwargs"]["SSH"]} HTTP/1.0')
		payload = payload.replace('[realData]',f'CONNECT {kwargs["kwargs"]["SSH"]} HTTP/1.0')               	
		payload = payload.replace('[split_delay]','[delay_split]')
		payload = payload.replace('[split_instant]','[instant_split]')
		payload = payload.replace('[method]','CONNECT')
		payload = payload.replace('[lfcr]','\n\r')
		payload = payload.replace('[host_port]',host+':'+port)
		payload = payload.replace('[host]',host)
		payload = payload.replace('[port]',port)
		payload = payload.replace('[IP]',host)
		payload = payload.replace('[PORT]',port)
		payload = payload.replace('[proxy]',kwargs["kwargs"]["PROXY"])
		payload = payload.replace('[ssh]',kwargs["kwargs"]["PROXY"])
		payload = payload.replace('[auth]','')
		payload = payload.replace('[split]' ,'=1.0=')
		payload = payload.replace('[delay_split]'  ,'=1.5=')
		payload = payload.replace('[instant_split]','=0.0=')
		return payload

	def connection(self,client, server,**kwargs):
	        if int(self.conn_mode(self.conf())) == 0:
	        	return self.get_resp(server=server,client=client)
	        			       
	        else:
	        	payloads = self.payloadformating(self.getpayload(self.conf()),**kwargs).split('=')
	        	
	        for payload in payloads:
	              if payload in ['1.0','1.5','0.0'] :
	                time.sleep(float(payload))
	              else:
	                self.logs(f'{O} sending payload : {payload.encode()}{GR}')
	                server.send(payload.encode())
	        return self.get_resp(server=server,client=client)

	def get_resp(self,server,client) :
		packet = server.recv(1024)
		status = packet.decode('utf-8','ignore').split('\r\n')[0]
		serverHandshakeResponse = status if status.split('-')[0]=='SSH' else False
		if serverHandshakeResponse:
			self.logs(f'response : {serverHandshakeResponse}')
			client.send(packet)
			return True
		else:
			if re.match(r'HTTP/\d(\.\d)? \d\d\d ',status):
				self.logs(f'response : {status}')
				client.send(b'HTTP/1.1 200 Connection established\r\n\r\n')
				return self.get_resp(server,client)

	def logs(self,log):
		logtime = str(time.ctime()).split()[3]
		logfile = open('logs.txt','a')
		logfile.write(f'[{logtime}] : {str(log)}\n')
