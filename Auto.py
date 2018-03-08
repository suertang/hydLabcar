# asap3.py 
# (C) 2017 Patrick Menschel
import ASAP3_full
import SpdCtl		
import time
def seq():
	mSerial=SpdCtl.SpdCtl()
	#init asap3
	HOST = "10.8.187.241"
	PORT = 22222
	mya3client = ASAP3_full.asap3client(host=HOST,port=PORT)
	#remote_server_desc = mya3client.get_remote_server_data()[0].upper()
	#print(remote_server_desc)
	map_info=mya3client.get_map_vals_by_name("PhyMod_trq2qBas_MAP")
	#remote_server_desc = mya3client.get_remote_server_data()[0].upper()
	#mya3client.set_whole_map_vals(map_info,0.1)

	while True:
		cmd = input(">:")
		print("command: " + cmd)
		if cmd == "q":
			break
		elif cmd=="run":
			sp_alt,q_alt=[0,0]
			for line in open("Speedinput_Python_trq.csv"):
				stt=time.time()
				[sp,q]=line.strip().split(';')

				if(sp!="Speed"):
					sp=float(sp)
					q=float(q)
					if(q_alt!=q):
						mya3client.a3set_lookup_table_value(map_info["map_number"],1,1,map_info["y_number"],map_info["x_number"],q)
						q_alt=q
					if(sp_alt!=sp):
						mSerial.send_data("\nG" + SpdCtl.tohaus(sp) +"\r")
						sp_alt=sp
					time.sleep(0.1-(time.time()-stt) % 0.1)
					#print(resp)
			mSerial.send_data("\nG0\r")
			mya3client.disconnect_from_host()

	
if __name__ == "__main__":
	seq()