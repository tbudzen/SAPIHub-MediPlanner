#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spacy
import json
import os
import functools
import operator
nlp = spacy.load('pl_spacy_model') 

print("start")

withoutPunctuationRank = 1
theSameLineRank = 2
maxRank = withoutPunctuationRank + theSameLineRank

dateTransitionWords = ["wówczas", "wtedy"]
punctuations = [",", ";", ".", "?", "!"]
punctuationForNegAndAlg = [",", ";", ".", "?", "!", "-"]
conjunctions = [" i ", "oraz "]
punctuationsAndConjunctions = punctuations + conjunctions
reservedNegationsForTags = {"odstaw": ["Drug", "Drug dose"]}
brokenEnumeration = [":", ";", ".", ","]
allowedBetweenAlgTags = ["w trakcie", "w czasie", "podczas"]
mandatoryForAlgTag1 = ["uczul", "alerg", "nadwrażliw", "nietolerancj"]
notAllowedBetweenAlgTags = ["zaleca się", "otrzymuj"]
lsum = lambda xs: functools.reduce(operator.add, xs, 0)
textLenLimit = 45


def writeToFile(lines, filename):
    outF = open(filename, "w")
    outF.writelines(lines)
    outF.close()
    
def appendToFile(lines, filename):
    outF = open(filename, "a")
    outF.writelines(lines)
    outF.close()

def textFromFile(filename):
    file = open(filename)
    toReturn = file.read()
    file.close()
    return toReturn

def linesFromFile(filename):
    lines = []
    f = open(filename, "r")
    for x in f:
        lines.append(x)
    f.close()
    return lines

def returnIfOrDefault(condition, value, default):
    if condition:
        return value
    else:
        return default

def textContainsAtLeastOne(text, texts):
    for t in texts:
        if t in text:
            return True
    return False

def textContainsPunctuationOrConjunction(text):
    if isinstance(text, str):
        return textContainsAtLeastOne(text, punctuations) or textContainsAtLeastOne(text, conjunctions)
    else:
        False

def textContainsPunctuationOrConjunctionForNegOrAlg(text):
    if isinstance(text, str):
        return textContainsAtLeastOne(text, punctuationForNegAndAlg) or textContainsAtLeastOne(text, conjunctions)
    else:
        False

def textContainsLineSeparator(text):
    if isinstance(text, str):
        return "\n" in text
    else:
        False
        
def textContainAlmostOnlyOneFromList(text, texts):
    for t in texts:
        if len(text) < len(t)+3 and t in text:
            return True
    return False
        

class FileInfo():
    def __init__(self, basename, annPath, txtPath, baseFolder):
        self.basename = basename
        self.annPath = annPath
        self.txtPath = txtPath
        self.baseFolder = baseFolder
    def __str__(self):
        return f"FileInfo: {self.basename}, {self.annPath}, {self.txtPath}"

class SentenceForRelation():
    def __init__(self, idx, sentence):
        self.idx = idx
        self.sentence = sentence
    def __str__(self):
        return f"Sentence {self.idx}:\n{self.sentence}"


class Relation():
    def __init__(self, idx, rType, arg1, arg2, sentenceIdx, tag1, tag2, doc):
        self.idx = idx
        self.rType = rType
        self.arg1 = arg1
        self.arg2 = arg2
        self.isOk = False
        self.sentenceIdx = sentenceIdx
        self.tag1 = tag1
        self.tag2 = tag2
        self.doc = doc
        self.removed = False
        self.removedReason = ""
        self.rank = -1
        
    tagsInTheSameLine = None
        
    def __str__(self):
        return f"Relation[{self.idx}, {self.rType}, {self.arg1}, {self.arg2}]"
    
    def setIdx(self, idx):
        self.idx = idx
    def isOK(self):
        return not self.removed and self.isOk
    def shouldNotBeRemoved(self):
        return self.isOk and self.removed
    def isRedundantAndRemoved(self):
        return not self.isOk and self.removed
    def shouldBeBemoved(self):
        return not self.isOk and not self.removed
    def alertMsg(self):
        if self.isOk:
            if not self.removed:
                return f" << OK >>"
            else:
                return " <<SHOULD NOT BE REMOVED>>"
        else:
            if self.removed:
                return f" <<REDUNDANT!!!REMOVED>>"
            else:
                return f" <<REDUNDANT!!!SHOULD BE REMOVED>>"
    def removedMsg(self):
        if self.removed:
            return f"<:REMOVED {self.removedReason}:>"
        else:
            return ""
    def reasonIfShouldNotBeRemoved(self):
        if self.removed and self.isOk:
            return self.removedMsg()
        else:
            return ""
        
    def relationStr(self):
        return f"{self.rType} Arg1:{self.arg1} Arg2:{self.arg2}"
    
    def toLine(self,verbose=True):
        if verbose:
            return f"R{self.idx}\t{self.relationStr()} {self.alertMsg()} {self.sentenceIdx}\n"
        else:
            return f"R{self.idx}\t{self.relationStr()}\n"
    
    def lineWithTextInfo(self):
        return f"R{self.idx}\t{self.relationStr()}{self.alertMsg()}\t{self.tag1.text.strip()} -> {self.tag2.text.strip()} {self.removedMsg()} {self.rankMsg()} <info: {self.additionalInfo()}>\n"
    
    def setOk(self, isOk):
        self.isOk = isOk
    def setRemoved(self, removed, removedReason = ""):
        self.removed = removed
        self.removedReason = removedReason
        
    def additionalInfo(self):
        return f"start[{self.tag1.start}, {self.tag2.start}] {self.sideMsg()}"
#        return f"start[{self.tag1.start}, {self.tag2.start}] --text b: {self.textBetweenTags()}"
#        return f" b[{self.tag2.end}:{self.tag1.start} or {self.tag1.end}:{self.tag2.start}]"
#        return ""
        
    def textBetweenTags(self):
        if self.tag1.start > self.tag2.end:
            return self.doc.text[self.tag2.end : self.tag1.start]
        elif self.tag1.end < self.tag2.start:
            return self.doc.text[self.tag1.end : self.tag2.start]
        else:
            return ""
            
    def isTagsSeparatedByPunctuation(self):
        if self.rType == "Neg" or self.rType == "Alg":
            return textContainsPunctuationOrConjunctionForNegOrAlg(self.textBetweenTags())
        else:
            return textContainsPunctuationOrConjunction(self.textBetweenTags())
    
    def isTagsInTheSameLine(self):
        if self.tagsInTheSameLine == None:
            self.tagsInTheSameLine = not textContainsLineSeparator(self.textBetweenTags())
        return self.tagsInTheSameLine
    
    def computeTheSameLineRank(self):
        return returnIfOrDefault(self.isTagsInTheSameLine(), theSameLineRank, 0)
    
    def computeWithoutPunctuationRank(self):
        return returnIfOrDefault(not self.isTagsSeparatedByPunctuation(), withoutPunctuationRank, 0)
    
    def computeRank(self):
        return self.computeTheSameLineRank() + self.computeWithoutPunctuationRank()
        
    def getRank(self):
        if self.rank == -1:
            self.rank = self.computeRank()
        return self.rank
    
    def rankMsg(self):
        return f"<RANK: {self.getRank()}>"
    
    def isRight(self):
        return self.tag1.start < self.tag2.start
    def isLeft(self):
        return not self.isRight()
    def sideMsg(self):
        if self.isRight():
            return "<type: RIGHT>"
        else:
            return "<type: LEFT>"
        
    def textBetweenFirstTags(self, otherFirstTag):
        if self.tag1.start > otherFirstTag.end:
            return self.doc.text[otherFirstTag.end : self.tag1.start]
        elif self.tag1.end < otherFirstTag.start:
            return self.doc.text[self.tag1.end : otherFirstTag.start]
        else:
            return ""

    def textBetweenSecondTags(self, otherSecondTag):
        if self.tag2.start > otherSecondTag.end:
            return self.doc.text[otherSecondTag.end : self.tag2.start]
        elif self.tag2.end < otherSecondTag.start:
            return self.doc.text[self.tag2.end : otherSecondTag.start]
        else:
            return ""

    def almostOnlyConcunctionOrPunctuationBetweenFirstTags(self, otherFirstTag):
        textBetween = self.textBetweenFirstTags(otherFirstTag)
        return textContainAlmostOnlyOneFromList(textBetween, punctuationsAndConjunctions)
    
    def tag1InParentheses(self):
        if (self.tag1.text[1] == "(" and self.tag1.text[-1] == ")"):
            return True
        if self.tag1.start >= 0 and self.tag1.end < len(self.doc.text) - 1:
            if (self.doc.text[self.tag1.start - 1] == "(" and self.doc.text[self.tag1.end] == ")"):
                return True
        return False
    
    def textBetweenTagsContainsBrokenEnumerationCharacter(self):
        textBetween = self.textBetweenTags()
        brokenEnumerationCharInText = list(filter(lambda ch: ch in textBetween, brokenEnumeration))
        return any(brokenEnumerationCharInText)
    def textBetweenTagsContainsText(self, text):
        textBetween = self.textBetweenTags()
        return text in textBetween
    
        
class TagInfo():
    def __init__(self, idx, start, end, tag, text):
        self.idx = idx
        self.start = int(start)
        self.end = int(end)
        self.tag = tag
        self.text = text
    def __str__(self):
        return f"TagInfo[{self.idx}, {self.start}, {self.end}, {self.tag}, {self.text}]"

class AggregatedResults():
    def __init__(self, relations, description = ""):
        self.relations = relations
        self.allRelations = len(relations)
        self.oks = len(list(filter(lambda rel: rel.isOK(), relations)))
        self.redundantAndRemoveds = len(list(filter(lambda rel: rel.isRedundantAndRemoved(), relations)))
        self.shouldNotBeRemoveds = len(list(filter(lambda rel: rel.shouldNotBeRemoved(), relations)))
        self.shouldBeBemoveds = len(list(filter(lambda rel: rel.shouldBeBemoved(), relations)))
        self.description = description

    def goodQuantity(self):
        return self.oks + self.redundantAndRemoveds

    def badQuantity(self):
        return self.shouldNotBeRemoveds + self.shouldBeBemoveds

    def rate(self):
        if (self.goodQuantity() + self.badQuantity()) > 0:
            return (self.goodQuantity()  * 100) / (self.goodQuantity() + self.badQuantity())
        else:
            return 100
        
    def rate1(self):
        if (self.oks + self.badQuantity()) > 0:
            return (self.oks * 100) / (self.oks + self.badQuantity())
        else:
            return 100
        
    def rateRedundant(self):
        if (self.oks + self.shouldBeBemoveds) > 0:
            return (self.oks * 100) / (self.oks + self.shouldBeBemoveds)
        else:
            return 100
    def rateTooManyRemoved(self):
        if (self.oks + self.shouldNotBeRemoveds) > 0:
            return (self.oks * 100) / (self.oks + self.shouldNotBeRemoveds)
        else:
            return 100
    def rateAVG(self):
        return (self.rateRedundant() + self.rateTooManyRemoved()) / 2

    def isTooBad(self):
        return self.rate() < 88
    def rateInfo(self):
        if self.isTooBad():
            return "BAD"
        else:
            return "GOOD"

    def infoList(self):
        result = []
        result.append(f"description           : {self.description}\n")
        result.append(f"allRelations          : {self.allRelations}\n")
        result.append(f"oks                   : {self.oks}\n")
        result.append(f"isRedundantAndRemoveds: {self.redundantAndRemoveds}\n")
        result.append(f"shouldNotBeRemoveds   : {self.shouldNotBeRemoveds}\n")
        result.append(f"shouldBeBemoveds      : {self.shouldBeBemoveds}\n")
        result.append(f"rate                  : {self.rate()} {self.rateInfo()}\n")
        result.append(f"GOOD / BAD            : {self.goodQuantity()} / {self.badQuantity()}\n")
        result.append(f"rate1                 : {self.rate1()}\n")
        result.append(f"GOOD / BAD (1)        : {self.oks} / {self.badQuantity()}\n")
        result.append(f"rate redundant        : {self.rateRedundant()}\n")
        result.append(f"rate too many         : {self.rateTooManyRemoved()}\n")
        result.append(f"rate AVG              : {self.rateAVG()}\n")
        result.append("\n\n")
        return result

    def printInfoList(self):
        for info in self.infoList():
            print(info)

class PartitionedAggregatedResults():
    def __init__(self, relations, description = ""):
        self.aggregateResults = AggregatedResults(relations, description)
        self.datAggregateResults = AggregatedResults(list(filter(lambda relation: relation.rType == "Dat", relations)), f"{description} Dat")
        self.negAggregateResults = AggregatedResults(list(filter(lambda relation: relation.rType == "Neg", relations)), f"{description} Neg")
        self.invAggregateResults = AggregatedResults(list(filter(lambda relation: relation.rType == "Inv", relations)), f"{description} Inv")
        self.drgAggregateResults = AggregatedResults(list(filter(lambda relation: relation.rType == "Drg", relations)), f"{description} Drg")
        self.algAggregateResults = AggregatedResults(list(filter(lambda relation: relation.rType == "Alg", relations)), f"{description} Alg")

    def infoList(self):
        result = ["----------------------------------------------------------"]
        result += self.aggregateResults.infoList()
        result += ["\n\n"]
        result += self.datAggregateResults.infoList()
        result += ["\n\n"]
        result += self.negAggregateResults.infoList()
        result += ["\n\n"]
        result += self.invAggregateResults.infoList()
        result += ["\n\n"]
        result += self.drgAggregateResults.infoList()
        result += ["\n\n"]
        result += self.algAggregateResults.infoList()
        return  result

    def isTooBad(self, rType = ""):
        if rType == "":
            return self.aggregateResults.isTooBad()
        elif rType == "Dat":
            return self.datAggregateResults.isTooBad()
        elif rType == "Neg":
            return self.negAggregateResults.isTooBad()
        elif rType == "Inv":
            return self.invAggregateResults.isTooBad()
        elif rType == "Drg":
            return self.drgAggregateResults.isTooBad()
        elif rType == "Alg":
            return self.algAggregateResults.isTooBad()
        else:
            return False

def findNotRemoved(relations):
    return list(filter(lambda relation: not relation.removed ,relations))

def lineToTag(line):
    splittedByAllWhitespaces = line.split()
    splittedByTabs = line.split("\t")
    tagInfo = TagInfo(splittedByTabs[0], splittedByAllWhitespaces[2], splittedByAllWhitespaces[3], splittedByAllWhitespaces[1], splittedByTabs[2])
    return tagInfo

def isAbleToCreateTag(line):
    splittedByAllWhitespaces = line.split()
    splittedByTabs = line.split("\t")
    
    return len(splittedByAllWhitespaces) > 3 and len(splittedByTabs) > 2 and splittedByAllWhitespaces[2].isdigit() and splittedByAllWhitespaces[3].isdigit()

def tagsFromFile(filename):
    lines = filter(lambda line: line.startswith('T') and isAbleToCreateTag(line), linesFromFile(filename))
    return list(map(lineToTag, lines))

def findTagsForSentence(sentence, tags):
    minIdx = -1
    maxIdx = 0
    for wordIdx,token in enumerate(sentence, start = 0):
        if minIdx < 0:
            minIdx = token.idx
        if maxIdx < token.idx:
            maxIdx = token.idx
    
    result = list(filter(lambda tagInfo: tagInfo.start >= minIdx and tagInfo.start <= maxIdx, tags))
    return result 

def findByTag(tags, tagName):
    return list(filter(lambda tagInfo: tagInfo.tag == tagName, tags))

def createRelations(tags1, tags2, rType, startIdx, sentenceIdx, doc):
    relations = []
    currentIdx = startIdx
    for tag1 in tags1:
        for tag2 in tags2:
            relations.append(Relation(currentIdx, rType, tag1.idx, tag2.idx, sentenceIdx, tag1, tag2, doc))
            currentIdx += 1
    return relations

def printTags(tags):
    for tag in tags:
        print(tag)
        
def findRelations(rType, sentence, tagsForSentence, fromTagType, toTagTypes, startIdx, sentenceIdx, doc):
    tags1 = findByTag(tagsForSentence, fromTagType)
    tags2 = []
    for toTagType in toTagTypes:
        tags2 += findByTag(tagsForSentence, toTagType)
    return createRelations(tags1, tags2, rType, startIdx, sentenceIdx, doc)

def incrementedMaxId(relations, startIdx):
    if len(relations) == 0:
        return startIdx
    else:
        return max(map(lambda relation: relation.idx, relations)) + 1

def suspectRelationsInSentence(sentence, tags, startIdx, sentenceIdx, doc):
    tagsForSentence = findTagsForSentence(sentence, tags)
    relations = findRelations("Inv", sentence, tagsForSentence, "Investigation", ["Investigation_result"], startIdx, sentenceIdx, doc)
    relations += findRelations("Neg", sentence, tagsForSentence, "Negation", ["Symptom", "Condition", "Behaviour", "Treatment", "Investigation", "Investigation_result", "Drug", "Drug_dose"], incrementedMaxId(relations, startIdx), sentenceIdx, doc)
    relations += findRelations("Drg", sentence, tagsForSentence, "Drug", ["Drug_dose"], incrementedMaxId(relations, startIdx), sentenceIdx, doc)
    relations += findRelations("Dat", sentence, tagsForSentence, "Date", ["Symptom", "Condition", "Behaviour", "Treatment", "Investigation", "Drug"], incrementedMaxId(relations, startIdx), sentenceIdx, doc)
    relations += findRelations("Alg", sentence, tagsForSentence, "Condition", ["Drug"], incrementedMaxId(relations, startIdx), sentenceIdx, doc)
    return relations

def findSuspectRelations(tags, text):
    doc = nlp(text)
    relations = []
    sentences = []
    mxIdx = 1
    for idx, sentence in enumerate(doc.sents, start = 0):
        sentences.append(SentenceForRelation(idx, sentence))
        mxIdx = incrementedMaxId(relations, mxIdx)
        relations += suspectRelationsInSentence(sentence, tags, mxIdx, idx, doc)
#        print(f"mxIdx: {mxIdx}  len(relations): {len(relations)}")
    return (relations, sentences)

def loggg(isLoggg, text):
    if isLoggg:
        print(text)
        
def logg(relation, text):
    isLog = relation.rType == "Dat" and "artroskopia kolana" in relation.tag2.text
    loggg(isLog, text)
        
def check(relation):
    return "T28" in relation.arg1

def setRremovedBecauseOtherFirstTagBetween(selectedRelations):
    notRemovedRelations = findNotRemoved(selectedRelations)
    for relation in notRemovedRelations:
        start1 = relation.tag1.start
        start2 = relation.tag2.start
        relWithFirstTagsBetween = list(filter(lambda rel: rel.getRank() > relation.getRank() and rel.tag1.start > start1 and rel.tag1.start < start2 and not rel.almostOnlyConcunctionOrPunctuationBetweenFirstTags(relation.tag1), notRemovedRelations))
        if len(relWithFirstTagsBetween) > 0:
#            ranksComparison = list(map(lambda r: r.getRank() > relation.getRank(), relWithFirstTagsBetween))
#            if all(ranksComparison):
            relation.setRemoved(True, "other first tag between (right)")
    for relation in notRemovedRelations: #kiedy relacja jest w lewo czyli tag2.start < tag1.start
        end2 = relation.tag2.end
        end1 = relation.tag1.end
        relWithFirstTagsBetween = list(filter(lambda rel: rel.getRank() > relation.getRank() and rel.tag1.end > end2 and rel.tag1.end < end1 and not rel.almostOnlyConcunctionOrPunctuationBetweenFirstTags(relation.tag1), notRemovedRelations))
        if len(relWithFirstTagsBetween) > 0:
#            ranksComparison = list(map(lambda r: r.getRank() > relation.getRank(), relWithFirstTagsBetween))
#            if all(ranksComparison):
            relation.setRemoved(True, "other first tag between (left)")
            
def isRelationNotAbleToRemove(relation, relations):
    return len(list(filter(lambda r: r.tag1.start == relation.tag1.start, relations))) <= 1

def isConnectedByTag2(notAbleToRemoveRelation, relation):
    return relation.getRank() <= notAbleToRemoveRelation.getRank() and relation.tag2.start == notAbleToRemoveRelation.tag2.start and relation.tag1.start != notAbleToRemoveRelation.tag1.start and not notAbleToRemoveRelation.almostOnlyConcunctionOrPunctuationBetweenFirstTags(relation.tag1)
            
def findAndSetRemovedByMultipleConnections(notRemovedRelations, notAbleToRemoveRelations):
    currentlyRemovedRelations = []
    for notAbleToRemoveRelation in notAbleToRemoveRelations:
        multipleConnectedByTag2 = list(filter(lambda relation: isConnectedByTag2(notAbleToRemoveRelation, relation), notRemovedRelations))
        for relation in multipleConnectedByTag2:
            relation.setRemoved(True, "multipleConnectedByTag2")
            currentlyRemovedRelations.append(relation)
                
    return currentlyRemovedRelations
    
def setRemovedBecauseMultipleConnection(selectedRelations):
    notRemovedRelations = findNotRemoved(selectedRelations)
    notAbleToRemoveRelations = list(filter(lambda relation: isRelationNotAbleToRemove(relation, notRemovedRelations), notRemovedRelations))
    if len(notRemovedRelations) > len(notAbleToRemoveRelations):
        removedByMultipleConnections = findAndSetRemovedByMultipleConnections(notRemovedRelations, notAbleToRemoveRelations)
        if len(removedByMultipleConnections) > 0:
            setRemovedBecauseMultipleConnection(notRemovedRelations)
 
def findRelationsWithSecondTagOnTheLeft(relations):
    foundRelations = []
    for relation in relations:
        tag1 = relation.tag1
        otherRelationsWithTag1AndSecondTagOnTheLeft = list(filter(lambda rel: rel.tag1.start == tag1.start and rel.tag2.start < rel.tag1.start, relations))
        if len(otherRelationsWithTag1AndSecondTagOnTheLeft) >= 1:
            foundRelations.append(relation)
    return foundRelations

def findRelationsWithSecondTagOnTheRight(relations):
    foundRelations = []
    for relation in relations:
        tag1 = relation.tag1
        otherRelationsWithTag1AndSecondTagOnTheRight = list(filter(lambda rel: rel.tag1.start == tag1.start and rel.tag2.start > rel.tag1.start, relations))
        if len(otherRelationsWithTag1AndSecondTagOnTheRight) >= 1:
            foundRelations.append(relation)
    return foundRelations
    
def setRemovedBecauseOneSecondTagOnTheLeftAndOtherSecondTagsOnTheRight(relations):
    notRemovedRelations = findNotRemoved(relations)
    relationsWithSecondTagOnTheLeft = findRelationsWithSecondTagOnTheLeft(notRemovedRelations)
#    print("second tag on the left")
#    print(len(relationsWithSecondTagOnTheLeft))
    for relation in relationsWithSecondTagOnTheLeft:
#        loggg(check(relation), f"mamy ${relation}")
        tag1 = relation.tag1
        tag2 = relation.tag2
        rType = relation.rType
        otherRelationsWithSecondTagsOnTheRight = list(filter(lambda rel: rel.getRank() < relation.getRank() and rel.rType == rType and rel.tag1.start == tag1.start and rel.tag2.start > tag2.start, notRemovedRelations))
        if len(otherRelationsWithSecondTagsOnTheRight) >= 1:
            for rel in otherRelationsWithSecondTagsOnTheRight:
                rel.setRemoved(True, "many second tags on the right")
                
def setRemovedBecauseOneSecondTagOnTheRightAndOtherSecondTagsOnTheLeft(relations):
    notRemovedRelations = findNotRemoved(relations)
    relationsWithSecondTagOnTheRight = findRelationsWithSecondTagOnTheRight(notRemovedRelations)
    for relation in relationsWithSecondTagOnTheRight:
        tag1 = relation.tag1
        tag2 = relation.tag2
        rType = relation.rType
        otherRelationsWithSecondTagsOnTheLeft = list(filter(lambda rel: rel.getRank() < relation.getRank() and rel.rType == rType and rel.tag1.start == tag1.start and rel.tag2.start < tag2.start, notRemovedRelations))
        if len(otherRelationsWithSecondTagsOnTheLeft) >= 1:
            for rel in otherRelationsWithSecondTagsOnTheLeft:
                if (rel.getRank() <= relation.getRank()):
                    rel.setRemoved(True, "many second tags on the left")
    
def findNotRemovedByRelType(relations, rType):
    return list(filter(lambda relation: relation.rType == rType, findNotRemoved(relations)))

def setRemovedRedundantRelationsByType(relations, rType):
    selectedRelations = findNotRemovedByRelType(relations, rType)
    setRremovedBecauseOtherFirstTagBetween(selectedRelations)
    setRemovedBecauseMultipleConnection(selectedRelations)

def isSimilar(tag1, tag2):
    connectedTags = set(["Symptom", "Condition"])
    isTheSame = tag1 == tag2
    isConnected = tag1 in connectedTags and tag2 in connectedTags
    return isTheSame or isConnected
    
def checkOtherSecondTagBetweenForDat(relation, relationsWithSecondTagsBetween):
    relationsWithBigRank = list(filter(lambda rel: rel.getRank() - relation.getRank() > 1, relationsWithSecondTagsBetween))
    if len(relationsWithBigRank) > 0:
        relation.setRemoved(True, "other second tag between (big rank) (dat)")
    else:
        for ch in brokenEnumeration:
            relationsWithoutBrokenEnumerationCharacters = list(filter(lambda rel: not rel.textBetweenTagsContainsText(ch), relationsWithSecondTagsBetween))
            brokenEnumerationCharactersQuantityList = list(map(lambda rel: rel.tag2.text.count(ch), relationsWithoutBrokenEnumerationCharacters))
            brokenEnumerationCharactersQuantity = lsum(brokenEnumerationCharactersQuantityList)
            brokenEnumerationCharactersQuantityBetweenTags = relation.textBetweenTags().count(ch)
            if len(relationsWithoutBrokenEnumerationCharacters) > 0 and brokenEnumerationCharactersQuantity < brokenEnumerationCharactersQuantityBetweenTags:
                relation.setRemoved(True, f"wrong enumeration char {ch}")

def setRremovedBecauseOtherSecondTagBetween(relations):
    for relation in relations:
        start1 = relation.tag1.start
        start2 = relation.tag2.start
        tagType = relation.tag2.tag
        relationsWithSecondTagsBetween = []
        if relation.rType != "Dat":
            relationsWithSecondTagsBetween = list(filter(lambda rel: rel.getRank() >= relation.getRank() and rel.tag2.start > start1 and rel.tag2.start < start2 and not isSimilar(rel.tag2.tag, tagType), relations))
        else:
            relationsWithSecondTagsBetween = list(filter(lambda rel: rel.getRank() >= relation.getRank() and rel.tag2.start > start1 and rel.tag2.start < start2, relations))
        if len(relationsWithSecondTagsBetween) > 0:
            if (relation.rType == "Dat"):
                checkOtherSecondTagBetweenForDat(relation, relationsWithSecondTagsBetween)
            else:
                relation.setRemoved(True, "other second tag between (right)")
    for relation in relations:
        end2 = relation.tag2.end
        end1 = relation.tag1.end
        tagType = relation.tag2.tag
        relationsWithSecondTagsBetween = []
        # usunięto warunek:  and not isSimilar(rel.tag2.tag, tagType)
        if relation.rType != "Dat":
            relationsWithSecondTagsBetween = list(filter(lambda rel: rel.getRank() >= relation.getRank() and rel.tag2.end > end2 and rel.tag2.end < end1, relations))
        else:
            # zmieniono rel.getRank() - relation.getRank() > 1 na  rel.getRank() >= relation.getRank()
            relationsWithSecondTagsBetween = list(filter(lambda rel: rel.getRank() >= relation.getRank() and rel.tag2.end > end2 and rel.tag2.end < end1 , relations))
        if len(relationsWithSecondTagsBetween) > 0:
#            relation.setRemoved(True, "other second tag between (left)")
            if (relation.rType == "Dat"):
                checkOtherSecondTagBetweenForDat(relation, relationsWithSecondTagsBetween)
            else:
                relation.setRemoved(True, "other second tag between (left)")

def setRemovedBecauseMultipleConnectionOfTag1WithDifferentTypesOfTag2(relations):
    notRemovedRelations = findNotRemoved(relations)
#    tags2 = list(map(lambda relation: relation.tag2, notRemovedRelations))
    setRremovedBecauseOtherSecondTagBetween(notRemovedRelations)

def setRemovedBecauseOfLine(relations):
    notRemovedRelations = findNotRemoved(relations)
    for relation in notRemovedRelations:
        tag1 = relation.tag1
        relationsWithTag1 = list(filter(lambda rel: rel.tag1.start == tag1.start, notRemovedRelations))
        if relation.isTagsInTheSameLine():
            relationsNotInTheSameLine =list(filter(lambda rel: not rel.isTagsInTheSameLine(), relationsWithTag1))
            for rel in relationsNotInTheSameLine:
                rel.setRemoved(True, "Tag2 not in the same line")
                
def setRemovedBecauseFirstTagOnTheOtherSideAndLowerRank(relations):
    notRemovedRelations = findNotRemoved(relations)
    for relation in notRemovedRelations:
        tag2 = relation.tag2
        relationsWithTag2 = list(filter(lambda rel: rel.tag2.start == tag2.start, notRemovedRelations))
        for rel in relationsWithTag2:
            if rel.isRight() != relation.isRight() and rel.getRank() < relation.getRank():
                rel.setRemoved(True, "the same tag2, but tag1 on the oter side and lower rank")
                
def textToLenIfInside(txt, otherTxt):
    if txt in otherTxt:
        return len(txt)
    else:
        return 0
                
def isTooLongTextAndNotPartOfEnumeration(relation, algRelations):
    textBetween = relation.textBetweenTags()
    textBetweenLen = len(textBetween)
    tag1 = relation.tag1
    (tag2From1, tag2To1) = (relation.tag1.end, relation.tag2.start)
    (tag2From2, tag2To2) = (relation.tag2.end, relation.tag1.start)
    relationsWithTag1 = list(filter(lambda rel: rel.tag1.start == tag1.start, algRelations))
    relationsWithTag2InBoundary = list(filter(lambda rel: (rel.tag2.start >= tag2From1 and rel.tag2.end < tag2To1) or (rel.tag2.start >= tag2From2 and rel.tag2.end < tag2To2), relationsWithTag1))
    tags2Len = list(map(lambda rel: len(rel.tag2.text), relationsWithTag2InBoundary))
    tags2LenSum = lsum(tags2Len)
    allowedTextsLenBetweenTags = list(map(lambda txt: textToLenIfInside(txt, textBetween) , allowedBetweenAlgTags))
    allowedTextsLenBetweenTagsSum = lsum(allowedTextsLenBetweenTags)
    return textBetweenLen - tags2LenSum - allowedTextsLenBetweenTagsSum > textLenLimit
    

def setRemovedAlgBecauseBecauseTooManyCharactersBetweenTags(relations):
    algRelations = findNotRemovedByRelType(relations, "Alg")
    for relation in algRelations:
        if isTooLongTextAndNotPartOfEnumeration(relation, relations):
            textBetweenLen = len(relation.textBetweenTags())
            relation.setRemoved(True, f"too long text between {textBetweenLen} limit:{textLenLimit}")

def setRemovedNegationsBecauseTag1DoNotMatchTag2(relations):
    negations = findNotRemovedByRelType(relations, "Neg")
    for reservedNegation in list(reservedNegationsForTags):
        reservedTags = reservedNegationsForTags[reservedNegation]
        for relation in negations:
            tag1 = relation.tag1
            if reservedNegation in tag1.text:
                if not (relation.tag2.tag in reservedTags):
                    relation.setRemoved(True, f"{reservedNegation} not for {relation.tag2.tag}")

def relationWithTag2MostLeft(relations):
    tag2Starts = list(map(lambda rel: rel.tag2.start, relations))
    minTag2Start = min(tag2Starts)
    return list(filter(lambda rel: rel.tag2.start == minTag2Start, relations))[0]

def relationsWithout(relations, relation):
    return list(filter(lambda rel: not (rel.tag1.start == relation.tag1.start and rel.tag2.start == relation.tag2.start), relations))

def removeAll(relations, reason):
    for relation in relations:
        relation.setRemoved(True, reason)

def isTooFar(rel1, rel2):
    return len(rel1.textBetweenSecondTags(rel2.tag2)) > 25

def removeRelationsBecauseWrongEnumeration(relationsWithTag1OnTheLeft, inputRank = -1):
    notRemovedRelations = findNotRemoved(relationsWithTag1OnTheLeft)
    if len(notRemovedRelations) > 1:
        firstRelation = relationWithTag2MostLeft(notRemovedRelations)
        relationsWithoutFirstRelation = relationsWithout(notRemovedRelations, firstRelation)
        secondRelation = relationWithTag2MostLeft(relationsWithoutFirstRelation)
        basicRank = 0
        if inputRank < 0:
            basicRank = firstRelation.getRank()
        else:
            basicRank = inputRank
        if isTooFar(firstRelation, secondRelation) and secondRelation.getRank() <= basicRank:
            removeAll(relationsWithoutFirstRelation, f"Too far from {firstRelation.tag1} {firstRelation.tag2}")
        else:
            removeRelationsBecauseWrongEnumeration(relationsWithoutFirstRelation, basicRank)

def setRemovedBecauseWrongEnumerationForDat(relations):
    notRemovedRelations = findNotRemovedByRelType(relations, "Dat")
    for relation in notRemovedRelations:
        tag1 = relation.tag1
        relationsWithTag1OnTheLeft = list(filter(lambda rel: rel.tag1.start == tag1.start, notRemovedRelations))
        removeRelationsBecauseWrongEnumeration(relationsWithTag1OnTheLeft)

# poniższa funkcja chyba jest do usunięcia
def setRemovedBecauseDatInParenthesesShouldBeOnlyForNearestTag(relationsInSentence):
    notRemovedRelations = findNotRemovedByRelType(relationsInSentence, "Dat")
    for relation in notRemovedRelations:
        textLenLimit = 10
        textBetweenLen = len(relation.textBetweenTags())
        if relation.tag1InParentheses() and textBetweenLen > textLenLimit:
            relation.setRemoved(True, f"tag1 in parentheses and too long text between {textBetweenLen} limit:{textLenLimit}")
            
def setRemovedBecauseAlgNegeted(relationsInSentence):
    negRelations = findNotRemovedByRelType(relationsInSentence, "Neg")
    algRelations = findNotRemovedByRelType(relationsInSentence, "Alg")
    for algRel in algRelations:
        algTag1 = algRel.tag1
        for negRel in negRelations:
            negTag2 = negRel.tag2
            if negTag2.start == algTag1.start:
                algRel.setRemoved(True, "Alg Tag1 negated")
                
def setRemovedBecauseAlgTag1NotContainMandatoryText(relationsInSentence):
    algRelations = findNotRemovedByRelType(relationsInSentence, "Alg")
    for algRel in algRelations:
        algTag1Text = algRel.tag1.text.lower()
        containsMandatoryText = False
        for text in mandatoryForAlgTag1:
            if text in algTag1Text:
                containsMandatoryText = True
        if not containsMandatoryText:
            algRel.setRemoved(True, "No mandatory text for Alg relation")
            
def setRemovedBecauseAlgContainsForbiddenTextBetweenTags(relationsInSentence):
    algRelations = findNotRemovedByRelType(relationsInSentence, "Alg")
    for algRel in algRelations:
        textBetween = algRel.textBetweenTags()
        for notAllowed in notAllowedBetweenAlgTags:
            if notAllowed in textBetween:
                algRel.setRemoved(True, f"Not allowed text between tags: '{notAllowed}'")
    
    
                
def setRemovedBecauseOnlyOneRelationHasTag1AndRankIsLow(notRemovedRelations):
    for relation in notRemovedRelations:
        otherRelationWithTag1 = list(filter(lambda rel: rel.tag1.start == relation.tag1.start and rel.tag2.start != relation.tag2.start, notRemovedRelations))
        if len(otherRelationWithTag1) == 0 and relation.getRank() < maxRank:
            relation.setRemoved(True, "One relation has tag1 and rank is low")
            


def removeRedundantRelations1(relations, sentences):
    for sentence in sentences:
        relationsInSentence = list(filter(lambda relation: relation.sentenceIdx == sentence.idx, relations))
        setRemovedNegationsBecauseTag1DoNotMatchTag2(relationsInSentence)
        setRemovedRedundantRelationsByType(relationsInSentence, "Inv")
        setRemovedRedundantRelationsByType(relationsInSentence, "Neg")
        setRemovedRedundantRelationsByType(relationsInSentence, "Drg")
        setRemovedRedundantRelationsByType(relationsInSentence, "Dat")
        setRemovedRedundantRelationsByType(relationsInSentence, "Alg")
        setRemovedBecauseMultipleConnectionOfTag1WithDifferentTypesOfTag2(relationsInSentence)
        setRemovedBecauseOneSecondTagOnTheLeftAndOtherSecondTagsOnTheRight(relationsInSentence)
        setRemovedBecauseOneSecondTagOnTheRightAndOtherSecondTagsOnTheLeft(relationsInSentence)
        setRemovedBecauseOfLine(relationsInSentence)
        setRemovedBecauseFirstTagOnTheOtherSideAndLowerRank(relationsInSentence)
        setRemovedAlgBecauseBecauseTooManyCharactersBetweenTags(relationsInSentence)
        setRemovedBecauseOnlyOneRelationHasTag1AndRankIsLow(findNotRemovedByRelType(relationsInSentence, "Drg"))
        setRemovedBecauseOnlyOneRelationHasTag1AndRankIsLow(findNotRemovedByRelType(relationsInSentence, "Alg"))

def removeRedundantRelations2(relations, sentences):
    for sentence in sentences:
        relationsInSentence = list(filter(lambda relation: relation.sentenceIdx == sentence.idx, relations))
        setRemovedBecauseWrongEnumerationForDat(relationsInSentence)
        setRemovedBecauseAlgNegeted(relationsInSentence)
        setRemovedBecauseAlgTag1NotContainMandatoryText(relationsInSentence)
        setRemovedBecauseAlgContainsForbiddenTextBetweenTags(relationsInSentence)
#        setRemovedBecauseDatInParenthesesShouldBeOnlyForNearestTag(relationsInSentence) jest złe

def removeRedundantRelations(relations, sentences, attempts = 1):
    for i in range(0, attempts):
        removeRedundantRelations1(relations, sentences)
    removeRedundantRelations2(relations, sentences)

def checkIfRelationsInLines(relation, annLines):
    matching = [s for s in annLines if relation.relationStr() in s]
    if len(matching) > 0:
        relation.setOk(True)
    else:
        relation.setOk(False)
    return relation

def checkIfRelationsInInputFile(annFile, relations):
    annLines = linesFromFile(annFile)
    return list(map(lambda relation: checkIfRelationsInLines(relation, annLines), relations))
        

def writeRelationsToFile(relations, filename):
    relationsLines = list(map(lambda relation: relation.toLine(), relations))
    relationsLines.sort()
    writeToFile(relationsLines, filename)
    
def appendRelationsToFile(relations, filename):
    relationsLines = list(map(lambda relation: relation.toLine(False), relations))
    relationsLines.sort()
    appendToFile(relationsLines, filename)

def aggregatedResults(relations):
    allRelations = len(relations)
    oks = len(list(filter(lambda rel: rel.isOK(), relations)))
    isRedundantAndRemoveds = len(list(filter(lambda rel: rel.isRedundantAndRemoved(), relations)))
    shouldNotBeRemoveds = len(list(filter(lambda rel: rel.shouldNotBeRemoved(), relations)))
    shouldBeBemoveds = len(list(filter(lambda rel: rel.shouldBeBemoved(), relations)))
    result = []
    result.append(f"allRelations          : {allRelations}\n")
    result.append(f"oks                   : {oks}\n")
    result.append(f"isRedundantAndRemoveds: {isRedundantAndRemoveds}\n")
    result.append(f"shouldNotBeRemoveds   : {shouldNotBeRemoveds}\n")
    result.append(f"shouldBeBemoveds      : {shouldBeBemoveds}\n")
    result.append(f"GOOD / BAD            : {oks + isRedundantAndRemoveds} / {shouldNotBeRemoveds + shouldBeBemoveds}")
    result.append("\n")
    return result
    
def writeSentencesWithRelationsToFile(sentences, relations, sentencesFile):
    linesToSave = aggregatedResults(relations)
    for sentence in sentences:
        relationsForSentence = list(filter(lambda relation: relation.sentenceIdx == sentence.idx, relations))
        linesToSave.append(f"{str(sentence)}\n")
        for relation in relationsForSentence:
            linesToSave.append(relation.lineWithTextInfo())
        linesToSave.append("\n\n")
    writeToFile(linesToSave, sentencesFile)

def reindex(relations):
    
    for idx,relation in enumerate(relations, start = 3):
        relation.setIdx(idx)


def singleProcess():
    folder = "train1"
    prefix = "karszym_"
    fileIdx = 166
    attempt = ""
    
    # INPUT FILES
    annFile =   f"input/{folder}/{prefix}patient_{fileIdx}.ann"
    textFile =  f"input/{folder}/{prefix}patient_{fileIdx}.txt"
    checkFile = f"input/{folder}/{prefix}patient_{fileIdx}.ann"
    
    # OUTPUT FILE
    outputFile = f"output/{folder}/{prefix}patient_{fileIdx}{attempt}_relations.txt"
    sentencesFile = f"output/{folder}/{prefix}patient_{fileIdx}{attempt}_sentences.txt"
    
    tags = tagsFromFile(annFile)
    text = textFromFile(textFile)
    (relations, sentences) = findSuspectRelations(tags, text)
    removeRedundantRelations(relations, sentences, 2)
    relations = checkIfRelationsInInputFile(checkFile, relations)
    writeSentencesWithRelationsToFile(sentences, relations, sentencesFile)
    relations = list(filter(lambda relation: not relation.removed, relations))
    #reindex(relations)
    writeRelationsToFile(relations, outputFile)
    
    
def singleProcessForSelectedFiles(fileInfo, outputFolder):
    
    # INPUT FILES
    annFile = fileInfo.annPath
    textFile = fileInfo.txtPath
    checkFile = fileInfo.annPath
    
    # OUTPUT FILE
    outputFile = f"{outputFolder}/{fileInfo.basename}_relations.txt"
    sentencesFile = f"{outputFolder}/{fileInfo.basename}_sentences.txt"
    
    tags = tagsFromFile(annFile)
    text = textFromFile(textFile).replace("\\x0a", "\n   ")
    (relations, sentences) = findSuspectRelations(tags, text)
    removeRedundantRelations(relations, sentences, 2)
    relations = checkIfRelationsInInputFile(checkFile, relations)
    writeSentencesWithRelationsToFile(sentences, relations, sentencesFile)
    relationsToSave = list(filter(lambda relation: not relation.removed, relations))
    writeRelationsToFile(relationsToSave, outputFile)
    print(f"finished {annFile}")
#    todo: zapisywać dodatkowo słabo zgodne zbiory relacji.
    return relations
    
    
def fileInfos(folder):
    files = []
    for r, d, f in os.walk(folder):
        for file in f:
            if ".ann" in file:
                basename = file.replace(".ann", "")
                annFilePath = os.path.join(r, file)
                txtFilePath = folder + "/" + basename + ".txt"
                if os.path.isfile(txtFilePath):
                    files.append(FileInfo(basename, annFilePath, txtFilePath, folder))
    return files
    
def relationsForAll(inputFolder, outputFolder):
    inputFiles = fileInfos(inputFolder)
    
    allRelations = []
    badAggregatedResults = []
    i = 0
    filesQuantity = len(inputFiles)

    for fileInfo in inputFiles:
        i += 1
        print(f"{i}/{filesQuantity}  {fileInfo}")
        currentRelations = singleProcessForSelectedFiles(fileInfo, outputFolder)
        currentAggregatedResult = PartitionedAggregatedResults(currentRelations, fileInfo.basename)
        if currentAggregatedResult.isTooBad("Alg"):
            badAggregatedResults.append(currentAggregatedResult)
        allRelations += currentRelations

    aggregatedResultsObject = PartitionedAggregatedResults(allRelations, "All relations")
    results = aggregatedResults(allRelations)
    print(len(allRelations))
    writeToFile(results, outputFolder + "/aggregatedResults.txt")

    aggregatedResultsWithBadResults = aggregatedResultsObject.infoList()
    for badAggregatedResult in badAggregatedResults:
        aggregatedResultsWithBadResults += badAggregatedResult.infoList()
    
    writeToFile(aggregatedResultsWithBadResults, outputFolder + "/aggregatedResultsObject.txt")



#inputFolder = "input/train51"
#outputFolder = "output/train51"
#relationsForAll(inputFolder, outputFolder)
# singleProcess()


