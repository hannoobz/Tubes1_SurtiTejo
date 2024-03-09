from typing import List, Optional, Union
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
import random
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

# Utilities
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def position_equals(a: Position, b: Position):
    return a.x == b.x and a.y == b.y


# Hash wrapper

class HashClass:
    def __init__(self, instance_object):
        self.instance_object = instance_object

    def __has__(self):
        return hash(self.instance_object.id)
# Main Class, greedy logic
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
        self.DiamondAfterPortal : Optional[GameObject] = None
        self.EnterPortal : Optional[GameObject] = None
        self.ExitPortal : Optional[GameObject] = None
        self.TimeLeft = None

    # getters
    def get_direction(self,current_x, current_y, dest_x, dest_y):
        print("Here")
        if (self.target_object):
            if (self.target_object.type == "TeleportGameObject"):
                print("CHASING TELEPORTER RIGHT NOW")
                if (self.DiamondAfterPortal):
                    print(self.DiamondAfterPortal)
                else :
                    print("CHASING PORTAL FOR NO REASON")
            else :
                print(self.target_object.type)
        else:
            print(self.target_position)
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
            print("Target position : ")
            print(self.target_position)
            print()
            print("Enter portal : ")
            print(self.EnterPortal)
            print()
            print("exit portal : ")
            print(self.ExitPortal)
            print()
            print("My position : ")
            print(self.ownBot.position)
            print()
            print("Target object")
            print(self.target_object)
            if (self.ownBot.position.x == self.target_position.x and self.ownBot.position.y == self.target_position.y):
                print("In place")
                print(self.DiamondAfterPortal)
                if (self.DiamondAfterPortal):
                    print("There is diamondafterportal")
                    self.target_position = self.DiamondAfterPortal.position
                    self.target_object = self.DiamondAfterPortal
                    self.DiamondAfterPortal = None
                    self.EnterPortal = None
                    self.ExitPortal = None
                    return self.get_direction(self.ownBot.position.x,self.ownBot.position.y,self.target_position.x,self.target_position.y)
                else:
                    self.target_position = None
                    self.DiamondAfterPortal = None
                    self.EnterPortal = None
                    self.ExitPortal = None
                    self.sortDiamonds(self.AllDiamonds,self.ownBot.position,False)

                    return self.get_direction(self.ownBot.position.x,self.ownBot.position.y, self.target_position.x,self.target_position.y)
                

        return (delta_x, delta_y)
    
    def getTeleporters(self):
        return [d for d in self.board.game_objects if d.type == "TeleportGameObject"]   
    
    def getButtons(self):
        return [d for d in self.board.game_objects if d.type == "DiamondButtonGameObject"]

    def getBase(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject"]
    
    def getEnemies(self):
        return [d for d in self.board.game_objects if d.type == "BaseGameObject" and d.id  != self.ownBot.id]
    

    # Algorithm
    def findNearestDiamond(self, closest_blue_diamond , closest_red_diamond, board_bot, board):
        closest_diamond = None  
        props = board_bot.properties
        base = board_bot.properties.base
                    # mencari optimal jia kedua ada
        if closest_blue_diamond and closest_red_diamond:
            if ( (0.7) ** self.calculate_distance(self.ownBot.position, closest_blue_diamond.position)  * (1) > (0.7)** self.calculate_distance(self.ownBot.position,closest_red_diamond.position)  * (2) ):  
                closest_diamond  = closest_blue_diamond
            else :
                if props.inventory_size - props.diamonds > 1:
                    closest_diamond  = closest_red_diamond
                else :
                    closest_diamond = closest_blue_diamond
        elif closest_blue_diamond and not closest_red_diamond:
            closest_diamond = closest_blue_diamond
        elif closest_red_diamond and props.inventory_size - props.diamonds > 1:
            closest_diamond = closest_red_diamond
                    
                    # update jika tidak ada diamond
        self.target_position = closest_diamond.position if closest_diamond else base
        if (self.target_position.x == self.ownBot.position.x and self.target_position.y == self.ownBot.position.y):
            print("DISINI")
            print(closest_diamond)
            print(closest_red_diamond)
        self.target_object = closest_diamond if closest_diamond else None

                # Lebih baik balik ke base atau tidak
        if props.diamonds >= 3 and MainBot.calculate_distance(self.target_position, base) >= 0.5 * (board.width + board.height) and MainBot.calculate_distance(self.ownBot.position,self.target_position) >= 0.25 * (board.width + board.height):
            self.target_position = base
            self.target_object = None
            self.EnterPortal = None
            self.ExitPortal = None
            self.DiamondAfterPortal = None

    def botInPortal(self):
        if (self.EnterPortal and self.ExitPortal):
            return (self.ownBot.position.x == self.EnterPortal.position.x and self.ownBot.position.y == self.EnterPortal.position.y) or (self.ownBot.position.x == self.ExitPortal.position.x and self.ownBot.position.y == self.ExitPortal.position.y)
        elif (self.EnterPortal):
            return (self.ownBot.position.x == self.EnterPortal.position.x and self.ownBot.position.y == self.EnterPortal.position.y)
        elif (self.ExitPortal):
            return (self.ownBot.position.x == self.ExitPortal.position.x and self.ownBot.position.y == self.ExitPortal.position.y)
        else :
            return False
        
            

    def make_decision(self):
                # for now, aim for closest diamond
        curr_position = self.ownBot.position
        props = self.ownBot.properties
        base = props.base
        if props.diamonds == self.ownBot.properties.inventory_size or (props.diamonds >= 4 and MainBot.calculate_distance(self.target_position, base) >= 0.5 * (self.board.width + self.board.height) and MainBot.calculate_distance(self.ownBot.position,self.target_position) >= 0.10 * (self.board.width + self.board.height)) or (props.diamonds >= 0.6 * props.inventory_size and self.TimeLeft <= 15000) or (props.diamonds >= 0.4 * props.inventory_size and self.TimeLeft <= 12000) :
            # Move to base if inventory is full
            self.target_position = base
            self.target_object = None
            self.EnterPortal = None
            self.ExitPortal = None
            self.DiamondAfterPortal = None
        else:
            if not (self.target_position) :
                self.pickTarget(True)
            elif (self.botInPortal()):
                self.pickTarget(False)
            elif (self.ownBot.position.x == self.target_position.x and self.ownBot.position.y == self.target_position.y):
                self.pickTarget(True)
            elif ( (abs(curr_position.x - self.prev_position[0]) + abs(curr_position.y - self.prev_position[1])  ) >= 5):
                self.pickTarget(True)
            else:
                self.objectInMap()
    
    # pick path
    def pickTarget(self, usePortal : bool):
        self.initializeState()
        curr_position = self.ownBot.position
        props = self.ownBot.properties
        self.sortDiamonds(self.AllDiamonds,curr_position, usePortal)

    # Check if objecy is in map
    def objectInMap(self):
        listObject = []
        props = self.ownBot.properties
        if (self.target_position.x != props.base.x and self.target_position.y != props.base.y and self.target_object) :
            if (self.target_object):
                if (self.target_object.type == "DiamondGameObject"):
                    listObject = self.AllDiamonds

                elif (self.target_object.type == "DiamondButtonGameObject"):
                    self.AllButtons = self.getButtons()
                    listObject = self.AllButtons

                elif (self.target_object.type == "TeleportGameObject"):
                    self.AllPortal = self.getTeleporters()
                    listObject = self.AllPortal

            if listObject :
                for obj in listObject:
                    if obj:
                        if (obj.position.x == self.target_position.x and obj.position.y == self.target_position.y):
                            return
                        
                self.target_object = None
                self.target_position = None
                self.EnterPortal = None
                self.ExitPortal = None
                self.DiamondAfterPortal = None   
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

    def sortDiamonds(self,allDiamonds : List[GameObject], curr_position : Position, usePortal : bool):
        closest_blue_diamond = None
        closest_red_diamond = None
        closest_blue_diamond_portal = None
        closest_red_diamond_portal = None
        in_portal = self.AllPortal[0]
        out_portal = self.AllPortal[1]
        diamond_distances = self.calculate_distances_parallel(self.ownBot.position,allDiamonds,usePortal)
        self.DiamondAfterPortal = None
        self.ExitPortal = None
        self.EnterPortal = None
        if (diamond_distances[0]):
            closest_blue_diamond, min_distance_blue  = min(diamond_distances[0].items(), key=lambda item: item[1])
            closest_blue_diamond = closest_blue_diamond.instance_object
            if (diamond_distances[1]):
                closest_blue_diamond_portal , min_portal_distance_blue = min(diamond_distances[1].items(), key=lambda item: item[1])
                closest_blue_diamond_portal = closest_blue_diamond_portal.instance_object

                if (min_portal_distance_blue < min_distance_blue):
                    closest_blue_diamond = in_portal
            
        if (diamond_distances[2]):
            closest_red_diamond,min_distance_red = min(diamond_distances[2].items(), key=lambda item: item[1])
            closest_red_diamond = closest_red_diamond.instance_object
            if (diamond_distances[3]):
                closest_red_diamond_portal, min_portal_distance_red  = min(diamond_distances[3].items(), key=lambda item: item[1])
                closest_red_diamond_portal = closest_red_diamond_portal.instance_object
                if (min_portal_distance_red < min_distance_red):
                    closest_red_diamond = in_portal
        print("WHATTT")
        
        print(diamond_distances[2])

        self.findNearestDiamond(closest_blue_diamond,closest_red_diamond,self.ownBot,self.board)
        if (self.target_object):
            if (self.target_object.type == "TeleportGameObject"):
                self.ExitPortal = out_portal
                self.EnterPortal = in_portal
                if (self.target_object.properties.points == 1):
                    self.DiamondAfterPortal = closest_blue_diamond_portal
                else :
                    self.DiamondAfterPortal = closest_red_diamond_portal
    
    # using manhattan distance for grid like maps    
    @staticmethod
    def calculate_distance(point_a : Position, point_b : Position):
        #using manhattan distance for grid map
        return abs(point_b.x - point_a.x) + abs(point_b.y - point_a.y)
    
    def calculate_distances_parallel(self,bot_position, targets, use_portal):
        distances_blue = {}
        distances_red = {}
        distances_blue_portal = {}
        distances_red_protal = {}
        self.AllPortal.sort(key=lambda x : self.calculate_distance(x.position,self.ownBot.position))
        in_portal = self.AllPortal[0]
        out_portal = self.AllPortal[1]
        distance_initial_relative_portal = self.calculate_distance(in_portal.position,self.ownBot.position)

        with ThreadPoolExecutor(max_workers=len(targets)) as executor:
            future_to_target = {executor.submit(MainBot.calculate_distance, bot_position, target.position): target for target in targets}
            for future in concurrent.futures.as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    if (target.properties.points == 1):
                        distances_blue[HashClass(target)] = future.result()
                        
                    else :
                        distances_red[HashClass(target)] = future.result()

                except Exception as exc:
                    print(f'Generated an exception: {exc}')
        
        if (use_portal):
            with ThreadPoolExecutor(max_workers=len(targets)) as executor:
                future_to_target_portal = {executor.submit(MainBot.calculate_distance, out_portal.position, target.position): target for target in targets}
                for future in concurrent.futures.as_completed(future_to_target_portal):
                    target = future_to_target_portal[future]
                    try:
                        if (target.properties.points == 1):
                            distances_blue_portal[HashClass(target)] = future.result() + distance_initial_relative_portal
                            
                        else :
                            distances_red_protal[HashClass(target)] = future.result() + distance_initial_relative_portal

                    except Exception as exc:
                        print(f'Generated an exception: {exc}')
        
        # print(distances_red)
        return distances_blue, distances_blue_portal, distances_red, distances_red_protal
        
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
        
        return self.next_move(board_bot,board)
        
