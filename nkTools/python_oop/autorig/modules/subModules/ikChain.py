# -*- coding: utf-8 -*-

import maya.cmds as cmds;
import boneChain, control;
from utils import nameUtils;

class IkChain(boneChain.BoneChain):
    def __init__(self, baseName="ikChain", side="C", ctrlColor="yellow", ctrlSicze=1):
        boneChain.BoneChain.__init__(self, baseName, side);

        self.baseName = baseName;
        self.side = side;
        self.ctrlColor = ctrlColor;
        self.Size = ctrlSize;
        self.grpArray = [];
        self.ctrlsArray = [];

    def fromList(self, posList=[], orientList=[], autoOrient=1):
        boneChain.BoneChain.fromList(self, posList, orientList, autoOrient);

        self.__addControls(posList);
        self.__buildIkDevice();
        self.__buildNoFlipJnt(posList, orientList);
        self.__buildNoFlipLocator(posList, orientList);
        self.__buildNoFlipIkDevice();
        self.__finalizedIkChain();

    def __addControls(self, posList=[]):
        for i in [1, self.chainLength -1]:
            ctrlClass = control.Control(self.side, self.baseName, self.ctrlSize, self.ctrlColor);
            if i == 1:
                ctrlClass = control.Control(self.side, self.baseName, self.ctrlSize, self.ctrlColor);# typeControl="PV"?
                ctrlClass.circleCtrl();# sphereCtrl

                cmds.rotate(0, 0, 0, ctrlClass.controlGrp, r=True);

            elif i == self.chainLength -1:
                ctrlClass.circleCtrl();# cubeCtrl

            cmds.xform(ctrlClass.controlGrp, ws=True, matrix=cmds.xform(self.chain[i], ws=True, matrix=True, q=True));

            self.grpArray.append(ctrlClass.controlGrp);
            self.controlsArray.append(controlName);

    def __buildIkDevice(self):
        self.__buildIkName();
        self.__buildPvCnstName();

        if not self.ikHandleName:
            return;

        cmds.ikHandle(name=self.ikHandleName, startJoint=self.chain[0], endEffector=self.chain[self.chainLength()-1], solver="ikRPsolver");

        if not self.pvCnstName:
            return;

        cmds.poleVectorConstraint(self.controlsArray[0], self.ikHandleName);

    def __buildIkName(self):
        self.ikHandleName = nameUtils.getUniqueName(self.side, self.baseName, "ikHandle");

    def __buildPvCnstName(self):
        self.pvCnstName = nameUtils.getUniqueName(self.side, self.baseName, "PVConst");

    def __buildNoFlipJnt(self, posList=[], orientList=[]):
        cmds.select(cl=True);
        self.noFlipChain=[];

        tempStartJntName = nameUtils.getUniqueName(self.side, self.baseName, "noFlipJnt");
        noFlipJntStart = cmds.joint(name=tempStartJntName, position=posList[0]);

        tempEndJntName = nameUtils.getUniqueName(self.side, self.baseName, "noFlipJnt");
        noFlipJntEnd = cmds.joint(name=tempEndJntName, position=posList[sellf.chainLength-1]);

        self.noFlipChain.append(noFlipJntStart);
        self.noFlipChain.append(noflipJntEnd);

        cmds.parent(noFlipJntEnd, noFlipJntStart);

        cmds.joint(noFlipJntStart, e=True, oj="xyz", secondaryAxisOrient="yup", ch=True, zso=True);

        for jo in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
            cmds.setAttr("{}.{}".format(noflipJntEnd, jo), 0);

    def __buildNoFlipLocator(self, posList=[], orientList=[]):
        self.__buildLocNoFlipName();
        cmds.spaceLocator(name=self.noFlipLocName);

        cmds.xform(self.noFlipLocName, translation=posList[self.chainLength() -1]);
        cmds.parent(self.noFlipLocName, self.noFlipChain[1], relative=True);
        cmds.xform(self.noFlipLocName, translation=[0, 0, 0], rotation=[0, 0, 0]);
        cmds.xform(self.noFlipLocName, translation=[0, -0.2, 0]);

        cmds.parent(self.noFlipLocName, self.controlsArray[1]);

    def __buildNoFlipIkDevice(self):
        self.__buildNoFlipIkHandleName();

        if not self.noFlipIkHandleName:
            return;

        cmds.ikHandle(name=self.noFlipIkHandleName, startJoint=self.noFlipChain[0], endEffector=self.noFlipChain[1], solver="ikRPsolver");

        if not self.pvConstName:
            return;

        cmds.poleVectorConstraint(self.noFlipLocName, self.noFlipIkHandleName);

    def __buildLocNoFlipName(self):
        self.noFlipLocName = nameUtils.getUniqueName(self.side, self.baseName, "noFlipLoc");

    def __buildNoFlipIkHandleName(self):
        self.noFlipIkHandleName = nameUtils.getUniqueName(self.side, self.baseName, "noFlipIkIkHandle");

    def __finalizedIkChain(self):
        cmds.pointConstraint(self.controlsArray[-1], self.ikHandleName);
        cmds.pointConstraint(self.controlsArray[-1], noFlipIkHandleName);
        cmds.parentConstraint(self.noFlipChain, self.grpArray[0], self.grpArray[0], maintainOffset=True);