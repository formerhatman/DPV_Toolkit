#Toolkit!
#Author: Miles Neretin
#Purpose: To ease the process control procedure for thermal spray...

'''
Functionality:
-Simple distribution viewer

-hdbscan to remove noise, with min_samples, epsilon, and min_cluster selectable

-data_smushing with customizable filename parser to collect process parameters

-process map visualization

tabs:
hdbscan ("Noise Removal")
data_smusher ("Combine Datasets")

hdbscan layout:
|                                                                                       |
|                                                                                       |
|  _______________ [Browse] [Load]                                                      |
|                                                                                       |
|  epsilon:           ---------[]-------                                                |
|  min_samples:       ---------[]-------                                                |
|  min_cluster_size:  ---------[]-------                                                |
|                                                                                       |
|   --------------------------------------------------------------------------------    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                       plot of temperature vs velocity                        |    |
|   |                                                                              |    |
|   |                         color by !=-1                                        |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |     
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   |                                                                              |    |
|   --------------------------------------------------------------------------------    |
|                                                                                       |
|---------------------------------------------------------------------------------------|
'''

import numpy as np
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtGui,QtCore
import pyqtgraph as pg
from pyqtgraph.graphicsItems.LegendItem import ItemSample
import pandas as pd
import re
import hdbscan
import os

class disto(QtGui.QWidget):
    def __init__(self,*args,**kwargs):
        num_bins = 30
        QtGui.QWidget.__init__(self,*args,**kwargs)
        self.distfileentry = QtGui.QLineEdit()
        self.dist_browsebutton = QtGui.QPushButton("Browse for file...")
        self.graphics = pg.GraphicsLayoutWidget()
        self.p1 = self.graphics.addPlot(row=0,col=0)
        self.p2 = self.graphics.addPlot(row=1,col=0)
        self.p3 = self.graphics.addPlot(row=2,col=0)
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.graphics,1,0,1,2)
        self.layout.addWidget(self.distfileentry,0,0)
        self.layout.addWidget(self.dist_browsebutton,0,1)
        self.setLayout(self.layout)
        self.dist_browsebutton.clicked.connect(lambda: self.get_filedist())
    def get_filedist(self):
        filename, opt = QFileDialog.getOpenFileName(self,"Browse for Data File", "","PRT files (*.prt);; CSV files (*.csv);; Excel files (*)")
        self.distfileentry.insert(filename)
        if ".prt" in filename.lower():
            self.df = pd.read_csv(filename,sep='\s+')
        elif ".csv" in filename.lower():
            self.df = pd.read_csv(filename)
        elif ".xlsx" in filename.lower():
            self.df = pd.read_excel(filename)
        else:
            print("Unknown File Extension")
            return
        for pp,thing in zip([self.p1,self.p2,self.p3],["Temperature","Speed","Diameter"]):
            pp.setTitle(thing)
            pp.addLegend()
            histo,binz = np.histogram(self.df[thing].values,bins = 128)
            pp.plot(binz,histo,stepMode=True, fillLevel=0, brush=(0,0,255,150),name="Mean: {}".format(self.df[thing].mean()))



class grapho(pg.PlotWidget):
    def __init__(self,bigY,bigX,*args,**kwargs):
        pg.PlotWidget.__init__(self,*args,**kwargs)
        self.ploot = self.plot()
        self.Y = bigY #Speed
        self.X = bigX #Temperature
        self.opendir = ""
        self.errorbars = pg.ErrorBarItem(x = 0,y=0,pen=None)
        self.legendo = pg.LegendItem()
        # self.addLegend()
        # self.legendo.setParentItem(self.ploot)
        # self.legendo.setParentItem(self.getPlotItem())
        self.getViewBox().addItem(self.errorbars)
        self.addItem(self.legendo)
        # self.getViewBox().autoRange(items = [self.ploot])
        # self.getViewBox().setAutoVisible()
        
    def set_df(self,filetype,sampath):
        if 'prt' in filetype.lower():
            self.df = pd.read_csv(sampath,sep='\s+')
            self.sampath = sampath[:-4]
        elif 'csv' in filetype.lower():
            self.df = pd.read_csv(sampath)
            self.sampath = sampath[:-4]
        else:
            self.df = pd.read_excel(sampath)
            self.sampath = sampath[:-5]
        self.df.dropna(axis=1,inplace=True)
        print(self.sampath)
        self.df.dropna(axis=0,inplace=True)
    def redo_scan(self,min_samp=10,epsilon=0.3,min_cluster=120):

        clustering = hdbscan.HDBSCAN(min_samples = min_samp,cluster_selection_epsilon=epsilon,min_cluster_size = min_cluster)
        clustering.fit(self.df[[self.X,self.Y]])
        mask = clustering.labels_==-1
        sizes = np.where(mask,5,10)
        # # print(angle)
        # # print(self.line.value())
        # test = self.df[self.X].values*slope + b
        # valid = np.where(self.df[self.Y].values>test,True,False)
        # print(valid)
        # where = self.df[self.Y].values>test
        self.ploot.setData(self.df[self.X],self.df[self.Y],symbolSize = sizes)

    def graphene(self,*args,**kwargs):
        self.ploot.setData(*args,**kwargs)
        # self.errorbars.setData
    def grouping(self,kwds):
        self.ploot.clear()
        self.legendo.clear()
        means = self.df.groupby(kwds).mean()
        stds = self.df.groupby(kwds).std()
        count = means.shape[0]
        labels= means.index.values
        colors = [pg.intColor(i,hues=count) for i  in range(count)]
        # pencil = pg.mkPen(color=colors,)
        
        self.errorbars.setData(x = means[self.X].values,y = means[self.Y].values,height = stds[self.Y].values, width = stds[self.Y].values)
        self.ploot.setData(means[self.X].values,means[self.Y].values,pen=None,symbolBrush = colors,symbol = 'o')
        # points = self.ploot.points()
        # points = self.ploot.scatter.points()
        for i in range(count):
            yes = self.plot(means[self.X].values[i:i],means[self.Y].values[i:i],pen=None,symbolBrush = colors[i],symbol = 'o',name = means.index.values[i])
            self.legendo.addItem(ItemSample(yes),name = means.index.values[i])
        # self.legendo.addItem(item)
        # self.addLegend()
        # self.legendo.setParent(self.ploot)
        self.ploot.getViewBox().setRange(xRange = (means[self.X].min() - stds[self.X].max(),means[self.X].max() + stds[self.X].max()), yRange = (means[self.Y].min() - stds[self.Y].max(),means[self.Y].max() + stds[self.Y].max()))
        self.legendo.setPos(means[self.X].min() - (stds[self.X].max()+50),means[self.Y].max()+stds[self.Y].max()+100)
        

 
    def save_data(self,min_samp,epsilon,min_cluster):
        clustering = hdbscan.HDBSCAN(min_samples = min_samp,cluster_selection_epsilon=epsilon,min_cluster_size = min_cluster)
        clustering.fit(self.df[[self.X,self.Y,"Diameter"]])
        goodpts = np.where(clustering.labels_==-1,False,True)
        gooddf = self.df[goodpts]

        #To change it from "Gucci" is an act of betrayal.
        #Live a little!

        gooddf.to_csv(self.sampath+"_Gucci.csv")
        self.ploot.clear()
        self.graphene(gooddf[self.X],gooddf[self.Y],pen=None,symbol='o')




Toolkit = QtGui.QApplication([])

w = QtGui.QMainWindow()

w.setWindowTitle("DPV Toolkit beta 0.6.9")
w.resize(QtCore.QSize(1200,600))
masterlayout = QtGui.QGridLayout()
tabs = QtGui.QTabWidget()
distributiontab = disto()
hdbscan_tab = QtGui.QWidget()
smusher_tab = QtGui.QWidget()
fitting_tab = QtGui.QWidget()
tabs.addTab(distributiontab, "Distributions")
tabs.addTab(hdbscan_tab, "Noise Removal")
tabs.addTab(smusher_tab, "Data Compiler")
tabs.addTab(fitting_tab, "Modeling")

#distributions tab



#hdbscan tab

hdbscan_tab.layout = QtGui.QGridLayout()

go_button = QtGui.QPushButton('Save Filtered Data')
browse_button = QtGui.QPushButton("Browse")
file_entry = QtGui.QLineEdit()

eps_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
eps_label = QtGui.QLabel('Epsilon')
min_samp_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
min_samp_label = QtGui.QLabel('Noisiness')
min_cluster_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
min_cluster_label = QtGui.QLabel('Error Size')
eps_slider.setMinimum(0.1)
eps_slider.setMaximum(10.0)
eps_slider.setSingleStep(0.1)
eps_slider.setValue(0.3)
min_samp_slider.setMinimum(1)
min_samp_slider.setMaximum(100)
min_samp_slider.setSingleStep(1)
min_samp_slider.setValue(10)
min_cluster_slider.setMinimum(2)
min_cluster_slider.setMaximum(300)
min_cluster_slider.setSingleStep(1)
min_cluster_slider.setValue(120)


labels = [eps_label,min_samp_label,min_cluster_label]
for i,slide in enumerate([eps_slider,min_samp_slider,min_cluster_slider]):
    slide.sliderReleased.connect(lambda: graph.redo_scan(min_samp = min_samp_slider.value(),epsilon=eps_slider.value(),min_cluster=min_cluster_slider.value()))
    hdbscan_tab.layout.addWidget(slide,1+i,1,1,4)
    hdbscan_tab.layout.addWidget(labels[i],1+i,0)
graph = grapho("Speed","Temperature")
graph.setLabels(left='Speed',bottom='Temperature')

def get_filename(filespot,graphspot,rolling=False):
    filename, opt = QFileDialog.getOpenFileName(hdbscan_tab,"Browse for Data File", "","PRT files (*.prt);; CSV files (*.csv);; Excel files (*)")
    filespot.insert(filename)
    graphspot.set_df(opt,filename)
    if rolling==False:
        graphspot.graphene(graphspot.df['Temperature'],graphspot.df['Speed'],pen=None,symbol='o')
        graphspot.redo_scan()
    else:
        graphspot.graphene(graphspot.df['Temperature'].rolling(500).mean(),graphspot.df['Speed'].rolling(500).mean(),pen=None,symbol='o',name='init')




browse_button.clicked.connect(lambda: get_filename(file_entry,graph))
go_button.clicked.connect(lambda:graph.save_data(min_samp = min_samp_slider.value(),epsilon=eps_slider.value(),min_cluster=min_cluster_slider.value()))
# hdbscan_tab.layout.addWidget()
hdbscan_tab.layout.addWidget(go_button,0,4)
hdbscan_tab.layout.addWidget(browse_button,0,3)
hdbscan_tab.layout.addWidget(file_entry,0,0,1,3)
hdbscan_tab.layout.addWidget(graph,5,0,2,5)

hdbscan_tab.setLayout(hdbscan_tab.layout)

#data compiler tab





smusher_tab.layout = QtGui.QGridLayout()
file_list = QtGui.QListWidget()
file_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
filename_config = QtGui.QLineEdit()
status_label = QtGui.QLabel("Waiting to smush...")
opendir = ''
def find_matches(search,filename):
    if "*" in search:
        regexp = search.replace("*","([0-9]+)")
        finds = re.findall(r'{}'.format(regexp) ,filename)
        if len(finds)>1:
            finds = [float(find) for find in finds]
            val = max(finds)
        elif len(finds)==0:
            val = 123.45678
        else:
            val = float(finds[0])
    else:
        regexp = search
        finds = re.findall(r'{}'.format(regexp) ,filename)
        if len(finds)==0:
            val = 'temp'
        else:
            val = finds[0]
    return(val)



def get_directory():
    graph.opendir = QFileDialog.getExistingDirectory(smusher_tab,"Browse for Data Folder")
    status_label.setText("Waiting to smush...")
    for root,dirs,files in os.walk(graph.opendir):
        for file in files:
            if ".prt" in file:
                file_list.addItem('{}/{}'.format(root.lower(),file.lower()))
            elif ".csv" in file:
                # file_list.addItem('{}/{}'.format(root.lower(),file.lower()))
                pass
            else:
                pass
def delete_selections():
    for file in file_list.selectedItems():
        file_list.takeItem(file_list.row(file))
def smush():
    status_label.setText("Now smushing, please wait...")
    filenames = []
    dfs = []
    for i in range(file_list.count()):
        if file_list.item(i) == '':
            pass
        else:
            filename = file_list.item(i).text()
            filenames.append(filename)
            if ".prt" in filename:
                print(filename)
                df = pd.read_csv(filename,sep='\s+',skiprows = 1,error_bad_lines = False,usecols=[x for x in range(9)])
                df.columns = ['Date', 'Time', 'X', 'Y', 'Speed', 'Temperature', 'Diameter', 'EnergyA','EnergyB']
                # df.columns = 
            else:
                df = pd.read_csv(filename)
            for item in re.findall('\(.*?\)',filename_config.text()):
                # print(item)
                search  = item[item.find(":")+1:item.find(")")]
                column_name = item[1:item.find(":")]
                # print(column_name)
                if column_name in df.columns:
                    if not ( (123.45678 in df[column_name].values) or ('temp' in df[column_name].values) ) :
                        pass
                    else:
                        df[column_name] = find_matches(search,filename)
                else:
                    df[column_name] = find_matches(search,filename)
            df['Filename'] = filename
            dfs.append(df.copy())
    try:
        bigdf = pd.concat(dfs)
        print(bigdf.columns)
        
        bigdf.to_csv('{}/combined.csv'.format(graph.opendir))
        status_label.setText("Smush Successful!")
    except ValueError:
        status_label.setText("No files to smush!")
        return
    


#(Ar:Ar*)-(H2:H*)-(Current:*A) (SD:*mm SD)


filename_label = QtGui.QLabel("Filename Configuration")

delete_button = QtGui.QPushButton("Remove Selections")
folder_browse = QtGui.QPushButton("Browse for Directory")
compile_button = QtGui.QPushButton('Smush!')
folder_browse.clicked.connect(lambda: get_directory())
delete_button.clicked.connect(lambda: delete_selections())
compile_button.clicked.connect(lambda: smush())
smusher_tab.layout.addWidget(compile_button,2,0)
smusher_tab.layout.addWidget(status_label,3,0)
smusher_tab.layout.addWidget(filename_config,0,1)
smusher_tab.layout.addWidget(filename_label,0,0)
smusher_tab.layout.addWidget(folder_browse,0,2)
smusher_tab.layout.addWidget(file_list,1,1,3,3)
smusher_tab.layout.addWidget(delete_button,0,3)
smusher_tab.setLayout(smusher_tab.layout)

#Modeling tab
'''modeling tab:

side list of column names after df loads
select columns to group on
legend updates with each group
'''

fitting_tab.layout = QtGui.QGridLayout()
fitting_filename = QtGui.QLineEdit()
fitting_filebrowse = QtGui.QPushButton("Browse for File...")
fitting_graph = grapho("Temperature","Speed")
fitting_list = QtGui.QListWidget()
fitting_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
def get_columnnames(filename,graphspot):
    get_filename(filename,graphspot,rolling=True)
    for col in graphspot.df.columns:
        fitting_list.addItem(col)


def separate_things(pls):
    # print(pls)
    items_list = []
    for i in range(fitting_list.count()):
        item = fitting_list.item(i)
        if item.isSelected():
            items_list.append(item.text())
    if not items_list:
        return
    else:
        fitting_graph.grouping(items_list)

    # for ind in fitting_list.
    # print(model.itemFromIndex(pls).text())



fitting_filebrowse.clicked.connect(lambda: get_columnnames(fitting_filename,fitting_graph))
fitting_list.clicked.connect(lambda yes: separate_things(yes))




fitting_tab.layout.addWidget(fitting_list,0,0,2,1)
fitting_tab.layout.addWidget(fitting_filename,0,1)
fitting_tab.layout.addWidget(fitting_filebrowse,0,2)
fitting_tab.layout.addWidget(fitting_graph,1,1,1,2)

fitting_tab.layout.setColumnStretch(1,20)

fitting_tab.layout.setColumnMinimumWidth(0,5)

fitting_tab.setLayout(fitting_tab.layout)



w.setCentralWidget(tabs)

Toolkit.window=w
w.show()
Toolkit.exec_()