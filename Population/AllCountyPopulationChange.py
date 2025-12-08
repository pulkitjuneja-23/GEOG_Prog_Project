""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Sophia Arora """

import arcpy, os

# Output folder and geodatabase
out_folder = r"C:\Users\sophi\SA-GEOG392-Lab\Labs\Project\Output_Files\All Texas Counties Population Change"
gdb_name   = "ALLTXCountiesPopulation.gdb"
gdb        = os.path.join(out_folder, gdb_name)

# CSV containing population data
population_csv = r"C:\Users\sophi\SA-GEOG392-Lab\Labs\Project\Pop Data\csv files\TexasPopChan.csv"
population_table_name = "PopulationChange"

# URL of the hosted feature layer 
feature_service_url = "https://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/Texas_County_Boundaries/FeatureServer/0"

# Output feature class names
local_fc_name  = "County_Boundaries_Local"
joined_fc_name = "PopulationChange2020_2010_Diff"

# Create geodatabase if it doesn't exist
if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(out_folder, gdb_name)

arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

# Export feature service to local feature class
arcpy.conversion.ExportFeatures(
    in_features = feature_service_url,
    out_features = os.path.join(gdb, local_fc_name)
)
print(f"Exported feature service to local feature class: {local_fc_name}")

# Import CSV as table
arcpy.conversion.TableToTable(
    in_rows = population_csv,
    out_path = gdb,
    out_name = population_table_name
)
print(f"CSV imported as table: {population_table_name}")

# Join population and population density data to county boundaries
arcpy.management.JoinField(
    in_data   = local_fc_name,
    in_field  = "CNTY_NM",           # field in feature class
    join_table= population_table_name,
    join_field= "CountyName",            # field in CSV
    fields    = ["Pop2010", "Pop2020", "PopChan", "PopChanPerc"]  # join both columns
)

# Save the joined feature class
arcpy.management.CopyFeatures(
    in_features = local_fc_name,
    out_feature_class = joined_fc_name
)
print("Join complete — output:", joined_fc_name)