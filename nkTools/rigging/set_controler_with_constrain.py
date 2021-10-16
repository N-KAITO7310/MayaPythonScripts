# -*- coding: utf-8 -*-
import maya.cmds as cmds;
import pymel.core as pm
from pymel.core.general import createNode;

"""
コンストレイント利用によるコントローラカーブのスナップ＆offset_grpの作成
Mayaキャラクタークリエーションp167：方法2を自動化
"""

def main():
    print("set_controler_with_constrain start...");

    # 選択オブジェクトをチェックし、対象のジョイントを取得
    selectedObjects = pm.selected();
    for index, selected in enumerate(selectedObjects):
        if not(selected.type() == "joint"):
            print("please select joint");
            continue;

        jointName = selected.name();
        print("jointName is " + jointName);

        prefix = jointName;
        if("_jnt" in jointName):
            prefix = jointName[:jointName.rfind("_jnt")];

        # カーブオブジェクトを作成
        crvShape = pm.createNode("nurbsCurve", skipSelect=True, name=prefix + "_ctrl_shape");
        mnCircle = pm.createNode("makeNurbCircle", skipSelect=True, name=prefix + "_mkCrv");
        trans = crvShape.getTransform();
        mnCircle.outputCurve >> crvShape.create;
        mnCircle.normal.set([1, 0, 0]);
        mnCircle.radius.set(0.4);
        print("curve created!");

        # offset_grpを作成し、カーブを子にする
        OFFSET_SUFFIX = "_offset_grp";
        AUTO_SUFFIX = "_auto_grp";
        offsetGrp = pm.createNode("transform", n=prefix + OFFSET_SUFFIX);
        autoGrp = pm.createNode("transform", n=prefix + AUTO_SUFFIX, p=offsetGrp);
        pm.matchTransform(offsetGrp, crvShape, pos=True, rot=True);
        pm.matchTransform(autoGrp, crvShape, pos=True, rot=True);
        crvShape.setParent(autoGrp);
        
        # 不要になったカーブのトランスフォームを削除し、新しく作成されたトランスフォームの名称を変更する
        pm.delete(trans);
        crvTrans = crvShape.getTransform().rename(prefix + "_ctrl");

        # オフセットオフでペアレントコンストレイントを行い、カーブをスナップ
        pConstrain =  cmds.parentConstraint(str(selected), str(offsetGrp), mo=False, weight=1);

        # コンストレイントを削除
        cmds.delete(str(pConstrain[0]));

        # 選択されたジョイントと作成したコントローラをコンストレイントする(あとでウィンドウで任意のコンストレイントができるよう機能追加する)
        cmds.orientConstraint(str(crvTrans), str(selected), mo=False);
        # cmds.parentConstraint(str(crvTrans), str(selected), mo=False);

        # offset_grpをロック
        """
        cmds.setAttr(str(offsetGrp) + ".tx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".ty", lock=True);
        cmds.setAttr(str(offsetGrp) + ".tz", lock=True);
        cmds.setAttr(str(offsetGrp) + ".rx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".ry", lock=True);
        cmds.setAttr(str(offsetGrp) + ".rz", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sx", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sy", lock=True);
        cmds.setAttr(str(offsetGrp) + ".sz", lock=True);
        """

        print("complete! " + jointName);