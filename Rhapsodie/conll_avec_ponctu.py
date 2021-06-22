#!/usr/bin/python3
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2020 Kim Gerdes
# kim AT gerdes. fr
# http://arborator.ilpga.fr/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public License (the "License")
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of of version 3 of the GNU Affero General Public License
# from http://www.gnu.org/licenses/agpl-3.0.html 
####

import collections, re
#debug=False
debug=True


class Tree(dict):
	"""
	just a dictionary that maps nodenumber->{"t":"qsdf", ...}
	moreover: 
		sentencefeatures is a dictionary with sentence wide information, eg "comments":"comment line content"
			there is a special key: _comments used for comments that are not of the form x = yyy, they are stored as such
		words is not necessarily a list of tokens: it contains the actual correctly spelled words, ie. the hyphen (1-2) lines
	"""
	def __init__(self, *args, **kwargs):
		self.update(*args, **kwargs)
		self.sentencefeatures={}
		self.rooti=None
		self.words=[]
		

	def __getitem__(self, key):
		val = dict.__getitem__(self, key)
		#print 'GET', key
		return val

	def __setitem__(self, key, val):
		#print 'SET', key, val
		dict.__setitem__(self, key, val)

	def __repr__(self):
		#dictrepr = dict.__repr__(self)
		#return '%s(%s)' % (type(self).__name__, dictrepr)
		return self.conllu()
		#return "\n".join(["Tree: "+self.sentence()]+[f+": "+v for f,v in self.sentencefeatures.items()]+[str(i)+": "+self[i].get("t","")+"\t"+str(self[i]) for i in self])
	
	def update(self, *args, **kwargs):
		#print 'update', args, kwargs
		for k, v in dict(*args, **kwargs).items():
			self[k] = v
	
	def sentence(self):
		if self.words==[]:
			self.words = [self[i].get("t","") for i in sorted(self)]
		return " ".join(self.words)
	
	def conllu(self):
		morphoSynt= ['Abbr', 'AbsErgDatNumber', 'AbsErgDatPerson', 'AbsErgDatPolite', 'AdpType', 'AdvType', 'Animacy', 'Aspect', 'Case', 'Clusivity', 'ConjType', 'Definite', 'Degree', 'Echo', 'ErgDatGender', 'Evident', 'Foreign', 'Gender', 'Hyph', 'Mood', 'NameType', 'NounClass', 'NounType', 'NumForm', 'NumType', 'NumValue', 'Number', 'PartType', 'Person', 'Polarity', 'Polite', 'Poss', 'PossGender', 'PossNumber', 'PossPerson', 'PossedNumber', 'Prefix', 'PrepCase', 'PronType', 'PunctSide', 'PunctType', 'Reflex', 'Style', 'Subcat', 'Tense', 'Typo', 'VerbForm', 'VerbType', 'Voice']
		specialFeatures=["t", "lemma", "tag", "tag2", "xpos", "egov", "id", "index", "gov", "kids", "govrel", "span"]
		treestring = ""
		for stftkey in sorted(self.sentencefeatures):
			if stftkey=="_comments":
				if self.sentencefeatures[stftkey].endswith("#"): self.sentencefeatures[stftkey]=self.sentencefeatures[stftkey][:-1]
				treestring+="# "+self.sentencefeatures[stftkey]
			else:
				treestring+="# "+stftkey+" = "+self.sentencefeatures[stftkey]+"\n"	
		for i in sorted(self):
			node = self[i]                        
			govs=node.get("gov",{})
			govk = sorted(govs)
			if govk:
				gk,gv = str(govk[0]),govs.get(govk[0],"_")
			else:
				gk,gv = "_","_"
			treestring+="\t".join([
				str(i), 
				node.get("t","_"), 
				node.get("lemma",""), 
				node.get("tag","_"), 
				node.get("xpos","_"), 
				"|".join( [ a+"="+v for a,v in sorted(node.items()) if a in morphoSynt]) or "_", 
				gk,
				gv,
				"|".join( [ str(g)+":"+govs.get(g,"_") for g in govk[1:] ] + [ str(a)+":"+v for a,v in node.get("egov",{}).items() ] ) or "_", 
				"|".join( [ a+"="+v for a,v in sorted(node.items()) if a not in morphoSynt+specialFeatures])  or "_" 
				])+ "\n"
				
		return treestring
	
	def addkids(self, exclude=[]):
		"""
		adds dictionary to each node: 'kids': {1: 'dobj', 2: 'aux', 3: 'nsubj', 5: 'prep', 9: 'punct'}
		adds self.rootnode
		"""
		for i in self:
			self[i]['kids'] = {}
		for i in self:
			for g,f in self[i].get("gov",{}).items():
				if f in exclude: continue
				if g>0: self[g]["kids"][i]=f
				else: self.rootnode=i
					
				
	def addspan(self, exclude=[]):
		"""
		adds the list of direct and indirect dependents to each node
		needs that kids have been added first
		"""
		self.addkids(exclude)
		for i in self:
			self[i]['span'] = sorted(self.span(i))
			
	def span(self, i):
		"""
		recursive function going down the tree
		"""
		sp = [i]
		for j in self[i]['kids']:
			sp += self.span(j)
		return sp
	
	def addflux(self):
		flux = {}
		for i in self:
			for g,f in self[i].get("gov",{}).items():
				#if f in exclude: continue
				if g>0: 
					#print(i,g)
					for ii in range(min(i,g),max(i,g)):
						#print(ii)
						flux[ii]=flux.get(ii,0)+1
					#self[g]["kids"][i]=f
		self.flux=[f for i,f in sorted(flux.items())]

	def addroof(self):
		roofs = {}
		for i in self:
			for g,f in self[i].get("gov",{}).items():
				#if f in exclude: continue
				if g>0:
					#print(i,g)
					for ii in range(min(i,g),max(i,g)):
						#print(ii)
						roofs[ii]=roofs.get(ii,[])+[(min(i,g),max(i,g))]
						#print(roofs[ii])
					#self[g]["kids"][i]=f
		self.roofs=[f for i,f in sorted(roofs.items())]
	# def addroof(self):
	# 	roofs = {}
	# 	for i in self:
	# 		for g,f in self[i].get("gov",{}).items():
	# 			#if f in exclude: continue
	# 			if g>0:
	# 				#print(i,g)
	# 				cpt,liste=0,[]
	# 				for ii in range(min(i,g),max(i,g)):
	# 					#print(ii)
	# 					roofs[ii]=roofs.get(ii,[])+[(min(i,g),max(i,g))]
	# 					print(roofs[ii])
	# 					cpt+=1
	# 				#self[g]["kids"][i]=f
	# 				liste.append(cpt)
	# 		ecart=min(liste)
	# 		print(ecart,i)
	# 	self.roofs=[f for i,f in sorted(roofs.items())]


	def correctNumbering(self):
		"""
		if numbering is not consistent, not 1,2,3, ... this function corrects this
		"""
		indexcorrection = {0:0} # old index --> new index
		problem = False
		for c, ind in enumerate(sorted(self.keys())):
			indexcorrection[ind]=c+1
			if c+1 != ind:
				problem = True
		if problem:
			correctTree = Tree()
			for i, node in list(self.items()):
				node["id"]=indexcorrection[i]
				newgov={}
				for gi,f in node["gov"].items():
					newgov[indexcorrection[gi]]=f
				node["gov"]=newgov
				correctTree[indexcorrection[i]]=node
				del self[i]
			for i, node in correctTree.items():
				self[i]=correctTree[i]
	
		
		
	def oldreplaceNodes(self, idsequence, instree, headid=0, hook=1):
		"""
		idsequence: ids to be replaced
		headid: headid has to be in idsequence, dangling links are attached here
		instree: treestructure to be inserted. can be dict, list or string
		"""
		if isinstance(instree, str):instree = {i+1:{'t':t} for (i,t) in enumerate(instree.split())}
		elif isinstance(instree, list):instree = {i+1:{'t':t} for (i,t) in enumerate(instree)}
		
		insinds = sorted(instree.keys())
		id2newid = {0:0}
		for ind in sorted(self.keys()):
			if ind<idsequence[0]: id2newid[ind]=ind # before insertion
			elif ind in idsequence: # the nodes to be replaced
				if instree.rooti:
					id2newid[ind]=idsequence[0]+instree.rooti-1
				else:
					if idsequence.index(ind) < len(instree): # align as long as possible
						id2newid[ind]=ind
					else: # spurious ones point to the headid
						id2newid[ind]=headid
			else: # behind insertion
				id2newid[ind]=ind+len(instree)-len(idsequence);	
		print(id2newid)
		
		newtree = {}
		for ind in sorted(self.keys()):
			# spurious nodes just get kicked out (more elements to be kicked out than to be inserted):
			if ind in idsequence and idsequence.index(ind) >= len(instree): continue
			node = self[ind]
			node['id']=id2newid[ind]
			for gg in ['gov','egov']:
				newgov={}
				for gi,gf in node[gg].items(): newgov[id2newid[gi]]=gf
				node[gg]=newgov
			if ind in idsequence: # now i got to insert the matching nodes
				insnode = instree[insinds[idsequence.index(ind)]]
				for gg in ['gov','egov']:
					nngov = {}
					for gi,gf in insnode.get(gg,{}).items(): # just in case the instree contains govs
						if gi in instree: # not touching root relations and no outgoing relations
							nngov[gi+idsequence[0]-1]=gf
					if nngov: insnode[gg]=nngov
					elif gg in insnode: del insnode[gg]
				if 'id' in insnode: del insnode['id']
				node = {**node, **insnode}
			newtree[id2newid[ind]]=node
		for i in insinds:
			insnode = instree[i]
			if instree.rooti:
				for gg in ['gov','egov']:
					nngov = {}
					
				
			elif i>len(idsequence): # [len(idsequence):]
				
				for gg in ['gov','egov']:
					nngov = {}
					for gi,gf in insnode.get(gg,{}).items(): # just in case the instree contains govs
						if gi in instree: # not touching root relations and no outgoing relations
							nngov[gi+idsequence[0]-1]=gf
					if nngov: insnode[gg]=nngov
					elif gg in insnode: del insnode[gg]
				newtree[i+idsequence[0]-1]=insnode
		sf = self.sentencefeatures
		self.__init__(newtree)
		sf['text'] = self.sentence()
		self.sentencefeatures = sf

	
	
	def replaceNodesByTree(self, idsequence, instree, hook=1, headid=0, keepExtpos=True):
		"""
		idsequence: ids to be replaced
		headid: headid has to be in idsequence, dangling links are attached here
		instree: treestructure to be inserted. can be dict, list or string
		"""
		if isinstance(instree, str):instree = {i+1:{'t':t} for (i,t) in enumerate(instree.split())}
		elif isinstance(instree, list):instree = {i+1:{'t':t} for (i,t) in enumerate(instree)}
		
		
		
		id2newid = {0:0}
		for ind in sorted(self.keys()):
			if ind<idsequence[0]: id2newid[ind]=ind # before insertion
			elif ind in idsequence: # the nodes to be replaced
				id2newid[ind] = hook # all nodes that have a governor in idsequence get hooked to hook
			else: # behind insertion
				id2newid[ind]=ind+len(instree)-len(idsequence);	
		print(id2newid)
		
		newtree = {}
		for ind in sorted(self.keys()):
			if ind in idsequence: continue
			node = self[ind]
			node['id']=id2newid[ind]
			for gg in ['gov','egov']:
				newgov={}
				for gi,gf in node[gg].items(): newgov[id2newid[gi]]=gf
				node[gg]=newgov
			if keepExtpos: node['extpos']=node['tag']
			newtree[id2newid[ind]]=node
			
		print('newtree',Tree(newtree))
		
		insgov = 0
		for i in idsequence:
			for gi,gf in self[i]['gov'].items():pass
			if gi not in idsequence: 
				insgov = gi
				break
		print('found insgov:',insgov)
		
		insid2newid = {oi:oi+idsequence[0]-1 for oi in idsequence}
		insid2newid[0]=insgov
		for i in instree:
			insnode = instree[i]
			for gg in ['gov','egov']:
				nngov = {}
				for gi,gf in insnode.get(gg,{}).items(): # just in case the instree contains govs
					if gi in instree: # not touching root relations and no outgoing relations
						nngov[gi+idsequence[0]-1]=gf
					else:
						nngov[insgov]=gf # hooking all outgoing relations to insgov
				insnode[gg]=nngov
				newtree[i+idsequence[0]-1]=insnode
		
		print('newtre2',len(Tree(newtree)),Tree(newtree))
		
		
		
		
		sf = self.sentencefeatures
		inssf = instree.get('sentencefeatures',{})
		self.__init__({})
		self.__init__(newtree)
		sf['text'] = Tree(newtree).sentence()
		self.sentencefeatures = {**sf, **inssf}
		
		print('newtre3',len(Tree(newtree)),Tree(newtree))
		print('self',len(self),self)
	

def update(d, u):
	for k, v in u.items():
		if isinstance(v, collections.Mapping):
			r = update(d.get(k, {}), v)
			d[k] = r
		else:
			d[k] = u[k]
	return d


def conll2tree(conllstring):
	""" 
	takes the conll string (or malt) representation of a single tree and creates a Tree (dictionary) for it
	"""
	tree=Tree()
	nr=1
	skipuntil=0 # only used to get the right "words" sequence, doesn't touch the actual tokens
	for line in conllstring.split('\n'):
		#print line
		if line.strip():
			if line.strip().endswith('# sent_id = D_ENU_13_School-life_1'):
				line=line[1:]
			if line.strip()[0]=="#": # comment of conllu
				if "=" in line:
					tree.sentencefeatures[line.split("=")[0].strip()[1:].strip()]="=".join(line.split("=")[1:]).strip()
				else:
					tree.sentencefeatures["_comments"]=tree.sentencefeatures.get("_comments","")+line.strip()[1:]+"\n#"
				continue
			
			cells = line.split('\t')
			nrCells = len(cells)
			
			if nrCells in [4,10,14]:
				
				if nrCells == 4: # malt!
					t, tag, govid, rel = cells
					if govid=="_": govid=-1
					else:govid = int(govid)
					newf={'id':nr,'t': t, 'tag': tag,'gov':{govid: rel}}
					tree[nr]=update(tree.get(nr,{}), newf)
					nr+=1

				elif nrCells == 10: # standard conll 10 or conllu
					nr, t, lemma , tag, xpos, features, govid, rel, edeps, misc = cells
					if "-" in nr: 
						try:	skipuntil=int(nr.split("-")[-1])
						except:	skipuntil=float(nr.split("-")[-1])
						tree.words+=[t]
						continue
					try:	nr = int(nr)
					except:	nr = float(nr) # handling the 3.1 format for "emtpy nodes"
					if govid.strip()=="_": govid=-1
					else:
						try:	govid = int(govid)
						except:	
							try:	govid = float(govid)
							except: 
								try:	assert(govid[0]=='$') # for transconll
								except: raise FormatError("not number or variable: "+govid)
					egov={}
					if ":" in edeps: # the enhanced graph is used
						egov=dict([(gf.split(":")[0],gf.split(":")[-1]) for gf in edeps.split("|")])					
					
					#newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'xpos': xpos, 'gov':{govid: rel}, 'egov':egov, 'misc': misc}
					newf={'id':nr,'t': t,'lemma': lemma, 'tag': tag, 'xpos': xpos, 'gov':{govid: rel}, 'egov':egov, 'misc': misc,'fff':features}
					if "=" in features:
						mf=dict([(av.split("=")[0],av.split("=")[-1]) for av in features.split("|")])
						newf=update(mf,newf)
					if "=" in misc:
						mf=dict([(av.split("=")[0],av.split("=")[-1]) for av in misc.split("|")])
						newf=update(mf,newf)
						del newf['misc']
					elif misc=="_":
						del newf['misc']
					tree[nr]=update(tree.get(nr,{}), newf)
					
					# to be removed:
					#if 'Glose' in tree[nr]: 
						#tree[nr]['Gloss']=tree[nr]['Glose']
						#del tree[nr]['Glose']
					#if 'startali' in tree[nr]: 
						#tree[nr]['AlignBegin']=tree[nr]['startali']
						#del tree[nr]['startali']
					#if 'endali' in tree[nr]: 
						#tree[nr]['AlignEnd']=tree[nr]['endali']
						#del tree[nr]['endali']
					# end to be removed
					
					if nr>skipuntil: tree.words+=[t]
					
				elif nrCells == 14:
					#mate:
					#6, inscriptions, _, inscription, _, N, _, pl|masc, -1, 4, _, dep, _, _
					nr, t, lemma, lemma2, tag, xpos, morph, morph2, govid, govid2, rel, rel2, _, _ = cells
					nr = int(nr)
					if govid.strip()=="_": govid=-1
					else:govid = int(govid)
					if govid2.strip()=="_": govid2=-1
					else:govid2 = int(govid2)
					if lemma=="_" and lemma2!="_":lemma=lemma2
					if tag=="_" and xpos!="_":tag=xpos
					if morph=="_" and morph2!="_":morph=morph2
					if rel=="_" and rel2!="_":
						rel=rel2
						govid=govid2
					newf={'id':nr,'t': t,'lemma': lemma,'lemma2': lemma2, 'tag': tag, 'xpos': xpos, 'morph': morph, 'morph2': morph2, 'gov':{govid: rel}, 'egov':{govid2: rel2} }
					
					
					
					tree[nr]=update(tree.get(nr,{}), newf)
					
					
			elif debug:
				print("strange conll:",nrCells,"columns!",line)
				print(ord(line[0]))
				print(line[0].encode('utf-8'))
				print(line[1])
	
	return tree


def conllFile2trees(path):
	"""
	file with path -> list of trees
	
	important function!	
	called from enterConll, treebankfiles, and uploadConll in treebankfiles.cgi
	
	"""
	trees=[]
	with open(path,"r",encoding="utf8") as f:
		conlltext=""
		for li in f:
			li=li.strip()
			if li: 	conlltext+=li+"\n"
			elif conlltext: # emptyline, sentence is finished
				tree=conll2tree(conlltext)
				trees+=[tree]
				del tree
				conlltext=""
		f.close()
		if conlltext.strip(): # last tree may not be followed by empty line
			tree=conll2tree(conlltext)
			trees+=[tree]
		return trees


def trees2conllFile(trees, outfile, columns="u"): # changed default from 10 to u!
	"""
	exports a list of treedics into outfile
	used after tree transformations...
	in conll14 format, the lemma position contains a duplicated t if lemma is not available
	"""
	treestrings=[]
	with open(outfile,"w") as f:
		for tree in trees:
			if columns=="u": # conllu format
				treestring = tree.conllu()
			else:
				
				treestring = ""
				for stftkey in sorted(tree.sentencefeatures):
					if stftkey=="_comments":
						treestring+=tree.sentencefeatures[stftkey]
					else:
						treestring+=stftkey+" = "+tree.sentencefeatures[stftkey]				
				for i in sorted(tree):					
					node = tree[i] 
					gov = list(node.get("gov",{}).items())
					govid = -1
					func = "_"
					if gov:
						for govid,func in gov:
							if columns==10:
								treestring+="\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("xpos","_"), "_", str(govid),func,"_","_"])+"\n"
							elif columns==14:
								lemma = node.get("lemma","_")
								if lemma == "_": lemma = node.get("t","_")
								treestring+="\t".join([str(i), node.get("t","_"), lemma, lemma or node.get("t","_"), node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n"
					else:
						if columns==10:
							treestring+="\t".join([str(i), node.get("t","_"), node.get("lemma",""), node.get("tag","_"), node.get("xpos","_"), "_", str(govid),func,"_","_"])+"\n"
							
						elif columns==14:
							lemma = node.get("lemma","_")
							if lemma == "_": lemma = node.get("t","_")
							treestring+="\t".join([str(i), node.get("t","_"), lemma, lemma, node.get("tag","_"), node.get("tag","_"), node.get("morph","_"), node.get("morph","_"), str(govid),str(govid),func,func,"_","_"])+"\n"
			treestrings+=[treestring]
		f.write("\n".join(treestrings))


def sentences2emptyConllFile(infile, outfile):
	"""
	transforms a list of sentences into conll format without trees
	"""
	inf=open(infile)
	outf=open(outfile,"w")
	counter=0
	for line in inf:
		line=line.strip()
		if line:
			for i,word in enumerate(line.split()):
				outf.write("\t".join([str(i+1),word,word,"_","_","_","-1","","_","_"])+"\n")
				## nr, t, lemma , tag, xpos, _, govid, rel, _, _ = cells
			outf.write("\n")
			counter+=1
	inf.close()
	outf.close()
	print(counter, "sentences")


def textFiles2emptyConllFiles(infolder, outfolder):
	import glob, os
	sentenceSplit=re.compile(r"(\s*\n+\s*|(?<!\s[A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜÃÑÕÆÅÐÇØ])[\?\!？\!\.。！……]+\s+|\s+\|\s+|[？。！……]+)(?!\d)", re.M+re.U)
	resentence=re.compile(r"[\?\!？\!\.。！……]+", re.M+re.U)
	retokenize=re.compile("(\W)",re.U+re.I)
	redoublespace=re.compile("(\s+)",re.U+re.I)
	renumber=re.compile("(\d) \. (\d)",re.U+re.I)
	rewhite=re.compile("\w",re.U+re.I)
	try:os.mkdir(outfolder)
	except:print("folder exists")
	for infile in glob.glob(os.path.join(infolder, '*.*')):
		print(infile)
		outfile=open(outfolder+"/"+infile.split("/")[-1],"w")
		for line in open(infile):
			line=line.strip()
			for s in sentenceSplit.split(line):
				s=s.strip()
				if resentence.match(s):
					outfile.write(str(count)+"\t"+s+"\n")
					outfile.write("\n")
				else:
					count=1
					s = retokenize.sub(r" \1 ",s)
					s = redoublespace.sub(r" ",s)
					s = renumber.sub(r"\1.\2",s)
					for token in s.split():
						if token.strip()=='\ufeff':continue # TODO: find out why this anti BOM shit is needed...
						outfile.write(str(count)+"\t"+token+"\n")
						count +=1

def tokenisation(torth):
	torth=re.sub("aujourd hui","aujourd'hui",torth)
	torth=re.sub("c est, c est à dire","c’est, c'est-à-dire",torth)
	torth=re.sub("c est à dire","c'est-à-dire",torth)
	torth=re.sub("peut être","peut-être",torth)
	torth=re.sub("ça peut-être","ça peut être",torth)	
	torth=re.sub(" t il"," t-il",torth)
	torth=re.sub("quelqu un","quelqu'un",torth)
	torth=re.sub("vis à vis","vis-à-vis",torth)
	torth=re.sub("dix sept","dix-sept",torth)
	torth=re.sub("dix huit","dix-huit",torth)
	torth=re.sub("dix neuf","dix-neuf",torth)
	torth=re.sub("vingt deux","vingt-deux",torth)
	torth=re.sub("vingt trois","vingt-trois",torth)
	torth=re.sub("vingt cinq","vingt-cinq",torth)
	torth=re.sub("vingt six","vingt-six",torth)
	torth=re.sub("vingt sept","vingt-sept",torth)
	torth=re.sub("vingt neuf","vingt-neuf",torth)
	torth=re.sub("trente et un","trente-et-un",torth)
	torth=re.sub("trente deux","trente-deux",torth)
	torth=re.sub("trente six","trente-six",torth)
	torth=re.sub("trente neuf","trente-neuf",torth)
	torth=re.sub("quarante trois","quarante-trois",torth)
	torth=re.sub("quarante cinq","quarante-cinq",torth)
	torth=re.sub("quarante huit","quarante-huit",torth)
	torth=re.sub("quarante neuf","quarante-neuf",torth)
	torth=re.sub("cinquante cinq","cinquante-cinq",torth)
	torth=re.sub("cinquante six","cinquante-six",torth)
	torth=re.sub("soixante quatre","soixante-quatre",torth)
	torth=re.sub("soixante cinq","soixante-cinq",torth)
	torth=re.sub("soixante dix","soixante-dix",torth)
	torth=re.sub("soixante quinze","soixante-quinze",torth)
	torth=re.sub("quatre vingt six","quatre-vingt-six",torth)
	torth=re.sub("quatre vingt sept","quatre-vingt-sept",torth)
	torth=re.sub("quatre vingt dix neuf","quatre-vingt-dix-neuf",torth)
	torth=re.sub("quatre vingt dix","quatre-vingt-dix",torth)
	torth=re.sub("quatre vingt onze","quatre-vingt-onze",torth)
	torth=re.sub("quatre vingt douze","quatre-vingt-douze",torth)
	torth=re.sub("quatre vingt","quatre-vingt",torth)
	torth=re.sub("cinq cents","cinq-cents",torth)
	torth=re.sub("dix septième","dix-septième",torth)
	torth=re.sub("dix huitième","dix-huitième",torth)
	torth=re.sub("dix neuvième","dix-neuvième",torth)
	torth=re.sub("vingt et unième","vingt-et-unième",torth)
	torth=re.sub("vingt deuxième","vingt-deuxième",torth)
	torth=re.sub("belle mère","belle-mère",torth)
	torth=re.sub("grands parents","grands-parents",torth)
	torth=re.sub("arrière grand mère","arrière-grand-mère",torth)
	torth=re.sub("baby sitter","baby-sitter",torth)
	torth=re.sub("pâtissier boulanger","pâtissier-boulanger",torth)
	torth=re.sub("rendez vous","rendez-vous",torth)
	torth=re.sub("rond point","rond-point",torth)
	torth=re.sub("week end","week-end",torth)
	torth=re.sub("après midi","après-midi",torth)
	torth=re.sub("moi même","moi-même",torth)
	torth=re.sub("soi même","soi-même",torth)
	torth=re.sub("lui même","lui-même",torth)
	torth=re.sub("elle même","elle-même",torth)
	torth=re.sub("vous même","vous-même",torth)
	torth=re.sub("là dessus","là-dessus",torth)
	torth=re.sub("là dedans","là-dedans",torth)
	torth=re.sub("là bas","là-bas",torth)	
	torth=re.sub("contre attaques","contre-attaques",torth)
	torth=re.sub("mi temps","mi-temps",torth)
	torth=re.sub("anti viraux","anti-viraux",torth)
	torth=re.sub("médico sociales","médico-sociales",torth)
	torth=re.sub("anti littérature","anti-littérature",torth)
	torth=re.sub("contre littérature","contre-littérature",torth)
	torth=re.sub("enseignants chercheurs","enseignants-chercheurs",torth)
	torth=re.sub("mathématicien écrivain","mathématicien-écrivain",torth)	
	torth=re.sub("micro processeurs","micro-processeurs",torth)
	torth=re.sub("États Unis","États-Unis",torth)
	torth=re.sub("Grande Bretagne","Grande-Bretagne",torth)
	torth=re.sub("Royaume Uni","Royaume-Uni",torth)
	torth=re.sub("Proche Orient","Proche-Orient",torth)
	torth=re.sub("Alsace Lorraine","Alsace-Lorraine",torth)
	torth=re.sub("Hauts de Seine","Hauts-de-Seine",torth)
	torth=re.sub("Pointe à Pitre","Pointe-à-Pitre",torth)
	torth=re.sub("outre mer","outre-mer",torth)
	torth=re.sub("centre ville","centre-ville",torth)
	torth=re.sub("Reuilly Diderot","Reuilly-Diderot",torth)
	torth=re.sub("Jean Paul","Jean-Paul",torth)
	torth=re.sub("Jean François","Jean-François",torth)
	torth=re.sub("Jean Baptiste","Jean-Baptiste",torth)
	torth=re.sub("Jean Christophe","Jean-Christophe",torth)
	torth=re.sub("Saint Jean de Maurienne","Saint-Jean-de-Maurienne",torth)
	torth=re.sub("Saint Jean","Saint-Jean",torth)
	torth=re.sub("Saint Germain","Saint-Germain",torth)
	torth=re.sub("Saint Sauveur","Saint-Sauveur",torth)
	torth=re.sub("Sainte Claire","Sainte-Claire",torth)
	torth=re.sub("Notre Dame","Notre-Dame",torth)
	return torth

import re

if __name__ == "__main__":
	pass
	#trees = conllFile2trees("sudcorrected/ONI_26_News-Highlights_MG.conllu")
	trees = conllFile2trees('version_vanessa_speaker_id.sud.txt')
	print(len(trees))
	#print(trees[2].conllu())
	#replaceNodesByTree(idsequence, instree, hook=1, headid=0, keepExtpos=True)
	#trees[0].replaceNodes([2,3], 2, {1:{'t':'oh'}})
	#trees[0].replaceNodes([2,3], 2, {1:{'t':'oh'},2:{'t':'là','gov':{1:'mylink'}},3:{'t':'làaa','gov':{2:'mylink'}}})
	#trees[0].replaceNodes([2,3], 2, ["oh", "là", "là"])
	#trees[2].replaceNodesByTree([2,3], {}, 2)
	#trees[0].replaceNodes([2,3], 2, "oh là là")
	# print(dict(trees[2]))
	# print(trees[2])
	# trees[2].addroof()
	# print(trees[2].roofs)
	# for i in trees[2].roofs:
	# 	print(i)
	# 	champion,tc=1000,()
	# 	for tuple in i:
	# 		ecart=tuple[1]-tuple[0]
	# 		if ecart<=champion:
	# 			champion=ecart
	# 			tc=tuple
	# 	dic_gov=dict(trees[2])[tc[0]]['gov']
	# 	for key in dic_gov.keys():
	# 		cle=key
	# 	if cle==tc[1]:
	# 		print(f'{tc[0]} est bien le dépendant de {tc[1]}')
	# 	else:
	# 		print(f'{tc[1]} est le dépendant de {tc[0]}')
	# 		cle=tc[1]

	"""La partie ci-dessous vise à ajouter la ponctuation dans le conll en adaptant les id de chaque
	tokens et en trouvant automatiquement les gouverneurs des poncutations ajoutées."""

	with open('version_vanessa_speaker_id.sud.txt','r',encoding="utf8") as fichier:
		fichier=fichier.readlines()
		sortie=open('fr_spoken.sud.train.conllu.txt','w',encoding="utf8")
		cpt=0
		for i in range(len(fichier)):
			ligne=fichier[i]
			if re.match(r'\d',ligne) and not re.match(r'\d',fichier[i-1]):
				if re.match("# text_ortho",fichier[i-3]):
					null,torth=fichier[i-3].split(' = ')
				elif re.match("# text_ortho",fichier[i-2]):
					null,torth=fichier[i-2].split(' = ')
				torth=re.sub("' ","'",torth)
				torth=re.sub("'"," ",torth)  # On veille à ce que l'apostrophe ne gêne pas la tokenisation.
				torth=re.sub(" ,",",",torth)
				torth=re.sub("-"," ",torth)  # On veille à ce que le tiret ne gêne pas la tokenisation.
				torth=re.sub("  "," ",torth)
				torth=tokenisation(torth)
				torth=torth.split(" ")
				print(torth)
				n,p,v,id,tokens,tokens2,l_prec,l_vir=0,0,0,1,"","",["x"],[]
				dic={}
				trees[cpt].addroof()
				# n permet de parcourir les lignes du bloc, p les tokens de la ligne txt, id de récupérer l'id d'un token
				while ligne!="\n":  # On se place dans le bloc formé par les tokens d'une IU.
					ligne=ligne.split("\t")
					if not re.match(r"\d+\-\d+",ligne[0]):  # On traite le cas où il y a deux tokens en un (2 lignes en +).
						if p<len(torth):
							token=torth[p]
						p+=1
						v+=1
					else:
						p-=1
					if "," in token and not re.match(r"\d+\-\d+",ligne[0]) and not re.match(r"\d+\-\d+",l_prec[0]):
						# On s'occupe de traiter la virugle en évitant le pb des formes composées.
						if p<len(torth):
							tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])+f"{id+1}\t,\t,\tPUNCT\t_\t_\tX\tpunct\t_\t_\n"
							dic[ligne[0]]=id
							id+=2
							l_vir.append(v-1)
					elif "." in token:    # On s'occupe de traiter le point.
						tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])#+f"{id+1}\t.\t.\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
						dic[ligne[0]]=id
					elif "…" in token:    # On s'occupe de traiter le point.
						tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])#+f"{id+1}\t…\t…\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
						dic[ligne[0]]=id
					elif "?" in token:    # On s'occupe de traiter le point.
						tokens+=f"{id}\t?\t?\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
					else:
						if re.match(r"\d+\-\d+",ligne[0]):  # On traite de nouveau le cas où il y a deux tokens en un.
							tokens+=f"{str(id)}-{str(id+1)}\t"+"\t".join(ligne[1:len(ligne)])
						else:
							tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])
							dic[ligne[0]]=id
							id+=1
					n+=1
					l_prec=ligne
					ligne=fichier[i+n]
				if ".\n" in token:
					tokens+=f"{id+1}\t.\t.\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
				elif "…" in token:
					tokens+=f"{id+1}\t…\t…\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
					id+=2
				if "?\n" in torth:
					tokens+=f"{id}\t?\t?\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
				tokens=tokens.split("\n")
				#print(l_vir)
				del tokens[len(tokens)-1]
				iv=0
				for ligne in range(len(tokens)):
					ligne=tokens[ligne].split("\t")
					if "root" in ligne[7]:    # On récupère l'id de la racine pour l'indiquer comme gouv du point.
						root=ligne[0]
						tokens2+="\t".join(ligne[0:10])+"\n"
					elif ligne[2]==",":   # Pas de traitement ici puisque nous devrons compléter manuellement.
						#print(trees[cpt].roofs)
						champion,tc=1000,()
						#print("indice liste virgule =",iv)
						if l_vir[iv]<len(trees[cpt].roofs):	#iv<len(l_vir):
							#print(l_vir[iv],"->",trees[cpt].roofs[l_vir[iv]])
							for tuple in trees[cpt].roofs[l_vir[iv]]:
								ecart=tuple[1]-tuple[0]
								if ecart<=champion:
									champion=ecart
									tc=tuple
									#print(tc)
						else:
							#print("else ->",l_vir[iv]-1,"->",trees[cpt].roofs[l_vir[iv]-1])
							for tuple in trees[cpt].roofs[l_vir[iv]-1]:
								ecart=tuple[1]-tuple[0]
								if ecart<=champion:
									champion=ecart
									tc=tuple
									#print(tc)
						dic_gov=dict(trees[cpt])[tc[0]]['gov']
						for key in dic_gov.keys():
							cle=key
							#print(f"gouv de {tc[0]} = {cle}")
						if cle==tc[1]:
							gov_vir=str(tc[0])
						else:
							gov_vir=str(tc[1])
						# print(gov_vir,dic[gov_vir])
						# print(str(dic[gov_vir]))
						tokens2+="\t".join(ligne[0:6])+"\t"+str(dic[gov_vir])+"\t"+"\t".join(ligne[7:10])+"\n"
						iv+=1
					elif ligne[2]=="." or ligne[2]=="?" or ligne[2]=="…": # Le gouverneur du point est toujours la racine.
						tokens2+="\t".join(ligne[0:6])+"\t"+root+"\t"+"\t".join(ligne[7:10])+"\n"
					elif re.match(r"\d+\-\d+",ligne[0]) or ligne[6]=="_":   # Ce type de lignes reste identique.
						tokens2+="\t".join(ligne[0:10])+"\n"
					else:
						tokens2+="\t".join(ligne[0:6])+"\t"+str(dic[ligne[6]])+"\t"+"\t".join(ligne[7:10])+"\n"
				sortie.write(f"{tokens2}\n")
				cpt+=1
			else:
				if not re.match(r'\d',fichier[i-1]):
					sortie.write(ligne)
		sortie.close()
	
	# Cette partie sert à corriger les lemmes erronés.
	with open('fr_spoken.sud.train.conllu.txt','r',encoding="utf8") as fichier:
		lignes=fichier.readlines()
		sortie=open('fr_spoken.sud.train.conllu_final.txt','w',encoding="utf8")
		for ligne in lignes:
			ligne=re.sub("aujourd'\t","aujourd'hui\t",ligne)
			ligne=re.sub("qu'\tqu'\t","qu'\tque\t",ligne)
			ligne=re.sub("d'\td'\t","d'\tde\t",ligne)
			ligne=re.sub("l'\tl'\t","l'\tle\t",ligne)
			ligne=re.sub("là-dessus\tlà\t","là-dessus\tlà-dessus\t",ligne)
			ligne=re.sub("là-dedans\tlà\t","là-dedans\tlà-dedans\t",ligne)
			ligne=re.sub("là-bas\tlà\t","là-bas\tlà-bas\t",ligne)
			ligne=re.sub("rendez-vous\trendez\t","rendez-vous\trendez-vous\t",ligne)
			ligne=re.sub("week-end\tweek\t","week-end\tweek-end\t",ligne)
			ligne=re.sub("rond-point\trond\t","rond-point\trond-point\t",ligne)
			ligne=re.sub("Saint-Jean-de-Maurienne\tSaint\t","Saint-Jean-de-Maurienne\tSaint-Jean-de-Maurienne\t",ligne)
			ligne=re.sub("grenadin\t","grenadine\t",ligne)
			sortie.write(ligne)
		sortie.close()

	# Cette partie sert à comparer deux fichiers (versions manuelle et automatique).
	# with open('fr_spoken.sud.test.conllu_v5.txt','r',encoding="utf8") as manuel:
	# 	with open('fr_spoken.sud.test.conllu_prg_final.txt','r',encoding="utf8") as auto:
	# 		manuel,auto=manuel.readlines(),auto.readlines()
	# 		sortie=open('comparaison_test.txt','w',encoding="utf8")
	# 		for ligne in range(len(manuel)):
	# 			if re.match(r'# sent_id',manuel[ligne]):
	# 				bwah,sent_id=manuel[ligne].split(' = ')
	# 			if ligne<len(auto):
	# 				if manuel[ligne]!=auto[ligne]:
	# 					sortie.write(f"Ligne {ligne} / sent_id : {sent_id}Manuel :\t{manuel[ligne]}Auto :\t\t{auto[ligne]}\n\n")
	# 			else:
	# 				sortie.write(f"Ligne {ligne} / sent_id : {sent_id}Manuel :\t{manuel[ligne]}Auto :\t\tFINITO\n\n\n")
			
	# 		# print(dict(trees[2])[tuple[0]])
	# 		print(dict(trees[2])[tuple[0]])
			#else:

	#print(trees[0].sentencefeatures)
	#trees[0].correctNumbering()
	#print(trees[0].conllu())
	#open("test.conllu","w").write(trees[0].conllu())
	
