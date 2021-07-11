import pyautogui as pgui

startX = 33
startY = 175

numColumns = 24
numRows = 20

pixel = 25
halfPixel = pixel/2


def screenshot():
    pgui.screenshot("board.png", region=(startX, startY, 600, 500))


def moveMouseAway():
    pgui.moveTo(480, 10)


def getXCoordinate(column):
    return column*pixel+startX


def getYCoordinate(row):
    return row*pixel+startY


def cellScreenshot(filename, row, column):
    pgui.screenshot(filename, region=(getXCoordinate(row),
                    getYCoordinate(column), pixel, pixel))


def boardXCoord(column):
    return column*pixel


def boardYCoord(row):
    return row*pixel


def leftClick(column, row):
    pgui.click(x=getXCoordinate(column), y=getYCoordinate(row))


def rightClick(column, row):
    pgui.rightClick(x=getXCoordinate(column), y=getYCoordinate(row))
