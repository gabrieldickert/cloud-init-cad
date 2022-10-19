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
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])

requestSession.mount('http://', HTTPAdapter(max_retries=retries))

# NOTE: needs to gets executed in admin mode otherwise rhino rest api cant be started and crashed (is always given in the Cloud)
# Hostname and serverport for this Service-Server which is based on every VM
hostName = "localhost"
serverPort = 8081
alwaysAvailableInstanceCount = 0
instanceInactivityAmount = 180
# List of all  RhinoRESTServer Instances on this machine
rhinoServerCommand = "RhinoRESTAPIServerCommand"
rhinoServerList = []
roundRobinCounter = 0
# List of all Ports (Port 1024 is reserved for Port Forwading)
portList = [1025, 1026, 1027, 1028, 1029, 1030]
# List of all ports which are left available from the global Portlist
availablePorts = [1025, 1026, 1027, 1028, 1029, 1030]


def getFreePort():

    # getting ip-address of host
    ip = socket.gethostbyname(socket.gethostname())

    # check for all available ports in the defined dynamic port range
    for port in availablePorts:
        try:
            # create a new socket
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            serv.bind((ip, port))  # bind socket with address
            return port
        except:

            print('[OPEN] Port open :', port)  # print open port number

        serv.close()  # close connection


def createRhinoRESTInstance():
    # Server have no token whens we create them since no user is assigned yet to this server
    freePort = getFreePort()
    # Remove Port from available list
    try:
        availablePorts.remove(freePort)
    except:
        print("Could not remove port"+str(freePort)+" from free port list")
    print("Assign REST-Server with port"+str(freePort))
    restServer = RhinoRESTServer(None, None, freePort, None)
    rhinoServerList.append(restServer)
    # Start Rhino
    path = r"C:\Program Files\Rhino 7\System\Rhino.exe"

    command = '\"C:\\Program Files\\Rhino 7\\System\\Rhino.exe\" /nosplash /runscript=\"_-' + \
        rhinoServerCommand+' '+str(freePort)+'\"'
    proc = subprocess.Popen(command, universal_newlines=True, shell=False,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("assigned rhino pid"+str(proc.pid))
    # Get PID from Rhino Instance
    restServer.pid = proc.pid
    # time.sleep(5)
    # os.kill(proc.pid,signal.SIGINT)
    #print("killing over for pid"+str(proc.pid))

    return restServer


class InstanceWatcher(threading.Thread):

    def __init__(self):
        super(InstanceWatcher, self).__init__()
        self.instanceList = rhinoServerList
        pass

    def run(self):
        while True:
            # Checking Every x Seconds if Rhino Instance is still used
            time.sleep(1)
            print("Checking Instances")
            self.checkServerUsage()

    def checkServerUsage(self):
        currentTime = datetime.now()
        inactiveServers = [server for server in self.instanceList if (
            server.lastUsed + timedelta(seconds=instanceInactivityAmount)) < currentTime]
        for item in inactiveServers:
            try:
                os.kill(item.pid, signal.SIGINT)
                rhinoServerList.remove(item)
                print("Killed Rhino Instance with PID:",
                      str(item.pid), " and the Port:", str(item.port))
            except:
                print("Could not kill Rhino Instance with PID:", str(
                    item.pid), " and the Port:", str(item.port))
        
        #If current Rhino Instances is lower then desired spawn new instances
        if len(rhinoServerList) < alwaysAvailableInstanceCount:
            diff = alwaysAvailableInstanceCount - len(rhinoServerList)
            for i in range(0,diff):
                createRhinoRESTInstance()


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
        #Standard Path for Health-Probes
        if self.path=="/":
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
            createRhinoRESTInstance()
        elif self.path == "/registerServer":
            print("REST-Server wants to register here")
            body = json.loads(self.getPOSTBody().decode("utf-8"))
            if body["ready"]:
                print(self)
                # Searching the Instance from the RESTRhino Wehere the port matches the submitted port
                #!Server has to be created before it can be registered!
                # Should find only one Server
                server = [
                    item for item in rhinoServerList if item.port == body["port"]]
                server[0].ready = body["ready"]
                server[0].lastUsed = datetime.now()
                # Setting Hostname
                server[0].host = self.client_address[0]
                print("REST-Server with port" +
                      str(body["port"])+" is now ready?"+str(server[0].ready))

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
                self.wfile.write(bytes("<p>Request: %s</p>" %
                                 self.path, "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(
                    bytes("<p>This is an example web server.</p>", "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))

        elif self.path == "/api/construction/gear/createGear":
            # Extract POST-Body Part from the Request
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)

            # Assuming Token is always provided since the request gets forwared form the main api server
            bearerToken = self.headers.get("authorization")
            global roundRobinCounter
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
            """
            # Finding Server which is related to this token otherwise if no server is found we take one from the available pool
            bearerServer = [
                item for item in rhinoServerList if item.token == bearerToken]

            # No Server assigned to a token was found
            if(len(bearerServer) == 0):
                # if no Server with token was found we check if a server is free(has no assigned token)
                freeServer = [
                    item for item in rhinoServerList if item.token == None]
                if(len(freeServer) == 0):
                    assignedServer = createRhinoRESTInstance()
                    assignedServer.token = bearerToken
                else:
                    assignedServer = freeServer[0]
                    # Set Token for free server to make it in ownerhip of the user
                    assignedServer.token = bearerToken
            else:
                assignedServer = bearerServer[0]
            # Update Timestamp
            assignedServer.lastUsed = datetime.now()
            print("Request from"+bearerToken +
                  "for Server"+str(assignedServer.port))

            if assignedServer.ready:
                # Only REDIRECT When Rhino has been started and Plugin informed this Server that its ready to serve
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
                self.end_headers()"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rhinoInstanceStartNumber", type=int, default=1,
                        help="The number of the available Rhino Instance at startup")
    args = parser.parse_args()
    
    webServer = ThreadedHTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    # setup some rhino instances when booting the server to be instantly ready.
    # The amount depends heavily on the VM capabilities
    for i in range(0, args.rhinoInstanceStartNumber):
        createRhinoRESTInstance()
    #Settings Amount of always available Instances 
    alwaysAvailableInstanceCount = args.rhinoInstanceStartNumber
    # Starting Watcher to see when an Rhino Instance was inactive for a certain period of time e.g 5min in order to manage ressources
    instanceWatcher = InstanceWatcher()
    instanceWatcher.daemon = True
    instanceWatcher.start()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        # kill all rhino instances when closing server
        for server in rhinoServerList:
            os.kill(server.pid, signal.SIGINT)
        pass

    webServer.server_close()
    print("Server stopped.")
