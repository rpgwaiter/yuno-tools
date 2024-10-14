# Tools to analyze, decompile and recompile YU-NO from the early windows "elf classics" release of the game.

## Background

YU-NO is a PC-98 game published by the now defunct Elf corporation. At some point point, Elf re-released the game for early versions of Windows. This port of the game includes multiple seemingly custom archive and file formats. These include .ARC files (not related to any documented archive format), and .GP8 images (similar to .bmp).

The tools in this repo are meant to aid in reverse engineering YU-NO (and the other games included in Elf Classics I guess) for the purpose of porting and translating.

My intention with these is to eventually port the game to the web, allowing more people to experience one of my favorite games.

## TODO (tools)
- Windows build
- Linux install script for yu-no
- Make my own translation patch script
- Some helper scripts to unpack/repack the *entire* game install in-place
- Conversion tools to modern web formats

## TODO (reverse engineering)
- Figure out .S4 files
- Figure ous .MES files
- There is track looping info embedded in the .WAV files in some non-standard way. I need to extract these for porting
- What's up with zBG, zDATA, zMES?
- Hook the music libraries to support .opus or .flac (much smaller sizes)

## Credits

The bulk of custom format reversing was done by some friendly people on the defunct TLWiki forums. Primarily `kingshriek` who seems to not currently have much of an internet presence. These were released originally without a license, so hopefully the original author doesn't mind me continuing their work.