# -*- coding: utf-8 -*-

from logging import root
from maya import cmds, mel;

"""
AutoCreateSoftIk

created: 2022/09/16

＊制作当時急遽時間が取れなくなったために未完成のままとなっている。下記を参考としたソフトIKギミックを自動作成することを意図して開発に着手したもの。

Method by Hamondo Youtube Channel URL:https://www.youtube.com/user/Hazmondo

"""


# get jnts
jnts = cmds.ls(sl=True, type="joint");
startJnt = jnts[0];
endJnt = jnts[2];

upperArmLoc = cmds.createLocator(n="upperArmLoc");
lowerArmLoc = cmds.createLocator(n="lowerArmLoc");
wristArmLoc = cmds.createLocator(n="wristArmLoc");

# create locators
locList = [upperArmLoc, lowerArmLoc, wristArmLoc];

for i in range(3):
    cmds.delete(cmds.pointConstraint(jnts[i], locList[i]));

cmds.group(em=True, n="root_grp");

softBlendLoc = cmds.createLocator(n="softBlendLoc");
cmds.delete(cmds.pointConstraint(wristArmLoc, softBlendLoc));

armCtrlDistLoc = cmds.createLocator(n="armCtrlDistLoc");
cmds.delete(cmds.pointConstraint(wristArmLoc, armCtrlDistLoc));

# create ctrl and hierarchy
armCtrl = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=1, d=3, ut=0, tol=0.01, s=8, ch=0, n="arm_ctrl");
armCtrlOffset = cmds.group(armCtrl, n="{}_offset_grp");

cmds.parent(startJnt, wristArmLoc, upperArmLoc);
cmds.parent(upperArmLoc, lowerArmLoc, softBlendLoc, armCtrlOffset, root);
cmds.parent(armCtrlDistLoc, armCtrlOffset);

# create ikHandle
armIkHandle, armIkHandleEffector = cmds.ikHandle(name="arm_ikHandle", startJoint=startJnt, endEffector=endJnt, solver="ikRPsolver");
cmds.poleVectorConstraint(lowerArmLoc, armIkHandle);
cmds.parent(armIkHandle, softBlendLoc);

# TODO: lock ctrl rotate scale

# addAttrs to armCtrl
cmds.addAttribute(armCtrl, ln="ikControls", at="double", dv=0.0);
cmds.setAttr("{}.{}".format(armCtrl, "ikControls"), e=True, keyable="True");

cmds.addAttribute(armCtrl, ln="slideP", at="float", dv=0, min=-1, max=1);
cmds.setAttr("{}.{}".format(armCtrl, "slideP"), e=True, keyable="True");

cmds.addAttribute(armCtrl, ln="stretchP", at="float", dv=0, min=0, max=1);
cmds.setAttr("{}.{}".format(armCtrl, "stretchP"), e=True, keyable="True");

cmds.addAttribute(armCtrl, ln="softP", at="float", dv=0, min=0, max=1);
cmds.setAttr("{}.{}".format(armCtrl, "softP"), e=True, keyable="True");

cmds.addAttribute(armCtrl, ln="pinP", at="float", dv=0, min=0, max=1);
cmds.setAttr("{}.{}".format(armCtrl, "pinP"), e=True, keyable="True");

# TODO: enable change aimConstraint settings
cmds.aimConstraint(armCtrl, upperArmLoc, worldUpType="objectrotation", worldUpObject=root);

# create DistanceDimensions
ctrlDistShape = cmds.distanceDimension(startPoint=cmds.xform(upperArmLoc, q=True, translation=True, worldSpace=True), endPoint=cmds.xform(lowerArmLoc, q=True, translation=True, worldSpace=True));
ctrlDist = cmds.rename(cmds.listRelatives(ctrlDistShape), p=True)[0], "ctrlDist");
softDistShape = cmds.distanceDimension(startPoint=cmds.xform(upperArmLoc, q=True, translation=True, worldSpace=True), endPoint=cmds.xform(lowerArmLoc, q=True, translation=True, worldSpace=True))
softDist = cmds.rename(cmds.listRelatives(softDistShape, p=True)[0], "softDist");
upperArmDistShape = cmds.distanceDimension(startPoint=cmds.xform(upperArmLoc, q=True, translation=True, worldSpace=True), endPoint=cmds.xform(lowerArmLoc, q=True, translation=True, worldSpace=True))
upperArmDist = cmds.rename(cmds.listRelatives(upperArmDistShape, p=True)[0], "upperArmDist");
lowerArmDistShape = cmds.distanceDimension(startPoint=cmds.xform(upperArmLoc, q=True, translation=True, worldSpace=True), endPoint=cmds.xform(lowerArmLoc, q=True, translation=True, worldSpace=True))
lowerArmDist = cmds.rename(cmds.listRelatives(lowerArmDistShape, p=True)[0], "lowerArmDist");
stretchArmDistShape = cmds.distanceDimension(startPoint=cmds.xform(upperArmLoc, q=True, translation=True, worldSpace=True), endPoint=cmds.xform(lowerArmLoc, q=True, translation=True, worldSpace=True))
stretchArmDist = cmds.rename(cmds.listRelatives(stretchArmDistShape, p=True)[0], "stretchDist");

# connect dimensions
cmds.connectAttr("{}.{}".format(upperArmLoc, "worldPosition[0]"), "{}.{}".format(ctrlDistShape, "startPoint"));
cmds.connectAttr("{}.{}".format(armCtrlDistLoc, "worldPosition[0]"), "{}.{}".format(ctrlDistShape, "endPoint"));

cmds.connectAttr("{}.{}".format(wristArmLoc, "worldPosition[0]"), "{}.{}".format(softDistShape, "startPoint"));
cmds.connectAttr("{}.{}".format(softBlendLoc, "worldPosition[0]"), "{}.{}".format(softDistShape, "endPoint"));

cmds.connectAttr("{}.{}".format(upperArmLoc, "worldPosition[0]"), "{}.{}".format(upperArmDistShape, "startPoint"));
cmds.connectAttr("{}.{}".format(lowerArmLoc, "worldPosition[0]"), "{}.{}".format(upperArmDistShape, "endPoint"));

cmds.connectAttr("{}.{}".format(lowerArmLoc, "worldPosition[0]"), "{}.{}".format(lowerArmDistShape, "startPoint"));
cmds.connectAttr("{}.{}".format(softBlendLoc, "worldPosition[0]"), "{}.{}".format(lowerArmDistShape, "endPoint"));

cmds.connectAttr("{}.{}".format(upperArmLoc, "worldPosition[0]"), "{}.{}".format(stretchArmDistShape, "startPoint"));
cmds.connectAttr("{}.{}".format(softBlendLoc, "worldPosition[0]"), "{}.{}".format(stretchArmDistShape, "endPoint"));

# softIkExpression = 
"""
$controlDist = controlDistShape.distance;
$softDist = $controlDist;
$softP = armCtrl.softP;
$chainLen = 7.0;

if($controlDist > ($chainLen - $softP)){
    if(softP > 0){
        $softDist = $chainLen - $softP * exp(-($controlDist - ($chainLen - $softP)) / $softP);
    }
    else{
        $softDist = $chianLen;
    }
}

wristLoc.translateX = $softDist;
"""

cmds.createNode("condition", n="");
cmds.createNode("plusMinusAverage");

cmds.connectAttr("");