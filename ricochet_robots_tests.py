# ricochet_robots.py: Template para implementação do 1º projeto de Inteligência Artificial 2020/2021.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 42:
# 92436 Catarina Alegria
# 92468 Goncalo Fernandes

from search import Problem, Node, astar_search, breadth_first_tree_search, \
    depth_first_tree_search, greedy_search, compare_searchers, depth_first_graph_search
import sys
import time
import copy



class Robot:

    def __init__(self,line,column,color):
        self.color = color
        self.position = [line,column]

class Cell:

    def __init__(self):
        self.robot = False
        self.barriers = []
        self.minimumMoves = -1
    
    def addRobot(self):
        self.robot = True
    
    def addBarrier(self, barrier):
        self.barriers.append(barrier)

    def removeRobot(self):
        self.robot = False
    
    def hasBarrier(self, place):
        for x in self.barriers:
            if x == place:
                return True
        return False
    
    def hasRobot(self):
        return self.robot 



class RRState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = RRState.state_id
        RRState.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas."""

        if self.board.degree != other.board.degree:
            return self.board.degree < other.board.degree
        elif self.board.recentlyMoved[0] == self.board.targetColor and other.board.recentlyMoved[0] != other.board.targetColor:
            return True
        elif self.board.recentlyMoved[0] != self.board.targetColor and other.board.recentlyMoved[0] == other.board.targetColor:
            return False
        elif self.board.distance != other.board.distance:
            return self.board.distance < other.board.distance
        else:
            return (self.id < other.id)

      
    def __eq__(self, other):
        colorlist = ['Y', 'B', 'G', 'R']
        colorlist.remove(self.board.targetColor)
        board1 = {self.board.robot_position(colorlist[0]), self.board.robot_position(colorlist[1]), self.board.robot_position(colorlist[2])}
        board2 = {other.board.robot_position(colorlist[0]), other.board.robot_position(colorlist[1]), other.board.robot_position(colorlist[2])}
        
        return board1 == board2 and self.board.robot_position(self.board.targetColor) == other.board.robot_position(self.board.targetColor)
    
    def __hash__(self):
        return self.id
       


class Board:
    """ Representacao interna de um tabuleiro de Ricochet Robots. """

    def __init__(self, filename:str):

        f=open(filename,'r')
        Lines = f.readlines()
        self.recentlyMoved = []
        self.robots = []
        self.degree = 0
        self.distance = 0
        self.oneMore = 0

        count = 0
        for line in Lines:
            if count==0:
                self.dimension=int(line)
                self.cells = [[Cell() for x in range(self.dimension + 1)] for y in range(self.dimension + 1)] 
                for i in range(1, self.dimension + 1):
                    self.cells[1][i].addBarrier('u')
                    self.cells[i][1].addBarrier('l')
                    self.cells[self.dimension][i].addBarrier('d')
                    self.cells[i][self.dimension].addBarrier('r')

            elif 1<=count<=4:
                aux=line.split(" ")

                self.cells[int(aux[1])][int(aux[2])].addRobot()
                self.robots.append(Robot(int(aux[1]), int(aux[2]), aux[0][0]))

            elif count==5 :
                aux=line.split(" ")
                self.targetColor = aux[0][0]
                self.targetPosition = (int(aux[1]),int(aux[2]))

            elif count==6 :
                self.numberBarriers = int(line)

            else:
                if line != '\n':
                    aux=line.split(" ")
                    self.cells[int(aux[0])][int(aux[1])].addBarrier(aux[2][0])

            count+=1

        f.close()

        self.compute_minimum_moves(self.targetPosition[0], self.targetPosition[1], 0, None)

    def hasRobot(self, row, column):
        for r in self.robots:
            if r.position[0] == row and r.position[1] == column:
                return True
        return False

    def compute_minimum_moves(self, row, column, moves, fromDirection):
        if(self.cells[row][column].minimumMoves <= moves and self.cells[row][column].minimumMoves != -1):
            return
        else:
            self.cells[row][column].minimumMoves = moves
        
        if self.check_moves(row, column, 'u'):
            if fromDirection == 'u':
                self.compute_minimum_moves(row-1, column, moves, 'u')
            else:
                self.compute_minimum_moves(row-1, column, moves + 1, 'u')

        if self.check_moves(row, column, 'd'):
            if fromDirection == 'd':
                self.compute_minimum_moves(row+1, column, moves, 'd')
            else:
                self.compute_minimum_moves(row+1, column, moves + 1, 'd')
            
        if self.check_moves(row, column, 'l'):
            if fromDirection == 'l':
                self.compute_minimum_moves(row, column - 1, moves, 'l')
            else:
                self.compute_minimum_moves(row, column - 1, moves + 1, 'l')

        if self.check_moves(row, column, 'r'):
            if fromDirection == 'r':
                self.compute_minimum_moves(row, column + 1, moves, 'r')
            else:
                self.compute_minimum_moves(row, column + 1, moves + 1, 'r')


    def robot_position(self, robot: str):
        for r in self.robots:
            if r.color == robot:
                return (r.position[0], r.position[1])

    def check_moves(self, row, column, direction):
        if direction == 'u':
            return not (self.cells[row][column].hasBarrier('u') or (row > 0 and self.cells[row-1][column].hasBarrier('d')))
        if direction == 'd':
            return not (self.cells[row][column].hasBarrier('d') or (row < self.dimension and self.cells[row+1][column].hasBarrier('u')))
        if direction == 'l':
            return not (self.cells[row][column].hasBarrier('l') or (column > 0 and self.cells[row][column-1].hasBarrier('r')))
        if direction == 'r':
            return not (self.cells[row][column].hasBarrier('r') or (column < self.dimension and self.cells[row][column+1].hasBarrier('l')))
    
    
    def can_go_direction(self, row, column, direction):
        if direction == 'u':
            return not (self.cells[row][column].hasBarrier('u') or (row > 0 and self.cells[row-1][column].hasBarrier('d'))
                        or (self.hasRobot(row-1, column)))
        if direction == 'd':
            return not (self.cells[row][column].hasBarrier('d') or (row < self.dimension and self.cells[row+1][column].hasBarrier('u'))
                        or (self.hasRobot(row+1, column)))
        if direction == 'l':
            return not (self.cells[row][column].hasBarrier('l') or (column > 0 and self.cells[row][column-1].hasBarrier('r'))
                        or (self.hasRobot(row, column-1)))
        if direction == 'r':
            return not (self.cells[row][column].hasBarrier('r') or (column < self.dimension and self.cells[row][column+1].hasBarrier('l'))
                        or (self.hasRobot(row, column+1)))
    
    def update_robot_pos(self, color, row, column):
        for r in self.robots:
            if r.color == color:
                self.cells[r.position[0]][r.position[1]].removeRobot()
                self.cells[row][column].addRobot()
                r.position = [row, column]
                self.degree = 4
                for i in range(len(self.recentlyMoved)):
                    if self.recentlyMoved[i] == color:
                        self.recentlyMoved.remove(color)
                        self.degree = i
                        break

        self.recentlyMoved.insert(0, color)
        self.distance = self.calculate_distance()
        self.one_more()

    def calculate_distance(self):
        targetPos = self.targetPosition
        robotPos = self.robot_position(self.targetColor)
        return (abs(targetPos[0] - robotPos[0]) + abs(targetPos[1] - robotPos[1]))

    def one_more(self):
        
        if(self.can_go_direction(self.targetPosition[0], self.targetPosition[1], 'u') and self.can_go_direction(self.targetPosition[0], self.targetPosition[1], 'd') and
            self.can_go_direction(self.targetPosition[0], self.targetPosition[1], 'l') and self.can_go_direction(self.targetPosition[0], self.targetPosition[1], 'r')):
            self.oneMore = 1
        else:
            self.oneMore = 0
        
        
    
    def copy(self):
        newBoard = copy.copy(self)
        newBoard.robots = copy.deepcopy(self.robots)
        newBoard.recentlyMoved = copy.deepcopy(self.recentlyMoved)
        newBoard.oneMore = copy.deepcopy(self.oneMore)
        return newBoard



def parse_instance(filename: str) -> Board:
    return Board(filename)

def check_directions(board: Board, robot: Robot):
    pos = robot.position
    directions = [True, True, True, True]   # [up, down, left, right]

    if not board.can_go_direction(pos[0], pos[1], 'u'):
        directions[0] = False
    if not board.can_go_direction(pos[0], pos[1], 'd'):
        directions[1] = False
    if not board.can_go_direction(pos[0], pos[1], 'l'):
        directions[2] = False
    if not board.can_go_direction(pos[0], pos[1], 'r'):
        directions[3] = False
    
    return directions

class RicochetRobots(Problem):
    def __init__(self, board: Board):
        self.board = board
        self.initial = RRState(board)

    def actions(self, state: RRState):

        listActions = []

        for r in state.board.robots:

            directions = check_directions(state.board, r)

            if directions[0]:
                listActions.append((r.color, 'u'))
            if directions[1]:
                listActions.append((r.color, 'd'))
            if directions[2]:
                listActions.append((r.color, 'l'))
            if directions[3]:
                listActions.append((r.color, 'r'))
        
        return listActions


    def result(self, state: RRState, action):
        resultState = RRState(state.board.copy())
        robot = next(filter(lambda x: x.color == action[0], resultState.board.robots))

        r = robot.position[0]
        c = robot.position[1]
        if action[1] == 'u':
            while resultState.board.can_go_direction(r, c, 'u'):
                r -= 1

        elif action[1] == 'd':
            while resultState.board.can_go_direction(r, c, 'd'):
                r += 1

        elif action[1] == 'l':
            while resultState.board.can_go_direction(r, c, 'l'):
                c -= 1
        
        elif action[1] == 'r':
            while resultState.board.can_go_direction(r, c, 'r'):
                c += 1

        resultState.board.update_robot_pos(robot.color, r, c)
        return resultState
        

    def goal_test(self, state: RRState):
        for r in state.board.robots:
            if r.color == state.board.targetColor:
                return state.board.targetPosition[0] == r.position[0] and state.board.targetPosition[1] == r.position[1]

    def h(self, node: Node):

        color = node.state.board.targetColor
        targetPos = node.state.board.targetPosition
        robotPos = node.state.board.robot_position(color)


        oneMoreMore = 0  
        
        """
        if(node.state.board.oneMore == 0):
            if(node.state.board.cells[robotPos[0]][robotPos[1]].minimumMoves == 1):
                if(robotPos[0] == targetPos[0]):
                    if(robotPos[1] > targetPos[1]):
                        if (node.state.board.can_go_direction(targetPos[0], targetPos[1], 'l')):
                            oneMoreMore = 1
                    if(robotPos[1] < targetPos[1]):
                        if (node.state.board.can_go_direction(targetPos[0], targetPos[1], 'r')):
                            oneMoreMore = 1
                if(robotPos[1] == targetPos[1]):
                    if(robotPos[0] > targetPos[0]):
                        if (node.state.board.can_go_direction(targetPos[0], targetPos[1], 'u')):
                            oneMoreMore = 1
                    if(robotPos[0] < targetPos[0]):
                        if (node.state.board.can_go_direction(targetPos[0], targetPos[1], 'd')):
                            oneMoreMore = 1
        
        """

        """
        return abs(robotPos[0] - targetPos[0]) + abs(robotPos[1] - targetPos[1])
        """    
        return node.state.board.cells[robotPos[0]][robotPos[1]].minimumMoves 
        """+ node.state.board.oneMore + oneMoreMore"""
        


if __name__ == "__main__":

    start_time = time.time()
    
    """
    board1 = parse_instance(sys.argv[1] + "i1.txt")
    board2 = parse_instance(sys.argv[1] + "i2.txt")
    board3 = parse_instance(sys.argv[1] + "i3.txt")
    board4 = parse_instance(sys.argv[1] + "i4.txt")
    board5 = parse_instance(sys.argv[1] + "i5.txt")
    board6 = parse_instance(sys.argv[1] + "i6.txt")
    board7 = parse_instance(sys.argv[1] + "i7.txt")
    board8 = parse_instance(sys.argv[1] + "i8.txt")
    """
    board1 = parse_instance(sys.argv[1] + "01_5x5-05.txt")
    board2 = parse_instance(sys.argv[1] + "02_6x6-06.txt")
    board3 = parse_instance(sys.argv[1] + "03_6x6-10.txt")
    board4 = parse_instance(sys.argv[1] + "04_7x7-04.txt")
    board5 = parse_instance(sys.argv[1] + "05_7x7-06.txt")
    board6 = parse_instance(sys.argv[1] + "06_8x8-07.txt")
    board7 = parse_instance(sys.argv[1] + "07_9x9-07.txt")
    board8 = parse_instance(sys.argv[1] + "08_9x9-08.txt")
    board9 = parse_instance(sys.argv[1] + "09_10x10-06.txt")
    
    
    problems=[]
    problems.append(RicochetRobots(board1))
    problems.append(RicochetRobots(board2))
    problems.append(RicochetRobots(board3))
    problems.append(RicochetRobots(board4))
    problems.append(RicochetRobots(board5))
    problems.append(RicochetRobots(board6))
    problems.append(RicochetRobots(board7))
    problems.append(RicochetRobots(board8))
    problems.append(RicochetRobots(board9))

    """
    for i in range(1,9):
        for j in range (1,9):
            print(board.cells[i][j].minimumMoves, end=' ')
        print(" ")
    """

    for i in range(0, len(problems)):
        
        start_time = time.time()
        solution_node = astar_search(problems[i])
        print("Teste ", i+1, ": ", (time.time() - start_time), " seconds")

    """
    actions=[]

    node = solution_node

    while node.parent != None:
        actions.insert(0, node.action)
        node = node.parent
    
    print(len(actions))
    for action in actions:
        print(action[0], action[1])
    """
    
    """
    compare_searchers(problems, "-123456789", [astar_search, breadth_first_tree_search])
    


    print("--- %s seconds ---" % (time.time() - start_time))
    """