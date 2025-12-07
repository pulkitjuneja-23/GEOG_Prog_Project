import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "School Accessibility Toolbox"
        self.alias = "school_access"
        self.tools = [SchoolServiceArea]


class SchoolServiceArea(object):
    def __init__(self):
        """Define the tool."""
        self.label = "School Service Areas & House Distance Bands"
        self.description = (
            "1) Clips the road network to a 5-mile buffer around schools "
            "to show all roads within 5 miles of any school; "
            "2) Uses straight-line distance from houses to the nearest school "
            "to assign houses to distance bands (e.g., 0-1, 1-5, 5-10, 10-15 miles) "
            "and counts how many houses fall in each band for each school."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        # 0 - School points
        schools = arcpy.Parameter(
            displayName="School Points",
            name="schools",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input"
        )

        # 1 - Roads layer
        roads = arcpy.Parameter(
            displayName="Roads Layer",
            name="roads",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input"
        )

        # 2 - Distance breaks for house distance bands
        breaks = arcpy.Parameter(
            displayName="Distance Breaks in Miles (e.g. 1 5 10 15)",
            name="breaks",
            datatype="String",
            parameterType="Optional",
            direction="Input"
        )
        breaks.value = "1 5 10 15"

        # 3 - Output roads within 5 miles of schools
        out_roads = arcpy.Parameter(
            displayName="Output Roads within 5 Miles of Schools",
            name="out_roads",
            datatype="Feature Class",
            parameterType="Required",
            direction="Output"
        )

        # 4 - House points
        houses = arcpy.Parameter(
            displayName="House Points",
            name="houses",
            datatype="Feature Layer",
            parameterType="Required",
            direction="Input"
        )

        # 5 - Output summary table: houses per school per distance band
        out_summary = arcpy.Parameter(
            displayName="Output House per School (Table)",
            name="out_summary",
            datatype="Table",
            parameterType="Required",
            direction="Output"
        )

        return [schools, roads, breaks, out_roads, houses, out_summary]

    def isLicensed(self):
        return True

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        schools     = parameters[0].valueAsText
        roads       = parameters[1].valueAsText
        breaks_text = parameters[2].valueAsText
        out_roads   = parameters[3].valueAsText
        houses      = parameters[4].valueAsText
        out_summary = parameters[5].valueAsText

    
        if not breaks_text or breaks_text.strip() == "":
            breaks_text = "1 5 10 15"

        breaks_list = sorted([float(b) for b in breaks_text.split()])
        arcpy.AddMessage("Distance breaks (miles) for house bands: {}".format(breaks_list))

        try:
            # PART 1: All roads within 5-mile radius of any school
            arcpy.AddMessage("Buffering schools by 5 miles...")
            school_buffer = r"in_memory\school_5mi"
            arcpy.analysis.Buffer(
                in_features=schools,
                out_feature_class=school_buffer,
                buffer_distance_or_field="5 Miles",
                line_side="FULL",
                line_end_type="ROUND",
                dissolve_option="ALL", 
                dissolve_field=None,
                method="PLANAR"
            )

            arcpy.AddMessage("Clipping roads to school 5-mile buffer...")
            arcpy.analysis.Clip(
                in_features=roads,
                clip_features=school_buffer,
                out_feature_class=out_roads
            )

            arcpy.AddMessage(
                "Roads within 5 miles of schools created: {}".format(out_roads)
            )

            # PART 2: Nearest school + house distance bands (straight-line)
        
            arcpy.AddMessage("Copying house points to in_memory for Near analysis...")
            tmp_houses = arcpy.management.CopyFeatures(
                houses, r"in_memory\houses_near"
            ).getOutput(0)

            arcpy.AddMessage(
                "Finding closest school for each house (straight-line, planar)..."
            )
            arcpy.analysis.Near(
                in_features=tmp_houses,
                near_features=schools,
                search_radius="",
                location="NO_LOCATION",
                angle="NO_ANGLE",
                method="PLANAR"
            )

            # Add Band field if needed
            band_field = "Band"
            if band_field not in [f.name for f in arcpy.ListFields(tmp_houses)]:
                arcpy.management.AddField(tmp_houses, band_field, "TEXT", field_length=20)

            arcpy.AddMessage("Classifying houses into distance bands (using NEAR_DIST)...")

            # Figure out NEAR_DIST units -> miles
            desc = arcpy.Describe(tmp_houses)
            sr = desc.spatialReference

            unit_to_miles = 1.0 / 5280.0  

            if sr.type == "Projected":
                unit_name = (sr.linearUnitName or "").lower()
                arcpy.AddMessage("Projected coordinate system detected: {}".format(unit_name))

                if "foot" in unit_name:
                    unit_to_miles = 1.0 / 5280.0
                elif "meter" in unit_name:
                    unit_to_miles = 1.0 / 1609.344
                elif "kilometer" in unit_name:
                    unit_to_miles = 1.0 / 1.609344
                else:
                    arcpy.AddWarning(
                        "Unrecognized linear unit '{}'; assuming feet.".format(unit_name)
                    )
                    unit_to_miles = 1.0 / 5280.0
            elif sr.type == "Geographic":
                arcpy.AddMessage("Geographic coordinate system detected; NEAR_DIST in degrees.")
                unit_to_miles = 69.0  # approx miles per degree
            else:
                arcpy.AddWarning("Unknown spatial reference type; assuming feet.")
                unit_to_miles = 1.0 / 5280.0

            def classify_band(dist_miles):
                """Return labels like '0-1', '1-5', '5-10', '10-15', '>15'."""
                if dist_miles is None or dist_miles < 0:
                    return "NoSchool"
                prev = 0.0
                for b in breaks_list:
                    if dist_miles <= b:
                        return "{}-{}".format(prev, b)
                    prev = b
                return ">{}".format(breaks_list[-1])

            # Assign bands
            with arcpy.da.UpdateCursor(tmp_houses, ["NEAR_DIST", band_field]) as cursor:
                for near_dist, band in cursor:
                    if near_dist is None:
                        miles = None
                    else:
                        miles = float(near_dist) * unit_to_miles
                    new_band = classify_band(miles)
                    cursor.updateRow([near_dist, new_band])

            arcpy.AddMessage(
                "Calculating summary: number of houses per school per distance band..."
            )

            # Statistics; FREQUENCY = house count
            stats_fields = [["NEAR_DIST", "MIN"]]   
            case_fields  = ["NEAR_FID", band_field]

            arcpy.analysis.Statistics(
                in_table=tmp_houses,
                out_table=out_summary,
                statistics_fields=stats_fields,
                case_field=case_fields
            )

            arcpy.AddMessage(
                "Summary table created: {} (one row per school NEAR_FID and Band; "
                "FREQUENCY = house count)".format(out_summary)
            )

            # Rename fields for clarity
            arcpy.AddMessage("Renaming summary table fields for clarity...")
            field_names = [f.name for f in arcpy.ListFields(out_summary)]

            if "FREQUENCY" in field_names:
                arcpy.management.AlterField(
                    out_summary,
                    "FREQUENCY",
                    new_field_name="HouseCount",
                    new_field_alias="House Count"
                )
            if "NEAR_FID" in field_names:
                arcpy.management.AlterField(
                    out_summary,
                    "NEAR_FID",
                    new_field_name="SchoolOID",
                    new_field_alias="School OBJECTID"
                )
            if band_field in field_names:
                arcpy.management.AlterField(
                    out_summary,
                    band_field,
                    new_field_name="DistanceBand",
                    new_field_alias="Distance Band (Miles)"
                )
            if "MIN_NEAR_DIST" in field_names:
                arcpy.management.DeleteField(out_summary, ["MIN_NEAR_DIST"])

        finally:
            # Clean up in_memory
            try:
                arcpy.management.Delete(r"in_memory\school_5mi")
            except Exception:
                pass
            try:
                arcpy.management.Delete(r"in_memory\houses_near")
            except Exception:
                pass
