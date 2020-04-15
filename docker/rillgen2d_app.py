import tkinter as tk
from tkinter import *
import os.path
import subprocess



class Application(tk.Frame):
    def __init__(self, *args):
        tk.Frame.__init__(self, *args)

        ########################### MAIN TAB ###########################
        self.introLabel = Label(self, text='rillgen2d', font='Helvetica 40 bold italic underline').grid(row=1, column=1)
        self.description = Label(self, text='Input Descriptions', font='Halvetica 20 bold underline', fg='gray').grid(row=2, column=2, sticky='w')
        self.inputLabel = Label(self, text='Inputs', font='Halvetica 20 bold underline').grid(row=2, column=0)
        self.goButton = Button(self, text='Go', command=self.runCommand, padx=20)
        self.goButton.grid(row=30, column=1)

        # Flagformask variable
        self.flagformaskLabel = Label(self, text='flagformask:', font='Helvetica 15 bold').grid(row=3, column=0)
        self.flagformaskLabel2 = Label(self, text='Should be 1 if the user provides a raster (mask.txt) that restricts the model to certain portions of the input DEM\n(mask = 1 means run the model, 0 means ignore these areas), 0 otherwise.', fg='gray',justify=LEFT).grid(row=3, column=2, sticky='w')
        self.flagformaskVar = StringVar()
        self.flagformaskInput = Entry(self, textvariable=self.flagformaskVar, width=5)
        self.flagformaskInput.grid(row=3, column=1)
        self.flagformaskOut = self.flagformaskVar        
        # Should be 1 if the user provides a raster (mask.txt) that restricts the model to certain portions of the input DEM (mask = 1 means run the model, 0 means ignore these areas), 0 otherwise.
    
        # Flagford50 variable
        self.flagford50Label = Label(self, text='flagford50:', font='Helvetica 15 bold').grid(row=4, column=0)
        self.flagford50Label2 = Label(self, text='Should be 1 if the user provides a raster of median rock armor particle diameter (d50.txt) equal in size and resolution to the input DEM,\n0 if a single value of the median rock armor particle dimater is input (including 0 in the case of no rock armor).', fg='gray',justify=LEFT).grid(row = 4, column=2, sticky='w')
        self.flagford50Var = StringVar()
        self.flagford50Input = Entry(self, textvariable=self.flagford50Var, width=5)
        self.flagford50Input.grid(row=4, column=1)
        self.flagford50Out = self.flagford50Var
        # Should be 1 if the user provides a raster of median rock armor particle diameter (d50.txt) equal in size and resolution to the input DEM, 0 if a single value of the median rock armor particle dimater is input (including 0 in the case of no rock armor).

        # Flagfortaucsoilandveg variable
        self.flagfortaucsoilandvegLabel = Label(self, text='flagfortaucsoilandveg:', font='Helvetica 15 bold').grid(row=5, column=0)
        self.flagfortaucsoilandvegLabel2 = Label(self, text='Should be 1 if the user provides a raster of the shear strength of the soil and vegetation (taucsoilandveg.txt) equal to in size and resolution to the input DEM.', fg='gray',justify=LEFT).grid(row=5, column=2, sticky='w')
        self.flagfortaucsoilandvegVar = StringVar()
        self.flagfortaucsoilandvegInput = Entry(self, textvariable=self.flagfortaucsoilandvegVar, width=5)
        self.flagfortaucsoilandvegInput.grid(row=5, column=1)
        self.flagfortaucsoilandvegOut = self.flagfortaucsoilandvegVar
        # Should be 1 if the user provides a raster of the shear strength of the soil and vegetation (taucsoilandveg.txt) equal to in size and resolution to the input DEM.

        # Flagforrouting variable
        self.flagforroutingLabel = Label(self, text='flagforrouting:', font='Helvetica 15 bold').grid(row=6, column=0)
        self.flagforroutingLabel2 = Label(self, text='Should be 1 if the user wants to use DInfinity (Tarboton et al., 1997) routing,  0 if the user wants to use MFD (Freeman, 1991) routing.', fg='gray',justify=LEFT).grid(row=6, column=2, sticky='w')
        self.flagforroutingVar = StringVar()
        self.flagforroutingInput = Entry(self, textvariable=self.flagforroutingVar, width=5)
        self.flagforroutingInput.grid(row=6, column=1)
        self.flagforroutingOut = self.flagforroutingVar
        # Should be 1 if the user wants to use DInfinity (Tarboton et al., 1997) routing, 0 if the user wants to use MFD (Freeman, 1991) routing.

        # Fillincrement variable
        self.fillincrementLabel = Label(self, text='fillincrement:', font='Helvetica 15 bold').grid(row=7, column=0)
        self.fillincrementLabel2 = Label(self, text='This value (in meters) is used to fill in pits and flats for hydrologic correction. 0.01 is a reasonable default value.', fg='gray',justify=LEFT).grid(row=7, column=2, sticky='w')
        self.fillincrementVar = StringVar()
        self.fillincrementInput = Entry(self, textvariable=self.fillincrementVar, width=5)
        self.fillincrementInput.grid(row=7, column=1)
        self.fillincrementOut = self.fillincrementVar
        # This value (in meters) is used to fill in pits and flats for hydrologic correction. 0.01 is a reasonable default value.

        # Threshslope variable
        self.threshslopeLabel = Label(self, text='threshslope:', font='Helvetica 15 bold').grid(row=8, column=0)
        self.threshslopeLabel2 = Label(self, text='This value (unitless) is used to halt runoff from areas below a threshold slope steepness.\nSetting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.', fg='gray',justify=LEFT).grid(row=8, column=2, sticky='w')
        self.threshslopeVar = StringVar()
        self.threshslopeInput = Entry(self, textvariable=self.threshslopeVar, width=5)
        self.threshslopeInput.grid(row=8, column=1)
        self.threshslopeOut = self.threshslopeVar
        # This value (unitless) is used to halt runoff from areas below a threshold slope steepness. Setting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.

        # Expansion variable
        self.expansionLabel = Label(self, text='expansion:', font='Helvetica 15 bold').grid(row=9, column=0)
        self.expansionLabel2 = Label(self, text='This value (in number of pixels) is used to expand the zones where rills are predicted in the output raster.\nThis is useful for making the areas where rilling is predicted easier to see in the model output.', fg='gray',justify=LEFT).grid(row=9, column=2, sticky='w')
        self.expansionVar = StringVar()
        self.expansionInput = Entry(self, textvariable=self.expansionVar, width=5)
        self.expansionInput.grid(row=9, column=1)
        self.expansionOut = self.expansionVar
        # This value (in number of pixels) is used to expand the zones where rills are predicted in the output raster. This is useful for making the areas where rilling is predicted easier to see in the model output.
        
        # Yellowthreshold variable
        self.yellowthresholdLabel = Label(self, text='yellowthreshold:', font='Helvetica 15 bold').grid(row=10, column=0)
        self.yellowthresholdLabel2 = Label(self, text='This is a threshold value of f used to indicate an area that is close to but less than the threshold for generating rills.\nThe model will visualize any location with a f value between this value and\n1 as potentially prone to rill generation(any area with a f value larger than 1 is considered prone to rill generation and is colored red).', fg='gray',justify=LEFT).grid(row=10, column=2, sticky='w')
        self.yellowthresholdVar = StringVar()
        self.yellowthresholdInput = Entry(self, textvariable=self.yellowthresholdVar, width=5)
        self.yellowthresholdInput.grid(row=10, column=1)
        self.yellowthresholdOut = self.yellowthresholdVar
        # This is a threshold value of f used to indicate an area that is close to but less than the threshold for generating rills. The model will visualize any location with a f value between this value and 1 as potentially prone to rill generation (any area with a f value larger than 1 is considered prone to rill generation and is colored red)
        
        # Lattice_size_x variable
        self.lattice_size_xLabel = Label(self, text='lattice_size_x:', font='Helvetica 15 bold').grid(row=11, column=0)
        self.lattice_size_xLabel2 = Label(self, text='The number of pixels along the east-west direction in the DEM.', fg='gray').grid(row=11, column=2, sticky='w')
        self.lattice_size_xVar = StringVar()
        self.lattice_size_xInput = Entry(self, textvariable=self.lattice_size_xVar, width=5)
        self.lattice_size_xInput.grid(row=11, column=1)
        self.lattice_size_xOut = self.lattice_size_xVar
        # The number of pixels along the east-west direction in the DEM.

        # Lattice_size_y variable
        self.lattice_size_yLabel = Label(self, text='lattice_size_y:', font='Helvetica 15 bold').grid(row=12, column=0)
        self.lattice_size_yLabel2 = Label(self, text='The number of pixels along the east-west direction in the DEM.', fg='gray',justify=LEFT).grid(row=12, column=2, sticky='w')
        self.lattice_size_yVar = StringVar()
        self.lattice_size_yInput = Entry(self, textvariable=self.lattice_size_yVar, width=5)
        self.lattice_size_yInput.grid(row=12, column=1)
        self.lattice_size_yOut = self.lattice_size_yVar
        # The number of pixels along the east-west direction in the DEM.

        # Deltax variable
        self.deltaxLabel = Label(self, text='deltax:', font='Helvetica 15 bold').grid(row=13, column=0)
        self.deltaxLabel2 = Label(self, text='The resolution (in meters/pixel) of the DEM and additional optional raster inputs.', fg='gray',justify=LEFT).grid(row=13, column=2, sticky='w')
        self.deltaxVar = StringVar()
        self.deltaxInput = Entry(self, textvariable=self.deltaxVar, width=5)
        self.deltaxInput.grid(row=13, column=1)
        self.deltaxOut = self.deltaxVar
        # The resolution (in meters/pixel) of the DEM and additional optional raster inputs.

        # Rain variable
        self.rainLabel = Label(self, text='rain:', font='Helvetica 15 bold').grid(row=14, column=0)
        self.rainLabel2 = Label(self, text='Peak 5 minute rainfall intensity (in mm/hr).', fg='gray',justify=LEFT).grid(row=14, column=2, sticky='w')
        self.rainVar = StringVar()
        self.rainInput = Entry(self, textvariable=self.rainVar, width=5)
        self.rainInput.grid(row=14, column=1)
        self.rainOut = self.rainVar
        # Peak 5 minute rainfall intensity (in mm/hr)

        # Infil variable
        self.infilLabel = Label(self, text='infil:', font='Helvetica 15 bold').grid(row=15, column=0)
        self.infilLabel2 = Label(self, text='Effective infiltration rate (in mm/hr).', fg='gray',justify=LEFT).grid(row=15, column=2, sticky='w')
        self.infilVar = StringVar()
        self.infilInput = Entry(self, textvariable=self.infilVar, width=5)
        self.infilInput.grid(row=15, column=1)
        self.infilOut = self.infilVar
        # Effective infiltration rate (in mm/hr)
        
        # Coefficient of uniformity variable
        self.cuLabel = Label(self, text='cu:', font='Helvetica 15 bold').grid(row=16, column=0)
        self.cuLabel2 = Label(self, text='Cofficient of uniformity (unitless) of the rock armor. Not used if d50 or thickness equals 0.', fg='gray',justify=LEFT).grid(row=16, column=2, sticky='w')
        self.cuVar = StringVar()
        self.cuInput = Entry(self, textvariable=self.cuVar, width=5)
        self.cuInput.grid(row=16, column=1)
        self.cuOut = self.cuVar
        # Cofficient of uniformity (unitless) of the rock armor. Not used if d50 or thickness equals 0.
        
        # Thickness variable
        self.thicknessLabel = Label(self, text='thickness:', font='Helvetica 15 bold').grid(row=17, column=0)
        self.thicknessLabel2 = Label(self, text='The thickness of the rock armor layer in multiples of the median grain diameter.\nFor example, if d50 is 10 cm and the rock armor is 30 cm thick then this value should be 3.', fg='gray',justify=LEFT).grid(row=17, column=2, sticky='w')
        self.thicknessVar = StringVar()
        self.thicknessInput = Entry(self, textvariable=self.thicknessVar, width=5)
        self.thicknessInput.grid(row=17, column=1)
        self.thicknessOut = self.thicknessVar
        # The thickness of the rock armor layer in multiples of the median grain diameter. For example, if d50 is 10 cm and the rock armor is 30 cm thick then this value should be 3.

        # Rockcover variable
        self.rockcoverLabel = Label(self, text='rockcover:', font='Helvetica 15 bold').grid(row=18, column=0)
        self.rockcoverLabel2 = Label(self, text='This value indicates the fraction of area covered by rock armor.\nWill be 1 for continuous rock armors, less than one for partial rock cover.', fg='gray',justify=LEFT).grid(row=18, column=2, sticky='w')
        self.rockcoverVar = StringVar()
        self.rockcoverInput = Entry(self, textvariable=self.rockcoverVar, width=5)
        self.rockcoverInput.grid(row=18, column=1)
        self.rockcoverOut = self.rockcoverVar
        # This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover.
        
        # Reducedspecificgravity variable
        self.reducedspecificgravityLabel = Label(self, text='reducedspecificgravity:', font='Helvetica 15 bold').grid(row=19, column=0)
        self.reducedspecificgravityLabel2 = Label(self, text='Reduced specific gravity of the rock armor particles.\n1.65 is a reasonable default value for quartz-rich rocks.', fg='gray',justify=LEFT).grid(row=19, column=2, sticky='w')
        self.reducedspecificgravityVar = StringVar()
        self.reducedspecificgravityInput = Entry(self, textvariable=self.reducedspecificgravityVar, width=5)
        self.reducedspecificgravityInput.grid(row=19, column=1)
        self.reducedspecificgravityOut = self.reducedspecificgravityVar
        # Reduced specific gravity of the rock armor particles. 1.65 is a reasonable default value for quartz-rich rocks.

        # b variable
        self.bLabel = Label(self, text='b:', font='Helvetica 15 bold').grid(row=20, column=0)
        self.bLabel2 = Label(self, text='This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.', fg='gray',justify=LEFT).grid(row=20, column=2, sticky='w')
        self.bVar = StringVar()
        self.bInput = Entry(self, textvariable=self.bVar, width=5)
        self.bInput.grid(row=20, column=1)
        self.bOut = self.bVar
        # This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.

        # c variable
        self.cLabel = Label(self, text='c:', font='Helvetica 15 bold').grid(row=21, column=0)
        self.cuLabel2 = Label(self, text='This value is the exponent in the model component that predicts the relationship between runoff and contributing area.', fg='gray',justify=LEFT).grid(row=21, column=2, sticky='w')
        self.cVar = StringVar()
        self.cInput = Entry(self, textvariable=self.cVar, width=5)
        self.cInput.grid(row=21, column=1)
        self.cOut = self.cVar
        # This value is the exponent in the model component that predicts the relationship between runoff and contributing area. 

        # Rillwidth variable
        self.rillwidthLabel = Label(self, text='rillwidth:', font='Helvetica 15 bold').grid(row=22, column=0)
        self.rillwidthLabel2 = Label(self, text='The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.\nFor example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed,\nfor the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.', fg='gray',justify=LEFT).grid(row=22, column=2, sticky='w')
        self.rillwidthVar = StringVar()
        self.rillwidthInput = Entry(self, textvariable=self.rillwidthVar, width=5)
        self.rillwidthInput.grid(row=22, column=1)
        self.rillwidthOut = self.rillwidthVar
        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. 
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    
    def runCommand(self):
        if os.path.isfile('../input.txt'):
            os.remove('../input.txt')
        f = open('../input.txt', 'w')
        f.write(str(self.flagformaskOut.get())+'\n') 
        f.write(str(self.flagford50Out.get())+'\n')
        f.write(str(self.flagfortaucsoilandvegOut.get())+'\n')
        f.write(str(self.flagforroutingOut.get())+'\n')
        f.write(str(self.fillincrementOut.get())+'\n')
        f.write(str(self.threshslopeOut.get())+'\n')
        f.write(str(self.expansionOut.get())+'\n')
        f.write(str(self.yellowthresholdOut.get())+'\n')
        f.write(str(self.lattice_size_xOut.get())+'\n')
        f.write(str(self.lattice_size_yOut.get())+'\n')
        f.write(str(self.deltaxOut.get())+'\n')
        f.write(str(self.rainOut.get())+'\n')
        f.write(str(self.infilOut.get())+'\n')
        f.write(str(self.cuOut.get())+'\n')
        f.write(str(self.thicknessOut.get())+'\n')
        f.write(str(self.rockcoverOut.get())+'\n')
        f.write(str(self.reducedspecificgravityOut.get())+'\n')
        f.write(str(self.bOut.get())+'\n')
        f.write(str(self.cOut.get())+'\n')
        f.write(str(self.rillwidthOut.get()))
        f.close()
        subprocess.call(["gcc", "rillgen2d_local.c"])
        return True

    if runCommand:
        pass




if __name__=="__main__":
    root=tk.Tk()
    Application(root).grid()
    root.mainloop()






