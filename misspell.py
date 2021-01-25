# Include functions which can act on either words, strings of text, or files.
# String functions should return strings, while file functions should write files.
# Also include the ability for this module to accept command line arguments for input/output file names or for a single input string.
# Include some parameters to adjust the extent of misspelling, and include a few different types of misspelling that can occur, like transposing letters or ADD/DROP/SWAP moves.
# Possibly include a config file to allow the user to easily adjust parameters. Python includes methods for reading and writing INI files.

# Try to make the resulting words "pronounceable" by applying some phonotactic rules.
# Words are made up of syllables, and each syllable can be divided into an onset, a nucleus, and a coda.
# English is a (C)(C)(C)V(C)(C)(C)(C)(C) language, meaning that the onset can contain 0-3 consonant sounds, the nucleus must contain a single vowel sound, and the coda can contain 0-5 consonant sounds.
# Occasionally English can allow a syllabic consonant as its nucleus, usually L, R, M, or N.
# There can also be additional phonotactical rules forbidding certain sounds from occurring consecutively. This can be done by making a table of every possible pair of sounds to specify which pairs are or are not allowed (or maybe even a degree of how allowable they are).

# One possible method would be to begin by converting any given word into an estimated pronunciation and syllable grouping, and then work on manipulating the phonetic symbols, and then convert the result back into a plain English spelling.
