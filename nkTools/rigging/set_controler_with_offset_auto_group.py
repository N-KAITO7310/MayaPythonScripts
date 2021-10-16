#!/usr/bin/env python
# coding=utf-8

import maya.cmds as cmds;
import pymel.core as pm;

"""
機能要件：
コントローラに_offset、_autoのグループノードを作成し、offsetではワールドからの座標値を保持し、
コントローラは値０になるように配置する
Mayaキャラクタークリエーションp167:方法1を自動化
"""
def main():
    print("start...");

    # 選択したオブジェクトを取得
    selected = pm.selected();

    # 選択先が複数のジョイントである場合はループ処理
    for index, selectedObject in enumerate(selected):
        if not (selectedObject.type() == "joint"):# or pm.nodeType(obj) == "joint" or isinstance(obj, pm.nodetypes.Transform)
            # ジョイントでなければ次の選択オブジェクト
            print("this selected object is not joint :index" + str(index) + "type is " + str(selectedObject.type));
            continue;

        jointName = selectedObject.name();

        print("jointName is " + jointName);

        prefix = jointName;
        # ジョイントが＿を含みプリフィックスが付与されている場合、＿以前を取得
        if("_jnt" in jointName):
            # 腕ジョイント等ジョイント名にL＿を含んでいる場合、後ろから検索し取得するようにする
            if("L_" in jointName or "R_" in jointName):
                prefix = jointName[:jointName.rfind("_jnt")];
            else:
                prefix = jointName[:jointName.find("_jnt")];

        # カーブ作成
        crvShape = pm.createNode("nurbsCurve", skipSelect=True, name=prefix + "_ctrl_shape");
        # カーブ作成ヒストリノード
        mnCircle = pm.createNode("makeNurbCircle", skipSelect=True, name=prefix + "_mkCrv");
        # カーブのトランスフォームを受け取っておく
        trans = crvShape.getTransform();

        # makeNurbCircleのoutputCurveアトリビュートとnurbscurveのcreateアトリビュートを接続
        mnCircle.outputCurve >> crvShape.create;
        # 方向をx方向に向ける
        mnCircle.normal.set([1, 0, 0]);
        # radiusアトリビュートで大きさを調整 ＊後でウィンドウ入力で調整できるようにする
        mnCircle.radius.set(0.6);

        print("curve created!");

        # カーブを子にautoグループノード、offsetグループノードを作成
        offsetSuffix = "_offset_grp";
        autoSuffix = "_auto_grp";
        offsetGrp = pm.createNode("transform", n=prefix + offsetSuffix);
        autoGrp = pm.createNode("transform", n=prefix + autoSuffix, p=offsetGrp);

        print("offsetGrp and autoGrp is created!");

        # グループノードのトランスフォームをカーブに合わせる
        pm.matchTransform(offsetGrp, crvShape, pos=True, rot=True);
        pm.matchTransform(autoGrp, crvShape, pos=True, rot=True);

        print("transform is matched");

        # カーブをautoの子としてペアレント
        crvShape.setParent(autoGrp);

        # offsetをジョイントの子としてペアレント
        offsetGrp.setParent(selectedObject);

        # offset_grpのtranslateとrotationを0に変更
        pm.setAttr(offsetGrp + '.translate', 0, 0, 0, type="double3");
        pm.setAttr(offsetGrp + '.rotate', 0, 0, 0, type="double3");

        # offsetのペアレントを解除(world=True)でワードにペアレントすることで解除
        offsetGrp.setParent(world=True);

        # 不要なカーブのトランスフォームノードを削除
        pm.delete(trans);
        
        # カーブのトランスフォームノードの名称変更
        crvTrans = crvShape.getTransform().rename(prefix + "_ctrl");

        # 作成したカーブのヒストリ削除
        cmds.delete(str(crvShape), constructionHistory = True);

        # 選択されたジョイントと作成したコントローラをコンストレイントする(あとでウィンドウで任意のコンストレイントができるよう機能追加する)
        cmds.orientConstraint(str(crvTrans), str(selectedObject), mo=False);

        # offsetグループノードのトランスフォームをロックする
        cmds.setAttr(str(offsetGrp) + ".tx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".ty", lock=True);
        cmds.setAttr(str(offsetGrp) + ".tz", lock=True);
        cmds.setAttr(str(offsetGrp) + ".rx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".ry", lock=True);
        cmds.setAttr(str(offsetGrp) + ".rz", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sy", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sz", lock=True);
    
        # 完了をプリント
        print("complete!");