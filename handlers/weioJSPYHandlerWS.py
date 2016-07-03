###
#
# WEIO Web Of Things Platform
# Copyright (C) 2013 Nodesign.net, Uros PETREVSKI, Drasko DRASKOVIC
# All rights reserved
#
#               ##      ## ######## ####  #######
#               ##  ##  ## ##        ##  ##     ##
#               ##  ##  ## ##        ##  ##     ##
#               ##  ##  ## ######    ##  ##     ##
#               ##  ##  ## ##        ##  ##     ##
#               ##  ##  ## ##        ##  ##     ##
#                ###  ###  ######## ####  #######
#
#                    Web Of Things Platform
#
# This file is part of WEIO and is published under BSD license.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by the WeIO project.
# 4. Neither the name of the WeIO nor the
# names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY WEIO PROJECT AUTHORS AND CONTRIBUTORS ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL WEIO PROJECT AUTHORS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors :
# Uros PETREVSKI <uros@nodesign.net>
# Drasko DRASKOVIC <drasko.draskovic@gmail.com>
#
###


from weioLib.weioIO import *
import json
import tornado.websocket

from weioLib.weioParser import weioSpells
from weioLib.weioParser import weioUserSpells
from weioLib import weioRunnerGlobals

import uuid
import os

class WeioWSHandler(tornado.websocket.WebSocketHandler):
    
    def check_origin(self, origin):
        return True

    def open(self):
        # Add the connection to the connections dictionary
        connUuid = uuid.uuid4()
        weioRunnerGlobals.weioConnections[connUuid] = self
        weioRunnerGlobals.weioConnUuids.append(connUuid)
        print self

        # collect client ip address and user machine info
        # print self.request to see all available info on user connection
        #self.userAgent = None
        #self.ip = request.ip

        #print "*SYSOUT* Client with IP address: " + self.ip + " connected to server"

        self.connection_closed = False

    def emit(self, instruction, rq):
        data = {}
        data['serverPush'] = instruction
        data['data'] = rq
        self.wite_message(json.dumps(data))

    def on_message(self, data):
        if (weioRunnerGlobals.running.value == True):
            """Parsing JSON data that is comming from browser into python object"""
            self.serve(json.loads(data))
        else:
            weioRunnerGlobals.weioConnections.clear()

    def serve(self, data) :
        print data
        for connUuid, conn in weioRunnerGlobals.weioConnections.iteritems():
            if (conn == self):
                # Create userAgentMessage and send it to the launcher process
                msg = weioRunnerGlobals.userAgentMessage()

                msg.connUuid = connUuid

                if (type(data) is dict):
                    #print "keys : %s" %  data.keys()
                    for key in data:
                        if key == "request":
                            msg.req = data["request"]
                        elif key == "data":
                            msg.data = data["data"]
                        elif key == "callback":
                            msg.callbackJS = data["callback"]

                # Send message to launcher process
                weioRunnerGlobals.QOUT.put(msg)


    def on_close(self):
        self.connection_closed = True
        #print "*SYSOUT* Client with IP address: " + self.ip + " disconnected from server"
        # Remove client from the clients list and broadcast leave message
        #self.connections.remove(self)
        #for connUuid, conn in weioRunnerGlobals.weioConnections.iteritems():
        #    if (conn == self):
        #        weioRunnerGlobals.weioConnections.pop(connUuid)
        #        weioRunnerGlobals.weioConnUuids.remove(connUuid)


###
# This is used for remote apps - Tornado User opens __client__ socket
# and puths everything that comes from this socket to WeioHandlerRemote()
###
class WeioHandlerRemote():
    def __init__(self):
        self.remoteConn = None
        self.connUuid = None

    def setRemoteConn(self, rc):
        self.remoteConn = rc
        # Add the connection to the connections dictionary
        self.connUuid = uuid.uuid4()
        weioRunnerGlobals.weioConnections[self.connUuid] = self.remoteConn


    def on_message(self, data):
        if (self.remoteConn != None):
            """Parsing JSON data that is comming from browser into python object"""
            self.serve(json.loads(data))

    def serve(self, data) :
        # Create userAgentMessage and send it to the launcher process
        msg = weioRunnerGlobals.userAgentMessage()
        #print "DATA: ", data

        if (type(data) is dict):
            #print "keys : %s" %  data.keys()
            for key in data:
                if key == "request":
                    msg.req = data["request"]
                elif key == "data":
                    msg.data = data["data"]
                elif key == "callback":
                    msg.callbackJS = data["callback"]

            # Send message to launcher process
            weioRunnerGlobals.QOUT.put(msg)

    def on_close(self):
        self.remoteConn = None

        # Remove client from the clients list and broadcast leave message
        weioRunnerGlobals.weioConnections.pop(self.connUuid)
        self.connUuid = None
