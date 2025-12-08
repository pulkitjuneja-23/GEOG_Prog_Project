""" GEOG 392 Project """
""" Group 9 """
""" Team Member: Sophia Arora """

import arcpy, os

# Output folder and geodatabase
out_folder = r"C:\Users\sophi\SA-GEOG392-Lab\Labs\Project\Output_Files\GAMA School Going Kids"
gdb_name   = "GAMASGKData.gdb"
gdb        = os.path.join(out_folder, gdb_name)

# CSV with population change data
population_csv = r"C:\Users\sophi\SA-GEOG392-Lab\Labs\Project\Pop Data\csv files\GAMA SGK ALL DATA.csv"
population_table_name = "GAMATotalSGK2020"

# Local county boundary shapefile
county_shapefile = r"C:\Users\sophi\SA-GEOG392-Lab\Labs\Project\Pop Data\Schooldata_Shapefiles\Austin_Counties.shp"

# Output feature class names (NO SPACES)
local_fc_name  = "GAMAPop_Local"
joined_fc_name = "GAMA2020TotalSGK"

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
    in_rows = population_csv,
    out_path = gdb,
    out_name = population_table_name
)
print("CSV imported as table.")

# Perform the join
arcpy.management.JoinField(
    in_data   = local_fc_path,
    in_field  = "CNTY_NM",        # County name field in county shapefile
    join_table= population_table_name,
    join_field= "CountyName",     # County name field in CSV
    fields    = ["Pop2020", "PopChan", "Total_SGK", "Percent_SGK"]
)
print("Join completed.")

# Save joined output as new feature class
arcpy.management.CopyFeatures(
    in_features = local_fc_path,
    out_feature_class = os.path.join(gdb, joined_fc_name)
)
print("Output saved as:", joined_fc_name)