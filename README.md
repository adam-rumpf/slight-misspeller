# Slight Misspeller

<a href="https://github.com/adam-rumpf/slight-misspeller/search?l=python"><img src="https://img.shields.io/badge/language-python-blue?style=plastic&logo=python&logoColor=white"/></a> <a href="https://github.com/adam-rumpf/slight-misspeller/releases"><img src="https://img.shields.io/github/v/release/adam-rumpf/slight-misspeller?style=plastic"/></a> <a href="https://github.com/adam-rumpf/slight-misspeller/blob/master/LICENSE"><img src="https://img.shields.io/github/license/adam-rumpf/slight-misspeller?style=plastic"/></a> <a href="https://github.com/adam-rumpf/slight-misspeller/commits/master"><img src="https://img.shields.io/maintenance/no/2021?style=plastic"/></a>

A Python module that generates slightly misspelled versions of text files.

See the author's notes for this project [here](https://adam-rumpf.github.io/programs/slight_misspeller.html).

Two different types of misspelling procedures are defined. _Typographical_ misspelling is based on common mistakes from sloppy typing on a QWERTY keyboard. _Phonological_ misspelling is based on some rudimentary and lazy English [phonotactics](https://en.wikipedia.org/wiki/Phonotactics) and is meant to yield a pronounceable result rather than simply a string of random characters. The alterations are also meant to be minor enough for the text to remain vaguely understandable.

What is the purpose of this module? That is an excellent question.

## Details

By default the script applies both typographical and phonological misspelling procedures to the input text, although options allow for only one to be used. Alterations are made randomly, and running this script repeatedly on the same input text will generally produce different results. The specifics of the misspelling procedures can be tweaked by changing the settings in a local INI file. If not already present, running any of the misspelling functions will generate the default `settings.ini` file which can be used as a template for custom settings.

Phonological misspelling is applied first, and consists of breaking each word into a rough estimate of syllable substrings and then deleting, inserting, or replacing characters within these syllables. Certain pairs of letters (like "th", "ch", and "qu") may be treated as a single character and altered together. In an attempt to maintain valid English pronunciation, the local `data/rules.ini` file defines lists of substrings forbidden in different sections of the word. This rules file was generated based on data [gathered](https://github.com/adam-rumpf/english-words) from the [dwyl](https://github.com/dwyl) [List of English Words](https://github.com/dwyl/english-words) project.

Typographical misspelling is applied next, and consists of considering each character of a word and independently deciding whether to conduct a deletion, insertion, or a replacement. If an insertion or a replacement is made, the new character is chosen from the set of nearby keyboard characters on a QWERTY keyboard. Whitespace characters are considered separately and may be randomly deleted. Finally, the entire file is considered as a whole and adjacent pairs of characters may be transposed.

The settings file includes a section for blacklisted words in order to prevent undesired words from being randomly generated. As a final step, any blacklisted words which might be present in the output file are deleted.

## Dependencies

This module was developed for Python 3.9.1 using only modules from the [Python Standard Library](https://docs.python.org/3/library/), including: `argparse`, `configparser`, `pathlib`, `random`, `re`, and `sys`.

The misspelling procedures are defined only for input text consisting of [ASCII printable characters](https://www.ascii-code.com/). Typographical misspelling procedures assume a QWERTY keyboard layout, and phonological rules are based on [English spellings](https://github.com/dwyl/english-words).

## Public Functions

Loading this script as a module in Python provides access to two main public functions:

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

## Examples

_Excerpt from [The Masque of the Red Death](https://poestories.com/read/masque), Edgar Allan Poe, 1850._

Suppose we have the following text file `masque.txt`:
```
THE "Red Death" had long devastated the country. No pestilence had ever been
so fatal, or so hideous. Blood was its Avator and its seal -- the redness and
the horror of blood. There were sharp pains, and sudden dizziness, and then
profuse bleeding at the pores, with dissolution. The scarlet stains upon the
body and especially upon the face of the victim, were the pest ban which
shut him out from the aid and from the sympathy of his fellow-men. And the
whole seizure, progress and termination of the disease, were the incidents of
half an hour. 
```
We can apply typographical misspelling from within the Python shell using `misspell_file("masque.txt", mode=2)`, or from the command line as follows:
```
$ python3 misspell.py masque.txt --typo --quiet

>>>>>>>>>>

THE "Red Death" had long devastated the country.No pestilence had ever been
so fatal, or so hideous. Blood was its Avator and its seal -- the redness an
the horror of blood. There were sharp pians, and sudden dizziness, and then
profuse bleednig at the pores, with dissoultion. The scarlet stains upon the
body and especially upon the face of the victim, were the pest ban which
shut him out from the aid and from the sympathy of his fellow-men. Andthe
whole seizure, progress and termination of the disease, were the incidents of
hal n hour.
```
Similarly, we can apply phonological misspelling using `misspell_file("masque.txt", mode=1)` or:
```
$ python3 misspell.py masque.txt --phono --quiet

>>>>>>>>>>

THE "Red Death" had long devastated thi country. No pestilence had ever been
so fatal, or so hideous. Blood was its Avator and its seal -- the redness and
the horror of blood. There were sharp pains, and sutden dizziness, and then
profuse bleeding at the pores, with dissolution. The scarlet stains upon the
bodshy and especiually upon the face of the victim, ware the pest ban which
shut him out from the aid and from the sympathy of his fellow-men. And the
whole seizure, progres and termination of the disease, were the incidents of
half an hour.
```
