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

###
# Command line options to support:
# --help, -h, --usage, -u
# --version, -v ("Slight Misspeller v0.1.0")
# --quiet, -q, --silent, -s (suppress progress messages) (may or may not include, since it could be tricky to suppress all possible errors; alternatively just suppress custom progress messages, by giving a "silent" argument to all functions)
# --init-file, -i (along with an option to select a custom INI file)
# --text, -t (interpret the first argument as a string to be converted, rather than a file name; in either case, if there's a second argument it's interpreted as the output specifier [file name or blank to print])

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
    $ python misspell.py [-i INIT_FILE] <in> [<out>]
where:
    <in>        name of input text file (or raw string to be converted, if
                --text flag is set)
    [<out>]     name of output text file (if left blank, result is printed to
                screen)
    INIT_FILE   name of custom INI file to define parameters (defaults to
                "settings.ini", which this program automatically generates if
                not present)

Command line options include the following:
    -h, --help              display help message and exit
    -u, --usage             equivalent to --help
    -v, --version           display version info and exit
    -t, --text              interpret first argument as a raw input string
                            rather than an input file name
    -i, --init-file=STRING  specifies a custom INI file to define parameters
                            (default "settings.ini", which this program
                            automatically generates if not present)
    -s, --silent            suppress progress messages
    -q, --quiet             equivalent to --silent
"""

import argparse
import configparser
import random
import re

#=============================================================================
# Global parameters
#=============================================================================

###
# Define any needed tables or rules for breaking syllables.

# Define global constants
_CONFIG = "settings.ini" # config file with default parameter values
_VOWELS = tuple("aeiou")
_CONSONANTS = tuple("bcdfghjklmnpqrstvwxyz")
_GROUPS = ("ch", "gh", "ph", "sh", "th", "ng", "qu") # letters to group
_ALLOW_CBLENDS = ("scr", "spl", "spr", "str") # allowed three-letter consonant
                                              # blends
### syllable onset whitelist
_ALLOW_ONSETS = () # allowed syllable onsets
### use for a final pass to delete such pairs
_FORBID_PAIRS = ("aa", "ii", "jj", "kk", "qq", "uu", "vv", "ww", "xx", "yy")
                                          # forbidden consecutive letter pairs

# Initialize global parameters to be set in config file
### use for a final pass to prevent certain words from being randomly created
_FORBID_WORDS = () # words to prevent the program from accidentally creating

#=============================================================================
# Argument parser outputs
#=============================================================================

### output functions for help and version

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

#-----------------------------------------------------------------------------

def _read_config(f):
    """_read_config(str) -> None
    Reads an INI file to set or reset parameters.
    
    Positional arguments:
    f (str) -- config file name
    """
    
    # Global parameters to be edited
    global _FORBID_WORDS
    
    # Validate input
    if type(f) != str:
        raise TypeError("input argument must be a config file name string")
    
    # Read INI file and set (or reset) parameters
    try:
        try:
            ### read fields one-by-one
            ### include input validation for each individual field
            pass
        except KeyError:
            ### print a message which specifies the key that does not exist
            key = "temp"###
            print("Key " + key + " not found in " + f + ".")
            print("Reverting to default parameters.")
            return _default_config()
    except FileNotFoundError:
        raise FileNotFoundError("config file " + f + " not found")
        return None

#-----------------------------------------------------------------------------

def _default_config():
    """_default_config() -> None
    Sets default parameters and writes the default config file.
    """
    
    # Global parameters to be edited
    global _FORBID_WORDS
    
    ### All parameters should be set here, and then the config file should be written based on them
    # If not silent, print a message whenever the file is successfully created, and mention that it can be copied and edited for custom settings.
    pass

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
    
    return out_text[:-1]

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
        print(out_text)
    else:
        with open(fout, 'w') as f:
            f.write(out_text)

#=============================================================================
# Command line usage
#=============================================================================

if __name__ == "__main__":
    ###
    # Parse command line arguments
    # If help or version is requested, just print that and quit
    # If a custom INI file is requested, read that first
    # Finally move on to processing the input string or file
    pass
