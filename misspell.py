###
# Include functions which can act on either words, strings of text, or files.
# String functions should return strings, while file functions should write files.
# Also include the ability for this module to accept command line arguments for input/output file names or for a single input string.
# Include some parameters to adjust the extent of misspelling, and include a few different types of misspelling that can occur, like transposing letters or ADD/DROP/SWAP moves.
# Possibly include a config file to allow the user to easily adjust parameters. Python includes methods for reading and writing INI files in the configparser module. While running this script, we should first define default values for all parameters, then check to see whether a local (and compatible) config file exists. If so, we overwrite the default parameter values, and if not, we attempt to write one initialized with the default values. Include the default config file in the repo.

###
# Try to make the resulting words "pronounceable" by applying some phonotactic rules.
# Words are made up of syllables, and each syllable can be divided into an onset, a nucleus, and a coda.
# English is a (C)(C)(C)V(C)(C)(C)(C)(C) language, meaning that the onset can contain 0-3 consonant sounds, the nucleus must contain a single vowel sound, and the coda can contain 0-5 consonant sounds.
# Occasionally English can allow a syllabic consonant as its nucleus, usually L, R, M, or N.
# There can also be additional phonotactical rules forbidding certain sounds from occurring consecutively. This can be done by making a table of every possible pair of sounds to specify which pairs are or are not allowed (or maybe even a degree of how allowable they are).

###
# One possible method would be to begin by converting any given word into an estimated pronunciation and syllable grouping, and then work on manipulating the phonetic symbols, and then convert the result back into a plain English spelling.
# A simple first approximation of syllable grouping would be to simply break the word into right-grouped (C)V(C) clusters. Specifically, take the first syllable to be everything up to and including the first C cluster which follows the first V cluster, and take every following syllable to be the alternating VC clusters.

"""A Python module for slightly misspelling strings and text files.

This module defines a number of functions for converting strings and text
files into slightly misspelled versions of themselves.

If imported, these functions can be called directly. The following is a
summary of the public functions:
    misspell_string(str) -- returns a misspelled version of a given string
    misspell_file(str[, str]) -- writes a misspelled version of a given input
        file (or prints to screen if no output is given)

This script can also be called from the command line using the following
format:
    $ python misspell.py str [str]
where the arguments, in order, are:
    1 -- input file name
    [2] -- optional output file name (if absent, output is printed to screen;
        if present, the specified file is written)
"""

import random
import re
import sys

#=============================================================================
# Public functions
#=============================================================================

def misspell_string(s):
    """misspell_string(str) -> str
    Returns a misspelled version of a given string.
    
    Positional arguments:
    s (str) -- string to be misspelled
    
    Returns:
    str -- misspelled version of string
    """
    
    # Validate input
    if type(s) != str:
        raise TypeError("input must be a string")
    
    # Translate line-by-line and word-by-word
    out_text = "" # complete output string
    for line in s.split('\n'):
        out_line = "" # complete line of output string
        line_part = re.split(r'(\s+)', line) # word and whitespace clusters
        for word in line_part:
            # Include whitespace as-is
            if word.isspace() == True:
                out_line += word
            # Process text
            else:
                out_line += _misspell_word(word)
        out_text += out_line + '\n'
    
    return out_text

#-----------------------------------------------------------------------------

def misspell_file(fin, fout=None):
    """misspell_file(str[, str]) -> None
    Writes a misspelled version of a given text file.
    
    Attempts to read a text file and misspell each word one-by-one. The result
    is either written to a separate text file or printed to the screen.
    
    Positional arguments:
    fin (str) -- input file name
    [fout=None] (str) -- output file name (or None to print to screen)
    """
    
    # Validate inputs
    if type(fin) != str:
        raise TypeError("input argument must be a file name string")
    if type(fout) != str and fout != None:
        raise TypeError("output argument must be a file name string or None")
    
    try:
        with open(fin, 'r') as f:
            # If file is found, translate line-by-line
            out_text = "" # complete output string
            for line in f:
                out_text += misspell_string(line)
    except FileNotFoundError:
        raise FileNotFoundError("input file " + fin + " not found")
        return None
    
    # Write output string to a file or print to the screen
    if fout == None:
        print(out_file)
    else:
        with open(fout, 'w') as f:
            f.write(out_text)

#=============================================================================
# Private parameters
#=============================================================================

###
# Define any needed tables or rules for breaking syllables.

# Define letter types
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

#=============================================================================
# Private functions
#=============================================================================

def _misspell_word(w):
    """_misspell_word(str) -> str
    Misspells a single word string.
    
    This function is called repeatedly by the main drivers above to misspell
    each individual word in the master string. The input is assumed here to
    consist entirely of a string of characters.
    
    Positional arguments:
    w (str) -- single word to be misspelled
    
    Returns:
    str -- misspelled version of word
    """
    
    ###
    # Steps:
    # Attempt to acquire capitalization
    # Attempt to split into syllables by guessing the break points
    # Convert each syllable individually
    # Combine syllables
    # Apply post-processing (like possibly transposing consonants)
    # Return the result
    
    ###
    return w

#-----------------------------------------------------------------------------

def _misspell_syllable(s):
    """_misspell_syllable(str) -> str
    Misspells a single syllable.
    
    The smallest unit of the recursive misspelling scheme. The input is
    assumed here to consist entirely of a string of characters.
    
    Positional arguments:
    s (str) -- syllable to be misspelled
    
    Returns:
    str -- misspelled syllable
    """
    
    ###
    # Steps:
    # Attempt to acquire capitalization
    # Apply misspelling rules
    # Return the transformed result
    
    ###
    return s

#=============================================================================
# Command line usage
#=============================================================================

if __name__ == "__main__":
    #for (i, arg) in enumerate(sys.argv):
    pass
