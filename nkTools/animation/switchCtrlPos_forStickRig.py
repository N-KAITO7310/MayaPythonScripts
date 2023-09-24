# -*- coding: utf-8 -*-

import maya.cmds as cmds;

"""

SwitchCtrlPos_forStickRig

created: 23/06/07

Description:非汎用。特定リグに対して使用。両側からの操作を可能とする槍などの棒状リグに対し利用し、持ち手を切り替えるためのスクリプト。

import nkTools.animation.SwitchCtrlPos_forStickRig as sw;
reload(sw);
sw.switchCtrlPos();

"""

bindJnt = "bind_jnt";
sourceLoc = "source_loc";
mainCtrl = "main_ctrl";
upCtrl = "up_ctrl";
botCtrl = "bot_ctrl";
upCtrlBotPos = "up_jnt_bot";
botCtrlUpPos = "bot_jnt_up";
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];

def switchCtrlPos():
    cmds.undoInfo(openChunk=True);
    
    newStatus = 0;
    currentCtrl = upCtrl;
    switchTo = botCtrl;
    newPos = botCtrlUpPos;
    status = cmds.getAttr("{}.change".format(mainCtrl));
    if status == 0:
        currentCtrl = botCtrl;
        newStatus = 1;
        switchTo = upCtrl;
        newPos = upCtrlBotPos;
        
    ff =  int(cmds.getAttr("{}.lastSwitchFrame".format(mainCtrl)));
    if ff == 0:
        ff = int(cmds.findKeyframe(currentCtrl, which="first"));
    ff = int(cmds.getAttr("{}.lastSwitchFrame".format(mainCtrl)));
    lf = int(cmds.findKeyframe(currentCtrl, which="last"));
    if not ff < lf:
        ff = int(cmds.findKeyframe(currentCtrl, which="first"));
    
    currentF = cmds.currentTime(q=True);
    cmds.currentTime(lf);

    # 一度既存のキーを一時ロケーターに保存する。
    for f in range(ff, lf+1):
        cmds.currentTime(f);
        pos = cmds.xform(bindJnt, q=True, ws=True, translation=True);
        rot = cmds.xform(bindJnt, q=True, ws=True, rotation=True);
        
        # cmds.xform(sourceLoc, translation=pos, ws=True);
        # cmds.xform(sourceLoc, rotation=rot, ws=True);
        # cmds.setKeyframe(sourceLoc, attribute=['translate', "rotate"]);
        
        switchToPos = cmds.xform(newPos, q=True, ws=True, translation=True);
        switchToRot = cmds.xform(newPos, q=True, ws=True, rotation=True);

        cmds.xform(switchTo, translation=switchToPos, ws=True);
        cmds.xform(switchTo, rotation=switchToRot, ws=True);
        cmds.setKeyframe(switchTo, attribute=['translate', "rotate"]);
    
    # cmds.bakeResults(sourceLoc, t="{}:{}".format(ff, lf), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        
    cmds.setAttr("{}.change".format(mainCtrl), newStatus);
    cmds.setAttr("{}.lastSwitchFrame".format(mainCtrl), lf);
    
    # cmds.cutKey(switchTo);
    cmds.currentTime(currentF);
    
    cmds.undoInfo(closeChunk=True);
    
if __name__ == "__main__":
    switchCtrlPos();