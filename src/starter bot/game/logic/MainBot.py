import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction
from typing import Tuple


class RandomLogic(BaseLogic):
    # def __init__(self):
    #     self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    #     self.goal_position: Optional[Position] = None
    #     self.current_direction = 0
    #     self.diamonds_position = []

    # def next_move(self, board_bot: GameObject, board: Board):
        # props = board_bot.properties
        # if props.diamonds == 5:
        #     # Move to base
        #     base = board_bot.properties.base
        #     self.goal_position = base
        # else:
        #     # Just roam around
        #     self.goal_position = None

        # current_position = board_bot.position
        # if self.goal_position:
        #     # We are aiming for a specific position, calculate delta
        #     delta_x, delta_y = get_direction(
        #         current_position.x,
        #         current_position.y,
        #         self.goal_position.x,
        #         self.goal_position.y,
        #     )
        # else:
        #     # Roam around
        #     delta = self.directions[self.current_direction]
        #     delta_x = delta[0]
        #     delta_y = delta[1]
        #     if random.random() > 0.6:
        #         self.current_direction = (self.current_direction + 1) % len(
        #             self.directions
        #         )
        # return delta_x, delta_y
    

    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.prev_position = (None,None)
        self.diamonds_position :Optional[list[Position]] = None
        self.target_positon : Optional[Position] = None
        self.go_back = 1
        
    
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        
        if (not self.diamonds_position):
            self.diamonds_position = [x.position  for x in board.game_objects if x.type == "DiamondGameObject" ]
            
        if props.diamonds == 5:
            self.target_positon = props.base
        else :
            self.target_positon = self.findFirstDiamond()
        
        curr_position = board_bot.position
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
        return self.diamonds_position[0]



