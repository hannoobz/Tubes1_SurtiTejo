from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class OldBot3(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.state = 0
    
    def calculate_distance(point_a : Position, point_b : Position):
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)

    def next_move(self, board_bot: GameObject, board: Board):
        current_position = board_bot.position
        base = board_bot.properties.base
        props = board_bot.properties

        if self.state==0:
            self.goal_position = base;
            maxpoint = 0.001;
            # print(points)
            for i in board.diamonds:
                nextpoint = i.properties.points*(0.7)**OldBot3.calculate_distance(current_position,i.position)
                if maxpoint<nextpoint and i.properties.points+props.diamonds<=props.inventory_size:
                    maxpoint = nextpoint
                    self.goal_position = i.position
            # print(maxpoint);
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            self.state = 1;
            # print(self.goal_position.x,self.goal_position.y,nextpoint)
            return delta_x, delta_y
        elif self.state==1:
            # print(self.goal_position.x,self.goal_position.y)
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            if(current_position.x+delta_x==self.goal_position.x and current_position.y+delta_y==self.goal_position.y) or (current_position.x==self.goal_position.x and current_position.y==self.goal_position.y):
                self.state=0

        return delta_x, delta_y

        
        # if self.goal_position:

        # else:
        #     point = 0
        #     nextpoint = 0;
        #     self.goal_position = base;
        #     for i in board.diamonds:
        #         nextpoint = (0.5**(abs(((i.position.x)+(i.position.y))-((current_position.x)-(current_position.y)))))*i.properties.points;
        #         print(point,nextpoint)
        #         if(point<nextpoint and props.diamonds+i.properties.points<=5):
        #             point = nextpoint;
        #             self.goal_position = i.position;
        #             chosen = i;
        #     delta_x, delta_y = get_direction(
        #         current_position.x,
        #         current_position.y,
        #         self.goal_position.x,
        #         self.goal_position.y,
        #     )
        # return delta_x, delta_y