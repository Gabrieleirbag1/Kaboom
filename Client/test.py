liste = ["mot", "moot", 'mooot']
liste2 = []

for mot in liste:
    print(mot)
    print(len(mot))
    if len(mot) < 5 or len(mot) > 5:
        liste2.append(mot)

for mot in liste2:
    liste.remove(mot)


print(liste)