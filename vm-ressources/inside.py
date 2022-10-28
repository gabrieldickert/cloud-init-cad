import rhinoinside
path = rhinoinside.load(r"C:\Program Files\Rhino 7\System")
import Rhino
import os
doc = Rhino.RhinoDoc.CreateHeadless(None)
print(doc)
Rhino.RhinoDoc.ActiveDoc = doc
the_doc = Rhino.RhinoDoc.ActiveDoc
the_doc.Objects.AddPoint(Rhino.Geometry.Point3d(1.0, 2.0, 3.0))
print(os.getcwd())
#cwd = os.getcwd();
#the_doc.WriteFile(cwd+'\\123est.3dm', Rhino.FileIO.FileWriteOptions())
#the_doc.Dispose()