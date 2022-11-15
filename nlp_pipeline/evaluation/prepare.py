# Rozdziela dane w katalogu <work>/data/<user> (z brata) na dane treningowe (80%) wg informacji o ukonczonych anotacjach zawartych w pliku <work>/anotacje.tsv
# Uzycie: python prepare.py <workdir>
import sys
import os
import re
import random
import shutil


class EvaluationPreparation():

	def prepare(self, work_dir):

		workdir=work_dir
		allusers=['mrakowski','karszym','mborkowska']
		foldDict={}
		random.seed(0)
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
			if user=='all':
				usernames=allusers
			else:
				usernames=[user]
			for username in usernames:
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
				if filename in foldDict:
					outof10=foldDict[filename]
				else:
					outof10=random.randrange(10)
					foldDict[filename]=outof10
				if outof10<2:
					portion="test"
				else:
					portion="train"
				txtpathD=workdir+"/"+portion+"/"+username+"_"+filename
				annpathD=re.sub('\\.txt$','.ann',txtpathD)
				shutil.copyfile(txtpath,txtpathD)
				shutil.copyfile(annpath,annpathD)
				counter=counter+1

		print(counter)


