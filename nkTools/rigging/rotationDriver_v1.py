# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;
import math as math;

"""
from nkTools.rigging import rotationDriver_v1;
reload(rotationDriver_v1);
reload(rotationDriver_v1.qt);
rotationDriver_v1.option();
"""
def rotationDriver():
    driver = str(cmds.ls(sl=True)[0]);
    drivenObjs = map(lambda obj: str(obj), cmds.ls(sl=True)[1:]);
    axisList = ["X", "Y", "Z"];

    if not driver or not drivenObjs:
        print("Select Driver or Driven Objects");
        return;

    if settings.simpleConnect:
        driverEulerToQuat = cmds.shadingNode("eulerToQuat",n=driver + "_eulerToQuat", asUtility=True);
        cmds.connectAttr(driver + ".rotate", driverEulerToQuat + ".inputRotate", force=True);
        driverQuatToEuler = cmds.shadingNode("quatToEuler", n=driver + "_quatToEuler", asUtility=True);
        cmds.connectAttr(driverEulerToQuat + ".outputQuat", driverQuatToEuler + ".inputQuat");
        connectObjIterate(driverQuatToEuler, drivenObjs, axisList);

        return;

    # create childMatrix of driver
    childMatrixNode = "{0}_childMatrix".format(driver);
    existChildMatrixNode = cmds.ls(childMatrixNode);
    if existChildMatrixNode:
        childMatrixNode = str(existChildMatrixNode[0]);
    else:
        childMatrixNode = str(cmds.createNode("transform", n=childMatrixNode));
        cmds.setAttr(childMatrixNode + ".translateX", 1);
        cmds.setAttr(childMatrixNode + ".visibility", 0);
        cmds.setAttr(childMatrixNode + ".visibility", lock=True);

    # change rot to matrix
    childComposeMatrix = str(cmds.createNode("composeMatrix", n="{0}_childComposeMatrix".format(driver)));
    driverComposeMatrix = str(cmds.createNode("composeMatrix", n= "{0}_composeMatrix".format(driver)));

    # change driver and childMatrix translate rotate to matrix
    cmds.connectAttr(childMatrixNode + ".translate", childComposeMatrix + ".inputTranslate", force=True);
    cmds.connectAttr(driver + ".rotate", driverComposeMatrix + ".inputRotate", force=True);

    # multiply matrix
    multMatrix = str(cmds.shadingNode("multMatrix", asUtility=True, n=driver + "_multMatrix"));
    cmds.connectAttr(childComposeMatrix + ".outputMatrix", multMatrix + ".matrixIn[0]", force=True);
    cmds.connectAttr(driverComposeMatrix + ".outputMatrix", multMatrix + ".matrixIn[1]", force=True);

    # decompose multiplied matrix
    decomposeMatrix = str(cmds.createNode("decomposeMatrix", n=driver + "_decomposeMatrix"));
    cmds.connectAttr(multMatrix + ".matrixSum", decomposeMatrix + ".inputMatrix", force=True);

    # input angleBetween
    angleBetween = str(cmds.shadingNode("angleBetween", n=driver + "_angleBetween", asUtility=True));
    cmds.connectAttr(decomposeMatrix + ".outputTranslate", angleBetween + ".vector1", force=True);
    cmds.connectAttr(decomposeMatrix + ".outputTranslate",  angleBetween + ".vector2", force=True);
    # disconnect for remain default info
    cmds.disconnectAttr(decomposeMatrix + ".outputTranslate", angleBetween + ".vector1");

    # input axisAngleToQuat
    axisAngleToQuat = str(cmds.shadingNode("axisAngleToQuat", asUtility=True, n=driver + "_axisAngleToQuat"));
    cmds.connectAttr(angleBetween + ".axis", axisAngleToQuat + ".inputAxis", force=True);
    cmds.connectAttr(angleBetween + ".angle", axisAngleToQuat + ".inputAngle", force=True);

    # connect Driven
    if settings.rotationComponent == 0:
        # connect Roll Only
        driverEulerToQuat = cmds.shadingNode("eulerToQuat",n=driver + "_eulerToQuat", asUtility=True);
        cmds.connectAttr(driver + ".rotate", driverEulerToQuat + ".inputRotate", force=True);

        # invert Bend rot
        quatInvert = str(cmds.shadingNode("quatInvert", n=driver + "_quatInvert", asUtility=True));
        cmds.connectAttr(axisAngleToQuat + ".outputQuat", quatInvert + ".inputQuat", force=True);

        # multiply quatProd for extract roll
        quatProd = str(cmds.shadingNode("quatProd", n=driver + "_quatProd",asUtility=True));
        cmds.connectAttr(driverEulerToQuat + ".outputQuat", quatProd + ".input1Quat", force=True);
        cmds.connectAttr(quatInvert + ".outputQuat", quatProd + ".input2Quat", force=True);

        # quatSlerp option
        if settings.quatSlerp:
            driverQuatToEuler = createQuatSlerp(driver, quatProd);
            connectObjIterate(driverQuatToEuler, drivenObjs, axisList[0]);
        else:
            roleEuler = str(cmds.shadingNode("quatToEuler", n=driver + "_role_quatToEuler", asUtility=True));
            cmds.connectAttr(quatProd + ".outputQuat", roleEuler + ".inputQuat", force=True);
            connectObjIterate(roleEuler, drivenObjs, axisList[0]);
    elif settings.rotationComponent == 1:
        # connect Bend Only
        if settings.quatSlerp:
            driverQuatToEuler = createQuatSlerp(driver, axisAngleToQuat);
            connectObjIterate(driverQuatToEuler, drivenObjs, axisList[1:]);
        else:
            bendEuler = str(cmds.shadingNode("quatToEuler", n=driver + "_bend_quatToEuler", asUtility=True));
            cmds.connectAttr(axisAngleToQuat + ".outputQuat", bendEuler + ".inputQuat", force=True);
            connectObjIterate(bendEuler, drivenObjs, axisList[1:]);
        
    
                
def createQuatSlerp(driver, quatProd):
    # create quatSlerp and connect
    driverQuatSlerp = str(cmds.shadingNode("quatSlerp", n=driver + "_quatSlerp", asUtility=True));
    driverQuatToEuler = str(cmds.shadingNode("quatToEuler",n=driver + "_quatToEuler", asUtility=True));
    # quatSlerpのinput1に無回転値を設定したのち接続を切る。input2に接続し、inputT値で既定値との相対で出力を調整する
    cmds.connectAttr(quatProd + ".outputQuat", driverQuatSlerp + ".input1Quat", force=True);
    cmds.connectAttr(quatProd + ".outputQuat",  driverQuatSlerp + ".input2Quat", force=True);
    cmds.disconnectAttr(quatProd + ".outputQuat", driverQuatSlerp + ".input1Quat");
    cmds.connectAttr(driverQuatSlerp + ".outputQuat", driverQuatToEuler + ".inputQuat", force=True);

    # quatSlerpのTアトリビュートに数値入力を行い割合を指定
    quatInputT = settings.quatSlerpRatio / 100;
    cmds.setAttr(driverQuatSlerp + ".inputT", quatInputT);

    return driverQuatToEuler;

def connectObjIterate(sourceNode, drivens, axisList):
    # default sourceNode is quatToEuler
    for driven in drivens:
        for axis in axisList:
            cmds.connectAttr(sourceNode + ".outputRotate{0}".format(axis), driven + ".rotate{0}".format(axis), f=True);

# apply
def main():
    rotationDriver();
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

        # QuatSlerp作成のONOFチェックボックス
        self.__simpleConnect = QtWidgets.QCheckBox("ON", self);
        mainLayout.addRow("SimpleConnect", self.__simpleConnect);

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
        self.__simpleConnect.setChecked(settings.simpleConnect);
        self.__rotationComponent.button(settings.rotationComponent).setChecked(True);
        self.__quatSlerp.setChecked(settings.quatSlerp);
        self.__quatSlerpRatio.setValue(settings.quatSlerpRatio);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.simpleConnect = self.__simpleConnect.isChecked();
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
        self.setWindowTitle("Rotation Driver Tool");
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
        self.simpleConnect = False;
        self.rotationComponent = 0;
        self.quatSlerp = True;
        self.quatSlerpRatio = 100;

settings = Settings();