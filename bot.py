import datetime
import time
import cv2
from PIL import ImageGrab
import numpy as np
import pyautogui   
import time
#from queue import Queue
#from threading import Thread

#visit site http://www.trex-game.skipser.com/

class cordinates():
	replay = (480, 400)
	dinosaur = (236, 408)

class agent():
	width = 40
	height = 43
	name = 'dinosaur'

def restart_game():
	pyautogui.click(cordinates.replay)

def big_jump():
	pyautogui.keyDown('space')
	time.sleep(0.01)
	pyautogui.keyUp('space')

def screenShot():
	box = (cordinates.dinosaur[0]-50, cordinates.dinosaur[1]-70,
			cordinates.dinosaur[0]+600, cordinates.dinosaur[1]+60)
	image = np.array(ImageGrab.grab(bbox=box).convert('RGB'))
	return image

def procssImage(img):
	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	#gray = cv2.GaussianBlur(gray, (21, 21), 0)
	return gray

def worker(input_q):
	while True:
		if input_q.empty():
			pass
		else:
			frame = input_q.get()
			cv2.imshow('Captured', frame)
			cv2.waitKey(1)

if __name__ == '__main__':
	restart_game()
	baseFrame = None
	nearest_obstacle = 1000000 # insane far obstacle
	game_over =  False

	'''
	input_q = Queue(5)  # fps is better if queue is higher but then more lags
	for i in range(1):
		t = Thread(target=worker, args=(input_q,))
		#t.daemon = True
		t.start()
	'''

	while True:
		frame = screenShot()
		image = procssImage(frame)
		if baseFrame is None:
			baseFrame = image
			continue

		bin_ada = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2);
		img,contours, hierachy = cv2.findContours(bin_ada,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE);

		left_edges = []
		obstacles = []
		# loop over the contours
		for c in contours:
			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			if w > 60 or w < 10 or h < 18:
				continue
			if x < cordinates.dinosaur[0]:
				cv2.rectangle(frame, (x, y), (x + w, y + h), (133, 144, 155), 1)
				continue
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
			left_edges.append(x)
			obstacles.append([x, y, w, h])

		if len(left_edges) >= 1:
			approaching = np.min(left_edges)
			if nearest_obstacle > approaching:
				nearest_obstacle = approaching
			else:
				# we must hit gave over here as no obstale is approaching anymore
				cv2.destroyAllWindows()
				print ("GAME OVER")
				game_over = True
				break
			#print (nearest_obtacle)
			#if nearest_obtacle <= 60:
			#	big_jump()

		cv2.imshow('Captured', frame)
		cv2.waitKey(1)
