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
               first = 'IntelligentAgent', second = 'IntelligentAgent'):
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

  global gameStrategy 
  gameStrategy = Strategy(firstIndex,secondIndex,isRed)

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########


class Strategy:
  
  firstIndex = 0
  agentMode = ['','','','']
  secondIndex = 2
  isRed = True

  def __init__(self, firstIndex, secondIndex, isRed):
    self.firstIndex = firstIndex
    self.secondIndex = secondIndex
    self.isRed = isRed
    self.agentMode[firstIndex] = 'attack'
    self.agentMode[secondIndex] = 'defence'

class IntelligentAgent(CaptureAgent):

  def registerInitialState(self, gameState): #initial


    CaptureAgent.registerInitialState(self, gameState)
    
    self.wall = gameState.getWalls()
    self.h = gameState.data.layout.height
    self.w = gameState.data.layout.width
    self.isRed = self.red


    # 지켜야 할 지점.
    # 모든 지점에, 아군 Agent가 먼저 도달할 수 있도록 배치해야 한다.
    self.savingPoint = self.getCapsulesYouAreDefending(gameState)
    if self.isRed:
      x = (int)(self.w/2)-1
    else:
      x = (int)(self.w/2)
    
    for y in range(self.h):
      if not self.wall[x][y]:
        self.savingPoint.append((x,y))
      

  def chooseAction(self, gameState):

    #get state
    self.updateSafeArea(gameState)

    #언제나 상대 agent를 죽이는 것이 가장 좋음
    if self.canKill(gameState) != None:
      return self.canKill(gameState)

    #게임이 끝날때까지 시간이 얼마 남지 않는다면 돌아옴
    if ((self.isRed and gameState.getAgentPosition(self.index)[0]>=self.w/2) or (not self.isRed and gameState.getAgentPosition(self.index)[0]<self.w/2)) and gameState.data.timeleft <= self.timeBackHome(gameState)*4+20:
      return self.comeBackHome(gameState)


    #그 외의 경우. 임무에 맞게 행동함
    if gameStrategy.agentMode[self.index] == 'defence':
      return self.letsGuard(gameState)
    else:
      return self.letsAttack(gameState)


  # x기본
  # 우선 공격 1, 방어 1로 두고
  # 위급한 상황에서 공격을 방어로, 공격 타이밍에 방어를 공격으로 교체한다.

  # 방어
  # 상대방이 어떤 곳에 가까워지고 있는지 계산한다.
  # 해당 위치에 먼저 도달할 수 있도록 이동.
  # 만약 모든 위치에 대해서 안전한 거리 내에 있다면, 공격하는 방향으로 조금 이동한다.
  # 만약 안전하지 않은 경우가 생겼다면, 공격하는 Agent를 수비하도록 만든다.

  # 처음에는 0이 공격, 2가 방어이다.
  # 만약 방어하는 Agent가 도움이 필요하다면, 자기 자신이 아닌 다른 Agent를 방어하도록 만든다. Strategy 이용.
  # 만약 자기 자신만으로도 충분하다면, 자기 자신이 아닌 다른 Agent를 공격으로 전환시킨다.

  # 공격

  # SafeBFSAgent와 마찬가지로, 안전한 위치에 대해서만 이동해본다.


  #상대 agent를 죽일 수 있는가?
  def canKill(self, gameState):
    posAg = gameState.getAgentPosition(self.index)

    for op in self.getOpponents(gameState):
      posOp = gameState.getAgentPosition(op)
      if gameState.data.agentStates[op].scaredTimer>0:
          if posAg[0] + 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.EAST
          elif posAg[1] + 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.NORTH
          elif posAg[0] - 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.WEST
          elif posAg[1] - 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.SOUTH
      elif self.isRed:
        if self.getMazeDistance(posAg, posOp) == 1:
          if posAg[0]+1 <self.w/2 and posAg[0] + 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.EAST
          elif posAg[0] <self.w/2 and posAg[1] + 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.NORTH
          elif posAg[0] - 1 <self.w/2 and posAg[0] - 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.WEST
          elif posAg[0] <self.w/2 and posAg[1] - 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.SOUTH
      else:
        if self.getMazeDistance(posAg, posOp) == 1:
          if posAg[0]+1 >=self.w/2 and posAg[0] + 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.EAST
          elif posAg[0] >=self.w/2 and posAg[1] + 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.NORTH
          elif posAg[0] - 1 >=self.w/2 and posAg[0] - 1 == posOp[0] and posAg[1] == posOp[1]:
            return Directions.WEST
          elif posAg[0] >=self.w/2 and posAg[1] - 1 == posOp[1] and posAg[0] == posOp[0]:
            return Directions.SOUTH


    
    return None


 
  # 혼자 defnece 중일때.
  def evaluate1(self, gameState):
    opponents = self.getOpponents(gameState)
    posAg = gameState.getAgentPosition(self.index)
      
    ret = 1000000
    sum = 0
    
    for (p,q) in self.savingPoint:
      for op in opponents:
        posOp = gameState.getAgentPosition(op)
        dis1 = self.getMazeDistance(posAg, (p,q))
        dis2 = self.getMazeDistance(posOp, (p,q))
        if (p,q) in self.getCapsulesYouAreDefending(gameState):
          dis2 -= 1

        # 내가 얼마나 더 빨리 도착할 수 있는가?
        tmp = dis2 - dis1

        sum += tmp

        if tmp < ret:
          ret = tmp

    return (ret, sum, sum)
    
    # 최솟값을 최대화시키자!!!

  def evaluate2(self, gameState):
    opponents = self.getOpponents(gameState)
    team = self.getTeam(gameState)[0] + self.getTeam(gameState)[1] - self.index
    posAg = gameState.getAgentPosition(self.index)
    posTm = gameState.getAgentPosition(team)

    ret = 1000000
    sum1 = 0 # 전체 savingpoint들에 대한 팀 최적 distance 차이 합

    sum2 = 0 # 전체 savingpoint들에 대한 현재 Agent distance 차이 합
    
    for (p,q) in self.savingPoint:
      for op in opponents:
        posOp = gameState.getAgentPosition(op)
        dis1 = self.getMazeDistance(posAg, (p,q))
        dis2 = self.getMazeDistance(posTm, (p,q))
        dis3 = self.getMazeDistance(posOp, (p,q))

        if (p,q) in self.getCapsulesYouAreDefending(gameState):
          dis3 -= 1

        # 둘 중 내가 더 먼저 도착할 수 있는 곳
        tmp = min(dis1, dis2)
        
        # 상대방보다 얼마나 빨리 도착할 수 있는가?
        tmp = dis3 - tmp

        sum1 += tmp
        sum2 += dis3 - dis1


        if tmp < ret:
          ret = tmp
    return (ret, sum1, sum2)
    
  def maxPlayer(self, gameState, agentIndex, depth, alpha, beta):
    maxi = (-10000000, 0, 0)
    ret = None

    if depth == 0:
      if gameStrategy.agentMode[(0 if self.isRed else 1)] == 'defence' and gameStrategy.agentMode[(2 if self.isRed else 3)] == 'defence':
        return (self.evaluate2(gameState), None)
      else:
        return (self.evaluate1(gameState), None)
    

    if gameStrategy.agentMode[agentIndex] == 'attack':
      return (self.minPlayer(gameState, (agentIndex + 1)%4, depth-1, alpha, beta), None)

    legalAction = gameState.getLegalActions(agentIndex)

    for action in legalAction:
      successor = gameState.generateSuccessor(agentIndex, action)
    
      tmp = self.minPlayer(successor, (agentIndex + 1)%4, depth-1, alpha, beta)

      if tmp>maxi:
        maxi = tmp
        ret = (maxi, action)
      if maxi >= beta:
        return ((10000000,0,0), action)
      if maxi < alpha:
        alpha = maxi
    
    return ret

  def minPlayer(self, gameState, agentIndex, depth, alpha, beta):
    mini = (10000000,0,0)
    ret = None

    legalAction = gameState.getLegalActions(agentIndex)

    for action in legalAction:
      successor = gameState.generateSuccessor(agentIndex, action)
 
      (tmp, _) = self.maxPlayer(successor, (agentIndex + 1)%4, depth-1, alpha, beta)

      if tmp < mini:
        mini = tmp
      if mini <= alpha:
        return mini - 1
      if beta > mini:
        beta = mini
    return mini
                          
        
  def letsGuard(self, gameState): 
    team = self.getTeam(gameState)[0] + self.getTeam(gameState)[1] - self.index
    gameStrategy.agentMode[team] = 'attack'
    (score, action) = self.maxPlayer(gameState, self.index, 4, (-10000000,0,0), (10000000,0,0))
    if score[0] <=0: # o or 1
      gameStrategy.agentMode[team] = 'defence'

      #여기서만 깊이를 늘려볼까
      (score, action) = self.maxPlayer(gameState, self.index, 4, (-10000000,0,0), (10000000,0,0))
    
      #여기서도 score가 낮다면? 차라리 공격에 올인할까?

    return action
        

  def letsAttack(self, gameState):


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

    return self.comeBackHome(gameState)  
 

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
    

  # capsure 상태 체크
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

  def gotoPosKill(self, gameState, pos):
    
    (x, y) = gameState.getAgentPosition(self.index)
    distance = self.getMazeDistance((x, y) , pos)
    maxval = 100000
    ret = Directions.STOP
    if x+1<self.w:
      if not self.wall[x+1][y]:
        tmp = self.getMazeDistance((x+1, y),pos)
        if tmp < distance:
          if maxval < self.SafeArea[x+1][y]:
            ret = Directions.EAST
    if y+1<self.h:
      if not self.wall[x][y+1]:
        tmp = self.getMazeDistance((x, y+1),pos)
        if tmp < distance:
          if maxval < self.SafeArea[x][y+1]:
            ret = Directions.NORTH
    if x-1>=0:
      if not self.wall[x-1][y]:
        tmp = self.getMazeDistance((x-1, y),pos)
        if tmp < distance:
          if maxval < self.SafeArea[x-1][y]:
            ret = Directions.WEST
    if y-1>=0:
      if not self.wall[x][y-1]:
        tmp = self.getMazeDistance((x, y-1),pos)
        if tmp < distance:
          if maxval < self.SafeArea[x][y-1]:
            ret = Directions.SOUTH

    return ret

  def gotoPosList(self, gameState, pos):
    
    (x, y) = gameState.getAgentPosition(self.index)
    distance = self.getMazeDistance((x, y) , pos)
    minval = 100000
    ret = []
    if x+1<self.w:
      if not self.wall[x+1][y]:
        tmp = self.getMazeDistance((x+1, y),pos)
        if tmp < distance:
          ret.append(Directions.EAST)
    if y+1<self.h:
      if not self.wall[x][y+1]:
        tmp = self.getMazeDistance((x, y+1),pos)
        if tmp < distance:
          ret.append(Directions.NORTH)
    if x-1>=0:
      if not self.wall[x-1][y]:
        tmp = self.getMazeDistance((x-1, y),pos)
        if tmp < distance:
          ret.append(Directions.WEST)
    if y-1>=0:
      if not self.wall[x][y-1]:
        tmp = self.getMazeDistance((x, y-1),pos)
        if tmp < distance:
          ret.append(Directions.SOUTH)

    if len(ret) == 0:
      ret.append(Directions.STOP)
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
    
    if gameState.data.agentStates[op[0]].scaredTimer <= self.timeBackHome(gameState):
      queue1.append(op1)
      bfs[op1[0]][op1[1]] = -1
    
    if gameState.data.agentStates[op[1]].scaredTimer <= self.timeBackHome(gameState):
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

