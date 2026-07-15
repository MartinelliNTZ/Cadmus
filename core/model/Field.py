# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..enum import MetadataFieldKey


@dataclass
class Field:
    normalized: Optional[str] = None
    core: Optional[str] = None
    label: Optional[str] = None
    attribute: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    type: Optional[int] = None
    length: Optional[int] = None
    precision: Optional[int] = None
    key: Optional["MetadataFieldKey"] = None
