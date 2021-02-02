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
    -u, --usage             equivalent to --help
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
import random
import re

#=============================================================================
# Global parameters
#=============================================================================

# Define global constants
_VERSION="""Slight Misspeller v1.0.0
         Copyright (c) 2021 Adam Rumpf <adam-rumpf.github.io>
         Released under MIT license <github.com/adam-rumpf/slight-misspeller>
         """
_VOWELS = "aeiou"
_CONSONANTS = "bcdfghjklmnpqrstvwxyz"
_GROUPS = ("ch", "gh", "ph", "sh", "th", "ng", "qu") # letters to group
_ALLOW_CBLENDS = ("scr", "spl", "spr", "str") # allowed three-letter consonant
                                              # blends
### syllable onset whitelist
_ALLOW_ONSETS = () # allowed syllable onsets
### use for a final pass to delete such pairs
_FORBID_PAIRS = ("ii", "jj", "kk", "qq", "vv", "ww", "xx", "yy")
                                          # forbidden consecutive letter pairs

# Initialize global parameters to be defined in the config file
_CONFIG = "settings.ini" # currently-loaded config file name
_BLACKLIST = () # words to prevent the program from accidentally creating
_DELETE_SPACE = 0.005 # chance to delete any given whitespace character
_DELETE_CHAR = 0.0075 # chance to delete any given non-whitespace character
_TYPO_SWAP = 0.0075 # chance to swap consecutive characters

### Other parameters:
### Typographical: extra adjacent letter, replacement adjacent letter
### Phonological: onset replacement, nucleus replacement, coda replacement, transpositions

#=============================================================================
# Argument parser outputs
#=============================================================================

### output functions for help and version

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
                if random.random() < 1.0 - _DELETE_SPACE:
                    w0 += c
        return w0
    
    # Apply phonological rules
    w1 = w # post-phonological misspelling string
    if mode in {0, 1}:
        # Split string into consonant/vowel/punctuation clusters
        s = [x for x in re.split("(["+_VOWELS+"]+)|(["+_CONSONANTS+"]+)",
             w1, flags=re.IGNORECASE) if x]
        
        ###
        print(s)
        pass
    
    # Apply typographical rules
    w2 = "" # post-typographical misspelling string
    if mode in {0, 2}:
        ###
        # Chance to randomly delete non-whitespace characters
        for c in w1:
            if random.random() < 1.0 - _DELETE_CHAR:
                w2 += c
    
    ###
    # Steps:
    # Attempt to acquire capitalization
    # Attempt to split into syllables by guessing the break points
    # Convert each syllable individually
    # Combine syllables
    # Apply post-processing (like possibly transposing consonants)
    # Apply typographical misspelling rules
    # Return the result
    
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

def _read_config(f, silent=False):
    """_read_config(f[, silent])
    Reads an INI file to set or reset parameters.
    
    Reading a config file updates a variety of internal parameters, which
    remain unchanged until a new config file is read. Attempting to read the
    most recent config file a second time has no effect.
    
    Positional arguments:
    f (str) -- config file name
    
    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Global parameters to be edited
    global _CONFIG, _BLACKLIST, _DELETE_SPACE, _DELETE_CHAR, _TYPO_SWAP
    
    # Validate input
    if type(f) != str:
        raise TypeError("input argument must be a config file name string")
        return None
    
    # Quit if config file has already been read
    if _CONFIG == f:
        return None
    
    # Read INI file and set (or reset) parameters
    if silent == False:
        print("Reading config file '" + f + "'.")
    try:
        try:
            ### read fields one-by-one
            ### include input validation for each individual field
            pass
        except KeyError:
            ### print a message which specifies the key that does not exist
            key = "temp"###
            if silent == False:
                print("Key " + key + " not found in '" + f + "'.")
                print("Reverting to default parameters.")
            return _default_config(silent=silent)
    except FileNotFoundError:
        raise FileNotFoundError("config file " + f + " not found")
        return None

#-----------------------------------------------------------------------------

def _default_config(silent=False):
    """_default_config([silent])
    Sets default parameters and writes the default config file.
    
    Keyword arguments:
    [silent=False] (bool) -- whether to print progress messages to the screen
    """
    
    # Global parameters to be edited
    global _CONFIG, _BLACKLIST, _DELETE_SPACE, _DELETE_CHAR, _TYPO_SWAP
    
    ### All parameters should be set here, and then the config file should be written based on them
    # If not silent, print a message whenever the file is successfully created, and mention that it can be copied and edited for custom settings.
    _CONFIG = "settings.ini"
    pass

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
            ### search out_line for the word; if present, delete one of the final letters from it (starting position offset by word length) and re-scan, moving on only WHILE the word is still present
            pass
                    
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
        print('>'*10 + '\n' + out_text)
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
    ###
    ###misspell_file("text/cthulhu.txt")
    misspell_string("This... is an example, see?", mode=1)
