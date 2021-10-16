# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;
import math as math;

"""
接続元、接続先複数選択で接続元のBend成分、Roll成分をRotateにコネクションする
オプション選択：
ラジオボタン
・Roll
・Bend
チェックボックス
・Create QuatSlerp

from nkTools.rigging import autoQuaternionDecomposition;
reload(autoQuaternionDecomposition);
reload(autoQuaternionDecomposition.qt);
autoQuaternionDecomposition.option();
"""
def autoQuaternionDecomposition():
    driver = str(cmds.ls(sl=True)[0]);
    drivenObjs = map(lambda obj: str(obj), cmds.ls(sl=True)[1:]);
    print(driver);
    print(drivenObjs);

    if not driver or not drivenObjs:
        print("Select Driver or Driven Objects");
        return;

    # 接続元となるノードの子としてのマトリックスを設定するためのノードを作成
    # TODO:シーンにすでにこのノードが存在するかのチェックと存在する場合の取得を追加しておくこと
    childMatrixNode = ""
    existChildMatrixNode = cmds.ls("childMatrix");
    if existChildMatrixNode:
        childMatrixNode = str(existChildMatrixNode[0]);
    else:
        childMatrixNode = str(cmds.createNode("transform", n="childMatrix"));
        cmds.setAttr(childMatrixNode + ".translateX", 1);
        cmds.setAttr(childMatrixNode + ".visibility", 0);
        cmds.setAttr(childMatrixNode + ".visibility", lock=True);

    # 回転成分分解ノードの構築
    childComposeMatrix = str(cmds.createNode("composeMatrix", n="childComposeMatrix"));
    driverComposeMatrix = str(cmds.createNode("composeMatrix", n= driver + "_composeMatrix"));

    cmds.connectAttr(childMatrixNode + ".translate", childComposeMatrix + ".inputTranslate", force=True);
    print(driver + ".rotate", driverComposeMatrix + ".inputRotate");
    cmds.connectAttr(driver + ".rotate", driverComposeMatrix + ".inputRotate", force=True);

    multMatrix = str(cmds.shadingNode("multMatrix", asUtility=True, n=driver + "_multMatrix"));
    cmds.connectAttr(childComposeMatrix + ".outputMatrix", multMatrix + ".matrixIn[0]", force=True);
    cmds.connectAttr(driverComposeMatrix + ".outputMatrix", multMatrix + ".matrixIn[1]", force=True);

    decomposeMatrix = str(cmds.createNode("decomposeMatrix", n=driver + "_decomposeMatrix"));
    cmds.connectAttr(multMatrix + ".matrixSum", decomposeMatrix + ".inputMatrix", force=True);

    angleBetween = str(cmds.shadingNode("angleBetween", n=driver + "_angleBetween", asUtility=True));
    cmds.connectAttr(decomposeMatrix + ".outputTranslate", angleBetween + ".vector1", force=True);
    cmds.connectAttr(decomposeMatrix + ".outputTranslate",  angleBetween + ".vector2", force=True);
    cmds.disconnectAttr(decomposeMatrix + ".outputTranslate", angleBetween + ".vector1");

    axisAngleToQuat = str(cmds.shadingNode("axisAngleToQuat", asUtility=True, n=driver + "_axisAngleToQuat"));
    cmds.connectAttr(angleBetween + ".axis", axisAngleToQuat + ".inputAxis", force=True);
    cmds.connectAttr(angleBetween + ".angle", axisAngleToQuat + ".inputAngle", force=True);

    # Bend
    bendEuler = str(cmds.shadingNode("quatToEuler", n=driver + "_bend_quatToEuler", asUtility=True));
    cmds.connectAttr(axisAngleToQuat + ".outputQuat", bendEuler + ".inputQuat", force=True);

    driverEulerToQuat = cmds.shadingNode("eulerToQuat",n=driver + "_eulerToQuat", asUtility=True);
    cmds.connectAttr(driver + ".rotate", driverEulerToQuat + ".inputRotate", force=True);

    quatInvert = str(cmds.shadingNode("quatInvert", n=driver + "_quatInvert", asUtility=True));
    cmds.connectAttr(axisAngleToQuat + ".outputQuat", quatInvert + ".inputQuat", force=True);

    quatProd = str(cmds.shadingNode("quatProd", n=driver + "_quatProd",asUtility=True));
    cmds.connectAttr(driverEulerToQuat + ".outputQuat", quatProd + ".input1Quat", force=True);
    cmds.connectAttr(quatInvert + ".outputQuat", quatProd + ".input2Quat", force=True);

    # Roll
    roleEuler = str(cmds.shadingNode("quatToEuler", n=driver + "_role_quatToEuler", asUtility=True));
    cmds.connectAttr(quatProd + ".outputQuat", roleEuler + ".inputQuat", force=True);

    # 各ジョイントに接続
    for driven in drivenObjs:
        if settings.quatSlerp:
            # quatSlerpを作成し接続
            drivenQuatSlerp = str(cmds.shadingNode("quatSlerp", n=driven + "_quatSlerp", asUtility=True));
            drivenQuatToEuler = str(cmds.shadingNode("quatToEuler",n=driven + "_quatToEuler", asUtility=True));
            cmds.connectAttr(drivenQuatSlerp + ".outputQuat", drivenQuatToEuler + ".inputQuat", force=True);
            cmds.connectAttr(drivenQuatToEuler + ".outputRotate", driven + ".rotate", f=True);

            # quatSlerpのTアトリビュートに数値入力を行い割合を指定
            quatInputT = settings.quatSlerpRatio / 100;
            cmds.setAttr(drivenQuatSlerp + ".inputT", quatInputT);
            
            if settings.rotationComponent == 0:
                # Roll成分をquatSlerp経由で接続
                cmds.connectAttr(quatProd + ".outputQuat", drivenQuatSlerp + ".input1Quat", force=True);
                cmds.connectAttr(quatProd + ".outputQuat", drivenQuatSlerp + ".input2Quat", force=True);
                cmds.disconnectAttr(quatProd + ".outputQuat", drivenQuatSlerp + ".input1Quat");
            else:
                # Bend成分をquatSlerp経由で接続
                cmds.connectAttr(axisAngleToQuat + ".outputQuat", drivenQuatSlerp + ".input1Quat", force=True);
                cmds.connectAttr(axisAngleToQuat + ".outputQuat", drivenQuatSlerp + ".input2Quat", force=True);
                cmds.disconnectAttr(axisAngleToQuat + ".outputQuat", drivenQuatSlerp + ".input1Quat");
        else:
            if settings.rotationComponent == 0:
                # Roll成分を直接接続
                cmds.connectAttr(roleEuler + ".outputRotate", driven + ".rotate", f=True);
                
            else:
                # Bend成分を直接接続
                cmds.connectAttr(bendEuler + ".outputRotate", driven + ".rotate", f=True);

# apply
def main():
    autoQuaternionDecomposition();
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

        # 接続する回転成分の選択ラジオボタン作成
        roll = QtWidgets.QRadioButton("Roll", self);
        bend = QtWidgets.QRadioButton("Bend", self);

        # ラジオボタンのレイアウト配置
        rotationLayout = QtWidgets.QHBoxLayout(self);
        rotationLayout.addWidget(roll, True);
        rotationLayout.addWidget(bend, True);
        mainLayout.addRow("Rotation Component", rotationLayout);

        # 各ボタンについての内部情報を作成
        self.__rotationComponent = QtWidgets.QButtonGroup(self);
        self.__rotationComponent.addButton(roll, 0);
        self.__rotationComponent.addButton(bend, 1);

        # QuatSlerp作成のONOFチェックボックス
        self.__quatSlerp = QtWidgets.QCheckBox("Create", self);
        mainLayout.addRow("QuatSlerp", self.__quatSlerp);

        # QuatSlerpの割合の入力
        self.__quatSlerpRatio = QtWidgets.QDoubleSpinBox(self);
        self.__quatSlerpRatio.setMinimum(0);
        self.__quatSlerpRatio.setMaximum(100);
        self.__quatSlerpRatio.setDecimals(2);
        mainLayout.addRow("QuatSlerpRatio", self.__quatSlerpRatio);

        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__rotationComponent.button(settings.rotationComponent).setChecked(True);
        self.__quatSlerp.setChecked(settings.quatSlerp);
        self.__quatSlerpRatio.setValue(settings.quatSlerpRatio);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.rotationComponent = self.__rotationComponent.checkedId();
        settings.quatSlerp = self.__quatSlerp.isChecked();
        settings.quatSlerpRatio = self.__quatSlerpRatio.value();

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Auto Quaternion Decomposition Tool");
        self.resize(400, 180);

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
        self.rotationComponent = 0;
        self.quatSlerp = True;
        self.quatSlerpRatio = 0;

settings = Settings();