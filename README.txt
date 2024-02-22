Install:

Copy entire folder to HOME/.nuke/

add this line to your init.py :
nuke.pluginAddPath('./mS_ARRI_MetaExtract')

Usage:
- If executed when a Read node is selected, it will extract locally from the node.

- If executed with nothing selected, then a prompt will come up to browse for a file.(Best method for full metadata extraction).

- When extracting from a file on disk, you can synch with a read node in Nuke.(Useful if you have a plate cut from rushes).

