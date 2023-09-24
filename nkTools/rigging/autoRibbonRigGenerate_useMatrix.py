# -*- coding: utf-8 -*-
import maya.cmds as cmds;

"""
last update date: 06/06

リボンリグをフォリクルでなくマトリックスでセットアップするために作成した簡易スクリプトを切り出したもの
リボンリグツールに導入できるようにしたい

surfaceName: 対象とするサーフェースオブジェクト名

"""
surfaceName = "l_beard_ribbon";

PARAMETER_V = 0.5;
AXIS_LIST = ["X", "Y", "Z"];
LOWER_AXIS_LIST = ["x", "y", "z"];

uSpan = 11;
surface = str(cmds.nurbsPlane(p=[0, 0, 0],ax=[0 ,1 ,0],w=1, lr=1, d=3, u=uSpan, v=1, ch=1, n=surfaceName)[0]);
    
shape = cmds.listRelatives(s=True)[0];
spansUV = cmds.getAttr("{}.spansUV".format(surface));
patchesU = float(spansUV[0][0]);
parameterURatio = 1.0 / patchesU;
print(patchesU, parameterURatio)

# rebuild
cmds.rebuildSurface(surface, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=patchesU, du=3, sv=1, dv=1, tol=0.0001, fr=0, dir=2);
cmds.delete(surface, constructionHistory=True);

for i in range(int(patchesU+1.0)):
    # parameter U
    parameterU = parameterURatio * i;
    
    # prepare nodes
    pOnSurfaceInfo = cmds.createNode("pointOnSurfaceInfo", n="{}_{}_pointOnSurfaceInfo".format(surface, str(i + 1).zfill(2)));
    # set parameter U and V
    cmds.setAttr("{}.parameterU".format(pOnSurfaceInfo), parameterU);
    cmds.setAttr("{}.parameterV".format(pOnSurfaceInfo), PARAMETER_V);
    vecProd = cmds.createNode("vectorProduct", n="{}_{}_vectorProduct".format(surface, str(i + 1).zfill(2)));
    # set operation Cross product
    cmds.setAttr("{}.operation".format(vecProd), 2);
    fourByFour = cmds.createNode("fourByFourMatrix", n="{}_{}_fourByFourMatrix".format(surface, str(i + 1).zfill(2)));
    decomposeMat = cmds.createNode("decomposeMatrix", n="{}_{}_decomposeMatrix".format(surface, str(i + 1).zfill(2)));
    loc = cmds.spaceLocator(n="{}_{}_loc".format(surface, str(i + 1).zfill(2)))[0];
    
    # create network
    cmds.connectAttr("{}.worldSpace[0]".format(shape), "{}.inputSurface".format(pOnSurfaceInfo));
    cmds.connectAttr("{}.normal".format(pOnSurfaceInfo), "{}.input1".format(vecProd));
    cmds.connectAttr("{}.tangentV".format(pOnSurfaceInfo), "{}.input2".format(vecProd));
    
    # input normal
    for i, axis in enumerate(AXIS_LIST):
        cmds.connectAttr("{}.normal{}".format(pOnSurfaceInfo, axis), "{}.in0{}".format(fourByFour, i));
    # input tangentV
    for i, axis in enumerate(LOWER_AXIS_LIST):
        cmds.connectAttr("{}.tangentV{}".format(pOnSurfaceInfo, axis), "{}.in1{}".format(fourByFour, i));
    # input cross product
    for i, axis in enumerate(AXIS_LIST):
        cmds.connectAttr("{}.output{}".format(vecProd, axis), "{}.in2{}".format(fourByFour, i));
    # input translate
    for i, axis in enumerate(AXIS_LIST):
        cmds.connectAttr("{}.position{}".format(pOnSurfaceInfo, axis), "{}.in3{}".format(fourByFour, i));
        
    # decompose
    cmds.connectAttr("{}.output".format(fourByFour), "{}.inputMatrix".format(decomposeMat));
    
    # connect loc
    cmds.connectAttr("{}.outputTranslate".format(decomposeMat), "{}.translate".format(loc));
    cmds.connectAttr("{}.outputRotate".format(decomposeMat), "{}.rotate".format(loc));
        
        
    
    
    
    
    
    
    