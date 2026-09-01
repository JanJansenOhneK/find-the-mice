
VERSION = "dev1"

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

class Tile:
    def __init__(self,pos:tuple[int,int],id:str):
        self.pos = pos

        self.id = id
        if id == "grass":
            self.texture = "grass1"
        elif id == "stone":
            self.texture = "stone1"
        else:
            self.texture = "notexture"
            self.id = "error"

class Level:
    def __init__(self):
        self.seed = rand.randint(-999,999)
        self.noise = noise.PerlinNoise(5,self.seed)
        self.tiles:dict[tuple[int,int],Tile] = {}

    def gen(self,pos:tuple[int,int]):
        print(self.noise((pos[0]/50,pos[1]/50)))
        if self.noise((pos[0]/50,pos[1]/50)) > 0.2:
            self.tiles[pos] = (Tile(pos,"stone"))
        else:
            self.tiles[pos] = (Tile(pos,"grass"))
        
        

    def genrect(self,rect:tuple[tuple[int,int],tuple[int,int]]):
        for x in range(rect[1][0]):
            for y in range(rect[1][1]):
                self.gen((rect[0][0]+x,rect[0][1]+y))

    def findpostile(self,pos:tuple[int,int]) -> bool:
        return pos in self.tiles.keys()


class GameState:
    def __init__(self):
        self.level = Level()
        self.plr_pos = [0,0]
        self.plr_tile = [0,0]
state = GameState()

print(f"Seed: {state.level.seed}")

state.level.genrect(((-8,-5),(16,10)))

while running:
    # events
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
        if event.type == pyg.QUIT:
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
    
    ## crosshair
    screen.blit(img("overlay1.png"),(0,0))

    pyg.display.flip()

pyg.quit()

