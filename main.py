import random
import sys
import threading

import pygame
from pygame.locals import *


class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        puzzleLoad()


# Create the constants
BOARDWIDTH = 0  # number of columns in the board
BOARDHEIGHT = 0  # number of rows in the board
TILESIZE = 80  # size of the tile
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30  # frames per second
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
VIOLET = (238, 130, 238)
INDIGO = (75, 0, 130)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED =           (255,   0,   0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)


UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT, \
        MAIN_SURF, MAIN_RECT, BOARDWIDTH, BOARDHEIGHT, img, TILESIZE, XMARGIN, YMARGIN, BASICFONTSIZE, pic, \
        WINDOWHEIGHT, WINDOWWIDTH

    pygame.init()

    # initialising all the constants again according to the game screen
    FPSCLOCK = pygame.time.Clock()
    WINDOWWIDTH = pygame.display.Info().current_w
    WINDOWHEIGHT = pygame.display.Info().current_h
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    XMARGIN = int(WINDOWWIDTH / 10)
    YMARGIN = int(2 * WINDOWHEIGHT / 10)

    BASICFONTSIZE = int(WINDOWHEIGHT / 20)
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 5 * BASICFONTSIZE)
    NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 3 * BASICFONTSIZE)
    SOLVE_SURF, SOLVE_RECT = makeText('Solve', TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - BASICFONTSIZE)
    MAIN_SURF, MAIN_RECT = makeText('Main Menu', TEXTCOLOR, BGCOLOR, WINDOWWIDTH - 120,
                                    WINDOWHEIGHT - 5 * BASICFONTSIZE)

    RESET_RECT.topleft = (WINDOWWIDTH - MAIN_SURF.get_width(), WINDOWHEIGHT - 8 * BASICFONTSIZE)
    SOLVE_RECT.topleft = (WINDOWWIDTH - MAIN_SURF.get_width(), WINDOWHEIGHT - 6 * BASICFONTSIZE)
    NEW_RECT.topleft = (WINDOWWIDTH - MAIN_SURF.get_width(), WINDOWHEIGHT - 4 * BASICFONTSIZE)
    MAIN_RECT.topleft = (WINDOWWIDTH - MAIN_SURF.get_width(), WINDOWHEIGHT - 2 * BASICFONTSIZE)

    startingScreen()  # starting screen displays flashing SLIDE PUZZLE
    mainBoard, solutionSeq, SOLVEDBOARD, pic, img, allMoves, puzzle, TILESIZE = preparingGame()

    while True:  # main game loop

        slideTo = None  # the direction, if any, a tile should slide
        msg = 'Tap on a tile to slide.'  # contains the message to show in the upper left corner.
        if mainBoard == SOLVEDBOARD:  # check if the board is solved
            msg = 'Solved!'
            allMoves = []
            solutionSeq = []

        drawBoard(mainBoard, msg)  # draws the board on the screen

        checkForQuit(pygame.event.get())
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves) # clicked on Reset button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(difficultyScreen())  # clicked on New Game button
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)  # clicked on Solve button
                        allMoves = []
                    elif MAIN_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq, SOLVEDBOARD, pic, img, allMoves, puzzle, TILESIZE = preparingGame()
                else:
                    # check if the clicked tile was next to the blank spot
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

        if slideTo:
            # show slide on screen
            slideAnimation(mainBoard, slideTo, 'Tap on a tile to slide.', FPS, animationSpeed=int(TILESIZE / 5))
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)  # record the slide
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit(ev):
    # checks for any quit event
    events = []
    if len(ev) > 0:
        for e in ev:
            if e.type == QUIT or e.type == KEYDOWN:
                terminate()
            events.append(e)
    # adds the rest of the event back to event queue of pygame
    for _ in events:
        pygame.event.post(_)


def getStartingBoard():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # This function does not check if the move is valid.
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE)
    top = YMARGIN + (tileY * TILESIZE)
    return left, top


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return tileX, tileY
    return None, None


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)
    imge = img[number - 1]
    imgRect = imge.get_rect()
    imgRect.topleft = (left + adjx, top + adjy)
    DISPLAYSURF.blit(imge, imgRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return textSurf, textRect


def drawBoard(board, message):

    DISPLAYSURF.fill(BGCOLOR)

    drawFinalPic()  # draws the original picture for reference to the player
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 9, height + 9), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    DISPLAYSURF.blit(MAIN_SURF, MAIN_RECT)


def drawFinalPic():
    picRect = pic.get_rect()
    picRect.topleft = (2 * XMARGIN + BOARDWIDTH * TILESIZE, YMARGIN)
    DISPLAYSURF.blit(pic, picRect)


def slideAnimation(board, direction, message, FPS, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
        tempx, tempy = getLeftTopOfTile(blankx, blanky)
        tempSurf = pygame.draw.rect(DISPLAYSURF, BGCOLOR, (tempx, tempy, TILESIZE, 2 * TILESIZE))
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
        tempx, tempy = getLeftTopOfTile(movex, movey)
        tempSurf = pygame.draw.rect(DISPLAYSURF, BGCOLOR, (tempx, tempy, TILESIZE, 2 * TILESIZE))
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
        tempx, tempy = getLeftTopOfTile(blankx, blanky)
        tempSurf = pygame.draw.rect(DISPLAYSURF, BGCOLOR, (tempx, tempy, 2 * TILESIZE, TILESIZE))
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky
        tempx, tempy = getLeftTopOfTile(movex, movey)
        tempSurf = pygame.draw.rect(DISPLAYSURF, BGCOLOR, (tempx, tempy, 2 * TILESIZE, TILESIZE))

    # prepare the base surface
    drawBoard(board, message)

    for i in range(0, TILESIZE, animationSpeed):
        # animate the tile sliding over
        checkForQuit(pygame.event.get())
        # draw the blank squares so that when the tile is sliding background looks empty
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, tempSurf)
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    # From a starting configuration, make numSlides number of moves (and
    # animate these moves).
    FPS = 360
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)  # pause 500 milliseconds for effect
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', FPS, animationSpeed=int(TILESIZE / 5))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):
    # make all of the moves in allMoves in reverse.
    revAllMoves = allMoves[:]  # gets a copy of the list
    revAllMoves.reverse()
    FPS = 120
    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', FPS, animationSpeed=int(TILESIZE / 5))
        makeMove(board, oppositeMove)


def chooseScreen():
    # choose the grid size
    DISPLAYSURF.fill(BGCOLOR)

    CHOOSE_SURF, CHOOSE_RECT = makeText('Choose the grid size...', TEXTCOLOR, BGCOLOR, 0, 0)
    CHOOSE_RECT.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 4)

    THREE_SURF, THREE_RECT = makeText('3 X 3', TEXTCOLOR, BGCOLOR, 0, 0)
    THREE_RECT.center = (WINDOWWIDTH / 4, WINDOWHEIGHT / 2)

    FOUR_SURF, FOUR_RECT = makeText('4 X 4', TEXTCOLOR, BGCOLOR, 0, 0)
    FOUR_RECT.center = (3 * WINDOWWIDTH / 4, WINDOWHEIGHT / 2)

    DISPLAYSURF.blit(CHOOSE_SURF, CHOOSE_RECT)
    DISPLAYSURF.blit(THREE_SURF, THREE_RECT)
    DISPLAYSURF.blit(FOUR_SURF, FOUR_RECT)
    pygame.display.update()

    while True:
        checkForQuit(pygame.event.get())
        event = pygame.event.get()
        for ev in event:
            if ev.type == MOUSEBUTTONUP:
                mouseX, mouseY = ev.pos
                if THREE_RECT.collidepoint(mouseX, mouseY):
                    return 3
                elif FOUR_RECT.collidepoint(mouseX, mouseY):
                    return 4


def startingScreen():
    FPS = 5
    colors = [VIOLET, INDIGO, BLUE, GREEN, YELLOW, ORANGE, RED]
    DISPLAYSURF.fill(BGCOLOR)
    TITLEFONT = pygame.font.Font('comic.ttf', int(WINDOWHEIGHT / 10))

    # Load the puzzles in memory using threading so that it doesn't takes up extra time
    t = MyThread()
    t.start()
    for _ in range(3):
        for color in colors:
            checkForQuit(pygame.event.get())
            titleText = TITLEFONT.render('SLIDE PUZZLE', True, color)
            titleRect = titleText.get_rect()
            titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
            DISPLAYSURF.blit(titleText, titleRect)
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    # Wait for the loading of puzzle to finish
    t.join()


def difficultyScreen():
    # Screen to choose difficulty level
    DISPLAYSURF.fill(BGCOLOR)

    CHOOSE_SURF, CHOOSE_RECT = makeText('Choose difficulty...', TEXTCOLOR, BGCOLOR, 0, 0)
    EASY_SURF, EASY_RECT = makeText('EASY', TEXTCOLOR, BGCOLOR, 0, 0)
    MED_SURF, MED_RECT = makeText('MEDIUM', TEXTCOLOR, BGCOLOR, 0, 0)
    HARD_SURF, HARD_RECT = makeText('HARD', TEXTCOLOR, BGCOLOR, 0, 0)

    CHOOSE_RECT.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 4)
    EASY_RECT.center = (WINDOWWIDTH / 6, WINDOWHEIGHT / 2)
    MED_RECT.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
    HARD_RECT.center = (5 * WINDOWWIDTH / 6, WINDOWHEIGHT / 2)

    DISPLAYSURF.blit(CHOOSE_SURF, CHOOSE_RECT)
    DISPLAYSURF.blit(EASY_SURF, EASY_RECT)
    DISPLAYSURF.blit(MED_SURF, MED_RECT)
    DISPLAYSURF.blit(HARD_SURF, HARD_RECT)
    pygame.display.update()

    while True:
        checkForQuit(pygame.event.get())
        event = pygame.event.get()
        for ev in event:
            if ev.type == MOUSEBUTTONUP:
                mouseX, mouseY = ev.pos
                if EASY_RECT.collidepoint(mouseX, mouseY):
                    return 10
                elif MED_RECT.collidepoint(mouseX, mouseY):
                    return 25
                elif HARD_RECT.collidepoint(mouseX, mouseY):
                    return 40


def puzzleLoad():
    # Load the images while the start screen is playing
    # allImage stores all the images available to choose from
    global allImage
    width = 6 * WINDOWWIDTH / 22
    height = 6 * WINDOWHEIGHT / 15
    allImage = []
    image = pygame.image.load('1.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)
    image = pygame.image.load('2.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)
    image = pygame.image.load('3.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)
    image = pygame.image.load('4.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)
    image = pygame.image.load('5.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)
    image = pygame.image.load('6.jpg').convert()
    image = pygame.transform.scale(image, (width, height))
    allImage.append(image)


def isColliding(coords, width, height, x, y):
    # Checks which image the user has chosen
    for i in range(6):
        pRect = pygame.Rect(coords[i], (width, height))
        if pRect.collidepoint(x, y):
            return i + 1
    return None


def puzzleChoiceScreen():
    # Screen to choose from various landscapes
    DISPLAYSURF.fill(BGCOLOR)
    width_gap = int(WINDOWWIDTH / 22)
    height_gap = int(WINDOWHEIGHT / 15)
    width = int(6 * WINDOWWIDTH / 22)
    height = int(6 * WINDOWHEIGHT / 15)
    x = width_gap
    y = height_gap
    coords = []  # Stores the topleft of each Rect to check later which puzzle has been chosen

    for i in range(3):
        imageRect = allImage[i].get_rect()
        imageRect.topleft = (x, y)
        coords.append((x, y))
        DISPLAYSURF.blit(allImage[i], imageRect)
        x += (width_gap + width)

    x = width_gap
    y = 2 * height_gap + height
    for i in range(3, 6):
        imageRect = allImage[i].get_rect()
        imageRect.topleft = (x, y)
        coords.append((x, y))
        DISPLAYSURF.blit(allImage[i], imageRect)
        x += (width_gap + width)

    pygame.display.update()

    while True:
        checkForQuit(pygame.event.get())
        event = pygame.event.get()
        for ev in event:
            if ev.type == MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                puzzle = isColliding(coords, width, height, x, y)
                if puzzle == 1:
                    return 1
                elif puzzle == 2:
                    return 2
                elif puzzle == 3:
                    return 3
                elif puzzle == 4:
                    return 4
                elif puzzle == 5:
                    return 5
                elif puzzle == 6:
                    return 6


def preparingGame():
    global BOARDWIDTH, BOARDHEIGHT, TILESIZE, pic, img
    puzzle = puzzleChoiceScreen()
    BOARDWIDTH = BOARDHEIGHT = chooseScreen()  # returns the size of the board chosen
    TILESIZE = int((WINDOWHEIGHT - 2 * YMARGIN) / BOARDHEIGHT)
    img = []  # list to store cropped images
    pic = pygame.image.load(str(puzzle) + '.jpg').convert()
    pic = pygame.transform.scale(pic, (BOARDWIDTH * TILESIZE, BOARDHEIGHT * TILESIZE))
    imgwidth, imgheight = pic.get_rect().size

    # looping to get the cropped images from the original image
    for i in range(0, imgheight, TILESIZE):
        for j in range(0, imgwidth, TILESIZE):
            box = (j, i, TILESIZE, TILESIZE)
            a = pic.subsurface(box)
            img.append(a)

    pic = pygame.transform.scale(pic, (3 * WINDOWWIDTH / 10, 3 * WINDOWHEIGHT / 10))
    mainBoard, solutionSeq = generateNewPuzzle(difficultyScreen())
    SOLVEDBOARD = getStartingBoard()  # a solved board is the same as the board in a start state.
    allMoves = []  # list of moves made from the solved configuration
    return (mainBoard, solutionSeq, SOLVEDBOARD, pic, img, allMoves, puzzle, TILESIZE)

if __name__ == '__main__':
    main()