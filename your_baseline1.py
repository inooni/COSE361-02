# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'SimpleBFSAttackAgent', second = 'SimpleBFSAttackAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########



class SimpleBFSAttackAgent(CaptureAgent):

  def registerInitialState(self, gameState): #initial


    CaptureAgent.registerInitialState(self, gameState)
    
    self.wall = gameState.getWalls()
    self.h = gameState.data.layout.height
    self.w = gameState.data.layout.width
    self.isRed = self.red
    
  def chooseAction(self, gameState):

    #get state
    self.updateSafeArea(gameState)

    #게임이 끝날때까지 시간이 얼마 남지 않는다면 돌아옴
    if ((self.isRed and gameState.getAgentPosition(self.index)[0]>=self.w/2) or (not self.isRed and gameState.getAgentPosition(self.index)[0]<self.w/2)) and gameState.data.timeleft <= self.timeBackHome(gameState)*4+20:
      return self.comeBackHome(gameState)


    foodMap = self.getFood(gameState)

    select = (-1, -1)
    mindis = 1000000

    now = gameState.getAgentPosition(self.index)

    #안전하게 갈 수 있는 food or capsure(확실하게 우리 진영으로 돌아올 수 있는) 중에서 가장 가까운 곳
    for y in range(self.h):
      for x in range(self.w):
        if (foodMap[x][y] or ((x,y) in self.getCapsules(gameState))) and self.SafeArea[x][y]<0:
          if self.canEscape(gameState, (x,y)):
            dis = self.getMazeDistance(now, (x,y))
            if dis < mindis:
              mindis = dis
              select = (x,y)
    
    #존재하는경우
    if select != (-1, -1):
      return self.gotoPos(gameState, select)

    opponents = self.getOpponents(gameState)

    #both two opponent are other side
    if self.isRed and gameState.getAgentPosition(opponents[0])[0]>=self.w/2 and gameState.getAgentPosition(opponents[1])[0]>=self.w/2:
      for y in range(self.h):
        for x in range((int)(self.w/2), self.w): # make this shortest
          if self.SafeArea[x][y]<0:
            if self.canEscape(gameState, (x,y)):
              dis = self.getMazeDistance(now, (x,y))
              if dis < mindis:
                mindis = dis
                select = (x,y)
              elif dis == mindis:
                if select[0]<x:
                  select = (x,y)
      if select != (-1, -1):
        return self.gotoPosSafe(gameState, select)  
    elif not self.isRed and gameState.getAgentPosition(opponents[0])[0]<self.w/2 and gameState.getAgentPosition(opponents[1])[0]<self.w/2:
      for y in range(self.h):
        for x in range(1, (int)(self.w/2)): # make this shortest
          if self.SafeArea[x][y]<0:
            if self.canEscape(gameState, (x,y)):
              dis = self.getMazeDistance(now, (x,y))
              if dis < mindis:
                mindis = dis
                select = (x,y)
              elif dis == mindis:
                if select[0]>x:
                  select = (x,y)
      if select != (-1, -1):
        return self.gotoPosSafe(gameState, select)  

      
    #집에 오거나, 집을 지킴
    # 집 지킬때 상대방 영역 갈 수도 있음. 근데 그러면 집에 오라도 한다.
    # 집에 오라는 명령을 버려야하나?
    if self.isRed:
      if now[0]<self.w/2:
        return self.justGuard(gameState)
      else:
        return self.comeBackHome(gameState)
    else:
      if now[0]>=self.w/2:
        return self.justGuard(gameState)
      else:
        return self.comeBackHome(gameState)  

  def justGuard(self, gameState): ##lets consider it using bfs on every unit


    if self.isRed:
      x = (int)(self.w/2) - 1
    else:
      x = (int)(self.w/2)
    maxval = -10000000
   
    
    for enemy in self.getOpponents(gameState):  
      for y in range(self.h):
        if self.wall[x][y] == 1:
          continue
        tmp = self.SafeArea[x][y]
        #change strange
        if maxval < tmp:
          ret = (x,y)
          maxval = tmp
      if gameState.getAgentPosition(enemy)[0]<self.w/2:
        return self.gotoPosSafe(gameState, ret)

    return self.gotoPosSafe(gameState, ret) #we cant catch find other way

  def comeBackHome(self, gameState):
    if self.isRed:
      x = (int)(self.w/2) - 1
    else:
      x = (int)(self.w/2)
    minval = 1000000
    ret = (-1, -1)

    #안전한 경로중 가장 가까운 곳으로 돌아온다.

    for y in range(self.h):
      if not self.wall[x][y]:
        if self.SafeArea[x][y]<0: #capsure
          tmp = self.getMazeDistance((x,y), gameState.getAgentPosition(self.index))
          if minval > tmp:
            ret = (x,y)
            minval = tmp
    if ret != (-1, -1):
      return self.gotoPosSafe(gameState, ret)

    #가장 가까운 곳으로 가는 것을 시도한다.

    for y in range(self.h):
      if not self.wall[x][y]:
        tmp = self.getMazeDistance((x,y), gameState.getAgentPosition(self.index))
        if minval > tmp:
          ret = (x,y)
          minval = tmp
    return self.gotoPosSafe(gameState, ret)

  def timeBackHome(self, gameState):
    if self.isRed:
      x = (int)(self.w/2) - 1
    else:
      x = (int)(self.w/2)
    minval = 1000000
    ret = (-1, -1)

    #안전한 경로중 가장 가까운 곳까지의 거리를 가져온다.

    for y in range(self.h):
      if not self.wall[x][y]:
        if self.SafeArea[x][y]<0: #capsure
          tmp = self.getMazeDistance((x,y), gameState.getAgentPosition(self.index))
          if minval > tmp:
            ret = (x,y)
            minval = tmp
    if ret != (-1, -1):
      return minval

    #가장 가까운 곳까지의 거리를 가져온다.

    for y in range(self.h):
      if not self.wall[x][y]:
        tmp = self.getMazeDistance((x,y), gameState.getAgentPosition(self.index))
        if minval > tmp:
          ret = (x,y)
          minval = tmp
    return minval
  
  def canEscape(self, gameState, pos): # if Agent go to pos, can agent Escape? (go to team area or eat capsule)
    
    bfs = [[0 for y in range(self.h)] for x in range(self.w)]
    
    distance = self.getMazeDistance(gameState.getAgentPosition(self.index), pos)

    if distance == 0:
      distance = 1

    #initial table
    for y in range(gameState.data.layout.height):
      for x in range(gameState.data.layout.width):
        if self.wall[x][y]:
          bfs[x][y] = -2
    
    #initial queue
    #queue1: opponent
    #queue2: agent
    queue1 = []

    op = self.getOpponents(gameState)
    op1 = gameState.getAgentPosition(op[0])
    op2 = gameState.getAgentPosition(op[1])
    
    if gameState.data.agentStates[op[0]].scaredTimer <= distance + self.timeBackHome(gameState):
      queue1.append(op1)
      bfs[op1[0]][op1[1]] = -1
    
    if gameState.data.agentStates[op[1]].scaredTimer <= distance + self.timeBackHome(gameState):
      queue1.append(op2)
      bfs[op2[0]][op2[1]] = -1
    
    queue2 = [pos]
    bfs[pos[0]][pos[1]] = 1

    #agent spend time to reach pos
    for i in range(distance):
      tmp = []
      for (x, y) in queue1:
        if x+1<self.w:
          if bfs[x+1][y] == 0 or (bfs[x+1][y] == 1 and ((x+1>=self.w/2 and self.isRed) or (x+1<self.w/2 and not self.isRed))):
            bfs[x+1][y] = -1
            tmp.append((x+1, y))
        if y+1<self.h:
          if bfs[x][y+1] == 0 or (bfs[x][y+1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y+1] = bfs[x][y]
            tmp.append((x, y+1))
        if x-1>=0:
          if bfs[x-1][y] == 0 or (bfs[x-1][y] == 1 and ((x-1>=self.w/2 and self.isRed) or (x-1<self.w/2 and not self.isRed))):
            bfs[x-1][y] = -1
            tmp.append((x-1, y))
        if y-1>=0:
          if bfs[x][y-1] == 0 or (bfs[x][y-1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y-1] = -1
            tmp.append((x, y-1))
      queue1 = tmp

    if bfs[pos[0]][pos[1]] == -1:
      return False
    else:
      capsures = self.getCapsules(gameState)
      if pos in capsures:
        return True
    
    #calculate all posible opponent move, and then calculate all posible agent move
    while len(queue2) != 0:
      tmp = []
      for (x, y) in queue1:
        if x+1<self.w:
          if bfs[x+1][y] == 0 or (bfs[x+1][y] == 1 and ((x+1>=self.w/2 and self.isRed) or (x+1<self.w/2 and not self.isRed))):
            bfs[x+1][y] = -1
            tmp.append((x+1, y))
        if y+1<self.h:
          if bfs[x][y+1] == 0 or (bfs[x][y+1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y+1] = bfs[x][y]
            tmp.append((x, y+1))
        if x-1>=0:
          if bfs[x-1][y] == 0 or (bfs[x-1][y] == 1 and ((x-1>=self.w/2 and self.isRed) or (x-1<self.w/2 and not self.isRed))):
            bfs[x-1][y] = -1
            tmp.append((x-1, y))
        if y-1>=0:
          if bfs[x][y-1] == 0 or (bfs[x][y-1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y-1] = -1
            tmp.append((x, y-1))
      queue1 = tmp

      tmp = []
      for (x, y) in queue2:
        if bfs[x][y] == -1:
          continue
        if (self.isRed and x < self.w/2) or (not self.isRed and x>=self.w/2):
          return True
        if x+1<self.w:
          if bfs[x+1][y] == 0 or (bfs[x+1][y] == -1 and ((x+1>=self.w/2 and not self.isRed) or (x+1<self.w/2 and self.isRed))):
            bfs[x+1][y] = 1
            tmp.append((x+1, y))
        if y+1<self.h:
          if bfs[x][y+1] == 0 or (bfs[x][y+1] == -1 and ((x>=self.w/2 and not self.isRed) or (x<self.w/2 and self.isRed))):
            bfs[x][y+1] = 1
            tmp.append((x, y+1))
        if x-1>=0:
          if bfs[x-1][y] == 0 or (bfs[x-1][y] == -1 and ((x-1>=self.w/2 and not self.isRed) or (x-1<self.w/2 and self.isRed))):
            bfs[x-1][y] = 1
            tmp.append((x-1, y))
        if y-1>=0:
          if bfs[x][y-1] == 0 or (bfs[x][y-1] == -1 and ((x>=self.w/2 and not self.isRed) or (x<self.w/2 and self.isRed))):
            bfs[x][y-1] = 1
            tmp.append((x, y-1))
      queue2 = tmp

    return False
    
  # it is not safe  
  def gotoPos(self, gameState, pos):
    
    (x, y) = gameState.getAgentPosition(self.index)
    distance = self.getMazeDistance((x, y) , pos)
    minval = 100000
    ret = Directions.STOP
    if x+1<self.w:
      if not self.wall[x+1][y]:
        tmp = self.getMazeDistance((x+1, y),pos)
        if tmp < distance:
          if minval > self.SafeArea[x+1][y]:
            ret = Directions.EAST
    if y+1<self.h:
      if not self.wall[x][y+1]:
        tmp = self.getMazeDistance((x, y+1),pos)
        if tmp < distance:
          if minval > self.SafeArea[x][y+1]:
            ret = Directions.NORTH
    if x-1>=0:
      if not self.wall[x-1][y]:
        tmp = self.getMazeDistance((x-1, y),pos)
        if tmp < distance:
          if minval > self.SafeArea[x-1][y]:
            ret = Directions.WEST
    if y-1>=0:
      if not self.wall[x][y-1]:
        tmp = self.getMazeDistance((x, y-1),pos)
        if tmp < distance:
          if minval > self.SafeArea[x][y-1]:
            ret = Directions.SOUTH

    return ret
    

  #안전하게 이동
  def gotoPosSafe(self, gameState, pos):

    bfs = [[0 for y in range(self.h)] for x in range(self.w)]
    backtrack = [[-1 for y in range(self.h)] for x in range(self.w)]
    for y in range(self.h):
      for x in range(self.w):
        if self.wall[x][y]:
          bfs[x][y] = -2


    queue1 = []

    op = self.getOpponents(gameState)
    op1 = gameState.getAgentPosition(op[0])
    op2 = gameState.getAgentPosition(op[1])
    
    if gameState.data.agentStates[op[0]].scaredTimer <=self.timeBackHome(gameState):
      queue1.append(op1)
      bfs[op1[0]][op1[1]] = -1
    
    if gameState.data.agentStates[op[1]].scaredTimer <=self.timeBackHome(gameState):
      queue1.append(op2)
      bfs[op2[0]][op2[1]] = -1
    
    now = gameState.getAgentPosition(self.index)
    queue2 = [now]
    bfs[now[0]][now[1]] = 1

    #-2: opponent pacman
    #-1: opponent ghost
    #1: our pacman and ghost

    while len(queue2) != 0:
      tmp = []
      for (x, y) in queue1:
        if x+1<self.w:
          if bfs[x+1][y] == 0 or (bfs[x+1][y] == 1 and ((x+1>=self.w/2 and self.isRed) or (x+1<self.w/2 and not self.isRed))):
            bfs[x+1][y] = -1
            tmp.append((x+1, y))
        if y+1<self.h:
          if bfs[x][y+1] == 0 or (bfs[x][y+1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y+1] = -1
            tmp.append((x, y+1))
        if x-1>=0:
          if bfs[x-1][y] == 0 or (bfs[x-1][y] == 1 and ((x-1>=self.w/2 and self.isRed) or (x-1<self.w/2 and not self.isRed))):
            bfs[x-1][y] = -1
            tmp.append((x-1, y))
        if y-1>=0:
          if bfs[x][y-1] == 0 or (bfs[x][y-1] == 1 and ((x>=self.w/2 and self.isRed) or (x<self.w/2 and not self.isRed))):
            bfs[x][y-1] = -1
            tmp.append((x, y-1))
      queue1 = tmp
      
      tmp = []
      for (x, y) in queue2:
        if bfs[x][y] == -1:
          continue
        if((x,y) == pos):
          ret = 0
          while backtrack[x][y] != -1:
            ret = backtrack[x][y]
            if backtrack[x][y] == 1:
              (x,y) = (x-1, y)
            elif backtrack[x][y] == 2:
              (x,y) = (x, y-1)
            elif backtrack[x][y] == 3:
              (x,y) = (x+1, y)
            elif backtrack[x][y] == 4:
              (x,y) = (x, y+1)
          if ret == 1:
            return Directions.EAST
          elif ret == 2:
            return Directions.NORTH
          elif ret == 3:
            return Directions.WEST
          elif ret == 4:
            return Directions.SOUTH
          else:
            return Directions.STOP

        if x+1<self.w:
          if bfs[x+1][y] == 0 or (bfs[x+1][y] == -1 and ((x+1>=self.w/2 and not self.isRed) or (x+1<self.w/2 and self.isRed))):
            bfs[x+1][y] = 1
            backtrack[x+1][y] = 1
            tmp.append((x+1, y))
        if y+1<self.h:
          if bfs[x][y+1] == 0 or (bfs[x][y+1] == -1 and ((x>=self.w/2 and not self.isRed) or (x<self.w/2 and self.isRed))):
            bfs[x][y+1] = 1
            backtrack[x][y+1] = 2
            tmp.append((x, y+1))
        if x-1>=0:
          if bfs[x-1][y] == 0 or (bfs[x-1][y] == -1 and ((x-1>=self.w/2 and not self.isRed) or (x-1<self.w/2 and self.isRed))):
            bfs[x-1][y] = 1
            backtrack[x-1][y] = 3
            tmp.append((x-1, y))
        if y-1>=0:
          if bfs[x][y-1] == 0 or (bfs[x][y-1] == -1 and ((x>=self.w/2 and not self.isRed) or (x<self.w/2 and self.isRed))):
            bfs[x][y-1] = 1
            backtrack[x][y-1] = 4
            tmp.append((x, y-1))
      queue2 = tmp

    return self.gotoPos(gameState,pos)


  def updateSafeArea(self, gameState):  #SafeArea: all position which agent can go faster than two ghost. it is only meanful for x>=self.w/2-1
    self.SafeArea = [[0 for y in range(self.h)] for x in range(self.w)]
    for y in range(self.h):
      for x in range(self.w):
        
        if self.wall[x][y]:
          self.SafeArea[x][y] = 100000
          continue

        enemy = self.getOpponents(gameState)
        tmp0 = self.getMazeDistance(gameState.getAgentPosition(self.index), (x, y)) - self.getMazeDistance(gameState.getAgentPosition(enemy[0]), (x, y))
        if self.getMazeDistance(gameState.getAgentPosition(self.index), (x, y))<=gameState.data.agentStates[enemy[0]].scaredTimer:
          tmp0 = -100000
        tmp1 = self.getMazeDistance(gameState.getAgentPosition(self.index), (x, y)) - self.getMazeDistance(gameState.getAgentPosition(enemy[1]), (x, y))
        if self.getMazeDistance(gameState.getAgentPosition(self.index), (x, y))<=gameState.data.agentStates[enemy[1]].scaredTimer:
          tmp1 = -100000
        self.SafeArea[x][y] = max(tmp0, tmp1)
        
    #for debug. show SafeArea
    '''
    List = []
    for y in range(self.h):
      for x in range(self.w):
        if self.SafeArea[x][y] < 0:
          List.append((x,y))
    self.debugDraw(List, (1,0,0),True)
    '''

