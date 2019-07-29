from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#Camera configuration:
camera = PiCamera()
camera.resolution = (512, 384)
camera.framerate = 32
record_amount = 10
delay = 2


#Other Variables:
PIR = 16
timmer_count = 3
photo_number = 1
reset_time = record_amount
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)                             #Use the regular pin identifiers. 
GPIO.setup(PIR, GPIO.IN)                                  #Read output from PIR motion sensor
date_string = time.strftime('%m_%d_%Y')           #Date for time stamp
hour_string = time.strftime("%H:%M:%S")           #Time used for file naming
standard_hour_string = time.strftime("%r")          #Time used for video time stamp overlay
mypath = '/home/pi/LOAVES/pics/' + date_string + '/'



def check():
        previous_line = ""
        with open('addr.txt','r') as infile:            #open the addr.txt file$
                for current_line in infile:
                        if 'wlan0' in previous_line:    #looks for wlan0 so it $
                                return current_line
                        previous_line = current_line


if not os.path.isdir(mypath):
        os.makedirs(mypath)

while (timmer_count > 0):                        # Delay that gives the pi sufficient 
        print (timmer_count)                     # time to boot up before trying to 
        time.sleep(1)                          # connect to the network
        timmer_count -= 1

gauth = GoogleAuth()                             # Google drive API

gauth.LoadCredentialsFile("mycreds.txt")         # Try to load saved client credentials
if gauth.credentials is None:                    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
    
elif gauth.access_token_expired:                 # Refresh them if expired
    gauth.Refresh()
    
else:                                            # Initialize the saved creds
    gauth.Authorize()
    
gauth.SaveCredentialsFile("mycreds.txt")         # Save the current credentials to a file
drive = GoogleDrive(gauth)                       # Set drive location using .json file


ip_address = check()                    #perform check for address
text = ip_address[20:35]                #snip the section of the address
file1 = drive.CreateFile({'title': 'loaf_ip.txt'})
file1.SetContentString(text)
file1.Upload()                          #save IP address to txt file


myfile = drive.CreateFile({'id': '0B4w2yS9E929tMUpfTmYzUXhzUG8'})
myfile.GetContentFile('loaf_settings.txt', mimetype='text/html')



settings = open("loaf_settings.txt", "r")               #open the settings.txt file
Motion = settings.read(3)                       #read a piece and assign the value to the Motion Sensor
Servo  = settings.read(6)

M = int(Motion[2:3])                            #snip just the ON\OFF part of the value and keep it
S = int(Servo[3:4])
settings.close()

if M == 1:
        M = "ON"
else:
        M = "OFF"

if S == 1:
        S = "ON"
else:
        S = "OFF"

print "Starting up"
print "Motion is %s" % M                        # The state of the motion and servo will show on boot
print "Servo is %s " % S





# Main program:
try:
	if __name__ == '__main__':
		
		while True:
			i=GPIO.input(PIR)                       #set PIR as input
			if i==0:                                #When output from motion sensor is LOW
				print "No intruders around"
				time.sleep(delay)
				 
			elif i==1:                              #When output from motion sensor is HIGH
				print "Intruder detected"
				my_file = (mypath +  str(hour_string) + '.h264')
			 
				camera.start_recording(my_file)
				file2 = drive.CreateFile()
			 

				print "Recording in progress"
				print "Will record for %s seconds." %(record_amount)
			 
				while (record_amount >= 0):                #This will blink red to let you know it's
					record_amount -= 1                  			#currently recording
					time.sleep(1)
					standard_hour_string = time.strftime("%r")
					camera.annotate_text = standard_hour_string
					
				camera.stop_recording()
				time.sleep(.5)
			 
				print "Pushing saved video to Google Drive"        
				file2.SetContentFile(my_file)             #Set the recorded file to be uploaded   
				file2.Upload()                            #upload file to google drive
					 
				hour_string = time.strftime("%H:%M:%S")   #reset time so we don't overwrite exisiting files
				standard_hour_string = time.strftime("%r")
			 
				record_amount = reset_time                #reset the record time so it doesn't stay at
				time.sleep(.5)                            #0 seconds and keep looping 1 sec videos
				print "Done!\n\n"
				 
except KeyboardInterrupt:
        print "Program Terminated \n"

except:
	print "Other Error Occurred"
        
finally:
        GPIO.cleanup()

