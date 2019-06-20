"""
    Script for obtaining dynamic of small neural networks
    Here we proceed to the rendering of the function: output(X1,X2) for X1 activator and X2 inhibitor (killer template)
    Equations are solved in parallel on the CPU

"""
import numpy as np
import os
from simulOfBioNN.parseUtils.parser import generateNeuralNetwork,generateTemplateNeuralNetwork,read_file
from simulOfBioNN.simulNN.simulator import executeSimulation
from simulOfBioNN.odeUtils.systemEquation import f
from simulOfBioNN.odeUtils.utils import readAttribute,obtainTemplateArray,obtainOutputArray
from simulOfBioNN.plotUtils.adaptivePlotUtils import colorDiagram,neuronPlot,plotEvolution
import sys

if __name__ == '__main__':

    name = "templateProtectedModel/activationSimulation_D4"
    endTime = 10000
    timeStep = 0.1
    masks = np.array([np.array([[1,-1]])])
    modes = ["verbose","outputPlot"]
    outputMode = "all"
    complexity="simple"
    useEndo = False  # if we want to use the complicated endo model
    useProtectionOnActivator = True
    #generate other layer concentration, for initialization:
    leak=10**(-13)
    layerInit = leak
    enzymeInit = 10**(-6)
    endoInit = 10**(-5)
    activInit =  10**(-6)
    inhibInit =  10**(-8)

    if useEndo:
        generateTemplateNeuralNetwork(name,masks,complexity=complexity,useProtectionOnActivator=useProtectionOnActivator)
    else:
        generateTemplateNeuralNetwork(name,masks,complexity=complexity,endoConstants=None,useProtectionOnActivator=useProtectionOnActivator)
    FULL = False

    #generate the first layer concentration:
    if(FULL):
        X1 = np.arange(10**(-7),10**(-5),10**(-7))
        X1 = np.concatenate((X1,np.arange( 10 ** (-5), 0.8*10 ** (-4), 10 ** (-6))))
        #X2=np.arange( 10 ** (-8), 10 ** (-6), 10 ** (-8))
        X2 = X1
    else:
        X1 = np.array([10**(-7),10**(-4)])
        X2 = np.array([10**(-7)])

    # generate concentration for all different experiments:
    x_test=[]
    for x1 in X1:
        for x2 in X2:
            x_test+=[[x1,x2]]
    x_test = np.array(x_test)


    # If we scale down the concentration of inhibiting template:
    # There is no need to differentiate concentration of input species.

    initialization_dic={}
    for layer in range(0,len(masks)): ## the first layer need not to be initiliazed
        for node in range(masks[layer].shape[0]):
            initialization_dic["X_"+str(layer+1)+"_"+str(node)] = layerInit
    inhibTemplateNames = obtainTemplateArray(masks=masks,activ=False)
    for k in inhibTemplateNames:
        initialization_dic[k] = inhibInit
    activTemplateNames = obtainTemplateArray(masks=masks,activ=True)
    for k in activTemplateNames:
        initialization_dic[k] = activInit
    initialization_dic["E"] = enzymeInit
    if complexity!="simple":
        initialization_dic["E2"] = enzymeInit
    if complexity!=None and useEndo:
        initialization_dic["Endo"] = endoInit

    outputList = "all"
    results = executeSimulation(f, name, x_test, initialization_dic, outputList= outputList, leak = leak, endTime=endTime,sparse=False, modes=modes, timeStep=0.1)

    if("outputPlot" in modes):
        shapeP = len(X1)*len(X2)
        nameDic = results[-1]
        X = results[modes.index("outputPlot")]
        myname=os.path.join(sys.path[0],name)
        if(outputMode=="all"):
            if outputList is None or type(outputList)==str:
                outputList = list(nameDic.keys())
        else:
            outputList = obtainOutputArray(nameDic)
        specialnameDic ={}
        for idx2,e in enumerate(outputList):
            specialnameDic[e] = idx2
        for e in range(X.shape[1]):
            displayX = np.moveaxis(X[:,e,:],0,1)
            plotEvolution(np.arange(0,endTime,timeStep),os.path.join(myname,str(e)), specialnameDic, displayX, wishToDisp=outputList, displaySeparate=True, displayOther=True)

    if("outputEqui" in modes):
        experiment_path = name
        C0=readAttribute(experiment_path,["C0"])["C0"]
        rescaleFactor = readAttribute(experiment_path,["rescaleFactor"])["rescaleFactor"]
        output = results[modes.index("outputEqui")]
        output = np.reshape(output,(len(X1),len(X2)))
        X1 = X1/(C0*rescaleFactor)
        X2 = X2/(C0*rescaleFactor)
        colorDiagram(X1,X2,output,"Initial concentration of X1","Initial concentration of X2","Equilibrium concentration of the output",figname=os.path.join(experiment_path, "neuralDiagramm.png"),equiPotential=False)
        neuronPlot(X1,X2,output,figname=os.path.join(experiment_path, "activationX1.png"),figname2=os.path.join(experiment_path, "activationX2.png"))