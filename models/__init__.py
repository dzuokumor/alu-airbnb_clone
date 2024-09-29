#!/usr/bin/python3
"""Initializes the storage system for the Airbnb clone project"""

from models.engine.file_storage import FileStorage

# Create the `storage` instance and load existing data from the file.
storage = FileStorage()
storage.reload()

