from pydantic import Field


class PropertyCategory:
    default = Field(category="Default")
    events = Field(category="Events")
    display_rules = Field(category="Display Rules")
    validation = Field(category="Validation")
    view_only = Field(category="View Only")
    other = Field(category="Other")
    internal = Field(category="Internal")
