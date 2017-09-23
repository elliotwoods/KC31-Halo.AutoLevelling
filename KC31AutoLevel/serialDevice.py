import sys
import serial.tools.list_ports
import threading
import queue
import time
from io import BytesIO
from IPython import embed

serialDeviceDebugEnabled = False

class SerialDevice:
	def __init__(self, port, baudRate = 9600):
		self.listeners = []
		self.port = port
		self.baudRate = baudRate
		self.sendQueue = queue.Queue()
		self.values = [None, None]

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
	
	def open(self):
		self.close()
		self.keepOpen = True
		self.thread = threading.Thread(target = self._threadedFunction)

		self.openSuccessQueue = queue.Queue()		
		self.thread.start()
		success = self.openSuccessQueue.get(block = True)
		del self.openSuccessQueue
		return success

	def close(self):
		self.keepOpen = False
		try:
			self.thread.join()
			del self.thread
		except:
			pass

	def getValues(self):
		return self.values

	def _threadedFunction(self):
		try:
			serialPort = serial.Serial(self.port, baudrate = self.baudRate)
			if(not serialPort.is_open):
				serialPort.open()
			print("Serial port [" + self.port + "] opened")
			self.openSuccessQueue.put(True)
		except Exception as e:
			print("Serial port [" + self.port + "] failed to open : " + str(e))
			self.keepOpen = False
			self.openSuccessQueue.put(False)
			return
		
		xString = ""
		yString = ""
		
		while(self.keepOpen):
			selectOutput = 0
			try:
				while serialPort.in_waiting > 0:
					data = serialPort.read(1).decode("utf-8")
					if data == 'X':
						selectOutput = 0
						try:
							self.values[selectOutput] = float(xString) / 100
						except:
							pass
						xString = ""
					elif data == 'Y':
						selectOutput = 1
						try:
							self.values[selectOutput] = float(yString) / 100
						except:
							pass
						yString = ""
					else:
						if selectOutput == 0:
							xString += data
						else:
							yString += data
			except Exception as e:
				print("Exception in serial thread : "  + str(e))

		print("Serial port [" + self.port + "] closed")
		serialPort.close()

def listSerialDevices(tryOpenDevice = False):
	return list(serial.tools.list_ports.comports());