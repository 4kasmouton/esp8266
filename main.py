try:
  import usocket as socket
except:
  import socket
import dht
from machine import Pin, I2C, SoftI2C, WDT
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import socket as s
import network
import gettime
import time
import esp
esp.osdebug(None)
import gc
gc.collect()


def temperature(d):
    d.measure()
    time.sleep(1)
    return d.temperature(), d.humidity()


def web_page(TEMPSTATE, HUMSTATE, UVLIGTH,HOTSPOT,NIGTHHOT):
    #print(TEMPSTATE, HUMSTATE, UVLIGTH,HOTSPOT,NIGTHHOT)
    html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}</style></head><body><h1>ESP Web Server</h1>
    <p>Temperatura: <strong>"""+ str(TEMPSTATE) + """</strong></p>
    <p>humidade: <strong>""" + str(HUMSTATE) + """</strong></p><p>LUZ UV: <strong>""" + UVLIGTH + """</strong></p>
    <p>LUZ AQUECIMENTO: <strong>""" + HOTSPOT + """</strong></p><p>LUZ Noturna: <strong>""" + NIGTHHOT + """</strong></p>"""
    return html

def wificonnect():
    ssid = '*******'
    password = '*******'
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass
    return station.ifconfig()

def controlerligthUV(hour,UVB):
    if 8 <= hour <= 19:
        print("dia")
        UVB.value(1)
        time.sleep(2)
        return "on"
    else:
        print("noite")
        UVB.value(0)
        time.sleep(2)
        return "off"
        
def controlerligthhot(temp,ligthhot, hour):
    if 8 <= hour <= 19: 
        if temp >= 27:
            print("desliga a luz de calor")
            ligthhot.value(0)#desliga a luz
            time.sleep(2)
            return "off"
        else:
            print("liga a luz de calor")
            ligthhot.value(1)#liga a luz
            time.sleep(2)
            return "on"
    else:
        print("desliga a luz de calor")
        ligthhot.value(0)#desliga a luz
         time.sleep(2)
        return "off"
        
    
def nigthhot(hour, temp,ligthnigthhot):
    if 8 <= hour <= 19:
        if temp <= 18:
            print("liga a luz de calor noturna")
            ligthnigthhot.value(1)#liga a luz
            time.sleep(2)
            return "on"
        else:
            print("esta dentro desta hora")
            return "off"
    else:
        ligthnigthhot.value(0)
        time.sleep(2)
        return "off"

def watercontroler(hour,minu,waterpin):
    if hour == 8:
        if 30 <= minu <= 34:
            print("entrou 1")
            waterpin.value(1)
            time.sleep(15)
            waterpin.value(0)
            time.sleep(300)
    elif hour == 12 :
        if 30 <= minu <= 34:
            print("entrou 2")
            waterpin.value(1)
            time.sleep(15)
            waterpin.value(0)
            time.sleep(300)
    elif hour == 15:
        if 30 <= minu <= 34:
            print("entrou 3")
            waterpin.value(1)
            time.sleep(15)
            waterpin.value(0)
            time.sleep(300)
    elif hour == 18:
        if 30 <= minu <= 34:
            print("entrou 4")
            waterpin.value(1)
            time.sleep(15)
            waterpin.value(0)
            time.sleep(300)
    else:
        print("nao precisa regar")

#defenir lcd
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
#led = Pin(2, Pin.OUT)
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000) 
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

#Definir o sensor de temperatura 
d = dht.DHT11(Pin(16))

#connectar a internet e definir o socket
IP=wificonnect()
led = Pin(2, Pin.OUT) #led da board
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP[0], 801))
s.settimeout(10)
s.listen(1)

waterpin=led = Pin(15, Pin.OUT)
waterpin.value(0)

UVB = Pin(13, Pin.OUT)
UVB.value(0)

ligthhot=Pin(12, Pin.OUT)
ligthhot.value(0)

ligthnigthhot=Pin(14, Pin.OUT)
ligthnigthhot.value(0)
temp,hum=temperature(d)
UVLIGTH="off"
HOTSPOT="off"
NIGTHHOT="off"
try:

    while True:
        gc.collect()
        try:
            
            print("testrede1")
            lcd.clear()
            lcd.putstr(IP[0])
            #print(gc.mem_free()+" espaço de memoria free")
            print("testrede1")
            conn, addr = s.accept()
            time.sleep(1)
            print('Got a connection from %s' % str(addr))
            conn.settimeout(3)
            request = conn.recv(1024)
            request = str(request)
            print('Content = %s' % request)
            response = web_page(temp,hum,UVLIGTH,HOTSPOT,NIGTHHOT)
            conn.send(b'HTTP/1.1 200 OK\n')
            conn.send(b'Content-Type: text/html\n')
            conn.send(b'Connection: close\n\n')
            conn.sendall(response.encode())
            conn.close()
            print("connecção")
            s.settimeout(5)
            lcd.clear()
        except:
            try:
                print("hora")
                hora =gettime.gettime()
                print("UVLIGTH")
                UVLIGTH =controlerligthUV(hora[3],UVB)
                temp,hum=temperature(d)
                lcd.clear()
                phrase="Temp:"+str(temp)+" Hum:"+str(hum)+"%"
                lcd.putstr(phrase)
                print(temp,hum)
                print("HOTSPOT")
                HOTSPOT = controlerligthhot(temp,ligthhot,hora[3])
                print("NIGTHHOT")
                NIGTHHOT = nigthhot(hora[3], temp,ligthnigthhot)
                print("watercontroler")
                watercontroler(hora[3],hora[4],waterpin)
                time.sleep(5)
                print("test1")
                lcd.clear()
                lcd.putstr(IP[0])
                time.sleep(2)
                print("test2")
                lcd.clear()
                time.sleep(1)
                lcd.putstr(phrase)
                time.sleep(1)
                lcd.clear()
                time.sleep(1)
                print(hora)#printa o tempo atualizado
                times = str(hora[0])+"-"+str(hora[1])+"-"+str(hora[2])+"        "+str(hora[3])+":"+str(hora[4])+":"+str(hora[5])
                print("test3")
                lcd.putstr(times)
                time.sleep(5)
                print("test4")
                print(gc.mem_alloc())
                print(str(gc.mem_free())+" espaço de memoria free")
            except Exception as e:
                #lcd.putstr(str(e))
                print(e)
except Exception as e:
    #lcd.putstr(str(e))
    print(e)
        

