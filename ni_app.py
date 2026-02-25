"""
Created on Feb 15 01:23:00 2026

@authors: Andrea Bassi, Yoginder Singh, Politecnico di Milano
"""

from ScopeFoundry import BaseMicroscopeApp

def add_path(path):
    import sys
    import os
    # add path to ospath list, assuming that the path is in a sybling folder
    from os.path import dirname
    sys.path.append(os.path.abspath(os.path.join(dirname(dirname(__file__)),path)))


class NI_App(BaseMicroscopeApp):

    name = 'ni_app'
    
    def setup(self):
        
        #Add hardware components
        print("Adding Hardware Components") 
       #from ni_ao_hardware import NI_AO_hw
       #from ni_do_hardware import NI_DO_hw
        from ni_co_hardware import NI_CO_hw
       #self.add_hardware(NI_AO_hw(self))
       #self.add_hardware(NI_DO_hw(self))
        self.add_hardware(NI_CO_hw(self))
        
        #Add measurement components
        print("Create Measurement objects")
        add_path('ImageFlowCytometry_System')
        from IFC_measurement import IfcMeasure
        self.add_measurement(IfcMeasure(self))
        
        # show ui
        if hasattr(self, "ui") and (self.ui is not None):
            self.ui.show()
            self.ui.activateWindow()
        else:
            print("ScopeFoundry UI not available as self.ui in this version. App will still run.")

if __name__ == '__main__':
    import sys
    
    app = NI_App(sys.argv)

    sys.exit(app.exec_())