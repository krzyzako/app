import serial 
import json
import datetime
from collections import namedtuple
from arduino import JSONObject
import os
import snap7
from snap7.util import *
from snap7.snap7types import *

def read_plc():
        area = 0x83    # area for Q memory
        start = 560    # location we are going to start the read
        length = 1     # length in bytes of the read
        bit = 0
        byte = plc.read_area(area,0,start,length)
        return get_bool(byte,0,bit)

def ReadMemory(plc,byte,bit,datatype):
    result = plc.read_area(areas['MK'],0,byte,datatype)
    if datatype==S7WLBit:
        return get_bool(result,0,bit)
    elif datatype==S7WLByte or datatype==S7WLWord:
        return get_int(result,0)
    elif datatype==S7WLReal:
        return get_real(result,0)
    elif datatype==S7WLDWord:
        return get_dword(result,0)
    else:
        return None

def WriteMemory(plc,byte,bit,datatype,value):
    result = plc.read_area(areas['MK'],0,byte,datatype)
    if datatype==S7WLBit:
        set_bool(result,0,bit,value)
    elif datatype==S7WLByte or datatype==S7WLWord:
        set_int(result,0,value)
    elif datatype==S7WLReal:
        set_real(result,0,value)
    elif datatype==S7WLDWord:
        set_dword(result,0,value)
    plc.write_area(areas["MK"],0,byte,result)

def log(message):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print ("%s %s" % (now, message))

def arduino():
    while True:
        
        if ser.isOpen : 
        
        #dyst = "{\"error\":false,\"p_zasialanie\":23.5625,\"p_powrot\":35.1875,\"k_zasilanie\":34.6875,\"outside\":5.4375}"
         try:
            dyst = ser.readline().decode("utf-8").replace("\r\n", "") .replace(",", ", ").replace(":", " : ")
            data = json.loads(dyst, object_hook=JSONObject)
            if not data.error :
                zasilanie = int(data.p_zasialanie)
                powrot = int(data.p_powrot)
                kolektor = int(data.k_zasilanie)
                plc_zasilanie =  ReadMemory(s7,14,0,S7WLWord)
                
                if not powrot == plc_zasilanie:
                    WriteMemory(s7,14,0,S7WLWord,powrot)
                    print ("zapis")
                if not kolektor == ReadMemory(s7,30,0,S7WLWord):
                    WriteMemory(s7,30,0,S7WLWord,kolektor)
                    print ("zapis kol ",)

                log(('Zasilanie : ',kolektor) )
                log(('Powrot    : ',powrot))
                log(("Kolektor  : " , kolektor))
         except json.JSONDecodeError as identifier:
            pass
        
    else:
        ser.Open
 

try:
 print("Press Ctrl+C to stop the service")
 ser = serial.Serial("/dev/ttyACM0",9600)
 s7 = snap7.client.Client();
 s7.connect('192.168.1.120', 0, 1)
 iot =  ReadMemory(s7,14,0,S7WLWord)
 print(iot)
 arduino()

except KeyboardInterrupt:
    print()
    print("Service Stopped.")
