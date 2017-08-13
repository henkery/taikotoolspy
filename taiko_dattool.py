#!/usr/bin/env python3

import sys
import struct

class taiko_dattool:
	def __init__():
		self.var = 0

	def decode(file, mode):
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

			print(values)
			print(mainkey)

			i = 0
			while i < entries:
				print("attempting to read entry "+str(i))
				if mode == 0:
					values = struct.unpack('iii', f.read(12))
				elif mode == 1:
					byteread = f.read(64) # 40 bytes of mystery data
					values = struct.unpack('ii', byteread[0:8])
				print(values)
				i+=1
				keyOffset = values[0]
				stringOffset = values[1]
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
					f.seek(stringOffset)
					stringBytes = b""
					byte = f.read(1)
					while byte != b"\x00" and byte != b"":
						stringBytes+=byte
						byte = f.read(1)

					

					string1 = stringBytes.decode("utf-8")
					print(string1)
				f.seek(curOffset)


				strings[mainkey][key1] = string1
		print(strings)

taiko_dattool.decode("/mnt/yukari/Mai Torrent/Tested/Taiko no Tatsujin V/PCSG00551/_data/system/MusicInfo.dat", 0)