from typing import List, Optional, Union
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
import random

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y

class OldBot(BaseLogic):
    
    # Initialize
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.prev_position = (None,None)
        self.diamonds :Optional[list[GameObject]] = None
        self.target_position : Optional[Position] = None
        self.target_object : Optional[GameObject] = None
        self.board = None
        self.ownBot = None
        self.go_back = 1
        self.inventory_space_left = 0
        self.prioritize_horizontal = True

    #Algorithms
    def findNearestDiamond(self, closest_blue_diamond , closest_red_diamond, board_bot, board):
        closest_diamond = None  
        props = board_bot.properties
        base = board_bot.properties.base
        curr_position = board_bot.position
        
                    
                    # mencari optimal jia kedua ada
        if closest_blue_diamond and (not closest_red_diamond or OldBot.calculate_distance(closest_blue_diamond.position, curr_position) < OldBot.calculate_distance(closest_red_diamond.position, curr_position) * 0.75):
            closest_diamond = closest_blue_diamond
        elif closest_red_diamond and props.inventory_size - props.diamonds > 1:
            closest_diamond = closest_red_diamond
                    
                    # update jika tidak ada diamond
        self.target_position = closest_diamond.position if closest_diamond else base
        self.target_object = closest_diamond if closest_diamond else base

                # Lebih baik balik ke base atau tidak
        if props.diamonds >= 4 and OldBot.calculate_distance(self.target_position, base) >= 0.5 * (board.width + board.height):
            self.target_position = base
    

    def get_direction(self,current_x, current_y, dest_x, dest_y, obstacles, width, height):
        horizontal = random.randint(0,1)
        delta_x = clamp(dest_x - current_x, -1, 1)
        delta_y = clamp(dest_y - current_y, -1, 1)
        if horizontal:
            if delta_x != 0:
                delta_y = 0
        else :
            if delta_y != 0:
                delta_x = 0
        return (delta_x, delta_y)


    # getters
    def getTeleporters(self):
        return [d for d in self.board.game_objects if d.type == "TeleportGameObject"]   
    
    def getButtons(self):
        return [d for d in self.board.game_objects if d.type == "DiamondButtonGameObject"]

    def getBase(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject"]
    
    def getEnemies(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject" and d.id  != self.ownBot.id]
    
    def objectInMap(self, listObject : List[GameObject]):
        for obj in listObject:
            if (obj):
                if (obj.position.x == self.target_position.x and obj.position.y == self.target_position.y):
                    return True
        return False
    
    @staticmethod
    def sortDiamonds(allDiamonds : List[GameObject], curr_position : Position):
        closest_blue_diamond = None
        closest_red_diamond = None
        min_blue_distance = float('inf')
        min_red_distance = float('inf')
        for diamond in allDiamonds:
            #blue diamond
            distance = OldBot.calculate_distance(diamond.position,curr_position)
            if diamond.properties.points == 1:
                if (distance < min_blue_distance):
                    min_blue_distance = distance
                    closest_blue_diamond = diamond
            else:
                if (distance < min_red_distance) :
                    min_red_distance = distance
                    closest_red_diamond = diamond
        return  closest_blue_diamond,closest_red_diamond
    
    # using manhattan distance for grid like maps    
    @staticmethod
    def calculate_distance(point_a : Position, point_b : Position):
        #using manhattan distance for grid map
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)
    
    @staticmethod
    def thereIsObstacle(current_x, current_y, objects, delta_x, delta_y):
        for i in objects:
            if ((i.position.x == current_x + delta_x) and (i.position.y == current_y + delta_y)):
                return True
        return False
        

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        curr_position = board_bot.position
        self.board = board
        self.ownBot = board_bot
        base = board_bot.properties.base

        # setting up usefull list
        # most stressing process
        enemies = self.getEnemies()

        allPortals = self.getTeleporters()
        allPortals.sort(key=lambda x : OldBot.calculate_distance(x.position,curr_position))

        allButtons = self.getButtons()
        allButtons.sort(key=lambda x : OldBot.calculate_distance(x.position,curr_position))

        allbase = self.getBase()
        allbase.sort(key=lambda x : OldBot.calculate_distance(x.position, curr_position))

        allDiamonds = OldBot.sortDiamonds(board.diamonds,curr_position)
        closest_blue_diamond = allDiamonds[0]
        closest_red_diamond = allDiamonds[1]
        obstacles = enemies + [allPortals[0]] + [allButtons[0]] 

        # decision making
        if props.diamonds == 5 or (props.diamonds >=4 and OldBot.calculate_distance(curr_position,props.base) >= 0.5*(board.width + board.height)) :
            # Move to base if inventory is full
            self.target_position = base
        else:
            # for now, aim for closest diamond
            if not self.target_position or (self.target_position.x == curr_position.x and self.target_position.y == curr_position.y):
                if not allDiamonds :
                    self.target_position = base
                else:
                    # make decision making
                    self.findNearestDiamond(closest_blue_diamond , closest_red_diamond, board_bot, board)
            elif (self.target_position.x != base.x and self.target_position.y != base.y and self.target_position) :
                if (self.target_object.type == "DiamondGameObject"):
                    if (not self.objectInMap([closest_blue_diamond,closest_red_diamond])):
                        self.target_position = None
                        self.target_object = None
                elif (self.target_object.type == "DiamondButtonGameObject"):
                    if (not self.objectInMap([allButtons[0]])):
                        self.target_object = None
                        self.target_position = None
                elif (self.target_object.type == "TeleportGameObject"):
                    if (not self.objectInMap([allPortals[0]])):
                        self.target_object = None
                        self.target_position = None

        if self.target_position:
            delta_x , delta_y = self.get_direction(
                curr_position.x,
                curr_position.y,
                self.target_position.x,
                self.target_position.y,
                obstacles,
                board.width,
                board.height
            )
            if (curr_position.x == self.prev_position[0] and curr_position.y == self.prev_position[1]):
                if (delta_x != 0):
                    delta_y = delta_x*self.go_back
                    delta_x = 0
                elif (delta_y != 0) :
                    delta_x = delta_x * self.go_back
                    delta_y = 0
                self.go_back *= -1
            self.prev_position  = (curr_position.x,curr_position.y)
            return delta_x,delta_y
        
        return 0,0
        
