""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Jaquelin Quintero Ortiz """



import arcpy, os

out_folder = r"C:\Users\jaqui\OneDrive\Documents\ArcGIS\Projects\392 Project"
gdb_name   = "Poverty for all counties.gdb"
gdb        = os.path.join(out_folder, gdb_name)

poverty_csv = r"c:\Users\jaqui\Downloads\IncomePovertyDataForAllCounties.csv"
poverty_table_name = "PovertyByAllCounties"

# URL of the hosted feature layer 
feature_service_url = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Texas_County_Boundaries/FeatureServer/0"

# Output names
local_fc_name       = "County_Boundaries_Local1"
joined_fc_name      = "Counties_With_Poverty"

if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(out_folder, gdb_name)
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

arcpy.conversion.ExportFeatures(
    in_features = feature_service_url,
    out_features = os.path.join(gdb, local_fc_name)
)

print(f"Exported feature service to local feature class: {local_fc_name}")

arcpy.conversion.TableToTable(
    in_rows = poverty_csv,
    out_path = gdb,
    out_name = poverty_table_name
)
print(f"CSV imported as table: {poverty_table_name}")
arcpy.management.JoinField(
    in_data   = local_fc_name,
    in_field  = "CNTY_NM",        
    join_table= poverty_table_name,
    join_field= "County",         
    fields    = ["% of Population in Poverty"]
)

arcpy.management.CopyFeatures(
    in_features = local_fc_name,
    out_feature_class = joined_fc_name
)

print("Join complete — output:", joined_fc_name)
