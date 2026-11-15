"""Small synthetic image providers used only by UI tests."""
from PIL import Image
from app.ui.surfaces import BackdropSurface


def solid_surface(widget,color):
    return BackdropSurface(widget,Image.new('RGB',(1,1),color))
