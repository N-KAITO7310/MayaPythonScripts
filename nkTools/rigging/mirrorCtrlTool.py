# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;

'''
前提条件
・ミラー側のジョイントが既に存在していること
・対象のコントローラが選択されていること
・ジョイントにCtrlの名前があり、命名規則に従っていること

要件
・階層が異なるCtrlが複数選択されている場合に、全てに対して行いたい
・コンストレイントが対象のCtrlとジョイント間に存在すればそれもミラーする
・ペアレント化とコンストレイントコピーのオプション選択
'''

def mirrorCtrlTool():
    # 選択されたCtrlを取得
    selected = cmds.ls(sl=True);

    # check nurbsCurve
    for obj in selected:
        shape = cmds.listRelatives(obj, s=True);
        if cmds.objectType(shape) != "nurbsCurve":
            print("Please Select Curve");
            return;

    # Main Roop Start
    for ctrl in selected:
        #get ctrl side
        side = ctrl[0];

        Oside = "";
        if side=='l':
            Oside='r';
        elif side=='r':
            Oside='l';

        OsideCtrl = ctrl.replace(side,Oside, 1);

        #get the parent node
        parentctrl = cmds.listRelatives(ctrl, p=True)[0];

        #get jnt
        jnt = ctrl.replace('ctrl','jnt', 1);
        OsideJnt = jnt.replace(side,Oside, 1);

        #if joint doesnt exists, fail
        if cmds.objExists(jnt) == False:
            print 'cant find joint, please create joint or rename joint to Jnt';

        #create null grp 
        nullGrp = cmds.group(em=True, n=OsideJnt + '_null');

        #attach null to joint
        cmds.delete(cmds.parentConstraint(OsideJnt, nullGrp));

        #duplicate parent group
        dup = cmds.duplicate(parentctrl, n=parentctrl.replace(side,Oside, 1), renameChildren=True);
        dupParentGrp = dup[0];

        # rename
        children = cmds.listRelatives(dupParentGrp, ad=True);
        for child in children:
            child = cmds.rename(child, child.replace(side+'_', Oside+'_', 1));
            newname = cmds.rename(child, child.rstrip(child[-1]));

        # get renamed item and attr set
        children = cmds.listRelatives(dupParentGrp, ad=True);
        for child in children:
            for attr in ['translate','rotate','scale']:
                for axis in ['X','Y','Z']:
                    if 'Shape' in child:
                        pass
                    else:
                        # only transform: set keyable lock
                        cmds.setAttr('{0}.{1}{2}'.format(child, attr, axis), keyable=True);
                        cmds.setAttr('{0}.{1}{2}'.format(child, attr, axis) ,lock=False);

        try:
            cmds.parent(dupParentGrp, w=True);
        except:
            pass;

        # mirror
        scaleNeg = cmds.group(dupParentGrp, n = dupParentGrp +'_scal_eneg_X');
        cmds.setAttr('{0}.scaleX'.format(scaleNeg), -1);
        cmds.delete(cmds.parentConstraint(nullGrp, dupParentGrp));
        cmds.parent(dupParentGrp,nullGrp);
        # freeze
        cmds.makeIdentity(str(dupParentGrp), apply=True, t=True, r=True, s=True, n=False, pn=True);
        cmds.parent(dupParentGrp, w=True);
        cmds.delete(nullGrp, scaleNeg);

        # 親ノードにparent
        if settings.parent:
            parentObj = cmds.listRelatives(parentctrl, p=True);
            cmds.parent(dupParentGrp, parentObj);

        ctrlInfoDict = {};

        # copy constraint
        if settings.constraint:
            # get transform named Ctrl
            ctrlChildren = cmds.listRelatives(ctrl, ad=True, type="transform");
            if ctrlChildren:
                ctrls = [obj for obj in ctrlChildren  if obj.endswith("_ctrl")];
                ctrls.append(ctrl);
            else:
                ctrls = [ctrl];
                
            # check constraint
            for ctrl in ctrls:
                connections = cmds.listConnections(ctrl, type="constraint")
                constraints =  map(lambda obj: str(obj), connections);
                constraintList = [];
                # setがなぜか使えなかったため以下で代用
                for constraint in constraints:
                    if not constraint in constraintList:
                        constraintList.append(constraint);

                if len(constraintList) == 0:
                    continue;
            
                # get joint per constraint
                for constraint in constraintList:
                    # get joint from connections
                    targetJoints = cmds.listConnections(constraint, type="joint");
                    targetJoint =  str(targetJoints[0]);

                    if not targetJoint:
                        continue;

                    # save constraint information
                    if ctrl in ctrlInfoDict:
                        ctrlInfoDict[ctrl].append({"constraint":constraint, "joint":targetJoint});
                    else:
                        ctrlInfoDict[ctrl] = [{"constraint":constraint, "joint":targetJoint}];

            # constraint mirrored
            for ctrl, constrainInfodList in ctrlInfoDict.items():
                oppositeCtrl = ctrl.replace(side, Oside, 1);
                for info in constrainInfodList:
                    constraint = info["constraint"];
                    joint = info["joint"];
                    oppositeJnt = joint.replace(side, Oside, 1);

                    if "parent" in constraint:
                        cmds.parentConstraint(oppositeCtrl, oppositeJnt, mo=True);
                    elif "point" in constraint:
                        cmds.parentConstraint(oppositeCtrl, oppositeJnt, mo=True);
                    elif "orient" in constraint:
                        cmds.parentConstraint(oppositeCtrl, oppositeJnt, mo=True);
                    else:
                        print("Not applicable constraint");
                        continue;


# apply
def main():
    mirrorCtrlTool();
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

        # checkBoxWidgets:parent
        self.__parent = QtWidgets.QCheckBox("Parent", self);
        mainLayout.addRow(self.__parent);

        # checkBoxWidgets:constraint
        self.__constraint = QtWidgets.QCheckBox("Constraint Copy", self);
        mainLayout.addRow(self.__constraint);

        self.initialize();

    # window default Settings
    def initialize(self):
        self.__parent.setChecked(settings.parent);
        self.__constraint.setChecked(settings.constraint);

    # set settings input
    def saveSettings(self):
        settings.parent = self.__parent.isChecked();
        settings.constraint = self.__constraint.isChecked();

    # set settings and do mainMehod
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Mirror Ctrl Tool");
        self.resize(300, 150);

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
        self.parent = True;
        self.constraint = True;

settings = Settings();