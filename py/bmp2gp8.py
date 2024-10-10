#! /usr/bin/env python
#
# Yu-No windows ver. BMP-to-GP8 image converter
#

import io
import os
import re
import glob
import fnmatch
import struct
import optparse
import sys

version = "%prog 0.6"


def read_pos(fp, fname):
    for rawline in fp.readlines():
        line = rawline.strip()
        if not line:
            continue
        elems = line.split()
        gname = os.path.splitext(fname)[0] + ".GP8"
        if gname.upper() == elems[0].upper():
            xpos = int(elems[2])
            ypos = int(elems[4])
            return xpos, ypos
    raise Exception("%s entry not found in gp8 position file" % fname)


def read_bmp_hdr(fi):
    if fi.read(2) != b"BM":
        raise Exception("bad magic number (not a BMP file?)")
    fi.seek(8, os.SEEK_CUR)
    offset = struct.unpack("<I", fi.read(4))[0]
    nhdr = struct.unpack("<I", fi.read(4))[0]
    if nhdr != 40:
        raise Exception("header size should be 40")
    width, height = struct.unpack("<II", fi.read(8))
    if fi.read(2) != b"\x01\x00":
        raise Exception("number of color planes not 1")
    if fi.read(2) != b"\x08\x00":
        raise Exception("not a 8-bit BMP")
    fi.seek(16, os.SEEK_CUR)
    npal = struct.unpack("<I", fi.read(4))[0]
    if npal > 0x100:
        raise Exception("palette should have no more than 256 entries")
    fi.seek(4, os.SEEK_CUR)
    return offset, width, height, npal


def lazy_compress(fo, fi):
    while 1:
        data = fi.read(8)
        if not data:
            break
        fo.write(b"\xff")
        fo.write(data)


def bmp2gp8(fo, fi, xpos, ypos):
    offset, width, height, npal = read_bmp_hdr(fi)
    fo.write(struct.pack("<HHHH", xpos, ypos, width, height))
    palette = fi.read(npal * 4) + b"\x00" * (1024 - npal * 4)
    fo.write(palette)
    fi.seek(offset, os.SEEK_SET)
    lazy_compress(fo, fi)


def main():
    usage = "usage: %prog [options] <input_dir> <output_dir>"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option(
        "-f",
        "--file",
        dest="file",
        default="*",
        help="process specific file named FILE (Unix-style wildcards accepted)",
    )
    parser.add_option(
        "-r",
        "--regex",
        dest="regex",
        default=".+",
        help="filter processed files using REGEX",
    )
    parser.add_option(
        "-p",
        "--posfile",
        dest="posfile",
        default="gp8pos.txt",
        help="gp8 position file (default %default)",
    )
    parser.add_option(
        "-R",
        "--recurse",
        action="store_true",
        dest="recurse",
        help="recurse through subdirectories",
    )
    parser.add_option(
        "-H",
        "--half-recurse",
        action="store_true",
        dest="hrecurse",
        help="recurse through subdirectories but leave output directory flat",
    )
    parser.add_option(
        "-v", "--verbose", action="store_true", dest="verbose", help="verbose output"
    )
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.error("incorrect number of arguments")

    if not os.access(args[1], os.F_OK):
        os.mkdir(args[1])
    if options.recurse or options.hrecurse:
        for dirpath, dirnames, filenames in os.walk(args[0]):
            for ifile in glob.glob(os.path.join(dirpath, "*.BMP")):
                scr = os.path.splitext(os.path.split(ifile)[1])[0]
                if not fnmatch.fnmatch(scr, options.file):
                    continue
                if not re.match(options.regex, scr):
                    continue
                if options.recurse:
                    outpath = dirpath.replace(args[0], args[1], 1)
                    if not os.access(outpath, os.F_OK):
                        os.mkdir(outpath)
                elif options.hrecurse:
                    outpath = args[1]
                ofile = os.path.join(outpath, scr + ".GP8")
                if options.verbose:
                    print("Converting %s..." % ifile)
                xpos, ypos = read_pos(
                    open(options.posfile, "r"), os.path.split(ifile)[1]
                )
                bmp2gp8(open(ofile, "wb"), open(ifile, "rb"), xpos, ypos)
    else:
        for ifile in glob.glob(os.path.join(args[0], "*.BMP")):
            scr = os.path.splitext(os.path.split(ifile)[1])[0]
            if not fnmatch.fnmatch(scr, options.file):
                continue
            if not re.match(options.regex, scr):
                continue
            ofile = os.path.join(args[1], scr + ".GP8")
            if options.verbose:
                print("Converting %s..." % ifile)
            xpos, ypos = read_pos(open(options.posfile, "r"), os.path.split(ifile)[1])
            bmp2gp8(open(ofile, "wb"), open(ifile, "rb"), xpos, ypos)


if __name__ == "__main__":
    main()
