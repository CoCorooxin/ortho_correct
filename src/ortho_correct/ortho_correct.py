import sys
from unicodedata import category
import requests
import re
import spacy
from spacy import displacy

class OrthoCorrect(object):
    def __init__(self):
        self.vocabtree = requests.get(
            "https://github.com/mducos/Correction-automatique/raw/main/production/structure_arborescente.json").json()
        self.vocabtree = requests.get(
            "https://github.com/mducos/Correction-automatique/raw/main/production/structure_arborescente.json").json()
        self.wordsWithApostrophe = requests.get(
            "https://raw.githubusercontent.com/mducos/Correcteur-orthographique/main/production/words_with_apostrophe.json").json()
        self.wordsWithSpace = requests.get(
            "https://raw.githubusercontent.com/mducos/Correcteur-orthographique/main/production/two_words_in_one.json").json()
        self.wordsWithDash = requests.get(
            "https://raw.githubusercontent.com/mducos/Correcteur-orthographique/main/production/words_with_dash.json").json()
        self.chrs = (chr(i) for i in range(sys.maxunicode + 1))
        self.punctuation = set(c for c in self.chrs if category(c).startswith("P"))
        self.nlp = spacy.load("fr_core_news_sm")

    def _edits1(self, word):
        # ensemble des lettres de la langue française
        letters = 'abcdefghijklmnopqrstuvwxyzàâæçéèêëîïôœùûüÿ-'
        # découpage du mot pour y insérer les opérations
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        # suppression
        deletes = [L + R[1:] for L, R in splits if R]
        # transposition
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        # substitution
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        # insertion
        inserts = [L + c + R for L, R in splits for c in letters]

        return set(deletes + transposes + replaces + inserts)

    def _edits2(self, word):
        # retourne l'ensemble de tous les mots générés avec une distance de 1 avec les mots générés avec une distance de 1
        return set(e2 for e1 in self._edits1(word) for e2 in self._edits1(e1))

    def _probabilite(self, word):

        return self._frequence_relative(self.vocabtree, word)

    def _known(self, candidats):

        # retourne l'ensemble des mots qui existe dans l'arbre lexicographique
        return set(w for w in candidats if self._rechercheWordRec(self.vocabtree, w))

    def _frequence_relative(self, tree, word):

        # cas de base : on lit la dernière lettre du mot
        if len(word) == 1:
            # la suite de lettres est dans l'arbre alors pour toutes les clés dans l'arbre
            for key in tree[word]:
                # vérifier s'il est possible de convertir en float ce qui signifierait que la lettre est finale et donc le mot existe
                try:
                    float(key)
                    return float(key)
                except:
                    pass
            return 0.0
        # si la première lettre est dans les clés du dictionnaire, on poursuit la recherche
        return self._frequence_relative(tree[word[0]], word[1:])

    def _rechercheWordRec(self, tree, word):

        # cas de base : on lit la dernière lettre du mot
        if len(word) == 1:
            # la suite de lettres est dans l'arbre mais la dernière lettre n'y est pas donc ce n'est pas un mot du dictionnaire
            if not (word in tree):
                return False
            # la suite de lettres est dans l'arbre alors pour toutes les clés dans l'arbre
            for key in tree[word]:
                # vérifier s'il est possible de convertir en float ce qui signifierait que la lettre est finale et donc le mot existe
                try:
                    float(key)
                    return float(key)
                except:
                    pass
            # la suite de lettres est dans l'arbre mais la dernière lettre n'est pas finale donc ce n'est pas un mot du dictionnaire
            return False
        # si les opérations ont généré le mot vide
        elif len(word) == 0:
            return False
        # si la première lettre est dans les clés du dictionnaire, on poursuit la recherche
        elif word[0] in tree:
            return self._rechercheWordRec(tree[word[0]], word[1:])
        # si elle n'y est pas, on peut dès à présent retourner faux
        else:
            return False

    def corrigeMotAuto(self, word):

        # ensemble des mots dans le dictionnaire à partir des mots distants de 0 du mot de base
        word_distance0 = self._known([word])
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(word_distance0) > 0:
            # retourne le mot qui a la probabilité maximum
            return max(word_distance0, key=self._probabilite)

        # ensemble des mots dans le dictionnaire à partir des mots distants de 1 du mot de base
        word_distance1 = self._edits1(word)
        """print(f'word_distance1 {word_distance1}')"""
        known_word_distance1 = self._known(self._edits1(word))
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(known_word_distance1) > 0:
            """print(f'known_word_distance1 {known_word_distance1}')"""
            # retourne le mot qui a la probabilité maximum
            return max(known_word_distance1, key=self._probabilite)

        # ensemble des mots dans le dictionnaire à partir des mots distants de 2 du mot de base
        word_distance2 = set(e2 for e1 in word_distance1 for e2 in self._edits1(e1))
        known_word_distance2 = self._known(word_distance2)
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(known_word_distance2) > 0:
            """print(print(f'known_word_distance2 {known_word_distance2}'))"""
            # retourne le mot qui a la probabilité maximum
            return max(known_word_distance2, key=self._probabilite)

        # si aucun mot d'une distance de 2 ou moins n'a été trouvé,
        return "not found"

    def corrigeMotInter(self, word)->list:

        # ensemble des mots dans le dictionnaire à partir des mots distants de 0 du mot de base
        word_distance0 = self._known([word])
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(word_distance0) > 0:
            # retourne le mot qui a la probabilité maximum
            return max(word_distance0, key=self._probabilite)

        # ensemble des mots dans le dictionnaire à partir des mots distants de 1 du mot de base
        word_distance1 = self._edits1(word)
        known_word_distance1 = self._known(self._edits1(word))
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(known_word_distance1) > 0:
            # retourne le mot qui a la probabilité maximum
            list_max = []
            k = 1
            while known_word_distance1 != set() and k < 6:
                list_max.append(max(known_word_distance1, key=self._probabilite))
                known_word_distance1.remove(max(known_word_distance1, key=self._probabilite))
                k += 1
            return list_max

        # ensemble des mots dans le dictionnaire à partir des mots distants de 2 du mot de base
        word_distance2 = set(e2 for e1 in word_distance1 for e2 in self._edits1(e1))
        known_word_distance2 = self._known(word_distance2)
        # si au moins un mot parmi cet ensemble est dans le dictionnaire
        if len(known_word_distance2) > 0:
            # retourne le mot qui a la probabilité maximum
            list_max = []
            k = 1
            while known_word_distance2 != set() and k < 6:
                list_max.append(max(known_word_distance2, key=self._probabilite))
                known_word_distance2.remove(max(known_word_distance2, key=self._probabilite))
                k += 1
            return list_max

        # si aucun mot d'une distance de 2 ou moins n'a été trouvé,
        return "not found"

    def _addSpaceRegex(self, str):
        str = re.sub('([^\w\s-])', r' \1 ', str)
        str = re.sub('\s{2,}', ' ', str)
        return str

    def tokenizer(self, todo)->list: #retourne une liste de tokens
        # pour chaque mot de l'ensemble des mots avec une apostrophe de plus de 2 caractères (pour enlever les "l'" et "d'"), on vérifie s'il est dans le corpus
        for word in self.wordsWithApostrophe:
            if word in todo.lower() and len(word) > 2:
                # s'il y est, on change l'apostrophe en un signe présent dans aucun mot pour pouvoir le reconnaître plus tard
                todo = todo.replace(word, word.replace("'", "$"))
                # mais si le mot a une majuscule au début, il faut le traiter ainsi
                word = word[0].upper() + word[1:]
                todo = todo.replace(word, word.replace("'", "$"))

        # ajout des espaces autour des signes de ponctuation
        todo = self._addSpaceRegex(todo)

        # pour chaque mot de l'ensemble des mots à 2 composés, on vérifie s'il est dans le corpus
        for word in self.wordsWithSpace:
            # on doit faire comme si les apostrophes étaient sous forme d'apostrophe
            if word in todo.replace("$", "'").lower():
                # s'il y est, on change l'espace en un signe présent dans aucun mot pour pouvoir le reconnaître plus tard
                todo = todo.replace(word.replace("'", "$"), word.replace("'", "$").replace(" ", "*"))
                # mais si le mot a une majuscule au début, il faut le traiter ainsi
                word = word[0].upper() + word[1:]
                todo = todo.replace(word.replace("'", "$"), word.replace("'", "$").replace(" ", "*"))

        # en splitant, les composants d'un mot qui contient originellement un espace ne sont plus séparés
        tokens = todo.split()
        # pour chaque mot du corpus
        for i in range(len(tokens)):
            # s'il contient * signifie que c'est un mot à plusieurs composants
            if "$" in tokens[i]:
                # on remet l'espace
                tokens[i] = tokens[i].replace("$", "'")
            # s'il contient * signifie que c'est un mot à plusieurs composants
            if "*" in tokens[i]:
                # on remet l'espace
                tokens[i] = tokens[i].replace("*", " ")

        # pour chaque mot du corpus
        for i in range(len(tokens)):
            # s'il contient un tiret
            if "-" in tokens[i]:
                # on vérifie qu'il ne fait pas partie de l'ensemble des mots à tiret
                if not (tokens[i].lower() in self.wordsWithDash):
                    # on ajoute les espaces nécessaires autour de la ponctuation
                    tokens[i] = tokens[i].replace("-", " - ")
                    # on transforme l'expression en liste
                    listWord = tokens[i].split()
                    # on supprime le faux mot avec tiret dans le corpus
                    del tokens[i]
                    # et on ajoute à l'indice i tous les mots de la liste
                    for component in reversed(listWord):
                        tokens.insert(i, component)

        return tokens

    def _person(self, text)->list: #reconnaissance des entités nominales
        doc = self.nlp(text)
        return " ".join([ent.text for ent in doc.ents]).split()

    def _rechercheWordDict(self, word):
        # si le mot n'est pas un signe de ponctuation
        if not (word in self.punctuation):
            # on parcourt chaque lettre du mot pour vérifier qu'elles sont des noeuds/feuilles dans l'arbre
            return self._rechercheWordRec(self.vocabtree, word.lower())

    def correctionAutomatique(self, todo)->str:

        list_lemme = (self.tokenizer(todo))
        res = []
        count = 0
        to_write = ''
        # pour chaque élément dans cette liste tokenisée
        nertuple = tuple(self._person(todo))
        #print(nertuple)
        for id in range(len(list_lemme)):
            # si le mot n'existe pas
            nerVal = list_lemme[id].startswith(nertuple)
            if self._rechercheWordDict(list_lemme[id]) is False and nerVal is False:
                # enregistrement de la forme juste la plus probable du mot fautif
                corrected = self.corrigeMotAuto(list_lemme[id].lower())
                # si la forme juste la plus probable n'a pas été trouvée
                if corrected == "not found":
                    # on réécrit le mot tel quel dans le fichier
                    count+=1
                    to_write += f"({corrected}) "+'\u0332'.join(list_lemme[id]) + " "
                    res.append(f"no.{count} forme fautive détectée : {list_lemme[id]}; corrigé: {corrected}")
                    #res.append(corrected)
                # si une forme juste la plus probable a été trouvée
                else:
                    # pour chaque lettre dans le mot
                    for letter_id in range(len(min(corrected, list_lemme[id], key=len))):
                        # si une majuscule était présente dans la phrase d'origine
                        if list_lemme[id][letter_id] == list_lemme[id][letter_id].upper():
                            # on modifie le mot juste en y ajoutant la majuscule sur la bonne lettre
                            corrected = corrected.replace(corrected[letter_id],
                                                          corrected[letter_id].upper())
                    # on écrit le mot corrigé dans le fichier
                    count += 1
                    to_write += '\u0332'.join(corrected)  + " "
                    res.append(f"no.{count} forme fautive détectée : {list_lemme[id]} \ncorrigé: {corrected} \n ")
                    #res.append(corrected)
            # si le mot existe
            else:
                # on le réécrit dans le fichier
                to_write += list_lemme[id] + " "
                    # tokenisation de la ligne en enlevant #
        to_write = re.sub(r'\s+([?.!,"])', r'\1', to_write).replace(" ' ", "'")
        '''print(to_write)'''
        """for item in res:
            print(item)"""
        return to_write, res

    def correcteurInteractif(self, todo)->str:

        list_lemme = (self.tokenizer(todo))
        to_write = ''
        # pour chaque élément dans cette liste tokenisée
        nertuple = tuple(self._person(todo))
        # print(nertuple)
        for id in range(len(list_lemme)):
            # si le mot n'existe pas
            nerVal = list_lemme[id].startswith(nertuple)
            if self._rechercheWordDict(list_lemme[id]) is False and nerVal is False:
                # enregistrement de la forme juste la plus probable du mot fautif
                corrected = self.corrigeMotInter(list_lemme[id].lower())
                # si la forme juste la plus probable n'a pas été trouvée
                print(f"forme fautive détectée: {list_lemme[id]}")
                if corrected == "not found":
                    print(f"formes correctes: {corrected}")
                    to_write = to_write + list_lemme[id] + ' '
                else:
                    proposition = '"' + '", "'.join([w for w in corrected])
                    best_word = ""
                    while best_word == "":
                        # question posée pour déterminer si la correction sera automatique ou intéractive
                        answer = input(
                            "dans le contexte : " + list_lemme[id - 1] + " " +
                            list_lemme[id] + " " + list_lemme[id + 1] + "\nVeuillez choisir une correction possible : " + proposition + '", "not found"' + "\n")
                        # si la réponse correspond à un des mots proposés, on stocke le mot choisi
                        if answer in proposition.split('"'):
                            best_word = answer
                            answer = "_"
                        elif answer == "not found":
                            best_word = list_lemme[id]
                    to_write = to_write + best_word + ' '
            else:
                to_write = to_write + list_lemme[id] + ' '
        to_write = re.sub(r'\s+([?.!,"])', r'\1', to_write).replace(" ' ", "'")
        print(to_write)
        return to_write


"""test = Correcteur()
with open("corpus_fautes.txt", "r", encoding = 'utf-8') as f:
    str = f.read()
with open("corpus_corrigee.txt", "r", encoding = 'utf-8') as f:
    corrigee = f.read()

print(str[:100])
correct = test.correcteurInteractif(str[:100])"""
