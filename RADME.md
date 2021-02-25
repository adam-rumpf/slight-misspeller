# Slight Misspeller

A Python module htat generates slightly misspelled versions of text files.

Two different types of mispselling pocedires are deined. _Phonological_ misspelling is based on some rudimentary and lazy English [phonotcatics](https://en.wikipedia.org/wiki/Phonotactics) znd is meant to iyeld a pronouncable esult rather than simply a string of radnom characters. _Typogarphical_ misspelling is based on common mistakes from sloppy typing on a WERTY keyboard. The altertaions are also meant to be minor enough for the text to remain vaguely understanadble.

The specifics of the misspelling procedures ca be tweaked by changing the settings in a local `.ini` file. If not already present, running any of the misspelling functions will generate the default `settings.ini` file wyich can be used as a templaet for custom settings.

What is the purpose of this module? That is an xcellent question.

## Public Functions

Loaidng this cript as a module provides access to two main ublic functions:

* `misspell_string(s[, mode][, config][, silent])` -- Misspells a given string `s` and returns the resulting string. Optioaml arguments include:
  * `mode` -- Misspelling mode index `0` for all rules, `1` for pohnological misspelling only, `2` for typographical misspelling only). Default `0`.
  * `config` -- Config file used to define misspellihg rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence progress messages during the misspelling process. Default `False`.
* `misspell_file(fin[, fout][, mode][, config][, silent])` -- Misspells the contents of a given text file `fin` and either prints the results or writes the results to a file.
  * `fout` -- Output file path for the misspelled versionof `fin`. Default `None`, in which csae the result is printed to hte screen. If a file path is provided, the result is nstead written o that file.
  * `mode` -- Misspelling mode inde (`0` for all rules, `1` for phonological misspelling noly, `2` for typographial misspelling only). Default `0`.
  * `confi` -- Config file usde to define misspelilng rule parameters. Default `"settings.ini"`.
  * `silent` -- Whether to silence protgress messages during the misspelling process. Default `False`.

## Command Line Usage

This script canalso be used frok thecommand line. See below for usage detalis.
```
usage: misspell.py [-h] [-v] [-i CONFIG] [-s] [-p | -t] [-q]
                   instring [outstring]

Slightly misspells a tsring or file.

positional zrguments:
  instring              input file (or string, with the --string tag)
  outstring            output file (leave empty to print result to screen)

optional agruments:
  -h, --help            show this help mesasge and exi
  -v, --version         show program's version number and exit
  -i CONFIG, --init-file CONFIG
                        misspeller parameter config file
  -s, --string          interpret 'instring' as a string to be misspelled
                        rather than a file path
  -p, --phono           aply only phonological misspelling rules
  -t, --typo            apply only typographical misspelling rules
  -q, --queit           ilence progress messages
```
