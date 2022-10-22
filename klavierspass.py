#!/bin/python3
import argparse
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

def tannenbaum():
    notes=[" d' g' g' g'   a' h' h' h'",
           " h' a' h' c'' fis' a' g'",
           " d'' d'' h' e'' d'' d'' c'' c''",  
           " c'' c'' a' d'' c'' c'' h' h'"]
    images=arange_image(notes, title='Oh Tannenbaum', author='Weihnachten', space=0 ,line_h=800, scale=.3, note_w=200)
    #images[0].show()
    save_pdf(images, 'oh_tannenbaum.pdf')
    
def swarn():
    notes =[" e''  a' h' c'' d'' e''  c'' e''  c'' e''"," a' c'' a' f' c'' a'  f' d'' c'' h' e''"]
    images=arange_image(notes, title='Schwanensee', author='Tchaikovsky', space=0 ,line_h=800, scale=.3, note_w=200,height=2480, width=3508)
    save_pdf(images, 'swarnlake.pdf')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set notes sheets with images')
    parser.add_argument('infile',  type=str, help='textfile with notes')
    parser.add_argument('--title', help='song title', required=True)
    parser.add_argument('--author', help='song author', default='')
    parser.add_argument('--space', help='space between lines in pixels', type=int, default=0)
    parser.add_argument('--hline', help='line heigth in pixels',type=int,  default=800)
    parser.add_argument('--scale', help='scaling factor for the note images', default=.3)
    parser.add_argument('--note_w', help='space between notes in pixels',type=int,  default=200)
    parser.add_argument('--height', help='sheet height in pixels',type=int,  default=2480)
    parser.add_argument('--width', help='sheet width in pixels',type=int,  default=3508)
    parser.add_argument('--outfile', help='filename for output', default=None)
    args = parser.parse_args()
    with open(args.infile) as f:
        notes=[l.strip() for l in f.readlines()]
    print(notes)
    images=arange_image(notes, title=args.title, author=args.author, space=args.space, 
                        line_h=args.hline, scale=args.scale, note_w=args.note_w,
                        height=args.height, width=args.width)
    if args.outfile is None:
        outfile=args.title.replace(' ','_')+'.pdf'
    else:
        outfile=args.outfile

    save_pdf(images, outfile)

