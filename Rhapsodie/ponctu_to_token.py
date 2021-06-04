"""
Ce script permet de rajouter la ponctuation dans la partie conll de chaque IU.
Il vise à mettre à jour les id des tokens ainsi que ceux de leurs gouverneurs.
Les gouverneurs des virgules seront à rajouter manuellement.
"""

import re

with open('fr_spoken.sud.test.conllu_v3.txt','r',encoding="utf8") as fichier:
    fichier=fichier.readlines()
    sortie=open('fr_spoken.sud.test.conllu_v4.txt','w',encoding="utf8")
    for i in range(len(fichier)):
        ligne=fichier[i]
        if re.match(r'\d',ligne) and not re.match(r'\d',fichier[i-1]):
            null,torth=fichier[i-4].split(' = ')
            torth=re.sub("'"," ",torth)  # On veille à ce que l'apostrophe ne gêne pas la tokenisation.
            torth=torth.split(" ")
            n,p,id,tokens,tokens2=0,0,1,"",""
            # n permet de parcourir les lignes du bloc, p les tokens de la ligne txt, id de récupérer l'id d'un token
            while ligne!="\n":  # On se place dans le bloc formé par les tokens d'une IU.
                ligne=ligne.split("\t")
                if not re.match(r"\d+\-\d+",ligne[0]):  # On traite le cas où il y a deux tokens en un (2 lignes en +).
                    if p<len(torth):
                        token=torth[p]
                    p+=1
                else:
                    p-=2
                if "," in token:    # On s'occupe de traiter la virugle.
                    if p<len(torth):
                        tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])+f"{id+1}\t,\t,\tPUNCT\t_\t_\tX\tpunct\t_\t_\n"
                        id+=2
                # elif "." in token:    # On s'occupe de traiter le point.
                #     tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])+f"{id+1}\t.\t.\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
                else:
                    if re.match(r"\d+\-\d+",ligne[0]):  # On traite de nouveau le cas où il y a deux tokens en un.
                        tokens+=f"{str(id)}-{str(id+1)}\t"+"\t".join(ligne[1:len(ligne)])
                    else:
                        tokens+=str(id)+"\t"+"\t".join(ligne[1:len(ligne)])
                        id+=1
                n+=1
                ligne=fichier[i+n]
            tokens+=f"{id}\t.\t.\tPUNCT\t_\t_\tROOT\tpunct\t_\t_\n"
            tokens=tokens.split("\n")
            del tokens[len(tokens)-1]
            id,liste_vir=0,[]
            for token in tokens:    # On récupère la liste des id des virgules.
                token=token.split("\t")
                if token[1]==",":
                    liste_vir.append(token[0])
                    print(liste_vir)
            for ligne in range(len(tokens)):
                ligne=tokens[ligne].split("\t")
                if "root" in ligne[7]:    # On récupère l'id de la racine pour l'indiquer comme gouv du point.
                    root=ligne[0]
                if ligne[2]==",":   # Pas de traitement ici puisque nous devrons compléter manuellement.
                    tokens2+="\t".join(ligne[0:10])+"\n"
                    id+=1
                elif ligne[2]==".": # Le gouverneur du point est toujours la racine.
                    tokens2+="\t".join(ligne[0:6])+"\t"+root+"\t"+"\t".join(ligne[7:10])+"\n"
                elif re.match(r"\d+\-\d+",ligne[0]) or ligne[6]=="_":   # Ce type de lignes reste identique.
                    tokens2+="\t".join(ligne[0:10])+"\n"
                else:
                    vir=0   # On va tester s'il y a une virgule avant le token du gouv, sinon pas de modif.
                    for i in range(len(liste_vir)):
                        if int(ligne[6])>int(liste_vir[i]):
                            if i+1<len(liste_vir):
                                if int(ligne[6])<int(liste_vir[i+1]):
                                    tokens2+="\t".join(ligne[0:6])+"\t"+str(int(ligne[6])+(i+1))+"\t"+"\t".join(ligne[7:10])+"\n"
                                    vir=1
                            else:
                                tokens2+="\t".join(ligne[0:6])+"\t"+str(int(ligne[6])+(i+1))+"\t"+"\t".join(ligne[7:10])+"\n"
                                vir=1
                    if vir==0:
                        tokens2+="\t".join(ligne[0:6])+"\t"+str(int(ligne[6]))+"\t"+"\t".join(ligne[7:10])+"\n"
            sortie.write(f"{tokens2}\n")
        else:
            if not re.match(r'\d',fichier[i-1]):
                sortie.write(ligne)
