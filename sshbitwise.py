import configparser
import subprocess
import multiprocessing
import time
import os
import json

bg=''
G = bg+'\033[32m'
O = bg+'\033[33m'
GR = bg+'\033[37m'
R = bg+'\033[31m'


def main():
	
	os.system("echo -----------------logs--------------------------------- > logs.txt")
	jsondata = {
		"mode" : '',
			"payload" : '',
				"proxy" : '',
					"sni" : "",
	  } 

	os.system('cls')
	print('---------------------------------------------------------------')
	jsondata["mode"] = confParse()['mode']['connection_mode']	
	jsondata["payload"] = confParse()['config']['payload'] 
	jsondata["proxy"] = confParse()['config']['proxyip'] +':' +confParse()['config']['proxyport']
	jsondata["sni"] = confParse()['sni']['server_name']

	if jsondata["mode"] == '0':
		print( f'{O}Direct SSH{GR}')

	if jsondata["mode"] == '2':
		print(f'{O}SNI : {GR} {jsondata["sni"]}')

	if jsondata["mode"] in ['1','3']:
		print(f'{O}sending payload :\n{GR} {jsondata["payload"]}\n')
		#if len(jsondata["proxy"].split(':')[1]) > 1:
		print(f'{O}proxy :{GR} ', jsondata["proxy"] if len(jsondata["proxy"].split(':')[1]) > 1 else None,end='\n\n')

		print(f'{O}SSL/TLS :{GR}', jsondata["sni"] if jsondata["mode"] =='3' else None)
	
	threadServ = multiprocessing.Process(target=ServRun)
	threadServ.start()

	sshStart = multiprocessing.Process(target=sshrun).start()
	
	return readlogs()
	
def readlogs():
	OneTimeOutput = []
	while True:
		try: 
			with open('logs.txt','r') as file:
				time.sleep(1)
				end = 0
				logs = file.readlines()
				for line in logs:
					if line not in OneTimeOutput:
						OneTimeOutput.append(line)
						print(line)
						if line.split(":")[-1].split("-")[0].strip()=='SSH':
							os.system("echo -----------------logs--------------------------------- > logs.txt")
							runProxifier()
							end +=1
							break
				if end:break
		except KeyboardInterrupt:
			return serviceManage()
	return serviceManage()

def killProcessid(target):
	
	findProcess = subprocess.Popen(['tasklist','|','findstr', target],shell=True,stdout= subprocess.PIPE,stderr=subprocess.STDOUT)
	for line in findProcess.stdout:
		pid = line.decode('utf-8','ignore').split()[1]
		killprocess = subprocess.Popen(['taskkill','/f','/pid',pid],shell=True,stdout= subprocess.PIPE,stderr=subprocess.STDOUT)
	return "Done"

def ServRun():
	#path = os.path.abspath(os.path.curdir)+'/lib'
	Serv_Cmd = subprocess.Popen(['python','tunnel.py','8888'] , shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				
def confParse():
	config = configparser.ConfigParser()
	try:
		config.read_file(open('settings.ini'))
	except Exception as e:
		pass
	return config

def sshrun():
	#ssh load settings
	ssh_server = confParse()['ssh']['host']  
	ssh_port = confParse()['ssh']['port']
	username = confParse()['ssh']['username']
	password = confParse()['ssh']['password']

	#local proxy 
	proxy_ip = '127.0.0.1'
	proxy_port = '8888'

	#run ssh command
	ssh_cmd = subprocess.Popen(( f'BvSsh.exe -host={ssh_server} -user={username} -pw={password} -port={ssh_port} -proxy=y -proxyType=HTTP -proxyServer=127.0.0.1 -proxyPort={proxy_port} -proxyFwding=y -proxyListIntf=127.0.0.1 -proxyListPort=1080 -loginOnStartup -reconnect=Always -reconnTimeout=2'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	
def runProxifier():
	proxify = subprocess.Popen(('"C:\\Program Files (x86)\\Proxifier\\Proxifier.exe" socks5profile.ppx '))

def serviceManage():
	try:
		index_input = int(input('1 - To Disconnect \n2 - To Reconnect \n3 - show logs\n choose op num: '))
		services = ["Proxifier","BvSsh.exe",'python']
		if index_input in [1,2] :
			services = [services[0:2] if index_input == 2 else services[:]][0]
			for ev in services: 
				killProcessid(ev)
		if index_input == 2 :	
			return main()
		if index_input == 3:
			readlogs()
		if index_input not in [1,2,3]:
			print('Operation number not listed')
			return serviceManage()
		
	except Exception as e:
		print(e)
		print('A number required ')
		return serviceManage()

		
if __name__=='__main__':
	main()
	
	
		

	
	

