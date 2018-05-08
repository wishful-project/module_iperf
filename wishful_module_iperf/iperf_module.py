import logging
import subprocess
import wishful_upis as upis
import wishful_framework as wishful_module

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"

'''
    Packet flows are generated using IPerf tool.
'''


@wishful_module.build_module
class IperfModule(wishful_module.AgentModule):
    def __init__(self):
        super(IperfModule, self).__init__()
        self.log = logging.getLogger('IperfModule.main')
        self.trafficType = "udp"
        self.serverProc = None
        self.clientProc = None

    @wishful_module.bind_function(upis.net.create_packetflow_sink)
    def start_server(self, port):
        self.log.info("Starts iperf server on port {}".format(port))

        # iperf -s -u
        cmd = ['/usr/bin/iperf']
        cmd.extend(['-s'])
        cmd.extend(['-p', str(port)])
        if self.trafficType == "udp":
            cmd.extend(['-u'])

        self.serverProc = subprocess.Popen(cmd)
        self.log.info("iperf server started on port {} with PID: {}".format(port, self.serverProc.pid))
        return 0

    @wishful_module.bind_function(upis.net.destroy_packetflow_sink)
    def stop_server(self):
        if self.serverProc is None:
            return
        self.log.info("Stop iperf server with PID: {}".format(self.serverProc.pid))

        cmd = ['/bin/kill']
        cmd.extend(['-9'])
        cmd.extend([str(self.serverProc.pid)])
        subprocess.Popen(cmd)
        self.serverProc = None
        self.log.info("iperf server stopped")

        return 0

    @wishful_module.bind_function(upis.net.start_packetflow)
    def start_packetflow(self, dest_ip, port):
        self.log.info("Start iperf client to server IP: {}".format(dest_ip))
        # iperf -c 100.0.0.19 -t 1000000000 -u -b 200

        serverIp = dest_ip
        remotePort = port
        transmissionTime = 100000000
        bandwidth = '200M'

        cmd = ['/usr/bin/iperf']
        cmd.extend(['-c', str(serverIp)])
        cmd.extend(['-t', str(transmissionTime)])
        cmd.extend(['-p', str(remotePort)])
        if self.trafficType == "udp":
            cmd.extend(['-u'])
            cmd.extend(['-b', str(bandwidth)])

        self.clientProc = subprocess.Popen(cmd)
        self.log.info("iperf client started on port {} with PID: {}".format(port, self.clientProc.pid))
        return 0

    @wishful_module.bind_function(upis.net.stop_packetflow)
    def stop_packetflow(self):
        if self.clientProc is None:
            return
        self.log.info("Stop iperf client with PID: {}".format(self.clientProc.pid))

        cmd = ['/bin/kill']
        cmd.extend(['-9'])
        cmd.extend([str(self.clientProc.pid)])
        subprocess.Popen(cmd)
        self.clientProc = None
        self.log.info("iperf client stopped")
        return 0
