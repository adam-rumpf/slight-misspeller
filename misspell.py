"""A Python module for slightly misspelling strings and text files.

This module defines a number of functions for converting strings and text
files into slightly misspelled versions of themselves.

If imported, these functions can be called directly. The following is a
summary of the public functions:
    misspell_string(s[, config]) -- returns a misspelled version of a given
        string s (optional argument specifies custom settings file)
    misspell_file(fin[, fout][, config]) -- writes a misspelled version of a
        given input file (or prints to screen if no output is given; optional
        argument specifies a custom settings file)

Two different types of misspelling rule are defined: phonological misspelling,
which attempts to change the sounds of the words while still yielding a
pronounceable English word, and typographical misspelling, which simulates
random mistyping errors to replace letters without regard for
pronounceability.

The parameters which control the specifics of the misspelling process are
defined in a local INI file. If not already present, running any public
function generates a default file called "settings.ini". This file can be
manually edited to change the behavior of the algorithm, or it can be used as
a template for creating different settings profiles. Each public method
accepts an optional "config" keywoard argument to specify a non-standard
settings file.

This script can also be called from the command line using the following
(Linux) format:
    $ python misspell.py <in> [<out>]
where:
    <in>        name of input text file (or raw string to be converted, if
                --text flag is set)
    <out>       name of output text file (if left blank, result is printed to
                screen)

Command line options include the following:
    -h, --help              display usage guide and exit
    -v, --version           display version info and exit
    -i, --init-file=STRING  specifies a custom INI file to define parameters
                            (default "settings.ini", which this program
                            automatically generates if not present)
    -r, --raw               interpret first argument as a raw input string
                            rather than an input file name
    -p, --phono             apply only phonological (sound-based) misspelling
                            rules (mutually exclusive with --typo)
    -t, --typo              apply only typographical (letter-based)
                            misspelling rules (mutually exclusive with
                            --phono)
    -s, --silent            suppresses progress messages
    -q, --quiet             equivalent to --silent
"""

import argparse
import configparser
import math
import random
import re

#=============================================================================
# Global parameters
#=============================================================================

# Define docstrings
_VERSION = """Slight Misspeller v0.1.0-beta
Copyright (c) 2021 Adam Rumpf <adam-rumpf.github.io>
Released under MIT license <github.com/adam-rumpf/slight-misspeller>
"""
_CONFIG_COMMENTS = """; 
; The fields below can be manually edited to change the behavior of the
; misspelling algorithms in 'misspell.py'.
;
; [typographical]
;
; Defines parameters for typographical misspelling (conducted after all
; phonological misspelling). All fields specify probabilities between 0.0 and
; 1.0 for each event occurring for any given character.
;
; Events delete_char, insert, and replace are mutually exclusive, and the sum
; of their probabilities must not exceed 1.0.
;
; delete_space -- chance to delete any given whitespace character
; delete_char -- chance to delete any given non-whitespace character; mutually
;     exclusive with insert and replace
; swap -- chance to swap any pair of adjacent characters during a final pass
; insert -- chance to insert an additional character before or after any given
;     non-whitespace character (both equally likely); additional character
;     chosen as a keyboard key adjacent to the current character; mutually
;     exclusive with delete_char and replace
; replace -- chance to replace any given non-whitespace character with one next
;     to it on the keyboard; mutually exclusive with delete_char and insert
;
; [blacklist]
;
; Case-insensitive list of blacklisted words, each on a separate line.
; Blacklisted words are removed from the final output file after all
; misspelling procedures have completed.
"""

# Define global constants
_VOWELS = "aeiou"
_CONSONANTS = "bcdfghjklmnpqrstvwxyz"
_KEYBOARD = ["1234567890", "qwertyuiop", "asdfghjkl;", "zxcvbnm,./",
             "!@#$%^&*()", "QWERTYUIOP", "ASDFGHJKL:", "ZXCVBNM<>?"]
_COS45 = math.sqrt(2)/2
### Also include any sets needed to define phonological misspelling rules.

# Define default global parameters
_DEF_CONFIG = "settings.ini" # currently-loaded config file name
_DEF_BLACKLIST = () # words to prevent the program from accidentally creating
_DEF_TYPO_DELETE_SPACE = 0.005 # chance to delete any whitespace character
_DEF_TYPO_SWAP = 0.0075 # chance to swap consecutive characters
_DEF_TYPO_DELETE_CHAR = 0.0075 # chance to delete any non-whitespace character
_DEF_TYPO_INSERT = 0.001 # chance to insert a letter from an adjacent key
_DEF_TYPO_REPLACE = 0.0025 # chance to mistype a letter as an adjacent key

# Set global parameters to default values
_CONFIG = _DEF_CONFIG
_BLACKLIST = _DEF_BLACKLIST
_TYPO_DELETE_SPACE = _DEF_TYPO_DELETE_SPACE
_TYPO_SWAP = _DEF_TYPO_SWAP
_TYPO_DELETE_CHAR = _DEF_TYPO_DELETE_CHAR
_TYPO_INSERT = _DEF_TYPO_INSERT
_TYPO_REPLACE = _DEF_TYPO_REPLACE

### Other parameters:
### Typographical: extra adjacent letter, replacement adjacent letter
### Phonological: onset replacement, nucleus replacement, coda replacement,
### transpositions

#=============================================================================
# Private functions
#=============================================================================

def _misspell_word(w, mode=0):
    """_misspell_word(w[, mode]) -> str
    Misspells a single word string.
    
    This function is called repeatedly by the main driver to misspell each
    individual word in the master string. The input is assumed here to consist
    entirely of a string of characters.
    
    Positional arguments:
    w (str) -- single word to be misspelled
    
    Keyword arguments:
    [mode=0] (int) -- code for misspelling rules to apply (default 0 for all,
        1 for phonological only, 2 for typographical only)
    
    Returns:
    str -- misspelled version of word
    """
    
    # Validate input
    if mode not in {0, 1, 2}:
        mode = 0
    if type(w) != str:
        raise TypeError("argument must be a string")
        return None
    
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
        
        # Split string into consonant/vowel/punctuation clusters
        s = [x for x in re.split("(["+_VOWELS+"]+)|(["+_CONSONANTS+"]+)",
             w1, flags=re.IGNORECASE) if x]
        
        ### Apply phonological misspelling to each cluster.
    
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

def _misspell_syllable(s):
    """_misspell_syllable(s) -> str
    Misspells a single syllable.
    
    The smallest unit of the recursive phonological misspelling scheme. The
    input is assumed here to consist entirely of a string of characters.
    
    Positional arguments:
    s (str) -- syllable to be misspelled
    
    Returns:
    str -- misspelled syllable
    """
    
    # Validate input
    if type(s) != str:
        raise TypeError("argument must be a string")
        return None
    
    ###
    # Steps:
    # Attempt to acquire capitalization
    # Apply misspelling rules
    # Return the transformed result
    
    ###
    return s

#-----------------------------------------------------------------------------

def _read_config(fin, silent=False):
    """_read_config(fin[, silent])
    Reads an INI file to set or reset parameters.
    
    Reading a config file updates a variety of internal parameters, which
    remain unchanged until a new config file is read. Attempting to read the
    most recent config file a second time has no effect.
    
    Positional arguments:
    fin (str) -- config file name
    
    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Global parameters to be edited
    global _CONFIG, _BLACKLIST, _TYPO_DELETE_SPACE, _TYPO_DELETE_CHAR
    global _TYPO_SWAP, _TYPO_INSERT, _TYPO_REPLACE
    
    # Validate input
    if type(fin) != str:
        raise TypeError("input argument must be a config file name string")
        return None
    
    # Quit if config file has already been read
    if _CONFIG == fin:
        return None
    
    # Read INI file and set (or reset) parameters
    if silent == False:
        print("Reading config file '" + fin + "'.")
    try:
        try:
            ### read fields one-by-one
            ### include input validation for each individual field
            ###
            ### _DELETE_CHAR, _TYPO_INSERT, and _TYPO_REPLACE should sum to <=1
            pass
        except KeyError:
            ### print a message which specifies the key that does not exist
            key = "temp"###
            if silent == False:
                print("Key " + key + " not found in '" + fin + "'.")
                print("Reverting to default parameters.")
            return _default_config(silent=silent)
    except FileNotFoundError:
        raise FileNotFoundError("config file " + fin + " not found")
        return None

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

    # Initialize config parser
    config = configparser.ConfigParser(allow_no_value=True)

    # Load typographical parameters
    dic = {}
    dic["delete_space"] = _TYPO_DELETE_SPACE
    dic["delete_char"] = _TYPO_DELETE_CHAR
    dic["swap"] = _TYPO_SWAP
    dic["insert"] = _TYPO_INSERT
    dic["replace"] = _TYPO_REPLACE
    config["typographical"] = dic
    del dic

    ###
    # Load phonological parameters

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
        raise TypeError("both inputs must be single-character strings")
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
        raise TypeError("input key must be a single-character string")
        return None

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

#-----------------------------------------------------------------------------

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
        raise TypeError("sample object must be a key/weight dictionary")
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

def misspell_string(s, mode=0, config="settings.ini", silent=False):
    """misspell_string(s[, mode][, config][, silent]) -> str
    Returns a misspelled version of a given string.
    
    Positional arguments:
    s (str) -- string to be misspelled
    
    Keyword arguments:
    [mode=0] (int) -- code for misspelling rules to apply (default 0 for all,
        1 for phonological only, 2 for typographical only)
    [config="settings.ini"] (str) -- config file name to control parameters
    [silent=False] (bool) -- whether to print progress messages to the screen
    
    Returns:
    str -- misspelled version of string
    """
    
    # Validate input
    if mode not in {0, 1, 2}:
        if silent == False:
            print("unrecognized mode index; defaulting to 0 ('all')")
        mode = 0
    if type(s) != str:
        raise TypeError("input must be a string")
        return None
    if type(config) != str:
        raise TypeError("config file name must be a string")
        return None
    
    # Set config file (does nothing if no change)
    _read_config(config, silent=silent)
    
    # Translate line-by-line and word-by-word
    out_text = "" # complete output string
    for line in s.split('\n'):
        out_line = "" # complete line of output string
        line_part = re.split(r'(\s+)', line) # word and whitespace clusters
        for word in line_part:
            # Misspell word
            out_line += _misspell_word(word)
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

def misspell_file(fin, fout=None, mode=0, config="settings.ini",
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
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Validate inputs
    if mode not in {0, 1, 2}:
        if silent == False:
            print("unrecognized mode index; defaulting to 0 ('all')")
        mode = 0
    if type(fin) != str:
        raise TypeError("input argument must be a file name string")
        return None
    if type(fout) != str and fout != None:
        raise TypeError("output argument must be a file name string or None")
        return None
    if type(config) != str:
        raise TypeError("config file name must be a string")
        return None
    
    # Set config file (does nothing if no change)
    _read_config(config)
    
    # Translate file line-by-line
    try:
        with open(fin, 'r') as f:
            # If file is found, translate line-by-line
            if silent == False:
                print("Converting input file '" + fin + "' ...")
            out_text = "" # complete output string
            for line in f:
                # Call string misspeller for each line
                out_text += misspell_string(line, mode=mode, config=config,
                                            silent=silent)
    except FileNotFoundError:
        raise FileNotFoundError("input file " + fin + " not found")
        return None
    
    # Write output string to a file or print to the screen
    if fout == None:
        print('\n' + '>'*10 + '\n' + out_text)
    else:
        with open(fout, 'w') as f:
            f.write(out_text)
            if silent == False:
                print("Output file '" + fout + "' written.")

#=============================================================================
# Command line usage
#=============================================================================

if __name__ == "__main__":
    ###
    # Parse command line arguments
    # If help or version is requested, just print that and quit
    # If a custom INI file is requested, read that first
    # Finally move on to processing the input string or file
    # If given a string we need to manually run misspell_string() and print
    # the result here.
    ###
    ###misspell_file("text/cthulhu.txt", mode=2)
    _default_config()
