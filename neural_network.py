import cv2
import numpy as np
import pickle
import sys

def read_ocr(image):

	def digits_read(im):
		
		gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
		thresh = cv2.adaptiveThreshold(gray,255,1,1,11,2)

		contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
		samples =  np.empty((0,100))

		li = []
		for cnt in contours:
			if cv2.contourArea(cnt)>20:
				[x,y,w,h] = cv2.boundingRect(cnt)
				li.append([x,y,w,h])

		li = sorted(li,key=lambda x: x[0], reverse=True)
		for i in li:
			x,y,w,h = i[0], i[1], i[2], i[3]

			if  h>15 and h<30 and w<40 and w>7:
				cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
				roi = thresh[y:y+h,x:x+w]
				roismall = cv2.resize(roi,(10,10))
				sample = roismall.reshape((1,100))
				samples = np.append(samples,sample,0)

		return samples

	def classify(data):
		clas = []
		if isinstance(data, bool):
			return 0
		if isinstance(data, int):
			return data
		for i in data:
			a = int(digits_model.predict([i])[0])
			if a == 11:
				a = 44
			clas.append(a)

		clas.reverse()
		clas = map(str, clas)
		clas = ''.join(clas)
		return clas

	try:
		digits_model = pickle.load(open('digits_model.sav', 'rb'))
	
	except:
		print("No models found")
		sys.exit()
	
	return int(classify(digits_read(image)))