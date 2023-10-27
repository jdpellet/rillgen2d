from __future__ import annotations
from pathlib import Path

from .Fields import (
    Field,
    NumericField,
    FileField,
    OptionField,
    EmptyField,
    CheckBoxField,
    StaticParameter,
)
import shutil
import streamlit as st


class Parameters:
    """Class encapsulating parameters management, validation, and file I/O operations."""

    def __init__(self) -> None:
        """Initializes Parameters instance variables."""
        self.display_parameters = False
        self.image_path = ""
        self.order_of_attributes: list[str] = []
        self.file_fields: list[FileField] = []
        self.add_parameter_fields()

    def mutable_input_fields(self) -> list[str]:
        """Retrieve a list of mutable parameters."""
        return [
            field
            for field in self.order_of_attributes
            if not isinstance(field, StaticParameter)
        ]

    def parametersAsArray(self) -> list:
        """Converts ordered attributes to a list of their respective values."""
        return [self.get_value(attribute) for attribute in self.order_of_attributes]

    def draw_fields(self, disabled: bool) -> None:
        """Draws the UI components for all ordered attributes."""
        st.table(
            {
                "Lattice Size X:": self.get_value("lattice_size_x"),
                "Lattice Size Y:": self.get_value("lattice_size_y"),
            }
        )
        for attribute in self.order_of_attributes:
            self.get_parameter(attribute).draw(disabled)

    def get_value(self, attribute: str):
        """Retrieves the value of a specified attribute."""
        return getattr(self, attribute).get_value()

    def get_parameter(self, attribute: str) -> Field:
        """Retrieves the Field object of a specified attribute."""
        return getattr(self, attribute)

    def getParametersFromFile(self, filename: str) -> None:
        """Loads and sets parameter values from a file."""
        with open(filename, "r") as file:
            for attribute in self.order_of_attributes:
                line = file.readline().strip().split()
                if len(line) > 1:
                    comment = line[1]
                    self.get_parameter(attribute).comment = comment
                line = line[0]
                cur_obj = self.get_parameter(attribute)
                cur_obj.value = type(cur_obj.value)(line)

    def writeParametersToFile(self, path: str, comment=True) -> None:
        """Writes parameters to a file."""
        with open(path, "w") as file:
            for attribute in self.order_of_attributes:
                current_attr_obj = self.get_parameter(attribute)
                string = (
                    f"{current_attr_obj.get_value()}\t{'_'.join(current_attr_obj.comment.strip().split(' '))}\n"
                    if comment
                    else f"{current_attr_obj.value}\n"
                )
                print(f"{attribute} {current_attr_obj.get_value()}")
                file.write(string)

    def validate(self) -> list[str]:
        """Validates all parameters and returns a list of error messages."""
        errors = []
        for attribute in self.order_of_attributes:
            error = self.get_parameter(attribute).validate()
            if error:
                errors.append(error)
        return errors

    def copy_files_to_dir(self, path: Path) -> None:
        """Copies files related to FileField attributes to a specified directory."""
        for attribute in self.order_of_attributes:
            checkbox = self.get_parameter(attribute)
            if (
                isinstance(checkbox, (OptionField, CheckBoxField))
                and isinstance(checkbox.get_inner_type(),FileField)
            ):
                file_parameter = checkbox.get_inner_value()
                filepath = file_parameter.filename
                shutil.copy(file_parameter.get_value(), path / filepath)

    def add_parameter_fields(self):
        """Define the  basic parameter fields in order"""
        self.add_parameter(
            OptionField(
                name="mode",
                display_name="Enable Dynamic Mode (optional)",
                conditional_field=[
                    EmptyField(),
                    FileField(
                        display_name="Variable Input",
                        name="variableinput",
                        help=(
                            "Path to required file named `dynamicinput` as either `.tif` or `.txt`"
                        ),
                        value="",
                        comment="",
                        filename="variableinput.txt",
                    ),
                ],
                value=1,
                options=[
                    "Static Uniform Rainfall with Simple Outputs",
                    "Rainfall Variable in Space and/or Time and Complex Outputs",
                ],
                help="Default: unchecked, checked requires file named `dynamicinput`, \
                            unchecked uses 'peak mode' with spatially uniform rainfall",
            )
        )
        ...
        # 0=MFD,1=depth-based,2=DInfinity
        self.add_parameter(
            OptionField(
                display_name="Routing Method",
                name="routing_method",
                comment="Flag_for_outing_method._0=MFD,1=depth-based,2=DInfinity",
                value=1,
                # TODO
                help="",
                options=["MFD", "Depth-based", "DInfinity"],
            )
        )

        # 0=HawsandErickson(2020),1=Pelletieretal(inpress))
        self.add_parameter(
            OptionField(
                display_name="Rock Armor Sheer Strength",
                name="shear_stress_equation_flag",
                value=1,
                comment="Flag_for_shear_stress_equation.0=HawsandErickson(2020),1=Pelletieretal(inpress)",
                help="Default: uses [Pelletier et al. (2021)]() equation, \
                     Other option implements the rock armor shear strength equation of [Haws and Erickson (2020)]()",
                options=["Haws and Erickson (2020)", "Pelletier et al. (in press)"],
            )
        )

        self.add_parameter(
            CheckBoxField(
                name="mask_flag",
                display_name="Mask (optional)",
                value=0,
                comment="Flag_for_mask.0=nomask,1=mask",
                help="Default: unchecked, checked requires file named `mask`. If a raster (`mask`) is provided, \
                        the run restricts the model to certain portions of the input DEM \
                        (`mask values = 1` means run the model, `0` means ignore these areas).",
                conditional_field=FileField(
                    display_name="Path to required file named `mask`",
                    filename="mask.txt",
                    comment="",
                    value="",
                    name="mask_filepath",
                ),
            )
        )

        self.add_parameter(
            CheckBoxField(
                display_name="Soil & Vegetation Layer (optional)",
                name="tauc_soil_and_veg_flag",
                value=0,
                comment="Flag_for_tauc_soil_and_veg._0=fixed,1=rasterprovided",
                help="Default: unchecked,checked requires file named `taucsoilandveg`. If a raster `taucsoilandveg` \
                    is provided the model applies the shear strength of soil and veg, \
                    unchecked means a fixed value will be used.",
                conditional_field=FileField(
                    name="tauc_filepath",
                    display_name="Path to required file named `taucsoilandveg`",
                    help="Path to required file named `taucsoilandveg` as either `.tif` or `.txt`",
                    filename="taucsoilandveg.txt",
                ),
            )
        )

        self.add_parameter(
            CheckBoxField(
                name="d50_flag",
                value=0,
                comment="Flag_for_d50._0=fixed,1=rasterprovided",
                help="Default: unchecked, checked requires file named `d50`. If a raster `d50` is provided the model \
                          applies the median rock diameter, unchecked means a fixed value will be used.",
                display_name="Rock Armor Layer (optional):",
                conditional_field=FileField(
                    display_name="Path to required file named `d50`",
                    name="d50_filepath",
                    help="Path to required file named `d50` as either `.tif` or `.txt",
                    filename="d50.txt",
                ),
            )
        )

        self.add_parameter(
            CheckBoxField(
                name="rock_thickness_flag",
                value=0,
                comment="Flag_for_rock_thickness._0=fixed,1=rasterprovided",
                help="Default: unchecked, checked requires file named `rockthickness`. If a raster (`rockthickness`) is provided \
                          the model applies variable rock thickness fractions, unchecked means \
                          a fixed rock thickness value will be used.",
                display_name="Rock Thickness (optional):",
                conditional_field=FileField(
                    display_name="Path to required file named `rockthickness`",
                    name="rock_thickness_filepath",
                    help="Path to required file named `rockthickness` as either `.tif` or `.txt",
                    filename="rockthickness.txt",
                ),
            )
        )

        self.add_parameter(
            CheckBoxField(
                name="rock_cover_flag",
                value=0,
                comment="Flag_for_rock_cover._0=fixed,1=rasterprovided",
                help="Default: unchecked, checked requires file named `rockcover`. If a raster (`rockcover`) is provided \
                          the model applies the rock cover fraction, unchecked means \
                          a fixed value  will be used.",
                display_name="Rock Cover (optional):",
                conditional_field=FileField(
                    display_name="Path to rock cover raster",
                    name="rock_cover_filepath",
                    help="Path to required file named `rockcover` as either `.tif` or `.txt",
                    filename="rockcover.txt",
                ),
            )
        )
        # meters
        self.add_parameter(
            NumericField(
                name="fill_increment",
                value=0.01,
                step=0.001,
                format="%.3f",
                comment="Fill_increment_(meters)",
                help="Value in meters (m) used to fill pits and flats for the hydrologic correction step. \
                        `0.01` is a reasonable default value for lidar-based DEMs.",
                display_name="Fill increment (m):",
            )
        )
        # meter per meter
        self.add_parameter(
            NumericField(
                name="min_slope",
                value=0.01,
                step=0.001,
                format="%.3f",
                comment="_Minimum_slope_(meter per meter)",
                help="Value used to halt runoff from areas below a threshold slope steepness. \
                      Setting this value larger than 0 is useful for eliminating runoff from \
                      portions of the landscape that the user expects are too flat to produce \
                      significant runoff.",
                display_name="Minimum Slope Angle (degrees):",
            )
        )
        # pixels
        self.add_parameter(
            NumericField(
                name="expansion",
                value=1,
                comment="Expansion_(pixels)",
                help="Value (pixels) used to expand the zone where rills are predicted in \
                      the output raster. This is useful for making the areas where rilling \
                      is predicted easier to see in the model output.",
                display_name="Expansion (pixels):",
            )
        )

        self.add_parameter(
            NumericField(
                name="yellow_threshold",
                value=0.1,
                comment="Yellow_threshold",
                help="Threshold value of `f` used to indicate an area that is close to but \
                          less than the threshold for generating rills (yellow). The model will \
                          visualize any location with a `f` value between this value and 1 as \
                          potentially prone to rill generation (any area with a `f` value larger \
                          than 1 is considered prone to rill generation and is colored red).",
                display_name="Rilling Threshold (f):",
            )
        )
        # Don't initialize these, till we know the size of the image
        # TODO why should these be Static Fields vs just being stored in the object?
        self.add_parameter(
            StaticParameter(
                name="lattice_size_x",
                value=1,
                comment="Lattice_size_x",
                help="",
                display_name="Lattice Size X",
            )
        )
        self.add_parameter(
            StaticParameter(
                name="lattice_size_y",
                value=1,
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
                help="Resolution (m) $\Delta$X of the DEM is derived from the `.tif` file metadata. \
                          Review for accuracy, do not change unless something looks wrong.",
                display_name="DEM Resolution (m)",
            )
        )

        self.add_parameter(
            NumericField(
                name="no_data_value",
                value=-9999,
                comment="No_data_value",
                help="the no data null value of the DEM (m) which will be masked, defaults to `-9999",
                display_name="NoData (null)",
            )
        )
        # pixels
        self.add_parameter(
            NumericField(
                name="smoothing_length",
                value=1,
                comment="Smoothing_length_(pixels)",
                help="Length scale (pixels) for smoothing of the slope map. A length of 1 has no smoothing",
                display_name="Smoothing Length (pixels)",
            )
        )
        # m^(1/3)/s
        # ? Not sure if this is supposed ot be 1 word
        self.add_parameter(
            NumericField(
                name="manningsn",
                value=0.01,
                comment="Manning's N",
                help="",
                display_name=r"Manning's N (m^(1/3))/(s))'",
            )
        )

        self.add_parameter(
            NumericField(
                name="depth_weight_factor",
                value=0.01,
                comment="Depth_weight_factor",
                help="",
                display_name="Depth Weight Factor",
            )
        )
        self.add_parameter(
            NumericField(
                name="number_of_slices",
                value=1,
                comment="Number_of_slices",
                help="",
                display_name="Number of Slices",
            )
        )

        self.add_parameter(
            NumericField(
                name="number_of_sweeps",
                value=1,
                comment="Number_of_sweeps",
                help="",
                display_name="Number of Sweeps",
            )
        )
        # mm/hr
        self.add_parameter(
            NumericField(
                name="rain_fixed",
                value=1,
                comment="Rain_fixed_(mm/hr)",
                help="Uniform rainfall used in 'peak' mode. This value is ignored if 'Enable Dynamic Mode' flag is checked above.",
                display_name="Peak rainfall intensity (mm/hr)",
            )
        )
        self.add_parameter(
            NumericField(
                name="tauc_soil_and_veg",
                value=1,
                comment="Tauc_soil_and_vegetation",
                help="Tau C for soil and vegetation",
                display_name="Threshold shear stress for soil and vegetation (Pa)",
            )
        )

        # meters
        self.add_parameter(
            NumericField(
                name="d50_fixed",
                value=0.01,
                comment="D50_fixed_(meters)",
                help="This value is ignored if Rock Armor Flag (`d50`) is checked above.",
                display_name="Median rock armor diameter (mm)",
            )
        )
        # meters
        self.add_parameter(
            NumericField(
                name="rock_thickness_fixed",
                value=0.01,
                comment="Rock_thickness_fixed_(meters)",
                help="This value depth of rock armor. \
                          Defaults as 1 for continuous rock armors. \
                          This value is ignored if flag for 'Rock Thickness' is checked above.",
                display_name="Rock Thickness (m)",
            )
        )

        self.add_parameter(
            NumericField(
                name="rock_cover_fixed",
                value=1,
                comment="Rock_cover_fixed",
                help="This value indicates the fraction of area covered by rock armor. \
                          Will be 1 for continuous rock armors, <1 for partial rock cover. \
                          This value is ignored if flag for 'Rock Cover' is checked above.",
                display_name="Rock Cover (ratio)",
            )
        )
        self.add_parameter(
            NumericField(
                name="tan_angle_of_internal_friction",
                value=0.01,
                comment="Tan_angle_of_internal_friction",
                help="Values typically in the range of 0.5 to 0.8.",
                display_name="Tangent of the angle of internal friction",
            )
        )

        # ? b(2*(1-c)) No clue how to name this, just using b
        self.add_parameter(
            NumericField(
                name="b",
                value=1,
                comment="b(2*(1-c))",
                help="This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.",
                display_name="Coefficient of runoff to contributing area (b)",
            )
        )

        self.add_parameter(
            NumericField(
                name="c",
                value=0.01,
                comment="c",
                help="This value is the exponent in the model component that predicts the relationship between runoff and contributing area.",
                display_name="Exponent of runoff to contributing area (c)",
            )
        )
        # meters
        self.add_parameter(
            NumericField(
                name="rill_width_coefficient",
                value=0.01,
                comment="Rill_width_coefficient_(meters)",
                help="The width of rills (m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.",
                display_name="Rill Width Coefficient (m)",
            )
        )

        self.add_parameter(
            NumericField(
                name="rill_width_exponent",
                value=0.01,
                help="The width of rills (m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.",
                comment="Rill_width_exponent",
                display_name="Rill Width Exponent (m)t",
            )
        )

    """
    Function to add rillgen parameter to the object with the given name, value, comment, display_name, and other
    relevant metadata for an input field type
    """

    def add_parameter(self, field: Field):
        self.order_of_attributes.append(field.name)
        setattr(self, field.name, field)
