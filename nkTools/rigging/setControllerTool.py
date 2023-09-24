# -*- coding: utf-8 -*-

from maya import cmds, OpenMaya;
from PySide2 import QtWidgets;
from ..lib import qt;
import pymel.core as pm

"""
SetControllerTool
created: 2021/08/12

選択オブジェクトに対し、オフセットグループありでコントローラーを作成する。
コンストレイント、サイズ、シェイプオプションあり。
選択オブジェクトが階層上になっている場合、同様の階層構造を作成する。

ScriptEditorUse:
from nkTools.rigging import setControllerTool;
reload(setControllerTool);
reload(setControllerTool.qt);
setControllerTool.option();
"""

def setControlerTool():
    # 選択オブジェクトをチェックし、対象のジョイントを取得
    selectedObjects = pm.selected();

    # jointName:[curveName, offsetGroupName]
    createdCurveAndGroup = {};

    # コントローラカーブ＆グループノード作成処理
    for index, selected in enumerate(selectedObjects):
        # 選択オブジェクトがjointかどうかをチェック
        if not(selected.type() == "joint"):
            print("please select joint");
            continue;

        # joint名を取得し、コントローラにつけるprefixを作成
        jointName = str(selected.name());
        print("jointName is " + jointName);
        prefix = jointName;
        # joint名に_jntが命名されている場合はそれ以前をprefixとして利用する
        if("_jnt" in jointName):
            prefix = jointName[:jointName.rfind("_jnt")];

        # 任意のカーブオブジェクトを作成
        controlerName = prefix + "_ctrl";
        if(settings.shape == 0):
            # 円
            radius = settings.diameter;
            cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=controlerName);
        elif(settings.shape == 1):
            # 四角
            point =settings.diameter;
            cmds.curve(d=1, p=[(point, 0, point*-1), (point*-1, 0, point*-1), (point*-1, 0, point), (point, 0, point), (point, 0, point*-1)], k=[0, 1, 2, 3, 4], n=controlerName);
        elif(settings.shape == 2):
            # 三角
            pointA = 1.03923 * settings.diameter;
            pointB = 0.6 * settings.diameter;
            pointC = 1.2 * settings.diameter;
            cmds.curve(d=1, p=[(pointA*-1, 0, pointB), (pointA, 0, pointB), (0, 0, pointC*-1), (pointA*-1, 0, pointB)], k=[0, 1, 2, 3], n=controlerName);
        elif(settings.shape == 3):
            # 立方体
            point = settings.diameter * 0.5;
            cmds.curve(d=1, p=[(point, point, point), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point*-1, point*-1),(point, point*-1, point*-1), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point, point),(point, point, point), (point, point*-1, point), (point, point*-1, point*-1), (point*-1, point*-1, point*-1),(point*-1, point*-1, point), (point, point*-1, point), (point*-1, point*-1, point), (point*-1, point, point)],
            k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], n=controlerName);
        else:
             # 円(default)
            radius =settings.diameter;
            cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=controlerName);

        # offset_grpを作成し、カーブを子にする
        OFFSET_SUFFIX = "_offset_grp";
        AUTO_SUFFIX = "_auto_grp";
        offsetGrp = pm.createNode("transform", n=prefix + OFFSET_SUFFIX);
        autoGrp = pm.createNode("transform", n=prefix + AUTO_SUFFIX, p=offsetGrp);
        pm.matchTransform(offsetGrp, controlerName, pos=True, rot=True);
        pm.matchTransform(autoGrp, controlerName, pos=True, rot=True);
        cmds.parent(controlerName, str(autoGrp));

        # オフセットオフでペアレントコンストレインを行い、カーブをスナップ
        pConstrain =  cmds.parentConstraint(str(selected), str(offsetGrp), mo=False, weight=1);

        # コンストレインを削除
        cmds.delete(str(pConstrain[0]));

        # 選択されたジョイントと作成したコントローラを任意の方法でコンストレインする
        if(settings.constrainOption == 0):
            cmds.parentConstraint(controlerName, str(selected), mo=False);
        elif(settings.constrainOption == 1):
            cmds.pointConstraint(controlerName, str(selected), mo=False);
        elif(settings.constrainOption == 2):
            cmds.orientConstraint(controlerName, str(selected), mo=False);
        else:
            cmds.orientConstraint(controlerName, str(selected), mo=False);
        
        # 作成データの相関を保持
        createdCurveAndGroup[jointName] = [controlerName, str(offsetGrp)];

    jointList = createdCurveAndGroup.keys();
    if settings.hierarchy:
        # グループとコントローラの階層付け
        for jointName , curveAndGroup in createdCurveAndGroup.items():
            curve = curveAndGroup[0];
            group = curveAndGroup[1];

            # このジョイントに親が存在するかどうかチェック
            existParentJnt = cmds.listRelatives(jointName,allParents=True, type="joint");
            
            if not existParentJnt:
                print("this joint is rootJoint");
                continue;

            targetCursol = jointName
            flag = True;
            dangerCount = 50;
            count = 0;
            while flag:
                count = count +1;
                if count > dangerCount:
                    print("親ジョイントが見つかりませんでした。")
                    break;

                # 上記で取得した選択された親ジョイントを下の階層から探していき、処理を行う
                parentNodes = cmds.listRelatives(targetCursol, allParents=True, type="joint");
                if not parentNodes:
                    print("階層上に親となる選択対象が存在しませんでした。")
                    break;

                parentNode = parentNodes[0];

                print(str(parentNode));
                print(jointList)
                isSelectedParent = str(parentNode) in jointList;
                print(isSelectedParent)

                if isSelectedParent:
                    # 下から最も階層の近いジョイントが見つかった場合、その親のカーブとこのジョイントのグループをペアレントする
                    cmds.parent(group, createdCurveAndGroup[str(parentNode)][0]);
                    break;
                else:
                    # 直上の親が選択されたジョイントリストのものでない場合は、カーソルをこの親ノードにしループする
                    targetCursol = str(parentNode);
                    continue;

# apply
def main():
    setControlerTool();
    OpenMaya.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # 左にラベル、右にコントローラの配置レイアウトを設定
        mainLayout = QtWidgets.QFormLayout(self);

        # 階層作成のONOFチェックボックス
        self.__hierarchy = QtWidgets.QCheckBox("Create", self);
        mainLayout.addRow("Hierarchy", self.__hierarchy);

        # コンストレインt指定ラジオボタン作成
        parent = QtWidgets.QRadioButton("Parent", self);
        point = QtWidgets.QRadioButton("Point", self);
        orient = QtWidgets.QRadioButton("Orient", self);

        # ラジオボタンのレイアウト配置
        constrainLayout = QtWidgets.QHBoxLayout(self);
        constrainLayout.addWidget(parent, True);
        constrainLayout.addWidget(point, True);
        constrainLayout.addWidget(orient, True);
        mainLayout.addRow("Constrain", constrainLayout);

        # 各ボタンについての内部情報を作成
        self.__constrainOption = QtWidgets.QButtonGroup(self);
        self.__constrainOption.addButton(parent, 0);
        self.__constrainOption.addButton(point, 1);
        self.__constrainOption.addButton(orient, 2);

        # サイズの数値入力
        self.__diameter = QtWidgets.QDoubleSpinBox(self);
        self.__diameter.setMinimum(0);
        self.__diameter.setMaximum(100);
        self.__diameter.setDecimals(2);
        mainLayout.addRow("Diameter", self.__diameter);
        
        # コントローラのシェイプ指定ラジオボタン作成
        circle = QtWidgets.QRadioButton("Circle", self);
        square = QtWidgets.QRadioButton("Square", self);
        triangle = QtWidgets.QRadioButton("Triangle", self);
        cube = QtWidgets.QRadioButton("Cube", self);

        # ラジオボタンのレイアウト配置
        shapeLayout = QtWidgets.QHBoxLayout(self);
        shapeLayout.addWidget(circle, True);
        shapeLayout.addWidget(square, True);
        shapeLayout.addWidget(triangle, True);
        shapeLayout.addWidget(cube, True);
        mainLayout.addRow("Shape", shapeLayout);

        # 各ボタンについての内部情報を作成
        self.__shape = QtWidgets.QButtonGroup(self);
        self.__shape.addButton(circle, 0);
        self.__shape.addButton(square, 1);
        self.__shape.addButton(triangle, 2);
        self.__shape.addButton(cube, 3);
        

        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__hierarchy.setChecked(settings.hierarchy);
        self.__constrainOption.button(settings.constrainOption).setChecked(True);
        self.__diameter.setValue(settings.diameter);
        self.__shape.button(settings.shape).setChecked(True);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.hierarchy = self.__hierarchy.isChecked();
        settings.constrainOption = self.__constrainOption.checkedId();
        settings.diameter = self.__diameter.value();
        settings.shape = self.__shape.checkedId();

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Set Contoroler Tool");
        self.resize(400, 200);

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
        self.hierarchy = True;
        self.constrainOption = 0;
        self.diameter = 1;
        self.shape = 0;

settings = Settings();