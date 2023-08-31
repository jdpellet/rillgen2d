from __future__ import annotations

import streamlit as st

from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Union, List, Dict, Optional

"""
    Class handling the parameters for the model, and reading/creating input.txt
"""
class Field(ABC):
    """ Interface for the parameter fields """
    @abstractmethod
    def draw(self):
        pass
    
    @abstractmethod
    def get_value(self):
        pass
    
    @abstractmethod
    def validate(self):
        raise NotImplementedError("validate method not implemented")

@dataclass(kw_only=True)
class BaseField(Field):
    name : str 
    display_name : str
    help : str = ""
    comment : str = ""
    value : Any = None
    
    
    def get_value(self):
        return self.value
    
    def validate(self):
        pass

@dataclass(kw_only=True)
class EmptyField(Field):
    def draw(self):
        pass
    
    def get_value(self):
        return super().get_value()
    
    def validate(self):
        pass

@dataclass(kw_only=True)
class OptionField(BaseField):
    options : list[str]
    conditional_field : list[Field] = None
    output : int = None # index of the selected option
    value : int = 0 # value of the selected option
    
    def _callback(self):
        self.value = 0
    
    def draw(self):
        print(self.options)
        print(self.value)
        print("="*50)
        self.output = st.selectbox(
            label=self.display_name,
            options=self.options,
            index=self.value,
            # help=self.help,
            # key=self.name,
            on_change=self._callback
        )
        print(self.output)
        if self.conditional_field:
            self.conditional_field[self.options.index(self.output)].draw()
    
    def validate(self):
        if self.conditional_field[self.output]:
            self.options[self.output].validate()
        return super().validate()
    
    def get_value(self):
        return self.options.index(self.output)
       

    
@dataclass(kw_only=True)
class CheckBoxField(BaseField):
    output : st.checkbox = None
    conditional_field : Field = None
    
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
        return super().validate()
    
    def get_value(self):
        return int(self.output)

@dataclass(kw_only=True)
class FileField(BaseField):
    path : str = ""
    output : st.text_input = None
    def draw(self):
            self.output = st.text_input(
                self.display_name,
                help=self.help,
                key=self.name,
            )
    
    def validate(self):
        if not Path(FileField.output).exists:
            raise FileNotFoundError(f"File {FileField.output} does not exist")
        

@dataclass(kw_only=True)
class NumericField(BaseField):
    output : st.number_input = None
    def draw(self):
        self.output = st.number_input(
            self.display_name,
            help = self.help,
            key = self.name,
            value = self.value
        )

@dataclass(kw_only=True)
class StaticParameter(BaseField):
    def draw(self):
        pass
    def get_value(self):
        return self.value
    

