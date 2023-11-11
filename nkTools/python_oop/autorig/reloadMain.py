# -*- coding: utf-8 -*-

from modules import reloadModules;
from utils import reloadUtils;
from ui import reloadUi;
import autorig_settings;

def reloadIt():
    reload(reloadModules);
    reload(reloadUi);
    reload(reloadUtils);
    reload(autorig_settings);

    reloadModules.reloadIt();
    reloadUi.reloadIt();
    reloadUtils.reloadIt();


    print("---------- MAIN RELOAD : OK ----------");