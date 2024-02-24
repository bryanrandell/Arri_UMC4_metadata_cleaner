###ms_ARRI_META_EXTRACT V003
###Extract arri metadata from CSV file or Read node

import nuke
from subprocess import call
from os import path, environ, listdir
from csv import reader, writer, DictReader
from re import search, sub
from itertools import islice

def getSensor():
    thisNode = nuke.thisNode()
    thisKnob = nuke.thisKnob()
    try:
        selSensor = allSensorDicts[thisNode['camMode'].value()]
        sensorW = float(selSensor.split('x')[0])
        ###print "Sensor Width: %s" % sensorW
        sensorH = float(selSensor.split('x')[1])
        ###print "Sensor Height: %s" % sensorH
        thisNode['sensor'].setValue(sensorW, 0)
        thisNode['sensor'].setValue(sensorH, 1)
    except: pass

arriCams = []
xtSensorDict = {'Alexa XT/16:9/HD(1920x1080)':'23.76x13.37', 'Alexa XT/16:9/2K(2048x1152)':'23.66x13.32', 'Alexa XT/16:9/3.2K(3164x1778)':'26.14x14.70', 'Alexa XT/16:9/2.8K(2880x1620)':'23.76x13.37', 'Alexa XT/4:3/2K(2048x1536)':'23.66x17.75', 'Alexa XT/4:3/Cropped(2578x2160)':'21.27x17.82', 'Alexa XT/4:3/Full(2880x2160)':'23.76x17.82', 'Alexa XT/OpenGate/3414x2198':'28.25x18.17'}

sxtSensorDict = {'Alexa SXT/16:9/HD(1920x1080)':'23.76x13.37', 'Alexa SXT/16:9/2K(2048x1152)':'23.76x13.37', 'Alexa SXT/16:9/3.2K(3200x1800)':'26.40x14.85', 'Alexa SXT/16:9/4K UHD(3840x2160)':'26.40x14.85', 'Alexa SXT/16:9/2.8K(2880x1620)':'23.76x13.37', 'Alexa SXT/16:9/3.2K(3168x1782)':'26.14x14.70', 'Alexa SXT/4:3/2.8K(2880x2160)':'23.76x17.82', 'Alexa SXT/6:5/2K Anamorphic(2048x858)':'21.12x17.70', 'Alexa SXT/6:5/4K Cine Anamorphic(4096x1716)':'21.12x17.70', 'Alexa SXT/6:5/2.6K(2578x2160)':'21.38x17.82', 'Alexa SXT/OpenGate/3.4K(3424x2202)':'28.25x18.17','Alexa SXT/OpenGate/4K Cine(4096x2636)':'28.17x18.13'}

miniSensorDict = {'Alexa Mini/16:9/S16 HD(1920x1080)':'13.32x7.425', 'Alexa Mini/16:9/HD(1920x1080)':'23.76x13.37', 'Alexa Mini/16:9/HD Anamorphic(1920x1080)':'15.84x17.82', 'Alexa Mini/16:9/2K(2048x1152)':'23.6613.30', 'Alexa Mini/2:39:1/2K Anamorphic(2048x858)':'21.12x17.70', 'Alexa Mini/4:3/2.8K(2880x2160)':'23.76x17.82', 'Alexa Mini/16:9/3.2K(3200x1800)':'26.40x14.85', 'Alexa Mini/16:9/4K UHD(3840x2160)':'26.40x14.85', 'Alexa Mini/16:9/HD Ana.(OG 3.4K)(1920x2160)':'15.84x17.82', 'Alexa Mini/2:39:1/2K Ana.(OG 3.4K)(2560x2145)':'21.12x17.70', 'Alexa Mini/16:9/2.8K(2880x1620)':'23.76x17.82', 'Alexa Mini/4:3/2.8K(OG 3.4K)(2880x2160)':'23.76x17.82', 'Alexa Mini/OpenGate/3.4K(3424x2202)':'28.25x18.17'}

sixtyFiveSensorDict = {'Alexa 65/OpenGate/6560x3100':'54.12x25.58', 'Alexa 65/16:9/5120x2880':'42.24x23.76', 'Alexa 65/3:2/4320x2880':'35.64x23.76'}

allSensorDicts = {"":"0x0"}
allSensorDicts.update(xtSensorDict)
allSensorDicts.update(sxtSensorDict)
allSensorDicts.update(miniSensorDict)
allSensorDicts.update(sixtyFiveSensorDict)
arriCams.append('')
for s in allSensorDicts:
    arriCams.append(s)

def nodeRename(oldName):
    i= 1
    while True:
        if nuke.exists(oldName + str(i)) == False:
            return oldName + str(i)
        ###print "Found Duplicate Name..Renaming..."
        i+=1

def linear_iris_to_aperture(LensLinIris):
    n = (LensLinIris + 50) / 1000.0
    n = int((LensLinIris + 50) / 1000.0) 
    n = n-1
    full_aperture = pow(2, n/2.0)
    return full_aperture

    
def lookForMetaPrefix(node, prefix):
    for i in node.metadata():
            if prefix in i:
                ###print "Yes, Found %s in %s" % (prefix, i)
                return True

def matchMetaPrefix(node, prefix1, prefix2=None):
    match = None
    for l in node.metadata():
        try:
            if prefix1 in l.lower():
                ###print "Matched %s to %s"% (prefix1, l)
                match = l
        except:
            match = None
        if match == None:
            try:
                if prefix2 in l.lower():
                    ###print "Matched %s to %s"% (prefix2, l)
                    match = l
            except:
                match = None
    ###print "match= %s"% match
    return match

def sliceFileName(fileName, fileExt=None):
    if fileName[-1].isdigit() == True:
        frange =  path.splitext(fileName)[-1].lstrip(fileExt)
        ###print "File is a sequence"
        ###print "File FrameRange: %s" % frange
        fileName = fileName.split(frange, -1)[0]
        ###print "File name: %s"% fileName
        fileExt = path.splitext(fileName)[1]
        ###print "File extension: %s"% fileExt
        fileNameWithPadding = fileName.rstrip(fileExt)
        ###print "File name with padding: %s"% fileNameWithPadding
        m = search('(.%+\d+d)|(.#+)|(.%d)', fileNameWithPadding)
        padding = m.group() if m else None
        ###print "Padding: %s"% padding      
    else:
        ###print "File is not a sequence"
        ###print "File name: %s"% fileName
        fileExt = path.splitext(fileName)[1]
        ###print "File extension: %s"% fileExt
        fileNameWithPadding = fileName.rstrip(fileExt)
        ###print "File name with padding: %s"% fileNameWithPadding
        padding = path.splitext(fileNameWithPadding)[1]
        ###print "Padding: %s"% padding

    fileNameOnly = fileNameWithPadding.rstrip(padding)
    ###print "File Name Only: " + fileNameOnly
    return fileName, fileNameOnly, fileExt, padding
    
def scanDir(filePath):
    dir = listdir(filePath)
    movList = []
    mxfList = []
    for d in dir:
        if d.endswith('.mov'):
            movList.append(d)
        elif d.endswith('.mxf'):
            mxfList.append(d)
        else:
            pass
    movCount = len(movList)
    mxfCount = len(mxfList)
    if movCount > 1:
        foundMultiple = True
        ext = "quicktime"
        ###print "Found %s quicktime files in the directory" % movCount
    elif mxfCount > 1:
        foundMultiple = True
        ext = "mxf"
        ###print "Found %s mxf files in the directory" % mxfCount
    else:
        foundMultiple = False
        ext = ""
    return foundMultiple, ext
  
txtColor = "<b><span style=\"color:#0087B6;\"> "
           
def ms_Arri_metadata_extract_CSV(csv_path, FPS, csvFrame, synchData, node=None):
    with open(csv_path, 'rb') as csvfile:
        metareader = reader(csvfile, delimiter='\t')
        rowClipName = next(islice(metareader, 1, 1+1))
        if rowClipName[14] == "":
            nuke.message("Did not find ARRI data in CSV")
            print "Did not find ARRI data in CSV, Exiting..."
            return
        else:
            print "Found ARRI data in CSV"
    if synchData == False:
        with open(csv_path, 'rb') as csvfile:
            metareader = DictReader(csvfile, delimiter='\t')
            rowCount = sum(1 for row in metareader)-1
            #ret = nuke.getFramesAndViews('Extract Alexa Metadata', '%s-%s' %(0, rowCount))
            #frameRange = nuke.FrameRange(ret[0])
            
    else:
        first = node['first'].value()
        last = node['last'].value()
        tcFirst = node.metadata('input/timecode', first)
        ###print "Read TC in: " + tcFirst
        tcLast = node.metadata('input/timecode', last)
        ###print "Read TC out: " + tcLast
        with open(csv_path, 'rb') as csvfile:
            metareader = reader(csvfile, delimiter='\t')
            tcMatches = []
            for row in metareader:
                if not len(row[0]) < 2:
                    if row[1] == tcFirst:
                        ###print "CSV TC in: " + row[1] 
                        inIndex = row[0]
                        inTC = row[1]
                        tcMatches.append(row[1])
                        ###print "Index in is: " + inIndex
                    elif row[1] == tcLast:
                        ###print "CSV TC out: " + row[1] 
                        outIndex = row[0]
                        outTC = row[1]
                        tcMatches.append(row[1])
                        ###print "Index out is: " + outIndex             
                else:
                    nuke.message("This doesnt look like an Arri source")
                    return
            csvfile.close()
            ###print "Timecode matches: %s" % tcMatches
            if len(tcMatches) == 2:
                tOffset = int(inIndex)-int(first)
            else:
                nuke.message("Could not synch Timecode")
                return
    
    #Access static values in csv and put them in a list for later access 
    with open(csv_path, 'rb') as csvfile:
        metareader = DictReader(csvfile, delimiter='\t')
        for row in metareader:
            clipName = row.get('Camera Clip Name')
            ldsLagType = row.get('Lds Lag Type')
            if ldsLagType == str(0):
                ldsLagType = "None"
            elif ldsLagType == str(1):
                ldsLagType = "Constant"
            else:
                ldsLagType = "Not Available"
            ldsLagVal = row.get('Lds Lag Value')        
            frmLine1 = row.get('Frame Line File 1')
            frmLine2 = row.get('Frame Line File 2')
            camModel = row.get('Camera Model')
            expTime = row.get('Exposure Time')
            shutAngle = row.get('Shutter Angle')
            senFPS = row.get('Sensor FPS')
            projFPS = row.get('Project FPS')
            camResW = row.get('Image Width')
            camResH = row.get('Image Height')
            res = ((camResW) + ('x') + (camResH))
            wb = row.get('White Balance')
            nd = row.get('ND Filter Type')
            ndd = row.get('ND Filter Density')
            asa = row.get('Exposure Index ASA')
            colorSpace = row.get('Target Color Space')
            lensSqu = row.get('Lens Squeeze')
            lensModel = row.get('Lens Model')
            lensSerial = row.get('Lens Serial Number')
            lensUnit = row.get('Lens Distance Unit')
            lensIris = row.get('Lens Iris')
            lensLinIris = row.get('Lens Linear Iris')

    #Create Arri_Metadata Node and assign the metadata
    arriMetaNode = nuke.createNode('NoOp')   
    nodeName = ("Arri_Metadata")
    nodeName = nodeRename(nodeName)
    ###print "Node renamed to: %s" % nodeName
    arriMetaNode['name'].setValue(nodeName)
    arriMetaNode.knob('name').setValue(nodeName)
    arriMetaNode.addKnob(nuke.Tab_Knob(clipName))
    arriMetaNode['label'].setValue("Source Clip: %s"% clipName)
      
    arriMetaNode.addKnob(nuke.Tab_Knob('timeGroup', 'Time', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Double_Knob('index', txtColor + 'CSV Index'))
    arriMetaNode['index'].setAnimated()
    if synchData == True:
        arriMetaNode.addKnob(nuke.Text_Knob('inTC', txtColor + 'Start Timecode:', inTC))
        arriMetaNode.addKnob(nuke.Text_Knob('outTC', txtColor + 'End Timecode:', outTC))
    arriMetaNode.addKnob(nuke.Text_Knob('ldsLagType', txtColor + 'LDS Lag Type:', ldsLagType))
    if ldsLagVal not in [None, 'Inactive', '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('ldsLagVal', txtColor + 'LDS Lag Value:', str(ldsLagVal) + " frame"))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('ldsLagVal', txtColor + 'LDS Lag Value:', "Not Available"))
    arriMetaNode.knob('ldsLagVal').setTooltip('''Specifies the lag of the calibrated LDS values FocusDistance,FocalLength and Iris in frames. A value of +1 means the values have one frame delay (as it is in Alexa FW since 7.0). Thus the correct calibrated LDS values are found in the next frame. For AMIRA SUP 1.1 the lag value is constant 14 frames off for LDS and ENG zoom lenses.''')
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))
    
    arriMetaNode.addKnob(nuke.Tab_Knob('framing', 'Framing', nuke.TABBEGINGROUP))
    if frmLine1 not in [None, 'Inactive', '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('frmLine1', txtColor + 'Frame Line 1:', frmLine1))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('frmLine1', txtColor + 'Frame Line 1:', "Not Available"))
    if frmLine2 not in [None, 'Inactive', '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('frmLine2', txtColor + 'Frame Line 2:', frmLine2))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('frmLine2', txtColor + 'Frame Line 2:', "Not Available"))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))

    arriMetaNode.addKnob(nuke.Tab_Knob('camGroup', 'Camera', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Text_Knob('camModel', txtColor + 'Camera Model:', camModel))
    arriMetaNode.addKnob(nuke.Text_Knob('camRes', txtColor + 'Resolution:', res))
    arriCamsPulldown = nuke.CascadingEnumeration_Knob('camMode', txtColor + 'Sensor Presets', arriCams)
    arriMetaNode.addKnob(arriCamsPulldown)
    sensorKnob = nuke.XY_Knob('sensor', txtColor + 'Sensor Size(mm)')
    sensorKnob.setFlag(0x00008000)
    arriMetaNode.addKnob(sensorKnob)
    nuke.addKnobChanged(getSensor, nodeClass="NoOp")
    nuke.removeKnobChanged(getSensor)
    arriMetaNode.addKnob(nuke.Text_Knob('senFPS', txtColor + 'Sensor FPS:', senFPS))
    arriMetaNode.addKnob(nuke.Text_Knob('projFPS', txtColor + 'Project FPS:', projFPS))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))

    arriMetaNode.addKnob(nuke.Tab_Knob('expGroup', 'Exposure/Color', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Text_Knob('expTime', txtColor + 'Exposure Time:', expTime))
    arriMetaNode.addKnob(nuke.Text_Knob('shutAngle', txtColor + 'Shutter Angle:', shutAngle))
    arriMetaNode.addKnob(nuke.Text_Knob('asa', txtColor + 'Exposure Index ASA:', asa))
    arriMetaNode.addKnob(nuke.Text_Knob('colorSpace', txtColor + 'Taregt Color Space:', colorSpace))
    arriMetaNode.addKnob(nuke.Text_Knob('wb', txtColor + 'White Balance:', wb))
    if nd not in [None, 'Inactive', '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('nd', txtColor + 'ND Filter:', nd))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('nd', txtColor + 'ND Filter:', "Not Available"))
    if ndd not in [None, 'Inactive', '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('ndd', txtColor + 'ND Filter Density:', ndd))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('ndd', txtColor + 'ND Filter Density:', "Not Available"))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))

    arriMetaNode.addKnob(nuke.Tab_Knob('ldsGroup', 'LDS', nuke.TABBEGINGROUP))

    if row.get('Lens Model') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('lensModel', txtColor + 'Lens Model:', lensModel))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensModel', txtColor + 'Lens Model:', "Not Available"))
    if row.get('Lens Squeeze') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('lensSqu', txtColor + 'Lens Squeeze:', lensSqu))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensSqu', txtColor + 'Lens Squeeze:', "Not Available"))
    if row.get('Lens Model') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('lensSerial', txtColor + 'Serial Number:', lensSerial))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensSerial', txtColor + 'Serial Number:', "Not Available"))
    if row.get('Lens Distance Unit') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('lensUnit', txtColor + 'Distance Unit:', lensUnit))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensUnit', txtColor + 'Distance Unit:', "Not Available"))
    if row.get('Lens Focus Distance') not in [None, '-', '--', '']:
        arriMetaNode.addKnob(nuke.Double_Knob('focusD', txtColor + 'Focus Distance'))
        arriMetaNode['focusD'].setAnimated()
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('focusD', txtColor + 'Focus Distance:', "Not Available"))
    if row.get('Lens Focal Length') not in [None, '-', '--', '', '0']:
        arriMetaNode.addKnob(nuke.Double_Knob('focal', txtColor + 'Focal Length(mm)'))
        arriMetaNode['focal'].setAnimated()
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('focal', txtColor + 'Focal Length(mm):', "Not Available"))
    if row.get('Lens Iris') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Text_Knob('lensIris', txtColor + 'Iris:', lensIris))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensIris', txtColor + 'Iris:', "Not Available"))
    if row.get('Lens Linear Iris') not in [None, '--', '']:
        LenslinIris = row.get('Lens Linear Iris')
        arriMetaNode.addKnob(nuke.Text_Knob('lensLinIris', txtColor + 'Linear Iris:', lensLinIris))
        fstop = linear_iris_to_aperture(int(LenslinIris))
        arriMetaNode.addKnob(nuke.Text_Knob('fstop', txtColor + 'aperture/fstop:', str(round(fstop, 1))))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensLinIris', txtColor + 'Linear Iris:', "Not Available"))
        arriMetaNode.addKnob(nuke.Text_Knob('fstop', txtColor + 'aperture/fstop:', "Not Available"))
    if row.get('Camera Tilt') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Double_Knob('tilt', txtColor + 'Camera Tilt'))
        arriMetaNode['tilt'].setAnimated()
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('tilt', txtColor + 'Camera Tilt:', "Not Available"))
    if row.get('Camera Roll') not in [None, '--', '']:
        arriMetaNode.addKnob(nuke.Double_Knob('roll', txtColor + 'Camera Roll'))
        arriMetaNode['roll'].setAnimated()
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('roll', txtColor + 'Camera Roll:', "Not Available"))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))
        
    #export_Divider = nuke.Text_Knob("")
    #Tool.addKnob(export_Divider)
    #createCam = nuke.PyScript_Knob('createCam', 'Create Camera', 'createCam()' )
    #Tool.addKnob(createCam)
  
    if synchData == False:
    
        #Loop over csv file for animated values and assign them to the Arri Metadata node
        with open(csv_path, 'rb') as csvfile:
            metareader = DictReader(csvfile, delimiter='\t')
            task = nuke.ProgressTask('Baking meta data from CSV file')
                   
            for index, row in enumerate(metareader):
                if task.isCancelled():
                    break
                    nuke.executeInMainThread(nuke.message,args=('Aborted',))
                csvFrame = 0        
                frame = int(csvFrame) + index
                index = float(row['Index'])
                count = len(str(index))
                prog = 100.0/count
                task.setProgress(int(count*prog))
                task.setMessage(str(index))
                arriMetaNode['index'].setValueAt(index, frame)
                if row.get('Lens Focus Distance') not in [None, '-', '--', '']:
                    focalPoint = float(row.get('Lens Focus Distance'))
                    arriMetaNode['focusD'].setValueAt(focalPoint, frame)
                if row.get('Lens Focal Length') not in [None, '-', '--', '', '0']:
                    focalLength = float(row.get('Lens Focal Length'))
                    arriMetaNode['focal'].setValueAt(focalLength, frame)
                if row.get('Camera Tilt') not in [None, '--', '']:
                    tilt = float(row.get('Camera Tilt'))
                    arriMetaNode['tilt'].setValueAt(tilt, frame)
                if row.get('Camera Roll') not in [None, '--', '']:
                    roll = float(row.get('Camera Roll'))
                    arriMetaNode['roll'].setValueAt(roll, frame)


    else:
        with open(csv_path, 'rb') as csvfile:
            metareader = DictReader(csvfile, delimiter='\t')
            task = nuke.ProgressTask('Baking meta data from CSV file')
            for row in islice(metareader, int(inIndex), int(outIndex)+1):
                if task.isCancelled():
                    break
                    nuke.executeInMainThread(nuke.message,args=('Aborted',))
                index = float(row['Index'])
                frame = float(str(int(index)-int(tOffset)))
                count = len(str(frame))
                prog = 100.0/count
                task.setProgress(int(count*prog))
                task.setMessage(str(frame))

                arriMetaNode['index'].setValueAt(index, frame)
                if row.get('Lens Focus Distance') not in [None, '--', '']:
                    focalPoint = float(row.get('Lens Focus Distance'))
                    arriMetaNode['focusD'].setValueAt(focalPoint, frame)
                if row.get('Lens Focal Length') not in [None, '-', '--', '', '0']:
                    focalLength = float(row.get('Lens Focal Length'))
                    arriMetaNode['focal'].setValueAt(focalLength, frame)
                if row.get('Camera Tilt') not in [None, '--', '']:
                    tilt = float(row.get('Camera Tilt'))
                    arriMetaNode['tilt'].setValueAt(tilt, frame)
                if row.get('Camera Roll') not in [None, '--', '']:
                    roll = float(row.get('Camera Roll'))
                    arriMetaNode['roll'].setValueAt(roll, frame)
                    
def ms_Arri_metadata_extract_fromRead(node):
    first = node['first'].value()
    last = node['last'].value()
    clipName = node.metadata(matchMetaPrefix(node, "cameraclip".lower()))
    try:
        frmLine1 = node.metadata(matchMetaPrefix(node, "frmLnFilename1".lower(), "FramelineFileName1".lower()))
    except:
        frmLine1 = "Not Available"
    try:
        frmLine2 = node.metadata(matchMetaPrefix(node, "frmLnFilename2".lower(), "FramelineFileName2".lower()))
    except:
        frmLine2 = "Not Available"
    try:
        camModel = node.metadata(matchMetaPrefix(node, "cameramodel".lower()))
    except:
        camModel = "Not Available"
    try:
        expTime = node.metadata(matchMetaPrefix(node, "exposure_time".lower(), "ExposureTime".lower()))
    except:
        expTime = "Not Available"
    try:
        shutAngle = node.metadata(matchMetaPrefix(node, "shutter".lower()))
    except:
        shutAngle = "Not Available"
    try:
        senFPS = node.metadata(matchMetaPrefix(node, "sensorfps".lower(), 'capturerate'.lower()))
    except:
        senFPS = "Not Available"
    try:
        projFPS = node.metadata(matchMetaPrefix(node, "projectfps".lower(), "timebase".lower()))
    except:
        projFPS = "Not Available"
    try:
        camResW = node.metadata(matchMetaPrefix(node, "input/width".lower()))
    except:
        camResW = "Not Available"
    try:
        camResH = node.metadata(matchMetaPrefix(node, "input/height".lower()))
    except:
        camResH = "Not Available"
    if "Not Available" not in ['camResW', 'camResH']:
        res = (str(camResW) + ('x') + str(camResH))
    else:
        res = "Not Available"
    try:
        wb = node.metadata(matchMetaPrefix(node, "kelvin".lower()))
    except:
        wb = "Not Available"
    try:
        nd = node.metadata(matchMetaPrefix(node, "ndfilter".lower(), "nr.applied".lower()))
    except:
        nd = "Not Available"
    try:
        ndd = node.metadata(matchMetaPrefix(node, "ndfilterdensity".lower(), "nr.strength".lower()))
    except:
        ndd = "Not Available"
    try:
        asa = node.metadata(matchMetaPrefix(node, "asa".lower(), "iso".lower()))
    except:
        asa = "Not Available"            
    try:
        colorSpace = node.metadata(matchMetaPrefix(node, "colorgamma".lower()))
    except:
        colorSpace = "Not Available"
    try:
        lensSqu = node.metadata(matchMetaPrefix(node, "pixelAspect".lower()))
    except:
        lensSqu = "Not Available"
    try:
        lensModel = node.metadata(matchMetaPrefix(node, "lenstype".lower()))
    except:
        lensModel = "Not Available"
    try:
        lensSerial = node.metadata(matchMetaPrefix(node, "lensserial".lower()))
    except:
        lensSerial = "Not Available"
    try:
        lensUnit = node.metadata(matchMetaPrefix(node, "unit".lower()))
    except:
        lensUnit = "Not Available"
    try:
        lensIris = node.metadata(matchMetaPrefix(node, "lensiris".lower()))
    except:
        lensIris = "Not Available"
    try:
        lensLinIris = node.metadata(matchMetaPrefix(node, "lineariris".lower()))
    except:
        lensLinIris = "Not Available"

    arriMetaNode = nuke.createNode('NoOp')   
    nodeName = ("Arri_Metadata")
    nodeName = nodeRename(nodeName)
    ###print "Node renamed to: %s" % nodeName
    arriMetaNode['name'].setValue(nodeName)
    arriMetaNode.knob('name').setValue(nodeName)
    arriMetaNode.addKnob(nuke.Tab_Knob(clipName))
    arriMetaNode['label'].setValue("Source Clip: %s"% clipName)
    
    arriMetaNode.addKnob(nuke.Tab_Knob('framing', 'Framing', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Text_Knob('frmLine1', txtColor + 'Frame Line 1:', frmLine1))
    arriMetaNode.addKnob(nuke.Text_Knob('frmLine2', txtColor + 'Frame Line 2:', frmLine2))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))
    
    arriMetaNode.addKnob(nuke.Tab_Knob('camGroup', 'Camera', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Text_Knob('camModel', txtColor + 'Camera Model:', camModel))
    arriMetaNode.addKnob(nuke.Text_Knob('camRes', txtColor + 'Resolution:', res))
    arriCamsPulldown = nuke.CascadingEnumeration_Knob('camMode', txtColor + 'Sensor Presets', arriCams)
    arriMetaNode.addKnob(arriCamsPulldown)
    sensorKnob = nuke.XY_Knob('sensor', txtColor + 'Sensor Size(mm)')
    sensorKnob.setFlag(0x00008000)
    arriMetaNode.addKnob(sensorKnob)
    nuke.addKnobChanged(getSensor, nodeClass="NoOp")
    nuke.removeKnobChanged(getSensor)
    arriMetaNode.addKnob(nuke.Text_Knob('senFPS', txtColor + 'Sensor FPS:', str(senFPS)))
    arriMetaNode.addKnob(nuke.Text_Knob('projFPS', txtColor + 'Project FPS:', str(projFPS)))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))

    arriMetaNode.addKnob(nuke.Tab_Knob('expGroup', 'Exposure/Color', nuke.TABBEGINGROUP))
    arriMetaNode.addKnob(nuke.Text_Knob('expTime', txtColor + 'Exposure Time:', str(expTime)))
    arriMetaNode.addKnob(nuke.Text_Knob('shutAngle', txtColor + 'Shutter Angle:', str(shutAngle)))
    arriMetaNode.addKnob(nuke.Text_Knob('asa', txtColor + 'Exposure Index ASA:', str(asa)))
    arriMetaNode.addKnob(nuke.Text_Knob('colorSpace', txtColor + 'Taregt Color Space:', colorSpace))
    arriMetaNode.addKnob(nuke.Text_Knob('wb', txtColor + 'White Balance:', str(wb)))
    arriMetaNode.addKnob(nuke.Text_Knob('nd', txtColor + 'ND Filter:', str(nd)))
    arriMetaNode.addKnob(nuke.Text_Knob('ndd', txtColor + 'ND Filter Density:', str(ndd)))
    arriMetaNode.addKnob(nuke.Tab_Knob('', '', nuke.TABENDGROUP))

    arriMetaNode.addKnob(nuke.Tab_Knob('ldsGroup', 'LDS', nuke.TABBEGINGROUP))
    animMeta = []
    if lensModel not in [None, '--', '', "Not Available"]:
        arriMetaNode.addKnob(nuke.Text_Knob('lensModel', txtColor + 'Lens Model:', lensModel))
        arriMetaNode.addKnob(nuke.Text_Knob('lensSerial', txtColor + 'Serial Number:', str(lensSerial)))
    else:
        pass
    if lensSqu not in [None, '--', '', "Not Available"]:
        arriMetaNode.addKnob(nuke.Text_Knob('lensSqu', txtColor + 'Lens Squeeze:', str(lensSqu)))
    else:
        pass
    if lensUnit not in [None, '--', '', "Not Available"]:
        arriMetaNode.addKnob(nuke.Text_Knob('lensUnit', txtColor + 'Distance Unit:', lensUnit))
    else:
        pass
    try:
        focus = node.metadata(matchMetaPrefix(node, "exr/focus".lower(), "focusdistance".lower()))
        if isinstance(focus, float) == True:
            ###print "Found Focus Distance"
            arriMetaNode.addKnob(nuke.Double_Knob('focusD', txtColor + 'Focus Distance'))
            arriMetaNode['focusD'].setAnimated()
            animMeta.append('focus')
        else:
            ###print "Did not find Focus Distance"
            arriMetaNode.addKnob(nuke.Text_Knob('focusD', txtColor + 'Focus Distance:', "Not Available"))
    except:
        ###print "Did not find Focus"
        arriMetaNode.addKnob(nuke.Text_Knob('focusD', txtColor + 'Focus Distance:', "Not Available"))
    ###print "%s is: %s" % ("Focus", arriMetaNode['focusD'].value())
    try:
        focal =  node.metadata(matchMetaPrefix(node, "focal".lower()))
        if isinstance(focal, float) == True:
            ###print "Found Focal Length"
            arriMetaNode.addKnob(nuke.Double_Knob('focal', txtColor + 'Focal Length(mm)'))
            arriMetaNode['focal'].setAnimated()
            animMeta.append('focal')
        else:
            ###print "Did not find Focal Length"
            arriMetaNode.addKnob(nuke.Text_Knob('focal', txtColor + 'Focal Length(mm):', "Not Available"))
    except:
        arriMetaNode.addKnob(nuke.Text_Knob('focal', txtColor + 'Focal Length(mm):', "Not Available"))
    ###print "%s is: %s" % ("Focal", arriMetaNode['focal'].value())
    if lensIris not in [None, '--', '', "Not Available"]:
        arriMetaNode.addKnob(nuke.Text_Knob('lensIris', txtColor + 'Iris:', str(lensIris)))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensIris', txtColor + 'Iris:', "Not Available"))
    if lensLinIris not in [None, '--', '', "Not Available"]:
        if "." in str(lensLinIris):
            ###print "Found Dot in LinearIris"
            lensLinIris = int(str(round(lensLinIris, 3)).replace(".", ""))
        arriMetaNode.addKnob(nuke.Text_Knob('lensIris', txtColor + 'Linear Iris:', str(lensLinIris)))
        fstop = linear_iris_to_aperture(lensLinIris)
        arriMetaNode.addKnob(nuke.Text_Knob('fstop', txtColor + 'aperture/fstop:', str(round(fstop,1))))
    else:
        arriMetaNode.addKnob(nuke.Text_Knob('lensLinIris', txtColor + 'Linear Iris:', "Not Available"))
        arriMetaNode.addKnob(nuke.Text_Knob('fstop', txtColor + 'aperture/fstop:', "Not Available"))
    try:
        tilt = node.metadata(matchMetaPrefix(node, "tilt".lower()))
        if isinstance(tilt, float) == True:
            ###print "Found Tilt"
            arriMetaNode.addKnob(nuke.Double_Knob('tilt', txtColor + 'Camera Tilt'))
            arriMetaNode['tilt'].setAnimated()
            animMeta.append('tilt')
        else:
            ###print "Did not find Tilt"
            arriMetaNode.addKnob(nuke.Text_Knob('tilt', txtColor + 'Camera Tilt:', "Not Available"))
    except:
        arriMetaNode.addKnob(nuke.Text_Knob('tilt', txtColor + 'Camera Tilt:', "Not Available"))
    try:
        roll = node.metadata(matchMetaPrefix(node, "roll".lower()))
        if isinstance(roll, float) == True:
            ###print "Found Roll"
            arriMetaNode.addKnob(nuke.Double_Knob('roll', txtColor + 'Camera Roll'))
            arriMetaNode['roll'].setAnimated()
            animMeta.append('roll')
        else:
            ###print "Did not find Roll"
            arriMetaNode.addKnob(nuke.Text_Knob('roll', txtColor + 'Camera Roll:', "Not Available"))
    except:
        arriMetaNode.addKnob(nuke.Text_Knob('roll', txtColor + 'Camera Roll:', "Not Available"))
    ###print "Animation Meta: " + str(len(animMeta))
    #if len(animMeta) == 4:
    #ret = nuke.getFramesAndViews('Extract Alexa Metadata', '%s-%s' %(first, last))
    frameRange = nuke.FrameRange(str(first) + '-' + str(last))

    task = nuke.ProgressTask('Baking meta data in %s' % node.name())
        
    for curTask, frame in enumerate(frameRange):
        if task.isCancelled():
            break
        task.setMessage('processing frame %s' % frame)

        if not arriMetaNode['focal'].value() == "Not Available":
            focalL = float(node.metadata(matchMetaPrefix(node, "focal".lower()), frame))
            arriMetaNode['focal'].setValueAt(float(focalL), frame)
        if not arriMetaNode['focusD'].value() == "Not Available":
            focusD = float(node.metadata(matchMetaPrefix(node, "exr/focus".lower(), "focusdistance".lower()), frame))
            arriMetaNode['focusD'].setValueAt(float(focusD), frame)
        if not arriMetaNode['tilt'].value() == "Not Available":
            tilt = float(node.metadata(matchMetaPrefix(node, "tilt".lower()), frame))
            arriMetaNode['tilt'].setValueAt(float(tilt), frame)
        if not arriMetaNode['roll'].value() == "Not Available":
            roll = float(node.metadata(matchMetaPrefix(node, "roll".lower()), frame))
            arriMetaNode['roll'].setValueAt(float(roll), frame)

        task.setProgress(int(float(curTask) / frameRange.frames()*100))
    #else:
        #pass
  
def ms_ARRI_META_EXTRACT():
    if not nuke.Root().selectedNode():
        panel = nuke.Panel('Supported files: ari dpx exr mov mxf csv')
        panel.addFilenameSearch('Choose File', "")
        panel.addBooleanCheckBox("Synch with Read Node", "")
        panel.addSingleLineInput("Read Node Name", "")
        #panel.addSingleLineInput('Start Frame', '0')
        #panel.addSingleLineInput('Project FPS', '25')
        panel.show()
        
        synch = panel.value("Synch with Read Node")
        ###print "User chose to synch: " + str(synch)
        nodeName = panel.value("Read Node Name")
        if synch == True:
            print "Synching CSV with %s node" % nodeName
        FPS = panel.value('Project FPS')
        csvFrame = panel.value('Start Frame')
        filePath =  panel.value('Choose File')
        ###print "File Path: " + filePath
        fileName = path.basename(filePath)
        ###print "File Name: " + fileName
        fileExt = path.splitext(fileName)[1]
        if filePath !="":
            if synch == True and nodeName != "":
                if nuke.exists(nodeName) != False:
                    if nuke.toNode(nodeName).Class() == "Read":
                        node = nuke.toNode(nodeName)
                        ###print "Found Synch Node: " + node['name'].value()
                        synchData = True
                    else:
                        nuke.message("Please choose an existing Read node")
                        return
                else:
                    nuke.message("Please choose an existing Read node")
                    synchData = False
                    return
            else:
                synchData = False
        else:
            print "File path is empty"
            return

        if not path.splitext(fileName)[1] in ['.mov', '.mxf', '.csv']:
            if ".exr" in fileName:
                slicedName = sliceFileName(fileName, '.exr')
                fileName = slicedName[0]
                fileNameOnly = slicedName[1]
                fileExt = slicedName[2]
                padding = slicedName[3]
            if ".dpx" in fileName:
                slicedName = sliceFileName(fileName, '.dpx')
                fileName = slicedName[0]
                fileNameOnly = slicedName[1]
                fileExt = slicedName[2]
                padding = slicedName[3]
            if ".ari" in fileName:
                slicedName = sliceFileName(fileName, '.ari')
                fileName = slicedName[0]
                fileNameOnly = slicedName[1]
                fileExt = slicedName[2]
                padding = slicedName[3]
        else:
            fileExt = path.splitext(fileName)[1]
            padding = ""
            fileNameOnly = fileName
        ###print "New File Name is: " + fileName
        ###print "File Extension: " + fileExt
        if padding.startswith('_'):
            fileNameOnly+= '_'
            ###print "Added back underscore to file name"
        filePath = path.dirname(filePath) + "/"
        ###print "PATH EXISTS: %s" % path.exists(filePath)
        if " " in filePath:
            ###print "Found White Space in Path"
            filePathWS = '"' + filePath + '"'
            whiteSpace = True
        else:
            whiteSpace = False
            ###print "Did not find any white spaces in path"
        ###print "File Directory: " + filePath
        
        if fileExt == '.csv':
            if synchData == True:
                if whiteSpace == True:
                    filePath = filePath.replace('"', '')
                    ###print "removed qoutes from %s" % filePath
                csvFile = filePath + fileNameOnly
                ms_Arri_metadata_extract_CSV(csvFile, FPS, csvFrame, synchData, node)
            else:
                if whiteSpace == True:
                    filePath = filePath.replace('"', '')
                    ###print "removed qoutes from %s" % filePath
                csvFile = filePath + fileNameOnly
                ms_Arri_metadata_extract_CSV(csvFile, FPS, csvFrame, synchData)
        else:
            if fileExt in ['.mov', '.mxf']:
                if scanDir(filePath)[0] == True:
                    ask = nuke.ask("There are multiple %s files in the directory. This might take a long time.\n\n You can choose not to continue and make sure the %s file is in a sub-folder and try again.\n\nWould you like to continue?" % (scanDir(filePath)[1], scanDir(filePath)[1]))
                    if ask == False:
                        print "User cancelled"
                        return
            if not fileExt == "":
                ###print "File EXTENSION EXISTS"
                supportedFiles = ['.ari', '.dpx', '.exr', '.mov', '.mxf', '.csv']
                
                if fileExt in supportedFiles:
                    if not whiteSpace == True:
                        findCSV = filePath + fileNameOnly+".csv"
                    else:
                        findCSV = filePathWS + fileNameOnly+".csv"
                    
                    if not path.isfile(findCSV):
                        if nuke.env['WIN32']:
                            AME_EXE = environ['HOME'] + "/" + ".nuke/mS_ARRI_MetaExtract/ArriMetaExtract_CMD_3.4.5.50.exe " 
                        else: 
                            AME_EXE = environ['HOME'] + "/" + ".nuke/mS_ARRI_MetaExtract/ARRIMetaExtract_CMD_3.4.5.50_osx "
                        ###print "AME executable: %s"% AME_EXE
                        AME_arg1 = "-s %s " % '"\\t"'
                        if not whiteSpace == True:
                            AME_arg2 = "-i " + filePath
                            AME_arg3 = " -o " + filePath
                        else:
                            AME_arg2 = "-i " + filePathWS
                            AME_arg3 = " -o " + filePathWS
                        AME = AME_EXE + AME_arg1 + AME_arg2 + AME_arg3
                        ###print "AME = %s"% AME
                        nuke.message("Extracting CSV file from clip\n\nYou can check the command-line prompt for progress\n\nClick OK to start")
                        call(AME, shell=True)
                    else:
                        ###print fileNameOnly+".csv already exists"
                        nuke.message("CSV already exists\nSkipping making CSV")
                        pass
                    ###print "SynchData: " + str(synchData)
                    if synchData == True:
                        if whiteSpace == True:
                            filePath = filePath.replace('"', '')
                            ###print "removed qoutes from %s" % filePath
                        ms_Arri_metadata_extract_CSV(filePath + fileNameOnly+".csv", FPS, csvFrame, synchData, node)
                    else:
                        if whiteSpace == True:
                            filePath = filePath.replace('"', '')
                            ###print "removed qoutes from %s" % filePath
                        ms_Arri_metadata_extract_CSV(filePath + fileNameOnly+".csv", FPS, csvFrame, synchData)
                else:
                    nuke.message('File not supported. Supported file types MOV EXR DPX ARI CSV')
            else:
                nuke.message("Cancelled")
                print "Cancelled"
    else:
        node = nuke.selectedNode()
        if node.Class() == "Read":
            if not lookForMetaPrefix(node, "arri") == True:
                ###print "Did not find arri prefix"
                nuke.message("No ARRI metadata found")
                return
            else:
                if lookForMetaPrefix(node, "quicktime") == True:
                    clipName = node.metadata(matchMetaPrefix(node, "cameraclip".lower()))
                    nuke.message("Warning: The original source of this file is a quicktime.\nNot all the metadata will be available inside Nuke.\n\nYou can source the original quicktime (%s) from disk by running the tool again without selecting any nodes." % clipName)
            ms_Arri_metadata_extract_fromRead(node)
            return
        else:
            nuke.message("Please select a Read node")