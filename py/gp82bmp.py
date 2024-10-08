#
# Yu-No windows ver. GP8-to-BMP image converter
#

import io
import os
import re
import glob
import fnmatch
import struct
import optparse
import sys
import ctypes

version = "%prog 0.5"


def write_bmp_hdr(fo, width, height):
    fo.write(b"BM")
    fo.write(b"\x00\x00\x00\x00")
    fo.write(b"\x00\x00")
    fo.write(b"\x00\x00")
    fo.write(b"\x36\x04\x00\x00")
    fo.write(b"\x28\x00\x00\x00")
    fo.write(struct.pack("<I", width))
    fo.write(struct.pack("<I", height))
    fo.write(b"\x01\x00")
    fo.write(b"\x08\x00")
    fo.write(b"\x00\x00\x00\x00")
    fo.write(b"\x00\x00\x00\x00")
    fo.write(b"\x13\x0b\x00\x00")
    fo.write(b"\x13\x0b\x00\x00")
    fo.write(b"\x00\x01\x00\x00")
    fo.write(b"\x00\x00\x00\x00")


# ======================== begin terminally slow code =========================


def dwrite(fo, dict, dpos, b):
    dict[dpos] = b
    dpos = (dpos + 1) & 0xFFF
    fo.write(bytes([b]))
    return dict, dpos


# LZSS compression with a 0x1000-byte dictionary, meh
def slow_decomp(fo, fi):
    dict = bytearray(0x1000)
    dpos = 0xFEE  # weird place to start, but whatever...
    ipos = 0
    try:
        while 1:
            mask = fi.read(1)[0]
            for j in range(8):
                if mask & 1:
                    b = fi.read(1)[0]
                    dict, dpos = dwrite(fo, dict, dpos, b)
                else:
                    b1 = fi.read(1)[0]
                    b2 = fi.read(1)[0]
                    didx = ((b2 & 0xF0) << 4) | b1
                    dnum = (b2 & 0xF) + 3
                    for k in range(dnum):
                        b = dict[didx]
                        didx = (didx + 1) & 0xFFF
                        dict, dpos = dwrite(fo, dict, dpos, b)
                mask >>= 1
    except IndexError:
        pass


# ========================= end terminally slow code ==========================


# fast ctypes implementation of the above
# Windows only atm
def decomp(fo, bio):
    buf_size = 524288
    data = bio.read()
    c_cmprlen = ctypes.c_int(len(data))
    c_in = ctypes.create_string_buffer(data)
    # try 512 KB output buffer, then 1 MB, then 2MB
    for k in range(3):
        c_out_size = ctypes.c_int(buf_size)
        c_out = ctypes.create_string_buffer(c_out_size.value)
        uncmprlen = ctypes.cdll.yunolzss.yuno_decomp(c_out, c_in, c_cmprlen, c_out_size)
        if uncmprlen >= 0:
            break
        buf_size *= 2
    # three strikes and you're out!
    if uncmprlen == -1:
        raise MemoryError(
            "yunolzss.dll - uncompressed data too large for output buffer"
        )
    fo.write(c_out.raw[:uncmprlen])


def gp82bmp(fo, fi):
    xpos, ypos, width, height = struct.unpack("<HHHH", fi.read(8))
    palette = fi.read(1024)
    write_bmp_hdr(fo, width, height)
    fo.write(palette)
    try:
        ctypes.cdll.yunolzss  # to trigger an exception (if needed)
        decomp(fo, fi)
    except WindowsError:
        slow_decomp(fo, fi)
    return xpos, ypos


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

    fp = open(options.posfile, "w")
    if not os.access(args[1], os.F_OK):
        os.mkdir(args[1])
    if options.recurse or options.hrecurse:
        for dirpath, dirnames, filenames in os.walk(args[0]):
            for ifile in glob.glob(os.path.join(dirpath, "*.GP8")):
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
                ofile = os.path.join(outpath, scr + ".BMP")
                if options.verbose:
                    print("Converting %s..." % ifile)
                xpos, ypos = gp82bmp(open(ofile, "wb"), open(ifile, "rb"))
                fp.write("%s xpos %d ypos %d\n" % (os.path.split(ifile)[1], xpos, ypos))
    else:
        for ifile in glob.glob(os.path.join(args[0], "*.GP8")):
            scr = os.path.splitext(os.path.split(ifile)[1])[0]
            if not fnmatch.fnmatch(scr, options.file):
                continue
            if not re.match(options.regex, scr):
                continue
            ofile = os.path.join(args[1], scr + ".BMP")
            if options.verbose:
                print("Converting %s..." % ifile)
            xpos, ypos = gp82bmp(open(ofile, "wb"), open(ifile, "rb"))
            fp.write("%s xpos %d ypos %d\n" % (os.path.split(ifile)[1], xpos, ypos))
    fp.close()


if __name__ == "__main__":
    main()
