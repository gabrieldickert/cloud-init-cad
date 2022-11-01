# Python 3 server example
import argparse
from asyncio import constants
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import copy
import subprocess
import socket
import json
import time
import os
import signal
from requests.adapters import HTTPAdapter, Retry
from datetime import date, datetime, timedelta
import threading
import argparse
import socketserver
import psutil
# Since Starting the Rhino-Server can take some time an retry-mechanism is implemented
requestSession = requests.Session()
retries = Retry(total=10,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])

requestSession.mount('http://', HTTPAdapter(max_retries=retries))

# NOTE: needs to gets executed in admin mode otherwise rhino rest api cant be started and crashed (is always given in the Cloud)
# Hostname and serverport for this Service-Server which is based on every VM
hostName = "localhost"
serverPort = 8081
alwaysAvailableInstanceCount = 0
instanceInactivityAmount = 300
# List of all  RhinoRESTServer Instances on this machine
rhinoServerCommand = "RhinoRESTAPIServerCommand"
rhinoInstanceManager = None
rhinoServerList = []
roundRobinCounter = 0
# List of all Ports (Port 1024 is reserved for Port Forwading)
portList = [1025, 1026, 1027, 1028, 1029, 1030]
# List of all ports which are left available from the global Portlist
availablePorts = [1025, 1026, 1027, 1028, 1029, 1030]

#Retrieves a Free Port from the List of available Ports
def getFreePort():
    pass    
"""
    # getting ip-address of host
    ip = socket.gethostbyname(socket.gethostname())

    # check for all available ports in the defined dynamic port range
    for port in availablePorts:
        try:
            # create a new socket
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            serv.bind((ip, port))  # bind socket with address

            print("PORT IS FREE",port)
            return port
        except:

            print('[OPEN] Port open :', port)  # print open port number

        serv.close()  # close connection
    
    return None"""
#Creates a new Rhino Instance
"""def createRhinoRESTInstance():
    # Server have no token whens we create them since no user is assigned yet to this server
    freePort = getFreePort()
    # Remove Port from available list
    try:
        availablePorts.remove(freePort)
    except:
        print("Could not remove port"+str(freePort)+" from free port list")
        return None
    print("Assign REST-Server with port"+str(freePort))
    restServer = RhinoRESTServer(None, None, freePort, None)
    rhinoServerList.append(restServer)
    # Start Rhino
    command = '\"C:\\Program Files\\Rhino 7\\System\\Rhino.exe\" /nosplash /runscript=\"_-' + \
        rhinoServerCommand+' '+str(freePort)+'\"'
    proc = subprocess.Popen(command, universal_newlines=True, shell=False,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("assigned rhino pid"+str(proc.pid))
    # Get PID from Rhino Instance
    restServer.pid = proc.pid

    return restServer"""


class InstanceWatcher(threading.Thread):

    def __init__(self):
        super(InstanceWatcher, self).__init__()
        self.instanceList = rhinoServerList
        pass

    def run(self):
        while True:
            # Checking Every x Seconds if Rhino Instance is still used
            time.sleep(1)
            print("Checking Rhino Instances...")
            self.checkServerUsage()

    def checkServerUsage(self):
        pass
        """currentTime = datetime.now()
        inactiveServers = [server for server in self.instanceList if (
            server.lastUsed + timedelta(seconds=instanceInactivityAmount)) < currentTime]
        global availablePorts
        for item in inactiveServers:
            try:
                parent = psutil.Process(item.pid)
                for child in parent.children():
                    child.kill()
                parent.kill()
                #Remove Instance from List
                rhinoServerList.remove(item)
                #Add Port back to availbale Port List
                availablePorts.append(item.port)
                #Could be sorted to start again at first Port but we iterate through
                #availablePorts = sorted(availablePorts)
                print(availablePorts)
                print("Killed Rhino Instance with PID:",
                      str(item.pid), " and the Port:", str(item.port))
            except:
                print("Could not kill Rhino Instance with PID:", str(
                    item.pid), " and the Port:", str(item.port))"""

        #If current Rhino Instances is lower then desired spawn new instances
        if len(rhinoServerList) < alwaysAvailableInstanceCount:
            diff = alwaysAvailableInstanceCount - len(rhinoServerList)
            for i in range(0,diff):
                pass
                #createRhinoRESTInstance()


class RhinoInstanceManager:


    def __init__(self,pid):
        self.pid = pid


class RhinoRESTServer:

    def __init__(self, token, host, port, pid):
        self.token = token
        self.host = host
        self.port = port
        self.pid = pid
        self.ready = False
        # Creating Datetime
        self.lastUsed = datetime.now()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


class MyServer(BaseHTTPRequestHandler):
    #protocol_version = 'HTTP/1.1'
    def parse_headers(self, headers):
        req_header = {}
        for line in headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return req_header

    def getPOSTBody(self):
        content_len = int(self.headers.get('Content-Length'))
        return self.rfile.read(content_len)

    def do_GET(self):
        if self.path=="/33":
            #proc = subprocess.Popen("WindowsFormsApp1.exe", universal_newlines=True, shell=False,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"status":"files created"}), "utf-8"))
        #Standard Path for Health-Probes for Load Balancer
        if self.path=="/":
            #proc = subprocess.Popen("python inside.py", universal_newlines=True, shell=False,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"status":"ok"}), "utf-8"))
        # Returns the Amount of current active Sessions on this Machine
        if self.path == "/api/construction/sessions/all":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(
                [rhinoInstance.__dict__ for rhinoInstance in rhinoServerList], indent=4, sort_keys=True, default=str), "utf-8"))
        #Returns the Status of the Server
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps({"activeSessions":len(rhinoServerList),"sessionLimit":4,"isActive": True,"usageCPU":psutil.cpu_percent()}), "utf-8"))

    def do_POST(self):
        #Adds a construction session from the outside, needed?
        if self.path =="/api/construction/sessions/add":
            pass
            #createRhinoRESTInstance()
        #Endpoint for register an new Worker and add it to the available Pool of Worker
        elif self.path == "/registerServer":
            print("REST-Server wants to register here")
            body = json.loads(self.getPOSTBody().decode("utf-8"))
            if body["ready"]:
                # Searching the Instance from the RESTRhino Wehere the port matches the submitted port
                #!Server has to be created before it can be registered!
                # Should find only one Server
                instance = RhinoRESTServer(None, None, body["port"], None)
                instance.ready = body["ready"]
                instance.lastUsed = datetime.now()
                instance.host = self.client_address[0]
                rhinoServerList.append(instance)
                print("Added Rhino Geometry Worker Instance at port "+str(body["port"])+"to the Pool")
                """ server = [
                    item for item in rhinoServerList if item.port == body["port"]]

                if(len(server) == 1):
                    server[0].ready = body["ready"]
                    server[0].lastUsed = datetime.now()
                    # Setting Hostname
                    server[0].host = self.client_address[0]
                    print("REST-Server with port" +str(body["port"])+" is now ready?"+str(server[0].ready))"""

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    bytes("<html><head><title>Success</title></head>", "utf-8"))

        #Endpoint for Creating a Gear
        # "/api/construction/gear/createGear
        elif self.path == "/api/createGear":
            #Use global Round Robin Counter
            global roundRobinCounter
            # Extract POST-Body Part from the Request
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)

            # Assuming Token is always provided since the request gets forwared form the main api server
            bearerToken = self.headers.get("authorization")

            assignedServer = rhinoServerList[roundRobinCounter%alwaysAvailableInstanceCount]
            #Increase Value for Round Robin
            roundRobinCounter += 1
            #Resetting Counter to 0 
            if  roundRobinCounter == alwaysAvailableInstanceCount:
                roundRobinCounter = 0
            # Only REDIRECT When Rhino has been started and Plugin informed this Server that its ready to serve
            if assignedServer.ready:
                    #Update Server usage
                    assignedServer.lastUsed = datetime.now()
                    res = requestSession.post("http://"+str(assignedServer.host)+":"+str(assignedServer.port)+"/createGear",
                                            headers=self.headers, data=post_body, verify=False)
                    
                    self.send_response(res.status_code)
                    # self.send_header("Transfer-Encoding","chunked") is not supported in this Python-Server Version with HTTP 1 but HTTP 1/1 is not working
                    for k, v in res.headers.items():
                        if "Transfer-Encoding" not in k:
                            self.send_header(str(k), str(v))
                    self.end_headers()
                    self.wfile.write(bytes(res.content))
            else:
                self.send_response(500)
                self.end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rhinoInstanceStartNumber", type=int, default=2,
                        help="The number of the available Rhino Instance at startup")
    args = parser.parse_args()
    
    webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    """setup some rhino instances when booting the server to be instantly ready.
    The amount depends heavily on the VM capabilities"""
    for i in range(0, args.rhinoInstanceStartNumber):
        pass
        #createRhinoRESTInstance()
    
    #Opens the "Main" Rhino Instance Program
    proc = subprocess.Popen("AzureConform.exe", shell=True)
    rhinoInstanceManager = RhinoInstanceManager(proc.pid)
    print("Started Rhino Instance Manager at PID"+str(proc.pid))
    #Settings Amount of always available Instances 
    alwaysAvailableInstanceCount = args.rhinoInstanceStartNumber
    # Starting Watcher to see when an Rhino Instance was inactive for a certain period of time e.g 5min in order to manage ressources
    instanceWatcher = InstanceWatcher()
    instanceWatcher.daemon = True
    instanceWatcher.start()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        os.kill(rhinoInstanceManager.pid,signal.SIGINT)
        # kill all rhino instances when closing server
        """for server in rhinoServerList:
            os.kill(server.pid, signal.SIGINT)
        pass"""

    webServer.server_close()
    print("Server stopped.")
