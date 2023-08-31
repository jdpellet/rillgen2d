from __future__ import annotations

import streamlit as st
from pathlib import Path
from dataclasses import dataclass
from .Fields import Field, NumericField, FileField, OptionField, EmptyField, CheckBoxField, StaticParameter
import shutil

class Parameters: 
    def __init__(self):
        # Making this array so we can set attributes in a loop
        self.order_of_attributes = []
        self.display_parameters = False
        # Initializing variables to the correct types and associated useful information
        # 0=staticuniformrainfallwithsimpleoutputs,1=rainfallvariableinspaceand/ortimeandcomplexoutputs)
        self.image_path = ""
        #Mode probably needs more custom behavior in the acutal paramters
        self.add_parameter(
            OptionField(
                name="mode", 
                display_name="Mode", 
                conditional_field=[
                    EmptyField(),
                    FileField(
                        display_name="Variable Input",
                        name="variableinput.txt",
                        help=(
                            "A raster file with the same dimensions as the DEM," 
                            + " with 1s where you want to mask and 0s where you don't"
                        ),
                        value="",
                        comment="",
                    )
                ],
                value=1, 
                options=[
                    "Static Uniform Rainfall with Simple Outputs", 
                    "Rainfall Variable in Space and/or Time and Complex Outputs"
                ],
                help="ASK ABOUT WHAT TO INCLUDE IN THE HELP FOR NEW VARIABLES",
            )
        )
        
        # 0=MFD,1=depth-based,2=DInfinity
        self.add_parameter(
            OptionField(
                display_name="Routing Method", 
                name="routing_method",
                comment="Flag_for_outing_method._0=MFD,1=depth-based,2=DInfinity",
                value=1, 
                #TODO
                help="",
                options=["MFD", "Depth-based", "DInfinity"],
            )
        )
        
        #0=HawsandErickson(2020),1=Pelletieretal(inpress))
        self.add_parameter(
            OptionField(
                name="shear_stress_equation_flag",
                value=1,
                comment="Flag_for_shear_stress_equation.0=HawsandErickson(2020),1=Pelletieretal(inpress)",
                help="",
                display_name="Sheer Stress Equation Flag",
                options=["Haws and Erickson (2020)", "Pelletier et al. (in press)"],
            )
        )

        #TODO maybe we don't need to have a checkbox for this
        self.add_parameter(
            CheckBoxField(
                name="mask_flag",
                display_name="Mask Flag",
                value=0,
                comment="Flag_for_mask.0=nomask,1=mask",
                help="",
                conditional_field=FileField(
                    display_name="Mask File",
                    name="mask.tif",
                    help=(
                        "A raster file with the same dimensions as the DEM," + 
                        "with 1s where you want to mask and 0s where you don't"
                    ),
                    comment="",
                    value="",
                )
            )
        )

        self.add_parameter(
            CheckBoxField(
                name = "tauc_soil_and_veg_flag",
                value=0,
                comment="Flag_for_tauc_soil_and_veg._0=fixed,1=rasterprovided",
                help="",
                display_name="Tauc Soil and Vegetation Flag",
                conditional_field=FileField(
                    name="tauc_filepath",
                    display_name="Tauc Soil and Vegetation Raster filepath",
                    help="",
                ),
            )
        )
        
        self.add_parameter(
            CheckBoxField(
                name = "d50_flag",
                value = 0, 
                comment = "Flag_for_d50._0=fixed,1=rasterprovided",
                help="",
                display_name="d50 Flag",
                conditional_field=FileField(
                    display_name="d50 File",
                    name="d50_filepath",
                    help="A raster file with the same dimensions as the DEM, with 1s where you want to mask and 0s where you don't",
                )
            )
        )

        self.add_parameter(
            CheckBoxField(
                name="rock_thickness_flag",
                value=0,
                comment="Flag_for_rock_thickness._0=fixed,1=rasterprovided",
                help="",
                display_name="Rock Thickness Flag",
                conditional_field=FileField(
                    display_name="Rock Thickness Raster File",
                    name="rock_thickness_filepath",
                    help="",
                )
            )
        )
        
        self.add_parameter(
            CheckBoxField(
                name="rock_cover_flag",
                value=0,
                comment="Flag_for_rock_cover._0=fixed,1=rasterprovided",
                help="",
                display_name="Rock Cover Flag",
                conditional_field=FileField(
                    display_name="Path to rock cover raster",
                    name="rock_cover_filepath",
                    help="",
                )
            )
        )
        #TODO REMOVE DEFAULT ARG OR FIGURE OUT SOMETHING SMARTER. INPUT_FIELD_TYPE FEELS AWKWARD
        #meters
        self.add_parameter(
            NumericField(
                name="fill_increment",
                value=.01,
                comment="Fill_increment_(meters)",
                help="",
                display_name="Fill Increment",
            )
        )
        #meter per meter
        self.add_parameter(
            NumericField(
                name="min_slope",
                value=.01,
                comment="_Minimum_slope_(meter per meter)",
                help="",
                display_name="Minimum Slope"
            )
        )
        # pixels
        self.add_parameter(
            NumericField(
                name="expansion",
                value=1,
                comment="Expansion_(pixels)",
                help="",
                display_name="Expansion"
            )
        )
        
        self.add_parameter(
            NumericField(
                name="yellow_threshold",
                value=.1,
                comment="Yellow_threshold",
                help="",
                display_name="Yellow Threshold"
            )
        )
        # Don't initialize these, till we know the size of the image
        #TODO why should these be Static Fields vs just being stored in the object?
        self.add_parameter(
            StaticParameter(
                name = "lattice_size_x",
                value=1,
                comment="Lattice_size_x",
                help="",
                display_name="Lattice Size X",
            )
        )
        self.add_parameter(
            StaticParameter(
                name="lattice_size_y", 
                value = 1, 
                comment="Lattice_size_Y",
                help="",
                display_name="Lattice Size Y",
            )
        )
        
        self.add_parameter(
            NumericField(
                name="delta_x",
                value=1,
                comment="Delta_x",
                help="",
                display_name='$\Delta$ x',
            )
        )
        
        self.add_parameter(
            NumericField(
                name="no_data_value", 
                value=-9999, 
                comment="No_data_value",
                help="",
                display_name="No Data Value",
            )
        )
        #pixels
        self.add_parameter(
            NumericField( 
                name= "smoothing_length",
                value=1, 
                comment="Smoothing_length_(pixels)",
                help="",
                display_name="Smoothing Length",
            )
        )
        #m^(1/3)/s
        #? Not sure if this is supposed ot be 1 word
        self.add_parameter(
            NumericField(
                name="manningsn",
                value=.01,
                comment="Manningsn_(m^(1/3)/s)",
                help="",
                display_name="Manningsn"
            )

        )
        
        self.add_parameter(
            NumericField(
                name="depth_weight_factor",
                value=.01,
                comment="Depth_weight_factor",
                help="",
                display_name="Depth_Weight_Factor"
            )
        )
        self.add_parameter(
            NumericField(
                name="number_of_slices",
                value=1,
                comment="Number_of_slices",
                help="",
                display_name="Number of Slices"
            )
        )
        
        self.add_parameter(
            NumericField(
                name="number_of_sweeps",
                value=1,
                comment="Number_of_sweeps",
                help="",
                display_name="Number of Sweeps"
            )
        )
        # mm/hr
        self.add_parameter(
            NumericField(
                name="rain_fixed",
                value=1,
                comment="Rain_fixed_(mm/hr)",
                help="",
                display_name="Rain Fixed"
            )
        )
        self.add_parameter( 
            NumericField(
                name="tauc_soil_and_veg",
                value=1,
                comment="Tauc_soil_and_vegetation",
                help="",
                display_name="Tauc Soil and Vegetation"
            )
        )
        
        # meters
        self.add_parameter(
            NumericField(
                name="d50_fixed",
                value=.01,
                comment="D50_fixed_(meters)",
                help="",
                display_name="D50 Fixed",
            )
        )
        # meters
        self.add_parameter(
            NumericField(
                name="rock_thickness_fixed",
                value=.01,
                comment="Rock_thickness_fixed_(meters)",
                help="",
                display_name="Rock Thickness Fixed"
            )
        )

        self.add_parameter(
            NumericField(
                name="rock_cover_fixed",
                value=1,
                comment="Rock_cover_fixed",
                help="",
                display_name="Rock Cover Fixed"
            )
        )
        self.add_parameter(
            NumericField(
                name="tan_angle_of_internal_friction",
                value=.01,
                comment="Tan_angle_of_internal_friction",
                help="",
                display_name ="Tan Angle of Internal Friction"
            )
         )

        #? b(2*(1-c)) No clue how to name this, just using b
        self.add_parameter(
            NumericField(
                name="b",
                value=1,
                comment="b(2*(1-c))",
                help="",
                display_name="B",
            )
        )
        
        self.add_parameter(
            NumericField(
                name="c", 
                value=.01,
                comment="c", 
                help="", 
                display_name="c", 
            )
        )
        # meters
        self.add_parameter(
            NumericField(
                name="rill_width_coefficient",
                value=.01, 
                comment="Rill_width_coefficient_(meters)",
                help="",   
                display_name="Rill Width Coefficient",
            )
        )
        
        self.add_parameter(
            NumericField(
                name="rill_width_exponent",
                value=.01,
                help="",
                comment="Rill_width_exponent",
                display_name="Rill Width Exponent"
            )
        )

    """
        Function to add rillgen parameter to the object with the given name, value, comment, display_name, and other
        relevant metadata for an input field type
    """
    def add_parameter(self, field : Field):
        self.order_of_attributes.append(field.name)
        setattr(self, field.name, field)

    def mutable_input_fields(self):
        non_input_fields = ["lattice_size_x", "lattice_size_y"]
        return [
            field for field in self.order_of_attributes if field not in non_input_fields
        ]
    
    def parametersAsArray(self):
        return [self.get_value(attribute) for attribute in self.order_of_attributes]
    
    def getEnabledFilePaths(self):
        return [
            self.get_attribute_object(attribute).get_value() for attribute in self.order_of_attributes
            if isinstance(
                self.get_attribute_object(attribute),
                (FileField, OptionField, CheckBoxField,)
            ) and isinstance(self.get_attribute_object(attribute).get_value(), str)
        ]
    
    def draw_fields(self):
        st.table({"Lattice Size X:": self.get_value("lattice_size_x"), "Lattice Size Y:": self.get_value("lattice_size_y")})
        for attribute in self.order_of_attributes:
            self.get_attribute_object(attribute).draw()
        
        
        
    def get_associated_filepath(self, attribute):
        cur_obj = self.get_attribute_object(attribute)
    

    
    def get_value(self, attribute):
        return getattr(self, attribute).get_value()
    
    # Helper to clarify the type of the attribute
    def get_attribute_object(self, attribute):
        return getattr(self, attribute)
    
    def getParametersFromFile(self, filename):
        file = open(filename, "r")
        for attribute in self.order_of_attributes:
            # Get the first word of the line,
            # in case we are reading an annotated input file
            line = file.readline().strip().split()
            if len(line) > 1:
                comment = line[1]
                self.get_attribute_object(attribute).comment = comment
            line = line[0]
            cur_obj = self.get_attribute_object(attribute)
            print(cur_obj.name)
            self.get_attribute_object(attribute).value = type(cur_obj.value)((line))

        file.close()
    
    def writeParametersToFile(self, path, comment=True):
        file = open(path, "w")
        sum_of_length_of_comments = 0
        for attribute in self.order_of_attributes:
            current_attr_obj = self.get_attribute_object(attribute)
            sum_of_length_of_comments += len(current_attr_obj.comment)

            string = \
                    str(current_attr_obj.get_value()) + "\t" + "_".join(current_attr_obj.comment.strip().split(" "))+ "\n" \
                    if comment else \
                    str(current_attr_obj.value) + "\n"
 
                
            file.write(string)
        file.close()