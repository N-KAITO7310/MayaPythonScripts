# -*- coding: utf-8 -*-

import maya.cmds as cmds;
import maya.api.OpenMaya as om;
import autorig_settings;

def getUniqueName(baseName, side, suffix):

    security = 2000;

    
    if not side in autorig_settings.sides :
        om.MGlobal.displayError("Side is not valid");
        return;

    if not suffix in autorig_settings.suffixes:
        om.MGlobal.displayError("Suffix is not valid");
        return;

    name = side + "_" + baseName + str(0) + "_" + suffix;

    i = 0;
    while(cmds.objExists(name)):
        if(i < security):
            i += 1;

            name = side + "_" + baseName + "_" + str(i) + "_" + suffix;
        else:
            break;

    if checkName(name) == True:
        return name;
    else:
        return None;

def checkName(name):
    
    # TODO: HomeWork

    # 案：固有の名前化をチェックする？

    return True;