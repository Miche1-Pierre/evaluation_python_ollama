import json

class JsonFile:
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, "r", encoding = "utf-8") as file:
            return json.load(file)

    def write(self, data):
        with open(self.path, "w", encoding = "utf-8") as file:
            json.dump(data, file, ensure_ascii = False, indent = 2)