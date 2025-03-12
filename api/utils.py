from uuid import uuid4

def generate_image_name(filename):
    extension = filename.split('.')[-1]
    new_filename = uuid4().hex + '.' +extension
    return new_filename