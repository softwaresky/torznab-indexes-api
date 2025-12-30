from typing import Iterable, Type
from pydantic import BaseModel, create_model
import inspect

def merge_models(name: str, *models: Type[BaseModel]) -> Type[BaseModel]:
    fields = {}
    properties = {}

    for model in models:
        # Normal fields
        f = {k: (v.annotation, v) for k, v in model.model_fields.items()}
        fields.update(f)

        # Regular properties (runtime-only)
        for attr_name, attr_value in inspect.getmembers(model, predicate=lambda x: isinstance(x, property)):
            # Skip if property name is already a field
            if attr_name not in fields:
                properties[attr_name] = attr_value

    # Create model with normal fields
    merged_model = create_model(name, **fields)

    # Add properties dynamically to the new class
    for k, v in properties.items():
        setattr(merged_model, k, v)

    return merged_model