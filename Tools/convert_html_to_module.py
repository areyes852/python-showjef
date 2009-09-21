#!/usr/bin/env python

"""
convert_html_to_module.py - Converts HTML from threadchart.info into a Python
                            module with colour data.

Copyright (C) 2009 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, urllib2

if __name__ == "__main__":

    if len(sys.argv) != 3:
    
        sys.stderr.write("Usage: %s <URL of HTML chart> <Python module>\n" % sys.argv[0])
        sys.stderr.write("The URL should refer to a thread chart on the threadchart.info Web site.\n")
        sys.exit(1)
    
    html_chart = sys.argv[1]
    python_module = sys.argv[2]
    
    u = urllib2.urlopen(html_chart)
    lines = u.readlines()
    u.close()
    
    lines = filter(lambda line: 'onMouseOut="this.bgColor=' in line or \
                                'Color #' in line, lines)
    
    groups = {}
    
    for i in range(0, len(lines), 2):
    
        colour_line = lines[i]
        colour = colour_line[colour_line.rfind("#"):colour_line.rfind("'")]
        description = lines[i+1].split("<br>")
        number = int(description[0][description[0].rfind("#")+1:])
        group = description[1]
        name = description[2][:description[2].find("</font>")]
        
        name = " ".join(name.split("\xa0"))
        
        colours = groups.setdefault(group, {})
        colours[number] = (name, colour)
    
    f = open(python_module, "w")
    
    f.write("# Generated from the %s file obtained from\n" % html_chart)
    f.write("# http://threadchart.info/%s\n\n" % html_chart)
    
    f.write("groups = {\n")
    
    for group, colours in groups.items():
    
        f.write('  "'+group+'": {\n')
        f.write('    # code: (name, RGB)\n')
        codes = colours.keys()
        codes.sort()
        
        for code in codes:
        
            name, colour = colours[code]
            f.write('    '+str(code)+': ("'+name+'", "'+colour+'"),\n')
        
        f.write('  },\n')
    
    f.write("}\n")
    f.close()
    
    sys.exit()
