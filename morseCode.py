import cv2
import numpy as np 
import time

class MorseImageDecoder(object):
	def __init__(self):
		self.morseCodeData={'01':'A','1000':'B','1010':'C','100':'D','0':'E','0010':'F','110':'G','0000':'H'
							,'00':'I','0111':'J','101':'K','0100':'L','11':'M','10':'N','111':'O','0110':'P'
							,'1101':'Q','010':'R','000':'S','1':'T','001':'U','0001':'V','011':'W','1001':'X'
							,'1011':'Y','1100':'Z'
							}


		self.image = cv2.imread('images/morsecoa.jpg')
		# self.image = cv2.imread('images/morsecok.jpg')
		# self.image = cv2.imread('images/morsecoc.jpg')
		# self.image = cv2.imread('images/morsecoe.jpg')
		# self.image = cv2.imread('images/morsecof.jpg')
		# self.image = cv2.imread('images/morsecoh.jpg')
		# self.image = cv2.imread('images/morsecoj.jpg')
		
		self.finalData = []
		self.changeSizeflag = 0

	def filterImage(self):
		print(self.image.shape)
		if self.image.shape[0] <= 3000 and self.image.shape[0] >= 2000:
			self.changeSizeflag = 1

		# elif self.image.shape[1] >=2000:
		# 	self.image = cv2.resize(self.image,(600,700),interpolation=cv2.INTER_CUBIC)
		# else:
		self.image = cv2.resize(self.image,(650,700),interpolation=cv2.INTER_CUBIC)
		cv2.imshow('Image',self.image)	
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		grayImage = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
		# cv2.imshow('Gray Image',grayImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()

		threshImage = cv2.adaptiveThreshold(grayImage,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,45,15)
		#_,threshImage = cv2.threshold(grayImage,127,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		# cv2.imshow('Thresh Image',threshImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
		kernel = np.ones((5,5),np.uint8)
		morphImage = cv2.morphologyEx(threshImage, cv2.MORPH_CLOSE, kernel)
		# cv2.imshow('Morph Image',morphImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()

		kernel = np.ones((5,5),np.uint8)
		erodeImage = cv2.erode(morphImage,kernel,iterations = 1)
		# erodeImage = cv2.dilate(morphImage,kernel,iterations = 1)
		# cv2.imshow('Erode Image',erodeImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()
		
		# https://stackoverflow.com/a/58290380 [Thanks to Ricardo Abe for the answer, opencv modified the findContour fn]
		# Thanks to @mazharmachu28 for finding the bug [old findContour method return values]
		# old: contour = cv2.findContours(erodeImage.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[1]
		contour = cv2.findContours(erodeImage.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[0]
		copyImage = np.zeros((self.image.shape[0],self.image.shape[1],3),dtype='uint8')
		# cv2.drawContours(copyImage,contour,-1,(0,0,255),1)
		# cv2.imshow('Con Image',copyImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()		

		for cnt in contour:
			accuracy = 0.0001*cv2.arcLength(cnt,True)
			approx = cv2.approxPolyDP(cnt,accuracy,True)
			hull   = cv2.convexHull(approx)
			area = cv2.contourArea(hull)
			if area<=3000:
				# cv2.drawContours(copyImage,[hull],0,(0,0,255),1)
				x,y,w,h = cv2.boundingRect(hull)
				# print(str(w)+','+str(h))
				cv2.rectangle(copyImage,(x,y),(x+w,y+h),(0,255,0),-1)

		# cv2.imshow('Copy Image', copyImage)	
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()		

		copyImage = copyImage[:,:,1]
		if self.changeSizeflag == 0:
			self.image = cv2.resize(copyImage,(400,300),interpolation=cv2.INTER_CUBIC)
		else:	
			self.image = cv2.resize(copyImage,(300,200),interpolation=cv2.INTER_CUBIC)
		self.finalImage = self.image.copy()

		# kernel = np.ones((3,3),np.uint8)
		# erodeImage = cv2.dilate(morphImage,kernel,iterations = 1)
		# cv2.imshow('Resize Image',self.image)
		# cv2.waitKey(0)
		# cv2.destroyAllWindows()


	def mainAlgo(self):
		startCordList = []
		morseList = []
		startCord = (0,0)
		endCord = (0,0)
		for i in range(self.image.shape[0]):

			balckDotCount = 0
			whiteDotCount = 0
			morseText = ''
			startCord = (0,0)
			
			for j in range(self.image.shape[1]):
				if self.image[i,j]==0:
					if whiteDotCount>=30:
						morseText+='1'
					elif whiteDotCount<30 and whiteDotCount>=10:	
						morseText+='0'
					balckDotCount+=1
					whiteDotCount = 0

				elif self.image[i,j]>0:
					if startCord == (0,0):
						startCord = (i,j)

					balckDotCount = 0
					whiteDotCount+=1

			if morseText!='':
				startCordList.append((startCord[1],startCord[0]))
				morseList.append(morseText)
				startCord = (0,0)

			elif len(morseList)>0:
				currMax = 0
				data = ''
				loc = 0
				for i,item in enumerate(morseList):
					if len(item)>currMax:
						currMax = len(item)
						data = item
						loc = i

				morseList = []
				# print(data)
				try:
					self.finalData.append(self.morseCodeData[data])
					cv2.putText(self.finalImage,self.morseCodeData[data],(startCordList[loc][0]-30,startCordList[loc][1]+20),2,0.7,(255,255,255),1)

				except:
					print(data)
					self.finalData.append('')
				finally:
					startCordList = []
					startCord = (0,0)
					endCord = (0,0)
			i+=10


	def printFinalData(self):
		cv2.imshow('FinalData Image',self.finalImage)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		for item in self.finalData:
			print(item)


if __name__ == "__main__":
	obj = MorseImageDecoder()
	obj.filterImage()
	obj.mainAlgo()
	obj.printFinalData()
