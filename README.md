# Slight Misspeller

A Python module that generates slightly misspelled versions of text files.

Two different types of misspelling procedures are defined. _Phonological_ misspelling is based on some rudimentary and lazy English [phonotactics](https://en.wikipedia.org/wiki/Phonotactics) and is meant to yield a pronouncable result rather than simply a string of random characters. _Typographical_ misspelling is based on common mistakes from sloppy typing on a QWERTY keyboard. The alterations are also meant to be minor enough for the text to remain vaguely understandable.

The specifics of the misspelling procedures can be tweaked by changing the settings in a local `.ini` file. If not already present, running any of the misspelling functions will generate the default `settings.ini` file which can be used as a template for custom settings.

What is the purpose of this module? That is an excellent question.

## Public Functions

Loading this script as a module provides access to two main public functions:

* `misspell_string(s[, mode][, config][, silent])` -- Misspells a given string `s` and returns the resulting string. Optional arguments include:
  * `mode` -- Misspelling mode index (`0` for all rules, `1` for phonological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config file used to define misspelling rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Default `False`.
* `misspell_file(fin[, fout][, mode][, config][, silent])` -- Misspells the contents of a given text file `fin` and either prints the results or writes the results to a file.
  * `fout` -- Output file path for the misspelled version of `fin`. Default `None`, in which case the result is printed to the screen. If a file path is provided, the result is instead written to that file.
  * `mode` -- Misspelling mode index (`0` for all rules, `1` for phonological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config file used to define misspelling rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Default `False`.

## Command Line Usage

This script can also be used from the command line. See below for usage details.
```
usage: misspell.py [-h] [-v] [-i CONFIG] [-s] [-p | -t] [-q]
                   instring [outstring]

Slightly misspells a string or file.

positional arguments:
  instring              input file (or string, with the --string tag)
  outstring             output file (leave empty to print result to screen)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -i CONFIG, --init-file CONFIG
                        misspeller parameter config file
  -s, --string          interpret 'instring' as a string to be misspelled
                        rather than a file path
  -p, --phono           apply only phonological misspelling rules
  -t, --typo            apply only typographical misspelling rules
  -q, --quiet           silence progress messages
```
