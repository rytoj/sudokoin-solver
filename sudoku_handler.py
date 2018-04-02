#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Pierre Haessig October 2011
"""
Sudoku Solver
=============

A quick hobby Python program to represent
and (attempt to) solve the classic Sudoku game

see README.rst for more information
"""

from __future__ import division, print_function
import os.path

try:
    from termcolor import colored
except ImportError:
    pass
    # print('Warning: termcolor module is needed to add some fancyness!')


    def colored(text, color=None, on_color=None, attrs=None):
        '''dummy colored function'''
        return text


class Cell(object):
    """represents a Sudoku cell"""

    # all available possibilities in a the cell :
    all_possibilities = set(range(1, 10))  # = {1:9}

    def __init__(self, pos, solution=None):
        """pos = (a0,a1) is the cell position in the grid
        solution : [optional] sets the content of the cell
                   (creates a solved cell)
        """
        assert len(pos) == 2
        self.pos = pos
        self.possibilities = self.all_possibilities.copy()

        if solution is not None:
            assert solution in self.all_possibilities
            # keep only the solution
            self.keep_possibilities(set([solution]))

    def remove_possibilities(self, rm_set):
        """remove a set of possibilities

        - returns True if there was strict decrease in
        the size of possibilities set
        - returns False if rm_set has no elements in common with
        possibilities set

        See also : keep_possibilities
        """
        if self.possibilities.isdisjoint(rm_set):
            return False
        else:
            self.possibilities -= rm_set
            if len(self.possibilities) < 1:
                raise ValueError("Removing %s from Cell %s makes it empty!" %
                                 (rm_set, self.pos))
            return True

    # end remove_possibilities

    def keep_possibilities(self, kp_set):
        """ keep only a given set of possibilities `kp_set`
        The remaining possibilities are then the intersection of
        1. previously available possibilities
        2. `kp_set`

        (ValueError is raised if the intersection is empty)

        - returns True if there was strict decrease in
        the size of possibilities set
        - returns False if rm_set has no elements in common with
        possibilities set

        See also : remove_possibilities
        """
        # 1) Check for empty intersection:
        if self.possibilities.isdisjoint(kp_set):
            raise ValueError("Keeping only %s from Cell %s makes it empty!" %
                             (kp_set, self.pos))
        # 2) Do the job:
        if self.possibilities.issubset(kp_set):
            # nothing to do
            return False
        else:
            # Strict decrease in the number of available possibilities
            self.possibilities.intersection_update(kp_set)
            return True

    # end keep_possibilities

    def is_solved(self):
        """is the cell in a solved state, that is
        there is just one possibility"""
        return len(self.possibilities) == 1

    def solution(self):
        """returns the cell solution, if available
        else returns None"""
        if self.is_solved():
            return tuple(self.possibilities)[0]
        else:
            return None

    def __str__(self):
        """string of the solution, or "." if Cell is unsolved"""
        sol = self.solution()
        if sol is None:
            return "."
        else:
            return str(sol)

    def __repr__(self):
        sol = self.solution()
        if sol is None:
            return 'Cell((%d,%d))' % self.pos
        else:
            return 'Cell((%d,%d), %s)' % (self.pos + (str(sol),))


class Sudoku(object):
    """represent the Sudoku game"""
    # size of the Sudoku grid
    grid_size = (9, 9)
    # size of the subblocks :
    block_size = (3, 3)

    def __init__(self, input_game=None, debug=False):
        """input_game : filename of a file to load the game from
                        if None, Sudoku starts completely unsolved"""
        (N0, N1) = self.grid_size

        # 1) Read the input, if any
        input_str = None
        if input_game is not None:
            meaningful_chr = '123456789.'
            self.sudoku_file = input_game
            with open(input_game) as f:
                input_str = f.read()
            # filter out blanks and formatting characters
            input_str = [ch for ch in input_str
                         if ch in meaningful_chr]
            if len(input_str) == N0 * N1:  # 81
                if debug:
                    print('Sudoku "%s" successfully loaded' %
                          os.path.basename(self.sudoku_file))
            else:
                raise ValueError('Input game "%s" is of wrong size '
                                 '(should contain %d meaninful symbols instead of %d)' %
                                 (os.path.basename(self.sudoku_file),
                                  N0 * N1, len(input_str))
                                 )
        else:
            self.sudoku_file = ''
        # All the 9*9 cells are stored in a list :
        self.cells = []
        # Populate the list:
        for a0 in range(N0):
            for a1 in range(N1):
                sol = None
                if input_str is not None:
                    sol = input_str[a0 * N0 + a1]
                    try:
                        sol = int(sol)
                        # print('(%d,%d) = %d' % (a0, a1, sol))
                    except ValueError:
                        # sol is not a number. Just skip
                        sol = None
                cell = Cell((a0, a1), solution=sol)
                self.cells.append(cell)
        if debug:
            print(' number of solved cells at startup : %d/81' %
              len([c for c in self.cells if c.is_solved()]))

    # end __init__

    def get_cell(self, a0, a1):
        """get the cell at row `a0` and column a1
        (for interactive use only)
        """
        (N0, N1) = self.grid_size
        assert 0 <= a0 < N0
        assert 0 <= a1 < N1

        c_list = [c for c in self.cells
                  if (c.pos[0] == a0 and c.pos[1] == a1)]

        return c_list[0]

    def get_row_set(self, a0):
        """get the list of cells at row a0"""
        return [c for c in self.cells if c.pos[0] == a0]

    def get_col_set(self, a1):
        """get the list of cells at column a1"""
        return [c for c in self.cells if c.pos[1] == a1]

    def get_block_set(self, block_pos):
        """get the list of cell in the macro-block (A0,A1)"""
        assert len(block_pos) == 2
        (A0, A1) = block_pos
        # print("macro block (%d,%d)" % block_pos)
        return [c for c in self.cells if c.pos[0] // 3 == A0 and c.pos[1] // 3 == A1]

    def get_set(self, n):
        '''get the list of cell corresponding to set number n.
        This is the generic function to return any type of cell set.

        Cell sets are classified as follows :
         * n =  0 to  8  : corresponds to row 0 to 8
         * n =  9 to 17  : corresponds to column 0 to 8
         * n = 18 to 26  : corresponds to macro-block 0 to 8
        '''
        (N0, N1) = self.grid_size
        set_type = n // N0
        assert set_type in set([0, 1, 2])

        if set_type == 0:
            # returns a row
            return self.get_row_set(a0=n)

        if set_type == 1:
            # returns a colum
            return self.get_col_set(a1=n - N0)

        if set_type == 2:
            # returns a macro block
            block_number = n - N0 - N1
            block_pos = (block_number % 3, block_number // 3)
            return self.get_block_set(block_pos)

    # end get_set

    def find_solved_groups(self, cell_list):
        """find solved groups in the list of cells `cell_list`
        Returns a list of tuple pairs defined the following way :
         (set of solved numbers,
          list of the corresponding group of solved Cells)

        Solved groups are composed either of
          * one cell that contain one possibility.
            This cell is *fully solved*
          * two/three/four cells that contain
            two/three/four identical possibilities.
            These cells are only *partially solved* but we know for sure that
            their possibilities can't be used in an cell *outside* the group.
        """
        possibilities = [(c.possibilities, c) for c in cell_list
                         if len(c.possibilities) <= 4]

        solved_groups = []
        for n_pos in range(1, 5):
            # print('Finding groups of length %d...' % n_pos)
            groups_n = []  # TODO : remove the groups_n variable which is useless
            pos_n = [(pi, ci) for (pi, ci) in possibilities
                     if len(pi) == n_pos]

            # Special case of fully solved Cells:
            if n_pos == 1:
                groups_n = [(pi, [ci]) for (pi, ci) in pos_n]
                solved_groups.extend(groups_n)
                continue

            # Partially solved Cell: (n_pos>1)
            # simple draft search algorithm
            for i in range(len(pos_n) // 2):
                pi, ci = pos_n[i]
                group_i = [ci]
                for j in range(i + 1, len(pos_n)):
                    pj, cj = pos_n[j]
                    if pi == pj:
                        # print('Cells %s and %s are twins!' % (ci.pos,cj.pos))
                        group_i.append(cj)
                if len(group_i) == n_pos:
                    groups_n.append((pi, group_i))
                    # print('Solved group of length %d:' % n_pos)
                    # print((pi,group_i))
            if len(groups_n) > 0:
                solved_groups.extend(groups_n)
        return solved_groups

    def find_solved_placements(self, cell_list):
        '''find where numbers must be placed due to the rule of surjectivity

        Returns a list of tuple pairs defined the following way :
         (set of numbers to be placed,
          set of Cells where to place those numbers)
        '''
        solved_placements = []
        # Find all possible placements
        possible_placements = list((poss, set(cell for cell in cell_list
                                              if poss in cell.possibilities))
                                   for poss in Cell.all_possibilities)
        # Filter placements that are solved
        for n_pos in range(1, 5):
            places_n = [(poss, cells)
                        for poss, cells in possible_placements
                        if len(cells) == n_pos]

            # 1) Special case of fully solved placements:
            if n_pos == 1:
                solved_placements.extend([(set([poss]), cells)
                                          for poss, cells in places_n
                                          if not tuple(cells)[0].is_solved()])
                continue

            # 2) Partially solved placements: (n_pos>1)
            # Search for identical placement possibilities
            for i in range(len(places_n) // 2):
                pi, cells_i = places_n[i]
                poss_group_i = set([pi])
                for j in range(i + 1, len(places_n)):
                    # look for identical cells
                    pj, cells_j = places_n[j]
                    if cells_i == cells_j:
                        poss_group_i.add(pj)
                if len(poss_group_i) == n_pos:
                    # the group is of proper length
                    solved_placements.append((poss_group_i, cells_i))

        return solved_placements

    def process_set(self, n):
        """Apply the Sudoku Rules to the Cell set `n`
        (see Sudoku.get_set(n))
        It enforces both :
         * "Injectivity" : remove possibilities which are fully/partially solved
           (with the help of `find_solved_groups` method)
         * "Surjectivity" : enforce the placement of numbers which must be
           (with the help of `find_solved_placements` method)

        Returns True if there was some progress in the elimination process
                False otherwise
        """
        cell_list = self.get_set(n)
        # 1a) Find groups that are already solved:
        solved_groups = self.find_solved_groups(cell_list)

        # 1b) Find placements that are already solved:
        solved_placements = self.find_solved_placements(cell_list)

        nb_progress = 0

        # 2a) Apply Injectivity Rule
        for c in cell_list:
            if c.is_solved() or not (solved_groups):
                continue

            # Filter what are the wrong possibilities for cell `c`
            wrong_poss = [poss_i
                          for poss_i, group_i in solved_groups
                          if not c in group_i]

            # merge the sets of wrong possibilities:
            wrong_poss = wrong_poss[0].union(*wrong_poss[1:])
            # Remove the wrong possibilities from cell `c` :
            nb_progress += int(c.remove_possibilities(wrong_poss))

        # 2b) Surjectivity Rule
        # placement enforcement with c.keep_possibilities()
        for poss_i, group_i in solved_placements:
            for cell in group_i:
                nb_progress += int(cell.keep_possibilities(poss_i))

        # print('Number of cells that got some progress : %d' % nb_progress)
        return nb_progress > 0

    # end process_set

    def process_all_sets(self):
        """apply the Sudoku exclusion rules *once* to each Cell set of the grid

        Returns True if there was some progress in the elimination process
                False otherwise
        """
        progress = False
        for n in range(9 + 9 + 9):
            progress |= self.process_set(n)
        return progress

    # end process_all_sets

    def solve_game(self, max_iter=20):
        '''(attempt to) solve the Sudoku game

        It works by calling iteratively the `process_all_sets` method
        until there is no more progress OR until `max_iter` is reached

        Returns (is_solved, nb_iter) with
         * is_solved : boolean flag for success
         * nb_iter : (int) number of iterations used to solve the game
        '''
        # TODO : add timing information
        for nb_iter in range(1, max_iter + 1):
            progress = self.process_all_sets()
            if not progress:
                # Stop working if there is no more progress
                nb_iter -= 1
                print('No more progress after %d iterations' % nb_iter)
                break
        else:
            print('Maximum number of iteration (%d) reached !' % max_iter)
        # Check if we solved the game
        is_solved = all(c.is_solved() for c in self.cells)
        if is_solved:
            print('Sudoku successfully solved !')
        else:
            print('Unable to solve the Sudoku :-(')
        # Report back:
        return (is_solved, nb_iter)

    def __str__(self):
        """visual text representation of the Sudoku grid at current state
        Note : this function assumes block_size == (3,3)
        and grid width being 9 (that is the usual Sudoku format)
        """
        (N0, N1) = self.grid_size
        s = ""
        for a0 in range(N0):
            if a0 % 3 == 0 and a0 != 0:
                s += '\n'
            str_list = [str(c) for c in self.get_row_set(a0)]
            s += ''.join(str_list[0:3]) + '  ' + \
                 ''.join(str_list[3:6]) + '  ' + \
                 ''.join(str_list[6:9]) + '\n'
        s += '\n'
        # end for
        return s

    # end __str__

    def print_grid(self):
        """displays the Sudoky grid, in a fancier way than print()"""
        (N0, N1) = self.grid_size
        s = "Sudoku grid '%s':\n\n" % os.path.basename(self.sudoku_file)
        for a0 in range(N0):
            if a0 % 3 == 0 and a0 != 0:
                s += '------+-------+------\n'
            str_list = [str(c) for c in self.get_row_set(a0)]
            s += ' '.join(str_list[0:3]) + ' | ' + \
                 ' '.join(str_list[3:6]) + ' | ' + \
                 ' '.join(str_list[6:9]) + '\n'
        s += '\n\nNumber of solved cells : %d/81' % \
             len([c for c in self.cells if c.is_solved()])

        print(s)

    # end print_grid

    def print_all_possibilities(self):
        """displays the Sudoky grid,
        with all the available possibilities in each cell
        """
        (N0, N1) = self.grid_size
        # Display colors, depending on the number of remaining possibilities:
        colors = {1: 'green', 2: 'cyan'}
        print("Sudoku grid '%s':\n" % os.path.basename(self.sudoku_file))
        for a0 in range(N0):
            if a0 % 3 == 0 and a0 != 0:
                print('------------+-------------+------------')
            # Get all possibilities for each cell in the current row:
            str_list = [''.join(str(p) for p in c.possibilities)
                        for c in self.get_row_set(a0)]
            # prepare the color to use for each cell:
            color_list = [colors.get(len(s)) for s in str_list]
            # pad all the possibilities strings to fixed with 9
            str_list = [s.center(9) for s in str_list]
            # Split the possibilities into three lines:
            for i in range(3):
                # Select 3 possibilities for each Cell:
                str_list_i = [s[3 * i:3 * i + 3] for s in str_list]
                # Add the color control characters:
                str_list_i = [colored(s, color)
                              for s, color in zip(str_list_i, color_list)]
                print(' '.join(str_list_i[0:3]) + ' | ' + \
                      ' '.join(str_list_i[3:6]) + ' | ' + \
                      ' '.join(str_list_i[6:9]))
        print('\nNumber of solved cells : %d/81' %
              len([c for c in self.cells if c.is_solved()]))


    def print_nb_possibilities(self):
        """displays the number of remaining possibilities in each cell
        a `'` means the cell is solved (that is only one remaining possibility)
        """
        (N0, N1) = self.grid_size
        print("Number of remaining possibilities :\n")
        for a0 in range(N0):
            if a0 > 0 and a0 % 3 == 0:
                print('')
            str_list = [str(len(c.possibilities)) for c in self.get_row_set(a0)]
            str_list = ['\'' if char == '1' else char for char in str_list]
            s = ''.join(str_list[0:3]) + '  ' + \
                ''.join(str_list[3:6]) + '  ' + \
                ''.join(str_list[6:9]) + '  '
            print(s)
        print('\nNumber of solved cells : %d/81' %
              len([c for c in self.cells if c.is_solved()]))


if __name__ == '__main__':
    print("Sudoku solver program")
    print("-" * 21 + '\n')
    sudoku_file = 'unsolved.txt'
    S = Sudoku(sudoku_file)
    print('Sudoku grid "%s":\n' % os.path.basename(sudoku_file))
    print(S)
    S.process_all_sets()
    S.process_all_sets()
    S.process_all_sets()
    S.process_all_sets()
    print('Sudoku grid "%s" after 3 iterations:\n' % os.path.basename(sudoku_file))
    print(S)
