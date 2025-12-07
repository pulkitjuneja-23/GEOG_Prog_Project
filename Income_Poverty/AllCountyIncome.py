""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Jaquelin Quintero Ortiz """

import arcpy, os

out_folder = r"C:\Users\jaqui\OneDrive\Documents\ArcGIS\Projects\392 Project"
gdb_name   = "CountiesIncome.gdb"
gdb        = os.path.join(out_folder, gdb_name)

income_csv = r"c:\Users\jaqui\Downloads\IncomePovertyDataForAllCounties.csv"
income_table_name = "IncomeByAllCounties"

# URL of the hosted feature layer 
feature_service_url = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Texas_County_Boundaries/FeatureServer/0"

# Output names
local_fc_name       = "County_Boundaries_Local"
joined_fc_name      = "Counties_With_Income"

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
    in_rows = income_csv,
    out_path = gdb,
    out_name = income_table_name
)
print(f"CSV imported as table: {income_table_name}")

arcpy.management.JoinField(
    in_data   = local_fc_name,
    in_field  = "CNTY_NM",        
    join_table= income_table_name,
    join_field= "County",         
    fields    = ["Per_Capita_Income"]
)

arcpy.management.CopyFeatures(
    in_features = local_fc_name,
    out_feature_class = joined_fc_name
)

print("Join complete — output:", joined_fc_name)
