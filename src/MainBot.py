from typing import List, Optional, Union
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class MainBot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.prev_position = (None,None)
        self.diamonds :Optional[list[GameObject]] = None
        self.target_position : Optional[Position] = None
        self.board = None
        self.ownBot = None
        self.go_back = 1
        self.inventory_space_left = 0

    @staticmethod
    # using manhattan distance for grid like maps
    def calculate_distance(point_a : Position, point_b : Position):
        #using manhattan distance for grid map
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)
    
    def getTeleporters(self):
        return [d for d in self.board.game_objects if d.type == "TeleportGameObject"]   
    
    @staticmethod
    def getButtons(self):
        return [d for d in self.board.game_objects if d.type == "DiamondButtonGameObject"]   
    
    @staticmethod
    def sortDiamonds(allDiamonds : List[GameObject], curr_position : Position):
        closest_blue_diamond = None
        closest_red_diamond = None
        min_blue_distance = float('inf')
        min_red_distance = float('inf')
        for diamond in allDiamonds:
            #blue diamond
            distance = MainBot.calculate_distance(diamond.position,curr_position)
            if diamond.properties.points == 1:
                if (distance < min_blue_distance):
                    min_blue_distance = distance
                    closest_blue_diamond = diamond
            else:
                if (distance < min_red_distance) :
                    min_red_distance = distance
                    closest_red_diamond = diamond
        return  closest_blue_diamond,closest_red_diamond    

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        curr_position = board_bot.position
        self.board = board
        self.ownBot = board_bot
        base = board_bot.properties.base

        # setting up usefull list
        allBots = board.bots
        allPortals = self.getTeleporters().sort(key=lambda x : self.calculate_distance(x.position,curr_position))
        allDiamonds = MainBot.sortDiamonds(board.diamonds,curr_position)
        closest_blue_diamond = allDiamonds[0]
        closest_red_diamond = allDiamonds[1]
        allButtons = [d for d in board.game_objects if d.type == "DiamondButtonGameObject"]
        allbase = [d for d in board.game_objects if d.type == "BaseGameObject"]

        # decision making
        if props.diamonds == 5 or (props.diamonds >=3 and MainBot.calculate_distance(curr_position,props.base) >= 0.5*(board.width + board.height)) :
            # Move to base if inventory is full
            
            self.target_position = base
        else:
            # for now, aim for closest diamond
            if not self.target_position or (self.target_position.x == curr_position.x and self.target_position.y == curr_position.y):
                if not allDiamonds :
                    self.target_position = base
                else:
                    closest_diamond = None
                    
                    # mencari optimal jia kedua ada
                    if closest_blue_diamond and (not closest_red_diamond or MainBot.calculate_distance(closest_blue_diamond.position, curr_position) < MainBot.calculate_distance(closest_red_diamond.position, curr_position) * 0.75):
                        closest_diamond = closest_blue_diamond
                    elif closest_red_diamond and props.inventory_size - props.diamonds > 1:
                        closest_diamond = closest_red_diamond
                    
                    # update jika tidak ada diamond
                    self.target_position = closest_diamond.position if closest_diamond else base

                # Lebih baik balik ke base atau tidak
                if props.diamonds >= 4 and MainBot.calculate_distance(self.target_position, base) >= 0.5 * (board.width + board.height):
                    self.target_position = base
        if self.target_position:
            delta_x , delta_y = get_direction(
                curr_position.x,
                curr_position.y,
                self.target_position.x,
                self.target_position.y
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
        
