#!/bin/python3
import pkg_resources
import imageio
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import numpy as np
import os
from PIL.PngImagePlugin import PngImageFile, PngInfo

note_offset={n:o for o,n in enumerate('cdefgah')}
note_offset['fis']=note_offset['f']
note_offset['b']=note_offset['h']



def arange_image(notes, title='', author='',width=2480, height=3508, scale=.25,space=30,font_size=(100,80) , mar=140,line_h=600, note_w=150):
    out=[Image.fromarray(255*np.ones((int(height),int(width),3), np.uint8))]
    fnt = [ImageFont.truetype('FreeMono.ttf', sz) for sz in font_size]
    d = ImageDraw.Draw(out[-1])
    w, h = d.textsize(title, font=fnt[0])
    d.text(((width-w)/2,mar),title, font=fnt[0], fill=0)
    w2, h2= d.textsize(author, font=fnt[1])
    d.text((width-mar-w2,mar+h), author, font=fnt[1], fill=0)
    print(f'arage images of size {width}x{height}')
    n_notes=int((width-2*mar)/note_w)
    offset=[mar,mar+h+h2-line_h]
    line_count=0
    
    for note_line in notes:
        note_count=n_notes #force newline
        for note in note_line.split(' '):
            note_count+=1
            if note_count>= n_notes:
                note_count=0
                line_count+=1
                offset[1]+=line_h+space
                lines=(255*np.ones((line_h,int(width-2*mar))))
                for i in range(5):
                    lines[int((i+3)*line_h/10),:]=0
                out[-1].paste(Image.fromarray(lines), (mar,offset[1])) 
                
            offset[0]=mar+note_w*note_count
            if note=='|':
                patch=Image.fromarray(np.zeros((int(line_h/10*4),1)))
                out[-1].paste(patch, (int(offset[0]+note_w/2),int(offset[1]+line_h/10*3) ))
            elif note:
                octarve=1
                while note[-1]=="'":
                    octarve+=1
                    note=note[:-1]
                patch=load_image(f'images/{note}_{octarve}.png')
                patch=patch.resize((int(x*scale) for x in reversed(np.array(patch).shape[:-1])))
                out[-1].paste(patch, (offset[0],int(offset[1]-(note_offset[note]+octarve*7-29)*line_h/20)),patch) 


    return out

def load_image(filename):
    img = Image.open(filename)
    img = img.convert("RGBA")
    pixdata = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            if pixdata[x, y] == (255, 255, 255, 255):
                pixdata[x, y] = (255, 255, 255, 0)
    return(img)

    img=PngImageFile(filename)
    return(img)

def save_pdf(images, filename):
    print(f'saving {len(images)} pages to {filename}')
    if len(images)==1:
        images[0].save(filename)
    else:
        images[0].save(filename,save_all=True, append_images=images[1:])

def main():
    notes=[" d' h' a' g' d'  d' d' d' h' a' g' e'",
           " e' c'' h' a' fis'    d'' d'' c'' a' h'",
           " d' h' a' g' d'    d' h' a' g' e'",
           "e' e' c'' h' a' d'' d'' d'' d'' e'' d'' c'' a' g'",
           "d'' h' h' h'  h' h' h'  h' d'' g' a' h'",
           "c'' c'' c'' c'' c'' h' h' h' h' h' a' a' h' a' d'"]
    images=arange_image(notes, title='Jingle Bells', author='Weihnachten', space=0 ,line_h=500, scale=.22, note_w=140)
    #image[0].show()
    save_pdf(images, 'jinglebells.pdf')

if __name__ == "__main__":
    main()
