from __future__ import annotations

import streamlit as st

from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Union, List, Dict, Optional, Callable

"""
    Class handling the parameters for the model, and reading/creating input.txt
"""


class Field(ABC):
    """Interface for the parameter fields"""

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def validate(self):
        raise NotImplementedError("validate method not implemented")
    
    def get_inner_type(self):
        return type(self)


@dataclass(kw_only=True)
class BaseField(Field):
    name: str
    display_name: str
    help: str = ""
    comment: str = ""
    value: Any = None

    def get_value(self):
        return self.value

    def validate(self):
        pass


@dataclass(kw_only=True)
class EmptyField(Field):
    def draw(self):
        pass

    def get_value(self):
        return self.value

    def validate(self):
        pass


@dataclass(kw_only=True)
class OptionField(BaseField):
    options: list[str]
    conditional_field: list[Field] = None
    output: int = None  # index of the selected option
    value: int = 0  # value of the selected option

    def _callback(self):
        self.value = 0

    def draw(self):
        self.output = st.selectbox(
            label=self.display_name,
            options=self.options,
            index=self.value,
            # help=self.help,
            # key=self.name,
            on_change=self._callback,
        )
        if self.conditional_field:
            self.conditional_field[self.options.index(self.output)].draw()

    def validate(self):
        if self.conditional_field:
            err = self.conditional_field[self.options.index(self.output)].validate()
            if err:
                err+= f" for '{self.display_name}'"
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
            return self.conditional_field[self.options.index(self.output)]
        else:
            return None



@dataclass(kw_only=True)
class CheckBoxField(BaseField):
    output: st.checkbox = None
    conditional_field: Field = None

    def _callback(self):
        self.value = self.output
        if self.output and self.conditional_field:
            self.conditional_field.draw()

    def draw(self):
        self.output = st.checkbox(
            self.display_name,
            help=self.help,
            key=self.name,
        )
        if self.output and self.conditional_field:
            self.conditional_field.draw()

    def validate(self):
        if self.output and self.conditional_field:
            err = self.conditional_field.validate()
            if err:
                err += f" for {self.display_name}"
            return err
        return super().validate()

    def get_value(self):
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
    output: st.text_input = None
    filename : str = None

    def draw(self):
        self.output = st.text_input(
            self.display_name,
            help=self.help,
            key=self.name,
        )

    def validate(self):
        if not Path(self.output).is_file() or not self.output:
            return f"File {self.output} does not exist"
        return super().validate()
    
    def get_value(self):
        return self.output
        



@dataclass(kw_only=True)
class NumericField(BaseField):
    output: st.number_input = None
    step: float | int = None
    format: str = None

    def draw(self):
        self.output = st.number_input(
            self.display_name,
            help=self.help,
            step=self.step,
            format=self.format,
            key=self.name,
            value=self.value,
        )


@dataclass(kw_only=True)
class StaticParameter(BaseField):
    def draw(self):
        pass

    def get_value(self):
        return self.value
