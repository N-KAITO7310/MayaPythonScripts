# -*- coding: utf-8 -*-

import maya.api.OpenMayaUI as omUI;
import maya.api.OpenMaya as om;
import maya.cmds as cmds;
import maya.mel as mel;
import json, time;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN;
import glob


"""
version: 1.2
created Date: 2022/02/01
last update: 2023/03/25
最終更新内容：
・ミラー対象としてfrontArmorikのコントローラを指定していたが、
ミラーすると回転が余計に入りミラーが成立していなかったため、対象から削除を行った

import nkTools.animation.importExportPoseTool as importExportPoseTool;
reload(importExportPoseTool);
reload(importExportPoseTool.qt);
importExportPoseTool.option();

要件定義
・画像のキャプチャ機能
・コントローラ情報の取得とJSONデータ化
・JSON書き出し

ポイント
・Json書き出し処理
・コントローラの情報をどうJsonの形に成型するか
・ファイルパスの指定
・汎用的なものにするかどうか

UI必要項目
・import or export チェックボックス
・import元またはexport先ファイルパス
新規
・表示ウィジェットによる指定画像表示(Qlabel)
・import export でタブを分ける(QtabWidget)*v2での追加項目として
・ファイル表示をリストし、選択することでインタラクティブに画像を表示する
・プログレスバーの表示

"""

def saveImg(filePass):
    # アクティブなviewportを取得
    view = omUI.M3dView.active3dView();
    # 空の画像を作成
    image = om.MImage();
    view.readColorBuffer(image, True);
    image.resize(960, 540, preserveAspectRatio=True);

    try:
        temp = filePass.split(".");
        format = temp[-1];
        image.writeToFile(filePass, format);
    except:
        return False;

    return True;

def exportJson(data, filePass):
    jsonName = filePass[:filePass.rfind(".")] + ".json";
    
    writeJsonFile(data, jsonName);
    
def writeJsonFile(dataToWrite, fileName):
    if ".json" not in fileName:
        fileName += ".json"

    print "> write to json file is seeing: {0}".format(fileName)

    with open(fileName, "w") as jsonFile:
        json.dump(dataToWrite, jsonFile, indent=4, separators=(',', ': '))

    print "Data was successfully written to {0}".format(fileName)

    return fileName

def getSceneCtrlInfo():
    ctrls = cmds.ls( '*_ctrl');
    ctrls = map(lambda ctrl: str(ctrl), ctrls);
    
    ctrlsDict = {};
    for ctrl in ctrls:
        
        attrList = cmds.listAttr(ctrl, keyable=True, unlocked = True, connectable=True);
        attrList = map(lambda attr: str(attr), attrList);
        
        ctrlInfoDict = {};
        for attr in attrList:
            connectExist = cmds.listConnections("{0}.{1}".format(ctrl, attr), s=True, d=False);
            if not connectExist is None:
                continue;
            
            value = cmds.getAttr("{0}.{1}".format(ctrl, attr));
            if type(value) is float:
                # 余計な少数の丸め処理。float型ではなく文字列str型を指定すると正確にその値のDecimal型として扱われる
                value = float(Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP));
            ctrlInfoDict[attr] = value;
    
        ctrlsDict[ctrl] = ctrlInfoDict;
    
    return ctrlsDict;
    

def exportPose():
    filePass = settings.filePass
    # capture image
    imgResult = saveImg(filePass);
    
    if not imgResult:
        om.MGlobal.displayError("Failed to save picture.");
        return;
        
    # get controller info
    fileName = filePass[filePass.rfind("/"):];
    exportData = {"time": time.time(), "filePass": settings.filePass, "fileName": fileName};
    
    ctrlsData = getSceneCtrlInfo();
    exportData["controllerInfo"] = ctrlsData;
    
    # write json
    exportJson(exportData, filePass);
        
def importPose():
    print("start import");
    filePass = settings.filePass
    # json parse
    with open(filePass) as jsonFile:
        importData = json.load(jsonFile);
    
    # set attr iteration
    ctrlsDict = importData["controllerInfo"];
    for ctrl in ctrlsDict.keys():
        # 各コントローラ毎に、持っているアトリビュートでイテレート
        attrDict = ctrlsDict[ctrl];
        for attr in attrDict.keys():
            value = attrDict[attr];
            cmds.setAttr("{0}.{1}".format(ctrl, attr), value);
    
def mirrorPoseBehaviorAxis(ctrlList):
    axisList = ["X", "Y", "Z"];
    mirrorDict = {};
    culcList = [];
    proxyList = [];
    
    for ctrl in ctrlList:
        mirrorCtrl = "";
        if "l_" in ctrl:
            mirrorCtrl = ctrl.replace("l_", "r_", 1);
        elif "r_" in ctrl:
            mirrorCtrl = ctrl.replace("r_", "l_", 1);
        else:
            return;
            
        mirrorProxy = cmds.createNode("transform", n="{}_mirror_proxy".format(ctrl));
        eularToQuat = cmds.createNode("eulerToQuat");
        quatToEuler = cmds.createNode("quatToEuler");
        reverseMDN = cmds.createNode("multiplyDivide");
        culcList.extend([eularToQuat, quatToEuler, reverseMDN]);
        proxyList.append(mirrorProxy);
        
        cmds.connectAttr("{}.rotate".format(ctrl), "{}.inputRotate".format(eularToQuat));
        cmds.connectAttr("{}.outputQuat".format(eularToQuat), "{}.inputQuat".format(quatToEuler));
        cmds.connectAttr("{}.outputRotate".format(quatToEuler), "{}.rotate".format(mirrorProxy));
        cmds.disconnectAttr("{}.outputRotate".format(quatToEuler), "{}.rotate".format(mirrorProxy));
        
        for axis in axisList:
            cmds.setAttr("{}.input2{}".format(reverseMDN, axis), -1);
            cmds.connectAttr("{}.translate{}".format(ctrl, axis), "{}.input1{}".format(reverseMDN, axis));
            cmds.connectAttr("{}.output{}".format(reverseMDN, axis), "{}.translate{}".format(mirrorProxy, axis));
            cmds.disconnectAttr("{}.output{}".format(reverseMDN, axis), "{}.translate{}".format(mirrorProxy, axis));
    
        mirrorDict[mirrorCtrl] = mirrorProxy;
    
    cmds.delete(culcList);
    
    for targetCtrl, proxy in mirrorDict.items():
        cmds.connectAttr("{}.translate".format(proxy), "{}.translate".format(targetCtrl));
        cmds.disconnectAttr("{}.translate".format(proxy), "{}.translate".format(targetCtrl));
        cmds.connectAttr("{}.rotate".format(proxy), "{}.rotate".format(targetCtrl));
        cmds.disconnectAttr("{}.rotate".format(proxy), "{}.rotate".format(targetCtrl));
    
    cmds.delete(proxyList);
   
def mirrorPoseSameAxis(controllerList):
    inputSourceList = [];
    culNodeList = [];
    
    outputDict = {};
    outputOffsetList = [];
    
    # do process each controller
    for ctrl in controllerList:
        # search mirror target
        mirrorTargetCtrl = ctrl;
        sidePrefix = ctrl[0:2];
        if "l_" == sidePrefix:
            mirrorTargetCtrl = ctrl.replace("l_", "r_", 1);
        elif "r_" == sidePrefix:
            mirrorTargetCtrl = ctrl.replace("r_", "l_", 1);
        if not mirrorTargetCtrl in controllerList:
            continue;
        
        # create transform for each ctrl and connect by constrain
        source = cmds.createNode("transform", n="{}_source".format(ctrl));
        inputSourceList.append(source);
        
        # match trans rot to moved ctrl pos
        cmds.pointConstraint(ctrl, source, mo=False);
        cmds.orientConstraint(ctrl, source, mo=False);
        

        # create nodes to generate mirror vector
        sourceRotMatrix = cmds.createNode("composeMatrix");
        # aim Vector for Bend
        bendVectorNode = cmds.createNode("composeMatrix");
        # up Vector for Roll
        rollVectorNode = cmds.createNode("composeMatrix");
        
        bendVectorMatrix = cmds.createNode("multMatrix");
        rollVectorMatrix = cmds.createNode("multMatrix");
        
        bendVectorDecompose = cmds.createNode("decomposeMatrix");
        rollVectorDecompose = cmds.createNode("decomposeMatrix");
        
        mirrorBendVecFM = cmds.createNode("floatMath");
        mirrorRollVecFM = cmds.createNode("floatMath");
        
        bendAngle = cmds.createNode("angleBetween");
        rollAngle = cmds.createNode("angleBetween");
        
        bendQuat = cmds.createNode("axisAngleToQuat");
        rollQuat = cmds.createNode("axisAngleToQuat");
        
        bendMatrix = cmds.createNode("composeMatrix");
        multUpAndBend = cmds.createNode("multMatrix");
        multUpAndBendDecompose = cmds.createNode("decomposeMatrix");
        
        quatProdBendRoll = cmds.createNode("quatProd");
        finalOutputQuatToEuler = cmds.createNode("quatToEuler");
        
        mirrorTxFM = cmds.createNode("floatMath");
        
        culNodeList.extend([
            sourceRotMatrix,
            bendVectorNode,
            rollVectorNode,
            bendVectorMatrix,
            rollVectorMatrix,
            bendVectorDecompose,
            rollVectorDecompose,
            mirrorBendVecFM,
            mirrorRollVecFM,
            bendAngle,
            rollAngle,
            bendQuat,
            rollQuat,
            bendMatrix,
            multUpAndBend,
            multUpAndBendDecompose,
            quatProdBendRoll,
            finalOutputQuatToEuler,
            mirrorTxFM
        ]);
        
        # construct mirror matrix network
        cmds.connectAttr("{}.rotate".format(source), "{}.inputRotate".format(sourceRotMatrix));
        
        # difine aim Vector and up Vector
        cmds.setAttr("{}.inputTranslate".format(bendVectorNode), 0.0, 1.0, 0.0);
        cmds.setAttr("{}.inputTranslate".format(rollVectorNode), 0.0, 0.0, 1.0);
        
        # connect bend and roll multMatrix
        cmds.connectAttr("{}.outputMatrix".format(bendVectorNode), "{}.matrixIn[0]".format(bendVectorMatrix));
        cmds.connectAttr("{}.outputMatrix".format(rollVectorNode), "{}.matrixIn[0]".format(rollVectorMatrix));
        cmds.connectAttr("{}.outputMatrix".format(sourceRotMatrix), "{}.matrixIn[1]".format(bendVectorMatrix));
        cmds.connectAttr("{}.outputMatrix".format(sourceRotMatrix), "{}.matrixIn[1]".format(rollVectorMatrix));
        
        # decompose
        cmds.connectAttr("{}.matrixSum".format(bendVectorMatrix), "{}.inputMatrix".format(bendVectorDecompose));
        cmds.connectAttr("{}.matrixSum".format(rollVectorMatrix), "{}.inputMatrix".format(rollVectorDecompose));
        
        # connect and setting mult -1 FM
        cmds.connectAttr("{}.outputTranslateX".format(bendVectorDecompose), "{}.floatA".format(mirrorBendVecFM));
        cmds.connectAttr("{}.outputTranslateX".format(rollVectorDecompose), "{}.floatA".format(mirrorRollVecFM));
        cmds.setAttr("{}.floatB".format(mirrorBendVecFM), -1);
        cmds.setAttr("{}.floatB".format(mirrorRollVecFM), -1);
        cmds.setAttr("{}.operation".format(mirrorBendVecFM), 2);
        cmds.setAttr("{}.operation".format(mirrorRollVecFM), 2);
        
        # construct Bend
        cmds.connectAttr("{}.outFloat".format(mirrorBendVecFM), "{}.vector2X".format(bendAngle));
        cmds.connectAttr("{}.outputTranslateY".format(bendVectorDecompose), "{}.vector2Y".format(bendAngle));
        cmds.connectAttr("{}.outputTranslateZ".format(bendVectorDecompose), "{}.vector2Z".format(bendAngle));
        
        # construct Roll
        cmds.connectAttr("{}.outFloat".format(mirrorRollVecFM), "{}.vector2X".format(rollAngle));
        cmds.connectAttr("{}.outputTranslateY".format(rollVectorDecompose), "{}.vector2Y".format(rollAngle));
        cmds.connectAttr("{}.outputTranslateZ".format(rollVectorDecompose), "{}.vector2Z".format(rollAngle));
        
        # get Quaternion取得
        cmds.connectAttr("{}.axis".format(bendAngle), "{}.inputAxis".format(bendQuat));
        cmds.connectAttr("{}.angle".format(bendAngle), "{}.inputAngle".format(bendQuat));
        cmds.connectAttr("{}.axis".format(rollAngle), "{}.inputAxis".format(rollQuat));
        cmds.connectAttr("{}.angle".format(rollAngle), "{}.inputAngle".format(rollQuat));
        
        # culc dafult vector for roll angle
        cmds.connectAttr("{}.outputQuat".format(bendQuat), "{}.inputQuat".format(bendMatrix));
        cmds.setAttr("{}.useEulerRotation".format(bendMatrix), False);
        cmds.connectAttr("{}.outputMatrix".format(rollVectorNode), "{}.matrixIn[0]".format(multUpAndBend));
        cmds.connectAttr("{}.outputMatrix".format(bendMatrix), "{}.matrixIn[1]".format(multUpAndBend));
        
        cmds.connectAttr("{}.matrixSum".format(multUpAndBend), "{}.inputMatrix".format(multUpAndBendDecompose));
        
        # connect roll angle vector1
        cmds.connectAttr("{}.outputTranslate".format(multUpAndBendDecompose), "{}.vector1".format(rollAngle));
        
        
        # connection for output
        outputOffset = cmds.createNode("transform", n="{}_output_offset_grp".format(ctrl));
        outputOffsetList.append(outputOffset);
        outputNode = cmds.createNode("transform", n="{}_output".format(ctrl));
        cmds.parent(outputNode, outputOffset);
        
        outputDict[ctrl] = outputNode;
        
        # mult bend and roll rot component
        cmds.connectAttr("{}.outputQuat".format(bendQuat), "{}.input1Quat".format(quatProdBendRoll));
        cmds.connectAttr("{}.outputQuat".format(rollQuat), "{}.input2Quat".format(quatProdBendRoll));
        cmds.connectAttr("{}.outputQuat".format(quatProdBendRoll), "{}.inputQuat".format(finalOutputQuatToEuler));
        
        # connect final output
        cmds.connectAttr("{}.outputRotate".format(finalOutputQuatToEuler), "{}.rotate".format(outputOffset));
        
        # conncet mirror trans to final output
        cmds.connectAttr("{}.tx".format(source), "{}.floatA".format(mirrorTxFM));
        cmds.setAttr("{}.floatB".format(mirrorTxFM), -1.0);
        cmds.setAttr("{}.operation".format(mirrorTxFM), 2);
        
        cmds.connectAttr("{}.outFloat".format(mirrorTxFM), "{}.tx".format(outputOffset));
        cmds.connectAttr("{}.ty".format(source), "{}.ty".format(outputOffset));
        cmds.connectAttr("{}.tz".format(source), "{}.tz".format(outputOffset));
        
    
    # bake output offset
    startF = cmds.playbackOptions(q=True, min=True);
    endF = cmds.playbackOptions(q=True, max=True);
    
    cmds.bakeResults(outputOffsetList, sm=True, t=(startF, endF),
    at=("tx", "ty", "tz", "rx", "ry", "rz"));
    
    # delete temp nodes
    for node in inputSourceList:
        if cmds.objExists(node): cmds.delete(node);
    for node in culNodeList:
        if cmds.objExists(node): cmds.delete(node);
    
    for ctrl in controllerList:
        sourceCtrl = ctrl;
        sidePrefix = ctrl[0:2];
        
        if "l_" == sidePrefix:
            sourceCtrl = ctrl.replace("l_", "r_", 1);
        elif "r_" == sidePrefix:
            sourceCtrl = ctrl.replace("r_", "l_", 1);
            
        if not sourceCtrl in outputDict.keys():
            continue;
        
        cmds.pointConstraint(outputDict[sourceCtrl], ctrl, mo=False);
        cmds.orientConstraint(outputDict[sourceCtrl], ctrl, mo=False);
    
    # delete outputNodes
    cmds.delete(outputOffsetList);
    
def mirrorFKIKSwitch():
    fkikSwitchList = cmds.ls("*_fkikSwitch_ctrl", type="transform");
    lSideSwitchList = [l for l in fkikSwitchList if "l_" == l[:2]];
    rSideSwitchList = [r for r in fkikSwitchList if "r_" in r[:2]];
    
    for lSide in lSideSwitchList:
        lSideCondition = cmds.getAttr("{}.FKIKSwitch".format(lSide));
        suffix = lSide[lSide.find("l_") + 2:];
        
        rSide = [r for r in rSideSwitchList if suffix in r];
        if rSide is None or len(rSide) == 0:
            print("mirror side fkikSwitch is not exist");
            return;
        rSide = rSide[0];
        rSideCondition = cmds.getAttr("{}.FKIKSwitch".format(rSide));
        
        cmds.setAttr("{}.FKIKSwitch".format(lSide), rSideCondition);
        cmds.setAttr("{}.FKIKSwitch".format(rSide), lSideCondition);
    
def mirrorPose():
    """
    1. get controllers on this scene
    2. 回転軸が同じor中心にあるコントローラについてはCoyoteの手法を利用して反転Rotを取得して、Proxyに接続後、該当コントローラに流す
    3. 回転軸が反転している場合は、念のためQuatに変換してから接続
    4. 移動はX軸ミラーのため、ｘのみー１をかけた値をセットする
    
    残タスク02/14
    ・対象コントローラをどう振り分けるか
    ・首のUp軸がXのため、現状ミラーに成功していない。この問題を解決しなければ、首・頭のミラーができない。
    """
    # controllerList var
    # TODO: reveal hierarchy automate
    behaviorAxisControllerSet = "mirror_system_behaviorAxis_ctrl_set";
    behaviorAxisControllerList = cmds.sets(behaviorAxisControllerSet, q=True);
    sameAxisControllerList = [
        "cog_ctrl",
        "r_foot_fk_ctrl",
        "l_foot_fk_ctrl",
        "r_foot_ik_ctrl",
        "l_foot_ik_ctrl",
        "lower_spine_ik_ctrl",
        "chest_ik_ctrl",
        "shoulder_ik_ctrl",
        "pelvis_fk_ctrl",
        "mid_spine_fk_ctrl",
        "chest_fk_ctrl",
        "shoulder_fk_ctrl",
        "front_armor_down_A_fk_ctrl",
        "front_armor_down_B_fk_ctrl",
        "front_armor_down_C_fk_ctrl",
        "front_armor_down_D_fk_ctrl"
    ];
    # TODO: head and neck, pattern differentAxis Xup
    
    mirrorPoseBehaviorAxis(behaviorAxisControllerList);
    mirrorPoseSameAxis(sameAxisControllerList);
    mirrorFKIKSwitch();
    
def maya_useNewAPI():
    pass
    
# apply
def main():
    if settings.operation == 0:
        exportPose();
    else:
        importPose();
    om.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # グリッドレイアウトを設定
        layout = QtWidgets.QGridLayout(self);
        
        # TODO:　以下のレイアウトはv１としての仮。あとでUIをアプデする際に大幅に変更するが、まずはメイン処理を優先する。
        # operation radioButton
        export = QtWidgets.QRadioButton("Export", self);
        imp = QtWidgets.QRadioButton("Import", self);

        # ラジオボタンのレイアウト配置
        layout.addWidget(export, 0, 0);
        layout.addWidget(imp, 0, 1);

        # 各ボタンについての内部情報を作成
        self.__operation = QtWidgets.QButtonGroup(self);
        self.__operation.addButton(export, 0);
        self.__operation.addButton(imp, 1);

        # Input filePass
        filePassLabel = QtWidgets.QLabel("FilePass", self);
        layout.addWidget(filePassLabel, 1,0);
        self.__filePass = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__filePass, 1,1);
        
        # fillePass ref button
        filePassButton = QtWidgets.QPushButton("Input FilePass", self);
        filePassButton.clicked.connect(self.refFileSet);
        layout.addWidget(filePassButton, 2, 0);
        
        # Mirror Pose Button
        mirrorButton = QtWidgets.QPushButton("Mirror Pose", self);
        mirrorButton.clicked.connect(mirrorPose);
        layout.addWidget(mirrorButton, 3, 0, 1, 2);
        
        # view img selected
        self.__poseImgLabel = QtWidgets.QLabel(self);
        self.__poseImgLabel.setPixmap(QtGui.QPixmap(settings.filePass));
        layout.addWidget(self.__poseImgLabel, 4, 0, 1, 2);
        
        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__operation.button(settings.operation).setChecked(True);
        self.__filePass.setText(settings.filePass);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.operation = self.__operation.checkedId();
        settings.filePass = str(self.__filePass.text());
        
    # set fille pass
    def refFileSet(self):
        operation = self.__operation.checkedId();
        if operation == 0:
            ffSetting = "*.jpeg;;*.png;;*.bmp;;*.tif;;*.gif;;*.iff;;*.psd;;*.json";
        else:
            ffSetting = "*.json";
        # ds2:Mayaスタイルダイアログ, cap:ダイアログタイトル, fm;0=保存モード1=開く, ff:ファイル形式指定
        filename = str(cmds.fileDialog2(
            ds=2, cap="Save Image", fm=0, ff=ffSetting
        )[0]);
        settings.filePass = filename;
        self.__filePass.setText(filename);
        
        if operation == 1 and ".json" in filename:
            json = filename[filename.rfind("/") + 1:];
            fname = json[:json.rfind(".json")];
            files = glob.glob("C:/Users/kn_un/Documents/maya/scripts/nkTools/importExport/{0}.*".format(fname));
            print(json, fname, files);
            if len(files) > 0:
                filename = files[0].replace("\\", "/");
            else:
                print("not found selected json img");
                return;
            self.__poseImgLabel.setPixmap(QtGui.QPixmap(filename));
        else:
            self.__poseImgLabel.setPixmap(QtGui.QPixmap(""));
            
    # Do mainMethod
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("importExportPoseTool");
        self.resize(1100, 700);

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
        self.operation = 0;
        self.filePass = "";

settings = Settings();