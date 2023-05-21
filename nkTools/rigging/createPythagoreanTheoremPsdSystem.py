# -*- coding: utf-8 -*-
import maya.cmds as cmds;


"""

対象となるオブジェクト、ドライバー、アウトプット先を選択し実行。
三平方の定理を利用し、対象オブジェクトとドライバー間の距離で最大値1の値を出力するギミックを自動化する。

Reference:
https://www.youtube.com/watch?v=tr2v36AXXPs

lastUpdate: 23/05/20
"""

def createPythagoreanTheoremPsdSystem():
    cmds.undoInfo(openChunk=True);

    targetObj, driverObj = cmds.ls(sl=True, type="transform")[0:2];

    psdSphere = cmds.createNode('implicitSphere', n="{}_psd_sphere".format(targetObj));
    cmds.matchTransform(psdSphere, targetObj, pos=True, rot=True);

    pmm = cmds.createNode("pointMatrixMult", n="{}_pmm".format(targetObj));
    cmds.connectAttr("{}.worldInverseMatrix[0]".format(psdSphere), "{}.inMatrix".format(pmm));

    decomposeMat = cmds.createNode("decomposeMatrix", n="{}_psd_decomposeMatrix".format(targetObj));
    cmds.connectAttr("{}.worldMatrix[0]".format(driverObj), "{}.inputMatrix".format(decomposeMat));
    cmds.connectAttr("{}.outputTranslate".format(decomposeMat), "{}.inPoint".format(pmm));

    targetObjTrans = cmds.xform(targetObj, q=True, translation=True, ws=True);
    driverObjTrans = cmds.xform(driverObj,  q=True, translation=True, ws=True);

    startLoc = cmds.spaceLocator(name="{}_psd_startLoc".format(targetObj))[0];
    endLoc = cmds.spaceLocator(name="{}_psd_startLoc".format(targetObj))[0];
    distShape = cmds.createNode("distanceDimShape", name="{}_psd_distanceDimensionShape1".format(targetObj));
    cmds.connectAttr("{}.worldPosition[0]".format(startLoc), "{}.startPoint".format(distShape));
    cmds.connectAttr("{}.worldPosition[0]".format(endLoc), "{}.endPoint".format(distShape));

    cmds.xform(startLoc, t=targetObjTrans);
    cmds.xform(endLoc, t=driverObjTrans);

    cmds.parent(startLoc, targetObj);
    cmds.parent(endLoc, driverObj);

    cmds.addAttr(driverObj, longName="psdOutput", shortName="po", at="float");
    cmds.setAttr("{}.psdOutput".format(driverObj), e=True, keyable=True);

    exprStr = """
    float $tx = {}.outputX;
    float $ty = {}.outputY;
    float $tz = {}.outputZ;
    float $dist = sqrt($tx*$tx + $ty * $ty + $tz * $tz);
    $clamped = 1.0 - clamp(0.0, 1.0, $dist);

    {}.psdOutput = $clamped;
    """.format(pmm, pmm, pmm, driverObj);

    cmds.expression(s=exprStr, alwaysEvaluate=False, unitConversion="none", name="{}_psd_expr".format(targetObj));

    cmds.undoInfo(closeChunk=True);

if __name__ == "__main__":
    createPythagoreanTheoremPsdSystem();