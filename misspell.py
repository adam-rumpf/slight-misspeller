"""A Python module for slightly misspelling strings and text files.

This module defines a number of functions for converting strings and text
files into slightly misspelled versions of themselves.

If imported, these functions can be called directly. The following is a
summary of the public functions:

misspell_string(s[, config]) -- returns a misspelled version of a given string
    s (optional argument specifies custom settings file)
misspell_file(fin[, fout][, config]) -- writes a misspelled version of a given
    input file (or prints to screen if no output is given; optional argument
    specifies a custom settings file)

Command line arguments are also supported. Call "misspell.py --help" for a
complete guide.

Two different types of misspelling rule are defined: phonological misspelling,
which attempts to change the sounds of the words while still yielding a
pronounceable English word, and typographical misspelling, which simulates
random mistyping errors to replace letters without regard for
pronounceability.

The parameters which control the specifics of the misspelling process are
defined in a local INI file. If not already present, running any public
function generates a default file called "settings.ini". This file can be
manually edited to change the behavior of the algorithm, or it can be used as
a template for creating different settings profiles. See the comments in the
default config file for a complete guide.
"""

import argparse
import configparser
import math
import pathlib
import random
import re
import sys

#=============================================================================
# Global parameters
#=============================================================================

# Define docstrings
_VERSION = """Slight Misspeller v0.4.0-beta
Copyright (c) 2021 Adam Rumpf <adam-rumpf.github.io>
Released under MIT License <github.com/adam-rumpf/slight-misspeller>
"""
_DESCRIPTION = "Slightly misspells a string or file."
_EPILOG = """
The first argument may be either a string to convert, or the name of an input
file. The optional second argument specifies an output file. If excluded, the
result is instead printed to the screen.

Two different types of misspelling rule are defined: phonological misspelling,
which attempts to change the sounds of the words while still yielding a
pronounceable English word, and typographical misspelling, which simulates
random mistyping errors to replace letters without regard for
pronounceability.

The parameters which control the specifics of the misspelling process are
defined in a local INI file. If not already present, running this script
generates a default file called "settings.ini". This file can be manually
edited to change the behavior of the algorithm, or it can be used as a template
for creating different settings profiles. See the comments in the default
config file for a complete guide.
"""
_CONFIG_COMMENTS = """; 
; The fields below can be manually edited to change the behavior of the
; misspelling algorithms in 'misspell.py'.
;
; [typo]
;
; Defines parameters for typographical misspelling (conducted after all
; phonological misspelling). All fields specify probabilities between 0.0 and
; 1.0 for each event occurring for any given character.
;
; Events delete_char, insert, and replace are mutually exclusive, and the sum
; of their probabilities must not exceed 1.0.
;
; In general, typographical misspelling consists of replacing characters with
; nearby characters on the keyboard in order to simulate mistyping.
;
; delete_space -- chance to delete any given whitespace character
; delete_char -- chance to delete any given non-whitespace character; mutually
;     exclusive with insert and replace
; swap -- chance to swap any pair of adjacent characters during a final pass
; insert -- chance to insert an additional character before or after any given
;     non-whitespace character (both equally likely); additional character
;     chosen as a keyboard key adjacent to the current character; mutually
;     exclusive with delete_char and replace
; replace -- chance to replace any given non-whitespace character with one
;     next to it on the keyboard; mutually exclusive with delete_char and
;     insert
;
; [phono]
;
; Defines parameters for phonological misspelling (conducted before
; typographical misspelling. All fields specify probabilities between 0.0 and
; 1.0 for each event occurring for any given character.
;
; Events delete_char, insert, and replace are mutually exclusive, and the sum
; of their probabilities must not exceed 1.0.
;
; In general, phonological misspelling consists of replacing characters with
; other 'valid' characters based on a rough estimate of where the character
; falls within the word's pronunciation (e.g. vowels replace vowels,
; consonants replace consonants). Certain letter groups may be treated as a
; single unit (e.g. "th", "ch", "qu"), and any replacements are prohibited
; from creating an unpronounceable substring, both of which are defined in the
; local "data/rules.ini" file.
;
; delete -- chance to delete any given character or character group; mutually
;     exclusive with insert and replace
; insert -- chance to insert an additional valid character or character pair
;     before or after any given character or group (both equally likely)
; replace -- chance to replace any given character or group with another valid
;     character or group
;
; [blacklist]
;
; Case-insensitive list of blacklisted words, each on a separate line.
; Blacklisted words are removed from the final output string after all
; misspelling procedures have completed.
"""

# Define global constants
_VOWELS = "aeiou"
_CONSONANTS = "bcdfghjklmnpqrstvwxyz"
_KEYBOARD = ["1234567890", "qwertyuiop", "asdfghjkl;", "zxcvbnm,./",
             "!@#$%^&*()", "QWERTYUIOP", "ASDFGHJKL:", "ZXCVBNM<>?"]
_COS45 = math.sqrt(2)/2
_BLOCKS = ("c", "v", "vc", "c_b", "v_w", "cv_w")

# Define default global parameters
_DEF_CONFIG = "settings.ini" # currently-loaded config file name
_DEF_DATA = "data" # data file directory
_DEF_RULES = "rules.ini" # phonological rule file name
_DEF_BLACKLIST = () # words to prevent the program from accidentally creating
_DEF_TYPO_DELETE_SPACE = 0.005 # chance to delete any whitespace character
_DEF_TYPO_SWAP = 0.0075 # chance to swap consecutive characters
_DEF_TYPO_DELETE_CHAR = 0.0075 # chance to delete any non-whitespace character
_DEF_TYPO_INSERT = 0.001 # chance to insert a letter from an adjacent key
_DEF_TYPO_REPLACE = 0.0025 # chance to mistype a letter as an adjacent key
_DEF_PHONO_DELETE = 0.0025 # chance to delete a valid character
_DEF_PHONO_INSERT = 0.0025 # chance to insert a valid character
_DEF_PHONO_REPLACE = 0.005 # chance to replace a valid character

# Set global parameters to default values
_CONFIG = _DEF_CONFIG
_BLACKLIST = _DEF_BLACKLIST
_TYPO_DELETE_SPACE = _DEF_TYPO_DELETE_SPACE
_TYPO_SWAP = _DEF_TYPO_SWAP
_TYPO_DELETE_CHAR = _DEF_TYPO_DELETE_CHAR
_TYPO_INSERT = _DEF_TYPO_INSERT
_TYPO_REPLACE = _DEF_TYPO_REPLACE
_PHONO_DELETE = _DEF_PHONO_DELETE
_PHONO_INSERT = _DEF_PHONO_INSERT
_PHONO_REPLACE = _DEF_PHONO_REPLACE

#=============================================================================
# Misspelling algorithms
#=============================================================================

def _misspell_word(w, mode=0, rules=None):
    """_misspell_word(w[, mode][, rules]) -> str
    Misspells a single word string.
    
    This function is called repeatedly by the main driver to misspell each
    individual word in the master string. The input is assumed here to consist
    entirely of a string of characters.
    
    Positional arguments:
    w (str) -- single word to be misspelled
    
    Keyword arguments:
    [mode=0] (int) -- code for misspelling rules to apply (default 0 for all,
        1 for phonological only, 2 for typographical only)
    [rules=None] (configparser.ConfigParser) -- config parser for phonological
        misspelling rules, containing dictionaries of forbidden substrings and
        letter groups
    
    Returns:
    (str) -- misspelled version of word
    """
    
    # Validate input
    if type(w) != str:
        return w
    if mode not in {0, 1, 2}:
        mode = 0
    if type(rules) != type(configparser.ConfigParser()) and rules != None:
        rules = None
    
    # Special typographical procedures for whitespace
    w0 = "" # post-whitespace deletion string
    if w.isspace() == True:
        if mode in {0, 2}:
            # Chance to randomly delete whitespace characters
            for c in w:
                if random.random() < 1.0 - _TYPO_DELETE_SPACE:
                    w0 += c
        return w0
    
    # Apply phonological rules
    w1 = w # post-phonological misspelling string
    if mode in {0, 1}:

        # Split word into syllable blocks with categories
        (blocks, cats) = _word_blocks(w)
        
        ### Phonological misspelling procedure:
        ### Divide word into blocks.
        ###
        ### Go through each block one-at-a-time, and use its relationship with
        ### the other blocks to determine which rules to apply (C beginning,
        ### C after V, V before C, V at end, V only, C in a VC word, V in a
        ### VC word)
        ### If any of the blocks are punctuation, recursively apply rules to
        ### the maximal (C|V) blocks.
        ###
        ### After figuring out how to divide the word into syllables, send to
        ### the _misspell_syllable(block, category, rules=rules, preserve=?)
        ### function along with a syllable type categorization.
        ### If the gap between syllables is bridged by a letter group, we
        ### also set a flag to preserve the last letter of one and the first
        ### letter of the other.
        ###
        ### Finally, if the word includes enough blocks, consider
        ### transposing one VC block with another VC block.
        ###
        ### During this process, preserve the capitalization of the block.
        ### Keep to a single case if the entire block was a single case, and
        ### capitalize only the beginning if only the beginning was
        ### capitalized. If anything else, randomly choose cases for any
        ### new letters.
    
    # Apply typographical rules
    w2 = "" # post-typographical misspelling string
    if mode in {0, 2}:
        
        # Chance to randomly delete, insert, or mistype a character
        for c in w1:
            # Select a random type of mistake (or none)
            rand = random.random()
            if rand < _TYPO_DELETE_CHAR:
                # Delete character (omit from output string)
                continue
            elif rand < _TYPO_DELETE_CHAR + _TYPO_INSERT:
                # Insert an extra character (randomly select left or right)
                if random.random() < 0.5:
                    w2 += _mistype_key(c) + c
                else:
                    w2 += c + _mistype_key(c)
            elif rand < _TYPO_DELETE_CHAR + _TYPO_INSERT + _TYPO_REPLACE:
                # Replace character
                w2 += _mistype_key(c)
            else:
                # If no error, include unedited character
                w2 += c
    
    return w2

#-----------------------------------------------------------------------------

def _misspell_syllable(s, cat, rules=None, preserve=(False, False)):
    """_misspell_syllable(s, cat[, rules][, preserve]) -> str
    Misspells a single syllable.
    
    The smallest unit of the recursive phonological misspelling scheme. The
    input is assumed here to consist entirely of a string of characters.
    
    Positional arguments:
    s (str) -- syllable to be misspelled
    cat (str) -- categorization of the given syllable, as a section in the
        'rules' config parser
    
    Keyword arguments:
    [rules=None] (configparser.ConfigParser) -- config parser for phonological
        misspelling rules, containing dictionaries of forbidden substrings and
        letter groups
    [preserve=(False, False)] (tuple(bool)) -- flags indicating whether to
        preserve the first and last characters (2-tuple of first/last order,
        True to preserve character and False otherwise)
    
    Returns:
    (str) -- misspelled syllable
    """
    
    # Validate input
    if type(s) != str:
        return s
    if type(cat) != str:
        cat = ""
    if type(rules) != type(configparser.ConfigParser()) and rules != None:
        rules = None
    if (type(preserve) != tuple or len(preserve) != 2 or
        type(preserve[0]) != bool or type(preserve[1]) != bool):
        preserve = (False, False)
        
        ### _PHONO_DELETE
        ### _PHONO_INSERT
        ### _PHONO_REPLACE
    
        ### Go through each letter in the block and decide whether to apply
        ### any transformations. If the letter is part of a possible group,
        ### consider grouping it alongside an adjacent letter (which could
        ### be part of the next block, if this is the final letter in the
        ### current block).
        ### Use the 'preserve' value to determine whether to preserve the
        ### first or last symbol.
        ###
        ### Possible transformations include: deleting the letter (or pair),
        ### replacing the letter (or pair) with another of the same type,
        ### and inserting another letter of the same type before or after.
        ###
        ### Randomly generate a move of the chosen type, and check the
        ### resulting letter block against blacklisted substrings for its
        ### block type. If there's no problem, apply the change, and
        ### otherwise reroll to attempt a different type of change (up to
        ### a limit).
        ###
        ### During this entire process, keep track of our current place
        ### within the current block. By default it should advance by 1
        ### with each character, but go back 1 whenever we delete a
        ### character or forward by 1 whenever we insert one. We could
        ### generalize this process by simply remembering the length of the
        ### block before and after to compare the two, and offset our
        ### current position by 1 + new_length - old_length. The loop should
        ### be while our current position is less than the block's length.
    
    ###
    return s

#-----------------------------------------------------------------------------

def _word_blocks(w):
    """_word_blocks(w) -> (list, list)
    Divides a word into syllable blocks (with categories).

    Words are divided into blocks in an attempt to roughly represent the
    syllables of the word. This function returns a 2-tuple of lists, with the
    first containing a partition of the word into block substrings, and the
    second containing a corresponding list of syllable categorizations whose
    names correspond to the sections of the phonological rule data file.

    Categorizations are respresented by one of the following strings:
    "vc" -- vowel string followed by a consonant string
    "c_b" -- consonant string at beginning of word
    "v_e" -- vowel string at end of word
    "v_w" -- word made entirely of a single vowel string
    "cv_w" -- word made entirely of a consonant string followed by a vowel
        string
    "n" -- non-letter characters

    Positional arguments:
    w (str) -- word to split

    Returns:
    (list, list) -- tuple of the syllable block list followed by a
        corresponding list of categories for each syllable
    """

    # Validate input
    if type(w) != str:
        return w

    # Split string into consonant/vowel/other clusters
    clusters = [x for x in re.split("(["+_VOWELS+"]+)|(["+_CONSONANTS+"]+)",
                w, flags=re.IGNORECASE) if x]

    # Initialize return lists
    blocks = []
    cats = []

    # Check for single-block words
    if len(clusters) == 1 and clusters[0][0].lower() in _VOWELS:
        return ([w], ["v_w"])
    if (len(clusters) == 2 and clusters[0][0].lower() in _CONSONANTS
        and clusters[1][0].lower() in _VOWELS):
        return ([w], ["cv_w"])

    # Read through clusters in order
    i = -1 # current cluster index
    pbreak = False # whether the previous cluster is a break
    nbreak = False # whether the next cluster is a break
    c = "" # first character of current cluster
    while i < len(clusters) - 1:
        # Find current letter and whether it's against a break
        i += 1
        if i == 0 or clusters[i-1][0].isalpha() == False:
            pbreak = True
        else:
            pbreak = False
        if i == len(clusters) - 1 or clusters[i+1][0].isalpha() == False:
            nbreak = True
        else:
            nbreak = False
        c = clusters[i][0].lower()
        # Check for consonant at beginning
        if c in _CONSONANTS and pbreak == True:
            blocks.append(clusters[i])
            cats.append("c_b")
        # Check for vowel at end
        elif c in _VOWELS and nbreak == True:
            blocks.append(clusters[i])
            cats.append("v_e")
        # Check for vowel followed by consonant
        elif c in _VOWELS and clusters[i+1][0].lower() in _CONSONANTS:
            blocks.append(clusters[i] + clusters[i+1])
            cats.append("vc")
            i += 1
        # If nothing else, non-letter
        else:
            blocks.append(clusters[i])
            cats.append("n")

    # Return lists
    return (blocks, cats)

#-----------------------------------------------------------------------------

def _can_swap(c1, c2):
    """_can_swap(c1, c2) -> bool
    Defines whether a given pair of characters can swap.
    
    One of the allowed types of typographical error is for two characters to
    switch position. This is allowed only when they are two letters of the
    same case, or two numbers, or two punctuation marks.
    
    Positional arguments:
    c1 (str) -- first character
    c2 (str) -- second character
    
    Returns:
    (bool) -- True if the swap is valid, False otherwise
    """
    
    # Validate input
    if ((type(c1) != str) or (type(c2) != str) or
        (len(c1) > 1) or (len(c2) > 1)):
        return False
    
    # Check for allowed combinations
    if c1.islower() and c2.islower():
        return True
    if c1.isupper() and c2.isupper():
        return True
    if c1.isdigit() and c2.isdigit():
        return True
    p = "!@#$%^&*()_-+=[]{}\\|;:'\",.<>/?`~"
    if (c1 in p) and (c2 in p):
        return True
    
    # If all tests failed, the swap is not allowed
    return False

#-----------------------------------------------------------------------------

def _mistype_key(c):
    """_mistype_key(c) -> str
    Finds a key near the specified key.

    Given a keyboard character, this function returns the character of an
    adjacent key. Rectilinear moves are all equally likely, and diagonal moves
    are equally likely but with a diminished weight of sqrt(2)/2 ~= 0.707.

    Positional arguments:
    c (str) -- keyboard character to replace

    Returns:
    (str) -- single character to replace the given character
    """

    # Validate input
    if (type(c) != str) or (len(c) != 1):
        return c

    # Find the keyboard list to which the character belongs
    row = 0 # row index (0-3 for lowercase row, 4-7 for uppercase row)
    while (row <= 7) and (c not in _KEYBOARD[row]):
        row += 1

    # If all rows passed without a match, change nothing
    if row > 7:
        return c

    # Determine whether the key is on a boundary
    col = _KEYBOARD[row].find(c) # column index
    lb = False # left boundary
    if col == 0:
        lb = True
    rb = False # right boundary
    if col >= len(_KEYBOARD[row]) - 1:
        rb = True
    tb = False # top boundary
    if row % 4 == 0:
        tb = True
    bb = False # bottom boundary
    if row % 4 == 3:
        bb = True

    # Build a weighted list of adjacent keys
    choices = {} # dictionary of weighted choices
    if not lb:
        choices[_KEYBOARD[row][col-1]] = 1
        if not tb:
            choices[_KEYBOARD[row-1][col-1]] = _COS45
        if not bb:
            choices[_KEYBOARD[row+1][col-1]] = _COS45
    if not rb:
        choices[_KEYBOARD[row][col+1]] = 1
        if not tb:
            choices[_KEYBOARD[row-1][col+1]] = _COS45
        if not bb:
            choices[_KEYBOARD[row+1][col+1]] = _COS45
    if not tb:
        choices[_KEYBOARD[row-1][col]] = 1
    if not bb:
        choices[_KEYBOARD[row+1][col]] = 1

    # Randomly select an adjacent key
    return _dictionary_sample(choices)

#=============================================================================
# Resource file functions
#=============================================================================

def _read_config(fin, silent=False):
    """_read_config(fin[, silent])
    Reads an INI file to set or reset parameters.
    
    Reading a config file updates a variety of internal parameters, which
    remain unchanged until a new config file is read. Attempting to read the
    most recent config file a second time has no effect.
    
    Positional arguments:
    fin (str) -- config file name, or None to do nothing
    
    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Global parameters to be edited
    global _CONFIG, _BLACKLIST, _TYPO_DELETE_SPACE, _TYPO_DELETE_CHAR
    global _TYPO_SWAP, _TYPO_INSERT, _TYPO_REPLACE
    global _PHONO_DELETE, _PHONO_INSERT, _PHONO_REPLACE

    # Generate default config if it does not exist
    if pathlib.Path(_DEF_CONFIG).exists() == False:
        _default_config(silent=silent)
    
    # Validate input
    if type(fin) != str and fin != None:
        return None

    # Do nothing if input is None
    if fin == None:
        return None

    # Do nothing if selected file has already been loaded
    if fin == _CONFIG:
        return None

    # Regenerate default config
    if fin == _DEF_CONFIG:
        _CONFIG = _DEF_CONFIG
        return _default_config(silent=silent)
    
    # Read INI file and set (or reset) parameters
    if silent == False:
        print("Reading config file '" + fin + "' ...")
        
    # Initialize config parser
    config = configparser.ConfigParser(allow_no_value=True)

    # Verify that config file exists
    if pathlib.Path(fin).exists() == False:
        if silent == False:
            print("Config file '" + fin + "' not found.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)

    # Read config file
    config.read(fin)
    
    # Read typographical section
    try:
        key = "delete_space"
        _TYPO_DELETE_SPACE = float(config["typo"][key])
        key = "delete_char"
        _TYPO_DELETE_CHAR = float(config["typo"][key])
        key = "swap"
        _TYPO_SWAP = float(config["typo"][key])
        key = "insert"
        _TYPO_INSERT = float(config["typo"][key])
        key = "replace"
        _TYPO_REPLACE = float(config["typo"][key])
    except KeyError:
        if silent == False:
            print("Key '" + key + "' from 'typo' section not found in '" +
                fin + "'.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)
    except ValueError:
        if silent == False:
            print("Key '" + key + "' from 'typo' section in '" + fin +
                  "' should be a number.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)

    # Validate all typographical parameters as probabilities on [0.0,1.0]
    valid = True
    if _TYPO_DELETE_SPACE < 0 or _TYPO_DELETE_SPACE > 1:
        valid = False
    if _TYPO_DELETE_CHAR < 0 or _TYPO_DELETE_CHAR > 1:
        valid = False
    if _TYPO_SWAP < 0 or _TYPO_SWAP > 1:
        valid = False
    if _TYPO_INSERT < 0 or _TYPO_INSERT > 1:
        valid = False
    if _TYPO_REPLACE < 0 or _TYPO_REPLACE > 1:
        valid = False
    if _TYPO_DELETE_CHAR + _TYPO_INSERT + _TYPO_REPLACE > 1:
        valid = False
    if valid == False:
        if silent == False:
            print("Invalid 'typo' parameter read in '" + fin + "'.")
            print("All parameters should be probabilities between 0.0 and 1.0.")
            print("The sum of 'delete_char', 'insert', and 'replace' should " +
                  "not exceed 1.0.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)
    
    # Read phonological section
    try:
        key = "delete"
        _PHONO_DELETE = float(config["phono"][key])
        key = "insert"
        _PHONO_INSERT = float(config["phono"][key])
        key = "replace"
        _PHONO_REPLACE = float(config["phono"][key])
    except KeyError:
        if silent == False:
            print("Key '" + key + "' from 'phono' section not found in '" +
                fin + "'.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)
    except ValueError:
        if silent == False:
            print("Key '" + key + "' from 'phono' section in '" + fin +
                  "' should be a number.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)

    # Validate all phonological parameters as probabilities on [0.0,1.0]
    valid = True
    if _PHONO_DELETE < 0 or _PHONO_DELETE > 1:
        valid = False
    if _PHONO_INSERT < 0 or _PHONO_INSERT > 1:
        valid = False
    if _PHONO_REPLACE < 0 or _PHONO_REPLACE > 1:
        valid = False
    if _PHONO_DELETE + _PHONO_INSERT + _PHONO_REPLACE > 1:
        valid = False
    if valid == False:
        if silent == False:
            print("Invalid 'phono' parameter read in '" + fin + "'.")
            print("All parameters should be probabilities between 0.0 and 1.0.")
            print("The sum of 'delete', 'insert', and 'replace' should " +
                  "not exceed 1.0.")
            print("Reverting to default parameters.")
        return _default_config(silent=silent)

    # Read blacklist (section not required)
    if "blacklist" in config.sections():
        _BLACKLIST = tuple(dict(config.items("blacklist")))
    else:
        _BLACKLIST = _DEF_BLACKLIST
    
    if silent == False:
        print("Config file successfully loaded!")

    # Update current config file
    _CONFIG = fin

#-----------------------------------------------------------------------------

def _default_config(silent=False, comments=True):
    """_default_config([silent])
    Sets default parameters and writes the default config file.
    
    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    [comments=True] (bool) -- whether to include comments in the config file
    """
    
    # Global parameters to be edited
    global _CONFIG, _BLACKLIST, _TYPO_DELETE_SPACE, _TYPO_DELETE_CHAR
    global _TYPO_SWAP, _TYPO_INSERT, _TYPO_REPLACE
    global _PHONO_DELETE, _PHONO_INSERT, _PHONO_REPLACE

    if silent == False:
        print("Resetting config file to default 'settings.ini' ...")

    # Reset all global parameters to their default values
    _CONFIG = _DEF_CONFIG
    _BLACKLIST = _DEF_BLACKLIST
    _TYPO_DELETE_SPACE = _DEF_TYPO_DELETE_SPACE
    _TYPO_SWAP = _DEF_TYPO_SWAP
    _TYPO_DELETE_CHAR = _DEF_TYPO_DELETE_CHAR
    _TYPO_INSERT = _DEF_TYPO_INSERT
    _TYPO_REPLACE = _DEF_TYPO_REPLACE
    _PHONO_DELETE = _DEF_PHONO_DELETE
    _PHONO_INSERT = _DEF_PHONO_INSERT
    _PHONO_REPLACE = _DEF_PHONO_REPLACE

    # Initialize config parser
    config = configparser.ConfigParser(allow_no_value=True)

    # Load typographical parameters
    dic = {}
    dic["delete_space"] = _TYPO_DELETE_SPACE
    dic["delete_char"] = _TYPO_DELETE_CHAR
    dic["swap"] = _TYPO_SWAP
    dic["insert"] = _TYPO_INSERT
    dic["replace"] = _TYPO_REPLACE
    config["typo"] = dic
    del dic
    
    # Load phonological parameters
    dic = {}
    dic["delete"] = _PHONO_DELETE
    dic["insert"] = _PHONO_INSERT
    dic["replace"] = _PHONO_REPLACE
    config["phono"] = dic
    del dic

    # Load blacklist
    dic = {}
    for w in _BLACKLIST:
        dic[w] = None
    config["blacklist"] = dic
    del dic

    # Write config file
    with open(_CONFIG, 'w') as f:
        config.write(f)

    # Write comment lines to beginning of file
    if comments == True:
        text = "" # all text in config file

        # Get config contents
        with open(_CONFIG, 'r') as f:
            text = f.read()

        # Write version info into comments
        version = ""
        for line in _VERSION.split("\n")[:-1]:
            version += "; " + line + "\n"

        # Write version, comments, and config text to config file
        text = version + _CONFIG_COMMENTS + "\n" + text
        with open(_CONFIG, 'w') as f:
            f.write(text)

    if silent == False:
        print("Config file successfully reset!")

#-----------------------------------------------------------------------------

def _read_rules(silent=False):
    """_read_rules() -> configparser.ConfigParser
    Reads the rules resource INI file for phonological misspelling rules.

    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    
    Returns:
    (configparser.ConfigParser) -- parser object of phonological misspelling
        rules, including forbidden substrings within different word blocks and
        letter groups
    """

    if silent == False:
        print("Reading phonological rule data ...")

    # Define file path to data file
    fin = pathlib.PurePath(__file__).parent / _DEF_DATA / _DEF_RULES

    # Initialize data file parser
    config = configparser.ConfigParser(allow_no_value=True)

    # Verify that config file exists
    if pathlib.Path(fin).exists() == False:
        # If not, return an empty parser
        if silent == False:
            print("Rule data not found. Ignoring phonological rules.")
        config["group"] = {}
        for b in _BLOCKS:
            config[b] = {}
        return config

    # Read data file
    config.read(fin)

    # Verify that all needed fields are present
    if "group" not in config:
        config["group"] = {}
    for b in _BLOCKS:
        if b not in config:
            config[b] = {}

    if silent == False:
        print("Phonological rules loaded!")
    
    # Return the parser
    return config

#=============================================================================
# General utility functions
#=============================================================================

def _dictionary_sample(dic):
    """_dictionary_sample(dic) -> key
    Returns a weighted random sample key from a dictionary.

    The dictionary is assumed to consist of key/weight pairs.

    Positional arguments:
    dic (dict) -- dictionary of key/weight pairs (weights given as floats)

    Returns:
    (key) -- random key from dictionary
    """

    # Validate input
    if type(dic) != dict:
        return None

    # Find total weight
    total = 0.0
    for key in dic:
        total += dic[key]

    # Select a random weight
    rand = total*random.random()

    # Iterate through dictionary until passing this weight
    total = 0.0
    for key in dic:
        total += dic[key]
        if total >= rand:
            return key

    # Final stop for safety
    return list(dic)[0]

#=============================================================================
# Public functions
#=============================================================================

def misspell_string(s, mode=0, config=_DEF_CONFIG, silent=False,
    rules_in=None):
    """misspell_string(s[, mode][, config][, silent][, rules_in]) -> str
    Returns a misspelled version of a given string.
    
    Positional arguments:
    s (str) -- string to be misspelled
    
    Keyword arguments:
    [mode=0] (int) -- code for misspelling rules to apply (default 0 for all,
        1 for phonological only, 2 for typographical only)
    [config="settings.ini"] (str) -- config file name to control parameters
        (defaults to standard config file, or None to skip the file loading)
    [silent=False] (bool) -- whether to print progress messages to the screen
    [rules_in=None] (configparser.ConfigParser) -- config parser of letter
        group and forbidden substring dictionaries for phonological misspelling
        rules, normally expected to be passed by misspell_file; file loaded by
        this function if None
    
    Returns:
    (str) -- misspelled version of string
    """
    
    # Validate input
    if mode not in {0, 1, 2}:
        if silent == False:
            print("unrecognized mode index; defaulting to 0 ('all')")
        mode = 0
    if type(s) != str:
        sys.exit("input must be a string")
    if type(config) != str and config != None:
        sys.exit("config file name must be a string or None")
    if (type(rules_in) != type(configparser.ConfigParser())
        and rules_in != None):
        sys.exit("rules option must be a ConfigParser or None")
    
    # Set config file (does nothing if no change)
    if config != None:
        _read_config(config, silent=silent)
    
    # Load phonological rules dictionary if not already defined
    rules = rules_in
    if rules == None and mode in {0, 1}:
        rules = _read_rules(silent=silent)
    
    # Translate line-by-line and word-by-word
    out_text = "" # complete output string
    for line in s.split('\n'):
        out_line = "" # complete line of output string
        line_part = re.split(r'(\s+)', line) # word and whitespace clusters
        for word in line_part:
            # Misspell word
            out_line += _misspell_word(word, rules=rules)
        # Apply final typographical errors
        if mode in {0, 2}:
            # Random character swaps
            for i in range(len(out_line)-1):
                # Get two consecutive letters
                c1, c2 = out_line[i], out_line[i+1]
                # Skip if characters are not compatible
                if _can_swap(c1, c2) == False:
                    continue
                # Otherwise roll for random swap
                if random.random() < _TYPO_SWAP:
                    out_line = (("", out_line[:i])[i > 0] + c2 + c1 +
                                ("", out_line[i+2:])[i < len(out_line)-1])
        # Run a final check for blacklisted words
        for w in _BLACKLIST:
            # Attempt to find the blacklisted word
            while out_text.lower().find(w.lower()) >= 0:
                # If present, delete its last character
                pos = out_text.lower().find(w.lower()) + len(w) - 1
                out_text = out_text[:pos] + out_text[pos+1:]
                    
        out_text += out_line + '\n'
    
    return out_text[:-1]

#-----------------------------------------------------------------------------

def misspell_file(fin, fout=None, mode=0, config=_DEF_CONFIG,
                  silent=False):
    """misspell_file(fin[, fout][, mode][, config][, silent])
    Writes a misspelled version of a given text file.
    
    Attempts to read a text file and misspell each word one-by-one. The result
    is either written to a separate text file or printed to the screen.
    
    Positional arguments:
    fin (str) -- input file name
    
    Keyword arguments:
    [fout=False] (str) -- output file name (or None to print to screen)
    [mode=0] (int) -- code for misspelling rules to apply (default 0 for all,
        1 for phonological only, 2 for typographical only)
    [config="settings.ini"] (str) -- config file name to control parameters
        (defaults to standard config file, or None to skip the file loading)
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Validate inputs
    if mode not in {0, 1, 2}:
        if silent == False:
            print("unrecognized mode index; defaulting to 0 ('all')")
        mode = 0
    if type(fin) != str:
        sys.exit("input argument must be a file name string")
    if type(fout) != str and fout != None:
        sys.exit("output argument must be a file name string or None")
    if type(config) != str and config != None:
        sys.exit("config file name must be a string or None")
    
    # Set config file (does nothing if no change)
    if config != None:
        _read_config(config)
    
    # Load phonological rules dictionary if needed
    rules = None
    if mode in {0, 1}:
        rules = _read_rules(silent=silent)
    
    # Translate file line-by-line
    try:
        with open(fin, 'r') as f:
            # If file is found, translate line-by-line
            if silent == False:
                print("Converting input file '" + fin + "' ...")
            out_text = "" # complete output string
            for line in f:
                # Call string misspeller for each line
                out_text += misspell_string(line, mode=mode, config=None,
                                            silent=silent, rules_in=rules)
    except FileNotFoundError:
        sys.exit("input file " + fin + " not found")
    
    # Write output string to a file or print to the screen
    if fout == None:
        print('\n' + '>'*10 + '\n\n' + out_text)
    else:
        with open(fout, 'w') as f:
            f.write(out_text)
            if silent == False:
                print("Output file '" + fout + "' written.")

#=============================================================================
# Command line usage
#=============================================================================

###if __name__ == "__main__" and len(sys.argv) > 1:
if False:

    # Initialize argument parser and mutually exclusive group
    parser = argparse.ArgumentParser(description=_DESCRIPTION, epilog=_EPILOG,
                                     formatter_class=
                                     argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()

    # Define arguments
    parser.add_argument("-v", "--version", action="version", version=_VERSION)
    parser.add_argument("instring",
                        help="input file (or string with the --string tag)")
    parser.add_argument("outstring", nargs="?",
                        help="output file (leave empty to print result to " +
                        "screen)")
    parser.add_argument("-i", "--init-file", default=_DEF_CONFIG,
                        help="misspeller parameter config file", dest="config")
    parser.add_argument("-s", "--string", action="store_true",
                        help=("interpret 'instring' as a string to be " +
                              "misspelled rather than a file path"))
    parser.add_argument("-q", "--quiet", action="store_true", dest="silent",
                        help="silence progress messages")
    group.add_argument("-p", "--phono", action="store_true",
                       help="apply only phonological misspelling rules")
    group.add_argument("-t", "--typo", action="store_true",
                       help="apply only typographical misspelling rules")
    
    # Parse command line arguments
    args = parser.parse_args()

    # Use arguments to call an appropriate public function
    mode = 0
    if args.phono == True:
        mode = 1
    if args.typo == True:
        mode = 2
    if args.string == True:
        s = misspell_string(args.instring, mode=mode, config=args.config,
                            silent=args.silent)
        if args.outstring == None:
            print(s)
        else:
            with open(args.outstring, 'w') as f:
                f.write(s)
                if args.silent == False:
                    print("Output file '" + args.outstring + "' written.")
    else:
        misspell_file(args.instring, args.outstring, mode=mode,
                      config=args.config, silent=args.silent)
