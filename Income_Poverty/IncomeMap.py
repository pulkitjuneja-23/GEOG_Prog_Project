""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Jaquelin Quintero Ortiz """

import arcpy, os

# Output folder and geodatabase
out_folder = r"C:\Users\jaqui\OneDrive\Documents\ArcGIS\Projects\392 Project"
gdb_name   = "392Project.gdb"
gdb        = os.path.join(out_folder, gdb_name)

income_csv = r"C:\Users\jaqui\OneDrive\Desktop\GEOG 392 Project\Income_Data_CLEAN.csv"
income_table_name = "Income_Data.csv"

# Shapefile
county_shapefile = r"C:\Users\jaqui\OneDrive\Desktop\GEOG 392 Project\Austin_Metro_ExportFeatures.shp"
local_fc_name  = "PerCapitaIncome"
joined_fc_name = "PerCapitaIncome_Joined"

# Create geodatabase if missing
if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(out_folder, gdb_name)

arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

local_fc_path = os.path.join(gdb, local_fc_name)
arcpy.conversion.FeatureClassToFeatureClass(
    in_features = county_shapefile,
    out_path = gdb,
    out_name = local_fc_name
)
print("Shapefile copied into geodatabase.")

# Import CSV into geodatabase
arcpy.conversion.TableToTable(
    in_rows = income_csv,
    out_path = gdb,
    out_name = income_table_name
)



JOIN_FIELD_INCOME = "County"         
JOIN_FIELD_VALUE  = "Per Capita Income"   


arcpy.management.JoinField(
    in_data   = local_fc_path,
    in_field  = "CNTY_NM",       
    join_table= income_table_name,
    join_field= "County",  
    fields    = ["Per Capita Income"]
)
print("Join completed.")

# Save joined output 
arcpy.management.CopyFeatures(
    in_features = local_fc_path,
    out_feature_class = os.path.join(gdb, joined_fc_name)
)
print("Output saved as:", joined_fc_name)
