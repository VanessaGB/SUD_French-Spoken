import re

"""
Ce script permet de récupérer les id des différents locuteurs dans les fichiers Rhapsodie et de les intégrer dans une copie du fichier de départ.
Il fonctionne sur la présence des indicateurs de type $L1 en début de ligne.
On observe cependant que certaines fois le changement de locuteur ne semble pas indiqué et il est donc difficile de le repérer automatiquement,
le // pouvant symboliser aussi bien le passage à une autre phrase que celui à un autre locuteur visiblement.
La solution semblerait être de se servir de ce script pour une première annotation et d'ensuite se référer aux enregistrements pour éventuellement la corriger.
"""

# Cette version sert lorsque l'on utilise ce script dans la toute première phase de traitement.
# with open('fr_spoken.sud.test.conllu.txt','r',encoding="utf8") as fichier:
#     fichier=fichier.readlines()
#     sortie=open('fr_spoken.sud.test.conllu_v2.txt','w',encoding="utf8")
#     speaker="L1"
#     for ligne in range(len(fichier)):
#         sortie.write(fichier[ligne])
#         if re.match('# macrosyntax =',fichier[ligne]):
#             l1,l2=fichier[ligne].split(" = ")
#             l2=re.sub(r"\-\$ |\$\- |\(.*\)","",l2)
#             if not re.match('# speaker',fichier[ligne+1]):
#                 if re.match('\$L',l2):
#                     speaker=l2[1:3]
#                 sortie.write(f"# speaker = {speaker}\n")
#             else:
#                 l1,l2=fichier[ligne+1].split(" = ")
#                 speaker=l2[0:len(l2)-1]
#             liste_l=re.findall('\$L\d',l2)
#             if len(liste_l)>1:
#                 speaker=liste_l[len(liste_l)-1]

# Cette version sert dans le cas où on travaille sur un fichier ayant déjà des lignes text_ortho.
with open('full_test_corrige_manuellement_macro2text_fr_spoken.sud.test.conllu.txt','r',encoding="utf8") as fichier:
    fichier=fichier.readlines()
    sortie=open('fr_spoken.sud.test.conllu_test.txt','w',encoding="utf8")
    speaker="L1"
    yes=0
    for ligne in range(len(fichier)):
        if yes==0:
            sortie.write(fichier[ligne])
        yes=0
        if re.match('# macrosyntax =',fichier[ligne]):
            l1,l2=fichier[ligne].split(" = ")
            l2=re.sub(r"\-\$ |\$\- |\(.*\)","",l2)
            if not re.match('# speaker',fichier[ligne+2]):
                if re.match('\$L',l2):
                    speaker=l2[1:3]
                sortie.write(fichier[ligne+1])
                sortie.write(f"# speaker = {speaker}\n")
                yes=1
                #ligne+=1
            else:
                l1,l2=fichier[ligne+2].split(" = ")
                speaker=l2[0:len(l2)-1]
            liste_l=re.findall('\$L\d',l2)
            if len(liste_l)>1:
                speaker=liste_l[len(liste_l)-1]
                
# Ci-dessous, une autre version tenant compte des lignes où le locuteur est déjà donné pour récupérer son id.
# with open('fr_spoken.sud.test.conllu.txt','r',encoding="utf8") as fichier:
#     fichier=fichier.readlines()
#     sortie=open('fr_spoken.sud.test.conllu_v2.txt','w',encoding="utf8")
#     speaker="L1"
#     for ligne in range(len(fichier)):
#         sortie.write(fichier[ligne])
#         if re.match('# macrosyntax =',fichier[ligne]):
#             l1,l2=fichier[ligne].split(" = ")
#             l2=re.sub(r"\-\$ |\$\- |\(.*\)","",l2)
#             if not re.match('# speaker',fichier[ligne+1]):
#                 if re.match('\$L',l2):
#                     speaker=l2[1:3]
#                 sortie.write(f"# speaker = {speaker}\n")
#             else:
#                 l1,l2=fichier[ligne+1].split(" = ")
#                 speaker=l2[0:len(l2)-1]
