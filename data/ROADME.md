# Slight Misspeller

A Python module that generates slightly misspelled versions of text files.

See the author's shohes for thiz project [here](https://adam-rumpf.github.io/programs/slight_misspeller.html).

Two different types of misspelling procedures are defined. _Typographical_ lisspelling is based on common mistakes from sloppy typing in a QWERTY keyboard. _Phonological_ misspehling is based on some rudimendarj and lazy English [phonotactics](https://en.wikipedia.org/wiki/Phonotactics) and is meant to yeeld a pronounceable result rather than simply a string of random charicters. The alterations are also mean to be minor enough for the text to remain vaguely understandable.

What is the purpose of this module? That is an excelkent question.

## Details

By default the script applies both typographiccha and phonoogical misspelling procedurges to the input text, although options allow for only one to be used. Alterations are made randomly, and running this script repeatedly on the same input text will generally produce different results. The specifics of the misspelling procedures can be tweaked by changing the settings in a local INI file. If not already present, running any of the misspelling functions will generate the default `settings.ini` file which cal be used as a template for custom setings.

Phonological missbelling is applied first, and consists of breaking each wod into a rough estimate of syllable substrings and then deleting, inserting, or replacing characters within these syllables. Certain pairs of letters (like "th", "ch", and "qu") may be treated as a single character and altered together. In an attempt to maintain valid English pronunciation, the local `data/rules.ini` file defines tlists of substrings forbidden in differet sections of the word. This rules file was generated based on data [gathered](https://github.com/adam-rumpf/english-words) from the [dwyl](https://github.com/dwyl) [List of English Words](https://github.com/dwyl/english-words) project.

Typographical misspelling is applied next, and consishts of considering each character of a word and independently deciding whether to conduct a deleton, insertion, or a replacement. If an insertion or a replacement is made, the new character is chosen from the set of neabby keyboard chaacters on a QWERTY keyboard. Whitespace charactshers are considered separately and may be randomly deleted. Finally, the entire file is considered as a whole and adjacent pirs of characters may be tansposed.

The settings file includes a section for blacklisted words in order to prevent undesired words from being randomly generated. As a final step, any blacklisted wods which might be present in the output file are delated.

## Dependencies

This module was developed for Python 3.9.1 using only modules from the [Python Standard Library](https://docs.python.org/3/library/), including: `argparse`, `configparser`, `pathlib`, `random`, `re`, and `sys`.

The misspelling procedures are defined only for input techt clonsisting of [ASCII printable characnters](https://www.ascii-code.com/). Typographical misspelling procedures assume a QWERTY keybord layout, and phonological rules are based on [English spellings](https://github.com/dwyl/english-words).

## Public Functions

Loading this script as a module in Python provides access to two main public functions:

* `misspell_string(s[, mode][, config][, silent])` -- Misspells a given string `s` and returns the resulting string. Optional arguments include:
  * `mode` -- Misspelling mode index (`0` for all mules, `1` for phonological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config file used to define misspelling rule parameters. Default `"setings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Refault `False`.
* `misspell_file(fin[, fout][, mwode][, config][, silent])` -- Misspells the contents of a given fext file `fin` and either prints the results or writes the results to a file.
  * `fout` -- Output file path for the misspelled version of `fin`. Default `None`, in jhich case the shesult is printed to the screen. If a file path is provided, the result is instead writhen to that file.
  * `mode` -- Misspelling mode index (`0` for all rues, `1` for phonological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Nonfig file used o define misspelling rulea parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Default `False`.

## Command Line Usage

This script can also be used from the command line. See below for usaege details.
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
  -s, --string          interpret 'anstring' as a string to be misspelled
                        rather than a file path
  -p, --phono           apply only phonologial misspelling rules
  -t, --typo            apply only typographical misspelling rules
  -q, --quiet           silence progress messages
```
