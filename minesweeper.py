import itertools
import random
from copy import deepcopy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set() 

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        for iterableCell in self.cells:
            if iterableCell == cell:
                self.count -= 1
                self.cells.remove(cell)
                break

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        for iterableCell in self.cells:
            if iterableCell == cell:
                self.cells.remove(cell)
                break


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def find_uncertain_neighbours(self, cell, count):
        cellNeighbours = set()

        # top left
        if cell[0] > 0 and cell [1] > 0:
            cellNeighbours.add((cell[0]-1, cell[1]-1))
        # top centre
        if cell[0] > 0:
            cellNeighbours.add((cell[0]-1, cell[1]))
        # top right
        if cell[0] > 0 and cell [1] < self.width-1:
            cellNeighbours.add((cell[0]-1, cell[1]+1))
        # middle left
        if cell [1] > 0:
            cellNeighbours.add((cell[0], cell[1]-1))
        # middle right
        if cell[1] < self.width-1:
            cellNeighbours.add((cell[0], cell[1]+1))
        # bottom left
        if cell[0] < self.height-1 and cell [1] > 0:
            cellNeighbours.add((cell[0]+1, cell[1]-1))
        # bottom centre
        if cell[0] < self.height-1:
            cellNeighbours.add((cell[0]+1, cell[1]))
        # bottom right
        if cell[0] < self.height-1 and cell[1] < self.width-1:
            cellNeighbours.add((cell[0]+1, cell[1]+1))

        neighboursCopy = deepcopy(cellNeighbours)

        for individualCell in cellNeighbours:
            if individualCell in self.mines:
                neighboursCopy.remove(individualCell)
                count -= 1
            if individualCell in self.safes:
                neighboursCopy.remove(individualCell)

        return Sentence(neighboursCopy, count)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            Done
            2) mark the cell as safe
            Done
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            Done
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            Done?
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge

        """
        # Marks the cell as a move that has been made
        self.moves_made.add(cell)


        # Marks the cell as a safe cell
        self.mark_safe(cell)


        # Finds the set of all neighbouring cells which have not yet been explored
        # (Along with the number of mines known to be in that set) 
        cachedLocalKnowledge = deepcopy(self.knowledge) #Create a copy of localknowledge before it is altered
        self.knowledge.append(self.find_uncertain_neighbours(cell, count))


        # If we know the locations of specific mines in the unexplored set
        sentCopy = deepcopy(self.find_uncertain_neighbours(cell, count))
            # If the number of neighbouring cells = number of neighbouring mines then mark cells as mines
        if len(self.find_uncertain_neighbours(cell, count).known_mines()) != 0:
            for mine in self.find_uncertain_neighbours(cell, count).known_mines():
                self.mines.add(mine)
                sentCopy.cells.remove(mine)
                sentCopy.count -= 1
            
            #Vice versa for neighbouring safes
        if len(self.find_uncertain_neighbours(cell, count).known_safes()) != 0:
            for safe in self.find_uncertain_neighbours(cell, count).known_safes():
                self.safes.add(safe)
                sentCopy.cells.remove(safe)


        # Now for set subtraction...
        for iterableSentence in cachedLocalKnowledge:
            # If there exists a sentence in knowledge which contains a cell set which is a subset 
            if iterableSentence.cells.issubset(sentCopy.cells):
                newSet = sentCopy.cells.difference(iterableSentence.cells)
                newCount = sentCopy.count - iterableSentence.count
                
                self.knowledge.append(Sentence(newSet, newCount))

            if sentCopy.cells.issubset(iterableSentence.cells):
                newSet = iterableSentence.cells.difference(sentCopy.cells)
                newCount = iterableSentence.count - sentCopy.count

                self.knowledge.append(Sentence(newSet, newCount))

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        raise NotImplementedError
