import mdfreader
import pandas
def parseMDF():
    mdf=mdfreader.mdf("hot verification02-11-11.dat",channelList=['Epm_nEng','InjCtl_qSetUnBal'])
    #mydf.resample(0.1)
    #speed=mydf.getChannelData('Epm_nEng')
    #q=mydf.getChannelData("InjCtl_qSetUnBal")
    #mdf.keepChannels({})
    mdf.convertToPandas(0.1)
    mdf['master_group'].to_csv("ss.csv")
    #pd.DataFrame.toCSV("ss.csv")
    
parseMDF()
