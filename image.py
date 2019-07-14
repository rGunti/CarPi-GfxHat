from PIL import Image, ImageDraw
from gfxhat import lcd


def clear():
    lcd.clear()
    lcd.show()


def render(SCR, SIZ):
    for x in range(SIZ[0]):
        for y in range(SIZ[1]):
            lcd.set_pixel(x, y, SCR.getpixel((x, y)))

        lcd.show()


clear()

SIZ = lcd.dimensions()

SCR = Image.new('P', SIZ)
SCD = ImageDraw.Draw(SCR)
SCD.line((0, 0, SIZ[0] - 1, SIZ[1] - 1), fill=True)
SCD.line((SIZ[0] - 1, 0, 0, SIZ[1] - 1), fill=True)
render(SCR, SIZ)

IMG: Image.Image = Image.open("res/seat64.png")
for x in range(IMG.size[0]):
    for y in range(IMG.size[1]):
        p = IMG.getpixel((x, y))
        if p[3] > 128:
            SCD.point((x + 32, y), fill=True)

#SCR.paste(IMG.convert('P').copy(), (32, 0))

render(SCR, SIZ)
