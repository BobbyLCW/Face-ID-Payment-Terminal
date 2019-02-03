'''
Created on 26 Jan 2019

@author: bobbylee
'''
import socket, select
import sys
import os
import shutil
import datetime
import numpy as np
import pathlib
from keras.models import load_model
from keras.preprocessing.image import img_to_array, load_img

class Server:
    ip_address = '127.0.0.1'
    port_no = 100
    server_sock = ''
    connected_client_socket = []
    buffer_size = 0
    imagescounter = 1
    filepath = ''
    parent_path = ''
    image_format = ".jpg"
    filename = ""
    connected = False
    model_path = ''
    model = ""
    def __init__(self, ipaddr, portno, buffer_size = 1024):        
        self.ip_address = ipaddr
        self.port_no = portno
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = buffer_size
        self.parent_path = str(pathlib.Path(__file__).parent)
        self.model_path = self.parent_path + '\model\\BobbyAWAlexnet.h5'
        self.filepath = self.parent_path + '\server\\'
        self.model = load_model(self.model_path)
        self.model.compile(loss='categorical_crossentropy',optimizer='rmsprop',metrics=['accuracy'])
        self.start_server()
        
    def start_server(self):
        '''
        this is for server 
        '''
        try:
            print("Server Started...")
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind((self.ip_address, self.port_no))
            self.server_sock.listen(10)
            self.connected_client_socket.append(self.server_sock)
            self.connected = True
            self.asServer()
        except socket.error as e_msg:
            print(str(e_msg))
            self.connected = False
        
    def asServer(self):
        while(self.connected):
            print("Start listening...")
            read_sockets, write_sockets, error_sockets = select.select(self.connected_client_socket, [], [])
            for sock in read_sockets:
                if sock == self.server_sock:
                    sockfd, client_address = self.server_sock.accept()
                    self.connected_client_socket.append(sockfd)
                    print(str(sockfd) + " " + str(client_address) + " connected!")
                else:
                    try:
                        incoming_len = sock.recv(self.buffer_size)
                        print(incoming_len)
                        if incoming_len:
                            filesize = int(incoming_len) 
                            sock.send('OK'.encode())
                            now = datetime.datetime.now()
                            Fname = str(now.year)+ str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + "_"
                            self.filename = self.filepath + str(Fname) + str(self.imagescounter) + self.image_format
                            backupdir = self.filepath + "backup\\" + str(Fname) + str(self.imagescounter) + self.image_format
                            images = open(self.filename,'wb')          
                            incoming_data = sock.recv(self.buffer_size)
                            totalrecv = len(incoming_data)
                            images.write(incoming_data)
                            while totalrecv < filesize:
                                incoming_data = sock.recv(self.buffer_size)
                                totalrecv += len(incoming_data)
                                images.write(incoming_data)                               
                                if not incoming_data:
                                    self.filename = ""
                                    images.close()
                                    break
                            images.close()
                            #sock.send('received'.encode())
                            who = self.identifyBobbyFace(self.filename)
                            #os.remove(self.filename)
                            shutil.move(self.filename, backupdir)
                            if who[0] * 100 > 98.0:
                                print(str(who[0] * 100) + "% similar to Bobby Lee")
                                sock.send('yes,BobbyLee,112233,123456'.encode())
                            else:
                                print("Not Bobby Lee but is similar to other class")
                                sock.send('no,null,null,null'.encode())
                            self.imagescounter += 1 
                            sock.shutdown(socket.SHUT_RDWR)             
                    except socket.error as e_msg:
                        print(str(e_msg))                       
                        sock.close()
                        self.connected_client_socket.remove(sock)
                        continue
    
    def identifyBobbyFace(self, facedir):
        detection = []
        img_width,img_height = 224, 224
        img = load_img(facedir, target_size=(img_width,img_height))#, color_mode = 'grayscale')
        img = np.array(img).astype('float32')/255 #normalization to 0 and 1, because preprocessing do this
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)
        preds = self.model.predict_classes(x)
        probs = self.model.predict_proba(x)
        print(preds, probs)
        for i in probs[0]:
            detection.append(i)
        detection.append(preds)
        return detection
        
    def __del__(self):
        self.server_sock.close()   
class client:
    ip_address = '127.0.0.1'
    port_no = 100
    client_sock = ''
    buffer_size = 0
    imagescounter = 1
    image_format = ".jpg"
    filename = ""
    connected = False
    memberID = ""
    def __init__(self, ipaddr, portno, images_path = "", buffer_size = 1024):        
        self.ip_address = ipaddr
        self.port_no = portno
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = buffer_size
        self.start_connect()
        self.asClient(images_path)
        
    def start_connect(self):       
        '''
        this is for client
        '''
        try:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest_address = (self.ip_address, self.port_no)
            self.client_sock.connect(dest_address)
            self.connected = True
        except socket.error as e_msg:
            print(str(e_msg))
            self.connected = False
            
    def asClient(self, images_path):
        try:
            while(self.connected):
                self.client_sock.send((str(os.path.getsize(images_path))).encode())
                usrResponse = self.client_sock.recv(self.buffer_size)
                if usrResponse.decode() == 'OK':
                    with open(images_path, 'rb') as f:
                        print("Sending Image.....")
                        bytestosend = f.read(self.buffer_size)
                        while bytestosend:
                            self.client_sock.send(bytestosend)
                            bytestosend = f.read(self.buffer_size)
                        f.close()
                        print("Image Sent!")
                    reply = self.client_sock.recv(4096)
                    incoming_reply = str(reply.decode())
                    a,b,c,d = incoming_reply.split(",")
                    if a == 'yes':
                        print("server received Image")
                        print(incoming_reply)
                        print("client socket close...")
                        self.memberID = incoming_reply
                        break
                    else:
                        print("server no response...")
                        print("client socket close...")
                        self.memberID = incoming_reply
                        break 
        finally:
            self.client_sock.close()
            
    def getmemberID(self):
        return self.memberID
    
    def __del__(self):
        self.client_sock.close()