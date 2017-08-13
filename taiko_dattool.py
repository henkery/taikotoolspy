#!/usr/bin/env python3

import sys
import struct
import simplejson as json
from io import StringIO

class taiko_dattool:
	def __init__():
		self.var = 0

	def decode(file, mode, specialmode):
		#mode 0 musicinfo mode
		#mode 1 songinfo mode
		strings = {}
		with open(file, mode='rb') as f:
			values = struct.unpack('iiii', f.read(16))
			entries = values[0]
			unk = values[1]
			tableOffset = values[2]
			unk2 = values[3]
			#mainkey = values[4].decode("utf-8")

			#mainkey = struct.unpack('16s', f.read(16))[0].decode("utf-8")
			mainkey = "hello"
			strings[mainkey] = {}

			i = 0
			while i < entries:
				strings[mainkey][i] = {}
				print("attempting to read entry "+str(i))
				mystery_data = b""
				if mode == 0:
					byteread = f.read(12)
					values = struct.unpack('i', byteread[0:4]) # 8 bytes of mystery data
					mystery_data = str(byteread[4:12])
				elif mode == 1:
					bytestoread = 64
					if specialmode:
						bytestoread+=4
					byteread = f.read(bytestoread) # 40 bytes of mystery data
					values = struct.unpack('iiiiii', byteread[0:24])
					mystery_data = str(byteread[24:bytestoread])
					
				print(values)
				

				o = 0
				total = len(values)/2
				while o < total:
					keyOffset = values[o]				
					
					#unk3 = values[2]
					curOffset = f.tell()

					print("f.tell gives "+str(curOffset))


					keyBytes = b""

					print("seeking to "+str(keyOffset))

					f.seek(keyOffset) # might be wrong
					byte = f.read(1)
					while byte != b"\x00" and byte != b"":
						#print("byte is "+str(byte))
						keyBytes+=byte
						byte = f.read(1)

					key1 = keyBytes.decode("utf-8")
					print(key1)

					string1 = ""
					if mode == 1:
						stringOffset = values[o+1]
						f.seek(stringOffset)
						stringBytes = b""
						byte = f.read(1)
						while byte != b"\x00" and byte != b"":
							stringBytes+=byte
							byte = f.read(1)

						

						string1 = stringBytes.decode("utf-8")
						print(string1)
					f.seek(curOffset)


					strings[mainkey][i][key1] = string1
					o+=2

				strings[mainkey][i]["mystery"] = mystery_data
				i+=1
		newfilename = filename.split(".")[0]+".json"
		print ("writing result to "+newfilename)
		with open(newfilename, mode='w') as f:
			f.write(json.dumps(strings,ensure_ascii=False, encoding="utf-8"))

	def calcpadding(address):
		padding = 16 - (address % 16)
		if padding == 0:
			padding = 16
		return padding
		

	def genpadding(count):
		byte = b""
		i = 0
		while i < count:
			byte+= b"\x00"
			i+=1
		return byte

	def encode(filename, mode, specialmode):
		#mode 0 musicinfo mode
		#mode 1 songinfo mode
		indexbuffer = b""
		tablebuffer = b""
		strings = None
		with open(filename) as f:
			strings = json.load(f)
		mainkey = list(strings.keys())[0]
		entries = len(strings[mainkey])
		indexbuffer += struct.pack('iiii', entries , 16, 0, 0) #not sure why
		bytestoread = 0
		tableOffset = 16
		if mode == 0:
			bytestoread = 12
			tableOffset += entries*12
		elif mode == 1:
			bytestoread = 64
			if specialmode:
				bytestoread+=4
			tableOffset += entries*bytestoread
		#tableOffsetdiff = taiko_dattool.calcpadding(tableOffset)
		#tablebuffer+=taiko_dattool.genpadding(tableOffsetdiff) # or at the end of tablebuffer
		#tableOffset+=tableOffsetdiff
		indexpointer = 16
		tableOffset+=16

		i = 0
		keyOffset = tableOffset
		while i < entries:
#				mystery_data = b""
#				if mode == 0:
#					byteread = f.read(12)
#					values = struct.unpack('i', byteread[0:4]) # 8 bytes of mystery data
#					mystery_data = str(byteread[4:12])
#				elif mode == 1:
#					bytestoread = 64
#					if specialmode:
#						bytestoread+=4
#					byteread = f.read(bytestoread) # 40 bytes of mystery data
#					values = struct.unpack('iiiiii', byteread[0:24])
#					mystery_data = str(byteread[24:bytestoread])
#					
#				print(values)
			
			total = (len(strings[mainkey][str(i)])-1)/2

			localkeys = {"SLKEY":"", "SONGKEY":"", "MYSTKEY":""}
			for key in strings[mainkey][str(i)].keys():
				if key.startswith("SL_"):
					localkeys["SLKEY"] = key
				elif "mystery" in key:
					localkeys["MYSTKEY"] = key
				else:
					localkeys["SONGKEY"] = key

			collection = {}
			if mode == 0:
				collection = ["SONGKEY"]
			elif mode == 1:
				collection = ["SLKEY", "SONGKEY"]

			for key in collection:
				keyOffset = tableOffset
				indexbuffer += struct.pack('i', keyOffset)
				indexpointer+=4
				
				keyBytes = localkeys[key] # strings[mainkey][str(i)]

				tablebuffer += struct.pack(str(len(keyBytes))+'s', keyBytes.encode("utf-8"))
				tablebuffer += b"\x00"

				tableOffset+= len(keyBytes)+1

				#padding
				#tableOffsetdiff += taiko_dattool.calcpadding(tableOffset)
				#tablebuffer+= taiko_dattool.genpadding(tableOffsetdiff)
				#tableOffset += tableOffsetdiff


				string1 = ""
				if mode == 1:
					stringOffset = tableOffset
					stringBytes = strings[mainkey][str(i)][localkeys[key]]
					tablebuffer+= struct.pack(str(len(stringBytes))+'s', stringBytes.encode("utf-8"))
					tablebuffer += b"\x00"
					tableOffset+= len(stringBytes)+1

					#tableOffsetdiff += taiko_dattool.calcpadding(tableOffset)
					#tablebuffer+= taiko_dattool.genpadding(tableOffsetdiff)
					#tableOffset += tableOffsetdiff

					indexbuffer+=struct.pack('i', stringOffset)
					indexpointer+=4

			mysterybytes = eval(strings[mainkey][str(i)]["mystery"])
			if len(mysterybytes)>bytestoread:
				mysterybytes = mysterybytes[0:bytestoread]
			if len(mysterybytes)<bytestoread:
				mysterybytes = taiko_dattool.genpadding(bytestoread-len(mysterybytes)) + mysterybytes
			indexbuffer += struct.pack(str(len(mysterybytes))+'s', mysterybytes)
			indexpointer += len(mysterybytes)


			i+=1
		newfilename = filename.split(".")[0]+".dat"
		with open(newfilename, mode='wb') as f:
			f.write(indexbuffer)
			f.write(tablebuffer)

filename = sys.argv[1]
specialmode = False
if len(sys.argv) > 2:
	specialmode = True
modeswitch = filename.split("/")[-1].split(".")[0]
mode = 0
if modeswitch == "MusicInfo": # it seems the data format changes per input file
								# 	without changes in the header
	mode = 0
elif modeswitch == "SongInfo":
	mode = 1

if filename.endswith(".dat"):
	taiko_dattool.decode(filename, mode, specialmode) # specialmode is for ao/aka ban files which contain more padding for some reason
elif filename.endswith(".json"):
	taiko_dattool.encode(filename, mode, specialmode)
else:
	print ("incorrect filename, please give a .dat or .json file")