import maya.cmds as cmds;
import maya.mel as mel;

class BallAutoRig(object):
    
    def __init__(self):
        self.primary_color = [0.0, 0.0, 1.0];
        self.secondary_color = [1.0, 1.0, 1.0];
        
    def set_colors(self, primary, secondary):
        self.primary_color = primary;
        self.secondary_color = secondary;
        
    def construct_rig(self, name="ball"):
        cmds.select(clear=True);
        
        root_grp = cmds.group(n=name, em=True, world=True);
        anim_controls_geo = cmds.group(n="anim_controls", em=True, parent=root_grp);
        geometry_grp = cmds.group(n="geometry", em=True, parent=root_grp);
        
if __name__ == "__main__":
    cmds.file(newFile=True, force=True);
    
    ball = BallAutoRig();
    ball.construct_rig();