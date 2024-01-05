from pydantic import Field


class PropertyCategory:
    default = Field(category="Default")
    events = Field(category="Events")
    display_rules = Field(category="Display Rules")
    validation = Field(category="Validation")
    other = Field(category="Other")
