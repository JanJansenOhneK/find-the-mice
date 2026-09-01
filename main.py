
VERSION = "dev3"

import random as rand
import math

import pygame as pyg
import perlin_noise as noise

screen = pyg.display.set_mode((700,400),pyg.RESIZABLE|pyg.SCALED)
running = True
pyg.init()
pyg.display.set_caption(f"JanJansen's Cat Simulator | v. {VERSION}")

def asset():
    return f"assets/"

def img(scr:str) -> pyg.Surface:
    return pyg.image.load(f"{asset()}textures/{scr}")

def sound(scr:str) -> pyg.Sound:
    return pyg.Sound(f"{asset()}sounds/{scr}")

def text(text:str,size:int=20,color:tuple[int,int,int]=(255,255,255),font:str="font1") -> pyg.Surface:
    return pyg.font.Font(f"{asset()}{font}.ttf",size).render(text,False,color)

class DialougePerson:
    def __init__(self,name:str,sound:pyg.Sound,icon:pyg.Surface|None=None):
        self.name = name
        self.sound = sound
        self.icon = icon

class Dialouge:
    def __init__(self,text:str,person:DialougePerson):
        self.text = text
        self.person = person

DP_TUTORIAL = DialougePerson(name="Tutorial",sound=pyg.mixer.Sound(sound("uh.wav")))
DP_SIGN = DialougePerson(name="Sign",icon=img("dialouge/sign.png"),sound=pyg.mixer.Sound(sound("uh.wav")))

class Tile:
    def __init__(self,pos:tuple[int,int],id:str):
        self.pos = pos

        self.id = id
        if id == "grass":
            self.texture = "grass1"
        elif id == "stone":
            self.texture = "stone1"
        elif id == "water":
            self.texture = "water1"
        else:
            self.texture = "notexture"
            self.id = "error"

class Entity:
    def __init__(self):
        self.pos = [0,0]
        self.texture:pyg.Surface = img("placeholderentity1.png")
    def frame(self):
        pass
    def interact(self):
        pass
class Sign(Entity):
    def __init__(self,texts:tuple[str,...],pos:tuple[int,int]):
        super().__init__()
        self.pos = pos
        self.texture = img("sign.png")
        self.dialouges = []
        for _text in texts:
            self.dialouges.append(Dialouge(_text,DP_SIGN))
    def frame(self):
        pass
    def interact(self):
        state.dialouge = self.dialouges[0]
        state.dialougequeue = self.dialouges[1:]

class Level:
    def __init__(self):
        self.seed = rand.randint(-999,999)
        self.noise = noise.PerlinNoise(5,self.seed)
        self.tiles:dict[tuple[int,int],Tile] = {}
        self.entities:dict[tuple[int,int],Entity] = {}

    def gen(self,pos:tuple[int,int]):
        _perlin = self.noise((pos[0]/50,pos[1]/50))
        # entities
        if pos == (0,0):
            self.entities[pos] = Sign(("Welcome to Cat Simulator!",f"Seed: {self.seed}"),(0,0))
        # tiles
        if _perlin > 0.2:
            self.tiles[pos] = Tile(pos,"stone")
        elif _perlin < -0.2:
            self.tiles[pos] = Tile(pos,"water")
        else:
            self.tiles[pos] = Tile(pos,"grass")

        
    def genrect(self,rect:tuple[tuple[int,int],tuple[int,int]]):
        for x in range(rect[1][0]):
            for y in range(rect[1][1]):
                self.gen((rect[0][0]+x,rect[0][1]+y))

    def findpostile(self,pos:tuple[int,int]) -> bool:
        return pos in self.tiles.keys()
    def findposentity(self,pos:tuple[int,int]) -> bool:
        return pos in self.entities.keys()

class GameState:
    def __init__(self):
        self.level = Level()
        self.plr_pos:list[int] = [0,0]
        self.plr_tile:list[int] = [0,0]
        self.dialouge:Dialouge|None = None
        self.dialougequeue:list[Dialouge]=[]
state = GameState()

print(f"Seed: {state.level.seed}")
state.level.genrect(((-8,-5),(16,10)))

while running:
    # events
    ## movement
    if state.dialouge == None:
        if pyg.key.get_pressed()[pyg.K_LCTRL]:
            if pyg.key.get_pressed()[pyg.K_d] or pyg.key.get_pressed()[pyg.K_RIGHT]:
                state.plr_pos[0] += 10
            if pyg.key.get_pressed()[pyg.K_a] or pyg.key.get_pressed()[pyg.K_LEFT]:
                state.plr_pos[0] += -10
            if pyg.key.get_pressed()[pyg.K_s] or pyg.key.get_pressed()[pyg.K_DOWN]:
                state.plr_pos[1] += 10
            if pyg.key.get_pressed()[pyg.K_w] or pyg.key.get_pressed()[pyg.K_UP]:
                state.plr_pos[1] += -10
        else:
            if pyg.key.get_pressed()[pyg.K_d] or pyg.key.get_pressed()[pyg.K_RIGHT]:
                state.plr_pos[0] += 5
            if pyg.key.get_pressed()[pyg.K_a] or pyg.key.get_pressed()[pyg.K_LEFT]:
                state.plr_pos[0] += -5
            if pyg.key.get_pressed()[pyg.K_s] or pyg.key.get_pressed()[pyg.K_DOWN]:
                state.plr_pos[1] += 5
            if pyg.key.get_pressed()[pyg.K_w] or pyg.key.get_pressed()[pyg.K_UP]:
                state.plr_pos[1] += -5
    
    for event in pyg.event.get():
        #print(event)
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE:
                if state.dialouge != None:
                    if state.dialougequeue == []:
                        state.dialouge = None
                    else:
                        state.dialouge = state.dialougequeue[0]
                        state.dialougequeue.pop(0)
            elif event.key == pyg.K_e:
                if state.level.findposentity((state.plr_tile[0],state.plr_tile[1])):
                    state.level.entities[(state.plr_tile[0],state.plr_tile[1])].interact()
        elif event.type == pyg.QUIT:
            running = False

    # other
    ## plr tile
    state.plr_tile[0] = math.floor(state.plr_pos[0]/50)
    state.plr_tile[1] = math.floor(state.plr_pos[1]/50)

    # render
    ## black bg
    screen.fill((0,0,0))
    ## tiles
    for x in range(state.plr_tile[0]-8, state.plr_tile[0]+8):
        for y in range(state.plr_tile[1]-5, state.plr_tile[1]+5):
            if state.level.findpostile((x,y)):
                _tile = state.level.tiles[(x,y)]
                screen.blit(img(f"tiles/{_tile.texture}.png"),(_tile.pos[0]*50 + -1*state.plr_pos[0] + 350, _tile.pos[1]*50 + -1*state.plr_pos[1] + 200))
            else:
                state.level.gen((x,y))
    ## entities
    for _entity in state.level.entities.values():
        screen.blit(_entity.texture,(_entity.pos[0]*50 + -1*state.plr_pos[0] + 350, _entity.pos[1]*50 + -1*state.plr_pos[1] + 200))

    ## crosshair
    screen.blit(img("overlay1.png"),(0,0))
    ## dialouge
    if state.dialouge == None:
        pass
    else:
        pyg.draw.rect(screen,(0,0,0),pyg.Rect(0,300,700,100))
        if state.dialouge.person.icon == None:
            screen.blit(text(state.dialouge.person.name),(10,310))
            screen.blit(text(state.dialouge.text,size=30),(10,330))
        else:
            screen.blit(state.dialouge.person.icon,(0,300))
            screen.blit(text(state.dialouge.person.name),(110,310))
            screen.blit(text(state.dialouge.text,size=30),(110,330))


    pyg.display.flip()

pyg.quit()

