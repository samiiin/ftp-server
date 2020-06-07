#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 15:53:17 2020

@author: mac
"""
import json
import socket
import threading
import os
import sys
import shutil
import time
import logging




class FTPThreadServer(threading.Thread):
    def __init__(self, clientCommandSock,dataSock):
        self.clientCommandSock = clientCommandSock
        self.dataSock = dataSock
        self.login = False
        self.username = ""
        self.initialDirectory = os.getcwd()
        self.isLimited = False
        threading.Thread.__init__(self)
        self.cwd = os.getcwd()
        
        
    def isAdmin(self,username):
        for user in data["authorization"]["admins"]:
            if(user == username):
                return True
            return False
        
    def isAdminFile(self,filePath):
        for e in data["authorization"]["files"]:
            path = os.path.abspath(self.initialDirectory+ "/"+ e )
            if(filePath == path):
                return True
        return False
    
    def isUnavailableFile(self,username,filePath):
        if(self.isAdmin(username)):
            return False
        elif((not self.isAdmin(username)) and  (not self.isAdminFile(filePath))):
            return False
        else:
            return True
        
        
    def sendEmail(self,emailAddr):
        msg = "\r\n Hi! your byte credit is getting low!"
        endmsg = "\r\n.\r\n"
        mailserver = ("mail.ut.ac.ir", 25)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(mailserver)
        recv = clientSocket.recv(1024)
        recv = recv.decode()
        print("Message after connection request:" + recv)
        if recv[:3] != '220':
            print('220 reply not received from server.')


        heloCommand = 'HELO Haniyeh\r\n'
        clientSocket.send(heloCommand.encode())
        recv1 = clientSocket.recv(1024)
        recv1 = recv1.decode()
        print("Message after EHLO command:" + recv1)
        if recv1[:3] != '250':
            print('250 reply not received from server.')


        mailFrom = "MAIL FROM: <haniyeh.nasseri99@ut.ac.ir>\r\n"
        clientSocket.send(mailFrom.encode())
        recv2 = clientSocket.recv(1024)
        recv2 = recv2.decode()
        print("After MAIL FROM command: " + recv2)


        authLogin = "AUTH LOGIN\r\n"
        clientSocket.send(authLogin.encode())
        recv = clientSocket.recv(1024)
        print(recv.decode())
        username = "aGFuaXllaC5uYXNzZXJpOTk=" + "\r\n"
        password = "SGFuaXllaDc0NjM5MDM3NDYzOTAz" + "\r\n"
        clientSocket.send((username).encode())
        print(username.encode())
        recv_auth = clientSocket.recv(1024)
        print(recv_auth.decode())
        clientSocket.send((password).encode())
        print(password.encode())
        recv_auth = clientSocket.recv(1024)
        print(recv_auth.decode())


        rcptTo = "RCPT TO: <" + emailAddr +">\r\n"
        clientSocket.send(rcptTo.encode())
        recv3 = clientSocket.recv(1024)
        recv3 = recv3.decode()
        print("After RCPT TO command: " + recv3)

        data = "DATA\r\n"
        clientSocket.send(data.encode())
        recv4 = clientSocket.recv(1024)
        recv4 = recv4.decode()
        print("After DATA command: "+recv4)
        clientSocket.send(msg.encode())
        clientSocket.send(endmsg.encode())
        recv_msg = clientSocket.recv(1024)
        print("Response after sending message body:" + recv_msg.decode())
        clientSocket.close()
        
    def createClientDataSock(self):
        return self.dataSock.accept()
    
    def recvall(self,sock):
        BUFF_SIZE = 4096 
        data =""
        while True:
            part = sock.recv(BUFF_SIZE).decode()
            data += part
            if len(part) < BUFF_SIZE:
                break
        return data
    
    
    def handleCommand(self,command):
        splitCommand = command.split()
        commandType = splitCommand[0].upper()
        if((self.login == False) and (commandType != "USER") and (commandType != "PASS")):
            self.clientCommandSock.send(('332 Need account for login.').encode())
            self.username = ""
        elif(commandType == "USER"):
            self.handleUSERcommand(command)
        elif(commandType == "PASS"):
            self.handlePASScommand(command)
        elif(commandType == "MKD"):
            self.handleMKDcommand(command)
        elif(commandType == "LIST"):
            self.handleLISTcommand(command)
        elif(commandType == "DL"):
            self.handleDLcommand(command)
        elif(commandType == "HELP"):
            self.handleHELPcommand(command)
        elif(commandType == "QUIT"):
            self.handleQUITcommand(command)
        elif(commandType == "PWD"):
            self.handlePWDcommand(command)
        elif(commandType == "RMD"):
            self.handleRMDcommand(command)
        elif(commandType == "CWD"):
            self.handleCWDcommand(command)
        else:
            message = "500 Error."
            self.clientCommandSock.sendall(message.encode())
            
    def handleMKDcommand(self,command):
        splitCommand = command.split()
        if((len(splitCommand)<2) or (len(splitCommand)==2 and splitCommand[1]=="-i")):
            message = "501 Syntax error in parameters or arguments." 
        elif(splitCommand[1] == "-i"):
            try:
                name = command.split(" ",2)[2]
                path = os.path.join(self.cwd,name)
                if os.path.isfile(path):
                    message = "500 Error."
                else:
                    file = open(path, 'w+')
                    message ="257 <"+ name+ "> created."
                    self.log(self.username + " created " + name)
                    file.close()
            except Exception as e:
                    print(str(e))
                    message = "500 Error." 
        else:
            name = command.split(" ",1)[1]
            path = os.path.join(self.cwd,name)
            try:
                os.mkdir(path)
                message ="257 <"+ path + "> created."
                self.log(self.username + " created " + name)
            except Exception as e:
                message = "500 Error."   
        self.clientCommandSock.sendall(message.encode())

        
    def handleQUITcommand(self,command):
        if(command.upper() != "QUIT"):
            message = "501 Syntax error in parameters or arguments." 
        else:
            try:
                self.log(self.username + " Logged out.")
                self.clientCommandSock.sendall('221 Successful Quit.'.encode())
                self.clientCommandSock.close() 
                sys.exit(0)
            except Exception as e:
                print("QUIT error because of",str(e))
                self.clientCommandSock.sendall('500 Error.'.encode())
            return
        self.clientCommandSock.sendall(message.encode())
        
        
    def handleRMDcommand(self,command):
        splitCommand = command.split()
        if((len(splitCommand)<2) or (len(splitCommand)==2 and splitCommand[1]=="-f")):
            message = "501 Syntax error in parameters or arguments." 
        elif(splitCommand[1] == "-f"):
            dname = command.split(" ",2)[2]
            dpath = os.path.join(self.cwd,dname)
            if(os.path.isdir(dpath)):
                try:
                    shutil.rmtree(dpath)
                    message = '250 <' +  dpath + '> deleted.'
                    self.log(self.username + " removed " + dname)
                except Exception as e:
                    message = "500 Error."     
            else:
                message = "500 Error."
        else:
            fname = command.split(" ",1)[1]
            fpath = os.path.join(self.cwd,fname)
            if(os.path.isfile(fpath)):
                if(self.isUnavailableFile(self.username,fpath)):
                    message = "550 File unavailable."
                else:
                    try:
                        os.remove(fpath)
                        message = '250 <' + fname + '> deleted.'
                        self.log(self.username + " removed " + fname)
                    except Exception as e:
                        message = "500 Error."     
            else:
                message = "500 Error."
        self.clientCommandSock.sendall(message.encode())


    
    def handleHELPcommand(self,command):
        splitCommand = command.split()
        if(len(splitCommand) != 1):
            self.clientCommandSock.sendall(('501 Syntax error in parameters or arguments.').encode())
            return
        path = os.path.join(self.initialDirectory,"explanations.txt")
        file = open(path, "r")
        self.clientCommandSock.sendall((file.read()).encode())

        
        
    def handleCWDcommand(self,command):
        splitCommand = command.split()
        if((len(splitCommand) > 2) or (len(splitCommand) < 1)):
            self.clientCommandSock.sendall(('501 Syntax error in parameters or arguments.').encode())
            return
        if(len(splitCommand) == 1):
            path = self.initialDirectory
        else:
            path = os.path.abspath(self.cwd +"/"+ splitCommand[1])
            
        if(os.path.isdir(path)):
            self.cwd = path
            self.clientCommandSock.sendall(('250 ' + 'Successful Change.').encode())
            return 
        self.clientCommandSock.sendall(("500 Error.").encode())
        return


    
    def handlePWDcommand(self,command):
        splitCommand = command.split()
        if(len(splitCommand) != 1):
            self.clientCommandSock.sendall(('501 Syntax error in parameters or arguments.').encode())
            return 
        self.clientCommandSock.sendall(('257 ' + self.cwd).encode())
    
        
    def handleLISTcommand(self,command):
        clientDataSock , address = self.createClientDataSock()
        splitCommand = command.split()
        if(len(splitCommand)!=1):
            message = "501 Syntax error in parameters or arguments." 
        else:
            try:
                list = os.listdir(self.cwd)
                listdir =""
                for element in list:
                    listdir +=element+'\n'
                listdir = listdir[:-1]
                clientDataSock.sendall(listdir.encode())
                self.clientCommandSock.sendall("226 List transfer done.".encode())
            except Exception as e:
                print("Error on transform because of",str(e))
                self.clientCommandSock.sendall("500 Error.".encode())
            finally:
                clientDataSock.close()
            return
        self.clientCommandSock.sendall(message.encode())
        clientDataSock.close()


    def handleEmail(self):
        if(self.information["alert"] == True):
            self.sendEmail(self.information["email"])
        
    def log(self,message):
        if(logFilePath == ''):
            return
        logging.basicConfig(filename=logFilePath,format='%(asctime)s-%(name)s-%(message)s',filemode='a')
        logger = logging.getLogger(self.username)
        logger.setLevel(logging.DEBUG)
        logger.info(message)
         

    def handleDLcommand(self,command):
        clientDataSock , address = self.createClientDataSock()
        splitCommand = command.split()
        if(len(splitCommand)<2):
            message = "501 Syntax error in parameters or arguments." 

        else:
            try:
                name = command.split(" ",1)[1]
                fpath = os.path.join(self.cwd,name)
                if os.path.isfile(fpath):
                    if(self.isUnavailableFile(self.username,fpath)):
                        message = "550 File unavailable."
                        self.clientCommandSock.sendall(message.encode())
                    else:
                        fileSize = os.stat(fpath).st_size
                        if( (self.isLimited == True) and (int(self.information["size"]) < fileSize) ):
                            message = "425 Can't open data connection."
                            self.clientCommandSock.sendall(message.encode())
                        else:
                            if(self.isLimited):
                                self.information["size"] = int(self.information["size"]) - fileSize
                                print(self.information["size"])
                                if(self.information["size"] < treshold):
                                    self.handleEmail()

                            file = open(fpath, "r")
                            clientDataSock.sendall(file.read().encode())
                            message = "226 Successful Download."
                            self.log(self.username + " downloaded " + name)
                            self.clientCommandSock.sendall(message.encode())
                            file.close()

                else:
                    message = "500 Error."
                    self.clientCommandSock.sendall(message.encode())
            except Exception as e:
                print("Error on transform file because of",str(e))
                self.clientCommandSock.sendall("500 Error.".encode())
            finally:
                clientDataSock.close()
            return

        self.clientCommandSock.sendall(message.encode())
        clientDataSock.close()


    def handleUSERcommand(self,command):
        splitCommand = command.split()
        if(len(splitCommand)!=2):
            message = "501 Syntax error in parameters or arguments."
            self.clientCommandSock.sendall(message.encode())
            return
        username = splitCommand[1]
        if(self.login):
            message = "500 Error."
            self.clientCommandSock.sendall(message.encode())
            return
        for user in data["users"]:
            if(username == user["user"]):
                message = "331 User name okay, need password"
                self.clientCommandSock.sendall(message.encode())
                self.username = username
                return
        message = "430 Invalid username or password."
        self.clientCommandSock.sendall(message.encode())

    
    def handlePASScommand(self,command):
        splitCommand = command.split()
        if(len(splitCommand)!=2):
            message = "501 Syntax error in parameters or arguments."
            self.clientCommandSock.sendall(message.encode())
            if(not self.login):
                self.username= ""
            return
        if(self.login):
            message = "500 Error."
            self.clientCommandSock.sendall(message.encode())
            return
        password = splitCommand[1]
        if(self.username == ""):
            message = "503 Bad sequence of commands."
            self.clientCommandSock.sendall(message.encode())
            return
        for user in data["users"]:
            if(self.username == user["user"] and password == user["password"]):
                self.login = True

                self.log(self.username + "Logged in")

                for user in limitedUsers:
                    if(user["user"] == self.username):
                        self.information = user
                        self.isLimited = True


                message = "230 User logged in, proceed."
                self.clientCommandSock.sendall(message.encode())
                return
        message = "430 Invalid username or password."
        self.username = ""
        self.clientCommandSock.sendall(message.encode())
        
    
    def run(self):
        print("client connected")
        while True:
            try:
                command = self.recvall(self.clientCommandSock)
                if command:
                    self.handleCommand(command)
            except Exception as e:
                print ('Failed to do command because', str(e))
                self.clientCommandSock.close()
                break
            
class FTPserver:
    def __init__(self,commandChannelPort,dataChannelPort):
        self.commandChannelPort = int(commandChannelPort)
        self.dataChannelPort = int(dataChannelPort)

        
    def createCommandChannel(self):
        try: 
            self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.commandSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.commandSock.bind(('localhost',self.commandChannelPort))
            self.commandSock.listen(10)
            print('command channel create successfully')
        except Exception as e:
            print ('Failed to create command channel because', str(e))
            self.commandSock.close()
            
    def createDataSock(self):
        try: 
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dataSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dataSock.bind(('localhost',self.dataChannelPort))
            self.dataSock.listen(10)
            print('data channel create successfully')
        except Exception as e:
            print ('Failed to create data channel because', str(e))
            self.dataSock.close()


    def start(self):
        self.createCommandChannel()
        self.createDataSock()
        try:
            while True:
                clientCommandSock,address = self.commandSock.accept()
                thread = FTPThreadServer(clientCommandSock,self.dataSock)
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print ('Closing socket connection')
            self.commandSock.close()
            self.dataSock.close()
            sys.exit(0)
        

def get_data():
    with open('config.json') as file:
        data = json.load(file)
    return data

def getLimitedUsers(data):

    limitedUsers = []
    if(data["accounting"]["enable"] == True):
        limitedUsers = data["accounting"]["users"]

    return limitedUsers



data = get_data();
limitedUsers = getLimitedUsers(data)
treshold = data["accounting"]["threshold"]
commandChannelPort = data["commandChannelPort"]
dataChannelPort = data["dataChannelPort"]
logFilePath = ''
if(data["logging"]["enable"] == True):
    logFilePath = os.path.abspath(os.getcwd()+ "/"+ data["logging"]["path"])

server = FTPserver(commandChannelPort,dataChannelPort)
server.start()
