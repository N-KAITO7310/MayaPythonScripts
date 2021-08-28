# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;

"""
要件：FKIK併用コントロールの自動化
前提条件：FKジョイントとIKジョイントが既に設置されていること

流れ：
コントローラを設置するＦＫジョイント、開始終中間点のＩＫジョイントを選択して読み込む
スプラインIKの作成(スパン数はオプション)
ＩＫハンドルとカーブをリネーム
ＩＫの開始中間終点のジョイント位置に大きめのサイズでジョイントを配置
３つの独立したジョイントをカーブとスキニング
オフセットグループを持ったコントローラカーブを作成してあの方法でペアレントコンストレイン
それぞれのジョイントに対しコントローラを同様に設置
スプラインIKハンドルのIKソルバでツイストコントロールを有効化
ほかワールドアップタイプ、ワールドアップオブジェクト、ワールドアップオブジェクト２に開始と終了のコントロールをセット

カーブの長さを調べる
multiplyDivideを作成、除算にセット
カーブの円弧長を接続、入力に同じ値をセット
もう一つ乗算除算を用意し、対象のジョイントの移動ｘをコピー
乗算除算ノードの出力をジョイントに接続

ＦＫを通常通りにセットアップ(コントローラ設置位置が必要か)
IKをFKにペアレント化

必要情報：
・コントローラを設置するFKジョイント
・開始、中間、終点のIKジョイント
・コントローラの半径（シェイプは固定
・接頭辞にする名前

作成流れ
対象ジョイントの読み込みウィンドウの作成
あとはこれまでと同様
上記の流れに沿った処理を構築

from nkTools.rigging import setFKIKsplineController;
reload(setFKIKsplineController);
reload(setFKIKsplineController.qt);
setFKIKsplineController.option();
"""

def setFKIKsplineController():
    # 変数準備
    fkJointList = settings.fkJointList;
    ikJointList = settings.ikJointList;
    ikRoot = settings.ikRoot;
    ikMiddle = settings.ikMiddle;
    ikEnd = settings.ikEnd;
    diameter = settings.diameter;
    prefix = settings.prefix;

    # IKsplineハンドルの作成
    splineIkName = prefix + "_spline_IK"
    splineIkResult = cmds.ikHandle(startJoint=ikRoot, endEffector=ikEnd,sol="ikSplineSolver", tws="easeInOut", ns=2, n=splineIkName);
    splineCurve = str(splineIkResult[2])
    # TODO:splineカーブの名前付け
    # TODO:カーブのトランスフォームの継承をオフにするp183
    cmds.select( clear=True );

    # Ikの開始、中間、終点のそれぞれの位置に新しく独立したジョイントを配置する
    curveControleJointList = [prefix + "_root_ik_jnt", prefix + "_middle_ik_jnt", prefix + "_end_ik_jnt"];
    targetJoints = [ikRoot, ikMiddle, ikEnd];
    for i in range(3):
        cmds.joint(n=curveControleJointList[i], p=(0, 0, 0), rad=1.5)
        cmds.matchTransform(curveControleJointList[i], targetJoints[i]);
        cmds.select( clear=True );

    # スキンバインド
    cmds.skinCluster(splineCurve, prefix + "_root_ik_jnt", prefix + "_middle_ik_jnt", prefix + "_end_ik_jnt");
    # 各IKジョイントにコントローラを設置

    createdIkCurveAndGroup = {};
    for index, ikSplineJoint in enumerate(curveControleJointList):
        # コントローラにつけるprefixを作成
        prefix = ikSplineJoint[:ikSplineJoint.rfind("_jnt")];

        # カーブオブジェクトを作成
        controllerName = prefix + "_ctrl";
        # 立方体
        point = settings.diameter * 1;
        cmds.curve(d=1, p=[(point, point, point), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point*-1, point*-1),(point, point*-1, point*-1), (point, point, point*-1), (point*-1, point, point*-1), (point*-1, point, point),(point, point, point), (point, point*-1, point), (point, point*-1, point*-1), (point*-1, point*-1, point*-1),(point*-1, point*-1, point), (point, point*-1, point), (point*-1, point*-1, point), (point*-1, point, point)],
        k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], n=controllerName);

        # offset_grpを作成し、カーブを子にする
        OFFSET_SUFFIX = "_offset_grp";
        AUTO_SUFFIX = "_auto_grp";
        offsetGrp = pm.createNode("transform", n=prefix + OFFSET_SUFFIX);
        autoGrp = pm.createNode("transform", n=prefix + AUTO_SUFFIX, p=offsetGrp);
        pm.matchTransform(offsetGrp, controllerName, pos=True, rot=True);
        pm.matchTransform(autoGrp, controllerName, pos=True, rot=True);
        cmds.parent(controllerName, str(autoGrp));

        # オフセットオフでペアレントコンストレインを行い、カーブをスナップ
        pConstrain =  cmds.parentConstraint(str(ikSplineJoint), str(offsetGrp), mo=False, weight=1);

        # コンストレインを削除
        cmds.delete(str(pConstrain[0]));

        # ジョイントと作成したコントローラpコンストレインする
        cmds.parentConstraint(controllerName, str(ikSplineJoint), mo=False);

        # 階層化のため作成データを保持
        createdIkCurveAndGroup[index] = [controllerName, str(offsetGrp)];

    # IkSpline Twist Setting
    # IKハンドルのツイストコントロールを有効化
    cmds.setAttr(splineIkName + ".dTwistControlEnable", 1);
    cmds.setAttr(splineIkName + ".dWorldUpType", 4);
    cmds.setAttr(splineIkName + ".dTwistValueType", 1);
    # TODO:コントロール名をあとで変数に修正しておくこと
    cmds.connectAttr(createdIkCurveAndGroup[0][0] + ".worldMatrix[0]", splineIkName + ".dWorldUpMatrix", f=True);
    cmds.connectAttr(createdIkCurveAndGroup[2][0] + ".worldMatrix[0]", splineIkName +  ".dWorldUpMatrixEnd", force=True);
    
    # 伸縮性の構築
    # カーブの円弧長
    evalCommand = "arclen -ch 1 " + splineCurve + ";";
    arcInfo = mel.eval(evalCommand);
    arcLength = cmds.getAttr(str(arcInfo) + ".arcLength");
    curveLengthMd = "curveLength_md";
    cmds.shadingNode('multiplyDivide', asUtility=True, name=curveLengthMd);

    cmds.setAttr(curveLengthMd + ".operation", 2);
    cmds.connectAttr(str(arcInfo) + ".arcLength", curveLengthMd + ".input1X", f=True);
    cmds.setAttr(curveLengthMd + ".input2X", arcLength);

    # 各ジョイントにコネクト
    for ikJoint in ikJointList:
        if(str(ikJoint) == ikRoot):
            # rootジョイントには設定しない
            continue;

        jointLengthMd = str(ikJoint) + "_Length_md";
        cmds.shadingNode('multiplyDivide', asUtility=True, name=jointLengthMd);
        jointLength = cmds.getAttr(str(ikJoint) + ".translateX")
        cmds.setAttr(jointLengthMd + ".input2X", jointLength);
        cmds.connectAttr(curveLengthMd + ".outputX", jointLengthMd + ".input1X", f=True);
        cmds.connectAttr(jointLengthMd + ".outputX", str(ikJoint) + ".translateX", f=True);

    # fkジョイントをセッティング
    # jointName:[curveName, offsetGroupName]
    createdCurveAndGroup = {};
    for fkJoint in fkJointList:
        # コントローラにつけるprefixを作成
        fkPrefix = fkJoint[:fkJoint.rfind("_jnt")];

        # カーブオブジェクトを作成
        fkControllerName = fkPrefix + "_ctrl";
        # 円カーブ
        radius = diameter;
        cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, tol=0.01, s=8, ch=0, n=fkControllerName);

        # offset_grpを作成し、カーブを子にする
        OFFSET_SUFFIX = "_offset_grp";
        AUTO_SUFFIX = "_auto_grp";
        offsetGrp = pm.createNode("transform", n=fkPrefix + OFFSET_SUFFIX);
        autoGrp = pm.createNode("transform", n=fkPrefix + AUTO_SUFFIX, p=offsetGrp);
        pm.matchTransform(offsetGrp, fkControllerName, pos=True, rot=True);
        pm.matchTransform(autoGrp, fkControllerName, pos=True, rot=True);
        cmds.parent(fkControllerName, str(autoGrp));

        # オフセットオフでペアレントコンストレインを行い、カーブをスナップ
        pConstrain =  cmds.parentConstraint(fkJoint, str(offsetGrp), mo=False, weight=1);

        # コンストレインを削除
        cmds.delete(str(pConstrain[0]));

        # ジョイントと作成したコントローラpコンストレインする
        cmds.orientConstraint(fkControllerName, fkJoint, mo=False);

        # 作成データの相関を保持
        createdCurveAndGroup[fkJoint] = [fkControllerName, str(offsetGrp)];

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

            isSelectedParent = str(parentNode) in fkJointList;

            if isSelectedParent:
                # 下から最も階層の近いジョイントが見つかった場合、その親のカーブとこのジョイントのグループをペアレントする
                cmds.parent(group, createdCurveAndGroup[str(parentNode)][0]);
                break;
            else:
                # 直上の親が選択されたジョイントリストのものでない場合は、カーソルをこの親ノードにしループする
                targetCursol = str(parentNode);
                continue;

    # IKFK階層化
    # 一つ目のIKコントローラにFKをペアレント
    """mayaキャラクタークリエーションに準拠する場合は不要だが、念のため残す
    rootFk = fkJointList[0];
    rootfkGrp = createdCurveAndGroup[rootFk][1];
    cmds.parent(rootfkGrp, createdIkCurveAndGroup[0][0]);
    """
    # 中間のFKの一つ下に中間のIKをペアレント//TODO:FKとIKジョイントの数が違う場合は位置がずれるため、IKコントローラをセットした位置がわからないと最も適切な位置に配置することはできない
    underMiddleFk = fkJointList[int(len(fkJointList) / 2)-2];
    underMiddleFkCtrl = createdCurveAndGroup[underMiddleFk][0];
    middleIkGrp = createdIkCurveAndGroup[1][1];
    cmds.parent(middleIkGrp, underMiddleFkCtrl);
    # 中間のFKに最後のIKをペアレント化
    middleFk = fkJointList[int(len(fkJointList) / 2)-1];
    middleFkCtrl = createdCurveAndGroup[middleFk][0];
    endIkGrp = createdIkCurveAndGroup[2][1];
    cmds.parent(endIkGrp, middleFkCtrl);


# apply
def main():
    setFKIKsplineController();
    OpenMaya.MGlobal.displayInfo("Done");

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
        # ストッカービューを設定
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 0, 0, 1, 3);

        # モデルをビューにセット
        self.__model = StockItemModelFK(self);
        stockerView.setModel(self.__model);

        # loadボタン
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadFK)
        layout.addWidget(button, 1, 0);

        # ストッカービューを設定
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 2, 0, 1, 3);

        # モデルをビューにセット
        self.__ikModel = StockItemModelIK(self);
        stockerView.setModel(self.__ikModel);

        # loadボタン
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadIK)
        layout.addWidget(button, 3, 0);

        # IK:start
        ikRootLabel = QtWidgets.QLabel("IK:root", self);
        layout.addWidget(ikRootLabel, 4,0);
        self.__ikRoot = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__ikRoot, 4,1)

        # IK:middle
        ikMiddleLabel = QtWidgets.QLabel("IK:middle", self);
        layout.addWidget(ikMiddleLabel, 5,0);
        self.__ikMiddle = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__ikMiddle, 5,1)

        # IK:end
        ikEndLabel = QtWidgets.QLabel("IK:end", self);
        layout.addWidget(ikEndLabel, 6,0);
        self.__ikEnd = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__ikEnd, 6,1)

        # サイズの数値入力
        diameterLabel = QtWidgets.QLabel("Diameter", self);
        layout.addWidget(diameterLabel, 7,0);
        self.__diameter = QtWidgets.QDoubleSpinBox(self);
        self.__diameter.setMinimum(0);
        self.__diameter.setMaximum(100);
        self.__diameter.setDecimals(2);
        layout.addWidget(self.__diameter, 7,1);

        # prefix入力
        prefixLabel = QtWidgets.QLabel("Prefix", self);
        layout.addWidget(prefixLabel, 8,0);
        self.__prefix = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__prefix, 8,1)
        
        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__diameter.setValue(settings.diameter);
        self.__prefix.setText(settings.prefix);



    # ウィンドウで入力された値を設定にセット
    def saveSettings(self, fkModel, ikModel):
        settings.ikRoot = str(self.__ikRoot.text());
        settings.ikMiddle = str(self.__ikMiddle.text());
        settings.ikEnd = str(self.__ikEnd.text());
        settings.diameter = self.__diameter.value();
        settings.prefix = str(self.__prefix.text());

        settings.fkJointList = [];
        fkRowCount = self.__model.rowCount();
        for i in range(fkRowCount):
            settings.fkJointList.append(self.__model.rowData(i));

        settings.ikJointList = [];
        ikRowCount = self.__ikModel.rowCount();
        for i in range(ikRowCount):
            settings.ikJointList.append(self.__ikModel.rowData(i));


    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings(self.__model, self.__ikModel);
        main();

    def loadFK(self):
        self.__model.removeRows(0, self.__model.rowCount());
        jointList = cmds.ls(sl=True, type="joint");
        if not jointList:
            return;
        for joint in jointList:
            self.__model.appendItem(str(joint));

    def loadIK(self):
        self.__ikModel.removeRows(0, self.__ikModel .rowCount());
        jointList = cmds.ls(sl=True, type="joint");
        if not jointList:
            return;
        for joint in jointList:
            self.__ikModel.appendItem(str(joint));

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Set FKIKspline controller");
        self.resize(500, 500);

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


# 選択FKジョイントの表示ビュー
class StockerView(QtWidgets.QTreeView):
    mimeType = "application/x-mytool-copyattribute-data";

    def __init__(self, *args, **kwargs):
        super(StockerView, self).__init__(*args, **kwargs);
        # Ctrl,Shiftで選択可能設定
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection);
        # リストで交互に色を変更
        self.setAlternatingRowColors(True);
        # ルート表示不可に設定
        self.setRootIsDecorated(False);

    def removeSelectedItem(self):
        model = self.model();
        selModel = self.selectModel();

        while selModel.selectedIndexes():
            indexes = selModel.selectedIndexes();
            model.removeRow(indexes[0].row());


class StockItemModelFK(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelFK, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "FKjoints");

    def appendItem(self, jointName):
        # モデルに行を追加
        jointName = QtGui.QStandardItem(jointName);
        jointName.setEditable(False);

        self.appendRow([jointName]);

    def rowData(self, index):
        # 指定したインデックスの表示名を取得
        jointName = str(self.item(index, 0).text());

        return jointName;

class StockItemModelIK(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelIK, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "IKjoints");

    def appendItem(self, jointName):
        # モデルに行を追加
        jointName = QtGui.QStandardItem(jointName);
        jointName.setEditable(False);

        self.appendRow([jointName]);

    def rowData(self, index):
        # 指定したインデックスの表示名を取得
        jointName = str(self.item(index, 0).text());

        return jointName;

class Settings(object):
    def __init__(self):
        self.fkJointList = [];
        self.ikJointList = [];
        self.ikRoot = "";
        self.ikMiddle ="";
        self.ikEnd = "";
        self.diameter = 1;
        self.prefix = "spine";

settings = Settings();