import ntptime
import time

#if needed, overwrite default time server
def gettime():
    ntptime.host = "0.europe.pool.ntp.org"

    try:
      #print("Local time before synchronization：%s" %str(time.localtime()))
      #make sure to have internet connection
      ntptime.settime()
      #print("Local time after synchronization：%s" %str(time.localtime()))
      return time.localtime()
    except:
        ntptime.host = "0.pt.pool.ntp.org"
        ntptime.settime()
        return time.localtime()
