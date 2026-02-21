from ScopeFoundry import HardwareComponent
from ni_co_device import NI_CO_device
import nidaqmx.system as ni


class NI_CO_hw(HardwareComponent):
    name = "NI_CO_hw"

    def setup(self):
        #create logged quantities, that are related to the graphical interface
        board, terminals, trig = self.update_channels()

        self.devices = self.add_logged_quantity('device',  dtype=str, initial=board)        
        self.channel = self.add_logged_quantity('channel', dtype=str, choices=terminals, initial=terminals[0])
        self.channel.change_readonly(True)
        self.pulse_terminal = self.add_logged_quantity( "pulse_terminal", dtype=str, choices=["/Dev1/PFI12"], initial="/Dev1/PFI12" )
        self.pulse_terminal.change_readonly(True)

        self.initial_delay = self.add_logged_quantity('initial_delay', dtype=float, initial=0, vmin=0, spinbox_decimals=2, unit='s')
        self.freq = self.add_logged_quantity('freq', dtype = float, si = False, ro = 0, initial = 20, vmin=1, vmax=30, spinbox_decimals=2, unit='Hz')
        self.duty_cycle = self.add_logged_quantity('duty_cycle', dtype=float, initial=0.05, spinbox_decimals=3, vmin=0, vmax=1)
       
        # Mode A/B
        self.run_mode = self.add_logged_quantity("run_mode", dtype=str, choices=["continuous", "finite"], initial="continuous")
        self.n_pulses = self.add_logged_quantity("n_pulses", dtype=int, initial=50, vmin=1)

        """
        self.trigger=self.add_logged_quantity('trigger',dtype=bool, initial=False)
        self.trigger_source= self.add_logged_quantity('trigger_source', dtype=str, choices=trig, initial=(trig[0] if len(trig) else "/Dev1/PFI0"))
        self.trigger_edge= self.add_logged_quantity('trigger_edge', dtype=str, choices=['rising', 'falling'], initial='rising')
        """
        self.add_operation("start_task", self.start)
        self.add_operation("stop_task", self.stop)

    def connect(self):
        
        #open connection to hardware
        self.channel.change_readonly(True)
        
        try:
            self.CO_device = NI_CO_device(channel=self.channel.val, initial_delay=self.initial_delay.val, pulse_terminal=self.pulse_terminal.val, freq=self.freq.val, 
                                          duty_cycle=self.duty_cycle.val, run_mode=self.run_mode.val, n_pulses=self.n_pulses.val, debug=self.debug_mode.val)
        except Exception as e:
            self.log.error(f"NI_CO_hw connect failed: {e}")
            self.CO_device = None
            return

        #connect logged quantities
        self.initial_delay.hardware_set_func = self.CO_device.set_initial_delay
        self.freq.hardware_set_func = self.CO_device.set_freq
        self.duty_cycle.hardware_set_func = self.CO_device.set_duty_cycle
        self.run_mode.hardware_set_func = self.CO_device.set_run_mode
        self.n_pulses.hardware_set_func = self.CO_device.set_n_pulses
        
        """
        self.trigger.hardware_set_func = self.CO_device.set_trigger
        self.trigger_source.hardware_set_func = self.CO_device.set_trigger_source
        self.trigger_edge.hardware_set_func = self.CO_device.set_trigger_edge
        """
        """
        self.initial_delay.hardware_read_func = self.get_initial_delay
        self.freq.hardware_read_func = self.get_freq
        self.duty_cycle.hardware_read_func = self.get_duty_cycle
        self.run_mode.hardware_read_func = self.get_run_mode
        self.trigger.hardware_read_func = self.get_trigger
        self.trigger_source.hardware_read_func = self.get_trigger_source
        self.trigger_edge.hardware_read_func = self.get_trigger_edge
        """        
   
    def disconnect(self):
        self.channel.change_readonly(False)

        if getattr(self, "CO_device", None) is not None:
            self.CO_device.close()
            self.CO_device = None

        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None

    
    def start(self):
        if getattr(self, "CO_device", None) is None:
            self.log.error("NI_CO_hw: start requested but NI device is not connected.")
            return
        self.CO_device.start_task()

    def stop(self):
        if getattr(self, "CO_device", None) is None:
            return
        self.CO_device.stop_task()

    def update_channels(self):
        system = ni.System.local()
        dev_names = list(system.devices.device_names)

        # Fallback: allow UI to load without hardware
        if len(dev_names) == 0:
            board = "NI not connected"
            terminals = ["Dev1/ctr0", "Dev1/ctr1"]
            trig = [f"/Dev1/PFI{i}" for i in range(16)]
            return board, terminals, trig

        device = system.devices[0]
        board = device.product_type + " : " + device.name
        terminals=[]
        trig=[]
        for line in device.co_physical_chans:
            terminals.append(line.name)
        for j in device.terminals:
            if 'PFI' in j:
                trig.append(j)
                
        return board, terminals, trig
   
    """
    def get_initial_delay(self):

        return float("{0:.6f}".format(self.initial_delay.val))
    
    def get_freq(self):

        return float("{0:.6f}".format(self.freq.val))
    
    def get_duty_cycle(self):
        
        return float("{0:.2f}".format(self.duty_cycle.val))
    
    def get_run_mode(self):

        return self.run_mode.val
    
    def get_trigger(self):
        
        return self.trigger.val
    
    def get_trigger_source(self):

        return self.trigger_source.val
    
    def get_trigger_edge(self):
        
        return self.trigger_edge.val
    """