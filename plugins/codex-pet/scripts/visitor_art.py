"""Small native visitor sprites; wing poses share a fixed body anchor."""


def butterfly_pixels(frame):
    from pixel_art import Pixels
    p = Pixels(32,28)
    spread = (1.0,.88,.62,.30,.16,.30,.62,.88)[frame % 8]
    ink = '#594333'
    def wing(points, color, side):
        p.polygon([(16 + round(x * spread) * side,y) for x,y in points],color)
    for side in (-1,1):
        # Smaller rounded hindwings sit behind the swept forewings.
        wing([(0,13),(6,12),(10,16),(9,21),(6,24),(2,22)],ink,side)
        wing([(1,14),(6,14),(8,17),(7,21),(5,22),(2,20)],'#cf8a54',side)
        wing([(2,15),(5,15),(7,18),(5,20),(3,19)],'#efbd79',side)
        wing([(0,12),(3,7),(9,3),(13,4),(14,8),(12,13),(7,17),(1,16)],ink,side)
        wing([(1,12),(4,8),(9,5),(11,5),(12,8),(10,12),(6,15),(2,15)],'#d99557',side)
        wing([(3,11),(7,7),(10,6),(10,9),(7,11)],'#f5d28e',side)
        wing([(2,13),(7,11),(10,9),(8,13),(5,15)],'#edb76d',side)
        if spread > .5:
            for x,y in ((11,6),(12,9),(10,12),(7,15),(7,20)):
                p.rect(16+round(x*spread)*side,y,1,1,'#fff0c4')
            p.line(16+side*2,14,16+round(9*spread)*side,8,'#a46b43')
    p.line(16,10,16,19,ink)
    p.rect(16,12,1,4,'#bc9c6a')
    p.rect(15,9,3,2,ink)
    p.line(15,9,13,6,ink);p.line(17,9,19,6,ink)
    return p


def sparrow_pixels(frame):
    from pixel_art import Pixels
    p=Pixels(36,30)
    dip=2 if frame%8 in (5,6) else 0
    p.polygon([(10,18),(1,12),(3,20),(14,24)],'#70563e')
    p.line(3,15,11,21,'#b19468')
    p.oval(8,12,22,14,'#755a42')
    p.oval(12,14,17,11,'#d8c39a')
    p.oval(9,13,14,10,'#a18257')
    for x,y in ((11,15),(14,16),(17,17)):
        p.line(x,y,x+3,y+4,'#6c533c');p.rect(x,y,2,1,'#c3aa7c')
    p.oval(21,6+dip,12,13,'#79573d')
    p.oval(22,11+dip,10,7,'#e7d4b0')
    p.rect(27,12+dip,2,2,'#66503b')
    p.rect(29,10+dip,2,2,'#352f29');p.rect(29,10+dip,1,1,'#fff0cd')
    p.polygon([(32,11+dip),(35,13+dip),(32,14+dip)],'#92723f')
    p.line(19,25,18,28,'#876740');p.line(25,25,26,28,'#876740')
    p.line(16,28,20,28,'#876740');p.line(24,28,28,28,'#876740')
    return p
