import unidecode

dictionnaire = ["bonjôur", "salut", "coucou", "hello", "hi", "hola", "ciao", "hallo", "bonsoir", "bonne nuit", "bonne soiree", "bonne journee", "bonne matinee"]

def convert_word(word):
    """convert_word() : Permet d'ignorer les caractères spéciaux et les accents du dictionnaire

    Args:
        word (str): Mot à convertir

    Returns:
        str: Mot converti"""
    word = unidecode.unidecode(word)  # Convertir les caractères spéciaux en caractères ASCII
    return word

word = "bonjôur"
if any(convert_word(word.lower()) == convert_word(mot.lower()) for mot in dictionnaire):
    print("ok")
else:
    print("pas ok")


