from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class Newbot(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0
        self.chase_mode = False
        self.chosen: Optional[GameObject] = None

    def next_move(self, board_bot: GameObject, board: Board):
        current_position = board_bot.position
        base = board_bot.properties.base
        props = board_bot.properties

        if self.goal_position:
            if (self.goal_position.x==current_position.x and self.goal_position.y==current_position.y):
                self.goal_position=None;
            try:
                if(chosen not in board.diamonds):
                    self.goal_position=None
            except:
                pass;
        
        if self.goal_position:
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        else:
            point = 0
            nextpoint = 0;
            self.goal_position = base;
            for i in board.diamonds:
                nextpoint = (0.5**(abs(((i.position.x)+(i.position.y))-((current_position.x)-(current_position.y)))))*i.properties.points;
                print(point,nextpoint)
                if(point<nextpoint and props.diamonds+i.properties.points<=5):
                    point = nextpoint;
                    self.goal_position = i.position;
                    chosen = i;
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        return delta_x, delta_y