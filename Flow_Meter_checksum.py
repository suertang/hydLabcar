def calc_checksum(data):
    checksum = 0
    for idx in range(0,len(data),1):
        checksum += struct.unpack(">B",data[idx:idx+1])[0]
    return -checksum & 0xFF