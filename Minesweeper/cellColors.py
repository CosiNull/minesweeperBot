from PIL import Image
import pickle
from screenshot import pixel
from screenshot import halfPixel

cellTypes = ["0", "00", "1", "2", "3", "4",
             "44", "5", "6", "66", "9", "99", "-1"]

cellColors = {}

pixelCoordinate = (round(pixel*0.5), round(pixel*0.27))


for code in cellTypes:
    examinedImg = Image.open(code+"/1.png")
    examinedImgRGB = examinedImg.convert("RGB")
    pixelColor = examinedImgRGB.getpixel(pixelCoordinate)

    cellColors[code] = pixelColor


pickle.dump(cellColors, open("colors.p", "wb"))

print(cellColors)
