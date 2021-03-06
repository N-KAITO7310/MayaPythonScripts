# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;

"""
create:2021/11/22

install
from nkTools.rigging import autoDynamicsSetupTool;
reload(autoDynamicsSetupTool);
reload(autoDynamicsSetupTool.qt);
autoDynamicsSetupTool.option();

how to use
1. first select mainRootJnt
2. second select prepared ikCurve
3. input fkikSwitchCtrlName
4. load ikCtrl position jnt
"""

def autoDynamicsSetupTool():
    # create fk ik system
    mainTopJnt = str(cmds.ls(sl=True)[0]);
    curve = str(cmds.ls(sl=True)[1]);
    switchCtrl = settings.FKIKSwitchName;

    mainChildJnts = cmds.listRelatives(mainTopJnt, ad=True, type="joint");
    mainJnts = [mainTopJnt];
    mainChildJnts.reverse();
    for c in mainChildJnts:
        mainJnts.append(str(c));

    basePrefix = settings.prefix;

    # FKIKSwitch
    if settings.createFKIKSwitch:
        switchCtrl = basePrefix + "_fkikSwitch_ctrl";
        mel.eval("curve -d 1 -p 0 0 -2.31 -p -0.99 0 -0.99 -p -0.33 0 -0.99 -p -0.33 0 0.99 -p -0.99 0 0.99 -p 0 0 2.31 -p 0.99 0 0.99 -p 0.33 0 0.99 -p 0.33 0 -0.99 -p 0.99 0 -0.99 -p 0 0 -2.31 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -n {0};".format(switchCtrl));
        fkikSwitchCtrlOffset = cmds.group(switchCtrl, n=switchCtrl + "_offset_grp");
        cmds.matchTransform(fkikSwitchCtrlOffset, mainTopJnt);
        cmds.move(0, 10, 0, fkikSwitchCtrlOffset, r=True, wd=True);
        cmds.addAttr(switchCtrl, ln="FKIKSwitch", at="double", min=0, max=1 ,dv=0);
        cmds.setAttr(switchCtrl + ".FKIKSwitch", e=True, keyable=True);
        cmds.addAttr(switchCtrl, ln="Simulation", at="double", min=0, max=1 ,dv=0);
        cmds.addAttr(switchCtrl, ln="dynamicsOption", nn="----------", at="enum", en="DYNAMICS:");
        cmds.setAttr(switchCtrl + ".Simulation", e=True, keyable=True);
        cmds.addAttr(switchCtrl, ln="FollowPose", at="double", min=0, max=1 ,dv=1);
        cmds.setAttr(switchCtrl + ".FollowPose", e=True, keyable=True);
        cmds.addAttr(switchCtrl, ln="Drag", at="double", dv=1);
        cmds.setAttr(switchCtrl + ".Drag", e=True, keyable=True);
        cmds.addAttr(switchCtrl, ln="Turbulence", at="double", dv=0);
        cmds.setAttr(switchCtrl + ".Turbulence", e=True, keyable=True);
    ikfkReverse = cmds.shadingNode("reverse", n=switchCtrl + "_reverse", au=True);
    
    # duplicate jnts
    fkikPrefix = ["fk", "ik"];
    fkList = [];
    ikList = [];
    for fkik in fkikPrefix:
        # root duplicate
        duplicateJnts = cmds.duplicate(mainTopJnt, renameChildren=True);
        # rename
        for i, dup in enumerate(duplicateJnts):
            dup = str(dup);
            jntPrefix = dup[:dup.rfind("_jnt")];
            renamed = str(cmds.rename(dup, jntPrefix + "_" + fkik + "_jnt"));

            if "fk" in renamed:
                fkList.append(renamed);
            else:
                ikList.append(renamed);
    
    # setup fkikSwitch
    for i, mainJnt in enumerate(mainJnts):
        if i == len(mainJnts)-1:
            break;
        mainJnt = str(mainJnt);
        fkJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_fk_jnt";
        ikJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_ik_jnt";
        transBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_trans_BC");
        rotBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_rot_BC");
        cmds.connectAttr(switchCtrl + ".FKIKSwitch", transBC + ".blender");
        cmds.connectAttr(switchCtrl + ".FKIKSwitch", rotBC + ".blender");
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

    ctrlSuffix = "_ctrl";
    offsetSuffix = "_offset_grp";
    hierarchyParent = "";
    fkCtrlTopOffset = "";
    fkCtrlGrp = cmds.group(em=True, n=basePrefix + "_fk_ctrl_grp");
    # fkSetup
    for i, fkJnt in enumerate(fkList):
        if i == len(fkList) -1:
            break;
        # offset, controler?????????
        ctrlPrefix = fkJnt[:fkJnt.rfind("_jnt")];
        ctrlName = ctrlPrefix + ctrlSuffix;
        radius = 1;
        cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=ctrlName);
        offsetGroup = str(cmds.group(ctrlName, n=ctrlName + offsetSuffix));
        cmds.matchTransform(offsetGroup, fkJnt);
        cmds.orientConstraint(ctrlName, fkJnt, mo=False);

        if i == 0:
            hierarchyParent = ctrlName;
            cmds.parent(offsetGroup, fkCtrlGrp);
            fkCtrlTopOffset = offsetGroup;
        else:
            cmds.parent(offsetGroup, hierarchyParent);
            hierarchyParent = ctrlName;
    
    # ikSplineSetup
    ikStartJnt = ikList[0];
    ikEndJnt = ikList[len(ikList)-1];
    ikCtrlCreatePosList = settings.ikCtrlJntPosList;
    ikCtrlCreatePosList.insert(0, ikStartJnt);

    # ikSpline apply
    cmds.ikHandle(sj=ikStartJnt, ee=ikEndJnt, curve=curve,
        sol="ikSplineSolver", ccv=False, roc=False, pcv=False, ns=3, n=basePrefix + "_ikHandle");

    ikCtrlJnts = [];
    ikCtrls = [];
    cmds.select(cl=True);
    ikCtrlGrp = cmds.group(em=True, name=basePrefix + "_ik_ctrl_grp");
    ikCtrlJntGrp = cmds.group(em=True, name=basePrefix + "_ik_ctrlJnt_grp");
    for i, ik in enumerate(ikCtrlCreatePosList):
        cmds.select(cl=True);
        ctrlJnt = cmds.joint(n=ik[:ik.rfind("_ik_jnt")] + "_ikCtrl_jnt");
        cmds.matchTransform(ctrlJnt, ik);
        ikCtrlJnts.append(ctrlJnt);
        cmds.parent(ctrlJnt, ikCtrlJntGrp);
        
        if i == 0:
            # start jnt not ctrl
            continue;

        # create ikCtrl
        ikCtrlName = basePrefix + "_" + str(i+1).zfill(2) + "_ik_ctrl";
        mel.eval('curve -d 1 -p 0 0 -1.1025 -p -0.33 0 -0.6075 -p -0.165 0 -0.6075 -p -0.165 0 -0.165 -p -0.6075 0 -0.165 -p -0.6075 0 -0.33 -p -1.1025 0 0 -p -0.6075 0 0.33 -p -0.6075 0 0.165 -p -0.165 0 0.165 -p -0.165 0 0.6075 -p -0.33 0 0.6075 -p 0 0 1.1025 -p 0.33 0 0.6075 -p 0.165 0 0.6075 -p 0.165 0 0.165 -p 0.6075 0 0.165 -p 0.6075 0 0.33 -p 1.1025 0 0 -p 0.6075 0 -0.33 -p 0.6075 0 -0.165 -p 0.165 0 -0.165 -p 0.165 0 -0.6075 -p 0.33 0 -0.6075 -p 0 0 -1.1025 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 -n "{0}"'.format(ikCtrlName));
        ikOffsetGrp = cmds.group(ikCtrlName, n=ikCtrlName + "_offset_grp");
        cmds.connectAttr(ikfkReverse + ".outputY", ikOffsetGrp + ".visibility");
        cmds.matchTransform(ikOffsetGrp, ctrlJnt);
        cmds.parentConstraint(ikCtrlName, ctrlJnt, mo=False);
        cmds.parent(ikOffsetGrp, ikCtrlGrp);
        ikCtrls.append(ikCtrlName);
    cmds.parent(basePrefix + "_ikHandle", ikCtrlGrp);

    # bind ikCtrlJnt to Curve
    kwargs = {
                'tsb': True,
                'bm': 0,
                'sm': 0,
                'nw': 1,
                'weightDistribution':1,
                'mi':3,
                'omi':False,
                'dr':4
            }
    cmds.skinCluster(ikCtrlJnts, curve, **kwargs);

    # setup ikStretchScale from ikSpline 
    stretchJnts = mainJnts[:-1] + ikList[:-1];
    curveInfo = cmds.shadingNode("curveInfo", au=True, n=curve + "_curveInfo");
    cmds.connectAttr(curve + ".worldSpace[0]", curveInfo + ".inputCurve");
    stretchMDN = cmds.shadingNode("multiplyDivide", au=True, n=basePrefix + "_stretch_MDN");
    cmds.setAttr(stretchMDN + ".operation", 2);
    cmds.connectAttr(curveInfo + ".arcLength", stretchMDN + ".input1X");
    cmds.setAttr(stretchMDN + ".input2X", cmds.getAttr(curveInfo + ".arcLength"));
    scaleBC = cmds.shadingNode("blendColors", au=True, n=basePrefix + "_stretch_BC");
    cmds.setAttr(scaleBC + ".color2R", 1);
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", scaleBC + ".blender");
    cmds.connectAttr(stretchMDN + ".outputX", scaleBC + ".color1R");
    for jnt in stretchJnts:
        jnt = str(jnt);
        if "_ik_" in jnt:
            cmds.connectAttr(stretchMDN + ".outputX", jnt + ".scaleX");
        else:
            cmds.connectAttr(scaleBC + ".outputR", jnt + ".scaleX");

    # make dynamic ctrl
    dynCtrlList = [];
    fkCtrlDupList = cmds.duplicate(fkCtrlTopOffset, renameChildren=True);
    dynCtrlGrp = cmds.group(em=True, n=basePrefix + "_dyn_ctrl_grp");
    for i, dup in enumerate(fkCtrlDupList):
        dup = str(dup);
        dynName = dup.replace("_fk_", "_dyn_");
        dynName = dynName[:len(dynName)-1];

        if i == 0:
            cmds.rename(dup, dynName);
            cmds.parent(dynName, dynCtrlGrp);
        else:
            cmds.rename(dup, dynName);
        
        tempShape = cmds.listRelatives(dynName, s=True);
        if not tempShape is None:
            objType = cmds.objectType(str(tempShape[0]));
            if objType == "nurbsCurve":
                dynCtrlList.append(dynName);

    # visibility setting
    switchCtrlFKIKSwitchAttr = switchCtrl + ".FKIKSwitch";
    visAttr = ".visibility";
    cmds.connectAttr(switchCtrlFKIKSwitchAttr, ikfkReverse + ".inputX");
    cmds.connectAttr(ikfkReverse + ".outputX",  fkCtrlGrp + visAttr);
    cmds.connectAttr(switchCtrl + ".Simulation", ikfkReverse + ".inputY");
    cmds.connectAttr(switchCtrlFKIKSwitchAttr, ikCtrlGrp + visAttr);
    fkikdynCon = cmds.shadingNode("condition", n=basePrefix + "FKIKSwitch_CON", au=True);
    cmds.setAttr(fkikdynCon + ".colorIfTrueR", 1);
    cmds.setAttr(fkikdynCon + ".colorIfFalseR", 0);
    cmds.setAttr(fkikdynCon + ".secondTerm", 2);
    FM = cmds.shadingNode("floatMath", au=True, n=basePrefix + "FKIKSwitch_FM");
    cmds.connectAttr(switchCtrlFKIKSwitchAttr, FM + ".floatA");
    cmds.connectAttr(switchCtrl + ".Simulation", FM + ".floatB");
    cmds.connectAttr(FM + ".outFloat", fkikdynCon + ".firstTerm");
    cmds.connectAttr(fkikdynCon + ".outColorR", dynCtrlGrp + visAttr);
        
    # make Dynamic
    baseDynCurve = cmds.duplicate(curve, rr=True, renameChildren=True)
    baseDynCurve = str(cmds.rename(baseDynCurve, basePrefix + "_base_dynamics_curve"));
    cmds.select(baseDynCurve);
    mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};');

    # get nHair nodes
    follicle = str(cmds.listConnections(baseDynCurve + ".worldMatrix[0]", type="follicle", d=True)[0]);
    follicleShape = str(cmds.listRelatives(follicle, s=True)[0]);
    hairSystem = str(cmds.listConnections(follicleShape + ".outHair", type="hairSystem", d=True)[0]);
    hairSystemShape = str(cmds.listRelatives(hairSystem, s=True)[0]);
    dynCurve = str(cmds.listConnections(follicleShape + ".outCurve", type="nurbsCurve", d=True)[0]);
    dynCurve = str(cmds.rename(dynCurve, baseDynCurve.replace("_base_dynamics_", "_dynamics_")));
    nucleus = str(cmds.listConnections(hairSystemShape + ".startState", type="nucleus", d=True)[0]);
    
    # delete nHair grp
    hairsystemFollicleGrp = str(cmds.listRelatives(follicle, p=True)[0]);
    hairSystemOutputCurveGrp = str(cmds.listRelatives(dynCurve, p=True)[0]);

    nHairGrp = cmds.group(em=True, n=basePrefix + "_nHairSystem_grp");
    for h in [baseDynCurve, dynCurve, hairSystem, follicle, nucleus]:
        cmds.parent(h, nHairGrp);
    cmds.delete(hairsystemFollicleGrp, hairSystemOutputCurveGrp);

    # setting nHair BS
    cmds.setAttr(follicleShape + ".pointLock", 1);
    bs = str(cmds.blendShape(dynCurve, curve, n=basePrefix + "_dynamics_BS")[0]);
    cmds.connectAttr(switchCtrl + ".Simulation", bs + "." + dynCurve);

    clusterList = [];
    cvCount = cmds.getAttr(baseDynCurve + ".cp", s=True);
    cmds.select(baseDynCurve + ".cv[0:1]");
    topCluster = cmds.cluster(n=baseDynCurve + "_top_cluster");
    clusterList.append(topCluster);
    for i in range(int(cvCount) - 2):
        cmds.select(baseDynCurve + ".cv[{0}]".format(str(i+2)));
        cluster = cmds.cluster(n=baseDynCurve + "_{0}_cluster".format(str(i+1)));
        clusterList.append(cluster);

    for i, dynCtrl in enumerate(dynCtrlList):
        cmds.parentConstraint(dynCtrl, clusterList[i], mo=True);
        if i == len(dynCtrlList)-1:
            cmds.parentConstraint(dynCtrl, clusterList[i+1], mo=True);
            cmds.parentConstraint(dynCtrl, clusterList[i+2], mo=True);
            
    clusterGrp = cmds.group(em=True, n=basePrefix + "_cluster_grp");
    for cluster in clusterList:
        cmds.parent(cluster, clusterGrp);
        
    cmds.connectAttr(switchCtrl + ".FollowPose", hairSystemShape + ".startCurveAttract", f=True);
    cmds.connectAttr(switchCtrl + ".Drag", hairSystemShape + ".drag", f=True);
    cmds.connectAttr(switchCtrl + ".Turbulence", hairSystemShape + ".turbulenceStrength", f=True);
    
    # rename hairSystemNode
    cmds.rename(hairSystem, basePrefix + "_hairSystem");
    cmds.rename(follicle, basePrefix + "_follicle");

    # apply
def main():
    autoDynamicsSetupTool();
    OpenMaya.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # ????????????????????????????????????
        layout = QtWidgets.QGridLayout(self);


        # Input prefix
        prefixLabel = QtWidgets.QLabel("Prefix", self);
        layout.addWidget(prefixLabel, 0,0);
        self.__prefix = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__prefix, 0,1);


        # checkbox selfCreateFkikSwitch
        switchLabel = QtWidgets.QLabel("CreateFKIKSwitch???", self);
        layout.addWidget(switchLabel, 1,0);
        self.__createFKIKSwitch = QtWidgets.QCheckBox("Create", self);
        layout.addWidget(self.__createFKIKSwitch, 1, 1);


        # Input fkikSwitchCtrlName
        switchNameLabel = QtWidgets.QLabel("FKIKSwitchName", self);
        layout.addWidget(switchNameLabel, 2,0);
        self.__FKIKSwitchName = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__FKIKSwitchName, 2,1)


        # ?????????????????????????????????
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 3, 0, 1, 3);

        # set ikCtrlJnt model
        self.__ikCtrlJntModel = StockItemModelIkCtrlJnt(self);
        stockerView.setModel(self.__ikCtrlJntModel);

        # ikCtrlJnt load button
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadIkCtrlJnts);
        layout.addWidget(button, 4, 0);
        
        
        self.initialize();

    # ???????????????????????????????????????
    def initialize(self):
        self.__prefix.setText(settings.prefix);
        self.__createFKIKSwitch.setChecked(settings.createFKIKSwitch);
        self.__FKIKSwitchName.setText(settings.FKIKSwitchName);

    # ?????????????????????????????????????????????????????????
    def saveSettings(self, ikCtrlJntModel):
        settings.prefix = str(self.__prefix.text());
        settings.FKIKSwitchName = str(self.__FKIKSwitchName.text());
        settings.createFKIKSwitch = self.__createFKIKSwitch.isChecked();
        
        settings.ikCtrlJntPosList = [];
        ikCtrlJntRowCount = self.__ikCtrlJntModel.rowCount();
        for i in range(ikCtrlJntRowCount):
            settings.ikCtrlJntPosList.append(self.__ikCtrlJntModel.rowData(i));

    # ?????????????????????????????????????????????????????????
    def apply(self):
        self.saveSettings(self.__ikCtrlJntModel);
        main();

    def loadIkCtrlJnts(self):
        self.__ikCtrlJntModel.removeRows(0, self.__ikCtrlJntModel.rowCount());
        objList = cmds.ls(sl=True);
        if not objList:
            return;
        for obj in objList:
            self.__ikCtrlJntModel.appendItem(str(obj));
            print(obj);

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("AutoDynamicsSetupTool");
        self.resize(500, 500);

        # qt.py?????????????????????????????????(????????????????????????????????????????????????)???????????????????????????
        toolWidget = qt.ToolWidget(self);
        self.setCentralWidget(toolWidget);

        # ???????????????????????????????????????????????????????????????????????????
        optionWidget = OptionWidget(self);
        toolWidget.setOptionWidget(optionWidget);
        
        # ?????????close???????????????????????????????????????
        toolWidget.setActionName(self.windowTitle());
        # applied???????????????slot?????????
        toolWidget.applied.connect(optionWidget.apply);# qt.Callback(optionWidget.apply) ??????????????????????????????
        # closed??????????????????QmainWindow???close?????????????????????
        toolWidget.closed.connect(self.close);


# ??????????????????????????????????????????
class StockerView(QtWidgets.QTreeView):
    mimeType = "application/x-mytool-copyattribute-data";

    def __init__(self, *args, **kwargs):
        super(StockerView, self).__init__(*args, **kwargs);
        # Ctrl,Shift?????????????????????
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection);
        # ?????????????????????????????????
        self.setAlternatingRowColors(True);
        # ??????????????????????????????
        self.setRootIsDecorated(False);

    def removeSelectedItem(self):
        model = self.model();
        selModel = self.selectModel();

        while selModel.selectedIndexes():
            indexes = selModel.selectedIndexes();
            model.removeRow(indexes[0].row());

class StockItemModelIkCtrlJnt(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelIkCtrlJnt, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "IkCtrlJnts");

    def appendItem(self, ikCtrlJntName):
        # ????????????????????????
        ikCtrlJntName = QtGui.QStandardItem(ikCtrlJntName);
        ikCtrlJntName.setEditable(False);

        self.appendRow([ikCtrlJntName]);

    def rowData(self, index):
        # ???????????????????????????????????????????????????
        ikCtrlJntName = str(self.item(index, 0).text());

        return ikCtrlJntName;

class Settings(object):
    def __init__(self):
        self.prefix = "";
        self.createFKIKSwitch = True;
        self.FKIKSwitchName = "_fkikSwitch_ctrl";
        self.ikCtrlJntPosList = [];

settings = Settings();