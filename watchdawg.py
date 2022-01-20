import datetime
import subprocess
import derek_functions as df
import time
from collections import defaultdict
import sys

class ServerHealth:

    def __init__(self) -> None:
        self.servers = ['192.168.2.70','192.168.2.71','192.168.2.72','192.168.2.73','192.168.2.22']
        self.first_run = True
        # Key is ip and val is last time seen up
        self.server_dict = defaultdict(lambda: 0)
        # Key is server val is 1 if server was down and notification sent otherwise 0
        self.needs_notfication = defaultdict(lambda: 0)
        self.minutes_downtime = 1
        self.servers_down = []
        self.sent_pi_notification = False
        self.server_name_dict = {}
        self.server_name_dict['192.168.2.70'] = 'laptop'
        self.server_name_dict['192.168.2.71'] = 'ogxps'
        self.server_name_dict['192.168.2.72'] = 'xps2'
        self.server_name_dict['192.168.2.73'] = 'xps3'
        self.server_name_dict['192.168.2.22'] = 'server'


    def is_server_down(self, ip) -> bool:
        status, result = subprocess.getstatusoutput(f"ping -c1 -w2 {ip}")
        if status == 0:
            return True
        return False


    def build_server_dict(self):
        for server in self.servers:
            status = self.is_server_down(server)
            if status:
                self.server_dict[server] = datetime.datetime.now()
            elif self.first_run:
                self.server_dict[server] = 0

        self.first_run = False

    def main(self):
        self.build_server_dict()

        for server, last_uptime in self.server_dict.items():
            # If the server has been down for 5 minutes send notification
            try:
                time_object = last_uptime + datetime.timedelta(minutes=self.minutes_downtime)
                if time_object < datetime.datetime.now():
                    name = self.server_name_dict[server]
                    time_message = datetime.datetime.now().strftime("%A, %B %d, at %I:%M %p")
                    message = f'{name} went down at {time_message}'
                    print(message)
                    if self.needs_notfication[server] == 0:
                        print('Going to send text')
                        df.sendText('+17153471797',message)
                    self.needs_notfication[server] = 1
                else:
                    self.needs_notfication[server] = 0
            except Exception as e:
                name = self.server_name_dict[server]
                time_message = datetime.datetime.now().strftime("%A, %B %d, at %I:%M %p")
                message = f'{name} went down at {time_message}'
                print(message)
                if self.needs_notfication[server] == 0:
                    print('Going to send text')
                    df.sendText('+17153471797',message)
                self.needs_notfication[server] = 1

            
    def pi_functions(self):
        self.build_server_dict()
        self.servers_down = []
        for server, last_uptime in self.server_dict.items():
            try:
                time_object = last_uptime + datetime.timedelta(minutes=self.minutes_downtime)
                if time_object < datetime.datetime.now():
                    if server not in self.servers_down:
                        self.servers_down.append(server)
            except Exception as e:
                print('Server was down when started')
                if server not in self.servers_down:
                    self.servers_down.append(server)

        if len(self.servers_down) >= 3 and self.sent_pi_notification == False:
            time_message = datetime.datetime.now().strftime("%A, %B %d, at %I:%M %p")
            message = f'The cluster went down at {time_message}'
            print(message)
            df.sendText('+17153471797',message)
            self.sent_pi_notification = True

        if len(self.servers_down) < 3:
            self.sent_pi_notification = False



def main():
    s = ServerHealth()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'pi':
            print('Running pi functions')
            while True:
                s.pi_functions()
                time.sleep(60)
    
    while True:
        print('Running server functions')
        s.main()
        time.sleep(60)
    

if __name__ == "__main__":
    main()