#!/usr/bin/python3
"""
This file defines the storage system (File System) for the project.
It uses JSON format to serialize or deserialize an object.
"""

import json
from json.decoder import JSONDecodeError
from .errors import ModelNotFoundError, InstanceNotFoundError
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from datetime import datetime


class FileStorage:
    """This class serves as an ORM to interface between our Storage System."""

    # Class private variables
    __objects = {}
    __file_path = "file.json"
    models = (
        "BaseModel", "User", "City", "State", "Place",
        "Amenity", "Review"
    )

    def __init__(self):
        pass

    def all(self):
        """Returns the dictionary __objects."""
        return FileStorage.__objects

    def new(self, obj):
        """Adds a new object to __objects with the key <obj_class_name>.id."""
        key = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects[key] = obj

    def save(self):
        """Serializes __objects to the JSON file specified by __file_path."""
        serialized = {
            key: val.to_dict()
            for key, val in self.__objects.items()
        }
        with open(FileStorage.__file_path, "w") as f:
            f.write(json.dumps(serialized))

    def reload(self):
        """Deserializes the JSON file to __objects, if it exists."""
        try:
            deserialized = {}
            with open(FileStorage.__file_path, "r") as f:
                deserialized = json.loads(f.read())
                FileStorage.__objects = {
                    key: eval(obj["__class__"])(**obj)
                    for key, obj in deserialized.items()
                }
        except (FileNotFoundError, JSONDecodeError):
            pass

    def find_by_id(self, model, obj_id):
        """
        Finds an object by its model name and ID.

        Args:
            model (str): The name of the model.
            obj_id (str): The ID of the object.

        Raises:
            ModelNotFoundError: If the model is not registered.
            InstanceNotFoundError: If the object is not found.

        Returns:
            Object: The instance of the found object.
        """
        if model not in FileStorage.models:
            raise ModelNotFoundError(model)

        key = model + "." + obj_id
        if key not in FileStorage.__objects:
            raise InstanceNotFoundError(obj_id, model)

        return FileStorage.__objects[key]

    def delete_by_id(self, model, obj_id):
        """
        Deletes an object by its model name and ID.

        Args:
            model (str): The name of the model.
            obj_id (str): The ID of the object.

        Raises:
            ModelNotFoundError: If the model is not registered.
            InstanceNotFoundError: If the object is not found.
        """
        if model not in FileStorage.models:
            raise ModelNotFoundError(model)

        key = model + "." + obj_id
        if key not in FileStorage.__objects:
            raise InstanceNotFoundError(obj_id, model)

        del FileStorage.__objects[key]
        self.save()

    def find_all(self, model=""):
        """
        Finds all objects of a given model.

        Args:
            model (str, optional): The name of the model. Defaults to "".

        Raises:
            ModelNotFoundError: If the model is not registered.

        Returns:
            List: A list of all instances of the specified model.
        """
        if model and model not in FileStorage.models:
            raise ModelNotFoundError(model)
        results = []
        for key, val in FileStorage.__objects.items():
            if key.startswith(model):
                results.append(str(val))
        return results

    def update_one(self, model, obj_id, field, value):
        """
        Updates a single field of an object.

        Args:
            model (str): The name of the model.
            obj_id (str): The ID of the object.
            field (str): The field to update.
            value: The new value for the field.

        Raises:
            ModelNotFoundError: If the model is not registered.
            InstanceNotFoundError: If the object is not found.
        """
        if model not in FileStorage.models:
            raise ModelNotFoundError(model)

        key = model + "." + obj_id
        if key not in FileStorage.__objects:
            raise InstanceNotFoundError(obj_id, model)

        if field in ("id", "updated_at", "created_at"):
            return

        inst = FileStorage.__objects[key]
        try:
            vtype = type(inst.__dict__[field])
            inst.__dict__[field] = vtype(value)
        except KeyError:
            inst.__dict__[field] = value
        finally:
            inst.updated_at = datetime.utcnow()
            self.save()
