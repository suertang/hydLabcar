import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import shlex
class dcm():
    def __init__(self):
        self.path='QPC_QntInt_MC09_20180328.DCM'
        self.comments=[]
        self.format=2.0
        self.name=""
        self.maps=[]
        self.solos=[]
        self.curves=[]
        self.blocks=[]
        self.functions=[]
        self.read()
    def read(self):
        blockStatus=False
        currentData=None
        dtyps={
                "KENNFELD":[c_map,"maps"],
                "FESTWERT":[c_solo,"solos"],
                "KENNLINIE":[c_curve,"curves"],
                "FESTWERTEBLOCK":[c_block,'blocks'],
                "FUNKTIONEN":[c_function,'functions'],                
        }
        for line in open(self.path):
            s=shlex.split(line.strip())
            if(len(s)>0):
                if blockStatus:
                    if s[0] != "END":                        
                        currentData.data.append(s)
                        continue
                    else:
                        currentData.process()
                        eval("self.{}s".format(currentData.string)).append(currentData)
                        blockStatus=False
                        currentData=None
                elif s[0] in dtyps:
                    currentData=dtyps[s[0]][0](s)
                    blockStatus=True  # 实例化各种类
                elif s[0][:1]=="*":
                    self.comments.append(line)
            
    def export(self):
        pass
class c_map():
    def __init__(self,s):
        self.name,self.sizex,self.sizey=s[1:]
        self.data=[]
        self.cols=[]
        self.index=[]
        self.vals=[]
        self.string="map"
    def process(self):
        tempdata=[]
        for v in self.data:
            if(v[0]=="ST/X"):
                self.cols.extend(v[1:])
            elif(v[0]=="ST/Y"):                
                self.index.extend(v[1:])
            elif(v[0]=="WERT"):
                tempdata.extend(v[1:])
                if len(tempdata)==int(self.sizex):                    
                    self.vals.append(tempdata)
                    tempdata=[]
            elif(v[0]=="LANGNAME"):
                self.lang=v[1:]
            elif(v[0]=="FUNKTION"):
                self.function=v[1:]
            elif(v[0]=="EINHEIT_X"):
                self.xunit=v[1:]
            elif(v[0]=="EINHEIT_Y"):
                self.yunit=v[1:]
            elif(v[0]=="EINHEIT_W"):
                self.vunit=v[1:]
    def __str__(self):
        return self.string
class c_solo():
    def __init__(self,s):
        self.name=s[1]
        self.data=[]        
        self.string="solo"
    def process(self):        
        for v in self.data:
            if(v[0]=="WERT"):
                self.val=v[1]
            if(v[0]=="TEXT"):
                self.val=v[1]
            elif(v[0]=="LANGNAME"):
                self.lang=v[1]
            elif(v[0]=="FUNKTION"):
                self.function=v[1:]
            elif(v[0]=="EINHEIT_W"):
                self.vunit=v[1:]
    def __str__(self):
        return self.string
class c_curve():
    def __init__(self,s):
        self.name,self.sizex=s[1:]
        self.data=[]
        self.cols=[]
        self.index=[]
        self.vals=[]
        self.string="curve"
    def process(self):
        tempdata=[]
        for v in self.data:
            if(v[0]=="ST/X"):
                self.cols.extend(v[1:])
            elif(v[0]=="ST/Y"):                
                self.index.extend(v[1:])
            elif(v[0]=="WERT"):
                tempdata.extend(v[1:])
                if len(tempdata)==int(self.sizex):                    
                    self.vals.append(tempdata)
                    tempdata=[]
            elif(v[0]=="LANGNAME"):
                self.lang=v[1:]
            elif(v[0]=="FUNKTION"):
                self.function=v[1:]
            elif(v[0]=="EINHEIT_X"):
                self.xunit=v[1:]
            elif(v[0]=="EINHEIT_Y"):
                self.yunit=v[1:]
            elif(v[0]=="EINHEIT_W"):
                self.vunit=v[1:]
    def __str__(self):
        return self.string    
class c_block():
    def __init__(self,s):
        self.name,self.sizex=s[1:]
        self.data=[]
        self.cols=[]
        self.index=[]
        self.vals=[]
        self.string="block"

    def __str__(self):
        return self.string
    
    def process(self):
        tempdata=[]
        for v in self.data:
            if(v[0]=="ST/X"):
                self.cols.extend(v[1:])
            elif(v[0]=="ST/Y"):                
                self.index.extend(v[1:])
            elif(v[0]=="WERT"):
                tempdata.extend(v[1:])
                if len(tempdata)==int(self.sizex):                    
                    self.vals.append(tempdata)
                    tempdata=[]
                else:
                    continue
            elif(v[0]=="LANGNAME"):
                self.lang=v[1:]
            elif(v[0]=="FUNKTION"):
                self.function=v[1:]
            elif(v[0]=="EINHEIT_X"):
                self.xunit=v[1:]
            elif(v[0]=="EINHEIT_Y"):
                self.yunit=v[1:]
            elif(v[0]=="EINHEIT_W"):
                self.vunit=v[1:]
 
class c_function():
    def __init__(self,s):
        self.fkts=[]
        self.data=[]
        self.string="function"
    def __str__(self):
        return self.string
    def process(self):
        for v in self.data:
            if(v[0]=="FKT"):
                self.fkts.append(fkt(v[1:]))
 

class fkt():
    def __init__(self,s):
        self.name,self.version,self.desp=s
mydcm=dcm()
df=pd.DataFrame(mydcm.maps[0].vals,index=mydcm.maps[0].index,columns=mydcm.maps[0].cols)
print(df)
