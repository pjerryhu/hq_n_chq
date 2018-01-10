from PIL import Image, ImageEnhance
import os


def process_image(img):
    width, height = img.size
    img = img.crop((width*0.1, height*0.22, width*0.9, height * 0.68))

    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(2)

    img = img.convert("L")
    threshold = 230
    img = img.point(lambda p: p > threshold and 255)

    img.show()

    return img

SCREEN_DIR = "/Users/pengxianghu/Projects/hq_OCR/hqcheat/py-version"
IDENTIFIER = "booted_image"

screen_shots = list(filter(
    lambda p: IDENTIFIER in p, os.listdir(SCREEN_DIR)))
file_path = os.path.join(SCREEN_DIR, screen_shots[0])
screen = process_image(Image.open(file_path))
# screen.save(SCREEN_DIR + "/test.png")
