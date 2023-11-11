# -*- coding: utf-8 -*-

import control;

def reloadIt():
    reload(control);
    reload(boneChain);
    reload(fkChain);
    reload(ikChain);
    reload(armModule);

    print("---------- MODULES RELOAD : OK ----------");