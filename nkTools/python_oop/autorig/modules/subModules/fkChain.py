# -*- coding: utf-8 -*-

import maya.cmds as cmds;

class FkChain(boneChain.BoneChain):
    def __init__(self, baseName="fkChain", side="C", ctrlColor="yellow", ctrlSize=1):
        boneChain.BoneChain.__init__(self, baseName, side);

        self.baseName = baseName;
        self.side = side;

        self.ctrlColor = ctrlColor;
        self.ctrlSize = ctrlSize;

        self.controlsArray = [];

    def fromList(self, posList=[], orientList=[], autoOrient=1, skipLast=1):
        boneChain.BoneChain.fromList(self, posList, orientList, autoOrient);

        self.__addControls(skipLast);
        self.__finalizeFkChain();

    def __addControls(self, skipLast=True):
        for i in range(self.chainLength()):
            if skipLast == 1:
                if i == (self.chainLength()-1):
                    return;

            ctrlClass = control.Control(self.baseName, self.side, self.ctrlSize, self.ctrlColor);
            ctrlClass.circleCtrl();

            cmds.xform(ctrlClass.controlGrp, ws=True, matrix=cmds.xform(self.chain[i], q=True, ws=True, matrix=True));

            self.controlsArray.append(ctrlClass);

    def __finalizeFkChain(self):
        reversedList = list(self.controlsArray);
        reversedList = reversedList.reverse();

        for i in range(len(reversedList)):
            if i != (len(reversedList-1)):
                cmds.parent(reversedList[i].controlGrp, reversedList[i+1]);

        for i, ctrl in enumerate(self.controlsArray):
            cmds.orientConstraint(ctrl.control, self.chain[i], mo=False);