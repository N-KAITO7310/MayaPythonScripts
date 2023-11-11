# -*- coding: utf-8 -*-

import maya.cmds as cmds;
from utils import nameUtils;

class BoneChain(object):
    def __init__(self, baseName="chain", side="C"):
        self.baseName = baseName;
        self.side = side;
        self.chain = [];

    def fromList(self, posList=[], orientList=[], autoOrient=1):
        for i in range(len(posList)):
            tempName = nameUtils.getUniqueName(self.baseName, self.side, "jnt");

            cmds.select(cl=True);

            if autoOrient == 1:
                tempJnt = cmds.joint(n=tempName, position=posList[i]);
            else:
                tempJnt = cmds.joint(n=tempName, position=posList[i], orientation=orientList[i]);

            self.chain.append(tempJnt);

        self.__parentJoints();

        if autoOrient == 1:
            cmds.joint(n=self.chain[0], e=True, oj="xyz", secondaryAxisOrient="yup", children=True, zso=True);

        self.__zeroOrientJoint(self.chain[-1]);

    def __str__(self):
        result = "BoneChain class , length : {}, chain : ".format(self.chainLength());
        chainNames = [obj for obj in self.chain];
        result += str(chainNames);

        return result;

    def chainLength(self):
            return len(self.chain);

    def __zeroOrientJoint(self, bone):
        for attr in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
            cmds.setAttr("{}.{}".format(bone, attr), 0);

    def __parentJoints(self):
        reversedList = list(self.chain);
        reversedList.reverse();
        for i in range(len(reversedList)):
            if i != (len(reversedList)-1):
                cmds.parent(reversedList[i], reversedList[i+1]);