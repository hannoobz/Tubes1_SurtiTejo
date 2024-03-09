from random import randint
import concurrent.futures
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_direction(current_x, current_y, dest_x, dest_y):
    horizontal = randint(0,1)
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if horizontal:
        if delta_x != 0:
            delta_y = 0
    else:
        if delta_y != 0:
            delta_x = 0
    return (delta_x, delta_y)

class BotWithTackle(BaseLogic):
    def __init__(self):
        self.enemy_counter = 0
        pass

    def calculate_distance(point_a : Position, point_b : Position):
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)

    def greedy(self,board,board_bot):
        goal_position = board_bot.properties.base
        maxpoint = board_bot.properties.diamonds*(0.7)**BotWithTackle.calculate_distance(board_bot.position,board_bot.properties.base)
        for i in board.diamonds:
                nextpoint = i.properties.points*(0.8)**BotWithTackle.calculate_distance(board_bot.position,i.position)
                if maxpoint<nextpoint and i.properties.points+board_bot.properties.diamonds<=board_bot.properties.inventory_size:
                    maxpoint = nextpoint
                    goal_position = i.position
        return goal_position,maxpoint
    
    def tackle(self,board,board_bot):
        enemies = [item.position  for item in board.game_objects if item.type=="BotGameObject" and item.id != board_bot.id]
        index = 0
        idx_choosen = -1
        for enemy in enemies:
            if BotWithTackle.calculate_distance(board_bot.position, enemy) == 1:
                idx_choosen = index
                break
            
            index += 1
        if (idx_choosen != -1):
            return enemies[idx_choosen]
        else:
            return False    
        

    def greedyPortal(self,board,board_bot):
        portals = [item.position for item in board.game_objects if item.type=="TeleportGameObject"]
        portal1_base = BotWithTackle.calculate_distance(portals[0],board_bot.properties.base)
        portal2_base = BotWithTackle.calculate_distance(portals[1],board_bot.properties.base)
        portal1_bot = BotWithTackle.calculate_distance(portals[0],board_bot.position)
        portal2_bot = BotWithTackle.calculate_distance(portals[1],board_bot.position)

        if portal1_base<portal2_base:
            exitpoint = portals[1]
        else:
            exitpoint = portals[0]

        if portal1_bot>portal2_bot:
            entrypoint = portals[1]
        else:
            entrypoint = portals[0]

        goal_position = entrypoint
        maxpoint = board_bot.properties.diamonds*(0.69)**(BotWithTackle.calculate_distance(board_bot.position,entrypoint)+BotWithTackle.calculate_distance(exitpoint,board_bot.properties.base));
        for i in board.diamonds:
                nextpoint = i.properties.points*(0.79)**(BotWithTackle.calculate_distance(board_bot.position,entrypoint)+BotWithTackle.calculate_distance(exitpoint,i.position))
                if maxpoint<nextpoint and i.properties.points+board_bot.properties.diamonds<=board_bot.properties.inventory_size:
                    maxpoint = nextpoint
        return goal_position,maxpoint

    def next_move(self, board_bot: GameObject, board: Board):
            # Get next move
            with concurrent.futures.ThreadPoolExecutor() as executor:

                future_one = executor.submit(BotWithTackle.greedyPortal, self, board, board_bot)
                future_second = executor.submit(BotWithTackle.greedy, self, board, board_bot)
                future_third = executor.submit(BotWithTackle.tackle, self, board, board_bot)

                result_one = future_one.result()
                result_two = future_second.result()
                result_third = future_third.result()
                

                greedyP, pPoint = result_one
                greedyN , nPoint = result_two
                if (pPoint>nPoint):
                    greedyS = greedyP
                else:
                    greedyS = greedyN
                
                # greedy by tackle
                if (result_third):
                    self.enemy_counter += 1
                    if (self.enemy_counter >=2):
                        self.enemy_counter = 0
                    else:
                        greedyS = result_third
                else:
                    self.enemy_counter = 0

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
