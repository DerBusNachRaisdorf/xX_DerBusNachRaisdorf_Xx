import os
import math

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageFilter


def make_offensive_image(text: str):
    # Open an Image
    img = Image.open(os.path.join('resources', 'memes', 'torvaldsnvidia-640x424.jpg'))

    fontsize: int = (550 * 2) // math.ceil(math.sqrt(len(text)) + 6)  # This is ugly and bad but good enough for this bs
    my_font = ImageFont.truetype(os.path.join('resources', 'fonts', 'Impacted.ttf'), fontsize)

    # Add Text to an image
    # I1.text((36, 350 - fontsize), text, fill=(255, 255, 255), font=my_font)
    x, y = img.size
    # calc new coords
    new_coords = (x // 2, (y * 0.9) // 1)
    # draw drop shadow
    on_top = Image.new("RGBA", (x, y))
    I2 = ImageDraw.Draw(on_top)
    I2.text(new_coords, text, fill=(0, 0, 0), font=my_font, align="center", anchor="mb")
    # paste drop shadow on other image
    blurred = on_top.filter(ImageFilter.GaussianBlur(radius=15))
    # img.merge("RGB", (blurred, blurred, blurred))

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)
    # add normal text
    I1.text(new_coords, text, fill=(255, 255, 255), font=my_font, align="center", anchor="mb")

    # Save the edited image
    filename = f'offensive_image_{__to_legal_filename(text)}.png'
    path = os.path.join('tmp', filename)
    try:
        img.save(path, )
    except:
        return None

    return path


def __to_legal_filename(text: str) -> str:
    result = [c if c.isalnum() else '' for c in text]
    return ''.join(result)
