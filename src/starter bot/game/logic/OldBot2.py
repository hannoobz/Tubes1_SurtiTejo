from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class OldBot2(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.prev_position = (None,None)
        self.diamonds :Optional[list[GameObject]] = None
        self.target_positon : Optional[Position] = None
        self.go_back = 1
        self.inventory_space_left = 0
        
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        diamond_locations = board.diamonds
        if (not self.diamonds):
            self.diamonds = diamond_locations
            
        elif (self.diamonds != diamond_locations):
            self.diamonds = diamond_locations
   
        curr_position = board_bot.position

        if props.diamonds == 5:
            self.target_positon = props.base
        else :
            if (not self.target_positon or (self.target_positon.x == curr_position.x and self.target_positon.y == curr_position.y)):
                self.inventory_space_left = board_bot.properties.inventory_size -  board_bot.properties.diamonds
                self.target_positon = self.findClosestDiamond(curr_position,board)
                if (self.target_positon.x == 0 and self.target_positon.y == 0 ):
                    self.target_positon = props.base
        
        
        if self.target_positon:
            delta_x , delta_y = get_direction(
                curr_position.x,
                curr_position.y,
                self.target_positon.x,
                self.target_positon.y
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
        
    def findFirstDiamond(self):
        return self.diamonds[0].position

    def findClosestDiamond(self, current_position: Position, board: Board) -> Position:
        best_position = 0,0 # It's assumed to be a tuple, but should ideally be a Position object
        best_distance = float('inf')  # Use float('inf') for initial comparison to simplify logic

        for diamond in self.diamonds:
            if (self.inventory_space_left == 1 and diamond.properties.points == 2):
                pass
            else :
                distance = OldBot2.calculate_distance(current_position, diamond.position)
                if distance < best_distance:
                    best_distance = distance
                    best_position = diamond.position

        return best_position
            
    @staticmethod
    def calculate_distance(point_a : Position, point_b : Position):
        #using manhattan distance for grid map
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)