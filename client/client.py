#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 15:53:25 2020

@author: mac
"""
import sys
import socket
import os

class FTPclient:
    def __init__(self, address, commandChannelPort, dataChannelPort):
        self.address = address
        self.commandChannelPort = int(commandChannelPort)
        self.dataChannelPort= int(dataChannelPort)
    def connectToServer(self):
        try:
            self.commandSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.commandSock.connect((self.address,self.commandChannelPort))
        except KeyboardInterrupt:
            self.commandSock.close()
            sys.exit(0)
        except Exception as e:
            print("connection failed because of",str(e))
            sys.exit(0)
            
    def recvall(self,sock):
        BUFF_SIZE = 4096 
        data =""
        while True:
            part = sock.recv(BUFF_SIZE).decode()
            data += part
            if len(part) < BUFF_SIZE:
                break
        return data
    
    def connectDataSock(self):
        try:
            self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dataSock.connect((self.address, self.dataChannelPort))
        except Exception as e:
            print("data socket can't connect because of",str(e))
    
    def handleCommand(self,command):
        splitCommand = command.split()
        if(command.upper() == "LIST"):
            try:
                self.connectDataSock()
                list = self.recvall(self.dataSock)
                if(list!=""):
                    print(list)         
            except Exception as e:
                print("LIST command error because of",str(e))
            finally:
                self.dataSock.close()
                
        elif(len(splitCommand)>0 and splitCommand[0].upper()=="DL"):
            if(len(splitCommand)>1):
                name = command.split(" ",1)[1]
            try:
                self.connectDataSock()
                content = self.recvall(self.dataSock)
                if(content!=""):
                   file = open(os.path.join(os.getcwd(),name), 'w+')
                   file.write(content)
                   file.close()
            except Exception as e:
                print("DL command error because of",str(e))
            finally:
                self.dataSock.close() 
                
        elif(command.upper() == "QUIT"):
            data = self.recvall(self.commandSock)
            if(data == '221 Successful Quit.'):
                self.commandSock.close()
                print(data)
                sys.exit(0)
            else:
                print(data)
            
        if(command.upper() != "QUIT"):
            data = self.recvall(self.commandSock)
            print(data)
             
    def start(self):
        self.connectToServer()
        while True:
            try:
                command = str(input())
                self.commandSock.sendall(command.encode())
                self.handleCommand(command)
            except KeyboardInterrupt:
                self.commandSock.close()
                sys.exit(0)

            

commandChannelPort = 8000
dataChannelPort = 8001
ftpClient = FTPclient('localhost',commandChannelPort,dataChannelPort)
ftpClient.start()

