# Modified by: Kejkaew Thanasuan
# Date: April 2024
# reference: Multi-agent Pac-Man Stanford CS221 Spring 2019-2020

"""
ห้ามแก้ไขโค้ดในทุกๆ  class ในไฟล์นี้ ยกเว้นในส่วนของ setArgs() ที่ใช้ในการเรียก agent และการเปลี่ยนแปลงต่างๆ

Pacman.py holds the logic for the classic pacman game along with the main
code to run a game.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!

"""

from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearestPoint
from util import manhattanDistance
import util, layout
import graphicsDisplay
import sys, types, time, random, os

class GameState:
  """
  A GameState specifies the full game state, including the food, capsules,
  agent configurations and score changes.

  GameStates are used by the Game object to capture the actual state of the game and
  can be used by agents to reason about the game.

  Much of the information in a GameState is stored in a GameStateData object.  We
  strongly suggest that you access that data via the accessor methods below rather
  than referring to the GameStateData object directly.

  """

  ####################################################
  # Accessor methods: use these to access state data #
  ####################################################

  def getLegalActions( self, agentIndex=0 ):
    """
    Returns the legal actions for the agent specified.
    """
    if self.isWin() or self.isLose(): return []

    if agentIndex == 0 or agentIndex == 1:  # Pacman is moving
      return PacmanRules.getLegalActions( self, agentIndex )

  def generateSuccessor( self, agentIndex, action):
    """
    Returns the successor state after the specified agent takes the action.
    """
    # Check that successors exist
    if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')

    # Copy current state
    state = GameState(self)

    # Let agent's logic deal with its action's effects on the board
    # fixed by: Kejkaew Thanasuan
    if agentIndex == 0 or agentIndex == 1:  # Pacman is moving
      state.data._eaten = [False for i in range(state.getNumAgents())]
      PacmanRules.applyAction( state, action,agentIndex )

     # Time passes
    
    pacmanState = state.data.agentStates[agentIndex]
    PacmanRules.decrementTimer(pacmanState)

    # steal food
    pacman2Index = (agentIndex+1)%2
    pacman2 = state.getPacmanState(pacman2Index)
    if pacman2.scaredTimer > 0 and pacmanState.scaredTimer == 0:
      PacmanRules.checkSteal( state, agentIndex )

    # Book keeping
    state.data._agentMoved = agentIndex
    state.data.score[agentIndex] += state.data.scoreChange[agentIndex]
    return state

  def getLegalPacmanActions( self,agentIndex=0 ):
    return self.getLegalActions( agentIndex )

  def generatePacmanSuccessor( self, action,agentIndex=0 ):
    """
    Generates the successor state after the specified pacman move
    """
    return self.generateSuccessor( agentIndex, action )

  def getPacmanState( self ,agentIndex=0):
    """
    Returns an AgentState object for pacman (in game.py)

    state.configuration.pos gives the current position
    state.direction gives the travel vector
    """
    return self.data.agentStates[agentIndex].copy()

  def getPacmanPosition( self,agentIndex=0 ):
    return self.data.agentStates[agentIndex].getPosition()

  def getGhostStates( self ):
    return self.data.agentStates[1:]

  def getGhostState( self, agentIndex ):
    if agentIndex == 0 or agentIndex >= self.getNumAgents():
      raise Exception("Invalid index passed to getGhostState")
    return self.data.agentStates[agentIndex]

  def getGhostPosition( self, agentIndex ):
    if agentIndex == 0:
      raise Exception("Pacman's index passed to getGhostPosition")
    return self.data.agentStates[agentIndex].getPosition()

  def getGhostPositions(self):
    return [s.getPosition() for s in self.getGhostStates()]

  def getNumAgents( self ):
    return len( self.data.agentStates )
  
  def getScaredTimes( self,agentIndex=0 ):
    return self.data.agentStates[agentIndex].scaredTimer
  
  def getScore( self,agentIndex=0):
    # print("score: ",self.data.score[agentIndex])
    return self.data.score[agentIndex]
  
  def getScores( self): #จัดการเรื่อง deepcopy
    return self.data.score
  

  def getCapsules(self):
    """
    Returns a list of positions (x,y) of the remaining capsules.
    """
    return self.data.capsules

  def getNumFood( self ):
    return self.data.food.count()

  def getFood(self):
    """
    Returns a Grid of boolean food indicator variables.

    Grids can be accessed via list notation, so to check
    if there is food at (x,y), just call

    currentFood = state.getFood()
    if currentFood[x][y] == True: ...
    """
    return self.data.food

  def getWalls(self):
    """
    Returns a Grid of boolean wall indicator variables.

    Grids can be accessed via list notation, so to check
    if there is a wall at (x,y), just call

    walls = state.getWalls()
    if walls[x][y] == True: ...
    """
    return self.data.layout.walls

  def hasFood(self, x, y):
    return self.data.food[x][y]

  def hasWall(self, x, y):
    return self.data.layout.walls[x][y]

  def isLose( self ):
    return self.data._lose

  def isWin( self ):
    return self.data._win

  #############################################
  #             Helper methods:               #
  # You shouldn't need to call these directly #
  #############################################

  def __init__( self, prevState = None ):
    """
    Generates a new state by copying information from its predecessor.
    """
    if prevState is not None: # Initial state
      self.data = GameStateData(prevState.data)
    else:
      self.data = GameStateData()

  def deepCopy( self ):
    state = GameState( self )
    state.data = self.data.deepCopy()
    return state

  def __eq__( self, other ):
    """
    Allows two states to be compared.
    """
    if other is None: return False
    return self.data == other.data

  def __hash__( self ):
    """
    Allows states to be keys of dictionaries.
    """
    return hash( self.data )

  def __str__( self ):

    return str(self.data)

  def initialize( self, layout, numGhostAgents=1000 ):
    """
    Creates an initial game state from a layout array (see layout.py).
    """
    self.data.initialize(layout, numGhostAgents)

############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

SCARED_TIME = 20    # Moves ghosts are scared
COLLISION_TOLERANCE = 1 # How close ghosts must be to Pacman to kill
# TIME_PENALTY = 1 # Number of points lost each round

class ClassicGameRules:
  """
  These game rules manage the control flow of a game, deciding when
  and how the game starts and ends.
  """
  def __init__(self, timeout=30):
    self.timeout = timeout

  def newGame( self, layout, pacmanAgent,pacmanAgent2, ghostAgents, display, quiet = False, catchExceptions=False):
    # agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
    agents = [pacmanAgent,pacmanAgent2]
    initState = GameState()
    initState.initialize( layout, len(ghostAgents) )
    game = Game(agents, display, self, catchExceptions=catchExceptions)
    game.state = initState
    self.initialState = initState.deepCopy()
    self.quiet = quiet
    return game

  def getProgress(self, game):
    return float(game.state.getNumFood()) / self.initialState.getNumFood()

  def agentCrash(self, game, agentIndex):
    self.agentIndexCrash = agentIndex

  def getAgentCrash(self):
    return self.agentIndexCrash

  def getMaxTotalTime(self, agentIndex):
    return self.timeout

  def getMaxStartupTime(self, agentIndex):
    return self.timeout

  def getMoveWarningTime(self, agentIndex):
    return self.timeout

  def getMoveTimeout(self, agentIndex):
    return self.timeout

  def getMaxTimeWarnings(self, agentIndex):
    return 0

class PacmanRules:
  """
  These functions govern how pacman interacts with his environment under
  the classic game rules.
  """
  PACMAN_SPEED=1

  def getLegalActions( state,agentIndex=0 ):
    """
    Returns a list of possible actions.
    """

    possibleActions = Actions.getPossibleActions( state.getPacmanState(agentIndex).configuration, state.data.layout.walls )
    if Directions.STOP in possibleActions:
      possibleActions.remove( Directions.STOP )
    return possibleActions
  getLegalActions = staticmethod( getLegalActions )

  def applyAction( state, action, agentIndex=0 ):
    """
    Edits the state to reflect the results of the action.
    """
    # print("action: ",action, " agentIndex: ",agentIndex)
    legal = PacmanRules.getLegalActions( state ,agentIndex)
    if action not in legal:
      raise Exception("Illegal action " + str(action))

    pacmanState = state.data.agentStates[agentIndex]

    # Update Configuration
    vector = Actions.directionToVector( action, PacmanRules.PACMAN_SPEED )
    pacmanState.configuration = pacmanState.configuration.generateSuccessor( vector )

    # Eat
    next = pacmanState.configuration.getPosition()
    nearest = nearestPoint( next )
    if manhattanDistance( nearest, next ) <= 0.5 :
      # Remove food
      PacmanRules.consume( nearest, state ,agentIndex)
  applyAction = staticmethod( applyAction )

  def decrementTimer( state):
    timer = state.scaredTimer
    # print("timer: ",timer)
    if timer == 1:
      state.configuration.pos = nearestPoint( state.configuration.pos )
    state.scaredTimer = max( 0, timer - 1 )
  decrementTimer = staticmethod( decrementTimer )

  def consume( position, state,agentIndex=0 ):
    x,y = position
    # Eat food
    if state.data.food[x][y]:
      state.data.scoreChange[agentIndex] += 10
      state.data.food = state.data.food.copy()
      state.data.food[x][y] = False
      state.data._foodEaten = position
    
    # Eat capsule
    if( position in state.getCapsules() ):
      state.data.capsules.remove( position )
      state.data._capsuleEaten = position
      index = (agentIndex+1)%2
      state.data.agentStates[index].scaredTimer = SCARED_TIME
  consume = staticmethod( consume )

  def collide( state, agentIndex, pacman2,pacman2Index):
    if pacman2.scaredTimer > 0:
      score = 0.5*state.data.score[pacman2Index]
      state.data.scoreChange[agentIndex] += score
      state.data.score[pacman2Index] = score
      # เพื่อไม่ให้ pacman อีกตัว ได้คะแนนเพิ่มเยอะเกินไป
      pacman2.scaredTimer = 0
  collide = staticmethod( collide )

  def checkSteal( state, agentIndex):
    pacmanPosition = state.getPacmanPosition(agentIndex)
    pacman2Index = (agentIndex+1)%2
    pacman2 = state.getPacmanState(pacman2Index)
    pacman2Position = state.getPacmanPosition(pacman2Index)
    if PacmanRules.canSteal( pacmanPosition, pacman2Position ):
      PacmanRules.collide( state,agentIndex, pacman2, pacman2Index )
  checkSteal = staticmethod( checkSteal )

  def canSteal( pacmanPosition, ghostPosition ):
    # print("canSteal",(pacmanPosition, ghostPosition),manhattanDistance( ghostPosition, pacmanPosition ))
    return manhattanDistance( ghostPosition, pacmanPosition ) <= COLLISION_TOLERANCE
  canSteal = staticmethod( canSteal )


def loadAgent(pacman, nographics):
  # Looks through all pythonPath Directories for the right module,
  pythonPathStr = os.path.expandvars("$PYTHONPATH")
  if pythonPathStr.find(';') == -1:
    pythonPathDirs = pythonPathStr.split(':')
  else:
    pythonPathDirs = pythonPathStr.split(';')
  pythonPathDirs.append('.')

  for moduleDir in pythonPathDirs:
    if not os.path.isdir(moduleDir): continue
    moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py') or f=='submission.py']
    for modulename in moduleNames:
      try:
        module = __import__(modulename[:-3])
      except ImportError:
        continue
      if pacman in dir(module):
        if nographics and modulename == 'keyboardAgents.py':
          raise Exception('Using the keyboard requires graphics (not text display)')
        return getattr(module, pacman)
  raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')

def printResults(numGames, games, display, rules ):
  scores = [game.state.getScores() for game in games]
  winners = [checkWinner(games[i],rules[i]) for i in range(numGames)]
  print('**** Summary: *****')
  print('Scores: ', scores)
  print('Winners: ', winners)
    

def checkWinner(game, rule):
  winner = None
  if game.agentTimeout:
    print('Agent timed out')
    print('agentTimeout:', rule.getAgentCrash())
    if rule.getAgentCrash() == 0:
      print("Pacman 2 win")
      winner = 2
    else:
      print("Pacman 1 win")
      winner = 1
  else:
    scores = game.state.getScores()
    print('Score: ', scores)
    if scores[0] > scores[1]:
      print("Pacman 1 win")
      winner = 1
    elif scores[0] < scores[1]:
      print("Pacman 2 win")
      winner = 2
    else:
      time_score = game.totalAgentTimes
      if time_score[0] > time_score[1]:
        print("Pacman 2 win")
        winner = 2
      elif time_score[0] < time_score[1]:
        print("Pacman 1 win")
        winner = 1
      else:
        print("Draw")
  return winner

############################################
# หลังจากบรรทัดนี้ สามารถแก้ code ได้ 
#  เปลี่ยน setting ต่างๆได้
############################################
def setArgs():
  args = dict()
  # Choose a layout
  layout1 = "open310"
  # layout1 = "mediumClassic"
  # layout1 = "testClassic"
  args['layout'] = layout.getLayout(layout1 )
  zoom = 1.0
  # ความเร็วในการเคลื่อนที่ของ pacman สามารถกำหนดได้ โดยค่ามากขึ้น จะช้าลง
  frameTime = 0.1
  args['display'] = graphicsDisplay.PacmanGraphics(zoom, frameTime = frameTime)

  # Choose a Pacman agent 1
  # MinimaxAgent
  noKeyboard = False
  # yellow pacman
  # pacmanType = loadAgent("MinimaxAgent", noKeyboard)
  
  pacmanType = loadAgent("KeyboardAgent", False)
  
  # สามารถแก้เป็น agent ของทีมตัวเองได้
  #pacmanType = loadAgent("YourTeamAgent", False)

  agentOpts = {}
  pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
  args['pacman'] = pacman

  # Choose a Pacman agent 2
  # orange pacman
  noKeyboard = False
  pacmanType = loadAgent("ReflexAgent", noKeyboard)

  # สามารถแก้เป็น agent ของทีมตัวเองได้
  #pacmanType = loadAgent("YourTeamAgent", False)

  agentOpts = {}
  pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
  args['pacman2'] = pacman

  args['numGames'] = 1
  args['catchExceptions'] = False
  # เวลาที่ให้ agent คิด หน่วยเป็นวินาที
  args['timeout'] = 20
  # ระยะเวลาที่ให้เล่นเกม หน่วยเป็นวินาที
  args['game_time'] = 90
  return args

def runGames( layout, pacman,pacman2, display, numGames, catchExceptions=False, timeout=30,game_time = 90 ):
  import __main__
  __main__.__dict__['_display'] = display

  games = []
  rules = []
  for i in range(numGames):
    ## Timeout in seconds for total movement, 
    rule = ClassicGameRules(timeout)
    rules.append(rule)
    gameDisplay = display
    rule.quiet = False
    game = rule.newGame( layout, pacman,pacman2, [], gameDisplay, False, catchExceptions)
    game.run(game_time)
    games.append(game)

  printResults(numGames, games, display, rules)
  

if __name__ == '__main__':
  
  args = setArgs() # Get game components based on input
  runGames(**args )

