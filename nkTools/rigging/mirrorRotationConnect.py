# -*- coding: utf-8 -*-
import maya.cmds as cmds;

"""
自作リグのミラーポーズツール

Memo
・移動地の反転は、原点を基準に反転したい方向に-1を乗じた値
・オイラー回転の単純な利用では回転の反転はできない


・rootを選択して実行
・IKなどの移動値と、回転のミラーを行う

・Lの値をRに、Rの値をLに送る
・プリフィックスのないものは逆の値を入れる

from nkTools.rigging import mirrorRotationConnect;
reload(mirrorRotationConnect);
mirrorRotationConnect;
"""

# prepare var
driver = str(cmds.ls(sl=True)[0]);
driven = str(cmds.ls(sl=True)[1]);
driverSideNull = cmds.createNode("transform", n="{0}_driverSideNull".format(driver));

# TODO:need to input axis by UI
axisList = ["X", "Y", "Z"];

# driverSide to drivenSide
cmds.setAttr("{0}.sx".format(driverSideNull), -1);
multMatrix = cmds.shadingNode("multMatrix", au=True);
cmds.connectAttr("{0}.matrix".format(driver), "{0}.matrixIn[0]".format(multMatrix), f=True);
cmds.connectAttr("{0}.matrix".format(driverSideNull), "{0}.matrixIn[1]".format(multMatrix), f=True);
decompose = cmds.createNode("decomposeMatrix");
cmds.connectAttr("{0}.matrixSum".format(multMatrix), "{0}.inputMatrix".format(decompose), f=True);
quatToEular = cmds.shadingNode("quatToEuler", au=True);

# connection
cmds.connectAttr("{0}.outputQuat".format(decompose), "{0}.inputQuat".format(quatToEular), f=True);
for axis in axisList:
    cmds.connectAttr("{0}.outputRotate{1}".format(quatToEular, axis), "{0}.rotate{1}".format(driven, axis), f=True);


            
