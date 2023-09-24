# -*- coding: utf-8 -*-
import maya.cmds as cmds;
import pymel.core as pm;

"""

ShowControllerCameraWindow
created: 2021/12/28

非汎用、自作リグシーン専用。
UIとしてデザインされたコントローラーを、パネルポップアップで表示する。
Rigシーンを開いた際に自動実行されるようscriptノードを埋め込む。

from nkTools.rigging import showControllerCameraWindow;
reload(showControllerCameraWindow);
showControllerCameraWindow;

"""

# create camera
existCamera = cmds.ls("forControl_camera*", type="transform");
if len(existCamera) == 0:
    camera = cmds.camera(n="forControl_camera");
else:
    print(existCamera);
    cameraShape = str(cmds.listRelatives(existCamera[0], s=True)[0]);
    camera = [str(existCamera[0]), cameraShape];

# set window and tearoff
windowLabel = "Controller Panel"
window = cmds.window(w=600,h=540, title="Controller Panel Window")
frame = cmds.frameLayout( lv=0 )
model = cmds.modelPanel( l=windowLabel )
show = cmds.showWindow()

cmds.lookThru(camera[0],model);

# fit Camera to UI
cmds.select(cl=True);
targetObj = "wing_ui";
cmds.select(targetObj);
pm.viewFit(camera[1]);
cmds.select(cl=True);

# lock Camera
cmds.setAttr(camera[0] + ".visibility", 0);
cmds.camera(camera[0], e=True, lockTransform=True);

# set scriptNode for open scene
scripts = cmds.ls("scriptNode_forCameraOpen", type="script");
if len(scripts) == 0:
    cmds.scriptNode(n="scriptNode_forCameraOpen", st=1, stp="python", beforeScript="from nkTools.rigging import showControllerCameraWindow;reload(showControllerCameraWindow);showControllerCameraWindow;");