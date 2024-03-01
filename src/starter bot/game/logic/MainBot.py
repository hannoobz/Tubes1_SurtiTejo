from typing import List, Optional, Union
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
import random



def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y

class MainBot(BaseLogic):
    
    # Initialize
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.prev_position = (None,None)

        self.target_position : Optional[Position] = None
        self.target_object : Optional[GameObject] = None
        self.board = None
        self.ownBot = None
        self.go_back = 1
        self.inventory_space_left = 0
        self.prioritize_horizontal = True

        self.AllEnemies : Optional[List[GameObject]] = None
        self.AllPortal : Optional[List[GameObject]] = None
        self.AllButtons : Optional[List[GameObject]] = None
        self.AllBase :  Optional[List[GameObject]] = None
        self.AllDiamonds :Optional[list[GameObject]] = None
        self.TimeLeft = None



    #Algorithms
    def findNearestDiamond(self, closest_blue_diamond , closest_red_diamond, board_bot, board):
        closest_diamond = None  
        props = board_bot.properties
        base = board_bot.properties.base
        curr_position = board_bot.position
        
                    
                    # mencari optimal jia kedua ada
        if closest_blue_diamond and (not closest_red_diamond or MainBot.calculate_distance(closest_blue_diamond.position, curr_position) < MainBot.calculate_distance(closest_red_diamond.position, curr_position) * 0.75):
            closest_diamond = closest_blue_diamond
        elif closest_red_diamond and props.inventory_size - props.diamonds > 1:
            closest_diamond = closest_red_diamond
                    
                    # update jika tidak ada diamond
        self.target_position = closest_diamond.position if closest_diamond else base
        self.target_object = closest_diamond if closest_diamond else base

                # Lebih baik balik ke base atau tidak
        if props.diamonds >= 4 and MainBot.calculate_distance(self.target_position, base) >= 0.5 * (board.width + board.height):
            self.target_position = base
            self.target_object = None

    def make_decision(self):
                # for now, aim for closest diamond
        curr_position = self.ownBot.position
        props = self.ownBot.properties
        base = props.base
        self.initializeState()
        closest_enemy = None
        closest_enemy_distance = None

        # if (self.AllEnemies is not None) and (self.AllEnemies  != []):
        #     closest_enemy = min(self.AllEnemies,key = lambda x : self.calculate_distance(x.position,curr_position), default="EMPTY")
        #     closest_enemy_distance = self.calculate_distance(closest_enemy.position,curr_position)

        # if (closest_enemy is not None and (closest_enemy_distance  <= 1 and closest_enemy.properties.diamonds >= 3)):
        #     self.target_position = closest_enemy.position
        #     self.target_object = closest_enemy

        # else :
        if props.diamonds == 5 or (props.diamonds >=4 and MainBot.calculate_distance(curr_position,props.base) >= 0.5*(self.board.width + self.board.height)) or (props.diamonds >= 3 and self.TimeLeft <= 15000) or (props.diamonds >= 2 and self.TimeLeft <= 10000) :
            # Move to base if inventory is full
            self.target_position = base
        else:
            allDiamonds = self.sortDiamonds(self.AllDiamonds,curr_position)
            if not allDiamonds :
                self.target_position = self.ownBot.properties.base
            else:
                closest_blue_diamond = allDiamonds[0]
                closest_red_diamond = allDiamonds[1]
                self.findNearestDiamond(closest_blue_diamond,closest_red_diamond,self.ownBot,self.board)

    
    # getters
    def get_direction(self,current_x, current_y, dest_x, dest_y,  width, height):
        horizontal = random.randint(0,1)
        delta_x = clamp(dest_x - current_x, -1, 1)
        delta_y = clamp(dest_y - current_y, -1, 1)
        if horizontal:
            if delta_x != 0:
                delta_y = 0
        else :
            if delta_y != 0:
                delta_x = 0
        if (delta_x == 0 and delta_y == 0):
            random_integer = random.randint(0, 3)
            return self.directions[random_integer]
        return (delta_x, delta_y)
    
    def getTeleporters(self):
        return [d for d in self.board.game_objects if d.type == "TeleportGameObject"]   
    
    def getButtons(self):
        return [d for d in self.board.game_objects if d.type == "DiamondButtonGameObject"]

    def getBase(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject"]
    
    def getEnemies(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject" and d.id  != self.ownBot.id]
    
    # Check if objecy is in map
    def objectInMap(self):
        listObject = []
        props = self.ownBot.properties

       
        if (self.target_position.x != props.base.x and self.target_position.y != props.base.y) :
            if (self.target_object.type == "DiamondGameObject"):
                self.AllDiamonds = self.board.diamonds
                allDiamonds = self.sortDiamonds(self.AllDiamonds,self.ownBot.position)
                listObject = [allDiamonds[0],allDiamonds[1]]

            elif (self.target_object.type == "DiamondButtonGameObject"):
                self.AllButtons = self.getButtons()
                listObject = self.AllButtons

            elif (self.target_object.type == "TeleportGameObject"):
                self.AllPortal = self.getTeleporters()
                listObject = self.AllPortal
        if listObject :
            for obj in listObject:
                if obj != None:
                    if (obj.position.x == self.target_position.x and obj.position.y == self.target_position.y):
                        return
            self.target_object = None
            self.target_position = None
        else :
            return
        
    # initialize everything
    def initializeState(self):
        self.AllButtons = []
        self.AllBase = []
        self.AllDiamonds = []
        self.AllPortal = []
        self.AllEnemies = []
        for objects in self.board.game_objects:
            if (objects.type == "DiamondButtonGameObject"):
                self.AllButtons.append(objects)
            elif (objects.type == "DiamondGameObject" ):
                self.AllDiamonds.append(objects)
            elif (objects.type == "TeleportGameObject"):
                self.AllPortal.append(objects)
            elif (objects.type == "BotGameObject" and not self.ownBot.id == objects.id):
                self.AllEnemies.append(objects)
            elif (objects.type == "BaseGameObject"):
                self.AllBase.append(objects)

    
    
    def sortDiamonds(self,allDiamonds : List[GameObject], curr_position : Position):
        closest_blue_diamond = None
        closest_red_diamond = None
        min_blue_distance = float('inf')
        min_red_distance = float('inf')
        self.AllPortal.sort(key=lambda x : self.calculate_distance(x.position,curr_position))
        in_portal = self.AllPortal[0]
        out_portal = self.AllPortal[1]
        distance_initial_relative_portal = self.calculate_distance(in_portal.position,curr_position)
        for diamond in allDiamonds:
            #blue diamond
            distance = MainBot.calculate_distance(diamond.position,curr_position)
            distance_relative = self.calculate_distance(diamond.position,out_portal.position) + distance_initial_relative_portal
            if diamond.properties.points == 1:
                if (distance < min_blue_distance):
                    min_blue_distance = distance
                    closest_blue_diamond = diamond
                if (distance_relative < min_blue_distance):
                    min_blue_distance = distance_relative
                    closest_blue_diamond = in_portal
            else:
                if (distance < min_red_distance) :
                    min_red_distance = distance
                    closest_red_diamond = diamond
                if (distance_relative < min_red_distance):
                    min_red_distance = distance_relative
                    closest_red_diamond = in_portal
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
        self.TimeLeft = props.milliseconds_left
        self.make_decision()

        if self.target_position:
            delta_x , delta_y = self.get_direction(
                curr_position.x,
                curr_position.y,
                self.target_position.x,
                self.target_position.y,
                # obstacles,
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
        
        return self.next_move(board_bot,board)
        