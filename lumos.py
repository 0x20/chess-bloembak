import time
from collections import Counter
import sys
import random
import datetime
import subprocess
import os
#from PIL import Image
config_length = 1024                    #Defining led array
config_length_hex = (config_length*6)
config_brightness=-1
config_error=[]
config_error_time=(int(time.time()*1000)+10000)
config_pushtime_last = round(time.time()*1000)
config_output = 'serial'

def frametime(type='',fps=30):
        global config_pushtime_last
        if type == 'push':
                config_pushtime_last = round(time.time()*1000)
        if type == 'since': 
                return round(time.time()*1000)-config_pushtime_last
        if type == 'wait':
                config_pushtime_left = config_pushtime_last+(1000/fps)-round(time.time()*1000)
                if config_pushtime_left < 2:
                        console('Running behind')
                while config_pushtime_left > 1:
                      config_pushtime_left = config_pushtime_last+(1000/fps)-round(time.time()*1000)  
                



def console(frame):
    #Function keeps track of occurring errors, displaying them every 10 seconds..
        global config_error,config_error_time
        config_error.append(frame)
        if config_error_time<int(time.time()*1000):
                counts = Counter(config_error)
                print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+" >>> LUMOS: "+str(counts))
                config_error=[]
                config_error_time=(int(time.time()*1000)+10000)

'''
def log(data,error=False):
    d = datetime.date.today()
    month = '%02d' % d.month
    day = '%02d' % d.day
    with open("logs/"+str(d.year)+str(month)+str(day), "a+") as myfile:
            if error == True:
                    data = "ERROR: "+str(data)
            myfile.write(str(datetime.datetime.now())+' >> '+str(data)+'\n')
'''
import serial
port = "/dev/ttyACM0"                #Defining our serial port
if config_output == 'serial':
	usart = serial.Serial(port,921600)
        

def push(frame='',repeat=False):            #Main function, send frame to the Teensy
    global config_length_hex,config_brightness
    while len(frame)<config_length_hex:     #We do need a full frame
        if(repeat and len(frame)>0):        #Repeat...
            frame += frame
        else:                   #or fill with zeros
            frame += '000000000000000000'
    if len(frame) % 2:                  #Hex frames shouldn't be odd-length
        frame += '0'
    

    split_line = [frame[i:i+192] for i in range(0, len(frame), 192)]
    #print split_line
    f = []
    for (ikey, item) in enumerate(split_line):
        if ikey % 2 != 0:
                split_item = [item[i:i+6] for i in range(0, len(item), 6)]
                rev_split_item = split_item[::-1]
                split_final = ''.join(rev_split_item)
        else:
                split_final = item
        f.append(split_final)
    frame = ''.join(f)



    frame_hex = '000001'
    frame_hex += frame[:config_length_hex]
    frame_bytes = bytes.fromhex(frame_hex)
    usart.write(frame_bytes)
    #filename = '../http-sim/frame.txt'
    
    try:
        frametime('push')
        if config_output == 'serial':
        	usart.write(frame_bytes)
        else:
        	with open(filename, "w") as f:
        		f.write(frame[:config_length_hex])
        console('Frame pushed')
    except:
            console('Output fail')
            #print 'j'
    '''
    try:
        #usart.write(frame_bytes)
        with open('C:/xampp/htdocs/frame.txt', "w") as f:
            f.write(frame[:config_length_hex])   
    except:
            console('Output fail')
            #print 'j'
    '''
def clear():                        #Send an empty frame
    push('000000',1)


def brightness(frame,offset=100):
    offset = offset/100.00
    pixels=[]
    pixels=[int(frame[x:x+2],16) for x in range(0,len(frame),2)]
    pixels=[(n*offset) for n in pixels]
    frame=''
    for i in pixels:
        i = int(i)
        if i<0:
            i=0
        if i>255:
            i=255
        i=hex(i)[2:]
        if len(i)<2:
            i = '0'+i
        frame=frame+i
    return frame

def controller(controller,checkfor):
    f = open('controllers/'+str(controller),'r')
    r = f.read()
    
    if checkfor < 8 and checkfor >= 0:
      try:
        if r[checkfor] == '0':
            return True
        else:
            return False
      except:
            console('Output fail')
            return False

def reset():
        os.system("screen -S 'lumos_temp' -X quit")
        time.sleep(0.5)
        os.system("screen -S lumos_temp -d -m")
        os.system("screen -r 'lumos_temp' -X stuff $'\npython start.py\n'")

def png(location,ret = False):
    try:
        img = Image.open(location)
        pixels = list(img.convert('RGBA').getdata())
        string=''
        for r, g, b, a in pixels: # just ignore the alpha channel
            string += '{:02x}{:02x}{:02x}'.format(r, g, b)
        if ret:
            return string
        else:
            push(string)
    except:
        console('Png error: '+str(location))

def gif(location,fps=24,amount=0,control=False):
    i=-1
    a=0
    path, dirs, files = os.walk(location).next()
    file_count = len(files)
    while i >= -1:
          i=i+1
          if i == file_count:
              i = 0
              a=a+1
          imgfile = location+'/'+str(i)+'.png'
          time.sleep(1/round(fps,2))
          png(imgfile)
          if a != 0 and a == amount:
              break
          
def controllercheck(controllers=[0,1,2,3]):

    png("gifs/split/pressa/0.png")
    players = {0:'ai',1:'ai',2:'ai',3:'ai'}
    start = time.time()
    while time.time()-10 < start:
        for i in controllers:
            if controller(i,0):
                players[i]='human'
        pl = '';
        for u in range(4):
            if players[u] == 'human':
            	pl += '1'
            else:
            	pl += '0'
        png("gifs/split/pressa"+pl+"/0.png")    



    return players

def mp3(path = ''):
    try:
        subprocess.Popen(['mpg123', '', str(path)],stdin=None, stdout=None, stderr=None)               
    except:
        console('Mp3 error: '+str(path))
