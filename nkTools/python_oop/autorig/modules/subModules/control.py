# -*- coding: utf-8 -*-

import maya.cmds;
from utils import nameUtils, xformUtils;

class Control(object):
    def __init__(self, side="C", baseName="ctrl", size=1, objColor="yellow", aimAxis="x"):
        self.baseName = baseName;
        self.side = side;
        self.objColor = objColor;
        self.size = size;
        self.aimAxis = aimAxis;

        self.control = None;
        self.controlGrp = None;
        self.controlName = None;

    def circleCtrl(self):
        self.__buildName();
        if self.controlName:
            self.control = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=1, d=3, ut=False, tol=0.01, s=8, ch=False, n=self.controlName)[0];

        self.__finalizeCtrl();

    def pinCtrl(self):
        pass;

    def circleCtrl(self):
        pass;

    def cubeCtrl(self):
        pass;

    def __buildName(self):
        self.controlName = nameUtils.getUniqueName(self.baseName, self.side, "ctrl");

    def __finalizeCtrl(self):
        self.__aimCtrl();

        if self.size != 1:
            for s in cmds.listRelatives(cmds.control, s=True):
                span = cmds.getAttr("{}.span".format(s));
                for i in range(span):
                    # TODO: circleは正しくスケールできるが、重なったcvがマージされていない形状に関しては+1する必要がある＊作成する形状は全てマージして閉じている必要がある
                    cmds.scale(self.size, self.size, self.size, "{}.cv[{}]".format(s, i), r=True);

            cmds.delete(self.control, ch=True);

        self.controlGrp = xformUtils.createOffset(self.control);

    def __aimCtrl(self):
        y = 0;
        z = 0;

        if self.aimAxis == "y":
            z = 90;
        elif self.aimAxis == "z":
            y = -90;

        for s in cmds.listRelatives(self.control, s=True):
            span = cmds.getAttr("{}.span".format(s));
                for i in range(span):
                    cmds.rotate(0, y, z, "{}.cv[{}]".format(s, i), r=True);

    def __setColor(self, control, color):
        pass;