import maya.cmds as cmds;

# delete under follicle curve
selected = cmds.ls(sl=True);
cmds.select(cl=True);
for i, s in enumerate(selected):
    curve = cmds.listRelatives(s, c=True, type="transform")
    cmds.delete(curve);

# rename follicles
selected = cmds.ls(sl=True);
cmds.select(cl=True);
follicles = [];
for i, s in enumerate(selected):
    i = str(i + 1);
    renamed = cmds.rename(s, "r_eyeBlow_ribbon_{0}_follicle".format(i.zfill(2)));
    follicles.append(renamed)
follicleGrp = str(cmds.listRelatives(follicles[0], p=True, type="transform")[0]);
cmds.rename(follicleGrp, "r_eyeBlow_ribbon_follicle_grp")
    
# create and rename jnt
selected = cmds.ls(sl=True);
cmds.select(cl=True);
for i, s in enumerate(selected):
    i = str(i + 1);
    cmds.select(s);
    joint = cmds.joint(n="r_eyeBlow_ribbon_{0}_jnt".format(i.zfill(2)))
    cmds.setAttr(joint + ".radius", 0.1);
    
# rename jnts zfill
selected = cmds.ls(sl=True);
cmds.select(cl=True);
follicles = [];
for i, s in enumerate(selected):
    i = str(i + 1);
    renamed = cmds.rename(s, "Chain_{0}_Jnt".format(i.zfill(3)));
    
# create Remap for jaw
jawJoint = "jaw_jnt";
jawControl = "jaw_ctrl";

offsetValue = 0;
controlList = cmds.ls(sl=1);

print(controlList);

prefix = str(controlList[0])[:str(controlList[0]).rfind("_ctrl")];
if len(controlList) > 1 :
    prefix2 = str(controlList[1])[:str(controlList[1]).rfind("_ctrl")];


multi = cmds.shadingNode("multiplyDivide", au=True, n=prefix + "_MDN");
remap = cmds.shadingNode("remapValue", au=True, n=prefix + "_remap");

cmds.connectAttr(jawJoint + ".rotate", multi + ".input1", f=True);
cmds.connectAttr(jawControl + ".LipInfluence", remap + ".inputValue", f=True);

xyzList = ["X", "Y", "Z"];
for i in xyzList:
    cmds.connectAttr(remap + ".outValue", multi + ".input2{}".format(i));
    
cmds.setAttr(remap + ".inputMin", offsetValue);
cmds.setAttr(remap + ".inputMax", offsetValue + 1);

cmds.connectAttr(multi + ".output", prefix + "_driver_grp.rotate", f=True);

if len(controlList) > 1:
    cmds.connectAttr(multi + ".output", prefix2 + "_driver_grp.rotate", f=True);


# create Remap fpr Eye
sidePrefix = str(cmds.ls(sl=True)[0])[:2];

eyeJoint = sidePrefix + "eye_jnt";
eyeControl = sidePrefix + "eye_ctrl";

offsetValue = 0;
controlList = cmds.ls(sl=1);

print(controlList);

prefix = str(controlList[0])[:str(controlList[0]).rfind("_ctrl")];
if len(controlList) > 1 :
    prefix2 = str(controlList[1])[:str(controlList[1]).rfind("_ctrl")];


multi = cmds.shadingNode("multiplyDivide", au=True, n=prefix + "_MDN");
remap = cmds.shadingNode("remapValue", au=True, n=prefix + "_remap");

pma = cmds.shadingNode("plusMinusAverage", au=True, n=prefix + "Blink_PMA");
cmds.connectAttr(eyeControl + ".BlinkHeight", pma + ".input1D[0]");
cmds.connectAttr(eyeControl + ".BlinkHeight", pma + ".input1D[1]");
cmds.disconnectAttr(eyeControl + ".BlinkHeight", pma + ".input1D[1]");
# input1D[1]への入力は各コントローラの回転値毎に手動で行う
cmds.connectAttr(pma + ".output1D", remap + ".outputMax");

# follow Eye
eyeInfPMA = cmds.shadingNode("plusMinusAverage", au=True, n=prefix + "_eyeInf_PMA");
eyeInfMulti = cmds.shadingNode("multiplyDivide", au=True, n=prefix + "_eyeInf_MDN");
cmds.connectAttr(eyeJoint + ".rotate", eyeInfMulti + ".input1");
cmds.connectAttr(eyeInfMulti + ".output", eyeInfPMA + ".input3D[0]");
cmds.connectAttr(multi + ".output", eyeInfPMA + ".input3D[1]");
cmds.connectAttr(eyeInfPMA + ".output3D", prefix + "_driver_grp" + ".rotate");
if len(controlList) > 1:
    cmds.connectAttr(eyeInfPMA + ".output3D", prefix2 + "_driver_grp" + ".rotate", f=True);

cmds.connectAttr(eyeControl + ".Blink", multi + ".input1X", f=True);
cmds.connectAttr(eyeControl + ".EyeInfluence", remap + ".inputValue", f=True);

xyzList = ["X", "Y", "Z"];
eyeInfRatio = 0.25
for i, axis in enumerate(xyzList):
    cmds.connectAttr(remap + ".outValue", multi + ".input2{}".format(axis));
    if "r_" in sidePrefix and i > 0:
        cmds.setAttr(eyeInfMulti + ".input2{0}".format(axis), eyeInfRatio * 1);
    else:
        cmds.setAttr(eyeInfMulti + ".input2{0}".format(axis), eyeInfRatio);
    
    
cmds.setAttr(remap + ".inputMin", offsetValue);
cmds.setAttr(remap + ".inputMax", offsetValue + 1);


# create driver grp
masterGroup = "r_eyeLid_ribbon_ctrl_grp";
selected = cmds.ls(sl=True);
driver = str(selected[0]);
ctrls = selected[1:];
for ctrl in ctrls:
    ctrl = str(ctrl);
    prefix = ctrl[:ctrl.rfind("_ctrl")];
    driverGrp = cmds.group(em=True, n=prefix + "_driver_grp");
    cmds.parent(driverGrp, masterGroup)
    cmds.matchTransform(driverGrp, driver, pos=True, rot=True, scl=True);
    ctrlOffset = str(cmds.listRelatives(ctrl, p=True)[0]);
    cmds.parent(ctrlOffset, driverGrp);
    
# match parentObj to under child
selected = cmds.ls(sl=True);
for i in selected:
    offset = str(i);
    parent = str(cmds.listRelatives(i, p=True)[0]);
    cmds.parent(i, w=True);
    cmds.matchTransform(parent, i, rot=True, pos=False, scl=False);
    cmds.parent(i, parent);
    
# create offset grp for under the group
masterGroup = "l_eyeLid_ribbon_ctrl_jnt_grp";
selected = cmds.ls(sl=True);
for obj in selected:
    obj = str(obj);
    prefix = obj[:obj.rfind("_grp")];
    offsetGrp = cmds.group(em=True, n=prefix + "_offset_grp");
    cmds.parent(offsetGrp, masterGroup)
    cmds.matchTransform(offsetGrp, obj, pos=True, rot=True, scl=True);
    cmds.parent(obj, offsetGrp);
    
# create offset grp withParenting
selected = cmds.ls(sl=True);
for obj in selected:
    obj = str(obj);
    parentObj = str(cmds.listRelatives(obj, p=True)[0]);
    prefix = obj[:obj.rfind("_grp")];
    offsetGrp = cmds.group(em=True, n=prefix + "_driver_grp");    
    cmds.matchTransform(offsetGrp, obj, pos=True, rot=True, scl=True);
    cmds.parent(offsetGrp, parentObj)
    cmds.parent(obj, offsetGrp);
    
# create offset grp world
selected = cmds.ls(sl=True);
for obj in selected:
    obj = str(obj);
    offsetGrp = cmds.group(em=True, n=obj + "_offset_grp");    
    cmds.matchTransform(offsetGrp, obj, pos=True, rot=True, scl=True);
    
# create jnt under joint 
posList = cmds.ls(sl=True);
cmds.select(cl=True);
for i, p in enumerate(posList):
    p = str(p);
    cmds.select(p);
    jnt = str(cmds.joint());
    cmds.parent(jnt, w=True);
    cmds.delete(p);
    cmds.select(cl=True);
    

# create jnt same position by pointConstraint
posList = cmds.ls(sl=True);
cmds.select(cl=True);
for i, p in enumerate(posList):
    p = str(p);
    jnt = str(cmds.joint());
    pc = str(cmds.pointConstraint(p, jnt, mo=False)[0]);
    cmds.delete(pc);
    cmds.delete(p);
    cmds.select(cl=True);

# create fk ik system
switchCtrl = str(cmds.ls(sl=True)[0]);
baseJnts = cmds.ls(sl=True)[1:];
for baseJnt in baseJnts:
    baseJnt = str(baseJnt);
    fkJnt = baseJnt[:baseJnt.rfind("_jnt")] + "_fk_jnt";
    ikJnt = baseJnt[:baseJnt.rfind("_jnt")] + "_ik_jnt";
    reverse = switchCtrl + "_reverse";
    transBC = cmds.shadingNode("blendColors", au=True, n=baseJnt + "_trans_BC");
    rotBC = cmds.shadingNode("blendColors", au=True, n=baseJnt + "_rot_BC");
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", transBC + ".blender");
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", rotBC + ".blender");
    xyz = ["X", "Y", "Z"];
    rgb = ["R", "G", "B"];
    for i, axis in enumerate(xyz):
        cmds.connectAttr(fkJnt + ".translate" + axis, transBC + ".color2" + rgb[i]);
        cmds.connectAttr(ikJnt + ".translate" + axis, transBC + ".color1" + rgb[i]);
        cmds.connectAttr(transBC + ".output" + rgb[i], baseJnt + ".translate" + axis);
    for i, axis in enumerate(xyz):
        cmds.connectAttr(fkJnt + ".rotate" + axis, rotBC + ".color2" + rgb[i]);
        cmds.connectAttr(ikJnt + ".rotate" + axis, rotBC + ".color1" + rgb[i]);
        cmds.connectAttr(rotBC + ".output" + rgb[i], baseJnt + ".rotate" + axis);
        
# create fk ik system scale only
switchCtrl = str(cmds.ls(sl=True)[0]);
baseJnts = cmds.ls(sl=True)[1:];
for baseJnt in baseJnts:
    baseJnt = str(baseJnt);
    fkJnt = baseJnt[:baseJnt.rfind("_jnt")] + "_fk_jnt";
    ikJnt = baseJnt[:baseJnt.rfind("_jnt")] + "_ik_jnt";
    reverse = switchCtrl + "_reverse";
    scaleBC = cmds.shadingNode("blendColors", au=True, n=baseJnt + "_scale_BC");
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", scaleBC + ".blender");
    xyz = ["X", "Y", "Z"];
    rgb = ["R", "G", "B"];
    for i, axis in enumerate(xyz):
        cmds.connectAttr(fkJnt + ".scale" + axis, scaleBC + ".color2" + rgb[i]);
        cmds.connectAttr(ikJnt + ".scale" + axis, scaleBC + ".color1" + rgb[i]);
        cmds.connectAttr(scaleBC + ".output" + rgb[i], baseJnt + ".scale" + axis);
        
# setup ikStretchScale from ikSpline 
curve = str(cmds.ls(sl=True)[0]);
stretchJnts = cmds.ls(sl=True)[1:];
prefix = "l_wing_index";
fkikSwitch = "l_wing_pbalanges_FKIKSwitch_ctrl"
curveInfo = cmds.shadingNode("curveInfo", au=True, n=curve + "_curveInfo");
cmds.connectAttr(curve + ".worldSpace[0]", curveInfo + ".inputCurve");
stretchMDN = cmds.shadingNode("multiplyDivide", au=True, n=prefix + "_stretch_MDN");
cmds.setAttr(stretchMDN + ".operation", 2);
cmds.connectAttr(curveInfo + ".arcLength", stretchMDN + ".input1X");
cmds.setAttr(stretchMDN + ".input2X", cmds.getAttr(curveInfo + ".arcLength"));
scaleBC = cmds.shadingNode("blendColors", au=True, n=prefix + "_stretch_BC");
cmds.connectAttr(fkikSwitch + ".FKIKSwitch", scaleBC + ".blender");
cmds.connectAttr(stretchMDN + ".outputX", scaleBC + ".color1R");
for jnt in stretchJnts:
    jnt = str(jnt);
    if "_ik_" in jnt:
        cmds.connectAttr(stretchMDN + ".outputX", jnt + ".scaleX");
    else:
        cmds.connectAttr(scaleBC + ".color1R", jnt + ".scaleX");
        

# proximityPin用のコントローラグループにドライバを設定しコンストレイントする(ProximityPinは手動で行う)
targetGrps = cmds.ls(sl=True);
for targetGrp in targetGrps:
    target = str(targetGrp);
    prefix = target[:target.rfind("offset_grp")];
    driverGrp = cmds.group(em=True, n=prefix + "proximityPin_driver");
    cmds.matchTransform(driverGrp, target);
    cmds.parent(driverGrp, target);
    auto = str(cmds.listRelatives(target, c=True)[0]);
    ctrl = str(cmds.listRelatives(auto, c=True)[0]);
    cmds.pointConstraint(driverGrp, auto, mo=False);

# followコントローラとスキンジョイント用コントローラとを接続する
ctrls = cmds.ls(sl=True);
for ctrl in ctrls:
    followCtrl = str(ctrl);
    ctrl = followCtrl.replace("_follow_ctrl", "");
    auto = str(cmds.listRelatives(p=True)[0]);
    print(auto);
    cmds.connectAttr(followCtrl + ".translate", ctrl + ".translate");
    cmds.connectAttr(followCtrl + ".rotate", ctrl + ".rotate");

# parent: multi shape to one parent
parent = cmds.ls(sl=True)[0];
childList = cmds.ls(sl=True)[1:];
for child in childList:
    child = str(child);
    shape = cmds.listRelatives(child, s=True);
    cmds.parent(shape, parent, add=True, s=True);
    cmds.delete(child);
    
# parent: one shape to one parent
shapeTrans = cmds.ls(sl=True)[0];
shape = str(cmds.listRelatives(shapeTrans, s=True)[0]);
offset = str(cmds.listRelatives(shapeTrans, p=True)[0]);
target = cmds.ls(sl=True)[1];
targetOriginalShape = cmds.listRelatives(target, s=True);
cmds.parent(shape, target, add=True, s=True);
cmds.delete(targetOriginalShape);
cmds.delete(offset);

# copy shape to each ctrls
origCtrl = cmds.ls(sl=True)[0];
targetCtrlList = cmds.ls(sl=True)[1:];
for targetCtrl in targetCtrlList:
    dupCtrl = cmds.duplicate(origCtrl, rc=True)[0];
    cmds.matchTransform(dupCtrl, targetCtrl);
    
    shape = cmds.listRelatives(dupCtrl, s=True)[0];
    targetCtrlShape = cmds.listRelatives(targetCtrl, s=True)[0];
    
    cmds.parent(shape, targetCtrl, s=True, add=True)
    cmds.delete(targetCtrlShape);
    cmds.delete(dupCtrl);


# for gameEngine:reset joint rotate axis offset
joints = cmds.ls(sl=True);
for jnt in joints:
    jnt = str(jnt);
    cmds.joint(jnt, e=True, zso=True);

# add a proxy attribute
parentCtrlName = "l_arm_fkikSwitch_ctrl"
cmds.addAttr(ln="IKFKSwitch", proxy="{0}.FKIKSWitch".format(parentCtrlName));

# set overrideEnabled
objs = cmds.ls(sl=True);
for obj in objs:
    obj = str(obj);
    cmds.setAttr("{0}.overrideEnabled".format(obj), 1);
   
# culc pole vec ctrl
pointA = om.MVector(cmds.xform("IK_shoulder_Jnt", q=1, ws=1, t=1));
pointB = om.MVector(cmds.xform("IK_elbow_Jnt", q=1, ws=1, t=1));
pointC = om.MVector(cmds.xform("IK_wrist_Jnt", q=1, ws=1, t=1));

# vec length
AB = pointB - pointA;
AC = pointC - pointA;

ACNormalize = AC.normalize();
projLength = AB * ACNormalize;

proj_vec = (ACNormalize * projLength) + pointA;

PB = pointB - proj_vec;
PBNorm = PB.normalize();

result = pointB + (PBNorm * 5);

cmds.xform("IK_PV_Ctrl_Offset_Grp", t=result);   
    
# implicit
cmds.createNode("implicitCone");
cmds.createNode("implicitSphere");

# create fixed Ik Stretch System
curveShape = "HydraTail_curveShape";
jntList = cmds.ls(sl=True);
orgLength = cmds.createNode("plusMinusAverage", n="orgLength");
pma = None;
pmaList = [];
locList = [];
for i, jnt in enumerate(jntList):
    if i == 0:
        poci = cmds.createNode("pointOnCurveInfo", n="{}_pointOnCurveInfo".format(jnt));
        cmds.connectAttr("{}.local".format(curveShape), "{}.inputCurve".format(poci));
        posLoc = str(cmds.spaceLocator()[0]);
        cmds.connectAttr("{}.position".format(poci), "{}.translate".format(posLoc));
        locList.append(posLoc);
        continue;
    
    jnt = str(jnt);
    cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(orgLength, i));
    pma = cmds.createNode("plusMinusAverage", n="{}_PMA".format(jnt));
    if len(pmaList) != 0:
        cmds.connectAttr("{}.output1D".format(pmaList[-1]), "{}.input1D[{}]".format(pma, 0));
        cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(pma, 1));
    else:
        cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(pma, 0));
        
    fm = cmds.createNode("floatMath", n="{}_FM".format(jnt));
    cmds.setAttr("{}.operation".format(fm), 3);
    cmds.connectAttr("{}.output1D".format(pma), "{}.floatA".format(fm));
    cmds.connectAttr("{}.output1D".format(orgLength), "{}.floatB".format(fm));
    
    poci = cmds.createNode("pointOnCurveInfo", n="{}_pointOnCurveInfo".format(jnt));
    cmds.connectAttr("{}.local".format(curveShape), "{}.inputCurve".format(poci));
    
    cmds.connectAttr("{}.outFloat".format(fm), "{}.parameter".format(poci));
    
    posLoc = str(cmds.spaceLocator()[0]);
    cmds.connectAttr("{}.position".format(poci), "{}.translate".format(posLoc));
    
    pmaList.append(pma);
    locList.append(posLoc);
    
scaleFactorFMList = [];
for i in range(len(locList) - 1):
    dist = cmds.createNode("distanceBetween");
    cmds.connectAttr("{}.translate".format(locList[i]), "{}.point1".format(dist));
    cmds.connectAttr("{}.translate".format(locList[i+1]), "{}.point2".format(dist));
    
    scaleFactorFM = cmds.createNode("floatMath", n="scaleFactor_{}_FM".format(i));
    cmds.setAttr("{}.operation".format(scaleFactorFM), 3);
    cmds.connectAttr("{}.distance".format(dist), "{}.floatA".format(scaleFactorFM));
    cmds.connectAttr("{}.distance".format(dist), "{}.floatB".format(scaleFactorFM));
    cmds.disconnectAttr("{}.distance".format(dist), "{}.floatB".format(scaleFactorFM));
    
    scaleFactorFMList.append(scaleFactorFM);
    
for i, fm in enumerate(scaleFactorFMList):
    cmds.connectAttr("{}.outFloat".format(fm), "{}.scaleX".format(jntList[i]));

# for fixed Ik Stretch System ScaleBugFix
scaleRatio = "transform_ctrl_scale_ratio_FM";
targets = cmds.ls("tongue_scaleFactor_*_FM");
for target in targets:
    target = str(target);
    num = target.split("_")[1];
    fm = cmds.createNode("floatMath", n="tongue_scaleFactor_{}_transformRatio_FM".format(num));
    cmds.setAttr("{}.operation".format(fm), 2);
    cmds.connectAttr("{}.outFloat".format(scaleRatio), "{}.floatA".format(fm));
    defaultAttr = cmds.getAttr("{}.floatB".format(target));
    cmds.setAttr("{}.floatB".format(fm), defaultAttr);
    cmds.connectAttr("{}.outFloat".format(fm), "{}.floatB".format(target));

# mothion path example like snake
curve = "animate_curve"
endLoc = "animate_curve_end_loc";
curveInfo = "animate_curveInfo";
sel = cmds.ls(sl=True)
for i, default in enumerate(sel):
    num = str(i + 26).zfill(2)
    dist = cmds.createNode("distanceBetween", n="animate_curve_{}_dist".format(num));
    cmds.connectAttr("{}.translate".format(endLoc), "{}.point1".format(dist))
    cmds.connectAttr("{}.translate".format(default), "{}.point2".format(dist))
    
    ratioFM = cmds.createNode("floatMath", n="animate_curve_{}_distRatio_FM".format(num))
    cmds.setAttr("{}.operation".format(ratioFM), 3)
    cmds.connectAttr("{}.distance".format(dist), "{}.floatA".format(ratioFM))
    cmds.connectAttr("{}.arcLength".format(curveInfo), "{}.floatB".format(ratioFM))
    
    reverseFM = cmds.createNode("floatMath", n="animate_curve_{}_distRatio_reverse_FM".format(num))
    cmds.setAttr("{}.operation".format(reverseFM), 1)
    cmds.connectAttr("{}.outFloat".format(ratioFM), "{}.floatB".format(reverseFM))
    
    controlFM = cmds.createNode("floatMath", n="animate_curve_{}_distRatio_control_FM".format(num))
    cmds.setAttr("{}.floatB".format(controlFM), 0)
    cmds.connectAttr("{}.outFloat".format(reverseFM), "{}.floatA".format(controlFM))
    
    driverLoc = "motionPath_driver_{}_loc".format(num)
    mel.eval('pathAnimation -fractionMode true -follow true -followAxis x -upAxis y -worldUpType "vector" -worldUpVector 0 1 0 -inverseUp false -inverseFront false -bank false -startTimeU 1 -endTimeU 100 {} {};'.format(driverLoc, curve))
    path = cmds.rename("motionPath{}".format(i+26), "motionPath_{}".format(num));
    cmds.connectAttr("{}.outFloat".format(controlFM), "{}.uValue".format(path), f=True)
      
# browse maya img default resouce
import maya.app.general.resourceBrowser as resourceBrowser;
resourceBrowser.resourceBrowser().run();

# SkinTransfer Python
def objectSel():
    if len(cmds.ls(sl=True)) < 2:
        return False;
    else:
        objects = cmds.listRelatives(s=True);
        shapehistory = cmds.listHistory(objects[0], lv=3);
        skc = cmds.ls(shapehistory, typ="skinCluster");
        target = cmds.ls(sl=True)[-1];
        assignSkc(skc, target);
        return True;

    
def assignSkc(skc, target):
    shapeHistory = cmds.listHistory(target, lv=3);
    oldSkc = cmds.ls(shapeHistory, typ="skinCluster");
    if oldSkc:
        cmds.delete(oldSkc);
        
    jnt = cmds.skinCluster(skc, weightedInfluence=True, q=True);
    newSkc = cmds.skinCluster(jnt, target);
    cmds.copySkinWeights(ss=sck[0], ds=newSkc[0], nm=True, surfaceAssociation="closestPoint");
    cmds.rename(newSkc, skc[0]);

    return newSkc;
    
objectSel();

"""
constraint mesh by closestPoint and Follicle
"""
# first select constrained then geo
sl = cmds.ls(sl=True);

closest = cmds.createNode("closestPointOnMesh");
cmds.connectAttr(sl[1] + ".outMesh", closest + ".inMesh");

trans = cmds.xform(sl[0], t=True, q=True);
cmds.setAttr(closest + ".inPositionX", trans[0]);
cmds.setAttr(closest + ".inPositionY", trans[1]);
cmds.setAttr(closest + ".inPositionZ", trans[2]);

follicle = cmds.createNode("follicle");
follicleTrans = cmds.listRelatives(follicle, type="transform", p=True);
cmds.connectAttr(follicle + ".outRotate", follicleTrans[0] + ".rotate");
cmds.connectAttr(follicle + ".outTranslate", follicleTrans[0] + ".translate");

cmds.connectAttr(sl[1] + ".worldMatrix", follicle + ".inputWorldMatrix");
cmds.connectAttr(sl[1] + ".outMesh", follicle + ".inputMesh");
cmds.setAttr(follicle + ".simulationMethod", 0);
parameterU = cmds.getAttr(closest + ".result.parameterU");
parameterV = cmds.getAttr(closest + ".result.parameterV");

cmds.setAttr(follicle + ".parameterU", parameterU);
cmds.setAttr(follicle + ".parameterV", parameterV);

cmds.parentConstraint(follicleTrans[0], sl[0], mo=True);
cmds.delete(closest);
