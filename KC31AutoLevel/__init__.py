import glob
import sys
import serial.tools.list_ports
import msgpack
import time
import json
import requests
import IPython
import os
import logging
import numpy as np
import traceback

from threading import Timer

from flask import Flask, render_template, jsonify, redirect, request
from KC31AutoLevel import serialDevice

serialPort = None

app = Flask(__name__,
			static_url_path='', 
			static_folder='static',
			template_folder='templates')

from  KC31AutoLevel import serialDevice

def boot():
	#this will likely happen twice
	requests.get("http://localhost:4444/")

def onOpen():
	try:
		#this will likely happen twice
		bootTimer = Timer(2.0, boot)
		bootTimer.start()
	except Exception as e:
		print("Open failed : " + str(e))
		

onOpen()

@app.before_first_request
def init():
	global serialPort
	print("Initializing")
	serialPort = serialDevice.SerialDevice("COM20")
	serialPort.open()

	#dont log requests
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.WARNING)

@app.route('/values')
def values():
	global serialPort
	values = serialPort.getValues()
	return jsonify({
		"x" : values[0],
		"y" : values[1]
	})

@app.route("/", methods=['POST', 'GET'])
def update():
	response = {
		"success" : True
	}
	ipAddress = "192.168.0.1"

	if request.method == 'POST':
		try:
			ipAddress = request.form['ipAddress']
			values = np.float32(serialPort.getValues())
			if ipAddress == "":
				raise Exception("No IP address specified")

			polarity = np.float32([+1.0, -1.0])

			walkAmount = values * polarity / 360.0 * 9000.0

			for i in range(2):
				if(walkAmount[i] != walkAmount[i]):
					raise(Exception("Readings are NaN"))

				if not abs(walkAmount[i]) < 300:
					raise(Exception("Cannot walk more than 300 steps during auto-levelling. Axis " + str(i + 1)))
				message = {
					"app" : {
						"axis" : {
							"walk" : int(round(walkAmount[i]))
						}
					}
				}
				url = "http://" + ipAddress + ":5000/axis/" + str(i+1) + "/sendCommand"
				postResult = requests.post(url, json=message)
				data = json.loads(postResult.content.decode("utf-8"))
				if not data['success']:
					print(data['traceback'])
					raise(Exception(data['error']))
		except Exception as e:
			response = {
				"success" : False,
				"error" : str(e),
				"traceback" : traceback.format_exc()
			}
	
	return render_template("form.html"
		, response=response
		, ipAddress=ipAddress)

@app.route("/faceDown", methods=['POST'])
def faceDown():
	try:
		incomingMessage = request.json
		message = {
			"app" : {
				"axis" : {
					"navigateTo" : 4500
				}
			}
		}
		url = "http://" + incomingMessage['ipAddress'] + ":5000/axis/1/sendCommand"
		postResult = requests.post(url, json=message)
		return jsonify({
			"success" : True
		})
	except Exception as e:
		return jsonify({
			"success" : False,
			"error" : str(e),
			"traceback" : traceback.format_exc()
		})

@app.route("/setDatum", methods=['POST', 'GET'])
def setDatum():
	try:
		incomingMessage = request.json
		url = "http://" + incomingMessage['ipAddress'] + ":5000/datum/set"
	
		postResult = requests.get(url)
		content = json.loads(postResult.content.decode("utf-8"))
		if not content['success']:
			return content
		
		return jsonify({
			"success" : True,
			"timestamp" : postResult
		})
	except Exception as e:
		return jsonify({
			"success" : False,
			"error" : str(e),
			"traceback" : traceback.format_exc()
		})
