'''
Created on 16 Dec 2018

@author: bobbylee
'''
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import sys
import cv2
import pathlib
import os
from TCPconnection import client

class MainGUI():
    status = "Idle"
    MemberID = ""
    macth_pw = ''
    my_master = ''
    amounttext  = ""
    inputbox = ""
    parent_path = ''
    def __init__(self, master):
        master.state('zoomed')
        self.my_master = master
        self.createLabel(master)
        self.createBtn(master)
        self.createinputbox(master)
        self.parent_path = str(pathlib.Path(__file__).parent)
        self.internalTimer1()
        self.internalTimer2()
    
    def createLabel(self, master):
        self.Mainlabel = Label(master, text="Face ID Payment Terminal", fg='red', bg='white')
        self.Mainlabel.config(font='Courier 70 bold')
        self.Mainlabel.pack(side=TOP, expand=True, fill=BOTH)
        self.Mainlabel.place(relx=0.5, rely=0.25, anchor='center')
        self.amountlabel = Label(master, text="Total amount :", bg='white')
        self.amountlabel.config(font='Helvetica 30 bold')
        self.amountlabel.pack(side=BOTTOM, expand=True, fill=X)
        self.amountlabel.place(relx=0.3, rely=0.5, anchor='center')
        self.statuslabel = Label(master, text="Transaction status : Idle", bg='white')
        self.statuslabel.config(font='Helvetica 30 bold')
        self.statuslabel.pack(side=BOTTOM, expand=True, fill=X)
        self.statuslabel.place(relx=0.3, rely=0.6, anchor='center')
    
    def createBtn(self,master):
        self.Btn_payment = Button(master, text="Make Payment", command = self.activateFD, bg='lightblue') #, command=)
        self.Btn_payment.config(font=("Courier", 18, 'bold'))
        self.Btn_payment.place(relx=0.5, rely=0.8, anchor='center', height=50, width=200)
        
    def createinputbox(self,master):
        self.inputbox = Entry(master)
        self.inputbox.place(relx=0.5, rely=0.7, anchor='center')
        self.inputbox.config(bd = 5, width = 30, font=("Courier", 30))
        
    def internalTimer1(self):
        self.amounttext = self.inputbox.get()     
        self.amountlabel.configure(text="Total amount :"+ str(self.amounttext))
        self.amountlabel.after(100, self.internalTimer1)
        
    def internalTimer2(self):
        self.statuslabel.configure(text = "Transaction status : " + str(self.status))
        self.statuslabel.after(100, self.internalTimer2)
    
    def HaarFD(self):
        facepath = self.parent_path + '\model\\Face_detector_Haar.xml'
        eyepath = self.parent_path + '\model\\Eye_detector_Haar.xml'
        LoadedFaceCascade = cv2.CascadeClassifier(facepath)
        LoadedEyeCascade = cv2.CascadeClassifier(eyepath)
        capvideo = cv2.VideoCapture(0)
        crop_image = ''
        while True:
            ret, myimage = capvideo.read()
            ret2, raw_image = capvideo.read()
            grayimg = cv2.cvtColor(myimage, cv2.COLOR_BGR2GRAY)
            findface = LoadedFaceCascade.detectMultiScale(grayimg, 1.3, 5)
            print(findface)
            for (xscale, yscale, width, height) in findface:
                cv2.rectangle(myimage, (xscale,yscale), (width+xscale, height+yscale), (0,0,255), 3)
                grayinsidefaces = grayimg[yscale:yscale+height, xscale:xscale+width]
                colorinsidefaces = myimage[yscale:yscale+height, xscale:xscale+width]
                print(len(findface))
                findeye = LoadedEyeCascade.detectMultiScale(grayinsidefaces)
                for (eyex, eyey, eyew, eyeh) in findeye:
                    cv2.rectangle(colorinsidefaces, (eyex, eyey), (eyex+eyew, eyey+eyeh), (255,0,0), 3)          
                    cv2.imshow('FaceEyeDetector', myimage)
            k = cv2.waitKey(30) & 0xff
            if k & 0xFF == ord('c'): # hit c for save images 32 for space
                if len(findface) > 0:
                    crop_image =  self.annotate_image_crop(raw_image,findface)
                    break 
                else:
                    print("No Face Found!")
            if k == 27:
                break       
        capvideo.release()
        cv2.destroyAllWindows()
        return crop_image
    
    def annotate_image_crop(self,frame, bboxes):
        ret = frame[:]
        crop = frame[:].copy()
        img_h, img_w, _ = frame.shape
        for xscale, yscale, width, height in bboxes:
            crop_img = crop[yscale-20:yscale+height+20, xscale-20:xscale+width+20]
        return crop_img
    
    def activateFD(self):
        if self.amounttext == "" or self.amounttext == '':
            messagebox.showerror("Payment Error!", "Payment Amount cannot be empty!")
            return  
        cropped_face = self.HaarFD()
        print(self.parent_path)
        temp = self.parent_path + '\local\\temp.jpg'
        cv2.imwrite(temp, cropped_face)
        Myclient = client('127.0.0.1', 5000, images_path=temp)
        self.MemberID = Myclient.getmemberID()
        os.remove(temp)
        self.identifier(self.MemberID)
            
    def identifier(self, memberID):
        a,b,c,d = memberID.split(",")
        count = 1     
        while True:
            if a == 'yes':
                self.macth_pw = str(d) 
                input = simpledialog.askstring("Please input your password", prompt="Hi Welcome "+ str(b) + "! Your membership ID : " + str(c) + "\nPlease Enter Your Password", show='*',parent = self.my_master)
                if count > 3:
                    messagebox.showinfo("Payment status", "Payment failure!")
                    self.status = "Idle"
                    break
                if input == '' or input == "":
                    messagebox.showinfo("Payment status", "password cannot be empty!")
                    self.status = "Retry attempt : " + str(count)
                    count += 1
                elif input == self.macth_pw:
                    messagebox.showinfo("Payment status", "Transaction approved! Your payment is Total: " + str(self.amounttext))
                    self.status = "Idle"
                    break                  
                else:
                    messagebox.showinfo("Payment status", "Wrong Password! Please Try again!")
                    self.status = "Retry attempt : " + str(count)
                    count += 1
            else:
                messagebox.showwarning("Membership Not Found", "Non Member!")
                self.status = "Member not found!"
                break
#===============================================================================
# class MyDialog:
#     def __init__(self, parent):
# 
#         top = self.top = Toplevel(parent)
# 
#         Label(top, text="Value").pack()
# 
#         self.e = Entry(top)
#         self.e.pack(padx=5)
# 
#         b = Button(top, text="OK", command=self.ok)
#         b.pack(pady=5)
# 
#     def ok(self):
# 
#         print ("value is", self.e.get())
# 
#         self.top.destroy()       
#===============================================================================
#===============================================================================
# class BobbyButton:
#     def __init__(self, master):
#         frame = Frame(master)
#         frame.pack()
#         
#         self.printButton = Button(frame, text="Print Message", command=self.printMessage)
#         self.printButton.pack(side=LEFT)
#         
#         self.quitButton = Button(frame, text="Quit", command=frame.quit)
#         self.quitButton.pack(side=LEFT)
#     
#     def printMessage(self):
#         print("wow this actually works!")
# 
# GUI = Tk()
# B= BobbyButton(GUI)
# GUI.mainloop()
#===============================================================================
#===============================================================================
# def leftclick(event):
#     print("Left")
#     
# def rightclick(event):
#     print("right")
#     
# def middleclick(event):
#     print("middle")
# GUI = Tk()
# frame = Frame(GUI, width=300, height=250)
# frame.bind("<Button-1>", leftclick) # left mouse click
# frame.bind("<Button-2>", middleclick) # mouse rooler button
# frame.bind("<Button-3>", rightclick) # right mouse click
# frame.pack()
# GUI.mainloop()
#===============================================================================
#===============================================================================
# def printName(event): # if using binding method need to add event in parameter
#     print("My name is Bobby")
# GUI = Tk()
# button_1 = Button(GUI, text="Print My Name")
# button_1.bind("<Button-1>",printName) # binding method to call function
# button_1.pack()
# 
# GUI.mainloop()
#===============================================================================
#===============================================================================
#===============================================================================
# def printName():
#     print("My name is Bobby")
# GUI = Tk()
# button_1 = Button(GUI, text="Print My Name", command=printName) # call function while button click 
# button_1.pack()
# 
# GUI.mainloop()
#===============================================================================


#GUI = Tk() # create a blank window
#===============================================================================
# label_1=Label(GUI, text="Name") # label
# label_2=Label(GUI, text="Password")
# entry_1 = Entry(GUI) # input box
# entry_2 = Entry(GUI) # input box
# 
# label_1.grid(row=0, column=0, sticky=E) # set at first row and first column 
# label_2.grid(row=1, column=0, sticky=E) # set at second row and first column
# 
# entry_1.grid(row=0, column=1) # set at first row and second column
# entry_2.grid(row=1, column=1) # set at second row and second column
# 
# checkbox = Checkbutton(GUI, text="Keep me logged in") #checkbox tick or untick
# checkbox.grid(columnspan=2) # use up 2 column space
#===============================================================================
#===============================================================================
# one = Label(GUI, text="ONE", bg="red", fg="white")
# one.pack()
# two = Label(GUI, text="TWO", bg="green", fg="black")
# two.pack(fill=X) # label fill on Y axis
# three = Label(GUI, text="THREE", bg="blue", fg="white")
# three.pack(side=LEFT, fill=Y) # label fill on Y axis and always stay on left of window
#===============================================================================
#===============================================================================
# topframe = Frame(GUI) # create a frame in window
# topframe.pack(side=TOP) # make frame on top of window
# bottomframe = Frame(GUI) # create a frame in window
# bottomframe.pack(side=BOTTOM) # make frame on bottom of window
# 
# button1 = Button(topframe, text="Button 1", fg="red") create button (where to put, button text, foreground color))
# button2 = Button(topframe, text="Button 2", fg="blue")
# button3 = Button(topframe, text="Button 3", fg="green")
# button4 = Button(bottomframe, text="Button 4", fg="purple")
# 
# button1.pack(side=LEFT) # function to pack in your instant after u create, if not pack it , figure won't appear
# button2.pack(side=LEFT)
# button3.pack(side=LEFT)
# button4.pack(side=BOTTOM)
#===============================================================================
#mylabel = Label(GUI, text="first try tkinter")
#mylabel.pack()
#GUI.mainloop() # after all setting initiate window program