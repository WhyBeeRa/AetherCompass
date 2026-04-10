from PIL import Image
import os

filepath = "logo.png.png"
if not os.path.exists(filepath):
    print("File not found.")
    exit(1)

# Open the logo image
img = Image.open(filepath)

# Let's crop the top part of the image, where the brain/compass icon is.
# The image dimensions are around right for 16:9 like 1024x576 or 1920x1080
# The text is at the bottom. We'll leave the central icon.
width, height = img.size
print(f"Original size: {width}x{height}")

# I will crop out the center area with the brain/compass, assuming standard centered position.
# We'll calculate roughly, but we can also do a square crop of the center top.
# For a 1920x1080 image, the brain icon is roughly in a square 800x800 in the top middle.
# Let's crop a square from the top-middle.
crop_width = min(width, height) * 0.7  
crop_height = min(width, height) * 0.7

left = (width - crop_width) / 2
# It looks slightly above absolute center, maybe start from y=0 or height*0.05
top = height * 0.05
right = left + crop_width
bottom = top + crop_height

img_cropped = img.crop((left, top, right, bottom))
img_cropped.save("logo_cropped.png")
print("Cropped logo saved as logo_cropped.png")
