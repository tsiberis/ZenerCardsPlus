#!/usr/bin/env python

'''
This game is the natural evolvement of the zenerpoker game I wrote back at 2006.

Started coding at 8/24/2011 and finished at 11/12/2011.

In the middle of the world economic crisis here's a free 4 all game.
'''

#-------------------Imports-------------------
import pygame
from pygame.locals import *
from os import path
from random import randint
from math import sin, cos, tan, pi, sqrt
from sys import platform

#-------------------Constants-------------------
SIZE = (650,265)
VERSION = '0.2'
DATA_FOLDER = 'zenercards+data'
PLATFORM = platform
if PLATFORM.startswith('linux'):
    _FONT = 'BitstreamVeraSerif'
else:
    _FONT = 'TimesNewRoman'
CLOCK = pygame.time.Clock()

#-------------------Global functions-------------------
def load_sound(name):
    return pygame.mixer.Sound(path.join(DATA_FOLDER, name))

def load_image(name, colorkey=None):
    fullname = path.join(DATA_FOLDER, name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is -1:
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def display_some_text(text,size,place,background,orientation):
    font = pygame.font.SysFont(_FONT, size)
    t = font.render(text, 1, Color("black"))
    trect = t.get_rect()
    if orientation == 0:
        trect.left = place[0]
        trect.top = place[1]
    elif orientation == 1:
        trect.centerx = place[0]
        trect.centery = place[1]
    elif orientation == 2:
        trect.right = place[0]
        trect.top = place[1]
    background.blit(t, trect)

#-------------------Classes-------------------
class simple_button:
    def __init__(self,x,y,title,background,small=0):
        self.background = background
        if small:
            self.image = pygame.Surface([80,30])
        else:
            self.image = pygame.Surface([95,25])
        self.image.fill(Color("burlywood"))
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        if background.mustlock():background.lock()
        # Draw the border
        pygame.draw.rect(self.image,Color("black"),(0,0,self.rect.width,self.rect.height),1)
        # Draw some shadow lines
        pygame.draw.line(background,Color("black"),(x+1,y+self.rect.height),(x+self.rect.width-1,y+self.rect.height)) #horizontal
        pygame.draw.line(background,Color("black"),(x+self.rect.width,y+1),(x+self.rect.width,y+self.rect.height)) #vertical
        if background.get_locked():background.unlock()
        # Display some text
        display_some_text(title,21,(self.rect.width/2,self.rect.height/2),self.image,1)
        self.background.blit(self.image,self.rect)
        self.status = 0
        self.is_dirty = 0
    def press(self):
        self.rect.inflate_ip(-2,-2)
        self.status = 1
        self.is_dirty = 1
    def unpress(self):
        self.rect.inflate_ip(2,2)
        self.status = 0
        self.is_dirty = 1
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_dirty:
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0

class check_box:
    def __init__(self,background,text,position):
        self.background = background
        self.font_size = 21
        self.thickness = 2

        image1 = pygame.font.SysFont(_FONT,self.font_size).render(text, 1, Color("black"))
        w1 = image1.get_width()
        self.h1 = image1.get_height()

        self.image = pygame.Surface((self.h1+w1,self.h1)).convert()
        self.image.fill(Color("burlywood"))
        self.image.blit(image1,(self.h1,0))

        self.image2 = pygame.Surface((self.h1,self.h1)).convert()
        self.image2.fill(Color("burlywood"))
        if self.image2.mustlock():self.image2.lock()
        self.dim = self.font_size/6
        pygame.draw.rect(self.image2, Color("black"), (self.dim,self.dim,self.h1 - self.dim*2,self.h1 - self.dim*2), self.thickness)
        if self.image2.get_locked():self.image2.unlock()
        self.image.blit(self.image2,(0,0))

        self.rect = self.image.get_rect(topleft=position)
        self.background.blit(self.image,self.rect)
        self.is_highlighted = 0
        self.is_checked = 0
        self.is_dirty = 0
    def highlight(self,flag):
        if flag == 1:
            _color = "darkseagreen4"
            self.is_highlighted = 1
        else:
            _color = "burlywood"
            self.is_highlighted = 0
        if self.image2.mustlock():self.image2.lock()
        pygame.draw.rect(self.image2, Color(_color), (self.dim + self.thickness,self.dim + self.thickness, self.h1 - self.dim*2 - self.thickness*2,self.h1 - self.dim*2 - self.thickness*2), self.thickness)
        if self.image2.get_locked():self.image2.unlock()
        self.image.blit(self.image2,(0,0))
        self.is_dirty = 1
    def check(self,flag):
        if flag == 1:
            _color = "black"
            self.is_checked = 1
        else:
            _color = "burlywood"
            self.is_checked = 0
        if self.image2.mustlock():self.image2.lock()
        pygame.draw.line(self.image2, Color(_color), (self.dim + self.thickness*2, self.h1/2),(self.h1/2, self.h1 - self.dim - self.thickness*2),self.thickness)
        pygame.draw.line(self.image2, Color(_color), (self.h1/2, self.h1 - self.dim - self.thickness*2),(self.h1 - self.dim - self.thickness*2, self.dim + self.thickness*2),self.thickness)
        if self.image2.get_locked():self.image2.unlock()
        self.image.blit(self.image2,(0,0))
        self.is_dirty = 1
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_dirty:
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0

class small_card_place:
    def __init__(self,background,image,image2,topleft,face_up,_index):
        self.background = background
        self.image = image
        self.image2 = image2
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.face_up = face_up
        if self.face_up:
            self.background.blit(self.image,self.rect)
        else:
            self.background.blit(self.image2,self.rect)
        self._index = _index
        self.has_border = 0
        self.is_selected = 0
        self.is_dirty = 0
    def draw_border(self,flag):
        if flag:
            _color = "black"
            self.has_border = 1
        else:
            _color = "white"
            self.has_border = 0
        if self.image.mustlock():self.image.lock()
        pygame.draw.rect(self.image, Color(_color), (0,0,79,104), 2)
        if self.image.get_locked():self.image.unlock()
        self.is_dirty = 1
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_dirty:
            if self.face_up:
                self.background.blit(self.image,self.rect)
            else:
                self.background.blit(self.image2,self.rect)
            self.is_dirty = 0

class big_card_place:
    def __init__(self,background,image,image2,topleft,face_up,_index):
        self.background = background
        self.image = image
        self.image2 = image2
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.face_up = face_up
        if self.face_up:
            self.background.blit(self.image,self.rect)
        else:
            self.background.blit(self.image2,self.rect)
        self._index = _index
        self.is_dirty = 0
    def update(self):
        if self.is_dirty:
            if self.face_up:
                self.background.blit(self.image,self.rect)
            else:
                self.background.blit(self.image2,self.rect)
            self.is_dirty = 0

class message_board:
    def __init__(self,background):
        self.background = background
        self.image = pygame.Surface((160,25)).convert()
        self.image.fill(Color("burlywood"))
        self.rect = self.image.get_rect()
        self.rect.topleft = (20,235)
        self.text1 = "Click on face ups"
        display_some_text(self.text1,21,(self.rect.width/2,self.rect.height/2),self.image,1)
        self.background.blit(self.image,self.rect)
        self.is_dirty = 0
    def update(self,text="Click on face ups"):
        if self.is_dirty:
            self.image.fill(Color("burlywood"))
            display_some_text(text,21,(self.rect.width/2,self.rect.height/2),self.image,1)
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0

class cards:
    def __init__(self,background):
        self.big_card_back = self.card_back()
        self.big_square = self.square(3)
        self.big_cross = self.cross(3)
        self.big_circle = self.circle(3)
        self.big_star = self.star(3)
        self.big_waves = self.waves(3)
        self.big_hexagon = self.hexagon(3)
        self.big_quadrifolium = self.quadrifolium(3)
        self.big_spiral = self.spiral(3)
        self.big_rhombus = self.rhombus(3)
        self.big_mandelbrot = self.mandelbrot(3)

        self.small_card_back = self.card_back(1)
        self.small_square = self.square(2)
        self.small_cross = self.cross(2)
        self.small_circle = self.circle(2)
        self.small_star = self.star(2)
        self.small_waves = self.waves(2)
        self.small_hexagon = self.hexagon(2)
        self.small_quadrifolium = self.quadrifolium(2)
        self.small_spiral = self.spiral(2)
        self.small_rhombus = self.rhombus(2)
        self.small_mandelbrot = self.mandelbrot(2)
        
        self.tiny_square = self.square(1)
        self.tiny_cross = self.cross(1)
        self.tiny_circle = self.circle(1)
        self.tiny_star = self.star(1)
        self.tiny_waves = self.waves(1)
        self.tiny_hexagon = self.hexagon(1)
        self.tiny_quadrifolium = self.quadrifolium(1)
        self.tiny_spiral = self.spiral(1)
        self.tiny_rhombus = self.rhombus(1)
        self.tiny_mandelbrot = self.mandelbrot(1)

    def card_back(self,small=0):
        if small:
            dim = (80,105)
            _image = 'pygame_icon2.png'
            _image_place = (8,20.5)
        else:
            dim = (160,210)
            _image = 'pygame_icon.png'
            _image_place = (16,41)
        background = pygame.Surface(dim).convert()
        background.fill(Color("lemonchiffon"))
        card_back_image = load_image(_image,-1)
        background.blit(card_back_image,_image_place)
        return background

    def square(self,size):
        if size == 1:
            dim = (40,40)
            side = 20
            thickness = 4
        elif size == 2:
            dim = (80,105)
            side = 50
            thickness = 5
        elif size == 3:
            dim = (160,210)
            side = 100
            thickness = 10
        background = pygame.Surface(dim).convert()
        if size == 1:
            kolor = "burlywood"
        else:
            kolor = "white"
        background.fill(Color(kolor))
        if background.mustlock():background.lock()
        pygame.draw.polygon(background, Color("black"), (((dim[0]-side)/2,(dim[1]-side)/2),((dim[0]-side)/2+side,(dim[1]-side)/2),((dim[0]-side)/2+side,(dim[1]-side)/2+side),((dim[0]-side)/2,(dim[1]-side)/2+side)), 0)
        pygame.draw.polygon(background, Color(kolor), (((dim[0]-side)/2+thickness,(dim[1]-side)/2+thickness),((dim[0]-side)/2+side-thickness,(dim[1]-side)/2+thickness),((dim[0]-side)/2+side-thickness,(dim[1]-side)/2+side-thickness),((dim[0]-side)/2+thickness,(dim[1]-side)/2+side-thickness)), 0)
        if background.get_locked():background.unlock()
        return background

    def cross(self,size):
        if size == 1:
            dim = (40,40)
            side = 20
            thickness = 4
        elif size == 2:
            dim = (80,105)
            side = 50
            thickness = 4
        elif size == 3:
            dim = (160,210)
            side = 100
            thickness = 10
        background = pygame.Surface(dim).convert()
        if size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        pygame.draw.line(background, Color("indianred3"), (dim[0]/2,(dim[1]-side)/2),(dim[0]/2,(dim[1]-side)/2+side), thickness)
        pygame.draw.line(background, Color("indianred3"), ((dim[0]-side)/2,dim[1]/2),((dim[0]-side)/2+side,dim[1]/2), thickness)
        if background.get_locked():background.unlock()
        return background

    def circle(self,size):
        if size == 1:
            dim = (40,40)
            radius = 10
            thickness = 14
        elif size == 2:
            dim = (80,105)
            radius = 25
            thickness = 20
        elif size == 3:
            dim = (160,210)
            radius = 50
            thickness = 40
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        for count in range(thickness):
            _color = Color("salmon2")
            r = radius - count * 0.2
            _point_list = []
            for t in range(361):
                t *= pi/180
                x = r * cos(t) + place[0]
                y = r * sin(t) + place[1]
                _point_list.append((x,y))
            pygame.draw.aalines(background, _color,0,_point_list,1)
        if background.get_locked():background.unlock()
        return background

    def star(self,_size):
        if _size == 1:
            dim = (40,40)
            size = 10
        elif _size == 2:
            dim = (80,105)
            size = 20
        elif _size == 3:
            dim = (160,210)
            size = 40
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if _size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        _color = "darkseagreen"
        if size == 1:
            _color2 = "darkseagreen"
        else:
            _color2 = "darkseagreen4"
        for count in range(size/2):
            size -= 1
            l1 = size*sin(18*pi/180)
            l2 = size*cos(36*pi/180)
            h1 = (size+l1)*tan(18*pi/180)
            h2 = size*cos(18*pi/180)
            h3 = size*sin(36*pi/180)
            _place = (place[0] - size - l1, place[1] - h1)
            p1 = (_place[0]+size, _place[1])
            pygame.draw.aaline(background,Color(_color),_place,p1)
            p2 = (_place[0] + size + l1, _place[1] - h2)
            pygame.draw.aaline(background,Color(_color2),p1,p2)
            p3 = (_place[0] + size + 2*l1, _place[1])
            pygame.draw.aaline(background,Color(_color),p2,p3)
            p4 = (_place[0] + 2*size + 2*l1, _place[1])
            pygame.draw.aaline(background,Color(_color2),p3,p4)
            p5 = (_place[0] + 2*size + 2*l1 - l2, _place[1] + h3)
            pygame.draw.aaline(background,Color(_color),p4,p5)
            p6 = (_place[0] + 2*size + 3*l1 - l2, _place[1] + h3 + h2)
            pygame.draw.aaline(background,Color(_color2),p5,p6)
            p7 = (_place[0] + 2*size + 3*l1 - 2*l2, _place[1] + h2)
            pygame.draw.aaline(background,Color(_color),p6,p7)
            p8 = (_place[0] + 2*size + 3*l1 - 3*l2, _place[1] + h3 + h2)
            pygame.draw.aaline(background,Color(_color2),p7,p8)
            p9 = (_place[0] + 2*size + 4*l1 - 3*l2, _place[1] + h3)
            pygame.draw.aaline(background,Color(_color),p8,p9)
            pygame.draw.aaline(background,Color(_color2),p9,_place)
        if background.get_locked():background.unlock()
        return background

    def waves(self,_size):
        if _size == 1:
            dim = (40,40)
            place_x = 0
            place_y = -6
            y_offset = 16
            size = 4
            thickness = 4
        elif _size == 2:
            dim = (80,105)
            place_x = 3
            place_y = -8
            y_offset = 4
            size = 8
            thickness = 10
        elif _size == 3:
            dim = (160,210)
            place_x = -15
            place_y = 15
            y_offset = 0
            size = 20
            thickness = 20
        background = pygame.Surface(dim).convert()
        if _size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        for v in range(3):
            place = (place_x,90 + v*place_y)
            for count in range(thickness):
                point_list = []
                for x in range(90,450):
                    x *= pi/180
                    y = 0.5*cos(x) - y_offset
                    x = x * size + place[0]
                    y = y * size + place[1] + count*0.5
                    point_list.append((x , y))
                pygame.draw.aalines(background, Color("slateblue4"),0,point_list,1)
        if background.get_locked():background.unlock()
        return background

    def hexagon(self,_size):
        if _size == 1:
            dim = (40,40)
            size = 15
        elif _size == 2:
            dim = (80,105)
            size = 30
        elif _size == 3:
            dim = (160,210)
            size = 60
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if _size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        _color = "dimgrey"
        if background.mustlock():background.lock()
        if _size == 1:
            c = 3
        else:
            c = 4
        for count in range(size/c):
            _place = (place[0]-size,place[1])
            size -= 0.8
            h = sqrt(size**2 - (size/2)**2)
            p1 = (_place[0]+size/2,_place[1]-h)
            pygame.draw.aaline(background,Color(_color),_place,p1)
            p2 = (_place[0]+size*3/2,_place[1]-h)
            pygame.draw.aaline(background,Color("black"),p1,p2)
            p3 = (_place[0]+2*size,_place[1])
            pygame.draw.aaline(background,Color(_color),p2,p3)
            p4 = (_place[0]+size*3/2,_place[1]+h)
            pygame.draw.aaline(background,Color("black"),p3,p4)
            p5 = (_place[0]+size/2,_place[1]+h)
            pygame.draw.aaline(background,Color(_color),p4,p5)
            pygame.draw.aaline(background,Color("black"),p5,_place)
        if background.get_locked():background.unlock()
        return background

    def quadrifolium(self,size):
        if size == 1:
            dim = (40,40)
            _size = 15
        elif size == 2:
            dim = (80,105)
            _size = 30
        elif size == 3:
            dim = (160,210)
            _size = 55
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        for count in range(20):
            if size == 1:
                _size_ = _size - count * 0.1
            elif size == 2:
                _size_ = _size - count * 0.25
            elif size == 3:
                _size_ = _size - count * 0.5
            _point_list = []
            for t in range(361):
                t *= pi/180
                x = cos(2*t) * cos(t) * _size_ + place[0]
                y = cos(2*t) * sin(t) * _size_ + place[1]
                _point_list.append((x,y))
            pygame.draw.aalines(background, Color("darkslategray"),0,_point_list,1)
        if background.get_locked():background.unlock()
        return background

    def spiral(self,_size):
        if _size == 1:
            dim = (40,40)
            size = 1100
            a = 0.8
            b = 0.8
        elif _size == 2:
            dim = (80,105)
            size = 1450
            a = 2
            b = 1.2
        elif _size == 3:
            dim = (160,210)
            size = 1800
            a = 4
            b = 2
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if _size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        for count in range(10):
            _place = (place[0] , place[1] + count*0.2)
            point_list = []
            for t in range(size):
                t *= pi/180
                x = a*cos(t) + b*t*cos(t) + _place[0]
                y = a*sin(t) + b*t*sin(t) + _place[1]
                point_list.append((x,y))
            pygame.draw.aalines(background, Color("peru"),0,point_list,1)
        if background.get_locked():background.unlock()
        return background

    def rhombus(self,size):
        if size == 1:
            dim = (40,40)
            _side = 15
        elif size == 2:
            dim = (80,105)
            _side = 33
        elif size == 3:
            dim = (160,210)
            _side = 65
        place = (dim[0]/2,dim[1]/2)
        background = pygame.Surface(dim).convert()
        if size == 1:
            background.fill(Color("burlywood"))
        else:
            background.fill(Color("white"))
        if background.mustlock():background.lock()
        for count in range(_side/2):
            side = _side - count
            l1 = sin(22.5*pi/180) * side
            h1 = cos(22.5*pi/180) * side
            _place = (place[0] - l1, place[1])
            p1 = (_place[0]+l1,_place[1]-h1)
            pygame.draw.aaline(background,Color("deeppink"),_place,p1)
            p2 = (_place[0]+2*l1,_place[1])
            pygame.draw.aaline(background,Color("deeppink"),p1,p2)
            p3 = (_place[0]+l1,_place[1]+h1)
            pygame.draw.aaline(background,Color("deeppink3"),p2,p3)
            pygame.draw.aaline(background,Color("deeppink3"),p3,_place)
        if background.get_locked():background.unlock()
        return background

    def mandelbrot(self,size):
        # derived from Ian Mallet (geometrian)
        if size == 1:
            dim = (40,40)
            width = 40
            height = 30
            place = (0,5)
        elif size == 2:
            dim = (80,105)
            width = 80
            height = 60
            place = (0,22.5)
        elif size == 3:
            dim = (160,210)
            width = 160
            height = 120
            place = (0,45)
        background = pygame.Surface(dim).convert()
        if size == 1:
            _Color = Color("burlywood")
        else:
            _Color = Color("white")
        background.fill(_Color)
        if background.mustlock():background.lock()
        max_iteration = 20
        for ypixel in xrange(height):
            for xpixel in xrange(width):
                x = -2 + (3*(float(xpixel)/float(width)))
                y = -1 + (2*(float(ypixel)/float(height)))
                z = complex(x,y)
                c = z
                for iteration in xrange(max_iteration):
                    z = (z*z)+c
                    if abs(z) > 1.8:
                        break
                    else:
                        if iteration == max_iteration - 1:
                            _Color = Color("navy")
                        else:
                            if size == 1:
                                _Color = Color("burlywood")
                            else:
                                _Color = Color("white")
                coords = (xpixel + place[0], height - ypixel + place[1])
                pygame.draw.aaline(background, _Color, coords, coords)
        if background.get_locked():background.unlock()
        return background

class gameplay:
    def __init__(self,background):
        self.background = background
        self.silence = 0
        self.additional_cards = 0
        self.success = 0
        
        self.a = cards(background)
        self.b = check_box(background," Additional cards",(200,235))
        self.c = check_box(background," Silence",(419,235))
        self.check_box_list = []
        self.check_box_list.append(self.b)
        self.check_box_list.append(self.c)
        self.d = simple_button(545,235,"About",background)

        self.small_list = []
        self.small_list.append(small_card_place(background,self.a.small_square,self.a.small_card_back,(200,10),1,0))
        self.small_list.append(small_card_place(background,self.a.small_cross,self.a.small_card_back,(290,10),1,1))
        self.small_list.append(small_card_place(background,self.a.small_circle,self.a.small_card_back,(380,10),1,2))
        self.small_list.append(small_card_place(background,self.a.small_star,self.a.small_card_back,(470,10),1,3))
        self.small_list.append(small_card_place(background,self.a.small_waves,self.a.small_card_back,(560,10),1,4))
        self.small_list.append(small_card_place(background,self.a.small_hexagon,self.a.small_card_back,(200,125),0,5))
        self.small_list.append(small_card_place(background,self.a.small_quadrifolium,self.a.small_card_back,(290,125),0,6))
        self.small_list.append(small_card_place(background,self.a.small_spiral,self.a.small_card_back,(380,125),0,7))
        self.small_list.append(small_card_place(background,self.a.small_rhombus,self.a.small_card_back,(470,125),0,8))
        self.small_list.append(small_card_place(background,self.a.small_mandelbrot,self.a.small_card_back,(560,125),0,9))

        self.big_first_list = [self.a.big_square,self.a.big_cross,self.a.big_circle,self.a.big_star,self.a.big_waves]
        self.big_all_list = [self.a.big_square,self.a.big_cross,self.a.big_circle,self.a.big_star,self.a.big_waves,\
                            self.a.big_hexagon,self.a.big_quadrifolium,self.a.big_spiral,self.a.big_rhombus,self.a.big_mandelbrot]
        self.big_list = self.big_first_list
        random_card = randint(0,len(self.big_list)-1)
        self.f = big_card_place(background,self.big_list[random_card],self.a.big_card_back,(20,15),0,random_card)
        
        self.good_sound_1 = load_sound('clapping with voice.ogg')
        self.good_sound_2 = load_sound('crowd yeah.ogg')
        self.good_sound_3 = load_sound('kids yeah.ogg')
        self.bad_sound_1 = load_sound('crowd oh no.ogg')
        self.bad_sound_2 = load_sound('dissapointed.ogg')
        self.bad_sound_3 = load_sound('crowd hoo.ogg')
        self.good_sound_list = [self.good_sound_1,self.good_sound_2,self.good_sound_3]
        self.bad_sound_list = [self.bad_sound_1,self.bad_sound_2,self.bad_sound_3]
        
        self.g = message_board(background)
        self.h = [0,0,0,0,0,0,0,0,0,0]
        self.i = 0
        self.j = 0

    def update(self):
        if self.additional_cards == 1 and self.big_list != self.big_all_list:
            self.big_list = self.big_all_list
            random_card = randint(0,len(self.big_list)-1)
            self.f = big_card_place(self.background,self.big_list[random_card],self.a.big_card_back,(20,15),0,random_card)
        elif self.additional_cards == 0 and self.big_list != self.big_first_list:
            self.big_list = self.big_first_list
            random_card = randint(0,len(self.big_list)-1)
            self.f = big_card_place(self.background,self.big_list[random_card],self.a.big_card_back,(20,15),0,random_card)

        for x in self.small_list:
            if x.has_border:
                # show big card
                self.f.face_up = 1
                self.f.is_dirty = 1
                self.f.update()
                pygame.display.update(self.f.rect)
                # compare
                self.i += 1
                if x._index == self.f._index:
                    self.success = 1
                    self.g.is_dirty = 1
                    self.g.update('Bravo !!!')
                    self.h[x._index] += 1
                    self.j += 1
                else:
                    self.success = 0
                    self.g.is_dirty = 1
                    self.g.update('Never mind ...')
                pygame.display.update(self.g.rect)
                # play sound or not
                if self.silence:
                    while pygame.time.delay(1000) < 1000:
                        pass
                    pygame.event.clear()
                else:
                    _channel = pygame.mixer.Channel(0)
                    if self.success:
                        _sound = self.good_sound_list[randint(0,2)]
                    else:
                        _sound = self.bad_sound_list[randint(0,2)]
                    _channel.play(_sound)
                    while _channel.get_busy():
                        pass
                    pygame.event.clear()
                self.g.is_dirty = 1
                self.g.update()
                x.draw_border(0)
                x.update()
                random_card = randint(0,len(self.big_list)-1)
                self.f = big_card_place(self.background,self.big_list[random_card],self.a.big_card_back,(20,15),0,random_card)

class scrolling_text:
    def __init__(self):
        in_file = open(path.join(DATA_FOLDER,'Credits.txt'),'r')
        opened_file = in_file.readlines()
        in_file.close()
        _len = len(opened_file)
        self.surf = pygame.Surface((550,(_len+1)*21)).convert()
        self.surf.fill(Color("burlywood"))
        self.surfrect = self.surf.get_rect()
        self.surfrect.topleft = (0,200)
        count = 0
        for f in opened_file:
            e = ''
            for g in f:
                if g == '\r' or g == '\n':
                    pass
                else:
                    e += g
            image = pygame.font.SysFont(_FONT,21).render(e, 1, Color("black"))
            rect = image.get_rect()
            rect.topleft = (0,count)
            count += 21
            self.surf.blit(image,rect)

#-------------------Game functions-------------------
def play(args):
    if args[1] == -1:
        a = gameplay(args[0])
    elif args[1] == 1:
        a = args[2]
        a.b.is_dirty = 1
        a.b.update()
        a.c.is_dirty = 1
        a.c.update()
        a.d.__init__(545,235,"About",args[0])
        a.d.is_dirty = 1
        a.d.update()
        a.f.is_dirty = 1
        a.f.update()
        a.g.is_dirty = 1
        a.g.update('Click on face ups')
        for x in a.small_list:
            x.is_dirty = 1
            x.update()

    if not pygame.mixer.music.get_busy() and a.silence == 0:
        musicfile = path.join(DATA_FOLDER,'greensleeves.mid')
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

    value = 0
    running = 1
    while running:

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = 0
            elif event.type == MOUSEMOTION:
                for box in a.check_box_list:
                    if box.is_focused(event.pos[0],event.pos[1]) and not box.is_highlighted:
                        box.highlight(1)
                        box.update()
                    elif not box.is_focused(event.pos[0],event.pos[1]) and box.is_highlighted:
                        box.highlight(0)
                        box.update()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if a.b.is_focused(event.pos[0],event.pos[1]):
                    if not a.b.is_checked:
                        a.b.check(1)
                        for c in a.small_list[5:10]:
                            c.face_up = 1
                            c.is_dirty = 1
                            c.update()
                        a.b.update()
                        a.additional_cards = 1
                    elif a.b.is_checked:
                        a.b.check(0)
                        for c in a.small_list[5:10]:
                            c.face_up = 0
                            c.is_dirty = 1
                            c.update()
                        a.b.update()
                        a.additional_cards = 0
                if a.c.is_focused(event.pos[0],event.pos[1]):
                    if not a.c.is_checked:
                        a.c.check(1)
                        if PLATFORM.startswith('win'):
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.pause()
                        a.silence = 1
                        a.c.update()
                    elif a.c.is_checked:
                        a.c.check(0)
                        if PLATFORM.startswith('win'):
                            pygame.mixer.music.play(-1)
                        else:
                            pygame.mixer.music.unpause()
                        a.silence = 0
                        a.c.update()
                if a.d.is_focused(event.pos[0],event.pos[1]):
                    a.d.press()
                    a.d.update()
                for s in a.small_list:
                    if s.is_focused(event.pos[0],event.pos[1]):
                        if s.face_up:
                            if not s.has_border:
                                s.draw_border(1)
                                s.update()
                                pygame.display.update(s.rect)
                                a.update()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if a.d.status:
                    a.d.unpress()
                    a.d.update()
                    value = 1
                    running = 0
        pygame.display.update()

    return [value,a]

def about(args):
    args[0].fill(Color("burlywood"))

    args[0].blit(args[1].a.tiny_square,(2,15))
    args[0].blit(args[1].a.tiny_cross,(2,55))
    args[0].blit(args[1].a.tiny_circle,(2,95))
    args[0].blit(args[1].a.tiny_star,(2,135))
    args[0].blit(args[1].a.tiny_waves,(2,175))
    args[0].blit(args[1].a.tiny_hexagon,(608,15))
    args[0].blit(args[1].a.tiny_quadrifolium,(608,55))
    args[0].blit(args[1].a.tiny_spiral,(608,95))
    args[0].blit(args[1].a.tiny_rhombus,(608,135))
    args[0].blit(args[1].a.tiny_mandelbrot,(608,175))

    basesurf = pygame.Surface((550,200)).convert()
    basesurf.fill(Color("burlywood"))
    baserect = basesurf.get_rect()
    baserect.bottomleft = (50,220)

    a = scrolling_text()
    b = simple_button(408,235,"Faster",args[0])
    c = simple_button(147,235,"Ok",args[0])
    d = simple_button(278,235,"Hold",args[0])

    value = 0
    running = 1
    speed = 20
    stop = 0

    while running:
        CLOCK.tick(speed)
        if not stop:
            if a.surfrect.bottom == 15:
                a.surfrect.top = 200
            else:
                a.surfrect.top -= 1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if b.is_focused(event.pos[0],event.pos[1]):
                    b.press()
                    b.update()
                    speed = 300
                elif c.is_focused(event.pos[0],event.pos[1]):
                    c.press()
                    c.update()
                elif d.is_focused(event.pos[0],event.pos[1]):
                    d.press()
                    d.update()
                    stop = 1
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if b.status:
                    b.unpress()
                    b.update()
                    speed = 20
                elif c.status:
                    c.unpress()
                    c.update()
                    value = 1
                    running = 0
                elif d.status:
                    d.unpress()
                    d.update()
                    stop =0
        basesurf.blit(a.surf,a.surfrect)
        args[0].blit(basesurf,baserect)
        pygame.display.update()

    args[0].fill(Color("burlywood"))
    return [value,args[1]]

def leave(args):
    args[0].fill(Color("burlywood"))

    tiny_list = [args[1].a.tiny_square,args[1].a.tiny_cross,args[1].a.tiny_circle,args[1].a.tiny_star,args[1].a.tiny_waves,\
                args[1].a.tiny_hexagon,args[1].a.tiny_quadrifolium,args[1].a.tiny_spiral,args[1].a.tiny_rhombus,args[1].a.tiny_mandelbrot]
    stats_list = args[1].h

    display_some_text("Guesses",28,(325,30),args[0],1)

    for y in range(2):
        xpos = 50
        ypos = 50*(y+1)
        for x in range(5):
            args[0].blit(tiny_list[x+5*y],(xpos,ypos))
            display_some_text(str(stats_list[x+5*y]),22,(xpos+50,ypos+25),args[0],1)
            xpos += 120

    if args[1].i == 0 or args[1].j == 0:
        score = 0
    else:
        score = round(float(args[1].j)/args[1].i*100,2)

    display_some_text("Total ESP score: " + str(score) + "%",28,(325,200),args[0],1)

    a = simple_button(545,235,"Exit",args[0])

    running = 1

    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if a.is_focused(event.pos[0],event.pos[1]):
                    a.press()
                    a.update()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if a.status:
                    a.unpress()
                    a.update()
                    running = 0
        pygame.display.update()

def main():
    pygame.init()
    background = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Zenercards+ v" + VERSION)
    background.fill(Color("burlywood"))
    args = [background,-1]

    running = 1
    while running:
        a = play(args)
        if a[0] == 0:
            running = 0
        elif a[0] == 1:
            running_2 = 1
            while running_2:
                b = about([background,a[1]])
                if b[0] == 0:
                    running = 0
                    running_2 = 0
                elif b[0] == 1:
                    args = [background,1,b[1]]
                    running_2 = 0
    c = leave([background,a[1]])
    pygame.quit()

if __name__ == '__main__': main()
