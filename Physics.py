
# coding: utf-8
#To do
# ASk professor for good python
# Menu/Combo box for Cell
# Menu/Combo box for Port
# HeatFlux insert actions
# Heat flux graph


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

from tkinter import *
from tkinter import ttk
import pandas as pd
import numpy as np
import serial
import time
import os.path
from matplotlib import pyplot as plt

#UI fonts
LARGE_FONT= ("Calibri", 24)
NORM_FONT= ("Calibri", 10)
SMALL_FONT= ("Calibri", 8)




style.use("ggplot")
day = time.strftime("%d-%m-%Y")
tempratureFigure = Figure()
heatFluxFigure = Figure()
tempraturePlot = tempratureFigure.add_subplot(111)
heatFluxPlot = heatFluxFigure.add_subplot(111)

#Arduino preconfigs
port="/dev/ttyACM0" 
speed=9600
tout=4 
ser = serial.Serial(port, speed, timeout=tout)
insideCellNumber = 1

#To change the serial port
def changePort():
    ser = serial.Serial(port, speed, timeout=tout)	
    #Sleep 2 seconds so the connection can finish
    time.sleep(2)	

#Ask the arduino for a temprature (0 is for outside temprature) (Numbers are for diferent cells)
def askArduino(n):
    ser.write(str(n).encode('UTF-8'))
    return float(ser.readline())
#Verifies if fileName exists
def checkFile(fileName,n):
    if  os.path.isfile(fileName):
        return
    print("Creating new file")
    file = open(fileName,"w+")
    #Sleep 2 seconds so the connection can finish
    time.sleep(2)	
    file.write(str(askArduino(n))+"\n")
    file.close()
    print(fileName+" temprature file created")
    
#First read of the outside file, if it does exist creates a new one with value
day = time.strftime("%d-%m-%Y")
checkFile("Outside"+day+".txt" ,0)
outsideValues = open("Outside"+day+".txt" ,"r").read().splitlines()
outsideValues = [float(numeric_string) for numeric_string in outsideValues]

#First read of the inside file, if it does exist creates a new one with value and predefined cell value of 1

checkFile("Cell-"+str(insideCellNumber)+"-"+day+".txt" ,insideCellNumber)
cellValues = open("Cell-"+str(insideCellNumber)+"-"+day+".txt").read().splitlines()
cellValues = [float(numeric_string) for numeric_string in cellValues]

#UI predefined pop message
def popupmsg(msg):
    popup = Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

#Plot animator
def animateOutsideTemp(i):
    file = open("Outside"+day+".txt","a")
    file.write(str(askArduino(0))+"\n")
    file.close()

    file = open("Cell-"+str(insideCellNumber)+"-"+day+".txt","a")
    file.write(str(askArduino(insideCellNumber))+"\n")
    file.close()

    outsideValues = open("Outside"+day+".txt","r").read().splitlines()
    cellValues = open("Cell-"+str(insideCellNumber)+"-"+day+".txt").read().splitlines()


    t = np.arange(0.0, len(outsideValues) , 1)
    tempraturePlot.clear()

    outsideValues = [float(numeric_string) for numeric_string in outsideValues]
    cellValues = [float(numeric_string) for numeric_string in cellValues]

    tempraturePlot.plot( t , outsideValues , "red", label="Temprature Outside")
    tempraturePlot.plot( t , cellValues , "blue", label="Temprature on Cell"+str(insideCellNumber))

    tempraturePlot.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0)

    title = "Temprature Monitoring Last 10 values: "
    tempraturePlot.set_title(title)


def animateHeatFlux(i):

    heatFluxT = np.arange(0, 100, 2)
    heatFluxPlot.clear()

    heatFluxPlot.plot( heatFluxT  , heatFluxT*2 , "red", label="Heat Flux")

    heatFluxPlot.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0)

    title = "Heat Flux"
    heatFluxPlot.set_title(title)






class TempratureMonitoring(Tk):

    def __init__(self, *args, **kwargs):

        #Sleep 2 seconds so the connection can finish
        time.sleep(2)

        Tk.__init__(self, *args, **kwargs)

        Tk.wm_title(self, "Temprature Monitoring")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("BW.TLabel", foreground="black", background="white")
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        menubar = Menu(container)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command = lambda: popupmsg("Not supported just yet!"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, Graph_Page,Heat_Flux_Graph):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self,parent)
        label = Label(self, text=("""Grupo Sigma ftw, Tempraturas e essas coisas."""), font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Agree",
                            command=lambda: controller.show_frame(Graph_Page))
        button1.pack()

        button2 = ttk.Button(self, text="Disagree",command=lambda: popupmsg("Program will not show"))
        button2.pack()



class Heat_Flux_Graph(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Heat Flux", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        buttonTemprature = ttk.Button(self, text="Temprature",
                            command=lambda: controller.show_frame(Graph_Page))
        buttonTemprature.pack()
        
        rightframe = Frame(self,height=50)
        rightframe.pack( side = RIGHT )
        
        labelMid = ttk.Label(rightframe,text="Condutividade", style="BW.TLabel", width=30)
        labelMid.pack(side="top")
        w = ttk.Entry(rightframe)
        w.pack(side="top")
        labelMid = ttk.Label(rightframe,text="Area", style="BW.TLabel", width=30)
        labelMid.pack(side="top",command=lambda: popmsg("Funionou"))
        w = ttk.Entry(rightframe)
        w.pack(side="top")
        labelMid = ttk.Label(rightframe,text="Espessura", style="BW.TLabel", width=30)
        labelMid.pack(side="top")
        w = ttk.Entry(rightframe)
        w.pack(side="top")
     
        heatFluxCanvas = FigureCanvasTkAgg(heatFluxFigure, self)
        heatFluxCanvas.show()
        heatFluxCanvas.get_tk_widget().pack(side=TOP, fill=BOTH , expand=True)
        
        heatFluxToolbar= NavigationToolbar2TkAgg(heatFluxCanvas, self)
        heatFluxToolbar.update()
        heatFluxCanvas._tkcanvas.pack(side=TOP)




class Graph_Page(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        buttonHeatFlux = ttk.Button(self, text="Heat Flux",
                            command=lambda: controller.show_frame(Heat_Flux_Graph))
        buttonHeatFlux .pack()
    
        rightframe = Frame(self,height=50)
        rightframe.pack( side = RIGHT )
     
        labelMaxInterior = ttk.Label(rightframe,text="Max Temp ="+str(max(outsideValues)), style="BW.TLabel", width=30)
        labelMaxInterior.pack(side="top")
        labelMinInterior = ttk.Label(rightframe,text="Min Temp ="+str(min(outsideValues)), style="BW.TLabel", width=30)
        labelMinInterior.pack(side="top")
        labelDifInterior = ttk.Label(rightframe,text="Delta T Temp ="+str(max(outsideValues)-min(outsideValues)), style="BW.TLabel", width=30)
        labelDifInterior.pack(side="top")
        labelMid = ttk.Label(rightframe,text="\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", style="BW.TLabel", width=30)
        labelMid.pack(side="top")
        labelDifExterior = ttk.Label(rightframe,text="Delta T Temp ="+str(max(cellValues)-min(cellValues)), style="BW.TLabel", width=30)
        labelDifExterior.pack(side="bottom")
        labelMinExterior = ttk.Label(rightframe,text="Min Temp ="+str(min(cellValues)), style="BW.TLabel", width=30)
        labelMinExterior.pack(side="bottom")
        labelMaxExterior = ttk.Label(rightframe,text="Max Temp ="+str(max(cellValues)), style="BW.TLabel", width=30)
        labelMaxExterior.pack(side="bottom")

        canvas = FigureCanvasTkAgg(tempratureFigure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH , expand=True)
        
        toolbar= NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()
        


app = TempratureMonitoring()
app.geometry("1000x600")
ani = animation.FuncAnimation(tempratureFigure, animateOutsideTemp, interval=5000)
heatFluxAni = animation.FuncAnimation(heatFluxFigure, animateHeatFlux, interval=5000)
app.mainloop()




print(askArduino(1))





