""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Jaquelin Quintero Ortiz """

import arcpy, os

# Output folder and geodatabase
out_folder = r"C:\Users\jaqui\OneDrive\Documents\ArcGIS\Projects\392 Project"
gdb_name   = "392Project.gdb"
gdb        = os.path.join(out_folder, gdb_name)

poverty_csv = r"C:\Users\jaqui\OneDrive\Desktop\GEOG 392 Project\Income_Data_CLEAN.csv"
poverty_table_name = "Income_Data.csv"

county_shapefile = r"C:\Users\jaqui\OneDrive\Desktop\GEOG 392 Project\Austin_Metro_ExportFeatures.shp"
local_fc_name  = "PercentPoverty"
joined_fc_name = "PercentPoverty_Joined"

# Create geodatabase if missing
if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(out_folder, gdb_name)

arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

# Copy the shapefile into the geodatabase
local_fc_path = os.path.join(gdb, local_fc_name)
arcpy.conversion.FeatureClassToFeatureClass(
    in_features = county_shapefile,
    out_path = gdb,
    out_name = local_fc_name
)
print("Shapefile copied into geodatabase.")

# Import CSV into geodatabase
arcpy.conversion.TableToTable(
    in_rows = poverty_csv,
    out_path = gdb,
    out_name = poverty_table_name
)
print("CSV imported as table.")

# join
arcpy.management.JoinField(
    in_data   = local_fc_path,
    in_field  = "CNTY_NM",       
    join_table= poverty_table_name,
    join_field= "County",    
    fields    = ["% of Population in Poverty"]
)
print("Join completed.")

# Save joined output 
arcpy.management.CopyFeatures(
    in_features = local_fc_path,
    out_feature_class = os.path.join(gdb, joined_fc_name)
)
print("Output saved as:", joined_fc_name)