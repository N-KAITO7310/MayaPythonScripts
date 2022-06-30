import maya.cmds as cmds;
import maya.mel as mel;

class ZubriggHelpers(object):
    def __init__():
        pass;
        
    @classmethod
    def add_attr(cls, node, long_name, attr_type, default_value, keyable=False):
        cmds.addAttr(node, longName=long_name, attributeType=attr_type, defaultValue=default_value, keyable=keyable);

    @classmethod
    def set_attr(cls, node, attr, value, value_type=None):
        if value_type:
            # expect a list that will be unpacked for the command
            cmds.setAttr("{}.{}".format(node, attr), *value, type=value_type);
        else:
            cmds.setAttr("{}.{}".format(node, attr), value);
            
    @classmethod
    def connect_attr(cls, node_a, attr_a, node_b, attr_b, force=False):
        cmds.connectAttr("{}.{}".format(node_a, attr_a), "{}.{}".format(node_b, attr_b), force=force);

    @classmethod
    def lock_and_hide_attr(cls, node, attrs, lock=True, hide=True, channelBox=False):
        keyable = not hide;
        for attr in attrs:
            full_name = "{}.{}".format(node, attr);
            cmds.setAttr(full_name, lock=lock, keyable=keyable, channelBox=channelBox);
            
    @classmethod
    def create_display_layer(cls, name, members, reference=False):
        display_layer = cmds.createDisplayLayer(name=name, empty=True);
        
        if reference:
            cmds.setAttr("{0}.displayType".format(display_layer), 2);
            
        if members:
            cmds.editDisplayLayerMembers(display_layer, members, noRecurse=True);
            
        return display_layer;
            
class ZubriggCurveLibrary(object):
    
    def __init__(self):
        pass;
    
    @classmethod
    def circle(cls, radius=1, name="circle_crv"):
        return cmds.circle(center(0, 0, 0), normal=(0, 1, 0), radius=radius, name=name)[0];
    
    @classmethod
    def two_way_arrow(cls, name="two_way_arrow_crv"):
        return cmds.curve(
            degree=1,
            point=[(-1, 0, -2), (-2, 0, -2), (0, 0, -4), (2, 0, -2), (1, 0, -2), (1, 0, 2), (2, 0, 2), (0, 0, 4), 
            (-2, 0, 2), (-1, 0, 2), (-1, 0, -2)],
            knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            name=name
        );
        

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
        anim_controls_grp = cmds.group(n="anim_controls", em=True, parent=root_grp);
        geometry_grp = cmds.group(n="geometry", em=True, parent=root_grp);
        
        ball_geo = self.create_ball("ball_geo", parent=geometry_grp);
        ball_ctrl = self.create_ball_ctrl("ball_ctrl", parent=anim_controls_grp);
        
        cmds.parentConstraint(ball_ctrl, ball_geo, maintainOffset=True, weight=1);
        
        ZubriggHelpers.create_display_layer("ball_geometry", [ball_geo], True);
        
    def create_ball(self, name, parent=None):
        ball_geo = cmds.sphere(pivot=(0, 0, 0), axis=(0, 1, 0), radius=1, name=name)[0];
        if parent:
            ball_geo = cmds.parent(ball_geo, parent)[0];
            
        return ball_geo;
        
    def create_ball_ctrl(self, name, parent=None):
        ball_ctrl = ZubriggCurveLibrary.two_way_arrow(name=name);
        if parent:
            ball_ctrl = cmds.parent(ball_ctrl, parent)[0];
            
        ZubriggHelpers.lock_and_hide_attr(ball_ctrl, ["sx", "sy", "sz", "v"]);
        ZubriggHelpers.set_attr(ball_ctrl, "rotateOrder", 3);
            
        return ball_ctrl;
        
        
if __name__ == "__main__":
    cmds.file(newFile=True, force=True);
    
    ball = BallAutoRig();
    ball.construct_rig();
    