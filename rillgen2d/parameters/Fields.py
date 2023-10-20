from __future__ import annotations

import streamlit as st

from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Union, Optional


# Abstract base class defining the interface for parameter fields
class Field(ABC):
    # Method to render the UI component
    @abstractmethod
    def draw(self, disabled: bool) -> None:
        pass

    # Method to obtain the value from the UI component
    @abstractmethod
    def get_value(self) -> Any:
        pass

    # Method to validate the value obtained from the UI component
    @abstractmethod
    def validate(self) -> None:
        pass

    # Method to obtain the inner type of the field value
    def get_inner_type(self) -> type:
        return type(self)


# Data class for handling basic field attributes and behaviors
@dataclass(kw_only=True)
class BaseField(Field):
    name: str
    display_name: str
    help: str = ""
    comment: str = ""
    value: Any = None

    # Validation method (no implementation since it's handled in specific field classes)
    def validate(self) -> None:
        pass


@dataclass(kw_only=True)
class EmptyField(Field):
    def draw(self, disabled):
        pass

    def validate(self):
        pass

    def get_value(self):
        return self.value


# Example for a specific field class:
@dataclass(kw_only=True)
class OptionField(BaseField):
    options: list[str]
    conditional_field: Optional[list[Field]] = None
    output: Optional[int] = None  # index of the selected option
    value: int = 0  # value of the selected option

    # Method to get the index of the selected option
    def _index(self) -> int:
        return self.options.index(self.output)

    # Method to render a dropdown selection box in the UI
    def draw(self, disabled: bool) -> None:
        self.output = st.selectbox(
            label=self.display_name,
            options=self.options,
            index=self.value,
            # help=self.help,
            # key=self.name,
            disabled=disabled,
        )
        # Draw additional fields based on selected option if applicable
        if self.conditional_field:
            self.conditional_field[self._index()].draw(disabled)

    # Validate the field's value and optionally validate conditional fields
    def validate(self) -> Optional[str]:
        if self.conditional_field:
            err = self.conditional_field[self._index()].validate()
            if err:
                err += f" for '{self.display_name}'"
            return err
        return super().validate()

    def get_inner_value(self):
        out = self.get_inner_parameter()
        return out.get_inner_value() if out else None

    def get_inner_type(self):
        out = self.get_inner_parameter()
        return out.get_inner_type() if out else None

    def get_inner_parameter(self):
        if self.output and self.conditional_field:
            return self.conditional_field[self._index()]
        else:
            return None

    def get_value(self):
        return self._index()


@dataclass(kw_only=True)
class CheckBoxField(BaseField):
    output: Optional[bool] = None  # Checked state of the checkbox
    conditional_field: Optional[Field] = None

    def draw(self, disabled: bool) -> None:
        """Renders a checkbox in the UI and conditionally draws additional fields."""
        self.output = st.checkbox(
            self.display_name,
            help=self.help,
            key=self.name,
            disabled=disabled,
        )
        if self.output and self.conditional_field:
            self.conditional_field.draw(disabled)

    def validate(self) -> Optional[str]:
        """Validates the checkbox state and conditionally validates additional fields."""
        if self.output and self.conditional_field:
            err = self.conditional_field.validate()
            if err:
                err += f" for {self.display_name}"
            return err
        return super().validate()

    def get_value(self) -> int:
        """Returns the checkbox state as an integer."""
        return int(self.output)

    def get_inner_value(self):
        out = self.get_inner_parameter()
        return out.get_inner_value() if out else None

    def get_inner_type(self):
        out = self.get_inner_parameter()
        return out.get_inner_type() if out else None

    def get_inner_parameter(self):
        if self.output and self.conditional_field:
            return self.conditional_field
        else:
            return None


@dataclass(kw_only=True)
class FileField(BaseField):
    output: Optional[str] = None  # Path to the selected file
    filename: str = None

    def draw(self, disabled: bool) -> None:
        """Renders a text input in the UI for file path entry."""
        self.output = st.text_input(
            self.display_name,
            help=self.help,
            key=self.name,
            disabled=disabled,
        )

    def validate(self) -> Optional[str]:
        """Validates the existence of the file at the specified path."""
        if not Path(self.output).is_file() or not self.output:
            return f"File {self.output} does not exist"
        return super().validate()

    def get_value(self) -> str:
        """Returns the path to the selected file."""
        return self.output


@dataclass(kw_only=True)
class NumericField(BaseField):
    output: Optional[int | float] = None  # Entered numeric value
    step: float | int | None = None  # Step size for input increments
    format: Optional[str] = None  # Display format for the numeric input

    def get_value(self) -> Union[int, float]:
        """Returns the entered numeric value."""
        return self.output

    def draw(self, disabled: bool) -> None:
        """Renders a numeric input in the UI."""
        self.output = st.number_input(
            self.display_name,
            help=self.help,
            step=self.step,
            format=self.format,
            key=self.name,
            value=self.value,
            disabled=disabled,
        )


@dataclass(kw_only=True)
class StaticParameter(BaseField):
    def draw(self, disabled: bool) -> None:
        """No UI rendering for static parameters."""
        pass

    def get_value(self) -> Any:
        """Returns the static value."""
        return self.value
