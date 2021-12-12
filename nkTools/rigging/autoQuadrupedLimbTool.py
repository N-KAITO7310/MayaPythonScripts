import maya.cmds as cmds;

def autoQuadrupedLimbTool():
    
    isRearLeg = True;
    
    limbJoints = 4;
    
    if isRearLeg:
        limbType = "rear";
    else:
        limbType = "front";
        
    selectionCheck = cmds.ls(sl=True, type="joint");
    
    if not selectionCheck:
        cmds.error("Please select the root joint");
    else:
        jointRoot = cmds.ls(sl=True, type="joint")[0];
        
    whichSide = jointRoot[0:2];
    
    if not "l_" in whichSide:
        if not "r_" in whichSide:
            cmds.error("Please use a joint with a usable prefix of eigher l_ or r_");
            
    limbName = whichSide + "leg_" + limbType;
    
    mainControlName = limbName + "_ctrl";
    pawControlName = limbName + "_IK_ctrl";
    kneeControlName = limbName + "_tibia_ctrl";
    hockControlName = limbName + "_hock_ctrl";
    rootControlName = limbName + "_root_ctrl";
    
    jointHierarchy = cmds.listRelatives(jointRoot, ad=True, type="joint");
    
    jointHierarchy.append(jointRoot);
    
    jointHierarchy.reverse();
    
    cmds.select(cl=True);
    
    newJointList = ["_ik", "_fk", "_stretch"];
    
    if isRearLeg:
        newJointList.append("_driver");
        
    for newJoint in newJointList:
        for i in range(limbJoints):
            newJointName = jointHierarchy[i] + newJoint;
            
            cmds.joint(n=newJointName);
            cmds.matchTransform(newJointName, jointHierarchy[i]);
            cmds.makeIdentity(newJointName, a=1, t=0, r=1, s=0);
            
        cmds.select(cl=True);
        
    for i in range(limbJoints):
        cmds.parentConstraint(jointHierarchy[i] + "_ik", jointHierarchy[i] + "_fk", jointHierarchy[i], w=True, mo=0);
        
        
    for i in range(limbJoints):
        cmds.parentConstraint(jointHierarchy[i] + "_fk_ctrl", jointHierarchy[i] + "_fk", jointHierarchy[i], w=True, mo=0);
        
    if isRearLeg:
        cmds.ikHandle(n=limbName + "_driver_ikHandle", solver="ikRPsolver", sj=jointHierarchy[0] + "_driver", ee=jointHierarchy[3] + "_driver");
        
    cmds.ikHandle(n=limbName + "_knee_ikHandle", solver="ikRPsolver", sj=jointHierarchy[0] + "_ik", ee=jointHierarchy[2] + "_ik");
    cmds.ikHandle(n=limbName + "_hock_ikHandle", solver="ikSCsolver", sj=jointHierarchy[2] + "_ik", ee=jointHierarchy[3] + "_ik");
  
    cmds.group((limbName + "knee_ikHandle", n-limbName + "_knee_control"));
    cmds.group((limbName + "_knee_control", n-limbName + "_knee_control_offset"));
    
    
    anklePivot = cmds.xform(jointHierarchy[3], q=True, ws=True, piv=True);
    cmds.xform(limbName + "_knee_control", limbName + "_knee_control_offset", ws=True, piv=(anklePivot[0], anklePivot[1], anklePivot[2]));
            
            
    cmds.parent(limbName + "_knee_control_offset", limbName + "_hock_ikHandle", pawControlName);
            
    if isRearLeg:
        cmds.parent(limbName + "_knee_control_offset", jointHierarchy[2] + "_driver");
        cmds.parent(limbName + "_hock_ikHandle", jointHierarchy[3] + "_driver");
        cmds.parent(limbName + "_driver_ikHandle", pawControlName);
    else:
        cmds.parent(limbName + "_knee_control_offset", "root_ctrl");
        cmds.pointConstraint(pawControlName, limbName + "_knee_control_offset", w=True, mo=0);
    
    cmds.orientConstraint(pawControlName, jointHierarchy[3] + "_ik", w=True, mo=0);
    
    if isRearLeg:
        cmds.poleVectorConstraint(kneeControlName, limbName + "_driver_ikHandle", w=1);
    else:
            cmds.poleVectorConstraint(kneeControlName, limbName + "_knee_ikHandle", w=1);
            
    if isRearLeg:
        multiValue = 2.5;
    else:
        multiValue = 5;
    
    cmds.shadingNode("multiplyDivide", au=1, n=limbName + "_hock_multi");
    cmds.connectAttr(hockControlName + ".translate", limbName + "_hock_multi.input1", f+True);
    cmds.connectAttr(limbName + "_hock_multi.outputZ", limbName + "_knee_control.rotateX", f+True);
    cmds.connectAttr(limbName + "_hock_multi.outputX", limbName + "_knee_control.rotateZ", f+True);
    
    cmds.setAttr(limbName + "_hock_multi.output2X", multiValue*-1);
    cmds.setAttr(limbName + "_hock_multi.output2Z", multiValue);
    
    # add fk ik blending
    for i in range(limbJoints):
        getConstraint = cmds.listConnections(jointHierarchy[i], type="parentConstraint");
        getWeights = cmds.parentConstraint(getConstraint, q=True, wal=True);
        
        # fk ik weight connect
        cmds.connectAttr(mainControlName + ".FK_IK_Switch", getConstraint + "." +  getWeights[0], f+True);
        cmds.connectAttr(limbName + "_fkik_reverse.outputX", getConstraint + "." +  getWeights[1], f+True);
        
        
    cmds.group(em=True, n=limbName + "_grp");
    cmds.matchTransform(limbName + "_grp", jointRoot);
    cmds.makeIdentity(limbName + "_grp", a=1, t=1, r=1, s=0);
    
    cmds.parent(jointRoot + "_ik", jointRoot + "_fk", jointRoot + "_stretch", limbName + "_grp");
    
    if isRearLeg:
        cmds.parent(jointRoot + "_driver", limbName + "_grp");
        
    cmds.parentConstraint(rootControlName, limbName + "_grp", w=True, mo=True);
        
    cmds.parent(limbName + "_grp", "rig_systems");
    
    cmds.select(cl=True);
    
    #----------------------------------------
    # make Stretch
    cmds.spaceLocator(n=limbName + "stretchEndPos_loc");
    cmds.matchTransform(limbName + "stretchEndPos_loc", jointHierarchy[3]);
    cmds.parent(limbName + "stretchEndPos_loc", pawControlName);
    
    cmds.shadingNode("plusMinusAverage", au=True, n=limbName + "stretchEndPos_length");
    
    for i in range(limbJoints):
        
        # ignore th last joint or it will try to uset toes
        if i is not limbJoints -1:
            cmds.shadingNode("distanceBetween", au=True, n=jointHierarchy[i] + "_distnode");
            
            cmds.coonectAttr(jointHierarchy[i] + "_stretch.worldMatrix", limbName + "_distnode.inMatrix1", f=1);
            cmds.coonectAttr(jointHierarchy[i+1] + "_stretch.worldMatrix", limbName + "_distnode.inMatrix2", f=1);
            
            cmds.coonectAttr(jointHierarchy[i] + "_stretch.rotatePivotTranslate", limbName + "_distnode.point1", f=1);
            cmds.coonectAttr(jointHierarchy[i+1] + "_stretch.rotatePivotTranslate", limbName + "_distnode.point2", f=1);
            
            cmds.connectAttr(jointHierarchy[i+1] + "_distance.distance", limbName + "_length.input1D[" + str(i) + "]");
            
    cmds.shadingNode("distanceBetween", au=True, n=limbName + "_stretch_distnode");
    
    cmds.coonectAttr(jointHierarchy[0] + "_stretch.worldMatrix", limbName + "_stretch_distnode.inMatrix1", f=1);
    cmds.coonectAttr(limbName + "stretchEndPos_loc.worldMatrix", limbName + "_stretch_distnode.inMatrix2", f=1);
    
    cmds.coonectAttr(jointHierarchy[0] + "_stretch.rotatePivotTranslate", limbName + "_stretch_distnode.point1", f=1);
    cmds.coonectAttr(limbName + "stretchEndPos_loc.rotatePivotTranslate", limbName + "_stretch_distnode.point2", f=1);


    # scale factor
    cmds.shadingNode("multiplyDivide", au=1, n=limbName + "_scaleFactor");
    cmds.shadingNode("condition", au=1, n=limbName + "_condition");
    
    cmds.setAttr(limbName + "_condition.operation", 2);# greater
    cmds.setAttr(limbName + "_condition.secondTerm", 1);
    
    cmds.connectAttr(limbName + "_stretch_distance.distance", limbName + "_scaleFactor.input1X", f=True);
    
    cmds.connectAttr(limbName + "_length.output1D", limbName + "_scaleFactor.input2X", f=True);
    
    cmds.connectAttr(limbName + "_scaleFactor.outputX", limbName + "_condition.firstTerm", f=True);
    
    
    for i in range(limbJoints):
        cmds.connectAttr(limbName + "_condition.outColorR", jointHierarchy[i] + "_ik.scaleX", f=True);
    
        
        if isRearLeg:
            cmds.connectAttr(jointHierarchy[i] + "_ik.scaleX", jointHierarchy[i] + "_driver.scaleX", f=True);
            
    cmds.shadingNode("blendColors", au=True, n=limbName + "_blendColors");
    cmds.setAttr(limbName + "_blendColors.color2", 1, 0, 0, type="double3");
    
    cmds.connectAttr(limbName + "_scaleFactor.outputX", limbName + "_blendColors.color1R", f=True);
    cmds.connectAttr(limbName + "_blendColors.outputR", limbName + "_condition.colorIfTrueR", f=True);
    
    cmds.connectAttr(pawControlName + ".Stretchiness", limbName + "_blendColors.blender", f=True);
    
    # set Drivenkey strechType
    cmds.setAttr(pawControlName + ".StretchType", 0);
    cmds.setAttr(limbName + "_condition.operation", 1);# not equal
    
    cmds.setDrivenKeyframe(limbName + "_condition.operation", cd=pawControlName + ".StretchType");
    
    
    cmds.setAttr(pawControlName + ".StretchType", 1);
    cmds.setAttr(limbName + "_condition.operation", 3);# greater than
    
    cmds.setDrivenKeyframe(limbName + "_condition.operation", cd=pawControlName + ".StretchType");
    
    cmds.setAttr(pawControlName + ".StretchType", 2);
    cmds.setAttr(limbName + "_condition.operation", 5);# less or equal
    
    cmds.setDrivenKeyframe(limbName + "_condition.operation", cd=pawControlName + ".StretchType");
    
    cmds.setAttr(pawControlName + ".StretchType", 1);
    
    cmds.select(cl=True);
    
    #-----------------------
    # Volume Preservation
    cmds.shadingNode("multiplyDivide", au=1, n=limbName + "_volume");
    cmds.setAttr(limbName + "_volume.operation", 3);
    
    cmds.connectAttr(limbName + "_blendColors.outputR", limbName + "_volume.input1X", f=True);
    cmds.connectAttr(limbName + "_volume.outputX", limbName + "_condition.colorIfTrueG", f=True);
    # fibula
    cmds.connectAttr(limbName + "_condition.outColorG", jointHierarchy[1] + ".scaleY", f=True);
    cmds.connectAttr(limbName + "_condition.outColorG", jointHierarchy[1] + ".scaleZ", f=True);
    # metatarsus
    cmds.connectAttr(limbName + "_condition.outColorG", jointHierarchy[2] + ".scaleY", f=True);
    cmds.connectAttr(limbName + "_condition.outColorG", jointHierarchy[2] + ".scaleZ", f=True);
    # volume attribute
    cmds.connectAttr(mainControlName + ".Volume_Offset", limbName + "_volume.input2X", f=True);
    
    
    #-----------------------
    # Add Roll Joints & Systems
    if whichSide == "l_":
        flipSide = 1;
    else:
        flipSide = -1;
    
    rollJointList = [jointHierarchy[0], jointHierarchy[3], jointHierarchy[0], jointHierarchy[0]];
    
    for i in range(len(rollJointList)):
        if i > 2:
            rollJointName = rollJointList[i] + "_follow_tip";
        elif i > 1:
            rollJointName = rollJointList[i] + "_follow";
        else:
            rollJointName = rollJointList[i] + "_roll";
            
        
        cmds.joint(n=rollJointName, rad=2);
        cmds.matchTransform(rollJointName, jointHierarchy[i]);
        cmds.makeIdentity(rollJointName, a=1, t=0, r=0, s=0);
        
        if i < 2:
            cmds.parent(rollJointName, rollJointList[i]);
        elif i > 2:
            cmds.parent(rollJointName, rollJointList[2] + "follow");
            
        cmds.select(cl=1);
    
    
    cmds.pointConstraint(jointHierarchy[0], jointHierarchy[1], rollJointList[2] + "_follow_tip", w=0, m=0, n="tempPC");
    cmds.delete("tempPC");
    
    cmds.move(0, 0, -5 * flipSide, rollJointList[2] + "_follow_tip", r=1, os=1, wd=1);
    
    cmds.spaceLocator(n=rollJointList[0] + "_roll_aim");
    
    cmds.matchTransform(rollJointList[0] + "_roll_aim", rollJointList[2] + "_follow");
    cmds.parent(rollJointList[0] + "_roll_aim", rollJointList[2] + "_follow");
    
    cmds.move(0, 0, -5 * flipSide, rollJointList[2] + "_follow", r=1, os=1, wd=1);
    
    cmds.aimConstraint(jointHierarchy[1], rollJointList[0] + "_roll", w=True, aim=[1,0,0], u=[0, 0, -1], wut="object", wuo=rollJointList[0] + "_roll_aim", mo=1);
    
    cmds.ikHandle(n=limbName + "_follow_ikHandle", solver="ikRPsolver", sj=rollJointList[2] + "_follow", ee=rollJointList[2] + "_follow_tip");
    
    cmds.parent(limbName + "follow_ikHandle", jointHierarchy[1]);
    cmds.matchTransform(limbName + "_follow_ikHandle", jointHierarchy[1]);
    
    cmds.setAttr(limbName + "_follow_ikHandle.poleVectorX", 0);
    cmds.setAttr(limbName + "_follow_ikHandle.poleVectorY", 0);
    cmds.setAttr(limbName + "_follow_ikHandle.poleVectorZ", 0);
    
    
    # Lower leg System
    cmds.spaceLocator(n=rollJointList[1] + "_roll_aim");
    cmds.matchTransform(rollJointList[1] + "_roll_aim", rollJointList[2] + "_roll");
    cmds.parent(rollJointList[1] + "_roll_aim", rollJointList[3]);
    
    cmds.move(5 * flipSide, 0, 0, rollJointList[1] + "_roll_aim", r=1, os=1, wd=1);
    cmds.aimConstraint(jointHierarchy[2], rollJointList[1] + "_roll", w=True, aim=[0,1,0], u=[1, 0, 0], wut="object", wuo=rollJointList[1] + "_roll_aim", mo=1);
    
    
    cmds.parent(rollJointList[0] + "_follow", limbName + "_grp");
    
    cmds.select(cl=True);
    
    