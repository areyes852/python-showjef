#!/usr/bin/env python

import commands, os, popen2, sys

def find_files(path, pattern):
    so, si = popen2.popen2('find '+commands.mkarg(path)+' -name "'+pattern+'"')
    si.close()
    return so.readlines()


if __name__ == "__main__":

    if len(sys.argv) != 4:
    
        sys.stderr.write("Usage: %s <search path> <dimensions> <output directory>\n" % sys.argv[0])
        sys.exit(1)
    
    search_path = sys.argv[1]
    dimensions = sys.argv[2]
    output_dir = sys.argv[3]
    
    paths = []
    paths += map(lambda line: line.strip(), find_files(search_path, "*.jef"))
    paths += map(lambda line: line.strip(), find_files(search_path, "*.JEF"))
    
    for path in paths:
    
        directory, file_name = os.path.split(path)
        if os.system("python jef2png.py --stitches-only "+dimensions+" "+commands.mkarg(path)+" "+commands.mkarg(os.path.join(output_dir, file_name+".png"))) == 0:
            print os.path.join(output_dir, file_name+".png")
        else:
            sys.stderr.write("Failed to convert file: "+path+"\n")
    
    sys.exit()
