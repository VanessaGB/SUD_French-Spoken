import re

# with open('fr_spoken.sud.dev.conllu.txt','r',encoding="utf8") as fichier:
#     sortie=open('fr_spoken.sud.dev.conllu_v2.txt','w',encoding="utf8")
#     speaker="L1"
#     for ligne in fichier:
#         sortie.write(ligne)
#         if re.match('# macrosyntax =',ligne):
#             l1,l2=ligne.split(" = ")
#             l2=re.sub(r"\-\$|\$\-|\(.*\)","",l2)
#             #sortie.write(l2)
#             if re.match('\$L',l2):
#                 speaker=l2[1:3]
#             sortie.write(f"# speaker = {speaker}\n")
# Traiter les lignes où il y a déjà un speaker - passer par les indices ?

with open('fr_spoken.sud.dev.conllu.txt','r',encoding="utf8") as fichier:
    fichier=fichier.readlines()
    sortie=open('fr_spoken.sud.dev.conllu_v2.txt','w',encoding="utf8")
    speaker="L1"
    for ligne in range(len(fichier)):
        sortie.write(fichier[ligne])
        if re.match('# macrosyntax =',fichier[ligne]):
            l1,l2=fichier[ligne].split(" = ")
            #print(l2)
            l2=re.sub(r"\-\$ |\$\- |\(.*\)","",l2)
            #sortie.write(l2)
            if not re.match('# speaker',fichier[ligne+1]):
                if re.match('\$L',l2):
                    speaker=l2[1:3]
                sortie.write(f"# speaker = {speaker}\n")
            # else:
            #     sortie.write("déjà là - ")

'''
On observe que certaines fois le changement de locuteur ne semble pas indiqué et il est donc
difficile de le repérer automatiquement, le // pouvant symboliser aussi bien le passage à
une autre phrase que celui à un autre locuteur visiblement.
La solution semblerait être de se servir de ce script pour une première annotation et
d'ensuite se référer aux enregistrements pour éventuellement corriger cette dernière.
'''