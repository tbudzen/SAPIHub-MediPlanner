# Oblicza zgodnosc anotacji kandydujacej (np. z automatycznego algorytmu) z wzorcowa (np. z recznej anotacji)
# Uruchamianie: python evaluation.py <folder_anotacji_wzorcowych> <folder_anotacji_kandydujacych> <plik_wyjsciowy>

import os
import sys

def readAnn(path):
	entities=readEntities(path)
	attributes=readAttributes(path,entities)
	normalisations=readNormalisations(path,entities)
	relations=readRelations(path,entities)
	return([entities,attributes,normalisations,relations])

def readEntities(path):
	entities={}
	for line in open(path):
		#print(line)
		parts=line.split('\t')
		if parts[0][0]!='T':
			continue
		if not parts[0][1].isdigit():
			continue
		idd=parts[0]
		text=parts[2].strip()
		parts=parts[1].split(' ')
		category=parts[0]
		if category=='NOTE':
			continue
		if parts[1]=='':
			print("Ignoring entity with empty location.")
			continue
		begin=int(parts[1])
		if ';' in parts[2]:
			print("Ignoring multi-segment entity.")
			continue
		end=int(parts[2])
		entity={'category':category,'begin':begin,'end':end,'text':text}		
		entities[idd]=entity
	print("Read "+str(len(entities))+" entites.")
	return(entities)

# Attributes under an assumption there is only one atytribute possible - 'History'
def readAttributes(path,entities):
	attributes={}
	for line in open(path):
		#print(line)
		parts=line.split('\t')
		if parts[0][0]!='A':
			continue
		if not parts[0][1].isdigit():
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
	print("Added "+str(len(attributes))+" attributes.")
	return(attributes)

def readNormalisations(path,entities):
	normalisations={}
	for line in open(path):
		parts=line.split('\t')
		if parts[0][0]!='N':
			continue
		if not parts[0][1].isdigit():
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
	print("Added "+str(len(normalisations))+" normalisations.")
	return(normalisations)

def readRelations(path,entities):
	relations={}
	for line in open(path):
		parts=line.split('\t')
		if parts[0][0]!='R':
			continue
		if not parts[0][1].isdigit():
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
	print("Added "+str(len(relations))+" relations.")
	return(relations)

def match(entityId1,entity1,entityId2,entity2,relaxed):
	#if ('~' in entityId1) or ('~' in entityId2):
	#	if entityId1[0:entityId1.find('~')]!=entityId2[0:entityId2.find('~')]:
	#		return(False)
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

def findMatchingEntity(entityId,entity,visitedC,entitiesAnn,relaxed):
	for entityC in sorted(entitiesAnn.keys()):
		if entityC in visitedC:
			continue
		if match(entityId,entity,entityC,entitiesAnn[entityC],relaxed):
			return(entityC)
	return(None)
	
def filterEntityComparison(entityComparisonM,file):
	comparison={'TP':[],'FP':[],'FN':[],'TN':[]}
	for section in comparison.keys():
		for pair in entityComparisonM[section]:
			if (pair[0] is None) or pair[0][0:pair[0].find('~')]==file:
				if (pair[1] is None) or pair[1][0:pair[1].find('~')]==file:
					comparison[section].append(pair)
	return(comparison)

def compareEntities(goldAnnM,candidateAnnM,relaxed,verbose=False):
	comparison={'TP':[],'FP':[],'FN':[],'TN':[]}
	for file in set(goldAnnM.keys()).union(candidateAnnM.keys()):
		goldAnn=[{},{},{},{}]
		candidateAnn=[{},{},{},{}]
		if file in goldAnnM:
			goldAnn=goldAnnM[file]
		if file in candidateAnnM:
			candidateAnn=candidateAnnM[file]
		visitedC=[]
		if verbose:
			print("Scanning entities in "+file)
		for entityG in sorted(goldAnn[0].keys()):
			entityC=findMatchingEntity(entityG,goldAnn[0][entityG],visitedC,candidateAnn[0],relaxed)
			if entityC is None:
				comparison['FN'].append((entityG,None))
				if verbose:
					print(entityG+" : "+str(goldAnn[0][entityG]))
			else:
				comparison['TP'].append((entityG,entityC))
				visitedC.append(entityC)
		for entityC in candidateAnn[0]:
			if not entityC in visitedC:
				comparison['FP'].append((None,entityC))
	print('Finished comparison with TP='+str(len(comparison['TP']))+" FN="+str(len(comparison['FN']))+" FP="+str(len(comparison['FP']))+" TN="+str(len(comparison['TN'])))
	return(comparison)

def compareAttributes(entityComparisonM,goldAnnM,candidateAnnM):
	comparison={'OK':[],'NOK':[],'UD':[]}
	for file in set(goldAnnM.keys()).union(candidateAnnM.keys()):
		goldAnn=[{},{},{},{}]
		candidateAnn=[{},{},{},{}]
		if file in goldAnnM:
			goldAnn=goldAnnM[file]
		if file in candidateAnnM:
			candidateAnn=candidateAnnM[file]
		entityComparison=filterEntityComparison(entityComparisonM,file)
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

def compareNormalisations(entityComparisonM,goldAnnM,candidateAnnM):
	comparison={'TP':[],'NOK':[],'FP':[],'FN':[],'UD':[],'TN':[]}
	for file in set(goldAnnM.keys()).union(candidateAnnM.keys()):
		goldAnn=[{},{},{},{}]
		candidateAnn=[{},{},{},{}]
		if file in goldAnnM:
			goldAnn=goldAnnM[file]
		if file in candidateAnnM:
			candidateAnn=candidateAnnM[file]
		entityComparison=filterEntityComparison(entityComparisonM,file)
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
				comparison['FN'].append((normalisationG,None))
			else:
				visitedC.append(normalisationC)
				if conceptC==conceptG:
					comparison['TP'].append((normalisationG,normalisationC))
				else:
					comparison['NOK'].append((normalisationG,normalisationC))
		for normalisationC in sorted(candidateAnn[2].keys()):
			if not normalisationC in visitedC:
				entityC=candidateAnn[2][normalisationC]['entity']
				entityG=None
				for (eG,eC) in entityComparison['TP']:
					if eC==entityC:
						entityG=eG
						break
				if entityG is None:
					comparison['UD'].append((None,normalisationC))
				else:
					comparison['FP'].append((None,normalisationC))
	print('Finished normalisation comparison with TP='+str(len(comparison['TP']))+" FN="+str(len(comparison['FN']))+" FP="+str(len(comparison['FP']))+" TN="+str(len(comparison['TN']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
	return(comparison)
			
			
def compareCategories(entityComparisonM,goldAnnM,candidateAnnM):
	comparison={'OK':[],'NOK':[],'UD':[]}
	for file in set(goldAnnM.keys()).union(candidateAnnM.keys()):
		goldAnn=[{},{},{},{}]
		candidateAnn=[{},{},{},{}]
		if file in goldAnnM:
			goldAnn=goldAnnM[file]
		if file in candidateAnnM:
			candidateAnn=candidateAnnM[file]
		entityComparison=filterEntityComparison(entityComparisonM,file)
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

def compareRelations(entityComparisonM,goldAnnM,candidateAnnM):
	comparison={'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]}
	for file in set(goldAnnM.keys()).union(candidateAnnM.keys()):
		goldAnn=[{},{},{},{}]
		candidateAnn=[{},{},{},{}]
		if file in goldAnnM:
			goldAnn=goldAnnM[file]
		if file in candidateAnnM:
			candidateAnn=candidateAnnM[file]
		entityComparison=filterEntityComparison(entityComparisonM,file)
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
				comparison['FN'].append((relationG,None))
				continue
			visitedC.append(relationC)
			if goldAnn[3][relationG]['category']==candidateAnn[3][relationC]['category']:
				comparison['TP'].append((relationG,relationC))
			else:
				comparison['NOK'].append((relationG,relationC))
				#print(sourceG+"-"+relationG+"-"+destinationG)
				#print(sourceC+"-"+relationC+"-"+destinationC)
		for relationC in sorted(candidateAnn[3].keys()):
			if not relationC in visitedC:
				sourceC=candidateAnn[3][relationC]['source']
				sourceG=None
				for (eG,eC) in entityComparison['TP']:
					if eC==sourceC:
						sourceG=eG
						break
				if sourceG is None:
					comparison['UD'].append((None,relationC))
					continue
				destinationC=candidateAnn[3][relationC]['destination']
				destinationG=None
				for (eG,eC) in entityComparison['TP']:
					if eC==destinationC:
						destinationG=eG
						break
				if destinationG is None:
					comparison['UD'].append((None,relationC))
					continue
				comparison['FP'].append((None,relationC))
	print('Finished relation comparison with TP='+str(len(comparison['TP']))+" FN="+str(len(comparison['FN']))+" FP="+str(len(comparison['FP']))+" TN="+str(len(comparison['TN']))+" NOK="+str(len(comparison['NOK']))+" UD="+str(len(comparison['UD'])))
	return(comparison)

def aggregate(comparison1,comparison2):
	for key in comparison1.keys():
		if key in comparison2:
			comparison1[key].extend(comparison2[key])

def computeF1(comparison):
	if (2*len(comparison['TP'])+len(comparison['FP'])+len(comparison['FN']))==0:
		F1=float('nan')
	else:
		F1=2*len(comparison['TP'])*1.0/(2*len(comparison['TP'])+len(comparison['FP'])+len(comparison['FN']))
	return(F1)

def computePrecision(comparison):
	if (2*len(comparison['TP'])+len(comparison['FP']))==0:
		prec=float('nan')
	else:
		prec=len(comparison['TP'])*1.0/(len(comparison['TP'])+len(comparison['FP']))
	return(prec)

def computePrecisionN(comparison):
	if (len(comparison['TP'])+len(comparison['NOK']))==0:
		prec=float('nan')
	else:
		prec=len(comparison['TP'])*1.0/(len(comparison['TP'])+len(comparison['NOK']))
	return(prec)

def computeRecall(comparison):
	if (2*len(comparison['TP'])+len(comparison['FN']))==0:
		rec=float('nan')
	else:
		rec=len(comparison['TP'])*1.0/(len(comparison['TP'])+len(comparison['FN']))
	return(rec)

def computeRecallN(comparison):
	if (len(comparison['TP'])+len(comparison['NOK'])+len(comparison['FN']))==0:
		rec=float('nan')
	else:
		rec=(len(comparison['TP'])+len(comparison['NOK']))*1.0/(len(comparison['TP'])+len(comparison['NOK'])+len(comparison['FN']))
	return(rec)

def computeAccuracy(comparison):
	if len(comparison['OK'])+len(comparison['NOK'])==0:
		A=float('nan')
	else:
		A=len(comparison['OK'])*1.0/(len(comparison['OK'])+len(comparison['NOK']))
	return(A)

def computeCertainty(comparison):
	if len(comparison['OK'])+len(comparison['NOK'])+len(comparison['UD'])==0:
		return(0)
	K=(len(comparison['OK'])+len(comparison['NOK']))*1.0/(len(comparison['OK'])+len(comparison['NOK'])+len(comparison['UD']))
	return(K)

def initCache(N):
	result=[]
	for i in range(N):
		row=[]
		for j in range(N):
			row.append({})
		result.append(row)
	return(result)

def addPrefix(annotation,prefix):
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

def splitByEntityCategory(entityComparison,goldAnn,candidateAnn):
	result=dict()
	for key in entityComparison.keys():
		for pair in entityComparison[key]:
			if not pair[0] is None:
				cat1=goldAnn[pair[0][0:pair[0].find('~')]][0][pair[0]]['category']
				if not cat1 in result:
					result[cat1]={}
				if not key in result[cat1]:
					result[cat1][key]=[]
				result[cat1][key].append(pair)
			if not pair[1] is None:
				cat2=candidateAnn[pair[1][0:pair[1].find('~')]][0][pair[1]]['category']
				if not cat2 in result:
					result[cat2]={}
				if not key in result[cat2]:
					result[cat2][key]=[]
				result[cat2][key].append(pair)
	return(result)
			
def splitByRelationCategory(relationComparison,goldAnn,candidateAnn):
	result=dict()
	for key in relationComparison.keys():
		for pair in relationComparison[key]:
			if not pair[0] is None:
				cat1=goldAnn[pair[0][0:pair[0].find('~')]][3][pair[0]]['category']
				if not cat1 in result:
					result[cat1]={}
				if not key in result[cat1]:
					result[cat1][key]=[]
				result[cat1][key].append(pair)
			if not pair[1] is None:
				cat2=candidateAnn[pair[1][0:pair[1].find('~')]][3][pair[1]]['category']
				if not cat2 in result:
					result[cat2]={}
				if not key in result[cat2]:
					result[cat2][key]=[]
				result[cat2][key].append(pair)
	return(result)

def splitByAttributeType(attributeComparison,goldAnn,candidateAnn):
	result=dict()
	for key in attributeComparison.keys():
		for pair in attributeComparison[key]:
			if not pair[0] is None:
				cat1=goldAnn[pair[0][0:pair[0].find('~')]][1][pair[0]]['type']
				if not cat1 in result:
					result[cat1]={}
				if not key in result[cat1]:
					result[cat1][key]=[]
				result[cat1][key].append(pair)
			if not pair[1] is None:
				cat2=candidateAnn[pair[1][0:pair[1].find('~')]][1][pair[1]]['type']
				if not cat2 in result:
					result[cat2]={}
				if not key in result[cat2]:
					result[cat2][key]=[]
				result[cat2][key].append(pair)
	return(result)
	

def summary(annotations,names,outPath):
	entityTotal={'TP':[],'FP':[],'FN':[],'TN':[]}
	categoryTotal={'OK':[],'NOK':[],'UD':[]}
	attributeTotal={'OK':[],'NOK':[],'UD':[]}
	normalisationTotal={'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]}
	relationTotal={'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]}
	entityCategoryTotal={'Symptom':{'TP':[],'FP':[],'FN':[],'TN':[]},'Condition':{'TP':[],'FP':[],'FN':[],'TN':[]},'Behaviour':{'TP':[],'FP':[],'FN':[],'TN':[]},'Treatment':{'TP':[],'FP':[],'FN':[],'TN':[]},'Investigation':{'TP':[],'FP':[],'FN':[],'TN':[]},'Investigation_result':{'TP':[],'FP':[],'FN':[],'TN':[]},'Drug':{'TP':[],'FP':[],'FN':[],'TN':[]},'Drug_dose':{'TP':[],'FP':[],'FN':[],'TN':[]},'Negation':{'TP':[],'FP':[],'FN':[],'TN':[]},'Date':{'TP':[],'FP':[],'FN':[],'TN':[]}}
	relationCategoryTotal={'Inv':{'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]},'Neg':{'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]},'Drg':{'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]},'Dat':{'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]},'Alg':{'TP':[],'FP':[],'FN':[],'TN':[],'NOK':[],'UD':[]}}
	attributeTypeTotal={'Status':{'OK':[],'NOK':[],'UD':[]},'Source':{'OK':[],'NOK':[],'UD':[]}}
	print(names)
	goldI=0#names.index("test")
	candidateI=1#names.index("test-pred")
	goldAnn=annotations[goldI]
	candidateAnn=annotations[candidateI]
	print('Comparing annotator '+names[candidateI]+' to '+names[goldI]+' ...')
	comparison=compareEntities(goldAnn,candidateAnn,True,False)
	categoryComparison=compareCategories(comparison,goldAnn,candidateAnn)
	attributeComparison=compareAttributes(comparison,goldAnn,candidateAnn)
	normalisationComparison=compareNormalisations(comparison,goldAnn,candidateAnn)
	relationComparison=compareRelations(comparison,goldAnn,candidateAnn)
	aggregate(entityTotal,comparison)
	aggregate(categoryTotal,categoryComparison)
	aggregate(attributeTotal,attributeComparison)
	aggregate(normalisationTotal,normalisationComparison)
	aggregate(relationTotal,relationComparison)
	comparisonByCategory=splitByEntityCategory(comparison,goldAnn,candidateAnn)
	for key in entityCategoryTotal.keys():
		if key in comparisonByCategory:
			aggregate(entityCategoryTotal[key],comparisonByCategory[key])
	relationComparisonByCategory=splitByRelationCategory(relationComparison,goldAnn,candidateAnn)
	for key in relationCategoryTotal.keys():
		if key in relationComparisonByCategory:
			aggregate(relationCategoryTotal[key],relationComparisonByCategory[key])
	attributeComparisonByType=splitByAttributeType(attributeComparison,goldAnn,candidateAnn)
	for key in attributeTypeTotal.keys():
		if key in attributeComparisonByType:
			aggregate(attributeTypeTotal[key],attributeComparisonByType[key])
	outFile=open(outPath,"w")
	outFile.write("Overall entity F1:\t"+("%.4f" % computeF1(entityTotal))+"\n")
	outFile.write("Overall entity precision:\t"+("%.4f" % computePrecision(entityTotal))+"\n")
	outFile.write("Overall entity recall:\t"+("%.4f" % computeRecall(entityTotal))+"\n")
	outFile.write("Overall category accuracy:\t"+("%.4f" % computeAccuracy(categoryTotal))+"\n")
	outFile.write("Overall category certainty:\t"+("%.4f" % computeCertainty(categoryTotal))+"\n")
	outFile.write("Overall attribute accuracy:\t"+("%.4f" % computeAccuracy(attributeTotal))+"\n")
	outFile.write("Overall attribute certainty:\t"+("%.4f" % computeCertainty(attributeTotal))+"\n")
	outFile.write("Overall normalisation recall:\t"+("%.4f" % computeRecallN(normalisationTotal))+"\n")
	outFile.write("Overall normalisation precision:\t"+("%.4f" % computePrecisionN(normalisationTotal))+"\n")
	outFile.write("Overall relation F1:\t"+("%.4f" % computeF1(relationTotal))+"\n")
	outFile.write("Overall relation precision:\t"+("%.4f" % computePrecision(relationTotal))+"\n")
	outFile.write("Overall relation recall:\t"+("%.4f" % computeRecall(relationTotal))+"\n")
	
	outFile.write("\nEntity F1\n")

	outFile.write("Average per entity type:\n")
	outFile.write('\t'+'\t'.join(entityCategoryTotal.keys())+"\n")
	for key in entityCategoryTotal.keys():
		outFile.write('\t'+("%.4f" % computeF1(entityCategoryTotal[key])))
	outFile.write('\n')

	outFile.write("\nAttribute accuracy\n")

	outFile.write("Average per attribute type:\n")
	outFile.write('\t'+'\t'.join(attributeTypeTotal.keys())+"\n")
	for key in attributeTypeTotal.keys():
		outFile.write('\t'+("%.4f" % computeAccuracy(attributeTypeTotal[key])))

	outFile.write("\nRelation F1\n")

	outFile.write("Average per relation type:\n")
	outFile.write('\t'+'\t'.join(relationCategoryTotal.keys())+"\n")
	for key in relationCategoryTotal.keys():
		outFile.write('\t'+("%.4f" % computeF1(relationCategoryTotal[key])))
	outFile.close()

def readAllAnnotations(path,subdirs=None):
	if subdirs is None:
		subdirs = [x[0] for x in os.walk(path)]
	allAnnotations=[]
	allNames=[]
	for subdir in subdirs:
		annotator=os.path.basename(os.path.normpath(subdir))
		if annotator=="":
			continue
		print("Adding annotator "+annotator)
		annotations={}
		for root, dirs, files in os.walk(subdir):
			for name in files:
				if not name.endswith(".ann"):
					continue
				print("Reading "+name)
				annotation=readAnn(subdir+"/"+name)
				addPrefix(annotation,name[:-4]+"~")
				annotations[name[:-4]]=annotation
		allAnnotations.append(annotations)
		allNames.append(annotator)
	return((allAnnotations,allNames))

(annotations,names)=readAllAnnotations(None,[sys.argv[1],sys.argv[2]])
summary(annotations,names,sys.argv[3])
