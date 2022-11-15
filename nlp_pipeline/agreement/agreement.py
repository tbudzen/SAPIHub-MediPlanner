import os

class Agreement():

	def readAnn(self, path):
		entities=self.readEntities(path)
		attributes=self.readAttributes(path,entities)
		normalisations=self.readNormalisations(path,entities)
		relations=self.readRelations(path,entities)
		return([entities,attributes,normalisations,relations])

	def readEntities(self, path):
		entities={}
		try:
			for line in open(path, encoding="utf-8", errors='ignore'):
				parts=line.split('\t')
				if parts[0][0]!='T':
					continue
				idd=parts[0]
				text=parts[2].strip()
				parts=parts[1].split(' ')
				category=parts[0]
				if category=='NOTE':
					continue
				begin=int(parts[1])
				if ';' in parts[2]:
					print("Ignoring multi-segment entity.")
					continue
				end=int(parts[2])
				entity={'category':category,'begin':begin,'end':end,'text':text}
				entities[idd]=entity
		except UnicodeDecodeError as e:
			print("UnicodeDecodeError: " + str(e))
		print("Read "+str(len(entities))+" entites.")
		return(entities)

	# Attributes under an assumption there is only one atytribute possible - 'History'
	def readAttributes(self, path,entities):
		attributes={}
		try:
			for line in open(path, encoding="utf-8", errors='ignore'):
				parts=line.split('\t')
				if parts[0][0]!='A':
					continue
				idd=parts[0]
				parts=parts[1].split(' ')
				attributeType=parts[0]
				entityId=parts[1]
				value=parts[2].strip()
				#assert(entityId in entities)
				if not entityId in entities:
					continue
				if attributeType=='Source' and value=='Confirmed':
				#	print('IGNORE')
					continue
				#else:
				#	print('ADDING '+attributeType+" : "+value)
				entry={'entity':entityId,'type':attributeType,'value':value}
				attributes[idd]=entry
		except UnicodeDecodeError as e:
			print("UnicodeDecodeError: " + str(e))
		print("Added "+str(len(attributes))+" attributes.")
		return(attributes)

	def readNormalisations(self, path,entities):
		normalisations={}
		try:
			for line in open(path, encoding="utf-8", errors='ignore'):
				parts=line.split('\t')
				if parts[0][0]!='N':
					continue
				idd=parts[0]
				text=parts[2].strip()
				parts=parts[1].split(' ')
				entityId=parts[1]
				concept=parts[2]
				#assert(entityId in entities)
				if not entityId in entities:
					continue
				entry={'entity':entityId,'concept':concept}
				normalisations[idd]=entry
		except UnicodeDecodeError as e:
			print("UnicodeDecodeError: " + str(e))
		print("Added "+str(len(normalisations))+" normalisations.")
		return(normalisations)

	def readRelations(self, path,entities):
		relations={}
		try:
			for line in open(path, encoding="utf-8", errors='ignore'):
				parts=line.split('\t')
				if parts[0][0]!='R':
					continue
				idd=parts[0]
				parts=parts[1].strip().split(' ')
				typer=parts[0]
				assert(parts[1].startswith('Arg1:'))
				source=parts[1][(len('Arg1:')):]
				assert(parts[2].startswith('Arg2:'))
				destination=parts[2][(len('Arg2:')):]
				#assert(source in entities)
				if not source in entities:
					continue
				#assert(destination in entities)
				if not destination in entities:
					continue
				entry={'category':typer,'source':source,'destination':destination}
				relations[idd]=entry
		except UnicodeDecodeError as e:
			print("UnicodeDecodeError: " + str(e))
		print("Added "+str(len(relations))+" relations.")
		return(relations)

	def match(self, entityId1,entity1,entityId2,entity2,relaxed):
		if ('~' in entityId1) or ('~' in entityId2):
			if entityId1[0:entityId1.find('~')]!=entityId2[0:entityId2.find('~')]:
				return(False)
		if not relaxed:
			return(entity1['begin']==entity2['begin'] and entity1['end']==entity2['end'])
		if entity1['begin']>=entity2['begin'] and entity1['begin']<entity2['end']:
			return(True)
		if entity1['end']>entity2['begin'] and entity1['end']<=entity2['end']:
			return(True)
		if entity2['begin']>=entity1['begin'] and entity2['begin']<entity1['end']:
			return(True)
		if entity2['end']>entity1['begin'] and entity2['end']<=entity1['end']:
			return(True)
		return(False)

	def findMatchingEntity(self,entityId,entity,visitedC,entitiesAnn,relaxed):
		for entityC in sorted(entitiesAnn.keys()):
			if entityC in visitedC:
				continue
			if self.match(entityId,entity,entityC,entitiesAnn[entityC],relaxed):
				return(entityC)
		return(None)


	def compareEntities(self,goldAnn,candidateAnn,relaxed):
		comparison={'TP':[],'FP':[],'FN':[],'TN':[]}
		visitedC=[]
		for entityG in sorted(goldAnn[0].keys()):
			entityC=self.findMatchingEntity(entityG,goldAnn[0][entityG],visitedC,candidateAnn[0],relaxed)
			if entityC is None:
				comparison['FN'].append((entityG,None))
			else:
				comparison['TP'].append((entityG,entityC))
				visitedC.append(entityC)
		for entityC in candidateAnn[0]:
			if not entityC in visitedC:
				comparison['FP'].append((None,entityC))
		print('Finished comparison with TP='+str(len(comparison['TP']))+" FN="+str(len(comparison['FN']))+" FP="+str(len(comparison['FP']))+" TN="+str(len(comparison['TN'])))
		return(comparison)

	def compareAttributes(self, entityComparison,goldAnn,candidateAnn):
		comparison={'OK':[],'NOK':[],'UD':[]}
		visitedC=[]
		for attributeG in sorted(goldAnn[1].keys()):
			entityG=goldAnn[1][attributeG]['entity']
			entityC=None
			for (eG,eC) in entityComparison['TP']:
				if eG==entityG:
					entityC=eC
					break
			if entityC is None:
				comparison['UD'].append((attributeG,None))
				continue
			valueG=goldAnn[1][attributeG]['value']
			typeG=goldAnn[1][attributeG]['type']
			valueC=None
			attributeC=None
			for attC in sorted(candidateAnn[1].keys()):
				if candidateAnn[1][attC]['entity']==entityC and typeG==candidateAnn[1][attC]['type']:
					valueC=candidateAnn[1][attC]['value']
					attributeC=attC
					break
			if valueC is None:
				comparison['NOK'].append((attributeG,None))
			else:
				visitedC.append(attributeC)
				if valueC==valueG:
					comparison['OK'].append((attributeG,attributeC))
				else:
					comparison['NOK'].append((attributeG,attributeC))
		for attributeC in sorted(candidateAnn[1].keys()):
			if not attributeC in visitedC:
				entityC=candidateAnn[1][attributeC]['entity']
				entityG=None
				for (eG,eC) in entityComparison['TP']:
					if eC==entityC:
						entityG=eG
						break
				if entityG is None:
					comparison['UD'].append((None,attributeC))
				else:
					comparison['NOK'].append((None,attributeC))
		print('Finished attribute comparison with OK='+str(len(comparison['OK']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
		return(comparison)

	def compareNormalisations(self, entityComparison,goldAnn,candidateAnn):
		comparison={'OK':[],'NOK':[],'UD':[]}
		visitedC=[]
		for normalisationG in sorted(goldAnn[2].keys()):
			entityG=goldAnn[2][normalisationG]['entity']
			entityC=None
			for (eG,eC) in entityComparison['TP']:
				if eG==entityG:
					entityC=eC
					break
			if entityC is None:
				comparison['UD'].append((normalisationG,None))
				continue
			conceptG=goldAnn[2][normalisationG]['concept']
			conceptC=None
			normalisationC=None
			for normC in sorted(candidateAnn[2].keys()):
				if candidateAnn[2][normC]['entity']==entityC:
					conceptC=candidateAnn[2][normC]['concept']
					normalisationC=normC
					break
			if conceptC is None:
				comparison['NOK'].append((normalisationG,None))
			else:
				visitedC.append(normalisationC)
				if conceptC==conceptG:
					comparison['OK'].append((normalisationG,normalisationC))
				else:
					comparison['NOK'].append((normalisationG,normalisationC))
		for normalisationC in sorted(candidateAnn[2].keys()):
			if not normalisationC in visitedC:
				comparison['UD'].append((None,normalisationC))
		print('Finished normalisation comparison with OK='+str(len(comparison['OK']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
		return(comparison)


	def compareCategories(self, entityComparison,goldAnn,candidateAnn):
		comparison={'OK':[],'NOK':[],'UD':[]}
		for (entityG,entityC) in entityComparison['TP']:
			if goldAnn[0][entityG]['category']==candidateAnn[0][entityC]['category']:
				comparison['OK'].append((entityG,entityC))
			else:
				comparison['NOK'].append((entityG,entityC))
		for (entityG,entityC) in entityComparison['FP']:
			comparison['UD'].append((entityG,entityC))
		for (entityG,entityC) in entityComparison['FN']:
			comparison['UD'].append((entityG,entityC))
		print('Finished category comparison with OK='+str(len(comparison['OK']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
		return(comparison)

	def compareRelations(self, entityComparison,goldAnn,candidateAnn):
		comparison={'OK':[],'NOK':[],'UD':[]}
		visitedC=[]
		for relationG in sorted(goldAnn[3].keys()):
			sourceG=goldAnn[3][relationG]['source']
			sourceC=None
			for (eG,eC) in entityComparison['TP']:
				if eG==sourceG:
					sourceC=eC
					break
			if sourceC is None:
				comparison['UD'].append((relationG,None))
				continue
			destinationG=goldAnn[3][relationG]['destination']
			destinationC=None
			for (eG,eC) in entityComparison['TP']:
				if eG==destinationG:
					destinationC=eC
					break
			if destinationC is None:
				comparison['UD'].append((relationG,None))
				continue
			relationC=None
			for relC in sorted(candidateAnn[3].keys()):
				if candidateAnn[3][relC]['source']==sourceC and candidateAnn[3][relC]['destination']==destinationC:
					relationC=relC
					break
			if relationC is None:
				comparison['NOK'].append((relationG,None))
				continue
			visitedC.append(relationC)
			if goldAnn[3][relationG]['category']==candidateAnn[3][relationC]['category']:
				comparison['OK'].append((relationG,relationC))
			else:
				comparison['NOK'].append((relationG,relationC))
		for relationC in sorted(candidateAnn[3].keys()):
			if not relationC in visitedC:
				comparison['UD'].append((None,relationC))
		print('Finished relation comparison with OK='+str(len(comparison['OK']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
		return(comparison)

	def aggregate(self, comparison1,comparison2):
		for key in comparison1.keys():
			if key in comparison2:
				comparison1[key].extend(comparison2[key])

	def computeF1(self, comparison):
		if (2*len(comparison['TP'])+len(comparison['FP'])+len(comparison['FN']))==0:
			F1=float('nan')
		else:
			F1=2*len(comparison['TP'])*1.0/(2*len(comparison['TP'])+len(comparison['FP'])+len(comparison['FN']))
		return(F1)

	def computeAccuracy(self, comparison):
		if len(comparison['OK'])+len(comparison['NOK'])==0:
			A=float('nan')
		else:
			A=len(comparison['OK'])*1.0/(len(comparison['OK'])+len(comparison['NOK']))
		return(A)

	def computeCertainty(self, comparison):
		if len(comparison['OK'])+len(comparison['NOK'])+len(comparison['UD'])==0:
			return(0)
		K=(len(comparison['OK'])+len(comparison['NOK']))*1.0/(len(comparison['OK'])+len(comparison['NOK'])+len(comparison['UD']))
		return(K)

	def initCache(self, N):
		result=[]
		for i in range(N):
			row=[]
			for j in range(N):
				row.append({})
			result.append(row)
		return(result)

	def addPrefix(self, annotation,prefix):
		(entities,attributes,normalisations,relations)=annotation
		for key in list(entities.keys()):
			entities[prefix+key]=entities.pop(key)
		for key in list(attributes.keys()):
			attribute=attributes.pop(key)
			attribute['entity']=prefix+attribute['entity']
			attributes[prefix+key]=attribute
		for key in list(normalisations.keys()):
			normalisation=normalisations.pop(key)
			normalisation['entity']=prefix+normalisation['entity']
			normalisations[prefix+key]=normalisation
		for key in list(relations.keys()):
			relation=relations.pop(key)
			relation['source']=prefix+relation['source']
			relation['destination']=prefix+relation['destination']
			relations[prefix+key]=relation

	def splitByEntityCategory(self, entityComparison,goldAnn,candidateAnn):
		result=dict()
		for key in entityComparison.keys():
			for pair in entityComparison[key]:
				if not pair[0] is None:
					cat1=goldAnn[0][pair[0]]['category']
					if not cat1 in result:
						result[cat1]={}
					if not key in result[cat1]:
						result[cat1][key]=[]
					result[cat1][key].append(pair)
				if not pair[1] is None:
					cat2=candidateAnn[0][pair[1]]['category']
					if not cat2 in result:
						result[cat2]={}
					if not key in result[cat2]:
						result[cat2][key]=[]
					result[cat2][key].append(pair)
		return(result)

	def splitByRelationCategory(self, relationComparison,goldAnn,candidateAnn):
		result=dict()
		for key in relationComparison.keys():
			for pair in relationComparison[key]:
				if not pair[0] is None:
					cat1=goldAnn[3][pair[0]]['category']
					if not cat1 in result:
						result[cat1]={}
					if not key in result[cat1]:
						result[cat1][key]=[]
					result[cat1][key].append(pair)
				if not pair[1] is None:
					cat2=candidateAnn[3][pair[1]]['category']
					if not cat2 in result:
						result[cat2]={}
					if not key in result[cat2]:
						result[cat2][key]=[]
					result[cat2][key].append(pair)
		return(result)

	def splitByAttributeType(self, attributeComparison,goldAnn,candidateAnn):
		result=dict()
		for key in attributeComparison.keys():
			for pair in attributeComparison[key]:
				if not pair[0] is None:
					cat1=goldAnn[1][pair[0]]['type']
					if not cat1 in result:
						result[cat1]={}
					if not key in result[cat1]:
						result[cat1][key]=[]
					result[cat1][key].append(pair)
				if not pair[1] is None:
					cat2=candidateAnn[1][pair[1]]['type']
					if not cat2 in result:
						result[cat2]={}
					if not key in result[cat2]:
						result[cat2][key]=[]
					result[cat2][key].append(pair)
		return(result)


	def summary(self, annotations,names,outPath):
		entityTotal={'TP':[],'FP':[],'FN':[],'TN':[]}
		categoryTotal={'OK':[],'NOK':[],'UD':[]}
		attributeTotal={'OK':[],'NOK':[],'UD':[]}
		normalisationTotal={'OK':[],'NOK':[],'UD':[]}
		relationTotal={'OK':[],'NOK':[],'UD':[]}
		entityCategoryTotal={'Symptom':{'TP':[],'FP':[],'FN':[],'TN':[]},'Condition':{'TP':[],'FP':[],'FN':[],'TN':[]},'Behaviour':{'TP':[],'FP':[],'FN':[],'TN':[]},'Treatment':{'TP':[],'FP':[],'FN':[],'TN':[]},'Investigation':{'TP':[],'FP':[],'FN':[],'TN':[]},'Investigation_result':{'TP':[],'FP':[],'FN':[],'TN':[]},'Drug':{'TP':[],'FP':[],'FN':[],'TN':[]},'Drug_dose':{'TP':[],'FP':[],'FN':[],'TN':[]},'Negation':{'TP':[],'FP':[],'FN':[],'TN':[]},'Date':{'TP':[],'FP':[],'FN':[],'TN':[]}}
		relationCategoryTotal={'Inv':{'OK':[],'NOK':[],'UD':[]},'Neg':{'OK':[],'NOK':[],'UD':[]},'Drg':{'OK':[],'NOK':[],'UD':[]},'Dat':{'OK':[],'NOK':[],'UD':[]},'Alg':{'OK':[],'NOK':[],'UD':[]}}
		attributeTypeTotal={'Status':{'OK':[],'NOK':[],'UD':[]},'Source':{'OK':[],'NOK':[],'UD':[]}}
		cache=self.initCache(len(annotations))
		for goldI in range(len(annotations)):
			for candidateI in range(len(annotations)):
				goldAnn=annotations[goldI]
				candidateAnn=annotations[candidateI]
				if not goldAnn is candidateAnn:
					print('Comparing annotator '+names[candidateI]+' to '+names[goldI]+' ...')
					comparison=self.compareEntities(goldAnn,candidateAnn,True)
					categoryComparison=self.compareCategories(comparison,goldAnn,candidateAnn)
					attributeComparison=self.compareAttributes(comparison,goldAnn,candidateAnn)
					normalisationComparison=self.compareNormalisations(comparison,goldAnn,candidateAnn)
					relationComparison=self.compareRelations(comparison,goldAnn,candidateAnn)
					cache[goldI][candidateI]['comparison']=comparison
					cache[goldI][candidateI]['categoryComparison']=categoryComparison
					cache[goldI][candidateI]['attributeComparison']=attributeComparison
					cache[goldI][candidateI]['normalisationComparison']=normalisationComparison
					cache[goldI][candidateI]['relationComparison']=relationComparison
					self.aggregate(entityTotal,comparison)
					self.aggregate(categoryTotal,categoryComparison)
					self.aggregate(attributeTotal,attributeComparison)
					self.aggregate(normalisationTotal,normalisationComparison)
					self.aggregate(relationTotal,relationComparison)
					comparisonByCategory=self.splitByEntityCategory(comparison,goldAnn,candidateAnn)
					for key in entityCategoryTotal.keys():
						if key in comparisonByCategory:
							self.aggregate(entityCategoryTotal[key],comparisonByCategory[key])
					relationComparisonByCategory=self.splitByRelationCategory(relationComparison,goldAnn,candidateAnn)
					for key in relationCategoryTotal.keys():
						if key in relationComparisonByCategory:
							self.aggregate(relationCategoryTotal[key],relationComparisonByCategory[key])
					attributeComparisonByType=self.splitByAttributeType(attributeComparison,goldAnn,candidateAnn)
					for key in attributeTypeTotal.keys():
						if key in attributeComparisonByType:
							self.aggregate(attributeTypeTotal[key],attributeComparisonByType[key])
		outFile=open(outPath,"w")
		outFile.write("Overall entity F1:\t"+("%.4f" % self.computeF1(entityTotal))+"\n")
		outFile.write("Overall category accuracy:\t"+("%.4f" % self.computeAccuracy(categoryTotal))+"\n")
		outFile.write("Overall category certainty:\t"+("%.4f" % self.computeCertainty(categoryTotal))+"\n")
		outFile.write("Overall attribute accuracy:\t"+("%.4f" % self.computeAccuracy(attributeTotal))+"\n")
		outFile.write("Overall attribute certainty:\t"+("%.4f" % self.computeCertainty(attributeTotal))+"\n")
		outFile.write("Overall normalisation accuracy:\t"+("%.4f" % self.computeAccuracy(normalisationTotal))+"\n")
		outFile.write("Overall normalisation certainty:\t"+("%.4f" % self.computeCertainty(normalisationTotal))+"\n")
		outFile.write("Overall relation accuracy:\t"+("%.4f" % self.computeAccuracy(relationTotal))+"\n")
		outFile.write("Overall relation certainty:\t"+("%.4f" % self.computeCertainty(relationTotal))+"\n")

		outFile.write("\nEntity F1\n")
		outFile.write("Agreement matrix:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		for i in range(len(annotations)):
			outFile.write(names[i])
			for j in range(len(annotations)):
				if i>=j:
					outFile.write('\tX')
					continue
				#print('cache[' + str(i) + "][" + str(j) + "] = " + str(cache[i][j]))
				if len(cache[i][j]) > 0:
					score=(self.computeF1(cache[i][j]['comparison'])+self.computeF1(cache[j][i]['comparison']))/2
				else:
					score = 0.0
				outFile.write('\t'+("%.4f" % score))
			outFile.write("\n")

		outFile.write("Average for annotators:\n")
		outFile.write('\t'+'\t'.join(names)+'\n')
		perAnnotator=[0.0]*len(annotations)
		for i in range(len(annotations)):
			for j in range(len(annotations)):
				if i<j:
					print("cache[i][j] = " + str(cache[i][j]))
					if len(cache[i][j]) > 0:
						score=(self.computeF1(cache[i][j]['comparison'])+self.computeF1(cache[j][i]['comparison']))/2
					else:
						score = 0.0
					perAnnotator[i]+=score/(len(annotations)-1)
					perAnnotator[j]+=score/(len(annotations)-1)
		outFile.write('\t'+'\t'.join([("%.4f" % x) for x in perAnnotator])+"\n")

		outFile.write("Average per entity type:\n")
		outFile.write('\t'+'\t'.join(entityCategoryTotal.keys())+"\n")
		for key in entityCategoryTotal.keys():
			outFile.write('\t'+("%.4f" % self.computeF1(entityCategoryTotal[key])))
		outFile.write('\n')

		outFile.write("\nCategory accuracy\n")
		outFile.write("Agreement matrix:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		for i in range(len(annotations)):
			outFile.write(names[i])
			for j in range(len(annotations)):
				if i>=j:
					outFile.write('\tX')
					continue
				if len(cache[i][j]) > 0:
					score=(self.computeAccuracy(cache[i][j]['categoryComparison'])+self.computeAccuracy(cache[j][i]['categoryComparison']))/2
				else:
					score = 0.0
				outFile.write('\t'+("%.4f" % score))
			outFile.write('\n')

		outFile.write("Average for annotators:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		perAnnotator=[0.0]*len(annotations)
		for i in range(len(annotations)):
			for j in range(len(annotations)):
				if i<j:
					if len(cache[i][j]) > 0:
						score=(self.computeAccuracy(cache[i][j]['categoryComparison'])+self.computeAccuracy(cache[j][i]['categoryComparison']))/2
					else:
						score = 0.0
					perAnnotator[i]+=score/(len(annotations)-1)
					perAnnotator[j]+=score/(len(annotations)-1)
		outFile.write('\t'+'\t'.join([("%.4f" % x) for x in perAnnotator])+"\n")

		outFile.write("\nAttribute accuracy\n")
		outFile.write("Agreement matrix:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		for i in range(len(annotations)):
			outFile.write(names[i])
			for j in range(len(annotations)):
				if i>=j:
					outFile.write('\tX')
					continue
					if len(cache[i][j]) > 0:
						score=(self.computeAccuracy(cache[i][j]['attributeComparison'])+self.computeAccuracy(cache[j][i]['attributeComparison']))/2
					else:
						score = 0.0
				outFile.write('\t'+("%.4f" % score))
			outFile.write('\n')

		outFile.write("Average for annotators:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		perAnnotator=[0.0]*len(annotations)
		for i in range(len(annotations)):
			for j in range(len(annotations)):
				if i<j:
					if len(cache[i][j]) > 0:
						score=(self.computeAccuracy(cache[i][j]['attributeComparison'])+self.computeAccuracy(cache[j][i]['attributeComparison']))/2
					else:
						score = 0.0
					perAnnotator[i]+=score/(len(annotations)-1)
					perAnnotator[j]+=score/(len(annotations)-1)
		outFile.write('\t'+'\t'.join([("%.4f" % x) for x in perAnnotator])+"\n")

		outFile.write("Average per attribute type:\n")
		outFile.write('\t'+'\t'.join(attributeTypeTotal.keys())+"\n")
		for key in attributeTypeTotal.keys():
			outFile.write('\t'+("%.4f" % self.computeAccuracy(attributeTypeTotal[key])))

		outFile.write("\nNormalisation accuracy\n")
		outFile.write("Agreement matrix:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		for i in range(len(annotations)):
			outFile.write(names[i])
			for j in range(len(annotations)):
				if i>=j:
					outFile.write('\tX')
					continue
				if len(cache[i][j]) > 0:
					score=(self.computeAccuracy(cache[i][j]['normalisationComparison'])+self.computeAccuracy(cache[j][i]['normalisationComparison']))/2
				else:
					score = 0.0
				outFile.write('\t'+("%.4f" % score))
			outFile.write('\n')

		outFile.write("Average for annotators:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		perAnnotator=[0.0]*len(annotations)
		for i in range(len(annotations)):
			for j in range(len(annotations)):
				if i<j:
					if len(cache[i][j]) > 0:
						score=(self.computeAccuracy(cache[i][j]['normalisationComparison'])+self.computeAccuracy(cache[j][i]['normalisationComparison']))/2
					else:
						score = 0.0
					perAnnotator[i]+=score/(len(annotations)-1)
					perAnnotator[j]+=score/(len(annotations)-1)
		outFile.write('\t'+'\t'.join([("%.4f" % x) for x in perAnnotator])+"\n")


		outFile.write("\nRelation accuracy\n")
		outFile.write("Agreement matrix:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		for i in range(len(annotations)):
			outFile.write(names[i])
			for j in range(len(annotations)):
				if i>=j:
					outFile.write('\tX')
					continue
				if len(cache[i][j]) > 0:
					score=(self.computeAccuracy(cache[i][j]['relationComparison'])+self.computeAccuracy(cache[j][i]['relationComparison']))/2
				else:
					score = 0.0
				outFile.write('\t'+("%.4f" % score))
			outFile.write('\n')

		outFile.write("Average for annotators:\n")
		outFile.write('\t'+'\t'.join(names)+"\n")
		perAnnotator=[0.0]*len(annotations)
		for i in range(len(annotations)):
			for j in range(len(annotations)):
				if i<j:
					if len(cache[i][j]) > 0:
						score=(self.computeAccuracy(cache[i][j]['relationComparison'])+self.computeAccuracy(cache[j][i]['relationComparison']))/2
					else:
						score = 0.0
					perAnnotator[i]+=score/(len(annotations)-1)
					perAnnotator[j]+=score/(len(annotations)-1)
		outFile.write('\t'+'\t'.join([("%.4f" % x) for x in perAnnotator])+"\n")

		outFile.write("Average per relation type:\n")
		outFile.write('\t'+'\t'.join(relationCategoryTotal.keys())+"\n")
		for key in relationCategoryTotal.keys():
			outFile.write('\t'+("%.4f" % self.computeAccuracy(relationCategoryTotal[key])))
		outFile.close()

	def readAllAnnotations(self, path):
		subdirs = path # [x[0] for x in os.walk(path)]
		allAnnotations=[]
		allNames=[]
		for subdir in sorted(subdirs):
			annotator=os.path.basename(subdir)
			if annotator=="":
				continue
			print("Adding annotator "+annotator)
			annotations=None
			for root, dirs, files in os.walk(subdir):
				for name in files:
					if not name.endswith(".ann"):
						continue
					print("Reading "+name)
					annotation=self.readAnn(subdir+"/"+name)
					self.addPrefix(annotation,name[:-4]+"~")
					if annotations is None:
						annotations=annotation
					else:
						annotations[0].update(annotation[0])
						annotations[1].update(annotation[1])
						annotations[2].update(annotation[2])
						annotations[3].update(annotation[3])
			allAnnotations.append(annotations)
			allNames.append(annotator)
		return((allAnnotations,allNames))

	def do_agreement(self, work_dir, test_pred_dir, result_tsv):

		#(annotations,names)=self.readAllAnnotations("./par3/comparison/")
		#self.summary(annotations,names,"./out.tsv")

		(annotations,names)=self.readAllAnnotations([work_dir, test_pred_dir])
		self.summary(annotations,names,result_tsv)
