import mdfreader
import pandas
import sys
import os
def parseMDF(filename):
    if(os.path.exists(filename)):
        mdf=mdfreader.mdf(filename,channelList=['Epm_nEng','InjCtl_qSetUnBal'])
        mdf.convertToPandas(0.1)
        mdf['master_group'].to_csv(filename+".csv")
        print("done!")
    else:
        print("Sorry, please check the filename. Usage: Python " +__file__ + " filename.mdf")



if __name__=="__main__":
    parseMDF(sys.argv[1])
