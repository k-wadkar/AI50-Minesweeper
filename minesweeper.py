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
        '''
        Takes a cell as input, along with the number of mines known to be neighbouring that cell
        Produces a set of all cells that neighbour the input cell
        Removes cells from the set if they are already known to be safes or mines and updates count accordingly
        Based on the remaining number of cells in the set and count value:
            If the number of neighbouring cells equal the number of remaining mines around the cell
                Then mark all remaining neighbours as mines and return an empty set
            If the number of mines in the remaining set if zero
                Then mark all remaining neighbours as safes and return an empty set
            Else
                Return a sentence containing the remaining neighbours against the remaining mine count
        '''
        
        # Set to contain coordinates of all neighbouring cells of which the status is uncertain
        # (i.e. we don't know if it is safe or a mine)
        cellNeighbours = set()

        # Adds all possible neighbouring cells to the set, given the input cell's location
        # (i.e. it is not possible for a cell in the top row to have a neighbour above it, etc.)
        # top left
        if cell[0] > 0 and cell[1] > 0:
            cellNeighbours.add((cell[0]-1, cell[1]-1))
        # top centre
        if cell[0] > 0:
            cellNeighbours.add((cell[0]-1, cell[1]))
        # top right
        if cell[0] > 0 and cell[1] < self.width-1:
            cellNeighbours.add((cell[0]-1, cell[1]+1))
        # middle left
        if cell[1] > 0:
            cellNeighbours.add((cell[0], cell[1]-1))
        # middle right
        if cell[1] < self.width-1:
            cellNeighbours.add((cell[0], cell[1]+1))
        # bottom left
        if cell[0] < self.height-1 and cell[1] > 0:
            cellNeighbours.add((cell[0]+1, cell[1]-1))
        # bottom centre
        if cell[0] < self.height-1:
            cellNeighbours.add((cell[0]+1, cell[1]))
        # bottom right
        if cell[0] < self.height-1 and cell[1] < self.width-1:
            cellNeighbours.add((cell[0]+1, cell[1]+1))

        # Deepcopy made as changing a set within the loop causes an error
        neighboursCopy = deepcopy(cellNeighbours)

        # If a neighbour is already known to be a mine or safe, it is removed from the set and count is changed accordingly
        for individualCell in cellNeighbours:
            if individualCell in self.mines:
                neighboursCopy.remove(individualCell)
                count -= 1
            if individualCell in self.safes:
                neighboursCopy.remove(individualCell)

        # cellNeighbours now updated to exclude known mines and safes
        cellNeighbours = deepcopy(neighboursCopy)
        # If every remaining neighbour is known to be a safe
        if count == 0:
            # Add all neighbours to safes and return none
            for neighbour in cellNeighbours:
                self.mark_safe(neighbour)
            return Sentence(set(), None)
        # If every remaining neighbour is known to be a mine
        elif count == len(cellNeighbours):
            # Add all neighbours to mines and return none
            for neighbour in cellNeighbours:
                self.mark_mine(neighbour)
            return Sentence(set(), None)
        else:
            # Otherwise just return a sentence of neighbour cells against number of mines
            return Sentence(cellNeighbours, count)

    def knowledge_cleanup(self):
        '''
        Removes duplicate sentences in self.knowledge
        Removes empty sentences
        '''
        # Will contain exactly one copy of the sentences which appear more than once in self.knowledge
        badList = []
        # Will contain exactly one copy of the sentences which appear only once in self.knowledge
        goodList = []

        # For each sentence in self.knowledge
        for sentenceNum in range(len(self.knowledge)):
            # For each sentence between the currently selected sentence and the end of self.knowledge
            for nestedSentenceNum in range(sentenceNum+1, len(self.knowledge)):
                # If the two selected sentences have the same cells and the sentence does not already appear in badlist, add to badlist
                if self.knowledge[sentenceNum].cells == self.knowledge[nestedSentenceNum].cells and self.knowledge[sentenceNum] not in badList:
                    badList.append(self.knowledge[sentenceNum])
        
        # For each sentence not in badlist (i.e. sentences which only appeared once) add to goodlist
        for sentence in self.knowledge:
            if sentence not in badList:
                goodList.append(sentence)
        
        # Set self.knowledge equal to goodlist plus badlist (i.e. the list containing exactly one copy of each sentence)
        self.knowledge = deepcopy(goodList+badList)

        # Removes empty sentences
        for sentence in self.knowledge:
            if sentence.count == len(sentence.cells):
                for cell in list(sentence.cells):
                    self.mark_mine(cell)
                self.knowledge.remove(sentence)
            elif sentence.count == 0:
                for cell in list(sentence.cells):
                    self.mark_safe(cell)
                self.knowledge.remove(sentence)            

    def blanket_set_subtraction(self):
        # Set subtraction
        originalLength = len(self.knowledge)
        # Loops thorugh all sets in knowledge
        for sentenceNum in range(len(self.knowledge)):
            firstSet = self.knowledge[sentenceNum]
            
            # Loops through all sets between the current set and the end of knowledge
            for nestedSentenceNum in range(sentenceNum+1, originalLength):
                secondSet = self.knowledge[nestedSentenceNum]
                # If the first set is a subset of the second...
                if firstSet.cells.issubset(secondSet.cells):
                    sentenceAlreadyAdded = False
                    
                    for sentence in self.knowledge:
                        if sentence.cells == secondSet.cells.difference(firstSet.cells):
                            sentenceAlreadyAdded = True
                    
                    # And the symmetric difference between the sets has not already been added to knowledge...
                    if not sentenceAlreadyAdded:
                        # Add the symmetric difference to knowledge
                        self.knowledge.append(Sentence(secondSet.cells.difference(
                            firstSet.cells), secondSet.count-firstSet.count))
                
                # Otherwise if the second set is a subset of the first...
                elif secondSet.cells.issubset(firstSet.cells):
                    sentenceAlreadyAdded = False

                    for sentence in self.knowledge:
                        if sentence.cells == firstSet.cells.difference(secondSet.cells):
                            sentenceAlreadyAdded = True
                    
                    # And the symmetric difference between the sets has not already been added to knowledge...
                    if not sentenceAlreadyAdded:
                        # Add the symmetric difference to knowledge
                        self.knowledge.append(Sentence(firstSet.cells.difference(
                            secondSet.cells), firstSet.count - secondSet.count))

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
        # Marks the input cell as a move that has been made
        self.moves_made.add(cell)

        # Marks the input cell as a safe cell
        self.mark_safe(cell)

        # Contains a sentence regarding neighbours to the input cell, of which we are not sure of the status
        # (i.e we don't know if the neighbours are mines or safes)
        uncertainNeighbours = deepcopy(self.find_uncertain_neighbours(cell, count))

        # If there are neighbouring cells which we don't already know the state of
        # AND we don't know for sure based on count whether or not they are mines 
        if uncertainNeighbours.count != None:
            # Add a sentence based on this information to self.knowledge
            self.knowledge.append(uncertainNeighbours)

        # Remove duplicates and empty sentences from self.knowledge
        self.knowledge_cleanup()

        # Runs set subtraction on all sets in self.knowledge
        self.blanket_set_subtraction()

        # Runs again, this time not to check for duplicates or empty cells,
        # but to check if subtraction resulted in any additional mines/safes (and mark them)
        self.knowledge_cleanup()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        untouchedSafes = self.safes.difference(self.moves_made)
        
        for safe in untouchedSafes:
            return safe

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        while True:
            randomCoords = (random.randrange(self.height), random.randrange(self.width))

            if randomCoords not in self.moves_made and randomCoords not in self.mines:
                return randomCoords
