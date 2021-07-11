from PIL.Image import new
from pyautogui import click
from screenshot import *
from boardConverter import *
import time
import sys

movesLeft = numColumns*numRows
movesToExecute = 1

pastBoard = getBoardArray()
leftClick(round(numColumns/2), round(numRows/2))
time.sleep(2)
newBoard = getBoardArray()


def surroundingCellsNum(column, row):
    onVerticalEdge = column == 0 or column == numColumns-1
    onHorizontalEdge = row == 0 or row == numRows-1

    if onHorizontalEdge and onVerticalEdge:
        return 4
    elif onVerticalEdge or onHorizontalEdge:
        return 6
    else:
        return 9


def nearbyIncompleteCells(column, row):
    res = set()
    for x in range(column-1, column+2):
        for y in range(row-1, row+2):
            if y >= 0 and y < numRows and x >= 0 and x < numColumns:
                if newBoard[y][x] > 0 and newBoard[y][x] < 9:
                    res.add((x, y))
    return res


def surroundingMines(column, row):
    mines = 0
    for x in range(column-1, column+2):
        for y in range(row-1, row+2):
            if y >= 0 and y < numRows and x >= 0 and x < numColumns:
                if newBoard[y][x] == -1:
                    mines += 1
    return mines


def findNewCells():
    result = []

    for column in range(numColumns):
        for row in range(numRows):
            if pastBoard[row][column] != newBoard[row][column] and newBoard[row][column] != 0:
                result.append((column, row))

    return result


def shouldExamine(column, row):
    notOutOfBounds = row >= 0 and row < numRows and column >= 0 and column < numColumns
    return notOutOfBounds and newBoard[row][column] != 0 and newBoard[row][column] != 9 and newBoard[row][column] != -1


def findCellsToExamine():
    result = set()
    consideredCells = findNewCells()

    # find every cell near
    for coordinate in consideredCells:
        result.add(coordinate)
        for x in range(coordinate[0]-1, coordinate[0]+2):
            for y in range(coordinate[1]-1, coordinate[1]+2):
                if shouldExamine(x, y):
                    result.add((x, y))

    return result


def solveObviousOnes(cellsToCheck):
    flag = set()
    mineFree = set()

    for coordinate in cellsToCheck:
        mines = 0
        unknown = 0
        noMines = 0
        for x in range(coordinate[0]-1, coordinate[0]+2):
            for y in range(coordinate[1]-1, coordinate[1]+2):
                if y >= 0 and y < numRows and x >= 0 and x < numColumns:
                    if newBoard[y][x] == -1:
                        mines += 1
                    elif newBoard[y][x] == 9:
                        unknown += 1
                    else:
                        noMines += 1

        # check for the flags part
        if surroundingCellsNum(coordinate[0], coordinate[1])-noMines == newBoard[coordinate[1]][coordinate[0]]:
            for x in range(coordinate[0]-1, coordinate[0]+2):
                for y in range(coordinate[1]-1, coordinate[1]+2):
                    if y >= 0 and y < numRows and x >= 0 and x < numColumns:
                        if newBoard[y][x] == 9:
                            flag.add((x, y))

        # check for no mines part
        if newBoard[coordinate[1]][coordinate[0]] == mines:
            for x in range(coordinate[0]-1, coordinate[0]+2):
                for y in range(coordinate[1]-1, coordinate[1]+2):
                    if y >= 0 and y < numRows and x >= 0 and x < numColumns:
                        if newBoard[y][x] == 9:
                            mineFree.add((x, y))

    return (flag, mineFree)


def inSetList(elm, setList):
    for i in range(len(setList)):
        if elm in setList[i]:
            return (True, i)
    return (False, -1)


def findSectionsToProbTest():
    unexploredCells = []
    testableSurroundingCells = []
    sortedTestableCells = []

    # Every coordinate
    for row in range(numRows):
        for column in range(numColumns):
            # if it is an intresting tile
            if newBoard[row][column] > 0 and newBoard[row][column] < 9:
                # Check if it still has an undiscovered tile
                res = []
                for x in range(column-1, column+2):
                    for y in range(row-1, row+2):

                        if y >= 0 and y < numRows and x >= 0 and x < numColumns and newBoard[y][x] == 9:
                            res.append((x, y))

                if len(res) > 0:
                    unexploredCells.append((column, row))
                    testableSurroundingCells.append(res)

    # Sort my stuff

    for i in range(len(unexploredCells)):
        similarSets = set()
        for coordinate in testableSurroundingCells[i]:
            inSetData = inSetList(coordinate, sortedTestableCells)
            if inSetData[0]:
                similarSets.add(inSetData[1])

        similarSets = list(similarSets)
        if len(similarSets) == 0:
            sortedTestableCells.append(set(testableSurroundingCells[i]))
        elif len(similarSets) == 1:
            sortedTestableCells[similarSets[0]].update(
                set(testableSurroundingCells[i]))
        else:
            while len(similarSets) > 1:
                deletedSet = sortedTestableCells.pop(similarSets[-1])
                similarSets.pop()
                sortedTestableCells[similarSets[0]].update(deletedSet)
            sortedTestableCells[similarSets[0]].update(
                set(testableSurroundingCells[i]))

    # print(sortedTestableCells)
    # print(len(sortedTestableCells))

    return sortedTestableCells


def solveProbabilityOnes():
    cellProbabilities = {}
    # Step 1 Determine elligible ones
    # Step 2 Classify them by proximity
    explorableCells = findSectionsToProbTest()
    explorableCells.sort(key=len)
    # Step 3 Find every possible iteration through recursion
    for cellGroup in explorableCells:
        incompleteCellsDict = {}
        cellsAndSurroundingDict = {}
        for coordinate in cellGroup:
            # Explorable cells with surrounding cells
            cellsAndSurroundingDict[coordinate] = nearbyIncompleteCells(
                coordinate[0], coordinate[1])
            # Setting up surrounding cells
            for incompleteCoordinate in cellsAndSurroundingDict[coordinate]:
                incompleteCellsDict[incompleteCoordinate] = 0

        for incompleteCoordinate in incompleteCellsDict.keys():
            x = incompleteCoordinate[0]
            y = incompleteCoordinate[1]
            mines = surroundingMines(x, y)
            incompleteCellsDict[incompleteCoordinate] = newBoard[y][x] - mines

        # Step 4 Do probability
        goodResults = []
        cellGroupList = list(cellGroup)
        possibilities = [False]*len(cellGroupList)
        dontGoFurther = False
        totalRemainingMines = sum(incompleteCellsDict.values())

        def tryPossibiility(attempt, index, changeMine, incompletedCellDict, minesSum):
            nonlocal dontGoFurther
            dontGoFurther = False
            attempt[index] = changeMine

            # print(attempt)
            if changeMine:
                cellChanged = cellGroupList[index]
                for coordinate in cellsAndSurroundingDict[cellChanged]:
                    minesSum -= 1
                    incompletedCellDict[coordinate] -= 1
                    if incompletedCellDict[coordinate] < 0:
                        dontGoFurther = True

            if dontGoFurther:
                return
            if minesSum == 0:
                nonlocal goodResults
                goodResults.append(attempt.copy())
                return
            if index == len(possibilities)-1:
                return

            tryPossibiility(attempt.copy(), index+1, False,
                            incompletedCellDict.copy(), minesSum)
            tryPossibiility(attempt.copy(), index+1, True,
                            incompletedCellDict.copy(), minesSum)

        tryPossibiility(possibilities.copy(), 0, False,
                        incompleteCellsDict.copy(), totalRemainingMines)
        tryPossibiility(possibilities.copy(), 0, True,
                        incompleteCellsDict.copy(), totalRemainingMines)
        # print(goodResults)
        # print(len(goodResults))

        for index, coord in enumerate(cellGroupList):
            tot = 0
            for attempt in goodResults:
                if attempt[index]:
                    tot += 1
                else:
                    tot += 0
            cellProbabilities[coord] = tot/len(cellGroupList)
            # print(explorableCells)
    print(cellProbabilities)
    print(len(cellProbabilities))
    return cellProbabilities


def updateBoard():
    global pastBoard
    global newBoard

    pastBoard = newBoard
    newBoard = getBoardArray()


def makeMoves():
    cellsToExamine = findCellsToExamine()
    print(findCellsToExamine())
    moves = solveObviousOnes(cellsToExamine)

    global movesToExecute
    movesToExecute = len(moves[0])+len(moves[1])

    global movesLeft
    for coordinate in moves[0]:
        rightClick(coordinate[0], coordinate[1])
        movesLeft -= 1
    for coordinate in moves[1]:
        leftClick(coordinate[0], coordinate[1])
        movesLeft -= 1

    if movesLeft == 0:
        sys.exit("SOLVED!!!")


while movesLeft > 0:
    while movesToExecute > 0:
        makeMoves()
        time.sleep(0.9)
        updateBoard()

    print("COMPUTER IS THINKING")
    cellsWithProbabilities = solveProbabilityOnes()
    cellsProbList = list(cellsWithProbabilities.items())
    cellsProbList.sort(key=lambda x: x[1])

    clickLeftList = []
    clickRightList = []
    index = 0
    while index < len(cellsProbList):
        if cellsProbList[index][1] == 0:
            clickLeftList.append(cellsProbList[index][0])
            index += 1
        else:
            break

    while index < len(cellsProbList):
        if cellsProbList[-index][1] == 1:
            clickRightList.append(cellsProbList[-index][0])
            index += 1
        else:
            break

    if len(clickLeftList) == 0 and len(clickRightList) == 0:
        print("Taking a minor risk")
        clickLeftList.append(cellsProbList[0][0])

    for coordinate in clickRightList:
        rightClick(coordinate[0], coordinate[1])
        movesLeft -= 1
    for coordinate in clickLeftList:
        leftClick(coordinate[0], coordinate[1])
        movesLeft -= 1

    if movesLeft == 0:
        sys.exit("SOLVED!!!")

    time.sleep(0.9)

    updateBoard()
    movesToExecute = 1
