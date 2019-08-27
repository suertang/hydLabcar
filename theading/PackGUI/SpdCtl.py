#########
import serial
import time

import threading
############




class SpdCtl:
	message=''
	def __init__(self,port='COM1',buand=9600):
		self.port=serial.Serial(port,buand,parity='O',timeout=1)
		if not self.port.isOpen():
			self.port.open()
		#mSerial=SpdCtl('COM1',9600)
		#time.sleep(0.1)
		#_thread.start_new_thread(self.read_data,())
		self._running=True
		time.sleep(0.1)
		self.t=threading.Thread(target=self.send_heartbeat) 
		self.t.start()
        #watch dog
		time.sleep(0.1)
		self.send_data("\nRs\r") #init 
		time.sleep(0.1)
		self.send_data("\nRn\r")	#speed control mode
		time.sleep(0.1)
		self.send_data("\nI+\r") #Rotation direction Right
		self.send_data("\nH1000\r") #acceleration 1000
		print("Speed Ready!")
	def port_open(self):
		if not self.port.isOpen():
			self.port.open()
	def port_close(self):
		self.port.close()
	def send_data(self,data):
		number=self.port.write(data.encode())
		return number
	def send_heartbeat(self):
		while(self._running):
			number=self.port.write("\nD\r".encode())
			time.sleep(8.01)
		#return number
	def terminate_heartbeat(self):
		self._running=False
	def read_data(self):
		while True:
			data=bytearray()
			data_str=""
			data.extend(self.port.read(1))
			data.extend(self.port.read(self.port.inWaiting()))
			#self.message+=data
			data_str=str(data.decode())
			print(data_str)
			if(len(data_str)>0):				
				if(len(data_str)==4):					
					print("Current Speed : " + haustodec(data_str),)
				elif(data_str[0]=='\n'):
					print("Haus : " + str(haustodec(data_str[2:6])))
				else:
					print("Rec data: " + data_str)
			#time.sleep(0.5)
def haustodec(h):
	try:
		r=int(h[::-1],16)
	except ValueError as e:
		r=h
	return r
def tohaus(d):
    if int(d)>4000:
        return "0000"
    return format(int(d),'X').zfill(4)[::-1]

