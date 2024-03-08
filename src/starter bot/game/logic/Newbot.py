from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction
import threading

class Newbot(BaseLogic):
    def __init__(self):
        # self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.state = 0
        self.target_object: Optional[GameObject] = None

    def calculate_distance(point_a : Position, point_b : Position):
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)
    
    def greedy(self,board,board_bot):
        goal_position = board_bot.properties.base;
        self.target_object = board_bot.properties.base;
        maxpoint = board_bot.properties.diamonds*(0.65)**Newbot.calculate_distance(board_bot.position,board_bot.properties.base);
        for i in board.diamonds:
                nextpoint = i.properties.points*(0.7)**Newbot.calculate_distance(board_bot.position,i.position)
                if maxpoint<nextpoint and i.properties.points+board_bot.properties.diamonds<=board_bot.properties.inventory_size:
                    maxpoint = nextpoint
                    goal_position = i.position
                    self.target_object = i
        return goal_position
    
    def portalCheck(board,board_bot):
        portals = [(item.position.x,item.position.y) for item in board.game_objects if item.type=="TeleportGameObject"]
        return (board_bot.position.x,board_bot.position.y) in portals
    
    def next_move(self, board_bot: GameObject, board: Board):
            greedys = Newbot.greedy(self,board,board_bot)
            delta_x, delta_y = get_direction(
                board_bot.position.x,
                board_bot.position.y,
                greedys.x,
                greedys.y)
            self.goal_position = greedys
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