
# coding: utf-8

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
import datetime
import os.path
import cx_Oracle
import threading
from matplotlib import pyplot as plt

#UI fonts
LARGE_FONT= ("Calibri", 24)
NORM_FONT= ("Calibri", 10)
SMALL_FONT= ("Calibri", 8)




style.use("ggplot")
day = time.strftime("%d-%m-%Y")
temperatureFigure = Figure()
heatFluxFigure = Figure()
temperaturePlot = temperatureFigure.add_subplot(111)
heatFluxPlot = heatFluxFigure.add_subplot(111)

#Arduino preconfigs
port="/dev/ttyACM0" 
speed=9600
tout=4 
ser = serial.Serial(port, speed, timeout=tout)
insideCellNumber = 1
#Sets up data base connection 
username = 'cdioil15_11'
password = 'qwerty'
server = 'gandalf.dei.isep.ipp.pt'
service_name = 'pdborcl'
con = cx_Oracle.connect(username+'/'+password+'@'+server+'/'+service_name)             
print ("Connected to database, database version "+con.version)


#To change the serial port
def changePort():
    ser = serial.Serial(port, speed, timeout=tout)	
    #Sleep 2 seconds so the connection can finish
    time.sleep(2)	

#Ask the arduino for a temperature (0 is for outside temperature) (Numbers are for diferent cells)
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
    print(fileName+" temperature file created")
    
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
    temperaturePlot.clear()

    outsideValues = [float(numeric_string) for numeric_string in outsideValues]
    cellValues = [float(numeric_string) for numeric_string in cellValues]

    temperaturePlot.plot( t , outsideValues , "red", label="temperature Outside")
    temperaturePlot.plot( t , cellValues , "blue", label="temperature on Cell"+str(insideCellNumber))

    temperaturePlot.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0)

conductivity = 1
surface = 1
thickness = 1
def animateHeatFlux(i):

    outsideValues = open("Outside"+day+".txt","r").read().splitlines()
    cellValues = open("Cell-"+str(insideCellNumber)+"-"+day+".txt").read().splitlines()


    t = np.arange(0.0, len(outsideValues) , 1)
    heatFluxPlot.clear()

    outsideValues = np.array([float(numeric_string) for numeric_string in outsideValues])
    cellValues = np.array([float(numeric_string) for numeric_string in cellValues])
    temperatureDifference = outsideValues-cellValues
    heatFluxPlot.plot( t  , conductivity*surface*(temperatureDifference/thickness) , "red", label="Heat Flux")

    heatFluxPlot.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,ncol=2, borderaxespad=0)

    title = "Heat Flux"
    heatFluxPlot.set_title(title)

def saveValues():
    lastOutsideValue = str(outsideValues[-1])
    lastCellValue = str(outsideValues[-1])
    date = str(datetime.datetime.now())
    conString = 'INSERT INTO "CDIOIL15_11"."TEMPERATURE_DATA" (INSIDETEMPERATURE, OUTSIDETEMPERATURE, OCORRENCE_DATE) VALUES (\''+ lastOutsideValue+'\',\''+ lastCellValue+'\', TO_TIMESTAMP(\''+date+'\', \'YYYY-MM-DD HH24:MI:SS.FF\''+'))'
    cur.execute(conString)
    con.commit()
    cur.close()
    print("Values: Outside temprature-"+lastOutsideValue+"  Cell Temprature-"+lastCellValue+" Saved to database -"+ date)
    time.sleep(5)
    saveValues()


class temperatureMonitoring(Tk):

    def __init__(self, *args, **kwargs):

        #Sleep 2 seconds so the connection can finish
        time.sleep(2)

        Tk.__init__(self, *args, **kwargs)

        Tk.wm_title(self, "temperature Monitoring")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("BW.TLabel", foreground="black", background="white")
        self.option_add("*background", "white")
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

        buttontemperature = ttk.Button(self, text="temperature",
                            command=lambda: controller.show_frame(Graph_Page))
        buttontemperature.pack()
        
        rightframe = Frame(self,height=50)
        rightframe.pack( side = RIGHT )
        
        Label(rightframe,text = "Conductividade").pack(side="top")

        self.stringConductivity = StringVar()	
        self.stringConductivity.trace("w",lambda name, index ,mode, sv=self.stringConductivity, :self.updateConductivity(sv))
        materials = ['Madeira-1.2332','Aço-3.432','Ferro-4.3243']
        self.box = ttk.Combobox( rightframe,values=materials,textvariable=self.stringConductivity).pack(side="top")

        self.stringSurface = StringVar()	
        self.stringSurface.trace("w",lambda name, index ,mode, sv=self.stringSurface, :self.updateSurface(sv))
        Label(rightframe,text = "Area").pack(side="top")
        Entry(rightframe,textvariable=self.stringSurface).pack(side="top")

        self.stringThickness = StringVar()	
        self.stringThickness.trace("w",lambda name, index ,mode, sv=self.stringThickness, :self.updateThickness(sv))
        Label(rightframe,text = "Espessura").pack(side="top")
        Entry(rightframe,textvariable=self.stringThickness).pack(side="top")
     
        heatFluxCanvas = FigureCanvasTkAgg(heatFluxFigure, self)
        heatFluxCanvas.show()
        heatFluxCanvas.get_tk_widget().pack(side=TOP, fill=BOTH , expand=True)
        
        heatFluxToolbar= NavigationToolbar2TkAgg(heatFluxCanvas, self)
        heatFluxToolbar.update()
        heatFluxCanvas._tkcanvas.pack(side=TOP)

    def updateSurface(self,sv):
        global surface
        try: 
            s = ''.join(x for x in sv.get() if x.isdigit())
            num = float(s)
            print(num)
            surface = num
        except ValueError:
            surface = 1

    def updateThickness(self,sv):
        global thickness
        try: 
            num = float(sv.get())
            thickness = num
        except ValueError:
            thickness = 1

    def updateConductivity(self,sv):
        global conductivity
        try: 
            num = float(sv.get())
            conductivity = num
        except ValueError:
            conductivity = 1

		        
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
        texto = StringVar()
        self.labelTop = ttk.Label(rightframe,text="Outside", style="BW.TLabel", width=30,font=NORM_FONT)
        self.labelTop.pack(side="top")
        self.labelMaxInterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelMaxInterior.pack(side="top")
        self.labelMinInterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelMinInterior.pack(side="top")
        self.labelDifInterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelDifInterior.pack(side="top")
        self.labelMid = ttk.Label(rightframe,text="\n\n\nSelected Cell", style="BW.TLabel", width=30,font=NORM_FONT)
        self.labelMid.pack(side="top")
        self.labelMaxExterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelMaxExterior.pack(side="top")
        self.labelMinExterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelMinExterior.pack(side="top")
        self.labelDifExterior = ttk.Label(rightframe, style="BW.TLabel", width=30)
        self.labelDifExterior.pack(side="top")



        canvas = FigureCanvasTkAgg(temperatureFigure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH , expand=True)
        
        toolbar= NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()
	
        self.updateGraph()

    def updateGraph(self):
        outsideValues = open("Outside"+day+".txt","r").read().splitlines()
        cellValues = open("Cell-"+str(insideCellNumber)+"-"+day+".txt").read().splitlines()

        outsideValues = [float(numeric_string) for numeric_string in outsideValues]
        cellValues = [float(numeric_string) for numeric_string in cellValues]
        self.labelMaxInterior.configure(text="Max Temp ="+str(max(outsideValues)))	
        self.labelMinInterior.configure(text="Min Temp ="+str(min(outsideValues)))
        self.labelDifInterior.configure(text="Delta T Temp ="+str(max(outsideValues)-min(outsideValues)))
        self.labelDifExterior.configure(text="Delta T Temp ="+str(max(cellValues)-min(cellValues)))
        self.labelMinExterior.configure(text="Min Temp ="+str(min(cellValues)))
        self.labelMaxExterior.configure(text="Max Temp ="+str(max(cellValues)))

        self.after(5000,self.updateGraph)	
	
        


if __name__ == "__main__":
    app = temperatureMonitoring()
    app.geometry("1000x600")
    ani = animation.FuncAnimation(temperatureFigure, animateOutsideTemp, interval=500)
    heatFluxAni = animation.FuncAnimation(heatFluxFigure, animateHeatFlux, interval=500)
    t = threading.Thread(target=saveValues)
    t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
    t.start()
    app.mainloop()

