# ricochet_robots.py: Template para implementação do 1º projeto de Inteligência Artificial 2020/2021.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

from search import Problem, Node, astar_search, breadth_first_tree_search, \
    depth_first_tree_search, greedy_search, depth_limited_search, compare_searchers
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
        
        return (self.id < other.id)


class Board:
    """ Representacao interna de um tabuleiro de Ricochet Robots. """

    def __init__(self, filename:str):

        f=open(filename,'r')
        Lines = f.readlines()
        self.robots = []

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
                        or (row > 0 and self.cells[row-1][column].hasRobot()))
        if direction == 'd':
            return not (self.cells[row][column].hasBarrier('d') or (row < self.dimension and self.cells[row+1][column].hasBarrier('u'))
                        or (row < self.dimension and self.cells[row+1][column].hasRobot()))
        if direction == 'l':
            return not (self.cells[row][column].hasBarrier('l') or (column > 0 and self.cells[row][column-1].hasBarrier('r'))
                        or (column > 0 and self.cells[row][column-1].hasRobot()))
        if direction == 'r':
            return not (self.cells[row][column].hasBarrier('r') or (column < self.dimension and self.cells[row][column+1].hasBarrier('l'))
                        or (column < self.dimension and self.cells[row][column+1].hasRobot()))
    
    def update_robot_pos(self, color, row, column):
        for r in self.robots:
            if r.color == color:
                self.cells[r.position[0]][r.position[1]].removeRobot()
                self.cells[row][column].addRobot()
                r.position = [row, column]



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
        resultState = copy.deepcopy(state)
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
        return node.state.board.cells[robotPos[0]][robotPos[1]].minimumMoves


if __name__ == "__main__":

    board1 = parse_instance(sys.argv[1] + "i1.txt")
    board2 = parse_instance(sys.argv[1] + "i2.txt")
    board3 = parse_instance(sys.argv[1] + "i3.txt")
    board4 = parse_instance(sys.argv[1] + "i4.txt")
    board5 = parse_instance(sys.argv[1] + "i5.txt")
    board6 = parse_instance(sys.argv[1] + "i6.txt")
    board7 = parse_instance(sys.argv[1] + "i7.txt")
    board8 = parse_instance(sys.argv[1] + "i8.txt")

    start_time = time.time()

    print(board1.robot_position('Y'))
    print(board1.robot_position('G'))
    print(board1.robot_position('B'))
    print(board1.robot_position('R'))


    problems=[]
    problems.append(RicochetRobots(board1))
    problems.append(RicochetRobots(board2))
    #problems.append(RicochetRobots(board3))
    problems.append(RicochetRobots(board4))
    problems.append(RicochetRobots(board5))
    problems.append(RicochetRobots(board6))
    problems.append(RicochetRobots(board7))
    problems.append(RicochetRobots(board8))

    """
    for i in [1,2,3]:
        for j in [1,2,3]:
            print(board.cells[i][j].minimumMoves, end=' ')
        print("\n")
    """

    """solution_node = greedy_search(problem)"""

    compare_searchers(problems, "-1245678", [breadth_first_tree_search, greedy_search, astar_search])

    print("--- %s seconds ---" % (time.time() - start_time))
