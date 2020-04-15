from tkinter import *
import os.path
import subprocess

frame = Tk()

########################### MAIN TAB ###########################

AppInfoIcon = PhotoImage(file="img/AppInfoIcon.png")
AppInfoIcon =AppInfoIcon.subsample(25, 25)


introLabel = Label(text='rillgen2d', font='Helvetica 25 bold').grid(row=0, column=1)
inputLabel = Label(text='Input default or other values for use').grid(row=2, column=3)


flagformaskLabel = Label(text='flagformask:', font='Helvetica 15 bold').grid(row=4, column=1)
flagformaskLabel2 = Label(text='(Default value is 1)', fg='gray').grid(row=4, column=2)
flagformaskVar = StringVar()
flagformaskInput = Entry(textvariable=flagformaskVar, width=5)
flagformaskInput.grid(row=4, column=3)
if flagformaskVar == 1:
    flagformaskOut = 1
else:
    flagformaskOut = flagformaskVar
flagformaskInputInfo = Label(image=AppInfoIcon).grid(row=4, column=0)



flagford50Label = Label(text='flagford50:', font='Helvetica 15 bold').grid(row=5, column=1)
flagford50Label2 = Label(text='(Default value is 0)', fg='gray').grid(row = 5, column=2)
flagford50Var = StringVar()
flagford50Input = Entry(textvariable=flagford50Var, width=5)
flagford50Input.grid(row=5, column=3)
flagford50Input = flagford50Var.get()
if flagford50Var == 0:
    flagford50Out = 0
else:
    flagford50Out = flagford50Var
flagford50Info = Label(image=AppInfoIcon).grid(row=5, column=0)


flagfortaucsoilandvegLabel = Label(text='flagfortaucsoilandveg:', font='Helvetica 15 bold').grid(row=6, column=1)
flagfortaucsoilandvegLabel2 = Label(text='(Default value is 0)', fg='gray').grid(row=6, column=2)
flagfortaucsoilandvegVar = StringVar()
flagfortaucsoilandvegInput = Entry(textvariable=flagfortaucsoilandvegVar, width=5)
flagfortaucsoilandvegInput.grid(row=6, column=3)
if flagfortaucsoilandvegVar == 0:
    flagfortaucsoilandvegOut = 0
else:
    flagfortaucsoilandvegOut = flagfortaucsoilandvegVar
flagfortaucsoilandvegInfo = Label(image=AppInfoIcon).grid(row=6, column=0)

fillincrementLabel = Label(text='fillincrement:', font='Helvetica 15 bold').grid(row=7, column=1)
fillincrementLabel2 = Label(text='(Default value is 0)', fg='gray').grid(row=7, column=2)
fillincrementVar = StringVar()
fillincrementInput = Entry(textvariable=fillincrementVar, width=5)
fillincrementInput.grid(row=7, column=3)
if fillincrementVar == 0:
    fillincrementOut = 0
else:
    fillincrementOut = fillincrementVar
fillincrementInfo = Label(image=AppInfoIcon).grid(row=7, column=0)


threshslopeLabel = Label(text='threshslope:', font='Helvetica 15 bold').grid(row=8, column=1)
threshslopeLabel2 = Label(text='(Default value is 0.01)', fg='gray').grid(row=8, column=2)
threshslopeVar = StringVar()
threshslopeInput = Entry(textvariable=threshslopeVar, width=5)
threshslopeInput.grid(row=8, column=3)
if threshslopeVar == 0.01:
    threshslopeOut = 0.01
else:
    threshslopeOut = threshslopeVar
threshslopeInfo = Label(image=AppInfoIcon).grid(row=8, column=0)

expansionLabel = Label(text='expansion:', font='Helvetica 15 bold').grid(row=9, column=1)
expansionLabel2 = Label(text='(Default value is 0.02)', fg='gray').grid(row=9, column=2)
expansionVar = StringVar()
expansionInput = Entry(textvariable=expansionVar, width=5)
expansionInput.grid(row=9, column=3)
if expansionVar == 0.02:
    expansionOut = 0.02
else:
    expansionOut = expansionVar
expansionInfo = Label(image=AppInfoIcon).grid(row=9, column=0)
        
yellowthresholdLabel = Label(text='yellowthreshold:', font='Helvetica 15 bold').grid(row=10, column=1)
yellowthresholdLabel2 = Label(text=' (Default value is 5)', fg='gray').grid(row=10, column=2)
yellowthresholdVar = StringVar()
yellowthresholdInput = Entry(textvariable=yellowthresholdVar, width=5)
yellowthresholdInput.grid(row=10, column=3)
if yellowthresholdVar == 5:
    yellowthresholdOut = 5
else:
    yellowthresholdOut = yellowthresholdVar
yellowthresholdInfo = Label(image=AppInfoIcon).grid(row=10, column=0)
        
lattice_size_xLabel = Label(text='lattice_size_x:', font='Helvetica 15 bold').grid(row=11, column=1)
lattice_size_xLabel2 = Label(text='(Default value is 0.5)', fg='gray').grid(row=11, column=2)
lattice_size_xVar = StringVar()
lattice_size_xInput = Entry(textvariable=lattice_size_xVar, width=5)
lattice_size_xInput.grid(row=11, column=3)
if lattice_size_xVar == 0.5:
    lattice_size_xOut = 0.5
else:
    lattice_size_xOut = lattice_size_xVar
lattice_size_xInfo = Label(image=AppInfoIcon).grid(row=11, column=0)
        
lattice_size_yLabel = Label(text='lattice_size_y:', font='Helvetica 15 bold').grid(row=12, column=1)
lattice_size_yLabel2 = Label(text='(Default value is 3750)', fg='gray').grid(row=12, column=2)
lattice_size_yVar = StringVar()
lattice_size_yInput = Entry(textvariable=lattice_size_yVar, width=5)
lattice_size_yInput.grid(row=12, column=3)
if lattice_size_yVar == 3750:
    lattice_size_yOut = 3750
else:
    lattice_size_yOut = lattice_size_yVar
lattice_size_yInfo = Label(image=AppInfoIcon).grid(row=12, column=0)
        
deltaxLabel = Label(text='deltax:', font='Helvetica 15 bold').grid(row=13, column=1)
deltaxLabel2 = Label(text='(Default value is 2400)', fg='gray').grid(row=13, column=2)
deltaxVar = StringVar()
deltaxInput = Entry(textvariable=deltaxVar, width=5)
deltaxInput.grid(row=13, column=3)
if deltaxVar == 2400:
    deltaxOut = 2400
else:
    deltaxOut = deltaxVar
deltaxInfo = Label(image=AppInfoIcon).grid(row=13, column=0)

rainLabel = Label(text='rain:', font='Helvetica 15 bold').grid(row=14, column=1)
rainLabel2 = Label(text='(Default value is 0.5)', fg='gray').grid(row=14, column=2)
rainVar = StringVar()
rainInput = Entry(textvariable=rainVar, width=5)
rainInput.grid(row=14, column=3)
if rainVar == 0.5:
    rainOut = 0.5
else:
    rainOut = rainVar
rainInfo = Label(image=AppInfoIcon).grid(row=14, column=0)
        
infilLabel = Label(text='infil:', font='Helvetica 15 bold').grid(row=15, column=1)
infilLabel2 = Label(text='(Default value is 135)', fg='gray').grid(row=15, column=2)
infilVar = StringVar()
infilInput = Entry(textvariable=infilVar, width=5)
infilInput.grid(row=15, column=3)
if infilVar == 135:
    infilOut = 135
else:
    infilOut = infilVar
infilInfo = Label(image=AppInfoIcon).grid(row=15, column=0)
        
cuLabel = Label(text='cu:', font='Helvetica 15 bold').grid(row=16, column=1)
cuLabel2 = Label(text='(Default value is 35)', fg='gray').grid(row=16, column=2)
cuVar = StringVar()
cuInput = Entry(textvariable=cuVar, width=5)
cuInput.grid(row=16, column=3)
if cuVar == 35:
    cuOut = 35
else:
    cuOut = cuVar
cuInfo = Label(image=AppInfoIcon).grid(row=16, column=0)
        
thicknessLabel = Label(text='thickness:', font='Helvetica 15 bold').grid(row=17, column=1)
thicknessLabel2 = Label(text='(Default value is 2)', fg='gray').grid(row=17, column=2)
thicknessVar = StringVar()
thicknessInput = Entry(textvariable=thicknessVar, width=5)
thicknessInput.grid(row=17, column=3)
if thicknessVar == 2:
    thicknessOut = 2
else:
    thicknessOut = thicknessVar
thicknessInfo = Label(image=AppInfoIcon).grid(row=17, column=0)
        
rockcoverLabel = Label(text='rockcover:', font='Helvetica 15 bold').grid(row=18, column=1)
rockcoverLabel2 = Label(text='(Default value is 3)', fg='gray').grid(row=18, column=2)
rockcoverVar = StringVar()
rockcoverInput = Entry(textvariable=rockcoverVar, width=5)
rockcoverInput.grid(row=18, column=3)
if rockcoverVar == 3:
    rockcoverOut = 3
else:
    rockcoverOut = rockcoverVar
rockcoverInfo = Label(image=AppInfoIcon).grid(row=18, column=0)
        
reducedspecificgravityLabel = Label(text='reducedspecificgravity:', font='Helvetica 15 bold').grid(row=19, column=1)
reducedspecificgravityLabel2 = Label(text='(Default value is 1)', fg='gray').grid(row=19, column=2)
reducedspecificgravityVar = StringVar()
reducedspecificgravityInput = Entry(textvariable=reducedspecificgravityVar, width=5)
reducedspecificgravityInput.grid(row=19, column=3)
if reducedspecificgravityVar == 1:
    reducedspecificgravityOut = 1
else:
    reducedspecificgravityOut = reducedspecificgravityVar
reducedspecificgravityInfo = Label(image=AppInfoIcon).grid(row=19, column=0)
        
bLabel = Label(text='b:', font='Helvetica 15 bold').grid(row=20, column=1)
bLabel2 = Label(text='(Default value is 1.65)', fg='gray').grid(row=20, column=2)
bVar = StringVar()
bInput = Entry(textvariable=bVar, width=5)
bInput.grid(row=20, column=3)
if bVar == 1.65:
    bOut = 1.65
else:
    bOut = bVar
bInfo = Label(image=AppInfoIcon).grid(row=20, column=0)
        
cLabel = Label(text='c:', font='Helvetica 15 bold').grid(row=21, column=1)
cuLabel2 = Label(text='(Default value is 0.75)', fg='gray').grid(row=21, column=2)
cVar = StringVar()
cInput = Entry(textvariable=cVar, width=5)
cInput.grid(row=21, column=3)
if cVar == 0.75:
    cOut = 0.75
else:
    cOut = cVar
cInfo = Label(image=AppInfoIcon).grid(row=21, column=0)
        
rillwidthLabel = Label(text='rillwidth:', font='Helvetica 15 bold').grid(row=22, column=1)
rillwidthLabel2 = Label(text='(Default value is 1.0)', fg='gray').grid(row=22, column=2)
rillwidthVar = StringVar()
rillwidthInput = Entry(textvariable=rillwidthVar, width=5)
rillwidthInput.grid(row=22, column=3)
if rillwidthVar == 1.0:
    rillwidthOut = 1.0
else:
    rillwidthOut = rillwidthVar
rillwidthInfo = Label(image=AppInfoIcon).grid(row=22, column=0)
        
param20Label = Label(text='Parameter 20:', font='Helvetica 15 bold').grid(row=23, column=1)
param20Label2 = Label(text='(Default value is 0.2)', fg='gray').grid(row=23, column=2)
param20Var = StringVar()
param20Input = Entry(textvariable=param20Var, width=5)
param20Input.grid(row=23, column=3)
if param20Var == 0.2:
    param20Out = 0.2
else:
    param20Out = param20Var
param20Info = Label(image=AppInfoIcon).grid(row=23, column=0)
        
param21Label = Label(text='Parameter 21:', font='Helvetica 15 bold').grid(row=24, column=1)
param21Label2 = Label(text='(Default value is 100)', fg='gray').grid(row=24, column=2)
param21Var = StringVar()
param21Input = Entry(textvariable=param21Var, width=5)
param21Input.grid(row=24, column=3)
if param21Var == 100:
    param21Out = 100
else:
    param21Out = param21Var
param21Info = Label(image=AppInfoIcon).grid(row=24, column=0)
        
param22Label = Label(text='Parameter 22:', font='Helvetica 15 bold').grid(row=25, column=1)
param22Label2 = Label(text='(Default value is 10)', fg='gray').grid(row=25, column=2)
param22Var = StringVar()
param22Input = Entry(textvariable=param22Var, width=5)
param22Input.grid(row=25, column=3)
if param22Var == 10:
    param22Out = 10
else:
    param22Out = param22Var
param22Info = Label(image=AppInfoIcon).grid(row=25, column=0)


    
def runCommand():
    if os.path.isfile('input.txt'):
        os.remove('input.txt')
    f = open('input.txt', 'w')
    f.write(str(flagformaskOut.get())+'\n') 
    f.write(str(flagford50Out.get())+'\n')
    f.write(str(flagfortaucsoilandvegOut.get())+'\n')
    f.write(str(fillincrementOut.get())+'\n')
    f.write(str(threshslopeOut.get())+'\n')
    f.write(str(expansionOut.get())+'\n')
    f.write(str(yellowthresholdOut.get())+'\n')
    f.write(str(lattice_size_xOut.get())+'\n')
    f.write(str(lattice_size_yOut.get())+'\n')
    f.write(str(deltaxOut.get())+'\n')
    f.write(str(rainOut.get())+'\n')
    f.write(str(infilOut.get())+'\n')
    f.write(str(cuOut.get())+'\n')
    f.write(str(thicknessOut.get())+'\n')
    f.write(str(rockcoverOut.get())+'\n')
    f.write(str(reducedspecificgravityOut.get())+'\n')
    f.write(str(bOut.get())+'\n')
    f.write(str(cOut.get())+'\n')
    f.write(str(rillwidthOut.get())+'\n')
    f.write(str(param20Out.get())+'\n')
    f.write(str(param21Out.get())+'\n')
    f.write(str(param22Out.get()))
    f.close()
    subprocess.call(["gcc", "rillgen2d.c"])
    return True

if runCommand:
    pass

goButton = Button(text='Go', command=runCommand, padx=20)
goButton.grid(row=30, column=3)
########################### ^MAIN TAB^ ###########################

frame.title = ('RillGen2D')
frame.mainloop()