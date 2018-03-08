import serial
import time
import thread

class MSerialPort:
	message=''
	def __init__(self,port,buand):
		self.port=serial.Serial(port,buand,parity='O',timeout=1)
		if not self.port.isOpen():
			self.port.open()
	def port_open(self):
		if not self.port.isOpen():
			self.port.open()
	def port_close(self):
		self.port.close()
	def send_data(self,data):
		number=self.port.write(data)
		return number
	def send_heartbeat(self):
		while True:
			number=self.port.write("\nD\r")
			time.sleep(8)
		#return number
	def read_data(self):
		while True:
			data=''
			data=self.port.read(1)
			data+=self.port.read(self.port.inWaiting())
			#self.message+=data
			if(data!=''):
				if(len(data)==4):
					print("Current Speed : " + haustodec(data))
				else:
					print(data)
			#time.sleep(0.5)
def haustodec(h):
	return format(float(h[::-1]),".1f")
def tohaus(d):
    if int(d)>4000:
        return "0000"
    return format(int(d),'X').zfill(4)[::-1]
				

if __name__=='__main__':
	mSerial=MSerialPort('COM3',9600)
	thread.start_new_thread(mSerial.read_data,())
	#thread.start_new_thread(mSerial.send_heartbeat,())
    cmd=''
	while True:
		cmd = raw_input("Please input MGT command: q for quit:")
		if cmd == "q":
		    break;
		if cmd[0]=="G":
			mSerial.send_data("\nG" + tohaus(cmd[1:]) +"\r")
            time.sleep(0.5)
		else:
			mSerial.send_data("\n" + cmd +"\r")
			time.sleep(0.5)
			#print mSerial.message
			#print 'next line'