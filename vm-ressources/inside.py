import rhinoinside
rhinoinside.load()
import Rhino
import os
doc = Rhino.RhinoDoc.CreateHeadless(None)
Rhino.RhinoDoc.ActiveDoc = doc
Rhino.RhinoApp.RunScript('_-Line 0,0,0 10,10,10', False)
the_doc = Rhino.RhinoDoc.ActiveDoc
cwd = os.getcwd();
the_doc.WriteFile(cwd+'\\123est.3dm', Rhino.FileIO.FileWriteOptions())
the_doc.Dispose()