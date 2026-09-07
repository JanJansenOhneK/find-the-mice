
VERSION = "dev11"

import random as rand
import math
import json

import pygame as pyg
import perlin_noise as noise

screen = pyg.display.set_mode((700,400),pyg.RESIZABLE|pyg.SCALED)
running = True
clock = pyg.Clock()
pyg.init()
pyg.display.set_caption(f"Find the mice | v. {VERSION}")

levelfile = open("save/level1.json","r+")
settingsfile = open("save/settings.json","r+")

def asset():
    return f"assets/"

textfile = open(f"{asset()}text.json","r")
textdict = json.load(textfile)

def lang(id:str,language:str|None=None) -> str:
    if language == None:
        if id in textdict[state.language].keys():
            return textdict[state.language][id]
        else:
            return textdict["en"][id]
    else:
        if id in textdict[state.language].keys():
            return textdict[language][id]
        else:
            return textdict["en"][id]

def img(scr:str) -> pyg.Surface:
    return pyg.image.load(f"{asset()}textures/{scr}")

pyg.display.set_icon(img("favicon1.png"))

def sound(scr:str) -> pyg.Sound:
    return pyg.Sound(f"{asset()}sounds/{scr}")

def text(text:str,size:int=20,color:tuple[int,int,int]=(255,255,255),font:str="font1",antialias:bool=False) -> pyg.Surface:
    return pyg.font.Font(f"{asset()}{font}.ttf",size).render(text,antialias,color)

class DialougePerson:
    def __init__(self,name:str,icon:str|None=None,sound:str="uh.wav"):
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
class Mouse(Entity):
    def __init__(self,id:str,pos:tuple[int,int],textures:tuple[str,...],fpf:int=5,dpicon:str|None=None):
        super().__init__()
        self.id = id
        self.name = ""
        self.pos = pos
        self.textures = textures
        self.textureframe = 0
        self.fpf = fpf
        self.texture = self.textures[0]
        self.dp = DialougePerson("")
        self.dpicon = dpicon
        self.interactable = True
        self.found = False
    def frame(self):
        self.name = lang(f"mouse.{self.id}.name")
        self.dp = DialougePerson(self.name,self.dpicon)

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
        state.dialouge = Dialouge(lang(f"mouse.{self.id}.0"),self.dp)
        i = 1
        while f"mouse.{self.id}.{i}" in textdict[state.language].keys():
            state.dialougequeue.append(Dialouge(lang(f"mouse.{self.id}.{i}"),self.dp))
            i += 1


mousedict:dict[str,Mouse] = {
    "linux":Mouse(
        "linux",
        (0,0),
        ("mice/linux1.png","mice/linux2.png")
    ),
    "tutorial":Mouse(
        "tutorial",
        (0,0),
        ("mice/tutorial1.png","mice/tutorial2.png")
    ),
    "book":Mouse(
        "book",
        (0,0),
        ("mice/book1.png","mice/book2.png")
    ),
}


class Level:
    def __init__(self):
        self.seed = rand.randint(-999,999)
        self.noise = noise.PerlinNoise(5,self.seed)
        self.tiles:dict[tuple[int,int],Tile] = {}

        self.mice:dict[tuple[int,int],str] = {}
        self.entities:dict[tuple[int,int],Mouse] = {}
        self.genmice:list[str] = []

    def append_mouse(self,id:str,pos:tuple[int,int]):
        self.genmice.append(id)
        self.entities[pos] = mousedict[id]
        self.entities[pos].pos = pos

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
        _rand = rand.randint(0,100)
        if pos == (0,0):
            self.append_mouse("tutorial",pos)
        elif not "linux" in self.genmice:
            if _type == "grass":
                if _rand == 1:
                    self.append_mouse("linux",pos)
        elif not "book" in self.genmice:
            if not _type in ("water","snow"):
                if _rand == 2:
                    self.append_mouse("book",pos)
            
            
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
        levelfile.truncate(0)
        levelfile.seek(0)
        leveldict = {
            "plrpos":[state.plr_pos[0],state.plr_pos[1]],
            "seed":self.seed,
            "entities":[]
        }
        """
        for tile in self.tiles.values():
            leveldict["tiles"].append({
                "pos":list(tile.pos),
                "id":tile.id
            })
        """
        for entity in self.entities.values():
            _dict = {
                "pos":list(entity.pos),
                "found":entity.found,
                "id":entity.id
            }
            leveldict["entities"].append(_dict)
        json.dump(leveldict,levelfile)
        print("level saved")


def loadlevel():
    levelfile.seek(0)
    _dict = json.load(levelfile)
    _level = Level()
    _level.seed = _dict["seed"]
    for _mouse in _dict["entities"]:
        _mouseobj = mousedict[_mouse["id"]]
        _mouseobj.found = _mouse["found"]
        _level.entities[tuple(_mouse["pos"])] = _mouseobj
    state.plr_pos = [_dict["plrpos"][0],_dict["plrpos"][1]]
    _level.noise = noise.PerlinNoise(5,_level.seed)
    state.level = _level

def loadnewlevel():
    state.plr_pos = [25,25]
    state.level = Level()

def loadsettings():
    settingsfile.seek(0)
    _dict = json.load(settingsfile)
    state.language = _dict["language"]

def savesettings():
    settingsfile.seek(0)
    settingsfile.truncate(0)
    _dict = {"language":state.language}
    json.dump(_dict,settingsfile)

class GUIElement:
    def __init__(self,pos:tuple[int,int]):
        self.pos = pos
    def frame(self):
        pass

class GUIButton(GUIElement):
    def __init__(self,pos:tuple[int, int],size:tuple[int,int]):
        self.pos = pos
        self.size = size
        self.hovered = False
    def frame(self):
        _pos = pyg.mouse.get_pos()
        if _pos[0] >= self.pos[0]:
            if _pos[0] <= self.pos[0] + self.size[0]:
                if _pos[1] >= self.pos[1]:
                    if _pos[1] <= self.pos[1] + self.size[1]:
                        self.hovered = True
                        return

        self.hovered = False

class GUITextButton(GUIButton):
    def __init__(self, pos:tuple[int, int], textstr:str):
        self.pos = pos
        self.text = textstr
        self.size = text(f" {self.text} ").get_size()
        self.hovered = False
    def frame(self):
        self.size = text(f" {self.text} ").get_size()
        super().frame()

class GUI:
    def __init__(self,elements:dict[str,GUIElement],caption:str=""):
        self.caption = caption
        self.elements = elements

class GameState:
    def __init__(self):
        self.level = Level()
        self.plr_pos:list[int] = [25,25]
        self.plr_tile:list[int] = [0,0]
        self.dialouge:Dialouge|None = None
        self.dialougequeue:list[Dialouge]=[]

        self.menus:dict[str,GUI] = {
            "mainmenu":GUI({
                "newgame":GUITextButton((100,100),""),
                "continue":GUITextButton((100,130),""),
                "settings":GUITextButton((100,160),""),
                "quit":GUITextButton((100,190),""),
            }),
            "settings":GUI({
                "backmainmenu":GUITextButton((25,50),""),
                "settings_languageselect":GUITextButton((25,80),""),
            }),
            "settings_languageselect":GUI({
                "settings":GUITextButton((25,50),""),
            }),
        }
        self.menuopen = True
        self.menuid = "mainmenu"
        self.buttonclicked = False
        self.buttonid = ""

        self.languagelist = ["en","de"]
        self.language = "en"


state = GameState()

def set_menu(id:str):
    if state.menuopen:
        print("didnt set from ingame")
    else:
        state.level.savefile()
    state.menuid = id
    state.buttonid = ""
    state.buttonclicked = False
    state.menuopen = True

def close_menu():
    state.menuopen = False

loadsettings()
loadnewlevel()

print(f"Seed: {state.level.seed}")
state.level.genrect(((-8,-5),(16,10)))

while running:
    # events
    ## movement
    if state.dialouge == None:
        if not state.menuopen:
            if pyg.key.get_pressed()[pyg.K_LCTRL]:
                if pyg.key.get_pressed()[pyg.K_d] or pyg.key.get_pressed()[pyg.K_RIGHT]:
                    state.plr_pos[0] += 30
                if pyg.key.get_pressed()[pyg.K_a] or pyg.key.get_pressed()[pyg.K_LEFT]:
                    state.plr_pos[0] += -30
                if pyg.key.get_pressed()[pyg.K_s] or pyg.key.get_pressed()[pyg.K_DOWN]:
                    state.plr_pos[1] += 30
                if pyg.key.get_pressed()[pyg.K_w] or pyg.key.get_pressed()[pyg.K_UP]:
                    state.plr_pos[1] += -30
            else:
                if pyg.key.get_pressed()[pyg.K_d] or pyg.key.get_pressed()[pyg.K_RIGHT]:
                    state.plr_pos[0] += 10
                if pyg.key.get_pressed()[pyg.K_a] or pyg.key.get_pressed()[pyg.K_LEFT]:
                    state.plr_pos[0] += -10
                if pyg.key.get_pressed()[pyg.K_s] or pyg.key.get_pressed()[pyg.K_DOWN]:
                    state.plr_pos[1] += 10
                if pyg.key.get_pressed()[pyg.K_w] or pyg.key.get_pressed()[pyg.K_UP]:
                    state.plr_pos[1] += -10

    _leftclick = False
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
            elif event.key == pyg.K_ESCAPE:
                if state.dialouge == None:
                    set_menu("mainmenu")

        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == pyg.BUTTON_LEFT:
                _leftclick = True

        elif event.type == pyg.QUIT:
            running = False

    if state.menuopen:
        if _leftclick:
            state.buttonclicked = True
        else:
            state.buttonclicked = False
    else:
        state.buttonclicked = False

    # other
    ## plr tile
    state.plr_tile[0] = math.floor(state.plr_pos[0]/50)
    state.plr_tile[1] = math.floor(state.plr_pos[1]/50)
    ## buttons
    if state.buttonclicked:
        print(f"Button clicked ID: {state.buttonid}")
        if state.buttonid == "quit":
            running = False
        elif state.buttonid == "continue":
            levelfile.seek(0)
            if levelfile.read() == "":
                print("level file empty")
            else:
                loadlevel()
                close_menu()
        elif state.buttonid == "newgame":
            loadnewlevel()
            close_menu()
        elif state.buttonid == "settings":
            set_menu("settings")
        elif state.buttonid == "backmainmenu":
            set_menu("mainmenu")
        elif state.buttonid == "settings_languageselect":
            set_menu("settings_languageselect")
        elif state.buttonid == "resetsavefile":
            levelfile.seek(0)
            levelfile.truncate(0)
        elif "language_" in state.buttonid:
            state.language = state.buttonid[9:]
    ## gui refresh
    if state.menuopen:
        state.menus = {
            "mainmenu":GUI({
                "newgame":GUITextButton((100,100),lang("newgame")),
                "continue":GUITextButton((100,130),lang("continue")),
                "settings":GUITextButton((100,170),lang("settings")),
                "quit":GUITextButton((100,200),lang("quit")),
            }),
            "settings":GUI({
                "backmainmenu":GUITextButton((25,50),lang("back")),
                "settings_languageselect":GUITextButton((25,80),lang("select_language")),
                "resetsavefile":GUITextButton((25,110),lang("reset_savefile")),
            }),
            "settings_languageselect":GUI({
                "settings":GUITextButton((25,50),lang("back")),
            }),
        }
        for i,_language in enumerate(state.languagelist):
            state.menus["settings_languageselect"].elements[f"language_{_language}"] = GUITextButton((25,i*30+100),f"{lang(f'language.{_language}')} ({lang(f'language.{_language}',_language)})")
            

    # render
    ## black bg
    screen.fill((0,0,0))
    if state.menuopen:
        ## elements
        _id = ""
        for i,element in enumerate(state.menus[state.menuid].elements.values()):
            element.frame()
            _surface = pyg.Surface((69,69))
            if type(element) == GUIButton:
                _surface = pyg.Surface(element.size)
                if element.hovered:
                    _id = list(state.menus[state.menuid].elements.keys())[i]
                    _surface.fill((130,130,130))
                else:
                    _surface.fill((100,100,100))
            elif type(element) == GUITextButton:
                _surface = pyg.Surface(element.size)
                if element.hovered:
                    _id = list(state.menus[state.menuid].elements.keys())[i]
                    _surface.fill((130,130,130))
                else:
                    _surface.fill((100,100,100))
                _surface.blit(text(f" {element.text} "))

            screen.blit(_surface,element.pos)
        state.buttonid = _id
    else:
        ## tiles
        _usedtiles = list(state.level.tiles.keys())
        for x in range(state.plr_tile[0]-8, state.plr_tile[0]+9):
            for y in range(state.plr_tile[1]-5, state.plr_tile[1]+6):
                if state.level.findpostile((x,y)):

                    _usedtiles.remove((x,y))
                    
                    _tile = state.level.tiles[(x,y)]
                    _pos = (_tile.pos[0]*50 + -1*state.plr_pos[0] + 350, _tile.pos[1]*50 + -1*state.plr_pos[1] + 200)
                    screen.blit(img(f"tiles/{_tile.texture}.png"),_pos)

                    _overlay = pyg.Surface((50,50))
                    _overlay.fill((0,0,0))
                    _overlay.set_alpha(round(((abs(_tile.perlin) - abs(state.level.tiles[(state.plr_tile[0],state.plr_tile[1])].perlin))*-100)))
                    screen.blit(_overlay,_pos)
                else:
                    state.level.gen((x,y))

        for _tile in _usedtiles:
            state.level.tiles.pop(_tile)
        
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
    ## fps
    #screen.blit(text(f"FPS: {round(clock.get_fps())}",15,color=(0,0,0),antialias=False),(11,11))
    screen.blit(text(f"FPS: {round(clock.get_fps())}",15,antialias=True),(10,10))
    
    pyg.display.flip()
    clock.tick(60)

    #print(state.buttonid,state.buttonclicked)

state.level.savefile()
savesettings()
levelfile.close()
textfile.close()
pyg.quit()
