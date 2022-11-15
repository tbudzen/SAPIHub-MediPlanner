import sys

inPath=sys.argv[1]
outPath=sys.argv[2]

out=open(outPath,"w")
print("Processing file "+inPath)
currentCategory=None
currentStart=None
currentEnd=None
currentString=None
counter=1
counterT=1
for line in open(inPath):
	parts=line.split("\t")
	tag=parts[-1].strip()
	if len(parts)==1:
		continue
	if tag=="o":
		if not currentCategory is None:
			out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
			counterT=counterT+1
			currentCategory=None
	elif tag.startswith("b-"):
		if not currentCategory is None:
			out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
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
				out.write("T"+str(counterT)+"\t"+currentCategory+" "+str(currentStart)+" "+str(currentEnd)+"\t"+currentString+"\n")
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

out.close()
