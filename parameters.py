from pathlib import Path
import shutil
"""
    Class handling the parameters for the model, and reading/creating input.txt
"""
class Parameters:
    def __init__(self):
        # Making this array so we can set attributes in a loop
        self.order_of_attributes = []
        self.display_parameters = False
        # Initializing variables to the correct types and associated useful information
        # 0=staticuniformrainfallwithsimpleoutputs,1=rainfallvariableinspaceand/ortimeandcomplexoutputs)
        #TODO: oen issue is that the scope of these variables keeps growing
        self.image_path = ""
        #Mode probably needs more custom behavior in the acutal paramters
        self.add_parameter(
            name="mode",
            value=1,             
            comment=(
                "Flag_for_mode_of_operation.0=staticuniformrainfallwithsimpleoutputs,_1=rainfallvariableinspaceand/ortimeandcomplexoutputs"
            ),
            help="ASK ABOUT WHAT TO INCLUDE IN THE HELP FOR NEW VARIABLES",
            display_name="Mode",
            options=["Static Uniform Rainfall with Simple Outputs", "Rainfall Variable in Space and/or Time and Complex Outputs"],
            #TODO: Actually break this option out into different parameters
            file_input={
                "display_name": "Variable Input",
                "name" : "variableinput.txt",
                "path" : "",
                "path" : "",
                "help": "A raster file with the same dimensions as the DEM, with 1s where you want to mask and 0s where you don't",
            },
            input_field_type="file" 
            
        )
        # 0=MFD,1=depth-based,2=DInfinity
        self.add_parameter(
            name="routing_method", 
            value=1,
            comment="Flag_for_outing_method._0=MFD,1=depth-based,2=DInfinity",
            help="",
            display_name="Routing Method",
            input_field_type="select",
            options=["MFD", "Depth-based", "DInfinity"]
        )
        #0=HawsandErickson(2020),1=Pelletieretal(inpress))
        self.add_parameter(
            name="shear_stress_equation_flag", 
            value=1, 
            comment="Flag_for_shear_stress_equation.0=HawsandErickson(2020),1=Pelletieretal(inpress)",
            help="",
            display_name="Sheer Stress Equation Flag",
            options=["Haws and Erickson (2020)", "Pelletier et al. (in press)"],
            input_field_type="select"
        )
        #TODO maybe we don't need to have a checkbox for this
        self.add_parameter(
            "mask_flag", 
            0,
            comment="Flag_for_mask.0=nomask,1=mask",
            help="",
            display_name="Mask Flag",
            file_input={
                "display_name": "Mask File",
                "name" : "mask_filepath",
                "filename" : "mask.tif",
                "path" : "",
                "help": "A raster file with the same dimensions as the DEM, with 1s where you want to mask and 0s where you don't",
            },
            input_field_type="file" 
        )

        self.add_parameter(
            "tauc_soil_and_veg_flag",
            0, 
            comment="Flag_for_tauc_soil_and_veg._0=fixed,1=rasterprovided",
            help="",
            display_name="Tauc Soil and Vegetation Flag",
            file_input={
                "display_name": "Tauc Soil and Vegetation Raster filepath",
                "name" : "tauc_filepath",
                "path" : "",
                "help": "",
            },
            input_field_type="file"
        )
        
        self.add_parameter(
            "d50_flag",
            0, 
            comment="Flag_for_d50._0=fixed,1=rasterprovided",
            help="",
            display_name="d50 Flag",
            file_input={
                "display_name": "d50 File",
                "name" : "d50_filepath",
                "path" : "",
                "help": "A raster file with the same dimensions as the DEM, with 1s where you want to mask and 0s where you don't",
            },
            input_field_type="file"
        )

        self.add_parameter(
            "rock_thickness_flag", 
            0, 
            comment="Flag_for_rock_thickness._0=fixed,1=rasterprovided",
            help="",
            file_input={
                "display_name": "Path to rock thickness raster",
                "name" : "rock_thickness_filepath",
                "path" : "",
                "help": "",
            },
            display_name="Rock Thickness Flag",
            input_field_type="file"
        )
        
        self.add_parameter(
            "rock_cover_flag", 
            0, 
            comment="Flag_for_rock_cover._0=fixed,1=rasterprovided",
            help="",
            file_input={
                "display_name": "Path to rock cover raster",
                "name" : "rock_cover_filepath",
                "path" : "",
                "help": "",
            },
            display_name="Rock Cover Flag",
            input_field_type="file"
        )
        #TODO REMOVE DEFAULT ARG OR FIGURE OUT SOMETHING SMARTER. INPUT_FIELD_TYPE FEELS AWKWARD
        #meters
        self.add_parameter(
            "fill_increment", 
            .01,
            comment="Fill increment (meters)",
            help="",
            display_name="Fill_Increment",
            input_field_type="number"
        )
        #meter per meter
        self.add_parameter(
            name="min_slope",
            value=.01,
            comment="_Minimum_slope_(meter per meter)",
            help="",
            display_name="Minimum Slope"
        , input_field_type="number")
        # pixels
        self.add_parameter(
            name="expansion",
            value=1,
            comment="Expansion_(pixels)",
            help="",
            display_name="Expansion"
        , input_field_type="number")
        self.add_parameter(
            "yellow_threshold",
            .1,
            comment="Yellow_threshold",
            help="",
            display_name="Yellow Threshold"
        , input_field_type="number")
        # Don't initialize these, till we know the size of the image
        self.add_parameter(
            "lattice_size_x", 
            1, 
            comment="Lattice_size_x",
            help="",
            display_name="Lattice Size x",
            input_field_type="number"
        )
        self.add_parameter(
            "lattice_size_y", 
            1, 
            comment="Lattice_size_Y",
            help="",
            display_name="Lattice Size Y",
            input_field_type="number"
        )
        self.add_parameter(
            "delta_x",
            1,
            comment="Delta_x",
            help="",
            display_name='$\Delta$ x',
            input_field_type="number"
        )
        self.add_parameter(
            "no_data_value", 
            -9999, 
            comment="No_data_value",
            help="",
            display_name="No Data Value",
            input_field_type="number"
        )
        #pixels
        self.add_parameter(
            "smoothing_length",
            1, 
            comment="Smoothing_length_(pixels)",
            help="",
            display_name="Smoothing Length",
            input_field_type="number"
        )
        #m^(1/3)/s
        #? Not sure if this is supposed ot be 1 word
        self.add_parameter(
            "manningsn",
            .01,
            comment="Manningsn_(m^(1/3)/s)",
            help="",
            display_name="Manningsn"
        , input_field_type="number")
        self.add_parameter(
            "depth_weight_factor",
            .01,
            comment="Depth_weight_factor",
            help="",
            display_name="Depth_Weight_Factor"
        , input_field_type="number")
        self.add_parameter(
            "number_of_slices",
            1,
            comment="Number_of_slices",
            help="",
            display_name="Number of Slices"
        , input_field_type="number")
        self.add_parameter(
            "number_of_sweeps",
            1,
            comment="Number_of_sweeps",
            help="",
            display_name="Number of Sweeps"
        , input_field_type="number")
        # mm/hr
        self.add_parameter(
            "rain_fixed",
            1,
            comment="Rain_fixed_(mm/hr)",
            help="",
            display_name="Rain Fixed"
        , input_field_type="number")
        self.add_parameter( 
            "tauc_soil_and_veg",
            1,
            comment="Tauc_soil_and_vegetation",
            help="",
            display_name="Tauc Soil and Vegetation"
        , input_field_type="number")
        # meters
        self.add_parameter(
            "d50_fixed",
            .01,
            comment="D50_fixed_(meters)",
            help="",
            display_name="D50 Fixed"
        , input_field_type="number")
        # meters
        self.add_parameter(
            "rock_thickness_fixed",
            .01,
            comment="Rock_thickness_fixed_(meters)",
            help="",
            display_name="Rock Thickness Fixed"
        , input_field_type="number")

        self.add_parameter(
            "rock_cover_fixed",
            1,
            comment="Rock_cover_fixed",
            help="",
            display_name="Rock Cover Fixed"
        , input_field_type="number")
        self.add_parameter(
            "tan_angle_of_internal_friction",
            .01,
            comment="Tan_angle_of_internal_friction",
            help="",
            display_name ="Tan Angle of Internal Friction"
        , input_field_type="number")

        #? b(2*(1-c)) No clue how to name this, just using b
        self.add_parameter(
            "b",
            1,
            comment="b(2*(1-c))",
            help="",
            display_name="B",
            input_field_type="number"
        )
        self.add_parameter(
            "c", 
            .01,
            comment="c", 
            help="", 
            display_name="c", 
            input_field_type="number"
        )
        # meters
        self.add_parameter("rill_width_coefficent", 
            .01, 
            comment="Rill_width_coefficient_(meters)",
            help="",   
            display_name="Rill Width Coefficient",
            input_field_type="number"
        )
        
        self.add_parameter(
            "rill_width_exponent",
            .01,
            comment="Rill_width_exponent",
            help="",
            display_name="Rill Width Exponent",
            input_field_type="number"
        )

    """
        Function to add rillgen parameter to the object with the given name, value, comment, display_name, and other
        relevant metadata for an input field type
    """
    def add_parameter(self, name, value, comment, display_name, input_field_type, **kwargs):
        self.order_of_attributes.append(name)
        setattr(self, 
            name, 
            {  
                "name": name,
                "value": value, 
                "comment": comment,
                "display_name": display_name,
                "input_field_type": input_field_type,
                **kwargs
            }
        )

    def mutable_input_fields(self):
        non_input_fields = ["lattice_size_x", "lattice_size_y"]
        return [
            field for field in self.order_of_attributes if field not in non_input_fields
        ]
    
    def parametersAsArray(self):
        return [self.get_value(attribute) for attribute in self.order_of_attributes]
    
    def getEnabledFilePaths(self):
        return [self.get_associated_filepath(attribute) for attribute
            in self.order_of_attributes if self.get_attribute_object(attribute)["input_field_type"] == "file"]
    
    
    def get_associated_filepath(self, attribute):
        return (
            self.get_attribute_object(attribute)["file_input"]["path"] 
                if "file_input" in self.get_attribute_object(attribute) else None
        )
    
    def update_value(self, attribute, value):
        attribute_dictionary = getattr(self, attribute)
        # Convert the inputed value to the same type as the default value
        type_conversion = type(attribute_dictionary["value"])
        attribute_dictionary["value"] = type_conversion(value)
    
    def get_value(self, attribute):
        return getattr(self, attribute)["value"]
    
    # Helper to clarify the type of the attribute
    def get_attribute_object(self, attribute):
        return getattr(self, attribute)
    
    def getParametersFromFile(self, filename):
        file = open(filename, "r")
        for attribute in self.order_of_attributes:
            # Get the first word of the line,
            # in case we are reading an annotated input file
            line, comment = file.readline().strip().split()
            self.update_value(attribute, line)
            self.get_attribute_object(attribute)["comment"] = comment
        file.close()
    
    def writeParametersToFile(self, path, comment=True):
        file = open(path, "w")
        sum_of_length_of_comments = 0
        for attribute in self.order_of_attributes:
            current_attribute_dict = self.get_attribute_object(attribute)
            sum_of_length_of_comments += len(current_attribute_dict["comment"])

            string = \
                    str(current_attribute_dict['value']) + "\t" + "_".join(current_attribute_dict['comment'].strip().split(" "))+ "\n" \
                    if comment else \
                    str(current_attribute_dict['value']) + "\n"
            if current_attribute_dict["input_field_type"] == "file" and current_attribute_dict["value"] == 1:
                file_dict = current_attribute_dict["file_input"]
                filepath = file_dict["path"]
                print(filepath)
                if Path(filepath).exists():
                    Path(filepath).unlink()
                shutil.copyfile(filepath, Path(path).parent / file_dict["name"])
                
            file.write(string)
        file.close()