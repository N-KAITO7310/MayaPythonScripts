# -*- coding: utf-8 -*-
"""

Auto FK Ik SetUp Tool to Arm or Leg
version:1.0
created date:2021/11/01~

from nkTools.rigging import autoFKIKSetUpTool_v2;
reload(autoFKIKSetUpTool_v2);
reload(autoFKIKSetUpTool_v2.qt);
autoFKIKSetUpTool_v2.option();

"""

from maya import cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui
from ..lib import qt;
import pymel.core as pm;
import maya.api.OpenMaya as om;

def autoFKIKSetUpTool():
    # ------------------------------
    # Ready variables and Create joints

    # check joint select
    selectionCheck = cmds.ls(sl=True, type="joint");
    if not selectionCheck:
        cmds.error("Please select the root joint");
    else:
        jointRoot = cmds.ls(sl=True, type="joint")[0];

    # variables setting
    rigType = settings.rigType;
    isLower = settings.bodySide;
    grpSuffix = "_grp";
    bodyJoints = 4;

    # which body part, biped:arm or leg, quad:leg only
    bodyPrefix = "";
    if rigType == 0:
        if isLower:
            bodyPrefix = "leg_";
        else:
            bodyPrefix = "arm_";
    if rigType == 1:
        bodyPrefix = "leg_";

    # quadruped:front or rear
    bodySidePrefix = "";
    if rigType == 1:
        if isLower:
            bodySidePrefix = "rear";
        else:
            bodySidePrefix = "front";
        
    # check l or r side
    whichSide = jointRoot[0:2];
    if not "l_" in whichSide:
        if not "r_" in whichSide:
            cmds.error("Please use a joint with a usable prefix of eigher l_ or r_");
            return;
            
    # set prefix
    prefix = whichSide + bodyPrefix + bodySidePrefix
    # set suffix
    mainControlName = "transform_ctrl";
    pawControlName = prefix + "_ik_ctrl";
    kneeControlName = prefix + "_tibia_ctrl";
    hockControlName = prefix + "_hock_ctrl";
    rootControlName = prefix + "_root_ctrl";
    
    # get hierarchy
    jointHierarchy = cmds.listRelatives(jointRoot, ad=True, type="joint");
    jointHierarchy.append(jointRoot);
    jointHierarchy.reverse();
    
    
    # Bifurcation setup type
    if rigType == 0:
        setupBiped(whichSide, prefix, jointHierarchy[0], jointHierarchy);
        return;
    
    # create new joint ilst
    fkSuffix = "_fk_jnt";
    ikSuffix = "_ik_jnt";
    stretchSuffix = "_stretch_jnt";
    driverSuffix = "_driver_jnt";
    newJointList = [ikSuffix, fkSuffix, stretchSuffix];
    
    # add driver jnts
    # for 0~3jnt IKRP, for knee IKSC Rotation.Not needed at the rear
    if isLower:
        newJointList.append(driverSuffix);
        
    cmds.select(cl=True);
    # create joint per newJointList
    for newJoint in newJointList:
        # create joint per bodyJoints
        for i in range(bodyJoints):
            newJointName = removeJntSuffix(jointHierarchy[i]) + newJoint;
            cmds.joint(n=newJointName);
            cmds.matchTransform(newJointName, jointHierarchy[i]);
            cmds.makeIdentity(newJointName, a=1, t=0, r=1, s=0);
            
        cmds.select(cl=True);
    # ------------------------------
    # create Controlers
    
    # main transform ctrl
    if not cmds.ls(mainControlName):
        radius = 150;
        cmds.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=mainControlName);
    
    
    if "r_" in whichSide:
        sideInverse = -1
    else:
        sideInverse = 1;
    if not isLower:
        upperLowInverse = -1
    else:
        upperLowInverse = 1;

    # rootCtrl
    rootCtrl = createCurveAndOffset(0, rootControlName, jointRoot, 10)[1];

    # FKIKSwitch TODO:メソッドに置き換えること
    fkikSwitchCtrlOffset = createCurveAndOffset(5, prefix + "_fkikSwitch_ctrl", jointHierarchy[2], 10)
    cmds.move(10*sideInverse, 0, 0, fkikSwitchCtrlOffset[0], r=True, wd=True);
    cmds.addAttr(fkikSwitchCtrlOffset[1], ln="FKIKSwitch", at="double", min=0, max=1 ,dv=1);
    cmds.setAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", e=True, keyable=True);
    cmds.addAttr(fkikSwitchCtrlOffset[1], ln="VolumeOffset", at="double", min=-0.5, max=3 ,dv=0);
    cmds.setAttr(fkikSwitchCtrlOffset[1] + ".VolumeOffset", e=True, keyable=True);
    fkikReverse = cmds.shadingNode("reverse", au=True, n=prefix + "_fkik_reverse");
    cmds.connectAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", fkikReverse + ".inputX", f=True);

    # fk controler
    fkCtrlList = [];
    for i in range(bodyJoints):
        fkCtrlName = removeJntSuffix(jointHierarchy[i]) + "_fk_ctrl";
        ctrlAndOffset = createCurveAndOffset(0, fkCtrlName, jointHierarchy[i], 10);
        fkCtrlList.append(ctrlAndOffset);
    # fk hierarchy
    createFkHierarchy(fkCtrlList);
    
    # ik
    ikCtrlOffset = createCurveAndOffset(0, pawControlName, jointHierarchy[3], 10);
    # hock ctrl
    ikHockCtrlOffset = createCurveAndOffset(3, prefix + "_hock_ctrl", jointHierarchy[2], 10);
    cmds.setAttr(ikHockCtrlOffset[0] + ".rotate", 0, 0, 0, type="double3");
    cmds.parent(ikHockCtrlOffset[0], ikCtrlOffset[1]);
    # polevectorctrl
    ikTibiaCtrlOffset = createCurveAndOffset(4, kneeControlName, jointHierarchy[3],10);
    cmds.delete(str(cmds.pointConstraint(jointHierarchy[0], jointHierarchy[3], ikTibiaCtrlOffset[0], mo=False)[0]));
    cmds.move(0, 0, 40*upperLowInverse, ikTibiaCtrlOffset[0], r=True, wd=True);
    
    # fkikSwitch connect fk ik visibility
    cmds.connectAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", ikCtrlOffset[0] + ".visibility");
    cmds.connectAttr(fkikReverse + ".outputX", fkCtrlList[0][0] + ".visibility");
   
    # ------------------------------
    # setUp FK Ik
    cmds.parentConstraint(rootControlName, fkCtrlList[0][0], mo=0, w=True);
    
    for i in range(bodyJoints):
        # constraint mainJoint by ik fk joint
        cmds.parentConstraint(removeJntSuffix(jointHierarchy[i]) + ikSuffix, removeJntSuffix(jointHierarchy[i]) + fkSuffix, jointHierarchy[i], w=True, mo=0);
        # constraint fk
        cmds.parentConstraint(removeJntSuffix(jointHierarchy[i]) + "_fk_ctrl", removeJntSuffix(jointHierarchy[i]) + fkSuffix, w=True, mo=0);
    
    # IK set root to metacarpus
    if isLower:
        # driverIkHandle = str(cmds.ikHandle(n=prefix + "_driver_ikHandle", solver="ikRPsolver", sj=removeJntSuffix(jointHierarchy[0]) + driverSuffix, ee=removeJntSuffix(jointHierarchy[3]) + driverSuffix)[0]);
        mel.eval("ikSpringSolver;");
        driverIkHandle = str(cmds.ikHandle(n=prefix + "_driver_ikHandle", solver="ikSpringSolver", sj=removeJntSuffix(jointHierarchy[0]) + driverSuffix, ee=removeJntSuffix(jointHierarchy[3]) + driverSuffix)[0]);
    
    # IK root to knee(carpus)
    kneeIkHandle = str(cmds.ikHandle(n=prefix + "_knee_ikHandle", solver="ikRPsolver", sj=removeJntSuffix(jointHierarchy[0]) + ikSuffix, ee=removeJntSuffix(jointHierarchy[2]) + ikSuffix)[0]);
    # IK knee to metacarpus
    hockIkHandle = str(cmds.ikHandle(n=prefix + "_hock_ikHandle", solver="ikSCsolver", sj=removeJntSuffix(jointHierarchy[2]) + ikSuffix, ee=removeJntSuffix(jointHierarchy[3]) + ikSuffix)[0]);
  
    # group ikHandle
    kneeControlGrp = cmds.group(kneeIkHandle, n=prefix + "_knee_control_grp");
    kneeControlGrpOffset = cmds.group(kneeControlGrp, n=prefix + "_knee_control_offset_grp");
    
    # adjust group to  anklePivot
    anklePivot = cmds.xform(jointHierarchy[3], q=True, ws=True, piv=True);
    cmds.xform(kneeControlGrp, kneeControlGrpOffset, ws=True, piv=(anklePivot[0], anklePivot[1], anklePivot[2]));
            
    # parent hockIkhandle and kneeCtrl to pawCtrl
    cmds.parent(kneeControlGrpOffset, hockIkHandle, pawControlName);
    
    # pointConstraint pawCtrl to PoleVector for counterPlan of flip
    if isLower:
        cmds.pointConstraint(pawControlName, ikTibiaCtrlOffset, mo=True, w=True, )

    if isLower:
        cmds.parent(kneeControlGrpOffset, removeJntSuffix(jointHierarchy[2]) + driverSuffix);
        cmds.parent(hockIkHandle, removeJntSuffix(jointHierarchy[3]) + driverSuffix);
        cmds.parent(driverIkHandle, pawControlName);
    else:
        # cmds.parent(kneeControlGrpOffset, "root_ctrl");
        cmds.pointConstraint(pawControlName, kneeControlGrpOffset, w=True, mo=0, skip="y");
    
    cmds.orientConstraint(pawControlName, removeJntSuffix(jointHierarchy[3]) + ikSuffix, w=True, mo=0);
    
    # poleVector
    if isLower:
        cmds.poleVectorConstraint(kneeControlName, driverIkHandle, w=1);
    else:
        cmds.poleVectorConstraint(kneeControlName, kneeIkHandle, w=1);
            
        # adjust hockControler Translation
    if isLower:
        multiValue = 1;
    else:
        multiValue = 1;
    hockMulti = cmds.shadingNode("multiplyDivide", au=1, n=prefix + "_hock_multi");
    cmds.connectAttr(hockControlName + ".translate", hockMulti + ".input1", f=True);
    cmds.connectAttr(prefix + "_hock_multi.outputZ", kneeControlGrp + ".rotateX", f=True);
    cmds.connectAttr(prefix + "_hock_multi.outputX", kneeControlGrp + ".rotateZ", f=True);
    
    cmds.setAttr(hockMulti + ".input2X", multiValue*-1);
    cmds.setAttr(hockMulti + ".input2Z", multiValue);

    # add fk ik blending
    for i in range(bodyJoints):
        getConstraint = cmds.listConnections(jointHierarchy[i], type="parentConstraint")[0];
        print(getConstraint);
        getWeights = cmds.parentConstraint(getConstraint, q=True, wal=True);
        
        # fk ik weight connect
        cmds.connectAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", getConstraint + "." +  getWeights[0], f=True);
        cmds.connectAttr(fkikReverse + ".outputX", getConstraint + "." +  getWeights[1], f=True);
        
    # Organize group
    jntGroup = cmds.group(em=True, n=prefix + "_jnt_grp");
    cmds.matchTransform(jntGroup, jointRoot);
    cmds.makeIdentity(jntGroup, a=1, t=1, r=1, s=0);
    rootJntPrefix = removeJntSuffix(jointRoot);
    cmds.parent(rootJntPrefix + ikSuffix, rootJntPrefix + fkSuffix, rootJntPrefix + stretchSuffix, jntGroup);
    
    # parent driver jnt group
    if isLower:
        cmds.parent(rootJntPrefix + driverSuffix, jntGroup);
        
    cmds.parentConstraint(rootControlName, jntGroup, w=True, mo=True);
        
    # parent master jnt grp
    # cmds.parent(prefix + "_grp", "rig_systems");
    
    cmds.select(cl=True);
    
    #----------------------------------------
    # make Stretch
    stretchEndLoc = str(cmds.spaceLocator(n=prefix + "_stretchEndPos_loc")[0]);
    cmds.matchTransform(stretchEndLoc, jointHierarchy[3]);
    cmds.parent(stretchEndLoc, pawControlName);
    
    stretchLenPMA = cmds.shadingNode("plusMinusAverage", au=True, n=prefix + "_length");
    
    for i in range(bodyJoints):
        # ignore the last joint or it will try to use toes
        if i is not bodyJoints -1:
            tempDist = cmds.shadingNode("distanceBetween", au=True, n=jointHierarchy[i] + "_distnode");
            
            cmds.connectAttr(removeJntSuffix(jointHierarchy[i]) + stretchSuffix + ".worldMatrix", tempDist + ".inMatrix1", f=True);
            cmds.connectAttr(removeJntSuffix(jointHierarchy[i+1]) + stretchSuffix + ".worldMatrix", tempDist + ".inMatrix2", f=True);
            
            cmds.connectAttr(removeJntSuffix(jointHierarchy[i]) + stretchSuffix + ".rotatePivotTranslate", tempDist + ".point1", f=True);
            cmds.connectAttr(removeJntSuffix(jointHierarchy[i+1]) + stretchSuffix + ".rotatePivotTranslate", tempDist + ".point2", f=True);
            
            cmds.connectAttr(tempDist + ".distance", stretchLenPMA + ".input1D[" + str(i) + "]");
            
    stretchDist = cmds.shadingNode("distanceBetween", au=True, n=prefix + "_stretch_distnode");
    
    cmds.connectAttr(removeJntSuffix(jointHierarchy[0]) + stretchSuffix + ".worldMatrix", stretchDist + ".inMatrix1", f=True);
    cmds.connectAttr(stretchEndLoc + ".worldMatrix", stretchDist + ".inMatrix2", f=True);
    
    cmds.connectAttr(removeJntSuffix(jointHierarchy[0]) + stretchSuffix + ".rotatePivotTranslate", stretchDist + ".point1", f=True);
    cmds.connectAttr(stretchEndLoc + ".rotatePivotTranslate", stretchDist + ".point2", f=True);
    
    # scale factor
    scaleFactorMDN = cmds.shadingNode("multiplyDivide", au=1, n=prefix + "_scaleFactor");
    cmds.setAttr(scaleFactorMDN + ".operation", 2)# divide
    
    scaleCondition = cmds.shadingNode("condition", au=1, n=prefix + "_condition");
    cmds.setAttr(scaleCondition + ".operation", 2);# greater
    cmds.setAttr(scaleCondition + ".secondTerm", 1);
    
    cmds.connectAttr(stretchDist + ".distance", scaleFactorMDN + ".input1X", f=True);
    cmds.connectAttr(stretchLenPMA + ".output1D", scaleFactorMDN + ".input2X", f=True);
    cmds.connectAttr(scaleFactorMDN + ".outputX", scaleCondition + ".firstTerm", f=True);
    
    # connect scaleFactor per jnt
    for i in range(bodyJoints):
        cmds.connectAttr(scaleCondition + ".outColorR", removeJntSuffix(jointHierarchy[i]) + ikSuffix + ".scaleX", f=True);
    
        if isLower:
            cmds.connectAttr(removeJntSuffix(jointHierarchy[i]) + ikSuffix + ".scaleX", removeJntSuffix(jointHierarchy[i]) + driverSuffix +  ".scaleX", f=True);
            
    scaleBC = cmds.shadingNode("blendColors", au=True, n=prefix + "_blendColors");
    cmds.setAttr(scaleBC + ".color2", 1, 0, 0, type="double3");
    
    cmds.connectAttr(scaleFactorMDN + ".outputX", scaleBC + ".color1R", f=True);
    cmds.connectAttr(scaleBC + ".outputR", scaleCondition + ".colorIfTrueR", f=True);
    
    # add attr stretch manipurator
    cmds.addAttr(pawControlName, ln="Stretchiness", at="double", min=0, max=1, dv=1);
    cmds.setAttr(pawControlName + ".Stretchiness", e=True, keyable=True);
    cmds.connectAttr(pawControlName + ".Stretchiness", scaleBC + ".blender", f=True);
    
    cmds.addAttr(pawControlName, ln="StretchType", at="enum", en="Full:StretchOnly:SquashOnly", dv=1);
    cmds.setAttr(pawControlName + ".StretchType", e=True, keyable=True);
    cmds.setAttr(pawControlName + ".StretchType", 0);
    cmds.setAttr(scaleCondition + ".operation", 1);# not equal = stretch and squash
    
    # set Drivenkey strechType
    cmds.setDrivenKeyframe(scaleCondition + ".operation", cd=pawControlName + ".StretchType");
    
    # greater than = strechOnly
    cmds.setAttr(pawControlName + ".StretchType", 1);
    cmds.setAttr(prefix + "_condition.operation", 3);
    
    cmds.setDrivenKeyframe(prefix + "_condition.operation", cd=pawControlName + ".StretchType");
    
    # less or equal = squashOnly
    cmds.setAttr(pawControlName + ".StretchType", 2);
    cmds.setAttr(prefix + "_condition.operation", 5);
    
    cmds.setDrivenKeyframe(prefix + "_condition.operation", cd=pawControlName + ".StretchType");
    
    # set default
    cmds.setAttr(pawControlName + ".StretchType", 1);
    cmds.select(cl=True);
    
    #-----------------------
    # Volume Preservation
    volumeMDN = cmds.shadingNode("multiplyDivide", au=1, n=prefix + "_volume");
    cmds.setAttr(volumeMDN + ".operation", 3);# Power
    
    cmds.connectAttr(scaleBC + ".outputR", volumeMDN + ".input1X", f=True);
    cmds.connectAttr(volumeMDN + ".outputX", scaleCondition + ".colorIfTrueG", f=True);
    # radius or fibula
    cmds.connectAttr(scaleCondition + ".outColorG", jointHierarchy[1] + ".scaleY", f=True);
    cmds.connectAttr(scaleCondition + ".outColorG", jointHierarchy[1] + ".scaleZ", f=True);
    # carpus or tarsus
    cmds.connectAttr(scaleCondition + ".outColorG", jointHierarchy[2] + ".scaleY", f=True);
    cmds.connectAttr(scaleCondition + ".outColorG", jointHierarchy[2] + ".scaleZ", f=True);
    # volume attribute
    cmds.connectAttr(fkikSwitchCtrlOffset[1] + ".VolumeOffset", volumeMDN + ".input2X", f=True);
    
    #-----------------------
    # Add Roll Joints & Systems
    if whichSide == "l_":
        flipSide = 1;
    else:
        flipSide = -1;
    
    rollJointList = [jointHierarchy[0], jointHierarchy[3], jointHierarchy[0], jointHierarchy[0]];
    createdRollJntList = [];
    for i in range(len(rollJointList)):
        rollPrefix = removeJntSuffix(rollJointList[i]);
        # roll jnt to under that jnt, follow jnt chain to arm or leg root 
        if i > 2:
            rollJointName = rollPrefix + "_follow_tip_jnt";
        elif i > 1:
            rollJointName = rollPrefix + "_follow_jnt";
        else:
            rollJointName = rollPrefix + "_roll_jnt";
        
        cmds.joint(n=rollJointName, rad=2);
        cmds.matchTransform(rollJointName, rollJointList[i]);
        cmds.makeIdentity(rollJointName, a=1, t=0, r=1, s=0);
        
        if i < 2:
            cmds.parent(rollJointName, rollJointList[i]);
        elif i > 2:
            cmds.parent(rollJointName, removeJntSuffix(rollJointList[2]) + "_follow_jnt");
            
        createdRollJntList.append(rollJointName);
        cmds.select(cl=1);
    
    # follow tip jnt to mid position
    cmds.pointConstraint(jointHierarchy[0], jointHierarchy[1], createdRollJntList[3], w=0, mo=0, n="tempPC");
    cmds.delete("tempPC");
    
    cmds.move(0, 0, -10 * flipSide, createdRollJntList[2], r=1, os=1, wd=1);

    rollAimLoc = str(cmds.spaceLocator(n=removeJntSuffix(rollJointList[0]) + "_roll_aim")[0]);
    cmds.matchTransform(rollAimLoc, createdRollJntList[2]);
    cmds.parent(rollAimLoc, createdRollJntList[2]);
    cmds.move(0, 0, -5 * flipSide, rollAimLoc, r=1, os=1, wd=1);
    
    # aim roll to fibula
    cmds.aimConstraint(jointHierarchy[1], createdRollJntList[0], w=True, aim=[1,0,0], u=[0, 0, -1], wut="object", wuo=rollAimLoc, mo=1);
    
    # ik follow to follow tip
    cmds.ikHandle(n=prefix + "_follow_ikHandle", solver="ikRPsolver", sj=createdRollJntList[2], ee=createdRollJntList[3]);
    cmds.parent(prefix + "_follow_ikHandle", jointHierarchy[1]);
    cmds.matchTransform(prefix + "_follow_ikHandle", jointHierarchy[1]);
    
    cmds.setAttr(prefix + "_follow_ikHandle.poleVectorX", 0);
    cmds.setAttr(prefix + "_follow_ikHandle.poleVectorY", 0);
    cmds.setAttr(prefix + "_follow_ikHandle.poleVectorZ", 0);
    
    # Lower roll
    lowerRollAimLoc = str(cmds.spaceLocator(n=removeJntSuffix(rollJointList[1]) + "_roll_aim")[0]);
    cmds.matchTransform(lowerRollAimLoc, createdRollJntList[1]);
    cmds.parent(lowerRollAimLoc, jointHierarchy[3]);
    
    cmds.move(5 * flipSide, 0, 0, lowerRollAimLoc, r=1, os=1, wd=1);
    cmds.aimConstraint(jointHierarchy[2], createdRollJntList[1], w=True, aim=[0,1,0], u=[1, 0, 1], wut="object", wuo=lowerRollAimLoc, mo=1);
    
    
    cmds.parent(createdRollJntList[2], prefix + "_jnt_grp");
    cmds.select(cl=True);

# ------------------------------
# Methods
def removeJntSuffix(name):
    return name[:name.rfind("_jnt")];

def createCurveAndOffset(shape, controlerName, jnt, diameter):
    if(shape == 0):
        # Circle
        radius = diameter;
        cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=controlerName);
    elif(shape == 1):
        # Square
        point = diameter;
        cmds.curve(d=1, p=[(point, 0, point*-1), (point*-1, 0, point*-1), (point*-1, 0, point), (point, 0, point), (point, 0, point*-1)], k=[0, 1, 2, 3, 4], n=controlerName);
    elif(shape == 2):
        # Tri
        pointA = 1.03923 * diameter;
        pointB = 0.6 * diameter;
        pointC = 1.2 * diameter;
        cmds.curve(d=1, p=[(pointA*-1, 0, pointB), (pointA, 0, pointB), (0, 0, pointC*-1), (pointA*-1, 0, pointB)], k=[0, 1, 2, 3], n=controlerName);
    elif(shape == 3):
        # cube
        point = diameter * 0.5;
        cmds.curve(d=1, p=[(point, point, point), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point*-1, point*-1),(point, point*-1, point*-1), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point, point),(point, point, point), (point, point*-1, point), (point, point*-1, point*-1), (point*-1, point*-1, point*-1),(point*-1, point*-1, point), (point, point*-1, point), (point*-1, point*-1, point), (point*-1, point, point)],
        k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], n=controlerName);
    elif(shape == 4):
        # sphere
        mel.eval("curve -d 1 -p 0 0 1 -p 0 0.5 0.866025 -p 0 0.866025 0.5 -p 0 1 0 -p 0 0.866025 -0.5 -p 0 0.5 -0.866025 -p 0 0 -1 -p 0 -0.5 -0.866025 -p 0 -0.866025 -0.5 -p 0 -1 0 -p 0 -0.866025 0.5 -p 0 -0.5 0.866025 -p 0 0 1 -p 0.707107 0 0.707107 -p 1 0 0 -p 0.707107 0 -0.707107 -p 0 0 -1 -p -0.707107 0 -0.707107 -p -1 0 0 -p -0.866025 0.5 0 -p -0.5 0.866025 0 -p 0 1 0 -p 0.5 0.866025 0 -p 0.866025 0.5 0 -p 1 0 0 -p 0.866025 -0.5 0 -p 0.5 -0.866025 0 -p 0 -1 0 -p -0.5 -0.866025 0 -p -0.866025 -0.5 0 -p -1 0 0 -p -0.707107 0 0.707107 -p 0 0 1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -k 25 -k 26 -k 27 -k 28 -k 29 -k 30 -k 31 -k 32 -n {0};".format(controlerName));
    elif(shape == 5):
        # double normal
        mel.eval("curve -d 1 -p 0 0 -2.31 -p -0.99 0 -0.99 -p -0.33 0 -0.99 -p -0.33 0 0.99 -p -0.99 0 0.99 -p 0 0 2.31 -p 0.99 0 0.99 -p 0.33 0 0.99 -p 0.33 0 -0.99 -p 0.99 0 -0.99 -p 0 0 -2.31 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -n {0};".format(controlerName));
    else:
        # default circle
        radius = diameter;
        cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=controlerName);

    # offset_grp
    OFFSET_SUFFIX = "_offset_grp";
    offsetGrp = str(cmds.group(controlerName, n=controlerName + OFFSET_SUFFIX));
    pm.matchTransform(offsetGrp, jnt, pos=True, rot=True);

    return [offsetGrp, controlerName];

# create hierarchy for fk
def createFkHierarchy(fkAndOffsetList):
    fkparent = "";
    for i, ctrlAndOffet in enumerate(fkAndOffsetList):
        if i == 0:
            fkparent = ctrlAndOffet[1];
            continue;
        cmds.parent(ctrlAndOffet[0], fkparent);
        fkparent = ctrlAndOffet[1];

def createFKIKSwitchCtrl(side, prefix, posObj):
    # FKIKSwitch
    fkikSwitchCtrlOffset = createCurveAndOffset(5, prefix + "fkikSwitch_ctrl", posObj, 10);
    cmds.setAttr("{}.rotate".format(fkikSwitchCtrlOffset[0]), 0, 0, 0, type="double3");
    # cmds.move(10*side, 0, 0, fkikSwitchCtrlOffset[0], r=True, wd=True);
    cmds.addAttr(fkikSwitchCtrlOffset[1], ln="FKIKSwitch", at="double", min=0, max=1 ,dv=1);
    cmds.setAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", e=True, keyable=True);
    cmds.addAttr(fkikSwitchCtrlOffset[1], ln="stretch", at="double", min=0.0, max=1, dv=1);
    cmds.setAttr(fkikSwitchCtrlOffset[1] + ".stretch", e=True, keyable=True);
    cmds.addAttr(fkikSwitchCtrlOffset[1], ln="VolumeOffset", at="double", min=-0.5, max=3 ,dv=0);
    cmds.setAttr(fkikSwitchCtrlOffset[1] + ".VolumeOffset", e=True, keyable=True);
    fkikReverse = cmds.shadingNode("reverse", au=True, n=prefix + "_fkik_reverse");
    cmds.connectAttr(fkikSwitchCtrlOffset[1] + ".FKIKSwitch", fkikReverse + ".inputX", f=True);
    fkikSwitchCtrlOffset.append(fkikReverse);

    return fkikSwitchCtrlOffset;

def connectMainJntToFKIK(switchCtrl, mainJnts):
    # setup fkikSwitch
    for i, mainJnt in enumerate(mainJnts):
        fkJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_fk_jnt";
        ikJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_ik_jnt";
        transBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_trans_BC");
        rotBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_rot_BC");
        scaleBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_scale_BC");
        cmds.connectAttr(switchCtrl + ".FKIKSwitch", transBC + ".blender");
        cmds.connectAttr(switchCtrl + ".FKIKSwitch", rotBC + ".blender");
        cmds.connectAttr(switchCtrl + ".FKIKSwitch", scaleBC + ".blender");
        xyz = ["X", "Y", "Z"];
        rgb = ["R", "G", "B"];
        for i, axis in enumerate(xyz):
            cmds.connectAttr(fkJnt + ".translate" + axis, transBC + ".color2" + rgb[i]);
            cmds.connectAttr(ikJnt + ".translate" + axis, transBC + ".color1" + rgb[i]);
            cmds.connectAttr(transBC + ".output" + rgb[i], mainJnt + ".translate" + axis);
        for i, axis in enumerate(xyz):
            cmds.connectAttr(fkJnt + ".rotate" + axis, rotBC + ".color2" + rgb[i]);
            cmds.connectAttr(ikJnt + ".rotate" + axis, rotBC + ".color1" + rgb[i]);
            cmds.connectAttr(rotBC + ".output" + rgb[i], mainJnt + ".rotate" + axis);
        for i, axis in enumerate(xyz):
            cmds.connectAttr(fkJnt + ".scale" + axis, scaleBC + ".color2" + rgb[i]);
            cmds.connectAttr(ikJnt + ".scale" + axis, scaleBC + ".color1" + rgb[i]);
            cmds.connectAttr(scaleBC + ".output" + rgb[i], mainJnt + ".scale" + axis);

# ---------- setup Biped Arm or Leg ----------
def setupBiped(side, prefix, root, jointHierarchy):
    axisList = ["X", "Y", "Z"];
    armJointsNum = 3;
    ctrlRootList = [];
    
    jointHierarchy = jointHierarchy[:armJointsNum];
    fkikSwitchCtrlName = prefix + "fkikSwitch_ctrl";
    
    # print(side, prefix, root);
    sideNum = 1;
    if not side in "l_":
        sideNum = -1;
    fkikSwitchCtrlAndOffset = createFKIKSwitchCtrl(sideNum, prefix, root);
    ctrlRootList.append(fkikSwitchCtrlAndOffset[0]);

    newJointList = ["_fk_jnt", "_ik_jnt"];
    fkJointList =[];
    ikJointList = [];
    # create joint per mainJoints
    for i, newJoint in enumerate(newJointList):
        for o in range(armJointsNum):
            newJointName = removeJntSuffix(jointHierarchy[o]) + newJoint;
            cmds.joint(n=newJointName);
            cmds.matchTransform(newJointName, jointHierarchy[o]);
            cmds.makeIdentity(newJointName, a=1, t=0, r=1, s=0);

            if i == 0:
                fkJointList.append(newJointName);
            else:
                ikJointList.append(newJointName);

        cmds.select(cl=True);

    # setup fk and ik jnt to main jnt
    connectMainJntToFKIK(fkikSwitchCtrlName, jointHierarchy);

    # set up FK
    # fk controller
    fkCtrlList = [];
    for i in range(armJointsNum):
        fkCtrlName = removeJntSuffix(jointHierarchy[i]) + "_fk_ctrl";
        ctrlAndOffset = createCurveAndOffset(0, fkCtrlName, jointHierarchy[i], 10);
        cmds.orientConstraint(ctrlAndOffset[1], fkJointList[i]);
        fkCtrlList.append(ctrlAndOffset);
    # fk hierarchy
    createFkHierarchy(fkCtrlList);
    ctrlRootList.append(fkCtrlList[0][0]);
    
    # set up IK
    # prepare ctrl
    ikCtrlName = prefix + "Ik_ctrl";
    ikCtrlAndOffset = createCurveAndOffset(3, ikCtrlName, jointHierarchy[-1], 10);
    ctrlRootList.append(ikCtrlAndOffset[0]);
    
    # createIkhandle
    ikHandle = str(cmds.ikHandle(n=prefix + "ikHandle", solver="ikRPsolver", sj=ikJointList[0], ee=ikJointList[-1])[0]);
    cmds.parent(ikHandle, ikCtrlName);
    
    # ---------- create pv ctrl
    # setup pv
    pvCtrlName = prefix + "Ik_pv_ctrl";
    pvCtrlNameAndOffset = createCurveAndOffset(4, pvCtrlName, jointHierarchy[1], 10);
    ctrlRootList.append(pvCtrlNameAndOffset[0]);

    # adjustment pv position
    ikShoulderJntVec = om.MVector(cmds.xform(ikJointList[0], q=1, ws=1, t=1));
    ikElbowJntVec = om.MVector(cmds.xform(ikJointList[1], q=1, ws=1, t=1));
    ikHandJntVec = om.MVector(cmds.xform(ikJointList[2], q=1, ws=1, t=1));

    # vec length
    shoulderToElbowLen = ikElbowJntVec - ikShoulderJntVec;
    shoulderToHandLen = ikHandJntVec - ikShoulderJntVec;

    # normalize
    shoulderToHandLenNorm = shoulderToHandLen.normalize();
    # dot product length
    projLength = shoulderToElbowLen * shoulderToHandLenNorm;
    # dot product vector
    proj_vec = (shoulderToHandLenNorm * projLength) + ikShoulderJntVec;

    # vector dot product point to elbow
    projToElbowVec = ikElbowJntVec - proj_vec;
    projToElbowVecNorm = projToElbowVec.normalize();

    # result pole vector point
    resultPvPoint = ikElbowJntVec + (projToElbowVecNorm * 5);

    # place pvCtrl offset grp
    cmds.xform(pvCtrlNameAndOffset[0], t=resultPvPoint);   
    
    # pv const
    cmds.poleVectorConstraint(pvCtrlName, ikHandle);
    
    # follow attr
    cmds.addAttr(pvCtrlName, longName="Follow", at="enum", enumName="None:IkCtrl", min=0, max=1, defaultValue=1);
    cmds.setAttr(pvCtrlName + ".Follow", e=True, keyable=True);
    pvParentConst = cmds.parentConstraint(ikCtrlName, pvCtrlNameAndOffset[0], mo=True)[0];
    cmds.connectAttr("{}.Follow".format(pvCtrlName), "{}.{}W0".format(pvParentConst, ikCtrlName));

    # ---------- pv ctrl created
    
    # ---------- make Stretchness
    # create pos loc
    shoulderLoc = cmds.spaceLocator(n="{}_loc".format(ikJointList[0]))[0];
    ikCtrlLoc = cmds.spaceLocator(n="{}_loc".format(ikCtrlName))[0];
    cmds.setAttr("{}.visibility".format(shoulderLoc), 0);
    cmds.setAttr("{}.visibility".format(ikCtrlLoc), 0);
    
    # snap pos
    cmds.pointConstraint(ikJointList[0], shoulderLoc, mo=False);
    cmds.pointConstraint(ikCtrlName, ikCtrlLoc, mo=False);
    
    # get shape
    shoulderLocShape = cmds.listRelatives(shoulderLoc, s=True)[0];
    ikCtrlLocShape = cmds.listRelatives(ikCtrlLoc, s=True)[0];
    
    # create dist and connect
    distShape = cmds.createNode("distanceDimShape", n="{}stretch_distShape".format(prefix));
    distTrans = cmds.listRelatives(distShape, p=True)[0];
    cmds.setAttr("{}.visibility".format(distTrans), 0);
    cmds.connectAttr("{}.worldPosition[0]".format(shoulderLoc), "{}.startPoint".format(distShape));
    cmds.connectAttr("{}.worldPosition[0]".format(ikCtrlLocShape), "{}.endPoint".format(distShape));
    
    # create stretch factor
    stretchMd = cmds.createNode("multiplyDivide", n="{}stretchFactor_MD".format(prefix));
    cmds.setAttr("{}.operation".format(stretchMd), 2);
    cmds.connectAttr("{}.distance".format(distShape), "{}.input1X".format(stretchMd));
    
    # transform Scale
    transformScaleMd = cmds.createNode("multiplyDivide", n="transform_{}scale_MD".format(prefix));
    cmds.setAttr("{}.input1X".format(transformScaleMd), cmds.getAttr("{}.distance".format(distShape)));
    transformCtrl = cmds.ls("transform_ctrl");
    transformScalePMA = cmds.ls("transform_scale_PMA");
    
    if len(transformCtrl) > 0 and len(transformScalePMA) < 1:
        # transform scale average pma
        transformScalePMA = cmds.createNode("plusMinusAverage", n="transform_scale_PMA");
        for i, axis in enumerate(axisList):
            cmds.connectAttr("{}.scale{}".format(transformCtrl[0], axis), "{}.input1D[{}]".format(transformScalePMA, i));
            
        cmds.connectAttr("{}.output1D".format(transformScalePMA), "{}.input2X".format(transformScaleMd));
    cmds.connectAttr("{}.outputX".format(transformScaleMd), "{}.input2X".format(stretchMd));
    
    # stretch Factor condition
    stretchFactorCondition = cmds.createNode("condition", n="{}stretchFactor_condition");
    cmds.setAttr("{}.secondTerm".format(stretchFactorCondition), cmds.getAttr("{}.distance".format(distShape)));
    cmds.connectAttr("{}.distance".format(distShape), "{}.firstTerm".format(stretchFactorCondition));
    cmds.setAttr("{}.operation".format(stretchFactorCondition), 2);
    cmds.connectAttr("{}.outputX".format(stretchMd), "{}.colorIfTrueR".format(stretchFactorCondition));
    
    # stretch condition
    stretchCondition = cmds.createNode("condition", n="{}stretch_condition".format(prefix));
    cmds.setAttr("{}.secondTerm".format(stretchCondition), 1);
    cmds.connectAttr("{}.stretch".format(fkikSwitchCtrlName), "{}.firstTerm".format(stretchCondition));
    cmds.connectAttr("{}.outColorR".format(stretchFactorCondition), "{}.colorIfTrueR".format(stretchCondition));
    
    # volume offset
    volumeMd = cmds.createNode("multiplyDivide", n="{}volume_MD".format(prefix));
    cmds.setAttr("{}.operation".format(volumeMd), 3)
    cmds.connectAttr("{}.outColorR".format(stretchCondition), "{}.input1X".format(volumeMd));
    volumePma = cmds.createNode("plusMinusAverage", n="{}volume_PMA".format(prefix));
    cmds.setAttr("{}.input1D[0]".format(volumePma), 0);
    cmds.setAttr("{}.operation".format(volumePma), 2);
    cmds.connectAttr("{}.VolumeOffset".format(fkikSwitchCtrlName), "{}.input1D[1]".format(volumePma));
    cmds.connectAttr("{}.output1D".format(volumePma), "{}.input2X".format(volumeMd));
    
    # construct stretch connection each ik jnt
    for ikJnt in ikJointList[1:]:
        tempMd = cmds.createNode("multiplyDivide", n="{}_stretch_MD".format(ikJnt));
        defaultTx = cmds.getAttr("{}.tx".format(ikJnt));
        cmds.setAttr("{}.input1X".format(tempMd), defaultTx);
        cmds.connectAttr("{}.outColorR".format(stretchCondition), "{}.input2X".format(tempMd));
        cmds.connectAttr("{}.outputX".format(tempMd), "{}.translateX".format(ikJnt));
        for axis in axisList[1:]:
            cmds.connectAttr("{}.outputX".format(volumeMd), "{}.scale{}".format(ikJnt, axis));
    
    # ---------- adjustment
    # visibility setup
    cmds.setAttr(fkJointList[0] + ".visibility", 0);
    cmds.setAttr(ikJointList[0] + ".visibility", 0);
    cmds.setAttr(ikJointList[0] + ".visibility", 0);
    # fk vis
    cmds.connectAttr(fkikSwitchCtrlAndOffset[2] + ".outputX", str(cmds.listRelatives(fkCtrlList[0], p=True)[0]) + ".visibility");
    # ik vis
    cmds.connectAttr(fkikSwitchCtrlName + ".FKIKSwitch", ikCtrlAndOffset[0] + ".visibility");
    cmds.connectAttr(fkikSwitchCtrlName + ".FKIKSwitch", pvCtrlNameAndOffset[0] + ".visibility");

    # Organize
    ctrlGrp = cmds.group(n="{}ctrl_grp".format(prefix), em=True);
    cmds.parent(ctrlRootList, ctrlGrp);
    
    locGrp = cmds.ls("loc_grp");
    if len(locGrp) == 0:
        locGrp = cmds.group(n="loc_grp", em=True);
    cmds.parent([shoulderLoc, ikCtrlLoc, distTrans], locGrp);

# ------------------------------
# UI
# apply
def main():
    autoFKIKSetUpTool();
    om.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # layout, left:label, right:controler
        mainLayout = QtWidgets.QFormLayout(self);

        # input rigType RadioButton
        biped = QtWidgets.QRadioButton("Biped", self);
        quadruped = QtWidgets.QRadioButton("Quadruped", self);

        radioLayout = QtWidgets.QHBoxLayout(self);
        radioLayout.addWidget(biped, True);
        radioLayout.addWidget(quadruped, True);
        
        mainLayout.addRow("RigType", radioLayout);

        self.__rigType = QtWidgets.QButtonGroup(self);
        self.__rigType.addButton(biped, 0);
        self.__rigType.addButton(quadruped, 1);
    
        # input bodySide RadioButton
        arm = QtWidgets.QRadioButton("arm", self);
        leg = QtWidgets.QRadioButton("leg", self);

        radioLayout = QtWidgets.QHBoxLayout(self);
        radioLayout.addWidget(arm, True);
        radioLayout.addWidget(leg, True);
        
        mainLayout.addRow("BodySide", radioLayout);

        self.__bodySide = QtWidgets.QButtonGroup(self);
        self.__bodySide.addButton(arm, 0);
        self.__bodySide.addButton(leg, 1);

        self.initialize();

    # window default Settings
    def initialize(self):
        self.__rigType.button(settings.rigType).setChecked(True);
        self.__bodySide.button(settings.bodySide).setChecked(True);

    # set settings input
    def saveSettings(self):
        settings.rigType = self.__rigType.checkedId();
        settings.bodySide = self.__bodySide.checkedId();

    # set settings and do mainMehod
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Auto FKIK Setup Tool");
        self.resize(350, 200);

        toolWidget = qt.ToolWidget(self);
        self.setCentralWidget(toolWidget);

        optionWidget = OptionWidget(self);
        toolWidget.setOptionWidget(optionWidget);
        
        toolWidget.setActionName(self.windowTitle());
    
        toolWidget.applied.connect(optionWidget.apply);
        toolWidget.closed.connect(self.close);

class Settings(object):
    def __init__(self):
        # default Settings
        # setting rigtype biped or quadruped
        self.rigType = 0;
        # setting arm(front) or leg(rear)
        self.bodySide = 0;

settings = Settings();
    