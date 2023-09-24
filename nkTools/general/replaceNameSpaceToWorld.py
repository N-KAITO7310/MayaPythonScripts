# -*- coding: utf-8 -*-
"""
    replaceNameSpaceToWorld
    description: 複数選択されたmaファイルに対して実行。リファレンスに伴い付与されたnameSpaceをma内部コードを直接編集する方法によって除去する。
    なお、リファレンスではなくシーン内で直接namespaceを付与している状況は想定していない。

    created: 2022/08/24
    lastUpdated: 2022/08/24

"""

from __future__ import absolute_import, division, generators, print_function, unicode_literals
try:
    from future_builtins import *
except:
    pass
import sys
sys.dont_write_bytecode = True
from maya import cmds;
import io;

def replaceNameSpaceToWorld(filter):
    paths = cmds.fileDialog2(fileFilter=filter, fileMode=4, dialogStyle=2);

    for path in paths:
        
        with io.open(path, mode="r", encoding="utf-8") as f:
            newText = '';
            nameSpaceList = [];

            while True:
                line = f.readline();
                if not line:
                    break;

                if 'file' in line and '-ns' in line:
                    nsIndexStart = line.find('-ns')+5;
                    nsIndexEnd = line.find('"', nsIndexStart);
                    ns = line[nsIndexStart:nsIndexEnd];
                    nameSpaceList.append(ns);

                    line = line.replace('"' + ns + '"', '":"');

                    for ns in nameSpaceList:
                        if ns + ':' in line:
                            line = line.replace(ns+':', '');
                    
                else:
                    for ns in nameSpaceList:
                        if ns + ':' in line:
                            line = line.replace(ns+':', '');
                        
                newText = newText + line;

        with io.open(path, mode="w", encoding="utf-8") as f:
            f.write(newText);

if __name__ == "__main__":
    FILE_FILTER = "*.ma";

    replaceNameSpaceToWorld(FILE_FILTER);
    