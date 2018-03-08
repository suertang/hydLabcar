# asap3.py 
# (C) 2017 Patrick Menschel
import socket
import struct
import time
import datetime
import queue
import threading
import logging

A3_INIT = 0x1000000
A3_REQ = 0x1000001

A3_ACK = 0xAAAA
A3_CMPL = 0x0
A3_ERR = 0xFFFF
A3_NONIMPL = 0x5656


ASAP3VERSION = 2.1
ASAP3CLIENTVERSION = "0.1beta"


ASAP3ERRORCODES = {0x0:"ACK: Faultless execution of the last command",
                   0x1232:"ACK: Faultless execution of the last command",
                   0x2342:"ERROR: Restart of Communication necessary",
                   0x2344:"INFO: MC System is in simulation mode",
                   0x5656:"ERROR: Command not available",
                   0xAAAA:"ACK: Command received, execution is pending",
                   0xEEEE:"RETRY: repeat the request",
                   0xFFFF:"ERROR: see description",
                   }

ASAP3COMMANDS = {1:"emergency",
                 2:"init",
                 3:"select_description_file_and_binary_file",
                 4:"copy_binary_file",
                 5:"change_binary_filename",
                 6:"select_look-up_table",
                 7:"put_look-up_table",
                 8:"get_look-up_table",
                 9:"get_look-up_table_value",
                 10:"increase_look-up_table",
                 11:"set_look-up_table",
                 12:"parameter_for_value_acquisition",
                 13:"switching_online_offline",
                 14:"get_parameter",
                 15:"set_parameter",
                 16:"set_graphic_mode",
                 17:"reset_device",
                 18:"set_format",
                 19:"get_online_value",
                 20:"identify",
                 21:"get_user_defined_value",
                 22:"get_user_defined_value_list",
                 30:"define_description_and_binary_file",
                 41:"define_recorder_parameters",
                 42:"define_trigger_condition",
                 43:"activate_recorder",
                 44:"get_recorder_status",
                 45:"get_recorder_result_header",
                 46:"get_recorder_results",
                 47:"save_recorder_file",
                 48:"load_recorder_file",
                 50:"exit",
                 61:"set_case_sensitive_labels",
                 106:"extended_select_look-up_table",
                 107:"extended_put_look-up_table",
                 108:"extended_get_look-up_table",
                 109:"extended_get_look-up_table_value",
                 110:"extended_increase_look-up_table",
                 111:"extended_set_look-up_table",
                 112:"extended_parameter_for_value_acquisition",
                 114:"extended_get_parameter",
                 115:"extended_set_parameter",
                 119:"extended_get_online_value",
                 200:"extended_query_available_services",
                 201:"extended_get_service_information",
                 202:"extended_execute_service",
                 }

def get_asap3_command_code_by_name(n):
    for x in ASAP3COMMANDS:
        if ASAP3COMMANDS[x] == n:
            return x
    raise ValueError("Not Found {0}".format(n))


class asap3error(Exception):
    def __init__(self, *args, **kwargs):
        super(asap3error,self).__init__(self, *args, **kwargs)

class asap3timeout(asap3error):
    def __init__(self, *args, **kwargs):
        super(asap3timeout,self).__init__(self, *args, **kwargs)

class asap3notimplemented(asap3error):
    def __init__(self, *args, **kwargs):
        super(asap3notimplemented,self).__init__(self, *args, **kwargs)


def create_asap3_string(s):
    bs = s.encode()
    ret = bytearray()
    ret.extend(struct.pack(">H",len(s)))
    ret.extend(bs)
    if len(bs) % 2:
        ret.append(0)
    return ret

def pop_asap3_string(data):
    L = struct.unpack(">H",data[:2])[0]
    if L % 2:
        L += 1
    return (str(asap3string(s=data[:2+L])),data[2+L:])
    

def create_asap3_message(cmd,status=None,data=None):
    assert(cmd != None)
    d = bytearray()
    d.extend(struct.pack(">H",cmd))
    if status:
        d.extend(struct.pack(">H",status))
    if data:
        if isinstance(data,str):
            d.extend(create_asap3_string(data))
        elif isinstance(data,bytearray):
            d.extend(data)
        elif isinstance(data,bytes):
            d.extend(data)
    ret = bytearray()
    ret.extend(struct.pack(">H",len(d)+4))
    ret.extend(d)
    ret.extend(struct.pack(">H",calc_checksum(ret)))
    return ret

def create_asap3_version(v):
    ret = bytearray()
    major,minor = [int(x) for x in str(v).split(".")]
    ret.extend(struct.pack("BB",major,minor))
    return ret
    
def interpret_asap3_message(data):
    l = struct.unpack(">H",data[:2])[0]
    assert (l == len(data))
    cs = calc_checksum(data[:-2])
    c = struct.unpack(">H",data[-2:])[0]
    assert(c == cs)
    cmd,stat = struct.unpack(">HH",data[2:6])
    d = data[6:-2]
    if d:
        da = d
    else:
        da = None
    return {"cmd":cmd,
            "status":stat,
            "data":da,
            }
    
def calc_checksum(data):
    checksum = 0
    for idx in range(0,len(data),2):
        checksum += struct.unpack(">H",data[idx:idx+2])[0]
    return checksum & 0xFFFF


class asap3string():
    def __init__(self,s):
        if isinstance(s,str):
            self.str = s
        elif isinstance(s,bytes) or isinstance(s,bytearray):
            self.from_bin(s)
            
    def to_bin(self):
        return create_asap3_string(self.str)

    def from_bin(self,s):
        L = struct.unpack(">H",s[:2])[0]
        try:
            self.str = s[2:2+L].decode()
        except UnicodeError:
            self.str = s[2:2+L].decode("latin9")
        return

    def __str__(self):
        return self.str

class asap3version():
    def __init__(self,version):
        if isinstance(version,float):
            self.version = version
        elif isinstance(version,bytes) or isinstance(version,bytearray):
            self.from_bin(version)

    def to_bin(self):
        major,minor = [int(x) for x in str(self.version).split(".")]
        ret = struct.pack("BB",major,minor)
        return ret

    def from_bin(self,b):
        self.version = float(b[0]+(b[1]/10))

    def __str__(self):
        return str(self.version)

    def __float__(self):
        return self.version

class asap3map():
    def __init__(self):
        pass
    
    def to_bin(self):
        pass
    
    def from_bin(self,b):
        pass

    def __str__(self):
        pass


class asap3message():
    def __init__(self,cmd,data):
        self.cmd = cmd
        self.data = data

    def to_bin(self):
        return create_asap3_message(cmd=self.cmd,data=self.data)


class asap3service():
    def __init__(self,cmd,data=None,timeout=None):
        self.cmd = get_asap3_command_code_by_name(cmd)
        self.request = asap3message(cmd=self.cmd,data=data)
        self.response = queue.Queue()
        self.timeout = timeout
        self.status = A3_INIT
        self.txtimestamp=None
        self.rxtimestamp=None
    
    def get_status(self):
        return self.status
    
    def set_status(self,status):
        self.status = status
        return
        
    def get_request(self):
        self.set_status(status=A3_REQ)
        self.txtimestamp = datetime.datetime.now()
        return self.request.to_bin()
        
    def feed_response(self,resp):
        if resp["cmd"] != self.cmd:
            raise NotImplementedError("get_response {0} but found {1}".format(self.cmd,resp["cmd"]))
        self.set_status(status=resp["status"])
        self.rxtimestamp = datetime.datetime.now()
        resp.update({"timestamp":self.rxtimestamp})
        if resp["status"] == A3_CMPL:
            self.response.put(self.feed_specific(resp))
        elif resp["status"] == A3_ERR:
            data = resp.pop("data")
            err_code = struct.unpack(">H",data[:2])[0]
            err_text = asap3string(data[2:])
            resp.update({"err_code":err_code,
                         "err_txt":err_text})
            self.response.put(resp)
        return
                
    def feed_specific(self,resp):
        return resp
    
    def get_response(self):
        resp = self.response.get(timeout=self.timeout)
        if not resp:
            raise asap3timeout("Timeout of service")
        elif "err_code" in resp:
            print("ERR {err_code} TXT {err_txt}".format_map(resp))
            raise asap3error("ERR {err_code} TXT {err_txt}".format_map(resp))
        return resp
    
    def is_complete(self):
        if self.status in (A3_CMPL,A3_ERR,A3_NONIMPL):
            return True
        else:
            return False

#basic communication services


class asap3init(asap3service):
    def __init__(self):
        super(asap3init, self).__init__(cmd="init")


class asap3identify(asap3service):
    def __init__(self,version,description):
        data = bytearray()
        data.extend(create_asap3_version(v=version))
        data.extend(create_asap3_string(s=description))
        super(asap3identify, self).__init__(cmd="identify",data=data)

    def feed_specific(self,resp):
        data = resp.pop("data")
        v = asap3version(data[:2])
        d = asap3string(data[2:])
        resp.update({"version":v,
                     "description":d,
                    })
        return resp
        

class asap3exit(asap3service):
    def __init__(self):
        super(asap3exit, self).__init__(cmd="exit")




class asap3select_lookup_table(asap3service):
    def __init__(self,Lun,map_name):
        data = bytearray()
        data.extend(struct.pack(">H",Lun))
        data.extend(create_asap3_string(s=map_name))
        super(asap3select_lookup_table, self).__init__(cmd="select_look-up_table",data=data)


    def feed_specific(self,resp):
        data = resp.pop("data")
        map_num,ny,nx,addr = struct.unpack(">HHHH",data[:8])
        resp.update({"map_number":map_num,
                     "y_number":ny,
                     "x_number":nx,
                     "address":addr,
                    })
        return resp


    
    
class asap3get_parameter(asap3service):
    def __init__(self,Lun,para_name):
        data = bytearray()
        data.extend(struct.pack(">H",Lun))
        data.extend(create_asap3_string(s=para_name))
        super(asap3get_parameter, self).__init__(cmd="get_parameter",data=data)
        
    def feed_specific(self,resp):
        data = resp.pop("data")
        val,val_min,val_max,min_inc = struct.unpack(">ffff",data)
        
        resp.update({"val":val,
                     "min":val_min,
                     "max":val_max,
                     "min_inc":min_inc,
                    })
        return resp
    

class asap3set_parameter(asap3service):
    def __init__(self,Lun,para_name,val):
        data = bytearray()
        data.extend(struct.pack(">H",Lun))
        data.extend(create_asap3_string(s=para_name))
        data.extend(struct.pack(">f",val))
        super(asap3set_parameter, self).__init__(cmd="set_parameter",data=data)



class asap3client:
    def __init__(self,host=None,port=None,timeout=30):
        self._init_logger()
        self.host = None
        self.port = None
        self.con = None
        self.timeout = timeout
        self.rxbuffer = bytearray()
        
        if host:
            self.host = host
        if port:
            self.port = port
            
        
        self.implemented_asap_version = ASAP3VERSION
        self.description = "python3 client for ASAP3 V{0}".format(ASAP3CLIENTVERSION)
        
        self.remote_server_description = None
        self.remote_server_asap_version = None

        self.rx_queue = queue.Queue()
        self.rx_handler = threading.Thread(target=self.handlerx)
        self.rx_handler.setDaemon(True)
        
        self.requests = queue.Queue()
        self.request_handler = threading.Thread(target=self.handlerequests)
        self.request_handler.setDaemon(True)
        self.currentrequest = None
        
        if (self.host != None) and (self.port != None):
            self.connect_to_host(host=self.host,port=self.port)

        self._log_debug('Init complete')

    def _init_logger(self):
        self._logger = logging.getLogger('asap3client')
        self._logger.setLevel(logging.DEBUG)
        self._fh = logging.FileHandler('asap3client.log')
        #self._fh.setLevel(logging.DEBUG)
        self._fh.setLevel(logging.INFO)
        #self._fh.setLevel(logging.ERROR)
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.ERROR)
        self._formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._fh.setFormatter(self._formatter)
        self._ch.setFormatter(self._formatter)
        self._logger.addHandler(self._fh)
        self._logger.addHandler(self._ch)
        self._log_debug('Logger has been initialized')
        return
    
    def _log_info(self,msg):
        if self._logger:
            self._logger.info(msg)
        return
                
    def _log_error(self,msg):
        if self._logger:
            self._logger.error(msg)
        return
    
    def _log_debug(self,msg):
        if self._logger:
            self._logger.debug(msg)
        return
    
    def get_remote_server_data(self):
        return (self.remote_server_description,
                self.remote_server_asap_version)
    
    def transmit(self,msg):
        self._log_debug("SND: {0}".format(" ".join(["{0:02X}".format(x) for x in msg])))
        return self.con.sendall(msg)

    def connect_to_host(self,host,port):
        self.con = socket.create_connection(address=(host,port))
        self.rx_handler.start()
        self.request_handler.start()
        resp = self.a3init()
        if resp["status"] == 0:
            resp = self.a3identify()
            if resp["status"] == 0:
                self._log_info("Server:{description}, Version:{version}".format_map(resp))
                self.remote_server_description = str(resp["description"])
                self.remote_server_asap_version = float(resp["version"])
                assert (self.remote_server_asap_version == self.implemented_asap_version)
            
        return

    def disconnect_from_host(self):
        self._log_info("Disconnecting from Server")
        self.a3exit()
        self.con.close()
        self.con = None
        return
    
    def handlerequests(self):
        assert(self.con != None)
        while (self.con != None):
            self.currentrequest = self.requests.get()
            self.transmit(self.currentrequest.get_request())
            while not self.currentrequest.is_complete():
                self.currentrequest.feed_response(self.rx_queue.get(timeout=self.timeout))
        return None

    def handlerx(self):
        assert(self.con != None)        
        while (self.con != None):
            try:
                data = self.con.recv(2)
            except ConnectionAbortedError:
                break
            if len(data) == 2:
                self.rxbuffer.extend(data)
                l = struct.unpack(">H",data)[0]
                data = self.con.recv(l-2)
                self.rxbuffer.extend(data)
                self._log_debug("RCV: {0}".format(" ".join(["{0:02X}".format(x) for x in data])))
                msg = interpret_asap3_message(self.rxbuffer)
                if msg:
                    self.rx_queue.put(msg)
                    self.rxbuffer.clear()       
            else:
                time.sleep(1)
        return None
    
    def request_service(self,s):
        self.requests.put(s)
        resp = s.get_response()
        return resp
    
    #standard asap3 commands follow
                
    def a3init(self):
        self._log_debug("a3init")
        return self.request_service(s=asap3init())

    def a3identify(self):
        self._log_debug("a3identify")
        return self.request_service(s=asap3identify(version=self.implemented_asap_version,description=self.description))
 
    def a3exit(self):
        self._log_debug("a3exit")
        return self.request_service(s=asap3exit())

    def a3emergency(self,event=0):
        self._log_debug("a3emergency w event {0}".format(event))
        return self.request_service(s=asap3emergency(event=event))

 
    
    def a3get_parameter(self,Lun, para_name):
        self._log_debug("a3get_parameter w Lun {0} para_name {1}".format(Lun,para_name))
        return self.request_service(s=asap3get_parameter(Lun=Lun, para_name=para_name))

    def a3set_parameter(self,Lun, para_name, val):
        self._log_debug("a3set_parameter w Lun {0} para_name {1} val {2}".format(Lun,para_name,val))
        return self.request_service(s=asap3set_parameter(Lun=Lun, para_name=para_name, val=val))

    
    def switch_online(self):
        return self.a3switching_online_offline(mode=1)
    
    def switch_offline(self):
        return self.a3switching_online_offline(mode=0)
    

    
    
    
def selftest(testmode="object"):
    HOST = "127.0.0.1"
    PORT = 22222

    if testmode == "object":
        mya3client = asap3client(host=HOST,port=PORT)
        remote_server_desc = mya3client.get_remote_server_data()[0].upper()
        print(remote_server_desc)
        for line in open("D:/ttt.txt"):
            [sp,q]=line.strip().split(',')
            if(sp!="speed"):
                resp=mya3client.a3set_parameter(0,"DEMO_CONSTANT_1",float(q))
                time.sleep(0.1)
                print(resp)
        mya3client.disconnect_from_host()
            
if __name__ == "__main__":
    selftest(testmode="object")    


