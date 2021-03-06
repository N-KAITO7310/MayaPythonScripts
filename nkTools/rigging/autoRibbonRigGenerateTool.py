# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui
from ..lib import qt;
import pymel.core as pm;

# AutoRibbonRigGenerateTool 2021/10/23

def autoRibbonRigGenerateTool():
    surfaces = [];
    allBindJoints = [];

    if settings.nurbsSelfCreate:
        surfaceInfo = createNurbsPlane();
        surfaces = [surfaceInfo[0]];
        # shape = surfaceInfo[1];
        vertexes = surfaceInfo[2];
        vertex = str(vertexes[0]);
        mesh = vertex[:vertex.find(".vtx")];
        meshShape = cmds.listRelatives(mesh, s=True)[0];
    else:
        selected = cmds.ls(sl=True);
        for s in selected:
            shape = str(cmds.listRelatives(str(s), s=True)[0]);
            
            if cmds.objectType(shape) == "nurbsSurface":
                cmds.rebuildSurface(s, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0 ,su=settings.bindJoint, du=3, sv=1, dv=1, tol=0.0001, fr=0, dir=2);
                cmds.setAttr(s + ".curvePrecisionShaded", 30);
                surfaces.append(str(s));
            elif cmds.objectType(shape) == "mesh":
                mesh = str(s);
                meshShape = cmds.listRelatives(mesh, s=True)[0];

    for surfaceIndex, surface in enumerate(surfaces):
        surfaceIndex = surfaceIndex + 1;
        
        shape = str(cmds.listRelatives(surface, s=True)[0]);
        follicles = createnHairAndDeleteNode(surface=surface, surfaceShape=shape);

        # フォリクルに対してオフセットグループ、オフセットコントローラ、ジョイント作成処理
        bindJoints = [];
        for i, follicle in enumerate(follicles):
            jntName = "ribbon_{0}_bindJoint{1}_jnt".format(surfaceIndex, str(i + 1));
            joint = str(cmds.createNode("joint", name=jntName, parent=follicle));
            bindJoints.append(joint);
        
        # joint Orientation
        for i, bj in enumerate(bindJoints):
            # 一度起点となるジョイントから先までをペアレントする
            if i == 0:
                master = bj;
                pj = bj;
                continue;
            cmds.parent(bj, pj);
            pj = bj;

        cmds.joint(master, e=True, oj="xyz",  secondaryAxisOrient="yup", ch=True,  zso=True);
        cmds.makeIdentity(apply=True, t=0, r=0, s=0, n=0, pn=1, jointOrient=True);
        
        cmds.parent(bindJoints, w=True);

        # create Ctrl and OffsetGrp
        for i, follicle in enumerate(follicles):
            ctrlName = "ribbon_{0}_bindJoint{1}_Ctrl".format(surfaceIndex, str(i + 1));
            ctrl = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=settings.ctrlDiameter, d=3, ut=0, tol=0.01, s=8, ch=0, n=ctrlName)[0];
            offsetGrp = cmds.group(ctrlName, n= "ribbon_{0}_bind{1}_Offset_Grp".format(surfaceIndex, str(i + 1)));
            
            constraint = cmds.parentConstraint(follicle, offsetGrp, mo=False);
            
            cmds.delete(constraint);
            cmds.parent(offsetGrp, follicle);
            cmds.parent(bindJoints[i], ctrl);
           
        # create Joint to surface vertex Cluster
        clusterList = [];
        if settings.nurbsSelfCreate:
            # 指定頂点のV側の2点でクラスタを作成し、2つのジョイントを配置、4点における中心クラスタ位置にジョイント配置で、コントローラを作成する
            cluster1 = str(cmds.cluster(surfaceInfo[2][0], surfaceInfo[2][2])[1]);
            cluster2 = str(cmds.cluster(surfaceInfo[2][1], surfaceInfo[2][3])[1]);
            cluster3 = str(cmds.cluster(surfaceInfo[2][0], surfaceInfo[2][2], surfaceInfo[2][1], surfaceInfo[2][3])[1]);

        else:
            cluster1 = str(cmds.cluster(surface + ".cv[0][0]".format(str(settings.bindJoint + 2)), surface + ".cv[0][1]".format(settings.bindJoint + 2))[1]);
            cluster2 = str(cmds.cluster(surface + ".cv[{}][0]".format(str(settings.bindJoint + 2)), surface + ".cv[{}][1]".format(settings.bindJoint + 2))[1]);
            cluster3 = str(cmds.cluster(surface + ".cv[0][0]", surface + ".cv[0][1]",
            surface + ".cv[{}][0]".format(str(settings.bindJoint + 2)), surface + ".cv[{}][1]".format(settings.bindJoint + 2))[1]);

        clusterList = [cluster1, cluster3, cluster2];
        newClusterList = [cluster1, cluster3, cluster2];
        
        proxyPolyList = [];

        for x in range(settings.controlJoint):
            pos = 1;
            for i in range(len(clusterList)-1):
                poly1 = str(cmds.polyCube(d=0.1, h=0.1, w=0.1)[0]);
                poly2 = str(cmds.polyCube(d=0.1, h=0.1, w=0.1)[0]);

                cmds.delete(str(cmds.pointConstraint(clusterList[i], poly1, mo=False)[0]));
                cmds.delete(str(cmds.pointConstraint(clusterList[i + 1], poly2, mo=False)[0]));

                midCluster = str(cmds.cluster(poly1, poly2)[1]);
                proxyPolyList.append(poly1);
                proxyPolyList.append(poly2);
                newClusterList.insert(pos, midCluster);
                pos = pos + 2;

            clusterList = newClusterList;

        prefix = "ribbon" + str(surfaceIndex) + "_";

        fkJoints = [];
        for i, cluster in enumerate(clusterList):
            j = str(cmds.createNode("joint", name= prefix + "fk" + str(i + 1) + "_jnt"));
            cons = cmds.pointConstraint(cluster, j, mo=False);
            cmds.delete(cons);
            cons = cmds.orientConstraint(bindJoints[0], j, mo=False);
            cmds.delete(cons);
            fkJoints.append(j);

            cmds.delete(cluster);

        cmds.group(fkJoints, n="fk_joint_Grp");
        cmds.delete(proxyPolyList);

        # create FK Ctrls
        fkCtrls = [];
        for i, j in enumerate(fkJoints):
            point = settings.ctrlDiameter;
            ctrl = str(cmds.curve(d=1, p=[(point, point, point), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point*-1, point*-1),(point, point*-1, point*-1), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point, point),(point, point, point), (point, point*-1, point), (point, point*-1, point*-1), (point*-1, point*-1, point*-1),(point*-1, point*-1, point), (point, point*-1, point), (point*-1, point*-1, point), (point*-1, point, point)],
            k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], n= prefix + "fk" + str(i + 1) +  "_Ctrl"));

            offsetGrp = str(cmds.group(ctrl, n=ctrl + "_Offset_Grp"));

            cons = cmds.parentConstraint(j, offsetGrp, mo=False);
            cmds.delete(cons);

            cmds.parentConstraint(ctrl, j);
            fkCtrls.append({"offset":offsetGrp, "ctrl":ctrl});

        #  hierarchize fkCtrls
        for i, v in enumerate(fkCtrls):
            if i == 0: 
                parentCtrl = v["ctrl"];
                continue;
            
            offset = v["offset"];
            ctrl = v["ctrl"];

            cmds.parent(offset, parentCtrl);
            parentCtrl = ctrl;

        # hierarchize fkCtrls
        for i, fkJoint in enumerate(fkJoints):
            if i == 0:
                parentJnt = fkJoint;
                continue;
            cmds.parent(fkJoint, parentJnt);
            parentJnt = fkJoint;

        # skinBind ctrlJnt to Surface
        if settings.bind:
            kwargs = {
                'tsb': True,
                'bm': 1,
                'sm': 0,
                'nw': 1,
                'weightDistribution':1,
                'mi':2,
                'omi':False,
                'dr':1
            }
            cmds.skinCluster(fkJoints, surface, **kwargs);

        allBindJoints.extend(bindJoints);
        cmds.setAttr("{}.visibility".format(surface), False);

    # skinBind follicleJoint to Mesh
    # 頂点からメッシュを取得、メッシュが既にバインドされているかどうかをチェックし、されている場合はAddにする
    
    if settings.bind:
        existingSkin = cmds.listConnections(meshShape + ".inMesh", s=True, d=False, type="skinCluster");
        if existingSkin:
            cmds.skinCluster(str(existingSkin[0]), ai=allBindJoints, edit=True, lw=True, weight=0);
        else:
            kwargs2 = {
                'tsb': True,
                'bm': 1,
                'sm': 0,
                'nw': 1,
                'mi':3,
                'omi':False,
                'dr':4
            }
            cmds.skinCluster(allBindJoints, mesh, **kwargs2);

        # スケールコンストレイント()

    return;

def getOrderedSelection():
    # Track selection orderが有効になっているか確認
    if not cmds.selectPref(q=True, tso=True):
        # Track selection orderを有効にする
        cmds.selectPref(tso=True)
     
    # フラグosを使って、選択を取得し返す。
    return cmds.ls(os=True, fl=True)

# createNurbsPlane from 4 vertex point
def createNurbsPlane():
        selectedVertex = getOrderedSelection();

        # make nurbs curve
        selectedPointsNameA = selectedVertex[0:2];
        selectedPointsA = map(lambda p: cmds.pointPosition(p, w=True), selectedPointsNameA);

        selectedPointsNameB = selectedVertex[2:4];
        selectedPointsB = map(lambda p: cmds.pointPosition(p, w=True), selectedPointsNameB);

        curveA = cmds.curve(d=1, p=selectedPointsA, k=[0, 1]);
        curveB = cmds.curve(d=1, p=selectedPointsB, k=[0, 1]);

        cmds.rebuildCurve(curveA, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=1, d=3, tol=0.0001);
        cmds.rebuildCurve(curveB, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=1, d=3, tol=0.0001);

        # make surface
        surface = str(cmds.loft(curveA, curveB, ch=1, u=1, c=0, ar=1, d=3, ss= 1, rn=0, po=0, rsn=True)[0]);
        surfaceShape = str(cmds.listRelatives(surface, s=True)[0]);
        cmds.delete(curveA, curveB);
        
        cmds.rebuildSurface(surface, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0 ,su=settings.bindJoint, du=3, sv=1, dv=1, tol=0.0001, fr=0, dir=2);
        cmds.setAttr(surface + ".curvePrecisionShaded", 30);

        return [surface, surfaceShape, selectedVertex];

# create nHair And Delete node except follicle on nurbsPlane
def createnHairAndDeleteNode(surface, surfaceShape):
    cmds.select(surface);
    pm.language.Mel.eval("createHair " + str(settings.bindJoint) + " 1 10 0 0 0 0 5 0 2 2 1;");
    follicles = cmds.listConnections(surfaceShape + ".worldMatrix[0]", type="follicle", d=True);

    follicleCurve = cmds.listConnections(str(follicles[0] + ".outCurve"), type="nurbsCurve", d=True)[0];
    hairSystemOutPutCurves = cmds.listRelatives(follicleCurve, p=True)[0];
    hairSystem =  hairSystemOutPutCurves[:hairSystemOutPutCurves.find("OutputCurves")];

    # delete nhair node
    cmds.delete(hairSystemOutPutCurves);
    cmds.delete("nucleus1");
    cmds.delete(hairSystem);
    for f in follicles:
        children = cmds.listRelatives(str(f), c=True, typ="transform")[0];
        cmds.delete(children);

    follicles = list(map(lambda x: str(x), follicles));

    numbers = [];
    follicleAndNumber = {};
    for f in follicles:
        number = int(f[f.find("Follicle")+8:]);
        follicleAndNumber[number] = f;
        numbers.append(number);

    numbers = sorted(numbers);
    print(numbers);
    print(follicleAndNumber);
    follicles = list(map(lambda n: follicleAndNumber[n], numbers));

    print(follicles);
    return follicles;

# apply
def main():
    autoRibbonRigGenerateTool();
    OpenMaya.MGlobal.displayInfo("Done");

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

        # checkBoxWidgets:createNurbsSelf
        self.__nurbsSelfCreate = QtWidgets.QCheckBox("CreateNurbsSurface", self);
        mainLayout.addRow("",self.__nurbsSelfCreate);

        # input BindJointCount
        self.__bindJoint = QtWidgets.QDoubleSpinBox(self);
        self.__bindJoint.setMinimum(0);
        self.__bindJoint.setMaximum(100);
        self.__bindJoint.setDecimals(0);
        mainLayout.addRow("BindJoint", self.__bindJoint);

        # input ControlJointCoount
        ctrl3 = QtWidgets.QRadioButton("3", self);
        ctrl5 = QtWidgets.QRadioButton("5", self);
        # ctrl9 = QtWidgets.QRadioButton("9", self);

        radioLayout = QtWidgets.QHBoxLayout(self);
        radioLayout.addWidget(ctrl3, True);
        radioLayout.addWidget(ctrl5, True);
        # radioLayout.addWidget(ctrl9, True);
        mainLayout.addRow("ControlJoint", radioLayout);

        self.__controlJoint = QtWidgets.QButtonGroup(self);
        self.__controlJoint.addButton(ctrl3, 0);
        self.__controlJoint.addButton(ctrl5, 1);
        # self.__controlJoint.addButton(ctrl9, 2);

        # input contoroller diameter
        self.__ctrlDiameter = QtWidgets.QDoubleSpinBox(self);
        self.__ctrlDiameter.setMinimum(0);
        self.__ctrlDiameter.setMaximum(100);
        self.__ctrlDiameter.setDecimals(2);
        mainLayout.addRow("ControllerDiameter", self.__ctrlDiameter);

        # checkBoxWidgets:Bind
        self.__bind = QtWidgets.QCheckBox("BindSkin", self);
        mainLayout.addRow("",self.__bind);

        self.initialize();

    # window default Settings
    def initialize(self):
        self.__nurbsSelfCreate.setChecked(settings.nurbsSelfCreate);
        self.__bindJoint.setValue(settings.bindJoint);
        self.__controlJoint.button(settings.controlJoint).setChecked(True);
        self.__bind.setChecked(settings.bind);
        self.__ctrlDiameter.setValue(settings.ctrlDiameter);

    # set settings input
    def saveSettings(self):
        settings.nurbsSelfCreate = self.__nurbsSelfCreate.isChecked();
        settings.bindJoint = self.__bindJoint.value();
        settings.controlJoint = self.__controlJoint.checkedId();
        settings.bind = self.__bind.isChecked();
        settings.ctrlDiameter = self.__ctrlDiameter.value();

    # set settings and do mainMehod
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Auto RibbonRig Generate Tool");
        self.resize(350, 200);

        # qt.pyで設定したウィジェット(下部実行ボタン＆スクロールエリア)をウィンドウに設定
        toolWidget = qt.ToolWidget(self);
        self.setCentralWidget(toolWidget);

        # スクロールエリアにオプションウィジェットを設定する
        optionWidget = OptionWidget(self);
        toolWidget.setOptionWidget(optionWidget);
        
        # 実行＆closeにウィンドウタイトルを設定
        toolWidget.setActionName(self.windowTitle());
        # appliedシグナルにslotを設定
        toolWidget.applied.connect(optionWidget.apply);# qt.Callback(optionWidget.apply) ←動作しないため削除
        # closedのスロットにQmainWindowのcloseメソッドを設定
        toolWidget.closed.connect(self.close);

class Settings(object):
    def __init__(self):
        # default Settings
        self.nurbsSelfCreate = True;
        self.bindJoint = 10;
        self.controlJoint = 0;
        self.bind = True;
        self.ctrlDiameter = 0.1;

settings = Settings();