from maya import cmds


'''
要件
・以下のコードを連続したものに書き換える
・恐らく足りない部分があるので、その部分を補う
・リギングクラスのTipsも挟める部分があれば挟むか、オプションで選択できるように改良する
'''

# AutoRibbonRigGenerateTool

#Dash
#l(5.0, -5.0)

# jointOrient 0 0 0
joints = cmds.ls(selection=True, type="joint")
for joint in joints:
    cmds.setAttr("{}.jointOrient".format(joint), 0.0, 0.0 ,0.0)

# リネーム
nodes = cmds.ls(selection=True)
for i, node in enumerate(nodes):
    cmds.rename(node, "ribbon_ctrl{}".format(i))
    
# 親空間を作成する
nodes = cmds.ls(selection=True)
for node in nodes:
    joint = cmds.createNode("joint", name=node.replace("_ctrl", "_ctrlSpace"), parent=node)
    cmds.parent(joint, world=True)
    cmds.parent(node, joint)
    cmds.setAttr("{}.drawStyle".format(joint), 2)

# 選択したノードの子にジョイントを作成する
nodes = cmds.ls(selection=True)
for i, node in enumerate(nodes): 
    cmds.joint(node, name="ribbon_bindJoint{}".format(i))
    cmds.setAttr(".radius", 0.2)
    
# コントローラーを作成する
nodes = cmds.ls(sl=True)
for node in nodes:
    circle = cmds.circle(ch=False, radius=0.4)[0]
    circle_shape = cmds.listRelatives(circle, shapes=True)[0]
    cmds.parent(circle_shape, node, r=True, shape=True)
    
# drawStyleをNoneにする
nodes = cmds.ls(selection=True, type="joint")
for node in nodes:
    cmds.setAttr("{}.drawStyle".format(node), 2)