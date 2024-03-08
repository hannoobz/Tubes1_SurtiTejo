from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class Newbot(BaseLogic):
    def __init__(self):
        pass
        # self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def calculate_distance(point_a : Position, point_b : Position):
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)
    
    def greedy(self,board,board_bot):
        goal_position = board_bot.properties.base;
        maxpoint = board_bot.properties.diamonds*(0.7)**Newbot.calculate_distance(board_bot.position,board_bot.properties.base);
        for i in board.diamonds:
                nextpoint = i.properties.points*(0.8)**Newbot.calculate_distance(board_bot.position,i.position)
                if maxpoint<nextpoint and i.properties.points+board_bot.properties.diamonds<=board_bot.properties.inventory_size:
                    maxpoint = nextpoint
                    goal_position = i.position
        return goal_position,maxpoint
    
    def greedyPortal(self,board,board_bot):
        portals = [item.position for item in board.game_objects if item.type=="TeleportGameObject"]
        portal1_base = Newbot.calculate_distance(portals[0],board_bot.properties.base)
        portal2_base = Newbot.calculate_distance(portals[1],board_bot.properties.base)
        portal1_bot = Newbot.calculate_distance(portals[0],board_bot.position)
        portal2_bot = Newbot.calculate_distance(portals[1],board_bot.position)

        if portal1_base>portal2_base:
             exitpoint = portals[1]
        else:
             exitpoint = portals[0]
        
        if portal1_bot>portal2_bot:
             entrypoint = portals[1]
        else:
             entrypoint = portals[0]

        goal_position = entrypoint
        maxpoint = board_bot.properties.diamonds*(0.69)**(Newbot.calculate_distance(board_bot.position,entrypoint)+Newbot.calculate_distance(exitpoint,board_bot.properties.base));
        for i in board.diamonds:
                nextpoint = i.properties.points*(0.79)**(Newbot.calculate_distance(board_bot.position,entrypoint)+Newbot.calculate_distance(exitpoint,i.position))
                if maxpoint<nextpoint and i.properties.points+board_bot.properties.diamonds<=board_bot.properties.inventory_size:
                    maxpoint = nextpoint
        return goal_position,maxpoint
    
    def portalCheck(board,board_bot):
        portals = [(item.position.x,item.position.y) for item in board.game_objects if item.type=="TeleportGameObject"]
        return (board_bot.position.x,board_bot.position.y) in portals
    
    def next_move(self, board_bot: GameObject, board: Board):
            # Get next move
            greedyP,pPoint = Newbot.greedyPortal(self,board,board_bot)
            greedyN,nPoint = Newbot.greedy(self,board,board_bot)
            
            if (pPoint>nPoint):
                 greedyS = greedyP
            else:
                 greedyS = greedyN

            delta_x, delta_y = get_direction(
                board_bot.position.x,
                board_bot.position.y,
                greedyS.x,
                greedyS.y)
            # Unstuck from base
            try:
                if delta_x==0 and delta_y==0:
                     print("UNSTUCK")
                     delta_x,delta_y =  get_direction(
                          board_bot.position.x,
                          board_bot.position.y,
                          board.diamonds[0].position.x,
                          board.diamonds[0].position.y,
                     )
            except:
                 pass
                 
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