import sys
import shutil
import os

class Deconversion():

	def deconversion(self, input_dir, output_dir):

		inPath = input_dir
		outPath = output_dir

		out=open(outPath,"w+", encoding="utf-8", errors='ignore')
		print("Processing file "+inPath)
		currentCategory=None
		currentStart=None
		currentEnd=None
		currentString=None
		counter=1
		counterT=1
		try:
			if not os.path.isfile(inPath):
				print("File doesn't exist: " + inPath)
			f_in = open(inPath, encoding="utf-8", errors='ignore')
			lines = f_in.readlines()
			for line in lines:
				parts=line.split("\t")
				tag=parts[-1].strip()
				if len(parts)==1:
					continue
				if tag=="o":
					if not currentCategory is None:
						try:
							out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
						except UnicodeEncodeError as e:
							print("UnicodeEncodeError: " + str(e))
						counterT=counterT+1
						currentCategory=None
				elif tag.startswith("b-"):
					if not currentCategory is None:
						try:
							out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
						except UnicodeEncodeError as e:
							print("UnicodeEncodeError: " + str(e))
						counterT=counterT+1
					currentCategory=tag[2:]
					currentStart=int(parts[-3])
					currentEnd=currentStart+int(parts[-2])
					currentString=parts[0]
				elif tag.startswith("i-"):
					thisCategory=tag[2:]
					if currentCategory is None or currentCategory!=thisCategory:
						print("Unexpected tag: "+tag+" in line "+str(counter))
						if not currentCategory is None:
							try:
								out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
							except UnicodeEncodeError as e:
								print("UnicodeEncodeError: " + str(e))
							counterT=counterT+1
						currentCategory=tag[2:]
						currentStart=int(parts[-3])
						currentEnd=currentStart+int(parts[-2])
						currentString=parts[0]
					else:
						thisStart=int(parts[-3])
						if currentEnd!=thisStart:
							currentString=currentString+" "
						currentString=currentString+parts[0]
						currentEnd=thisStart+int(parts[-2])

				else:
					print("Unexpected line: "+line)
					sys.exit(-1)
				counter=counter+1
		except UnicodeDecodeError as e:
			print('UnicodeDecodeError: ' + str(e))
		out.close()
