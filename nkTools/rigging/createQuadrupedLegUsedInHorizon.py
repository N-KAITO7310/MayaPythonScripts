# -*- coding: utf-8 -*-
import maya.cmds as cmds;

"""

Horizon Zero Dawnの四足動物の後ろ足3boneIKをするscript

3boneIKのルートジョイントから4つ、5つ目にコントローラオブジェクトを選択して実行
prerequisite:
    primaryAxis:x
    2つ目のジョイントの移動値にx以外値が入っていないこと

Reference:
https://www.youtube.com/watch?v=50mIKB-NACU&t=3043s

lastUpdated: 23/05/20
*作成時点ではあくまでサンプルを再現するものとして制作したためPV作成、左右での処理分けは行っていない

"""

def createQuadrupedLegUsedInHorizon():
    cmds.undoInfo(openChunk=True);
    
    ikBaseJnts = cmds.ls(sl=True, type="joint")[0:4];
    ikRootJnt = ikBaseJnts[0];
    
    ikCtrl = cmds.ls(sl=True, type="transform")[4];
    
    duplicatedJnts = cmds.duplicate(ikRootJnt, renameChildren=True);
    ikHelperJnts = [];
    helperJntsNameList = ["ikHelper_A_jnt", "ikHelper_B_jnt", "tempDupcated_jnt", "ikHelper_C_jnt"];
    
    for i, duplicatedJnt in enumerate(duplicatedJnts):
        helperJntsNameList.append(cmds.rename(duplicatedJnt, helperJntsNameList[i]));

    femurToTibiaLen = cmds.xform(helperJntsNameList[1], q=True, translation=True)[0];
    tarsusToMetatarsus = cmds.xform(helperJntsNameList[3], q=True, translation=True)[0];

    cmds.parent(helperJntsNameList[3], w=True);
    cmds.delete(helperJntsNameList.pop(2));
    
    helperBLen = femurToTibiaLen + tarsusToMetatarsus;
    
    cmds.xform(helperJntsNameList[1], translation=(helperBLen, 0.0, 0.0));
    
    cmds.parent(helperJntsNameList[2], helperJntsNameList[1]);
    
    ikHelperHandle =  cmds.ikHandle(n="{}_ikHelper_ikHandle".format(ikRootJnt), sj=helperJntsNameList[0], ee=helperJntsNameList[2])[0];
    ikBaseHandle = cmds.ikHandle(n="{}_ikBase_ikHandle".format(ikRootJnt), sj=ikBaseJnts[1], ee=ikBaseJnts[3])[0];
    
    cmds.connectAttr("{}.rotate".format(helperJntsNameList[0]), "{}.rotate".format(ikBaseJnts[0]));
    
    cmds.parent(ikHelperHandle, ikBaseHandle, ikCtrl);
    
    cmds.undoInfo(closeChunk=True);
    

if __name__ == "__main__":
    createQuadrupedLegUsedInHorizon();