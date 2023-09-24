# -*- coding: utf-8 -*-
import maya.cmds as cmds;

"""
RenameSuffixByGrp
created: 2021/07/25

親group名から、配下のオブジェクトを一括リネームする

"""
def main():
    # 定数
    SUFFIX_JNT = "_jnt";
    SUFFIX_CTRL = "_ctrl";
    SUFFIX_GEO = "_geo";
    SUFFIX_GRP = "_grp";
    OBJECTTYPE_TRANSFORM = "transform";
    OBJECTTYPE_JOINT = "joint";
    OBJECTTYPE_CURVE = "nurbsCurve";
    OBJECTTYPE_GEO = "mesh";

    # 選択オブジェクトの取得とチェック
    objects = cmds.ls(sl=True);
    for object in objects:
        if not SUFFIX_GRP in str(objects) and cmds.objectType(object) != OBJECTTYPE_TRANSFORM:
            print("Please select groupNode");
            return;

        # objectの名称で接頭辞を作成(_以前で決定)
        prefix = str(object)[:str(object).rfind(SUFFIX_GRP)];

        # 子ノードの取得
        children = cmds.listRelatives(object, c=True);
        if len(children) <= 0:
            print("This grp is empty. objectName:" + object);
            return;

        for index, child in enumerate(children):
            # 子ノードが複数ある場合は番号を振る、一つの場合は空文字
            number = "";
            if len(children) > 1:
                number = str(index + 1);

            # ジョイントの場合はそのままリネームし、さらに下の階層でトランスフォームノードが現れるまでリネーム処理を行う*一階層に複数のジョイントがある場合までは対応しない
            if cmds.objectType(child) == OBJECTTYPE_JOINT:
                childExist = True if cmds.listRelatives(child, c=True) > 0 else False;
                if childExist:
                    number = str(1);
                thisJnt = cmds.rename(str(child),  prefix + number + SUFFIX_JNT);
                while childExist:
                    number = str(int(number) + 1);
                    childJnt = cmds.listRelatives(thisJnt, c=True)[0];

                    # ジョイントでなければ処理を終了。条件："_jnt" in str(childJnt)はリネームを再度行いたい際に不要のため削除7/25
                    if  cmds.objectType(childJnt) != "joint":
                        return;

                    thisJnt = cmds.rename(str(childJnt),  prefix + number + SUFFIX_JNT);
                    childExist = True if cmds.listRelatives(thisJnt, c=True) > 0 else False;

                print("complete rename joint hierarchy");
                return;

            elif cmds.objectType(child) != OBJECTTYPE_TRANSFORM:
                # 子ノードがジョイントでもトランスフォームノードでもなく、想定しないものである場合は処理を行わない(基本の想定はシェイプのトランスフォーム)
                continue;
           
            # トランスフォームノードのシェイプを取得
            shapes = cmds.listRelatives(child, s=True, c=True)
            if len(shapes) <= 0:
                # シェイプを持たないトランスフォームノードの場合スキップ
                print("This transform is empty");
                continue;

            # ＿を名称に持っている場合は既に名前付けがされていると判断しスキップ
            if "_" in str(child):
                continue;

            # 基本的にシェイプは一つと想定する
            shape = shapes[0];
            
            # シェイプのタイプ毎でリネーム
            type = cmds.objectType(shape);
            if type == OBJECTTYPE_CURVE:
                cmds.rename(str(child),  prefix + number + SUFFIX_CTRL);
            elif type == OBJECTTYPE_GEO:
                cmds.rename(str(child),  prefix + number + SUFFIX_GEO);
            else:
                # 上記以外のタイプの場合でリネームするかは今後検討
                continue;

    # さらに下の階層までリネームするかは今後検討(ウィンドウを制作する場合に孫階層以下に関してオプションがあるとよいかもしれない)