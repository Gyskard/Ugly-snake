import pygame
import pygame.gfxdraw
import time
import configparser
import random

gameConfig = configparser.ConfigParser()
gameConfig.read('config/config.ini')
sizeX, sizeY, interval = int(gameConfig['Cell']['x']), int(gameConfig['Cell']['y']), float(gameConfig['Snake']['speed'])

def initGrid():
    return [["e" for x in range(sizeX)] for y in range(sizeY)]

def analyzePos(pos, let):
    size = {"x": sizeX, "y": sizeY}[let]
    if pos < -1:
        return size + pos
    if pos < 0:
        return size - 1
    if pos > size - 1:
        return pos - size
    return pos

def addPos(x, y, symbol, g):
    if not [analyzePos(x, "x"), analyzePos(y, "y")] == srchH(g):
        g[analyzePos(y, "y")][analyzePos(x, "x")] = symbol
    return g

def headS(g):
    return addPos(randPos(g)[0], randPos(g)[1], "h", g)

def bodyS(x, y, direction, g, size):
    h = [[srchH(g)[0], srchH(g)[1]]]
    a = {"up": ["y", 1], "down": ["y", -1], "left": ["x", 1], "right": ["x", -1]}[direction]
    for i in range(size):
        if a[0] == "x":
            x += a[1]
        else:
            y += a[1]
        g = addPos(x, y, "b", g)
        h.append([analyzePos(x, "x"), analyzePos(y, "y")])
    return [g, h]

def changDir(touche, direction):
    if (touche in ["z", "s"] and direction in ["left", "right"]) or (touche in ["q", "d"] and direction in ["up", "down"]):
        return {"z": "up", "s": "down", "q": "left", "d": "right"}[touche]
    return direction

def move(g, direction, history):
    x, y = srchH(g)
    g = initGrid()
    transform = {"up": ["y", -1], "down": ["y", 1], "left": ["x", -1], "right": ["x", 1]}[direction]
    if transform[0] == "y":
        y += transform[1]
    else:
        x += transform[1]
    g = addPos(x, y, "h", g)
    history.insert(0, [x, y])
    del history[len(history) - 1]
    for elm in history:
        g = addPos(elm[0], elm[1], "b", g)
    return [g, history]

def lenB(g, size):
    sizeNow = 0
    for x in g:
        for y in x:
            if y == "b":
                sizeNow += 1
    return sizeNow == size

def randPos(g):
    return [random.randint(0,len(g[0]) - 1), random.randint(0,len(g) - 1)]

def srchH(g):
    yH = 0
    for x in g:
        xH = 0
        for y in x:
            if y == "h":
                return [xH, yH]
            xH += 1
        yH += 1
    return False

def crdsFood(g):
    randomCoords = randPos(g)
    while g[randomCoords[0]][randomCoords[1]] != "e":
        randomCoords = randPos(g)
    return randomCoords

def fail():
    print("Ha bah c'est perdu!")

def ocurencSnak(h):
    for i in range(len(h) - 1):
        if h.count(h[i]) > 1 and i < len(h) - 2:
            return True
    return False

def font(size, text, color):
    return pygame.font.Font("font/Stencil8bit-Regular.otf", size).render(text, 1, color)

def main():
    game = True

    while game:
        partie, defeat, foodNow, start, restart, score = True, False, True, False, False, 0
        content = initGrid()
        headS(content)
        direction = ["up", "down", "left", "right"][random.randint(0, 3)]
        result = bodyS(srchH(content)[0], srchH(content)[1], direction, content, int(gameConfig['Snake']['size']))
        content, history = result
        foodX, foodY = crdsFood(content)

        window = [(sizeX * 10) + 20, (sizeY * 10) + 80]
        if window[0] < 140:
            window[0] = 140
        if window[1] < 180:
            window[1] = 180

        pygame.init()
        screen = pygame.display.set_mode((window[0], window[1]))

        centerX, centerY = screen.get_rect().centerx, screen.get_rect().centery
        white = (255, 255, 255)
        red = (255, 0, 0)

        txtTitl, txtMenu1, txtMenu2 = font(50, "SNAKE", white), font(27, "Press enter", white), font(27, "to start", white)

        txtposTitl, txtposMenu1, txtposMenu2 = txtTitl.get_rect(), txtMenu1.get_rect(), txtMenu2.get_rect()
        txtposTitl.centerx = txtposMenu1.centerx = txtposMenu2.centerx = centerX
        txtposTitl.centery, txtposMenu1.centery, txtposMenu2.centery = 25, centerY, centerY + 20

        timeNow = timeFood = time.time()
        while not start:
            screen.fill((0, 0, 0))

            for text in [[txtTitl, txtposTitl], [txtMenu1, txtposMenu1], [txtMenu2, txtposMenu2]]:
                screen.blit(text[0], text[1])

            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:

                    if event.key == 13:
                        start = True

                elif event.type == pygame.QUIT:
                    defeat, start, game, restart = True, True, False, True
            pygame.display.flip()
        while not defeat:
            screen.fill((0, 0, 0)), screen.blit(txtTitl, txtposTitl)

            content = initGrid()
            content, history = result

            if (time.time() - timeNow) > interval:
                result = move(content, direction, history)
                moveAvaible, timeNow = True, time.time()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    defeat, start, game, restart = True, False, False, True


                elif event.type == pygame.KEYDOWN and moveAvaible:
                    direction = changDir({119: "z", 273: "z", 115: "s", 274: "s", 97: "q", 276: "q", 100: "d", 275: "d"}[event.key], direction)
                    moveAvaible = False

            if [foodX, foodY] == history[0]:
                history.append(history[len(history) - 1])
                foodX, foodY = crdsFood(content)
                content = addPos(foodX, foodY, "f", content)
                timeFood, foodNow = time.time(), True
                score += 10

            if time.time() - timeFood > 5 and not foodNow:
                foodX, foodY = crdsFood(content)
                content = addPos(foodX, foodY, "f", content)
                timeFood, foodNow = time.time(), True

            else:
                content = addPos(foodX, foodY, "f", content)

            coords = [[10, 70], [10, 10]]

            for lign in content:
                for elm in lign:
                    pygame.gfxdraw.box(screen, ((coords[0][0]), coords[0][1], coords[1][0], coords[1][1]), {"e": [255, 255, 255], "b": [61, 241, 33], "h": [255, 148, 2], "f": [255, 0, 0]}[elm])
                    coords[0][0] += 10
                coords[0][0], coords[0][1] = 10, coords[0][1] +10

            if ocurencSnak(history):
                defeat = True

            pygame.display.flip()

        while not restart:
            screen.fill((0, 0, 0))

            txtRstart1, txtRstart2, txtScore = font(27, "Press enter", white), font(27, "to restart", white), font(35, "Score: " + str(score), red)

            txtposRstart1, txtposRstart2, txtposScore = txtRstart1.get_rect(), txtRstart2.get_rect(), txtScore.get_rect()
            txtposRstart1.centerx = txtposRstart2.centerx = txtposScore.centerx = centerX
            txtposRstart1.centery, txtposRstart2.centery, txtposScore.centery = centerY + 30, centerY + 50, centerY

            for text in [[txtTitl, txtposTitl], [txtRstart1, txtposRstart1], [txtRstart2, txtposRstart2], [txtScore, txtposScore]]:
                screen.blit(text[0], text[1])

            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:

                    if event.key == 13:
                        restart = True
                        start = False
                        defeat = False

                elif event.type == pygame.QUIT:
                    defeat, start, game, restart = True, False, False, True

            pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
