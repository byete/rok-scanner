from ppadb.client import Client
import cv2
import sys
import os
import pytesseract
import numpy as np
import time
import xlwt 
from xlwt import Workbook
from datetime import date
import tkinter as tk
import keyboard
from neural_network import read_ocr
import traceback


today = date.today()
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
thresh = 127

def tointcheck(element):
	try:
		return int(element)
	except ValueError:
		return element
		
def tointprint(element):
	try:
		return str(f'{int(element):,}')
	except ValueError:
		return str(element)
	
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

add_sum = False

def on_checkbox_click():
    global add_sum
    add_sum = True

os.system('')

root=tk.Tk()
root.title('Scanner')
root.geometry('400x200')

OPTIONS = [1, 3, 100, 200, 300]
	
variable = tk.StringVar(root)
variable.set('')

variable2 = tk.IntVar(root)
variable2.set('')

var1 = tk.IntVar()

kingdom_label = tk.Label(root, text='Kingdom', font=('calibre',10, 'bold'))  
scan_index_label = tk.Label(root, text ='Scan index', font=('calibre',10, 'bold'))
checkbox_label = tk.Label(root, text ='Enable Power/KP Sum', font=('calibre',10, 'bold'))

checkbox = tk.Checkbutton(root, command=on_checkbox_click)
kingdom_entry = tk.Entry(root, textvariable=variable, font=('calibre', 10, 'normal'))
scan_index = tk.Entry(root, textvariable=variable2, font=('calibre', 10, 'normal'))

def search():
	if variable.get():
		global kingdom
		kingdom = variable.get()
		global search_range
		search_range = variable2.get()
		root.destroy()

	else:
		print('You need to fill in a kingdom number')
		kingdom_entry.focus_set()
		
button = tk.Button(root, text='Scan', height=3, width=10, font=('calibre', 10, 'bold'), command=search)

checkbox_label.grid(row=3, column=0, sticky='w')
checkbox.grid(row=3, column=1, sticky='w', columnspan=2)

kingdom_label.grid(row=0, column=0, sticky='w')
kingdom_entry.grid(row=0, column=1, sticky='w', columnspan=2)

scan_index_label.grid(row=1, column=0, sticky='w')
scan_index.grid(row=1, column=1, sticky='w', columnspan=2)

button.grid(row=5, column=0, sticky='w', columnspan=2)


root.mainloop()

adb = Client(host='localhost', port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

wb = Workbook()
sheet1 = wb.add_sheet(str(today))

style = xlwt.XFStyle()
font = xlwt.Font()
font.bold = True
style.font = font

sheet1.write(0, 0, 'Governor ID', style)
sheet1.write(0, 1, 'Power', style)
sheet1.write(0, 2, 'Kill Points', style)
sheet1.write(0, 3, 'Deads', style)
sheet1.write(0, 4, 'Tier 4 Kills', style)
sheet1.write(0, 5, 'Tier 5 Kills', style)

Y =[285, 390, 490, 590, 605]


stop = False
def onkeypress(event):
	global stop
	if event.name == '\\':
		print("Your scan will be terminated when current governor scan is over!")
		stop = True

keyboard.on_press(onkeypress)

try:
	for i in range(search_range):
		if stop:
			print("Scan Terminated! Saving the current progress...")
			break
		if i>4:
			k = 4
		else:
			k = i
			
		gov_dead = 0
		gov_kills_tier4 = 0
		gov_kills_tier5 = 0
		device.shell(f'input tap 690 ' + str(Y[k]))
		time.sleep(1.8)
		
		gov_info = False
		count = 0
		while not (gov_info):
			image_check = device.screencap()

			with open(('images/check_more_info.png'), 'wb') as f:
				f.write(image_check)
			
			image_check = cv2.imread('images/check_more_info.png',cv2.IMREAD_GRAYSCALE)
			roi = (294, 786, 116, 29)
			
			im_check_more_info = image_check[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
			check_more_info = pytesseract.image_to_string(im_check_more_info,config="-c tessedit_char_whitelist=MoreInfo")
			
			if 'MoreInfo' not in check_more_info :
				device.shell(f'input swipe 690 605 690 540')
				device.shell(f'input tap 690 ' + str(Y[k]))
				count += 1
				time.sleep(2)
				if count == 5:
					break
			else:
				gov_info = True
				break
		
		image = device.screencap()
		with open(('images/gov_info.png'), 'wb') as f:
			f.write(image)

		image = cv2.imread('images/gov_info.png')

		roi = (733, 192, 200, 35)
		im_gov_id = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		image = cv2.imread('images/gov_info.png')

		roi = (874, 327, 224, 40)
		im_gov_power = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		roi = (1106, 327, 224, 40)
		im_gov_killpoints = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		image = cv2.imread('images/gov_info.png')
		kernel = np.ones((2, 2), np.uint8)
	 
		image = cv2.erode(image, kernel) 
		roi = (598, 331, 250, 40)
		im_alliance_tag = image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
		
		device.shell(f'input tap 1118 314')
        
		gov_id = read_ocr(im_gov_id)
		gov_killpoints2 = pytesseract.image_to_string(im_gov_killpoints,config="-c tessedit_char_whitelist=0123456789")
		gov_power2 = pytesseract.image_to_string(im_gov_power,config="-c tessedit_char_whitelist=0123456789")
		gov_power = read_ocr(im_gov_power)
		gov_killpoints = read_ocr(im_gov_killpoints)
		gov_killpoints = gov_killpoints2 if (len(''.join(str(gov_killpoints).split()))-1 > len(str(gov_killpoints))) else gov_killpoints
		gov_power = gov_power2 if (len(''.join(str(gov_power2).split()))-1 > len(str(gov_power))) else gov_power

		time.sleep(1)

		image = device.screencap()
		with open(('images/kills_tier.png'), 'wb') as f:
			f.write(image)
		
		image2 = cv2.imread('images/kills_tier.png')
		image2 = cv2.fastNlMeansDenoisingColored(image2,None,20,20,7,3)
		_,image2 = cv2.threshold(image2,180,255,cv2.THRESH_BINARY)

		roi = (862, 561, 215, 26)
		im_kills_tier4 = image2[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		roi = (862, 606, 215, 26)
		im_kills_tier5 = image2[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		device.shell(f'input tap 350 740') 
		
		gov_kills_tier4 = pytesseract.image_to_string(im_kills_tier4,config="-c tessedit_char_whitelist=0123456789")
		gov_kills_tier5 = pytesseract.image_to_string(im_kills_tier5,config="-c tessedit_char_whitelist=0123456789")
		time.sleep(1)
		
		image = device.screencap()
		with open(('images/more_info.png'), 'wb') as f:
			f.write(image)

		image3 = cv2.imread('images/more_info.png')
		kernel = np.ones((2, 2), np.uint8)
		image3 = cv2.dilate(image3, kernel)

		roi = (1130, 443, 183, 40)
		im_dead = image3[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		
		roi = (1130, 443, 183, 40)
		thresh_image = cv2.threshold(image3, thresh, 255, cv2.THRESH_BINARY)[1]
		im_dead2 = thresh_image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		roi = (1130, 443, 183, 40)
		blur_img = cv2.GaussianBlur(image3, (3, 3), 0)
		im_dead3 = blur_img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

		gov_dead = read_ocr(im_dead)
		gov_dead2 = read_ocr(im_dead2)
		gov_dead3 = read_ocr(im_dead3)

		gray = cv2.cvtColor(im_alliance_tag,cv2.COLOR_BGR2GRAY)
		threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
		alliance_tag = pytesseract.image_to_string(threshold_img)
		
		if gov_power == '':
			gov_power = 'Unknown'

		if gov_killpoints == '':
			gov_killpoints = 'Unknown'

		if gov_dead == '' :
			if gov_dead2 == '':
				if gov_dead3 =='':
					gov_dead = 'Unknown'
				
				else:			
					gov_dead = gov_dead3
			
			else:
				gov_dead = gov_dead2

		if gov_kills_tier4 == '' :
			gov_kills_tier4 = '0'

		if gov_kills_tier5 == '' :
			gov_kills_tier5 = '0'
		
		os.system('cls')
		print(f'ID: {gov_id}\nPower: {tointprint(gov_power)}\nTier 4 kills: {tointprint(gov_kills_tier4)}\nTier 5 kills: {tointprint(gov_kills_tier5)}\nGovernor Dead Troops: {tointprint(gov_dead)}')
		print(f'{i+1}/{search_range}') ; os.system(f'title {i+1}/{search_range}')

		device.shell(f'input tap 1396 58')
		time.sleep(0.5)

		device.shell(f'input tap 1365 104')
		time.sleep(1)

		sheet1.write(i+1, 0, tointcheck(gov_id))
		sheet1.write(i+1, 1, tointcheck(gov_power))
		sheet1.write(i+1, 2, tointcheck(gov_killpoints))
		sheet1.write(i+1, 3, tointcheck(gov_dead))
		sheet1.write(i+1, 4, tointcheck(gov_kills_tier4))
		sheet1.write(i+1, 5, tointcheck(gov_kills_tier5))

except:
	print('An issue has occured. Please rerun the tool and use "resume scan option" from where tool stopped.')
	traceback.print_exc()
	pass

file_name_prefix = 'TOP'

if add_sum:
	sheet1.write(0, 6, 'Power Sum', style)
	sheet1.write(1, 6, xlwt.Formula(f'SUM(B2:B{search_range+1})'))

	sheet1.write(0, 7, 'Killpoints Sum', style)
	sheet1.write(1, 7, xlwt.Formula(f'SUM(C2:C{search_range+1})'))

wb.save(f'{kingdom}_{str(search_range)}_{str(today)}.xls')