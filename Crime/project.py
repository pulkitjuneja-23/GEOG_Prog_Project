
import arcpy

#project = "C:\\Users\\Jeff Goldblumi\\Documents\\ArcGIS\\Projects\\392proj\\392proj.aprx"  
aprx = arcpy.mp.ArcGISProject("CURRENT")
map = aprx.listMaps("Map")[0]
layer = map.listLayers("Austin_Counties")[0]
joined_field = "Sheet1$.Total_Rate_per_100_000"

sym = layer.symbology
sym.updateRenderer("GraduatedColorsRenderer")
sym.renderer.classificationField = joined_field
sym.renderer.breakCount = 5
sym.renderer.colorRamp = aprx.listColorRamps("Yellow to Red")[0]
layer.symbology = sym

aprx.save()