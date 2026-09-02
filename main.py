
VERSION = "dev6"

import random as rand
import math
import json

import pygame as pyg
import perlin_noise as noise

screen = pyg.display.set_mode((700,400),pyg.RESIZABLE|pyg.SCALED)
running = True
pyg.init()
pyg.display.set_caption(f"Find the mice | v. {VERSION}")

levelfile = open("save/level1.json","w+")

def asset():
    return f"assets/"

def img(scr:str) -> pyg.Surface:
    return pyg.image.load(f"{asset()}textures/{scr}")

def sound(scr:str) -> pyg.Sound:
    return pyg.Sound(f"{asset()}sounds/{scr}")

def text(text:str,size:int=20,color:tuple[int,int,int]=(255,255,255),font:str="font1") -> pyg.Surface:
    return pyg.font.Font(f"{asset()}{font}.ttf",size).render(text,False,color)

class DialougePerson:
    def __init__(self,name:str,sound:str="uh.wav",icon:str|None=None):
        self.name = name
        self.sound = sound
        self.icon = icon

class Dialouge:
    def __init__(self,text:str,person:DialougePerson):
        self.text = text
        self.person = person

DP_SIGN = DialougePerson(name="Sign",icon="dialouge/sign.png",sound="uh.wav")

class Tile:
    def __init__(self,pos:tuple[int,int],id:str,perlin:float):
        self.pos = pos
        self.id = id
        self.perlin:float = perlin
        if id == "grass":
            self.texture = "grass2"
        elif id == "stone":
            self.texture = "stone1"
        elif id == "water":
            self.texture = "water1"
        elif id == "sand":
            self.texture = "sand5"
        elif id == "snow":
            self.texture = "snow1"
        else:
            self.texture = "notexture"
            self.id = "error"

class Entity:
    def __init__(self):
        self.pos = [0,0]
        self.texture:str = "placeholderentity1.png"
        self.interactable = False
    def frame(self):
        pass
    def interact(self):
        pass
class Sign(Entity):
    def __init__(self,texts:tuple[str,...],pos:tuple[int,int]):
        super().__init__()
        self.pos = pos
        self.texture = "sign.png"
        self.dialouges = []
        self.interactable = True
        for _text in texts:
            self.dialouges.append(Dialouge(_text,DP_SIGN))
    def frame(self):
        pass
    def interact(self):
        state.dialouge = self.dialouges[0]
        state.dialougequeue = self.dialouges[1:]
class Mouse(Entity):
    def __init__(self,texts:tuple[str,...],dp:DialougePerson,pos:tuple[int,int],textures:tuple[str,...],fpf:int=5):
        super().__init__()
        self.pos = pos
        self.textures = textures
        self.textureframe = 0
        self.fpf = fpf
        self.texture = self.textures[0]
        self.dialouges = []
        self.dp = dp
        self.interactable = True
        self.found = False
        for _text in texts:
            self.dialouges.append(Dialouge(_text,self.dp))
    def frame(self):
        if self.textureframe % self.fpf == 0:
            self.texture = self.textures[self.textureframe // self.fpf]
        self.textureframe += 1
        self.textureframe = self.textureframe % (len(self.textures)*self.fpf)
    def interact(self):
        if self.found:
            print(f"{self.dp.name} already found")
        else:
            print(f"{self.dp.name} found")
            
        self.found = True
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
        _type = "error"

        # tiles
        if _perlin > 0.4:
            _type = "snow"
        elif _perlin > 0.2:
            _type = "stone"
        elif _perlin < -0.2:
            _type = "water"
        elif _perlin < -0.1:
            _type = "sand"
        else:
            _type = "grass"
        self.tiles[pos] = Tile(pos,_type,_perlin)

        # entities
        if pos == (0,0):
            self.entities[pos] = Sign((
"(Press [E] to advance dialouge)",
"Welcome to Find the Mice!",
"This game is about finding mice.",
"Move your camera with [W] [A] [S] [D].",
"Be faster by pressing [Left CTRL] while moving.",
"If you found one...",
"...move your crosshair over it and press [E].",
"Your goal is to find all mice",
"Have fun!",
f"Seed: {self.seed}")
            ,(0,0))
        elif pos == (1,0):
            self.entities[pos] = Mouse((
"Test dialouge",
"Also Test dialouge",
"Maus"),DialougePerson("Test Mouse"),(1,0),(
"mice/normal.png",
"mice/normal2.png",
"mice/normal3.png",
))
            
    def genrect(self,rect:tuple[tuple[int,int],tuple[int,int]]):
        for x in range(rect[1][0]):
            for y in range(rect[1][1]):
                self.gen((rect[0][0]+x,rect[0][1]+y))

    def findpostile(self,pos:tuple[int,int]) -> bool:
        return pos in self.tiles.keys()
    def findposentity(self,pos:tuple[int,int]) -> bool:
        return pos in self.entities.keys()

    def savefile(self) -> None:
        print("saving level")
        global levelfile
        levelfile.seek(0)
        leveldict = {
            "plrpos":[state.plr_pos[0],state.plr_pos[1]],
            "seed":self.seed,
            "tiles":[],
            "entities":{"signs":[],"mice":[]}
        }
        """
        for tile in self.tiles.values():
            leveldict["tiles"].append({
                "pos":list(tile.pos),
                "id":tile.id
            })
        """
        for entity in self.entities.values():
            if type(entity) == Sign:
                _dict = {
                    "pos":list(entity.pos),
                    "texts":[],
                    "texture":entity.texture
                }
                for dialouge in entity.dialouges:
                    _dict["texts"].append(dialouge.text)
                leveldict["entities"]["signs"].append(_dict)

            elif type(entity) == Mouse:
                _dict = {
                    "pos":list(entity.pos),
                    "texts":[],
                    "textures":list(entity.textures),
                    "fpf":entity.fpf,
                    "found":entity.found,
                    "dp":{"name":entity.dp.name,"icon":entity.dp.icon,"sound":entity.dp.sound}
                }
                for dialouge in entity.dialouges:
                    _dict["texts"].append(dialouge.text)
                leveldict["entities"]["mice"].append(_dict)
        json.dump(leveldict,levelfile)

"""
def loadlevel() -> Level:
    dict = json.load(levelfile)
    level = Level()
"""

class GameState:
    def __init__(self):
        self.level = Level()
        self.plr_pos:list[int] = [25,25]
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
                state.plr_pos[0] += 20
            if pyg.key.get_pressed()[pyg.K_a] or pyg.key.get_pressed()[pyg.K_LEFT]:
                state.plr_pos[0] += -20
            if pyg.key.get_pressed()[pyg.K_s] or pyg.key.get_pressed()[pyg.K_DOWN]:
                state.plr_pos[1] += 20
            if pyg.key.get_pressed()[pyg.K_w] or pyg.key.get_pressed()[pyg.K_UP]:
                state.plr_pos[1] += -20
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
            if event.key == pyg.K_e:
                if state.dialouge == None:
                    if state.level.findposentity((state.plr_tile[0],state.plr_tile[1])):
                        state.level.entities[(state.plr_tile[0],state.plr_tile[1])].interact()
                else:
                    if state.dialougequeue == []:
                        state.dialouge = None
                    else:
                        state.dialouge = state.dialougequeue[0]
                        state.dialougequeue.pop(0)
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
    for x in range(state.plr_tile[0]-8, state.plr_tile[0]+9):
        for y in range(state.plr_tile[1]-5, state.plr_tile[1]+6):
            if state.level.findpostile((x,y)):

                _tile = state.level.tiles[(x,y)]
                _pos = (_tile.pos[0]*50 + -1*state.plr_pos[0] + 350, _tile.pos[1]*50 + -1*state.plr_pos[1] + 200)
                screen.blit(img(f"tiles/{_tile.texture}.png"),_pos)

                _overlay = pyg.Surface((50,50))
                _overlay.fill((0,0,0))
                _overlay.set_alpha(round(((abs(_tile.perlin) - abs(state.level.tiles[(state.plr_tile[0],state.plr_tile[1])].perlin))*-100)))
                screen.blit(_overlay,_pos)

            else:
                state.level.gen((x,y))
    ## entities
    for _entity in state.level.entities.values():

        _entity.frame()
        _pos = (_entity.pos[0]*50 + -1*state.plr_pos[0] + 350, _entity.pos[1]*50 + -1*state.plr_pos[1] + 200)
        screen.blit(img(_entity.texture),_pos)

        if [_entity.pos[0]*1,_entity.pos[1]*1] == state.plr_tile:
            if state.dialouge == None:

                _pos = (_entity.pos[0]*50 + -1*state.plr_pos[0] + 350 -50, _entity.pos[1]*50 + -1*state.plr_pos[1] + 200 -50)
                screen.blit(img("ehint.png"),_pos)
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
            screen.blit(img(state.dialouge.person.icon),(0,300))
            screen.blit(text(state.dialouge.person.name),(110,310))
            screen.blit(text(state.dialouge.text,size=30),(110,330))


    pyg.display.flip()

state.level.savefile()
levelfile.close()
pyg.quit()
