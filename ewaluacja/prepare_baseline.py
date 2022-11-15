# Rozdziela dane znakowane rownolegle w katalogu <work>/data/<user> (z brata) na dane pochodzace od roznych znakujacych (jeden w 'gold', drugi w 'candidate') wg informacji o ukonczonych anotacjach zawartych w pliku <work>/anotacje.tsv
# Uzycie: python prepare-baseline.py <workdir>
import sys
import os
import re
import random
import shutil

workdir=sys.argv[1]
allusers=['mrakowski','karszym','mborkowska']
allusersS=['mborkowska','mrakowski','karszym']
counter=0
for line in open(workdir+"/anotacje.tsv"):
	parts=line.split("\t")
	status=parts[3]
	if status!="oznakowane":
		continue
	comments=parts[4]
	if comments!="\n" and comments!="zweryfikowane all\n" and comments!="zweryfikowano all\n":
		print("Skipping due to comment: "+comments.strip())
		continue
	filename=parts[1]
	if not filename.endswith(".txt"):
			filename=filename+".txt"
	user=parts[2].strip()
	if user!='all':
		continue
	for i in range(len(allusers)):
		if counter%2==0:
			goldUser=allusers[i]
			candidateUser=allusersS[i]
		else:
			goldUser=allusersS[i]
			candidateUser=allusers[i]
		outprefix=goldUser+"_"+candidateUser
		for (username,portion) in [(goldUser,'gold'),(candidateUser,'candidate')]:
			txtpath=workdir+"/data/"+username+"/"+filename
			if not os.path.isfile(txtpath):
				print("Expected file missing: "+txtpath)
				continue
				#sys.exit(-1)
			annpath=re.sub('\\.txt$','.ann',txtpath)
			if not os.path.isfile(annpath):
				print("Expected file missing: "+annpath)
				sys.exit(-1)
			if os.stat(annpath).st_size==0:
				print("Expected file empty: "+annpath)
				#sys.exit(-1)
			txtpathD=workdir+"/"+portion+"/"+outprefix+"_"+filename
			annpathD=re.sub('\\.txt$','.ann',txtpathD)
			shutil.copyfile(txtpath,txtpathD)
			shutil.copyfile(annpath,annpathD)
	counter=counter+1

print(counter)
		
		
