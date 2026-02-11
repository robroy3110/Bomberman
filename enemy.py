import math

import pygame
import random
from bomb import Bomb
from enums.power_up_type import PowerUpType
from node import Node
from enums.algorithm import Algorithm


class Enemy:
    dire = [[1, 0, 1], [0, 1, 0], [-1, 0, 3], [0, -1, 2]]

    """ [1, 0, 1]: Movimento para a direita.
        [0, 1, 0]: Movimento para baixo.
        [-1, 0, 3]: Movimento para a esquerda.
        [0, -1, 2]: Movimento para cima."""

    TILE_SIZE = 4

    def __init__(self, x, y, alg):
        self.life = True
        self.path = []
        self.movement_path = []
        self.pos_x = x * Enemy.TILE_SIZE
        self.pos_y = y * Enemy.TILE_SIZE
        self.direction = 0
        self.frame = 0
        self.animation = []
        self.range = 3
        self.bomb_limit = 1
        self.plant = False
        self.algorithm = alg

    def move(self, map, bombs, explosions, enemy):
        if self.direction == 0:
            self.pos_y += 1
        elif self.direction == 1:
            self.pos_x += 1  # COMO MOVER NA GRID
        elif self.direction == 2:
            self.pos_y -= 1
        elif self.direction == 3:
            self.pos_x -= 1

        if self.pos_x % Enemy.TILE_SIZE == 0 and self.pos_y % Enemy.TILE_SIZE == 0:
            self.movement_path.pop(0)
            self.path.pop(0)
            if len(self.path) > 1:
                grid = self.create_grid(map, bombs, explosions, enemy)
                next = self.path[1]
                if grid[next[0]][next[1]] > 1:
                    self.movement_path.clear()
                    self.path.clear()

        if self.frame == 2:
            self.frame = 0
        else:
            self.frame += 1

    def move_chat(self, map, bombs, explosions, enemy):
        if (len(self.path) == len(self.movement_path) +1):
            if self.direction == 0:
                self.pos_y += 1
            elif self.direction == 1:
                self.pos_x += 1  # COMO MOVER NA GRID
            elif self.direction == 2:
                self.pos_y -= 1
            elif self.direction == 3:
                self.pos_x -= 1

            if self.pos_x % Enemy.TILE_SIZE == 0 and self.pos_y % Enemy.TILE_SIZE == 0:
                self.movement_path.pop(0)
                self.path.pop(0)
                if len(self.path) > 1:
                    grid = self.create_grid(map, bombs, explosions, enemy)
                    next = self.path[1]
                    if grid[next[0]][next[1]] > 1:
                        self.movement_path.clear()
                        self.path.clear()

            if self.frame == 2:
                self.frame = 0
            else:
                self.frame += 1
        else:
            self.path = []
            self.movement_path = []
            print("Limpei")

    def make_move(self, map, bombs, explosions, power_ups, enemy):
        if self.algorithm is not Algorithm.CHATGPT5:
            if not self.life:
                return
            if len(self.movement_path) == 0:
                if self.plant:
                    bombs.append(self.plant_bomb(map))
                    self.plant = False
                    map[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)] = 3
                if self.algorithm is Algorithm.DFS:
                    self.dfs(self.create_grid(map, bombs, explosions, enemy))
                else:
                    self.dijkstra(self.create_grid_dijkstra(map, bombs, explosions, enemy))
            else:
                self.direction = self.movement_path[0]
                self.move(map, bombs, explosions, enemy)
        else:
            self.make_move_chatgpt(map, bombs, explosions, power_ups, enemy)

    def make_move_chatgpt(self, map, bombs, explosions, power_ups, enemy):
        ## fazer com que se calcule varias vezes e nao so quando acabar o path calcular uma rota nova
        grid = self.create_chat_grid(map, bombs, explosions, power_ups, enemy)
        if not self.life:
            return
        
        # if not self.path and self.movement_path:
        #     self.movement_path.clear()
        # if self.path and not self.movement_path:
        #     self.path.clear()

        if not self.movement_path:
            if self.plant:
                bombs.append(self.plant_bomb(map))
                self.plant = False
                map[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)] = 3
            for pu in power_ups:
                if pu.pos_x == int(self.pos_x / Enemy.TILE_SIZE) \
                        and pu.pos_y == int(self.pos_y / Enemy.TILE_SIZE):
                    self.consume_power_up(pu, power_ups)
                    map[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)] = 0
            self.chatgpt5(grid)
        else:
            self.direction = self.movement_path[0]
            self.move_chat(map, bombs, explosions, enemy)

    def plant_bomb(self, map):
        b = Bomb(self.range, round(self.pos_x / Enemy.TILE_SIZE), round(self.pos_y / Enemy.TILE_SIZE), map, self)
        self.bomb_limit -= 1
        return b

    def consume_power_up(self, power_up, power_ups):
        if power_up.type == PowerUpType.BOMB:
            self.bomb_limit += 1
        elif power_up.type == PowerUpType.FIRE:
            self.range += 1
        power_ups.remove(power_up)

    def check_death(self, exp):

        for e in exp:
            for s in e.sectors:
                if int(self.pos_x / Enemy.TILE_SIZE) == s[0] and int(self.pos_y / Enemy.TILE_SIZE) == s[1]:
                    self.life = False
                    return

    def dfs(self, grid):

        new_path = [[int(self.pos_x / Enemy.TILE_SIZE), int(self.pos_y / Enemy.TILE_SIZE)]]
        depth = 0
        if self.bomb_limit == 0:
            self.dfs_rec(grid, 0, new_path, depth)
        else:
            self.dfs_rec(grid, 2, new_path, depth)

        self.path = new_path

    def dfs_rec(self, grid, end, path, depth):

        last = path[-1]
        if depth > 200:
            return
        if grid[last[0]][last[1]] == 0 and end == 0:
            return
        elif end == 2:
            if grid[last[0] + 1][last[1]] == end or grid[last[0] - 1][last[1]] == end \
                    or grid[last[0]][last[1] + 1] == end \
                    or grid[last[0]][last[1] - 1] == end:
                if len(path) == 1 and end == 2:
                    self.plant = True
                return

        grid[last[0]][last[1]] = 9

        random.shuffle(self.dire)

        # safe
        if grid[last[0] + self.dire[0][0]][last[1] + self.dire[0][1]] == 0:
            path.append([last[0] + self.dire[0][0], last[1] + self.dire[0][1]])
            self.movement_path.append(self.dire[0][2])
        elif grid[last[0] + self.dire[1][0]][last[1] + self.dire[1][1]] == 0:
            path.append([last[0] + self.dire[1][0], last[1] + self.dire[1][1]])
            self.movement_path.append(self.dire[1][2])
        elif grid[last[0] + self.dire[2][0]][last[1] + self.dire[2][1]] == 0:
            path.append([last[0] + self.dire[2][0], last[1] + self.dire[2][1]])
            self.movement_path.append(self.dire[2][2])
        elif grid[last[0] + self.dire[3][0]][last[1] + self.dire[3][1]] == 0:
            path.append([last[0] + self.dire[3][0], last[1] + self.dire[3][1]])
            self.movement_path.append(self.dire[3][2])

        # unsafe
        elif grid[last[0] + self.dire[0][0]][last[1] + self.dire[0][1]] == 1:
            path.append([last[0] + self.dire[0][0], last[1] + self.dire[0][1]])
            self.movement_path.append(self.dire[0][2])
        elif grid[last[0] + self.dire[1][0]][last[1] + self.dire[1][1]] == 1:
            path.append([last[0] + self.dire[1][0], last[1] + self.dire[1][1]])
            self.movement_path.append(self.dire[1][2])
        elif grid[last[0] + self.dire[2][0]][last[1] + self.dire[2][1]] == 1:
            path.append([last[0] + self.dire[2][0], last[1] + self.dire[2][1]])
            self.movement_path.append(self.dire[2][2])
        elif grid[last[0] + self.dire[3][0]][last[1] + self.dire[3][1]] == 1:
            path.append([last[0] + self.dire[3][0], last[1] + self.dire[3][1]])
            self.movement_path.append(self.dire[3][2])
        else:
            if len(self.movement_path) > 0:
                path.pop(0)
                self.movement_path.pop(0)
        depth += 1
        self.dfs_rec(grid, end, path, depth)

    def dijkstra(self, grid):

        end = 1
        if self.bomb_limit == 0:
            end = 0

        visited = []
        open_list = []
        current = grid[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)]
        current.weight = current.base_weight
        new_path = []
        while True:
            visited.append(current)
            random.shuffle(self.dire)
            if (current.value == end and end == 0) or \
                    (end == 1 and (
                            grid[current.x + 1][current.y].value == 1 or grid[current.x - 1][current.y].value == 1 or
                            grid[current.x][current.y + 1].value == 1 or grid[current.x][
                                current.y - 1].value == 1)):  ##Checkar se é node final
                new_path.append([current.x, current.y])
                while True:
                    if current.parent is None:
                        break
                    current = current.parent
                    new_path.append([current.x, current.y])  ##pegar o caminho todoo, atraves dos parents e dar reverse
                new_path.reverse()
                for xd in range(len(new_path)):
                    if new_path[xd] is not new_path[-1]:
                        if new_path[xd][0] - new_path[xd + 1][0] == -1:
                            self.movement_path.append(1)
                        elif new_path[xd][0] - new_path[xd + 1][0] == 1:
                            self.movement_path.append(3)
                        elif new_path[xd][1] - new_path[xd + 1][1] == -1:
                            self.movement_path.append(0)
                        elif new_path[xd][1] - new_path[xd + 1][1] == 1:
                            self.movement_path.append(2)
                if len(new_path) == 1 and end == 1:
                    self.plant = True
                self.path = new_path
                return

            for i in range(len(self.dire)):
                if current.x + self.dire[i][0] < len(grid) and current.y + self.dire[i][1] < len(grid):
                    if grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].reach \
                            and grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]] not in visited:
                        if grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]] in open_list:
                            if grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].weight > \
                                    grid[current.x][current.y].weight \
                                    + grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].base_weight:
                                grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].parent = current
                                grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].weight = current.weight + \
                                                                                                        grid[current.x +
                                                                                                             self.dire[
                                                                                                                 i][0]][
                                                                                                            current.y +
                                                                                                            self.dire[
                                                                                                                i][
                                                                                                                1]].base_weight
                                grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].direction = self.dire[i][
                                    2]

                        else:
                            grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].parent = current
                            grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].weight = \
                                current.weight + grid[current.x + self.dire[i][0]][
                                    current.y + self.dire[i][1]].base_weight
                            grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]].direction = self.dire[i][2]
                            open_list.append(grid[current.x + self.dire[i][0]][current.y + self.dire[i][1]])

            if len(open_list) == 0:
                self.path = [[int(self.pos_x / Enemy.TILE_SIZE), int(self.pos_y / Enemy.TILE_SIZE)]]
                return

            next_node = open_list[0]
            for n in open_list:
                if n.weight < next_node.weight:
                    next_node = n
            open_list.remove(next_node)
            current = next_node

    def attackEnemy(self, grid):
        print("TOU ATACANDO!!")
        temCaixa = []
        for row in range(len(grid)):
            for line in range(len(grid)):
                if grid[row][line] == 2:
                    temCaixa.append(1)
                    break
        if temCaixa:
            nearbyEnemies = self.nearby_enemies(grid)
            for nearbyEnemy in nearbyEnemies:
                if int(self.pos_x/Enemy.TILE_SIZE) == nearbyEnemy[0] and int(self.pos_y/Enemy.TILE_SIZE) == nearbyEnemy[1]:
                    if self.isValidBombPlacement((int(self.pos_x / Enemy.TILE_SIZE), int(self.pos_y / Enemy.TILE_SIZE)),
                                                 grid):
                        if self.bomb_limit != 0:
                            self.plant = True
                            return
                pathToEnemy = self.path_to_enemy(grid, nearbyEnemy)
                if len(pathToEnemy) != 0:
                    boxesNearby = self.findNearestBox(grid, nearbyEnemy)
                    if abs(boxesNearby[0] - nearbyEnemy[0]) + abs(boxesNearby[1] - nearbyEnemy[1]) > len(pathToEnemy):
                        if self.isValidBombPlacement((int(self.pos_x/Enemy.TILE_SIZE), int(self.pos_y/Enemy.TILE_SIZE)), grid):
                            if self.bomb_limit != 0:
                                self.plant = True
                                return
                    else:
                        self.definePath(pathToEnemy)
                        if self.bomb_limit != 0:
                            self.plant = True
                            return
            self.wander(grid)
        else:
            nearbyEnemies = self.nearby_enemies(grid)
            for nearbyEnemy in nearbyEnemies:
                if int(self.pos_x / Enemy.TILE_SIZE) == nearbyEnemy[0] and int(self.pos_y / Enemy.TILE_SIZE) == \
                        nearbyEnemy[1]:
                    if self.isValidBombPlacement((int(self.pos_x / Enemy.TILE_SIZE), int(self.pos_y / Enemy.TILE_SIZE)),
                                                 grid):
                        if self.bomb_limit != 0:
                            self.plant = True
                            return
                pathToEnemy = self.path_to_enemy(grid, nearbyEnemy)
                if len(pathToEnemy) > 7:
                    if self.bomb_limit != 0:
                        self.plant = True
                        return
                else:
                    print("ATACANDO ATRAVES DO PREDICT")
                    enemySafePoint = self.findNearestSafePoint(grid, nearbyEnemy)
                    if enemySafePoint is not None:
                        ambushEnemy = self.bestPlaceForBomb(enemySafePoint, grid)
                        pathToAmbush = self.astarSearch(grid, ambushEnemy)
                        self.definePath(pathToAmbush)
                        if self.bomb_limit != 0:
                            self.plant
                            return
            self.wander(grid)

        return


    def astarSearch(self, grid, goal):
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]

        Lo = []
        Lc = []

        # Assumindo que ele recebe uma posição, se receber um node dá pa skippar isto
        start_node = grid[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)]
        start_node.weight = start_node.base_weight
        # aqui no start node da pra meter so grid[initpos[0][initPos[1]] no? que isso ja da return a uma node
        Lo.append(start_node)

        while True:

            currentNode = None

            lowestCost = 2500  # Não escalavel a cenas maiores que 1 000 000
            for node in Lo:

                # Ver o f(c) que é o custo mais a manhatan até ao goal
                if node.weight + self.manhattan_distance((node.x, node.y), goal) < lowestCost:  ## MUDAR CASO NAO SEJA
                    lowestCost = node.weight + self.manhattan_distance((node.x, node.y), goal)
                    currentNode = node
                    Lo.remove(node)
            if currentNode is None:
                return []

            if (currentNode.x, currentNode.y) == goal:
                # Calculate Path (Pode nem ser preciso no fim)
                path = []
                ispathing = True
                while ispathing:
                    path.append((currentNode.x, currentNode.y))
                    ispathing = currentNode.parent is not None
                    currentNode = currentNode.parent
                path.reverse()
                if len(path) > 6:
                    return path[:6]
                return path

            for direction in directions:
                newx = direction[0] + currentNode.x
                newy = direction[1] + currentNode.y
                # Verificar se a direcao eh valida

                if grid[newx][newy].value != 0 and grid[newx][newy].value != 4 and grid[newx][
                    newy].value != 7 and grid[newx][newy].value != 6:  # Trocar para acomodar powerups tambem
                    continue
                # TODO não tá a verificar se a direcao ja foi visitada, talvez fazer uma lista de visitados (Ou entao deixar só porque nao vao ser explorados mas vai ser lixado porque a lista vai ficar grande)

                # Criar node de acordo com as cordenadas
                if grid[newx][newy] not in Lc:
                    grid[newx][newy].weight = currentNode.weight + grid[newx][newy].base_weight
                    grid[newx][newy].parent = currentNode

                # Ver se isto já existe em lo e se existir remover o com mais custo
                existe = False
                for node in Lo:
                    if (node.x, node.y) == (newx, newy):
                        existe = True
                        if grid[newx][newy].weight + self.manhattan_distance((newx, newy),
                                                                             goal) < node.weight + self.manhattan_distance(
                            (node.x, node.y), goal):
                            Lo.remove(node)
                            Lo.append(grid[newx][newy])
                        else:
                            # Nao eh adicionado ah lista
                            break

                if not existe and grid[newx][newy] not in Lc:  ## MAS AINDA NAO TENHO 100% CERTEZA
                    Lo.append(grid[newx][newy])
            if currentNode not in Lc:
                Lc.append(currentNode)

    def manhattan_distance(self, node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def is_in_danger(self, grid):
        # Verifica se a posição atual do robô está em uma área que vai explodir
        if grid[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)].value == 7 or grid[int(self.pos_x / Enemy.TILE_SIZE)][int(self.pos_y / Enemy.TILE_SIZE)].value == 3 :
            return True
        return False

    def nearby_enemies(self, grid):
        nearbyEnemies = []
        player_x = int(self.pos_x / Enemy.TILE_SIZE)
        player_y = int(self.pos_y / Enemy.TILE_SIZE)

        # Verifica a área de 3x3 ao redor da posição do jogador
        for dx in range(-4, 5):  # -4, -3, -2 , -1, 0, 1, 2, 3, 4
            for dy in range(-4, 5):  # -4, -3, -2, -1, 0, 1, 2, 3, 4
                nx = player_x + dx
                ny = player_y + dy
                # Verifica se as coordenadas estão dentro dos limites da grid
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    if grid[nx][ny].value == 6:
                        nearbyEnemies.append((nx, ny))
        return nearbyEnemies

    def path_to_enemy(self, grid, enemy):
        return self.astarSearch(grid, enemy)

    def isCornered(self, enemy, grid):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        visitedList = []
        toVisitList = []

        # enemy_pos = ((int(enemy.pos_x / Enemy.TILE_SIZE)), (int(enemy.pos_y / Enemy.TILE_SIZE)))
        enemy_pos = (enemy[0], enemy[1])
        visitedList.append(enemy_pos)

        # Pa cada direcao ver se o sitio é walcable, se sim, adicionar a visited
        counter = 0
        for direction in directions:
            newcell = (enemy_pos[0] + direction[0], enemy_pos[1] + direction[1])

            if grid[newcell[0]][newcell[1]].value == 0 or grid[newcell[0]][newcell[1]].value == 4:
                toVisitList.append(newcell)
                counter += 1

        if counter > 2:
            return False
        elif counter < 2:
            return True

        # Iterar os visitados
        counter = 0
        while toVisitList:
            cell = toVisitList.pop(0)

            cellCounter = 0
            newCellsList = []
            for direction in directions:
                newcell = (cell[0] + direction[0], cell[1] + direction[1])

                if grid[newcell[0]][newcell[1]].value == 0 or grid[newcell[0]][newcell[1]].value == 4:
                    if newcell not in visitedList:
                        newCellsList.append(newcell)
                    cellCounter += 1

            visitedList.append(cell)

            if cellCounter > 2:
                counter += 1
            elif cellCounter <= 2:
                toVisitList.extend(newCellsList)

        if counter > 1:
            return False
        else:
            return True

    def bestPlaceForBomb(self, enemy, grid):
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        bomb_range = self.range

        enemy_pos = ((int(enemy[0] / Enemy.TILE_SIZE)), (int(enemy[1] / Enemy.TILE_SIZE)))
        player_pos = ((int(self.pos_x / Enemy.TILE_SIZE)), (int(self.pos_y / Enemy.TILE_SIZE)))

        killPositions = []

        # Calcular os quadrados em que vale a pena checkar (onde a distancia da bomba ao enemy é menos que o range)
        spotsWorthToCheck = []
        toVisitList = []
        visitedList = []
        toVisitList.append(enemy_pos)
        while toVisitList:
            currentPos = toVisitList.pop(0)
            visitedList.append(currentPos)

            # Se o current node for bloqueante (paredes caixas bombas) nao chegar (é impossivel meter bomba lá)
            if grid[currentPos[0]][currentPos[1]].value == 1 or grid[currentPos[0]][currentPos[1]].value == 2 or \
                    grid[currentPos[0]][currentPos[1]].value == 3:
                continue

            # Se o current não for inimigo adicionar ao WorthToCheck (não se pode meter uma bomba no inimigo)
            if grid[currentPos[0]][currentPos[1]].value != 6:
                spotsWorthToCheck.append(currentPos)

            # Adicionar os descendentes ao toVisitList, se a distancia for o range ou menos
            for direction in directions:
                newNode = (currentPos[0] + direction[0], currentPos[1] + direction[1])

                # Se tiver dentro do range ele adiciona
                if self.manhattan_distance(newNode,
                                      enemy_pos) <= bomb_range - 1 and newNode not in toVisitList and newNode not in visitedList:
                    toVisitList.append(newNode)

        for spot in spotsWorthToCheck:
            bomb_damage = []
            # Calcular damage da bomba
            for direction in directions:
                for i in range(1, bomb_range):

                    newDir = (direction[0] * i, direction[1] * i)
                    newPos = (spot[0] + newDir[0], spot[1] + newDir[1])

                    if grid[newPos[0]][newPos[1]].value == 1 or grid[newPos[0]][newPos[1]].value == 2 or grid[newPos[0]][
                        newPos[1]].value == 3:
                        break

                    bomb_damage.append(newPos)

            # Cria uma nova grid com uma bomba a bloquear o caminho
            newGrid = []
            for line in grid:
                newGrid.append(line.copy())
            newGrid[spot[0]][spot[1]] = 3

            # Calcular sitios para ele ir (depois da bomba se colocada a bloquear o sitio)
            enemy_movement = []
            visitedList = []
            toVisitList.append(enemy_pos)
            while toVisitList:
                currentPos = toVisitList.pop(0)
                visitedList.append(currentPos)

                for direction in directions:
                    newPos = (currentPos[0] + direction[0], currentPos[1] + direction[1])

                    # Se for vazio ou powerup
                    if newGrid[newPos[0]][newPos[1]] == 0 or newGrid[newPos[0]][newPos[1]] == 4 or newGrid[newPos[0]][
                        newPos[1]] == 6:

                        if newPos not in enemy_movement:
                            enemy_movement.append(newPos)
                            if newPos not in toVisitList and newPos not in visitedList:
                                toVisitList.append(newPos)

            # Ver se a lista se sitios para onde o inimigo se pode mover é sublista dos sitios onde a bomba vai fazer damage
            for damage in bomb_damage:
                if damage in enemy_movement:
                    enemy_movement.remove(damage)

            if not enemy_movement:
                killPositions.append(spot)

        for position in killPositions:
            if self.manhattan_distance(position, enemy_pos) < self.manhattan_distance(position, player_pos):
                killPositions.remove(position)

        if killPositions:
            dist = 1000000
            positionToUse = (0, 0)
            for position in killPositions:
                if self.manhattan_distance(position, player_pos) <= dist:
                    dist = self.manhattan_distance(position, player_pos)
                    positionToUse = position

            return positionToUse
        else:

            return enemy_pos

    def nearby_powerUps(self, grid):
        nearbyPowerUps = []
        player_x = int(self.pos_x / Enemy.TILE_SIZE)
        player_y = int(self.pos_y / Enemy.TILE_SIZE)

        # Verifica a área de 3x3 ao redor da posição do jogador
        for dx in range(-4, 5):  # -4, -3, -2 , -1, 0, 1, 2, 3, 4
            for dy in range(-4, 5):  # -4, -3, -2, -1, 0, 1, 2, 3, 4
                nx = player_x + dx
                ny = player_y + dy
                # Verifica se as coordenadas estão dentro dos limites da grid
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    if grid[nx][ny].value == 4:
                        nearbyPowerUps.append((nx, ny))
        return nearbyPowerUps

    def wander(self, grid):
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        currentNode = ((int(self.pos_x / Enemy.TILE_SIZE)), (int(self.pos_y / Enemy.TILE_SIZE)))
        random.shuffle(directions)
        for direction in directions:
            if grid[currentNode[0] + direction[0]][currentNode[1] + direction[1]].value == 0 or \
                    grid[currentNode[0] + direction[0]][currentNode[1] + direction[1]].value == 4:
                self.definePath(self.astarSearch(grid, (currentNode[0] + direction[0], currentNode[1] + direction[1])))
                return
        return

    def isValidBombPlacement(self, pos, grid):

        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        bomb_range = self.range

        movementList = []
        explosionList = []
        toVisitList = []

        # Calcula sitios que a explosao vai afetar
        explosionList.append(pos)
        for direction in directions:
            for i in range(1, bomb_range):

                newDir = (direction[0] * i, direction[1] * i)
                newPos = (pos[0] + newDir[0], pos[1] + newDir[1])
                if 0 <= newPos[0] < len(grid) and 0 <= newPos[1] < len(grid[0]):

                    if grid[newPos[0]][newPos[1]].value == 1 or grid[newPos[0]][newPos[1]].value == 2 or \
                            grid[newPos[0]][newPos[1]].value == 3:
                        break

                    explosionList.append(newPos)

        toVisitList.append(pos)
        while toVisitList:
            currentPos = toVisitList.pop(0)

            for direction in directions:
                newPos = (currentPos[0] + direction[0], currentPos[1] + direction[1])

                # Se for vazio ou powerup
                if grid[newPos[0]][newPos[1]].value == 0 or grid[newPos[0]][newPos[1]].value == 4:

                    if newPos not in movementList:
                        movementList.append(newPos)
                        if newPos not in toVisitList:
                            toVisitList.append(newPos)

        for place in explosionList:
            if place in movementList:
                movementList.remove(place)

        if movementList:
            return True
        else:
            return False
    def findNearestBox(self, grid, pos = None):

        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        visitedList = []
        toVisitList = []

        if pos is None:
            enemy_pos = ((int(self.pos_x / Enemy.TILE_SIZE)), (int(self.pos_y / Enemy.TILE_SIZE)))
        else:
            enemy_pos = (pos[0], pos[1])

        toVisitList.append(enemy_pos)

        while toVisitList:
            currentNode = toVisitList.pop(0)

            for direction in directions:
                newNode = (currentNode[0] + direction[0], currentNode[1] + direction[1])
                if grid[newNode[0]][newNode[1]].value == 2:
                    if currentNode != 3:
                        return currentNode
                if newNode not in visitedList and (
                        grid[newNode[0]][newNode[1]].value == 0 or grid[newNode[0]][newNode[1]].value == 4):
                    toVisitList.append(newNode)

            visitedList.append(currentNode)

    def findNearestSafePoint(self, grid, pos = None):

        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        visitedList = []
        toVisitList = []

        if pos is None:
            enemy_pos = ((int(self.pos_x / Enemy.TILE_SIZE)), (int(self.pos_y / Enemy.TILE_SIZE)))
        else:
            enemy_pos = (pos[0], pos[1])

        toVisitList.append(enemy_pos)

        while toVisitList:
            currentNode = toVisitList.pop(0)

            if grid[currentNode[0]][currentNode[1]].value == 0 or grid[currentNode[0]][currentNode[1]].value == 4:
                return currentNode

            for direction in directions:
                newNode = (currentNode[0] + direction[0], currentNode[1] + direction[1])

                if newNode not in visitedList and (
                        grid[newNode[0]][newNode[1]].value == 0 or grid[newNode[0]][newNode[1]].value == 4 or
                        grid[newNode[0]][newNode[1]].value == 7):
                    toVisitList.append(newNode)

            visitedList.append(currentNode)


    def path_to_powerUp(self, grid, powerUp):
        return self.astarSearch(grid, powerUp)

    def chatgpt5(self, grid):

        if self.is_in_danger(grid):
            safeSpot = self.findNearestSafePoint(grid)
            if safeSpot is not None:
                print("DefinePath1")
                self.definePath(self.astarSearch(grid, safeSpot))
                return
            else:
                return
        else:
            nearbyEnemies = self.nearby_enemies(grid)
            if len(nearbyEnemies) != 0:
                for nearbyEnemy in nearbyEnemies:
                    pathToEnemy = self.path_to_enemy(grid, nearbyEnemy)
                    if len(pathToEnemy) != 0:
                        if self.isCornered(nearbyEnemy, grid):
                            bombPlacement = self.bestPlaceForBomb(nearbyEnemy, grid)
                            path = self.astarSearch(grid, bombPlacement)
                            if path:
                                print("DefinePath2")
                                self.definePath(path)
                                if path[-1] == bombPlacement and self.isValidBombPlacement(bombPlacement,grid) :
                                    if self.bomb_limit != 0:
                                        self.plant = True
                                        return
                        else:
                            print("DefinePath3")
                            self.definePath(pathToEnemy)
                            if pathToEnemy[-1] == nearbyEnemy and self.isValidBombPlacement(nearbyEnemy,grid) :
                                if self.bomb_limit != 0:
                                    self.plant = True
                                    return
                            
            nearbyPowerUps = self.nearby_powerUps(grid)
            if len(nearbyPowerUps) != 0:
                lowestCostPath = None
                lowestCost = 100000
                for powerUp in nearbyPowerUps:
                    pathToPowerUp = self.path_to_powerUp(grid, powerUp)
                    if pathToPowerUp:
                        pathWeight = 0
                        for node in pathToPowerUp:
                            pathWeight += grid[node[0]][node[1]].base_weight
                        if pathWeight < lowestCost:
                            lowestCostPath = pathToPowerUp
                if lowestCostPath is not None and self.path != lowestCostPath:
                    print("DefinePath4")
                    self.definePath(lowestCostPath)
                    return
            box = self.findNearestBox(grid)
            if box is not None:
                pathToBox = self.astarSearch(grid, box)
                if pathToBox:
                    print("DefinePath5")
                    self.definePath(pathToBox)
                    if self.isValidBombPlacement(box, grid) and pathToBox[-1] == box:
                        if self.bomb_limit != 0:
                            self.plant = True
                            return
                else:
                    self.wander(grid)
                    return

            else:
                self.attackEnemy(grid)
                return
        return

    def definePath(self, new_path):
        for xd in range(len(new_path)):
            if new_path[xd] is not new_path[-1]:
                if new_path[xd][0] - new_path[xd + 1][0] == -1:
                    self.movement_path.append(1)
                elif new_path[xd][0] - new_path[xd + 1][0] == 1:
                    self.movement_path.append(3)
                elif new_path[xd][1] - new_path[xd + 1][1] == -1:
                    self.movement_path.append(0)
                elif new_path[xd][1] - new_path[xd + 1][1] == 1:
                    self.movement_path.append(2)
        self.path = new_path

    def create_grid(self, map, bombs, explosions, enemys):
        grid = [[0] * len(map) for r in range(len(map))]

        # 0 - safe
        # 1 - unsafe
        # 2 - destryable
        # 3 - unreachable

        for b in bombs:
            b.get_range(map)
            for x in b.sectors:
                grid[x[0]][x[1]] = 1
            grid[b.pos_x][b.pos_y] = 3

        for e in explosions:
            for s in e.sectors:
                grid[s[0]][s[1]] = 3

        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] == 1:
                    grid[i][j] = 3
                elif map[i][j] == 2:
                    grid[i][j] = 2

        for x in enemys:
            if x == self:
                continue
            elif not x.life:
                continue
            else:
                grid[int(x.pos_x / Enemy.TILE_SIZE)][int(x.pos_y / Enemy.TILE_SIZE)] = 2

        return grid

    def create_chat_grid(self, map, bombs, explosions, power_ups, enemys):
        grid = [[None] * len(map) for r in range(len(map))]
        # 0 - safe
        # 1 - paredes do mapa
        # 2 - caixas
        # 3 - bomba
        # 4 - powerUp
        # 5 - explosao
        # 6 - inimigos
        # 7 - zonas onde vai explodir
        for i in range(len(map)):
            for j in range(len(map)):
                if map[i][j] == 0:
                    grid[i][j] = Node(i, j, True, 1, 0)
                elif map[i][j] == 2:
                    grid[i][j] = Node(i, j, False, 999, 2)
                elif map[i][j] == 1:
                    grid[i][j] = Node(i, j, False, 999, 1)
                elif map[i][j] == 3:
                    grid[i][j] = Node(i, j, False, 999, 3)
                elif map[i][j] == 4:
                    grid[i][j] = Node(i, j, True, 1, 4)

        for b in bombs:
            b.get_range(map)
            for x in b.sectors:
                if grid[x[0]][x[1]].value != 2 and grid[x[0]][x[1]].value != 3:
                    grid[x[0]][x[1]].value = 7
                    grid[x[0]][x[1]].base_weight = 3000 - b.time

        for e in explosions:
            for s in e.sectors:
                grid[s[0]][s[1]].value = 5
                grid[s[0]][s[1]].base_weight = 9999 

        for x in enemys:
            if x == self:
                continue
            elif not x.life:
                continue
            else:
                grid[int(x.pos_x / Enemy.TILE_SIZE)][int(x.pos_y / Enemy.TILE_SIZE)].value = 6

        return grid

    def create_grid_dijkstra(self, map, bombs, explosions, enemys):
        grid = [[None] * len(map) for r in range(len(map))]

        # 0 - safe
        # 1 - destroyable
        # 2 - unreachable
        # 3 - unsafe
        for i in range(len(map)):
            for j in range(len(map)):
                if map[i][j] == 0:
                    grid[i][j] = Node(i, j, True, 1, 0)
                elif map[i][j] == 2:
                    grid[i][j] = Node(i, j, False, 999, 1)
                elif map[i][j] == 1:
                    grid[i][j] = Node(i, j, False, 999, 2)
                elif map[i][j] == 3:
                    grid[i][j] = Node(i, j, False, 999, 2)
                elif map[i][j] == 4:
                    grid[i][j] = Node(i, j, True, 0, 0)

        for b in bombs:
            b.get_range(map)
            for x in b.sectors:
                grid[x[0]][x[1]].weight = 5
                grid[x[0]][x[1]].value = 3
            grid[b.pos_x][b.pos_y].reach = False

        for e in explosions:
            for s in e.sectors:
                grid[s[0]][s[1]].reach = False

        for x in enemys:
            if x == self:
                continue
            elif not x.life:
                continue
            else:
                grid[int(x.pos_x / Enemy.TILE_SIZE)][int(x.pos_y / Enemy.TILE_SIZE)].reach = False
                grid[int(x.pos_x / Enemy.TILE_SIZE)][int(x.pos_y / Enemy.TILE_SIZE)].value = 1
        return grid

    def load_animations(self, en, scale):
        front = []
        back = []
        left = []
        right = []
        resize_width = scale
        resize_height = scale

        image_path = 'images/enemy/e'
        if en == '':
            image_path = 'images/hero/p'

        f1 = pygame.image.load(image_path + en + 'f0.png')
        f2 = pygame.image.load(image_path + en + 'f1.png')
        f3 = pygame.image.load(image_path + en + 'f2.png')

        f1 = pygame.transform.scale(f1, (resize_width, resize_height))
        f2 = pygame.transform.scale(f2, (resize_width, resize_height))
        f3 = pygame.transform.scale(f3, (resize_width, resize_height))

        front.append(f1)
        front.append(f2)
        front.append(f3)

        r1 = pygame.image.load(image_path + en + 'r0.png')
        r2 = pygame.image.load(image_path + en + 'r1.png')
        r3 = pygame.image.load(image_path + en + 'r2.png')

        r1 = pygame.transform.scale(r1, (resize_width, resize_height))
        r2 = pygame.transform.scale(r2, (resize_width, resize_height))
        r3 = pygame.transform.scale(r3, (resize_width, resize_height))

        right.append(r1)
        right.append(r2)
        right.append(r3)

        b1 = pygame.image.load(image_path + en + 'b0.png')
        b2 = pygame.image.load(image_path + en + 'b1.png')
        b3 = pygame.image.load(image_path + en + 'b2.png')

        b1 = pygame.transform.scale(b1, (resize_width, resize_height))
        b2 = pygame.transform.scale(b2, (resize_width, resize_height))
        b3 = pygame.transform.scale(b3, (resize_width, resize_height))

        back.append(b1)
        back.append(b2)
        back.append(b3)

        l1 = pygame.image.load(image_path + en + 'l0.png')
        l2 = pygame.image.load(image_path + en + 'l1.png')
        l3 = pygame.image.load(image_path + en + 'l2.png')

        l1 = pygame.transform.scale(l1, (resize_width, resize_height))
        l2 = pygame.transform.scale(l2, (resize_width, resize_height))
        l3 = pygame.transform.scale(l3, (resize_width, resize_height))

        left.append(l1)
        left.append(l2)
        left.append(l3)

        self.animation.append(front)
        self.animation.append(right)
        self.animation.append(back)
        self.animation.append(left)

    def __str__(self):
        return str(f"{int(self.pos_x/Enemy.TILE_SIZE)}, {int(self.pos_y/Enemy.TILE_SIZE)}")

    def __repr__(self):
        return str(f"{int(self.pos_x/Enemy.TILE_SIZE)}, {int(self.pos_y/Enemy.TILE_SIZE)}")
