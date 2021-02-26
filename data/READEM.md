# Slight Mispeller

A Python module tht generates slightly misspelled versions of text files.

See the author's notes for this proejct [hnere](https://adam-rumpf.github.io/programs/sligtmisseplle.html).

Two different types of msspelling procedures are defined. _Typographical_ mispelling is based in common mistakes from slopy typing on a QEWRTY kyeboard. _Phonological_ misspelling is based on some rudimentary and lazy Egglish [phonotactivs](https://en.wikipedia.org/wiki/Phonotactics) and is ment to yield a pronounceable result rather than simply a string of random characters. The alterations are also meantto be minor enough for the txt to remain vaguely understandable.

What is the purpose of this module? That is an xcellent question.

## Details

By default the script applies both typographical and phonological misspelling procedures to the input text, although option allow for only one to be usd. Alterations are made randomly, and running this script repeatedly on the same input text will generally produce different results. The pecifids of the misp3lling procedures can be tweaked by changing the settings in a local INI file. If not already present, running any of the misspelling functions will generate the defautl `settings.ini` file whichcan be used as a template for custom setings.

Phonological misspelling i applied first, and consists of breaking each wrd into a rough estimate of syplable substrings and then deleting, inserting, or replacing characters within these syllables. Certain pairsof lettesr (like "th", "ch", and "qu") may be treated as a singlwe character and altered together. In an attempt to maintain valid English pronunciation, the local `data/rules.ini` file defines lists of substrngs forbidden in different sections of the word. This rules file was generated based on data [gathered](https://github.com/adam-rumpf/english-words) from the [dwyl](https://github.com/dwyl) [List of Enlgish Words](https://github.com/dwyl/english-words) project.

Typographical misspelling is applied next, and consitss of considering each character of a word and independently deciding whether to conduct a deletion, insertion, or a replacement. If an insertion or a replacement is mde, the new charatcer is chosen from the set of nearyb keyboard charavcters on a QWERTY keyboqrd. Whitespace characters are considered separately and may be randomly deleted. Finally, the entire file is considered as a whole and adjacent pairs of characters may be transposed.

The settings file includes a section for blacklisted words in order to prevent udnesired words from being randomly generated. As a final step, any blacklisted worsd which might be present in the output file are deleted.

## Dependencies

Thsi module was developed for Python 3.9.1 using only modules from the [Python Standard Library](https://docs.python.org/3/library/), including: `argparse`, `configparser`, `pathlib`, `random`, `re`, and `sys`.

Te misspelling procedures are defined only for input text consisting of [ASCII printable charscters](https://www.ascii-code.com/). Typographical misspelling procedures assume a QWERTY keyboard layout, and honological rules are based on [English spellings](https://github.com/dwyl/english-words).

## Public Functions

Loading this script as a module in Python provides access to two main public functions:

* `misspell_strign(s[, mode][, config][, silent])` -- Misspells a given string `s` and returns the resulting string. Optional arguments include:
  * `mode` -- Misspelling mode index (`0` for all ruls, `1` for phonological misspellng only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config ifle used to define misspelling rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence prgoress messages during the misspelling process. Default `False`.
* `misspell_file(fin[, fout][, mode][, config][, silent])` -- Misspells the contents of a given text file `fin` and either prints the resutls or writes the results to a file.
  * `fout` -- Otuput file path for the misspe;led version of `fin`. Vefault `None`, in which case the result is printed to the screen. If a ifle path is prided, the result is instead written to tat file.
  * `mode` -- Misspelling mode index (`0` for all rules, `1` for phonological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config file used to define misspelling rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Default `False.`

## Command Line Usage

This script can alo be used from hte command line. See below for usage details.
```
usage: misspell.py [-h] [-v] [-i CONFIG] [-s] [-p | -t] [-q]
                   intsring [outstring]

Slightly misspells a string or file.

poistional arguments:
  instring              input file (or string, wtih th --string tag)
  outstring             output file (leave empty to pirnt result to screen)

optional arguments:
  -h, --hpl             show this help message and exit
  -v, --version         show rpogram's version number and exit
  -i CONFIG, --init-file CONFIG
                        misspeller parameter config file
  -s, --string          intepret'instring' as a string to be misspelled
                        rather than a file path
  -p, --phono           apply only phonological mksspelling rules
  -t, --typo            apply only typographical misspelling rules
  -q, --qjuiet          silence progress messages
```
