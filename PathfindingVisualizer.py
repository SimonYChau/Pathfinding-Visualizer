import pygame
import sys
from queue import PriorityQueue
from tkinter import *
from tkinter import messagebox
import math

DISPLAY_SIZE = 1000
NUMBER_OF_ROWS = 50
START_COLOUR = (255,0,255)
END_COLOUR = (199,21,133)
VISITED = (39, 174, 96)
VISITING = (39, 174, 96)
DEFAULT_COLOUR = (26,26,26)
GRID_LINE_COLOUR = (31,31,31)
BARRIER_COLOUR = (0, 0, 0)
PATH_COLOUR = (255, 255, 0)

display = pygame.display.set_mode((DISPLAY_SIZE, DISPLAY_SIZE))
pygame.display.set_caption("Pathfinding Visualizer")

class Node:
	# Node constructor
	def __init__(self, row, col, blockSize):
		self.row = row
		self.col = col
		self.x = row * blockSize
		self.y = col * blockSize
		self.blockSize = blockSize
		self.colour = DEFAULT_COLOUR

	def isNotBarrier(self):
		return self.colour != BARRIER_COLOUR
		
	def setColour(self, colour):
		self.colour = colour
	
	def isNotDefaultColour(self):
		return self.colour != DEFAULT_COLOUR
	
	# we will only redraw the node (not the whole display)
	# The normal parameter is for the animation
		# normal = True means draw the regular square
		# normal = False means draw a circle instead
	def drawNode(self, display, normal = True):
		rect = pygame.Rect(self.x, self.y, self.blockSize, self.blockSize)
		if normal:
			pygame.draw.rect(display, self.colour, rect)
		else:
			centre = (self.x + self.blockSize // 2, self.y + self.blockSize // 2)
			pygame.draw.circle(display, self.colour, centre, self.blockSize // 2.5)
		pygame.draw.rect(display, GRID_LINE_COLOUR, rect, 1)
		pygame.display.update(rect)
	
	# basic defintion to compare nodes (ie. always return True)
	def __lt__(self, other):
		return True

def makeGrid(display, size, numRows):
	grid = []
	blockSize = size // numRows
	for i in range(numRows):
		grid.append([])
		for j in range(numRows):
			node = Node(i, j, blockSize)
			node.drawNode(display)
			grid[i].append(node)
	return grid

def resetGrid(display, grid):
	for row in grid:
		for node in row:
			if node.isNotDefaultColour():
				node.setColour(DEFAULT_COLOUR)
				node.drawNode(display)

def getMousePosition(position, size, numRows):
	blockSize = size // numRows
	y, x = position
	return y // blockSize, x // blockSize

def resetSearchingAnimation(display, startNode, endNode, grid):
	for row in grid:
		for node in row:
			if node.isNotDefaultColour() and node.isNotBarrier() and node is not startNode and node is not endNode:
				node.setColour(DEFAULT_COLOUR)
				node.drawNode(display)

def getListOfNeighbours(node, grid):
	neighbourList = []
	# up
	if node.row - 1 >= 0:
		neighbourList.append(grid[node.row - 1][node.col])
	# down
	if node.row + 1 < NUMBER_OF_ROWS:
		neighbourList.append(grid[node.row + 1][node.col])
	# left
	if node.col - 1 >=  0:
		neighbourList.append(grid[node.row][node.col - 1])
	# right
	if node.col + 1 < NUMBER_OF_ROWS:
		neighbourList.append(grid[node.row][node.col + 1])

	##########################################
	# the following logic is if you want to include diagonals
	# if not, use Manhattan distance instead of Euclidean distance

	# # top left
	# if node.row - 1 >= 0 and node.col - 1>= 0:
	# 	neighbourList.append(grid[node.row - 1][node.col - 1])
	# # top right
	# if node.row - 1 >= 0 and node.col + 1 < NUMBER_OF_ROWS:
	# 	neighbourList.append(grid[node.row - 1][node.col + 1])
	# # bottom left
	# if node.row + 1 < NUMBER_OF_ROWS and node.col - 1 >= 0:
	# 	neighbourList.append(grid[node.row + 1][node.col - 1])
	# # bottom right
	# if node.row + 1 < NUMBER_OF_ROWS and node.col + 1 < NUMBER_OF_ROWS:
	# 	neighbourList.append(grid[node.row + 1][node.col + 1])

	##########################################

	return neighbourList

def dijkstrasAlgorithm(display, startNode, endNode, grid):
	queue = PriorityQueue()
	queue.put((0, 0, startNode))
	queueNodes = {startNode}
	previousNode = {}
	distanceOfNode = {node: float("inf") for row in grid for node in row}
	distanceOfNode[startNode] = 0

	numNodes = 0
	clock = pygame.time.Clock()
	while not queue.empty():
		node = queue.get()[2]
		queueNodes.remove(node)
		if node is endNode:
			resetSearchingAnimation(display, startNode, endNode, grid)
			path = []
			node = previousNode[endNode]
			while node is not startNode:
				path.append(node)
				node = previousNode[node]
			path = list(reversed(path))
			return path, numNodes

		listOfNeighbours = getListOfNeighbours(node, grid)

		for neighbour in listOfNeighbours:
			if neighbour.isNotBarrier():
				distance = distanceOfNode[node] + 1
				if (distance < distanceOfNode[neighbour]):
					previousNode[neighbour] = node
					distanceOfNode[neighbour] = distance
					if neighbour not in queueNodes:
						numNodes += 1
						queue.put((distance, numNodes, neighbour))
						queueNodes.add(neighbour)
						if neighbour is not endNode:
							neighbour.setColour(VISITING)
							neighbour.drawNode(display, False)

		if node is not startNode:
			node.setColour(VISITED)
			node.drawNode(display)

		for event in pygame.event.get():
			# check if the user exits the pygame display
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		clock.tick(60)
	
	return None, numNodes

def getManhattanDistance(startNode, endNode):
	return abs(startNode.row - endNode.row) + abs(startNode.col - endNode.col)

def getEuclideanDistance(startNode, endNode):
	return math.sqrt(abs(startNode.row - endNode.row)**2 + abs(startNode.col - endNode.col)**2)

def aStarAlgorithm(display, startNode, endNode, grid):
	queue = PriorityQueue()
	queue.put((0, 0, startNode))
	queueNodes = {startNode}
	previousNode = {}
	gScore = {node: float("inf") for row in grid for node in row}
	gScore[startNode] = 0
	fScore = {node: float("inf") for row in grid for node in row}
	fScore[startNode] = getManhattanDistance(startNode, endNode)

	numNodes = 0
	clock = pygame.time.Clock()
	while not queue.empty():
		node = queue.get()[2]
		queueNodes.remove(node)

		if node is endNode:
			resetSearchingAnimation(display, startNode, endNode, grid)
			path = []
			node = previousNode[endNode]
			while node is not startNode:
				path.append(node)
				node = previousNode[node]
			path = list(reversed(path))
			return path, numNodes

		listOfNeighbours = getListOfNeighbours(node, grid)

		for neighbour in listOfNeighbours:
			if neighbour.isNotBarrier():
				tentativeGScore = gScore[node] + 1
				if tentativeGScore < gScore[neighbour]:
					previousNode[neighbour] = node
					gScore[neighbour] = tentativeGScore
					fScore[neighbour] = gScore[neighbour] + getManhattanDistance(neighbour, endNode)
					if neighbour not in queueNodes:
						numNodes += 1
						queue.put((fScore[neighbour], numNodes, neighbour))
						queueNodes.add(neighbour)
						if neighbour is not endNode:
							neighbour.setColour(VISITING)
							neighbour.drawNode(display, False)

		if node is not startNode:
			node.setColour(VISITED)
			node.drawNode(display)
		
		for event in pygame.event.get():
			# check if the user exits the pygame display
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		clock.tick(60)
	
	return None, numNodes

def drawPath(display, path, colour, animationTime):
	for node in path:
		node.setColour(colour)
		node.drawNode(display)
		pygame.time.wait(animationTime)

def main(display, size, numRows):
	pygame.init()
	grid = makeGrid(display, size, numRows)
	startNode = None
	endNode = None
	path = []

	window = Tk()
	window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
	window.withdraw()

	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():

			# check if the user exits the pygame display
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			# check if the user has typed
			if event.type == pygame.KEYDOWN:

				dKey = event.key == pygame.K_d
				aKey = event.key == pygame.K_a
				# if either a the d-key or a-key was pressed
				if dKey or aKey:
					if dKey:
						# start finding the path with dijkstras
						path, numNodes = dijkstrasAlgorithm(display, startNode, endNode, grid)
					else:
						# start finding the path with dijkstras
						path, numNodes = aStarAlgorithm(display, startNode, endNode, grid)

					if path is not None:
						drawPath(display, path, PATH_COLOUR, 30)
						msg = 'Path length: ' + str(len(path) + 1)
					else:
						msg = 'Path does not exist'
					messagebox.showinfo('Pathfinding stats: ', 'Searched: ' +  str(numNodes) + ' nodes' + '\n' + msg)
					window.quit()
				
				# reset the display
				elif event.key == pygame.K_r:
					for row in grid:
						for node in row:
							resetGrid(display, grid)
							startNode = endNode = None

			# check if the user left or right clicks the mouse
			leftClick = pygame.mouse.get_pressed()[0]
			rightClick = pygame.mouse.get_pressed()[2]
			if leftClick or rightClick:
				position = pygame.mouse.get_pos()
				row, col = getMousePosition(position, size, numRows)
				node = grid[row][col]

				# left click
				if leftClick:
					if startNode is None and node is not endNode:
						node.setColour(START_COLOUR)
						node.drawNode(display)
						startNode = node
					elif endNode is None and node is not startNode:
						node.setColour(END_COLOUR)
						node.drawNode(display)
						endNode = node
					elif node is not startNode and node is not endNode:
						node.setColour(BARRIER_COLOUR)
						node.drawNode(display)

				# right click
				else:
					if node is startNode:
						startNode = None
					elif node is endNode:
						endNode = None
					node.setColour(DEFAULT_COLOUR)
					node.drawNode(display)

		clock.tick(60)

if __name__ == "__main__":
	main(display, DISPLAY_SIZE, NUMBER_OF_ROWS)
