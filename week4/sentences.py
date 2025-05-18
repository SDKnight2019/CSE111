import random

def main():
    print(make_sentence(1, "past"))
    print(make_sentence(1, "present"))
    print(make_sentence(1, "future"))
    print(make_sentence(2, "past"))
    print(make_sentence(2,"present"))
    print(make_sentence(2, "future"))

def get_determiner(quantity):
    if quantity == 1:
        return random.choice(["a","one","the"])
    else:
        return random.choice(["some","many","the"])
    
#print(get_determiner(1))  # should return "a", "one", or "the"
#print(get_determiner(2))  # should return "some", "many", or "the"

def get_noun(quantity):
    if quantity == 1:
        return random.choice(["cat","dog","pickle","lion","goat","bear","pig","cow","student","teacher"])
    else:
        return random.choice(["cats","dogs","pickles","lions","bears","pigs","students","teachers","goats","cows"])
    
#print(get_noun(1))  # singular
#print(get_noun(2))  # plural

def get_verb(quantity, tense):
    if tense == "past":
        return random.choice(["walked","talked","ran","ate","slept","wrote","laughed","thought","drank","grew"])
    elif tense == "present":
        if quantity == 1:
            return random.choice(["walks","talks","laughs","eats","sleeps","thinks","writes","drinks","grows","runs"])
        else:
            return random.choice(["walk","talk","laugh","eat","sleep","think","write","drink","grow","run"])
    elif tense == "future":
        return random.choice(["will walk","will talk","will laugh","will eat","will sleep","will think","will write","will drink","will grow","will run"])

#print(get_verb(1, "past"))
#print(get_verb(1, "present"))
#print(get_verb(1, "future"))
#print(get_verb(2, "past"))
#print(get_verb(2, "present"))
#print(get_verb(2, "future"))

def get_preposition():
    return random.choice(["about", "above", "across", "after", "along", "around", "at", "before", "behind", "below", "beyond", "by", "despite", "except", "for", "from", "in", "into", "near", "of", "off", "on", "onto", "out", "over", "past", "to", "under", "with", "without"])

#print(get_preposition())

def get_prepositional_phrase(quantity):
    prep = get_preposition()
    det = get_determiner(quantity)
    noun = get_noun(quantity)
    phrase = f"{prep} {det} {noun}"
    return phrase

#print(get_prepositional_phrase(1))  # singular
#print(get_prepositional_phrase(2))  # plural

def make_sentence(quantity, tense):
    determiner = get_determiner(quantity)
    noun = get_noun(quantity)
    verb = get_verb(quantity, tense)
    prepositional_phrase_1 = get_prepositional_phrase(quantity)
    prepositional_phrase_2 = get_prepositional_phrase(quantity)
    adjective = get_adjective()
    adverb = get_adverb()
    sentence = f"{determiner} {adjective} {noun} {adverb} {verb} {prepositional_phrase_1} {prepositional_phrase_2}"
    sentence = sentence.capitalize()
    return sentence

#strech goals... I am adding this to exceed the requirments of the class.

def get_adjective():
    return random.choice(["fuzzy", "happy", "sleepy", "grumpy", "giant", "tiny", "brave", "playful", "noisy", "quiet"])

def get_adverb():
    return random.choice(["quickly", "loudly", "quietly", "angrily", "gracefully"])

main()