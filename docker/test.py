import tkinter as tk
from PIL import ImageTk
from PIL import Image
import os

root = tk.Tk()

def show_image():
    canvas3bg = Image.open(os.getcwd() + "/hillshade.png")
    canvas3fg = Image.open(os.getcwd() + "/color-relief.png")
    new_img = Image.open(os.getcwd() + "/hillshade.png")


    
    bgcpy = canvas3bg.copy()
    fgcpy = canvas3fg.copy()
    bgcpy = bgcpy.convert("RGBA")
    fgcpy = fgcpy.convert("RGBA")
    alphablended = Image.blend(bgcpy, fgcpy, alpha=.4)
    blended_image = Image.new("RGBA", alphablended.size)
    blended_image.paste(alphablended)
    blended_image.save("background.png")
    img_label = tk.Label(root)
    im = Image.open("background.jpg")
    print(im)
    img_label.image = ImageTk.PhotoImage(im)
    img_label['image'] = img_label.image

    img_label.pack()


show_image()
root.mainloop()