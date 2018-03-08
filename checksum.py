def cal_checksum(data):
	checksum=0
	data=data.upper()
	for idx in range(0,len(data),2):
		checksum -= int("0x" + data[idx:idx+2],16)
	return format(checksum & 0xFF,'X')