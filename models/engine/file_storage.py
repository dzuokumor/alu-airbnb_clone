#!/usr/bin/python3
"""
This File defines the storage system (File System)
For the project.
It uses json format to serialize or deserialize
an object"""

import json
from json.decoder import JSONDecodeError
from .errors import *
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from datetime import datetime

class FileStorage:
        """This class serve as an ORM to interface between or Storage System"""
        # class private variables
        __objects = {}
        __file_path = "file.json"
        models = (
                "BaseModel",
                "User", "City", "State", "Place",
                "Amenity", "Review"
         )

        def __init__(self):
            pass

        def all(self):
            return FileStorage.__objects

        def new(self, obj):
            key = "{}.{}".format(type(obj).__name__, obj.id)
            FileStorage.__objects[key] = obj

        def save(self):
            serialized = {
                key: val.to_dict()
                for key, val in self.__objects.items()
            }
            with open(FileStorage.__file_path, "w") as f:
                f.write(json.dumps(serialized))

        def reload(self):
             try:
                deserialized = {}
                with open(FileStorage.__file_path, "r") as f:
                    deserialized = json.loads(f.read())
                    FileStorage.__objects = {
                    key:
                        eval(obj["__class__"])(**obj)
                        for key, obj in deserialized.items()}
             except (FileNotFoundError, JSONDecodeError):
                pass

        def find_by_id(self, model, obj_id):
            F = FileStorage
            if model not in F.models:
                raise ModelNotFoundError(model)

            key = model + "." + obj_id
            if key not in F.__objects:
                raise InstanceNotFoundError(obj_id, model)

            return F.__objects[key]

        def delete_by_id(self, model, obj_id):
            F = FileStorage
            if model not in F.models:
                raise ModelNotFoundError(model)

            key = model + "." + obj_id
            if key not in F.__objects:
                raise InstanceNotFoundError(obj_id, model)

            del F.__objects[key]
            self.save()

        def find_all(self, model=""):
            if model and model not in FileStorage.models:
                raise ModelNotFoundError(model)
            results = []
            for key, val in FileStorage.__objects.items():
                if key.startswith(model):
                    results.append(str(val))
            return results

        def update_one(self, model, iid, field, value):
            F = FileStorage
            if model not in F.models:
                raise ModelNotFoundError(model)

            key = model + "." + iid
            if key not in F.__objects:
                raise InstanceNotFoundError(iid, model)
            if field in ("id", "updated_at", "created_at"):
                return
            inst = F.__objects[key]
            try:
                vtype = type(inst.__dict__[field])
                inst.__dict__[field] = vtype(value)
            except KeyError:
                inst.__dict__[field] = value

            finally:
                inst.updated_at = datetime.utcnow()
                self.save()


