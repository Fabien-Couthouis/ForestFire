import numpy as np
import pygame
import pygame.draw
import time
import matplotlib.pyplot as plt

TREE = 0
FIRE = 1
BURNT = 2

__screenSize__ = (600, 600)


def getColorCell(c):
    if c == TREE:
        return (0, 255, 0)
    elif c == FIRE:
        return (255, 0, 0)
    # Burnt
    else:
        return (255, 255, 255)


class Scene:
    "Show the forest fire"

    _grid = None
    _font = None

    def __init__(self, forest):
        pygame.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial', 25)
        self._grid = forest.grid
        self.forest = forest
        self.cellsize = __screenSize__[0] / self._grid.shape[0]

    def drawMe(self):
        self._screen.fill((128, 128, 128))
        for x in range(self._grid.shape[0]):
            for y in range(self._grid.shape[1]):
                pygame.draw.rect(self._screen,
                                 getColorCell(self._grid[x, y]),
                                 (x*self.cellsize + 1, y*self.cellsize + 1, self.cellsize-2, self.cellsize-2))

    def drawText(self, text, position, color=(255, 64, 64)):
        self._screen.blit(self._font.render(text, 1, color), position)

    def update(self):
        self.forest.step()


class Forest():
    """
    Burning forest simulation 

    Attributes:
        n (int): Size of the forest
        num_fires(int): Number of fires at the beggining
        p (float, optional, default=0.5): Probability that an adjacent tree burns

    """

    def __init__(self, n, num_fires, p=0.5):
        self.n = n
        self.grid = np.zeros((self.n, self.n))
        self.johnny(num_fires)
        self.p = p

    def johnny(self, num_fires):
        "Start fire"
        for _fire in range(num_fires):
            xrand, yrand = np.random.randint(0, self.n, 2)
            self.burn(xrand, yrand, 1)

    def burn(self, x, y, p):
        if np.random.random() < p:
            self.grid[x, y] = FIRE

    def step(self):
        grid = np.copy(self.grid)
        for x in range(self.n):
            for y in range(self.n):
                if grid[x, y] == FIRE:
                    # neightbours = [(x-1, y), (x, y-1),
                    #                (x+1, y), (x, y+1)]
                    neighbors = [(x-1, y), (x, y-1),
                                 (x+1, y), (x, y+1), (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)]
                    for xn, yn in neighbors:
                        if self.is_valid(xn, yn) and grid[xn, yn] == TREE:
                            self.burn(xn, yn, self.p)
                            # pass

                    self.grid[x, y] = BURNT

    def is_valid(self, x, y):
        if x < 0 or x >= self.n or y < 0 or y >= self.n:
            return False
        else:
            return True

    def get_nb_tree(self):
        nb_tree = 0
        for x in range(self.n):
            for y in range(self.n):
                if self.grid[x, y] == TREE:
                    nb_tree += 1
        return nb_tree

    def is_over(self):
        for x in range(self.n):
            for y in range(self.n):
                if self.grid[x, y] == FIRE:
                    return False
        return True


def play(forest):
    scene = Scene(forest)
    clock = pygame.time.Clock()
    done = False
    while not done:
        clock.tick(10)
        scene.update()

        scene.drawMe()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

    pygame.quit()


def sim(min_p, max_p, delta=0.1, n=100, num_fires=1, num_episodes_per_run=10):
    """Simulate runs. Return densities list and the list of corresponding percolation rate
        Arguments:
                    min_p (float): Minimum percolation rate
                    max_p (float): Maximum percolation rate
                    delta (float, optional, default=0.1): Difference between two percolation rate to simulate (next_p = old_p + delta)
                    n (int, optional, default=100): Size of the forest
                    num_fires (int, optional, default=1): Number of fires at the beggining
                    num_episodes_per_run (int, optional, default=10): Number of episodes per run
        """

    densities_list, p_list = [], []
    p = min_p
    while p < max_p:
        for _episode in range(num_episodes_per_run):
            nb_tree_list = []
            forest = Forest(n, num_fires, p)
            while not forest.is_over():
                forest.step()
            nb_tree_list.append(forest.get_nb_tree())

        densities_list.append(np.mean(nb_tree_list))
        p_list.append(p)
        p += delta
        nb_tree_list.clear()

    gride_size = n*n
    densities_list = np.divide(densities_list, gride_size)
    return densities_list, p_list


def plot(densities_list, p_list):
    plt.plot(p_list, densities_list)
    plt.ylabel("Tree density")
    plt.xlabel("Burning probability of adjacent trees")
    plt.title("Tree density in function of adjacent trees burning probability")

    plt.show()


if __name__ == "__main__":
    # forest = Forest(200, 1, p=0.3)
    # play(forest)

    densities_list, p_list = sim(
        0, 1, delta=0.01, n=100, num_fires=1, num_episodes_per_run=5)

    plot(densities_list, p_list)
