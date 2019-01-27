'''
Created on 16 Dec 2018

@author: bobbylee
'''
from tkinter import *
import sys
from MainGui import MainGUI

GUI = Tk()
GUI.title("Face ID Transaction")
GUI.config(bg='white')
x = (GUI.winfo_screenwidth() - GUI.winfo_reqwidth())/2
y = (GUI.winfo_screenheight() - GUI.winfo_reqheight())/2
GUI.geometry("+%d+%d" % (x,y))
GUI.deiconify()
MainGUI(GUI)
GUI.mainloop()