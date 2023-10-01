# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        '''
        Initializes a trie instance with key type (string or tuple), value (None) and a dictionary that maps 
        a single element sequence (length 1 string or length 1 tuple) to another trie instance
        Parameters
        ----------
        key_type : str or tuple

        Returns
        -------
        None.

        '''
        self.value = None
        self.key_type = key_type
        self.children = {}

    def keyType(self, key):
        """
        Check if key is of the correct type corresponding to the Trie. Raises Type Error if key is not of
        correct type. Raise Value Error if key is empty
        """
        if not isinstance(key, self.key_type):
            raise TypeError(f"Key is not of type {self.key_type}")
    
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        self.keyType(key) # check if correct type
        # base cases
        if len(key) == 1:
            # get trie corresponding to key or create new key value pair with new trie instance
            x = self.children.setdefault(key, Trie(self.key_type))
            x.value = value # set value of Trie corresponding to that key
        # recursive case
        else:
            # get Trie corresponding to first key value or create new Trie instance and bind to first key value
            x = self.children.setdefault(key[:1], Trie(self.key_type))
            x[key[1:]] = value # recursively call __setitem__ on rest of key values
            

    def get_trie(self, key):
        """
        Get Trie corresponding to a particular key. Return an empty list if key doesn't exist
        """
        self.keyType(key) # check if correct type
        # base cases
        if len(key) == 1:
            x = self.children.get(key) # get Trie instance corresponding to key, or None if key not in Trie
            if x == None: return []
            return x
        # recursive case
        x = self.children.get(key[:1]) # get trie instance corresponding to first key value
        if x == None: return []
        return x.get_trie(key[1:])

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        
        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bark'] = ':)'
        >>> t['bar'] = 3
        >>> t['bark']
        ':)'
        >>> t['ba']
        Traceback (most recent call last):
        KeyError: 'No value associated with key'
        """
        self.keyType(key) # check if correct type
        #base case
        if len(key) == 1:
            x = self.children.get(key)
            if x == None: raise KeyError("key not found in trie")
            if x.value == None: raise KeyError("No value associated with key")
            return x.value
        x = self.children.get(key[:1])
        if x == None: raise KeyError("key not found in trie")
        return x[key[1:]]

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
 
        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bark'] = ':)'
        >>> t['bar'] = 3
        >>> del t['bar']
        >>> t['bar']
        Traceback (most recent call last):
        KeyError: 'No value associated with key'
        >>> del t['foo']
        Traceback (most recent call last):
        KeyError: 'key not found in trie'      
        
        """
        self.keyType(key) # check if correct type
        if len(key) == 1:
            x = self.children.get(key)
            if x == None: raise KeyError("key not found in trie")
            if x.value == None: raise KeyError("No value associated with key")
            x.value = None # set Trie value to None
        else:
            x = self.children.get(key[:1])
            if x == None: raise KeyError("key not found in trie")
            del x[key[1:]]
        

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        
        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bark'] = ':)'
        >>> 'bat' in t
        True
        >>> 'ba' in t
        False
        """
        self.keyType(key)
        if len(key) == 1:
            x = self.children.get(key)
            if x == None: return False
            return x.value != None
        x = self.children.get(key[:1])
        if x == None: return False
        return key[1:] in x

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        for k, t in self.children.items():
            if t.value != None:
                yield (k, t.value)
            for x in iter(t):
                yield (k + x[0], x[1])
    
def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    
    >>> t = make_word_trie("goat go goad great ghost go go")
    >>> t['go']
    3
    >>> 'goat' in t
    True
    >>> 'goa' in t
    False
    """
    res = Trie(str)
    for sentence in tokenize_sentences(text):
        for word in sentence.split():
            if word in res:
                res[word] += 1
            else:
                res[word] = 1
    return res

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    
    >>> t = make_phrase_trie("let us have some fun")
    >>> t[('let', 'us', 'have', 'some', 'fun')]
    1
    """
    res = Trie(tuple)
    for sentence in tokenize_sentences(text):
        key = tuple(sentence.split())
        if key in res:
            res[key] += 1
        else:
            res[key] = 1
    return res

def autocomplete(trie, prefix, max_count = None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    
    >>> t = Trie(str)
    >>> t['bat'] = 2
    >>> t['bark'] = 1
    >>> t['battery'] = 3
    >>> t['boston'] = 4
    >>> autocomplete(t, 'ba', 1)
    ['battery']
    >>> autocomplete(t, 'be', 2)
    []
    >>> autocomplete(t, 'ba')
    ['bat', 'battery', 'bark']
    """

    trie.keyType(prefix) # check if prefix has correct type
    if max_count == None:
        res = [] # list to store results
        if prefix in trie:
            res.append(prefix)
        if len(prefix) != 0: 
            trie = trie.get_trie(prefix) # get trie node corresponding to prefix
        for k, v in trie:
            res.append(prefix + k) # get keys starting with prefix
        return res
    else:
        res = {} # initialize dictionary to store results
        if prefix in trie:
            res[prefix] = trie[prefix] # get key value pairs in order to sort
        if len(prefix) != 0: 
            trie = trie.get_trie(prefix)
        for k, v in trie:
            res[prefix + k] = v
        res = sorted(res, key = lambda x: res[x], reverse = True) # sort keys based on value
        if max_count < len(res):
            return res[:max_count]
        return res

def check_and_add(res, word, trie):
    """
    checks if word is in trie and adds it to dictionary
    """
    if word in trie:
        res[word] = trie[word]
       
def single_edits(trie, word):
    """
    Returns all the valid single character edits for a word sorted based on their frequency
    """
    res = {} # dict to store results
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(word)):
        check_and_add(res, word[:i] + word[i + 1:], trie) # char deletion
        check_and_add(res, word[:i] + word[i + 1 : i + 2] + word[i] + word[i + 2:], trie) # two char transpose
        for char in alphabet:
            check_and_add(res, word[:i] + char + word[i:], trie) # char insertion
            check_and_add(res, word[:i] + char + word[i + 1:], trie) # char replacement
    return sorted(res, key = lambda x: res[x]) # return sorted list

        
def autocorrect(trie, prefix, max_count = None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    
    >>> t = Trie(str)
    >>> t['bat'] = 2
    >>> t['bo'] = 3
    >>> t['bi'] = 2
    >>> t['ab'] = 1
    >>> t['bark'] = 1
    >>> t['battery'] = 3
    >>> t['boston'] = 4
    >>> autocorrect(t, 'ba')
    ['bat', 'bark', 'bo', 'ab', 'battery', 'bi']
    """
    
    res = autocomplete(trie, prefix, max_count) 
    edits = single_edits(trie, prefix)
    if max_count == None:
        return list(set(res + edits)) # convert to set to avoid adding duplicates
    elif len(res) < max_count:
        res = set(res)
        while edits and len(res) < max_count: # either make sure res is of length max_count or run out of edits
            res.add(edits.pop())
        return list(res)
    return res

def filt(trie, pattern, word = ''):
    """
    Return set of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    # base case
    if len(pattern) == 0:
        val = trie.value
        if val != None:
            return {(word, val)}
        else:
            return set()
    if pattern[0] == "*":
        res = filt(trie, pattern[1:], word) # match * with 0 characters 
        for k, v in trie.children.items():
            res |= filt(v, pattern, word + k) # match * with one or more
        return res
    if pattern[0] == "?":
        res = set()
        for k, v in trie.children.items():
            res |= filt(v, pattern[1:], word + k) # match rest of pattern
        return res
    res = set()
    for k, v in trie.children.items():
        if pattern[0] == k:
            res |= filt(v, pattern[1:], word + k) # match rest of pattern if first letter matches
            break
    return res
        
def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
         
    >>> t = make_word_trie("hi hello hause hose hide hide")
    >>> word_filter(t,"h*e")
    [('hose', 1), ('hause', 1), ('hide', 2)]
    
    """
    
    return [x for x in filt(trie, pattern)]


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    # t= make_word_trie("bat bat bark bar")
    
    with open("Alice_in_wonderland.txt", encoding = "utf-8") as f:
        alice = f.read()
    
    # t = make_phrase_trie(alice)
    # print(autocomplete(t, (), 6))

    # with open("metamorphosis.txt", encoding = "utf-8") as f:
    #     meta = f.read()
    
    # # t = make_word_trie(meta)
    # # # print(autocomplete(t, 'gre', 6))
    # # print(word_filter(t, 'c*h'))
    
    # with open("two_cities.txt", encoding = "utf-8") as f:
    #     cities = f.read()
    
    # t2 = make_word_trie(cities)
    # # print(word_filter(t2, 'r?c*t'))
    
    # t3 = make_word_trie(alice)
    # # print(autocorrect(t3, 'hear', 12))
    
    # with open("pride_and_prejudice.txt", encoding = "utf-8") as f:
    #     pride = f.read()
    
    # t4 = make_word_trie(pride)
    
    # # print(autocorrect(t4, 'hear'))
    
    # with open("Dracula.txt", encoding = "utf-8") as f:
    #     drac = f.read()
        
    # t5 = make_word_trie(drac)
    
    #print(sum(1 for key in t5))
    #print(sum(v for _,v in t5))
    
    #print(sum(1 for key in t))
    # print(sum(v for _,v in t))
    
    t4 = make_word_trie("man mat mattress map me met a man a a a map man met")
    # print(word_filter(t4, 'mat*'))
