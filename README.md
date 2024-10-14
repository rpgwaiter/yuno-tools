# Tools to analyze, decompile and recompile YU-NO from the early windows "elf classics" release of the game.

## Background

YU-NO is a PC-98 game published by the now defunct Elf corporation. At some point point, Elf re-released the game for early versions of Windows. This port of the game includes multiple seemingly custom archive and file formats. These include .ARC files (not related to any documented archive format), and .GP8 images (similar to .bmp).

The tools in this repo are meant to aid in reverse engineering YU-NO (and the other games included in Elf Classics I guess) for the purpose of porting and translating.

My intention with these is to eventually port the game to the web, allowing more people to experience one of my favorite games.

## TODO
- Windows build
- Linux install script for yu-no
- Some helper scripts to unpack/repack the *entire* game install in-place
- Conversion tools to modern web formats


## Credits

The bulk of this reversing work was done by some friendly people on the defunct TLWiki forums. Primarily `kingshriek` who seems to not currently have much of an internet presence. These were released originally without a license, so hopefully the original author doesn't mind me continuing their work.