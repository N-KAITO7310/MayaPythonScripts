# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;

"""
install
from nkTools.rigging import fkikSnap_v1;
reload(fkikSnap_v1);
fkikSnap_v1;

how to use
1. select fkikSwitchCtrl
2. apply
"""

"""
要件定義
・はじめに選択されたコントローラからFKIKアトリビュートを取得する
・FKIKそれぞれで条件分け(メソッド切り出し)
・FKの場合
    ・作成しておいたIKスナップドライバー(回転値を直接コネクト)から値を取得し、FKコントローラにセットするか、単にマッチトランスの回転のみを使用する
    ・この処理を肩、肘、手首に対して行う
・IKの場合
    ・作成しておいた、FKにペアレントしている既定のロケーターを取得。
    ・肘、手のコントローラをそれぞれそのロケータにマッチトランスフォームする
・FKIKアトリビュートを切り替える
"""
FKIK = ".FKIKSwitch";
SWITCHSUFIX = "_fkikSwitch_ctrl";
IKDRIVERSUFIX = "_ik_rot";
fkToIkSwitchTable = {"l_arm":[["l_upperArm_fk_ctrl", "l_upperArm_ik_rot"], ["l_lowerArm_fk_ctrl", "l_lowerArm_ik_rot"], ["l_hand_fk_ctrl", "l_hand_ik_rot"]] ,
                    "r_arm":[["r_upperArm_fk_ctrl", "r_upperArm_ik_rot"], ["r_lowerArm_fk_ctrl", "r_lowerArm_ik_rot"], ["r_hand_fk_ctrl", "r_hand_ik_rot"]],
                    "l_leg":[["l_upperLeg_fk_ctrl", "l_upperLeg_ik_rot"], ["l_lowerLeg_fk_ctrl", "l_lowerLeg_ik_rot"], ["l_foot_fk_ctrl", "l_foot_ik_rot"]],
                    "r_leg":[["r_upperLeg_fk_ctrl", "r_upperLeg_ik_rot"], ["r_lowerLeg_fk_ctrl", "r_lowerLeg_ik_rot"], ["r_foot_fk_ctrl", "r_foot_ik_rot"]]};

ikToFkSwitchTable = {"l_arm":[["l_elbow_pv_ctrl", "l_arm_elobow_fkikSnap_loc",], ["l_hand_ik_ctrl", "l_arm_hand_fkikSnap_loc"]] ,
                    "r_arm":[["r_elbow_pv_ctrl", "r_arm_elobow_fkikSnap_loc",], ["r_hand_ik_ctrl", "r_arm_hand_fkikSnap_loc"]],
                    "l_leg":[["l_knee_pv_ctrl", "l_leg_knee_fkikSnap_loc",], ["l_foot_ik_ctrl", "l_leg_foot_fkikSnap_loc"]],
                    "r_leg":[["r_knee_pv_ctrl", "r_leg_knee_fkikSnap_loc",], ["r_foot_ik_ctrl", "r_leg_foot_fkikSnap_loc"]]};

axisList = ["X", "Y", "Z"];

def fkToIk(fkikCtrl):
    key = fkikCtrl[:fkikCtrl.rfind(SWITCHSUFIX)];
    fkToIkSorceList = fkToIkSwitchTable[key];
    for fkToIkSorce in fkToIkSorceList:
        driven = fkToIkSorce[0];
        driver = fkToIkSorce[1];
        for axis in axisList:
            rot = cmds.getAttr("{0}.rotate{1}".format(driver, axis));
            cmds.setAttr("{0}.rotate{1}".format(driven, axis), rot);

def ikToFk(fkikCtrl):
    key = fkikCtrl[:fkikCtrl.rfind(SWITCHSUFIX)];
    print(key);
    ikToFkSorceList = ikToFkSwitchTable[key];
    print(ikToFkSorceList);
    for ikToFkSorce in ikToFkSorceList:
        driven = ikToFkSorce[0];
        driver = ikToFkSorce[1];
        print(driven, driver);
        cmds.matchTransform(driven, driver);


# main
fkikCtrl = str(cmds.ls(sl=True)[0]);
fkikStatus = cmds.getAttr(fkikCtrl + FKIK);

if fkikStatus == 0:
    ikToFk(fkikCtrl);
    cmds.setAttr(fkikCtrl + FKIK, 1);
else:
    fkToIk(fkikCtrl);
    cmds.setAttr(fkikCtrl + FKIK, 0);
    
print("Done");






