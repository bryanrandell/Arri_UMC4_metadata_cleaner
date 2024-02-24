import ms_Arri_Metadata_Extract_Nuke
toolbar = nuke.menu('Nodes')
mS_Tools = toolbar.addMenu('mS_Tools', icon='LittleHelpers.png')
md = mS_Tools.addMenu('Metadata', icon='CopyMetaData.png')
md.addCommand('mS_ARRI_Meta_Extract', ms_Arri_Metadata_Extract_Nuke.ms_ARRI_META_EXTRACT, icon='CopyMetaData.png')