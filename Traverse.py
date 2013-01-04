import sublime
import sublime_plugin

# Constants
STEP = 1000

# Shared state
stopRequested = False
move = None


class TraverseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit

        # initialize values
        self.init()

        # Start loop
        self.update()

    def init(self):
        self.pos = [0, 0]
        self.prev_pos = self.pos
        self.stopRequested = False

        # Place us at the end of the first line, ignoring whitespace
        self.pos[0] = len(self.view.substr(self.view.line(0)).strip())

        # Pad the first line
        self.pad_line(self.pos[1])

    def update(self):
        global move

        if (stopRequested):
            return

        dir = 0

        # Handle movement
        if (move == 'right'):
            dir = 1
        elif (move == 'left'):
            dir = -1

        # Check for wall in direction of movement
        wall = self.char_at(self.pos[0] + dir, self.pos[1])
        isOpen = (wall == ' ' or wall == '\n')

        # Move if no wall
        if (isOpen):
            # Always keep an open space next to us (avoid overwriting \n)
            self.pad_line(self.pos[1])
            self.pos[0] += dir

        # Clear movement
        move = None

        # erase old position
        self.draw_at(' ', self.prev_pos)

        # move to new position
        self.draw_at('@', self.pos)

        # clone the old position
        self.prev_pos = list(self.pos)

        # Pad the next line
        self.pad_line(self.pos[1] + 1)

        # Get character below us
        floor = self.char_at(self.pos[0], self.pos[1] + 1)

        if (floor == '\0'):
            print 'done'
            return

        # Check if open
        isOpen = (floor == ' ')

        # apply gravity if no floor
        if (isOpen):
            self.pos[1] += 1

        # Continue loop
        sublime.set_timeout(self.update, STEP)

    # Get character at position in vector or x,y form
    def char_at(self, xpos, ypos=None):
        if ypos is None:
            return self.char_at(xpos[0], xpos[1])

        return self.view.substr(self.view.text_point(ypos, xpos))

    # Draw character at position in vector or x,y form
    def draw_at(self, char, xpos, ypos=None):
        if ypos is None:
            return self.draw_at(char, xpos[0], xpos[1])

        pt = self.view.text_point(ypos, xpos)
        self.view.replace(self.edit, sublime.Region(pt, pt + 1), char)

    # Add proper whitespace to specified line
    def pad_line(self, row):
        # find point at beginning of line
        line_pt = self.view.text_point(row, 0)

        # get the region for this line
        line = self.view.line(line_pt)

        # get the contents of the line (w/o newline)
        line_contents = self.view.substr(line)

        # is the line too short?
        if (len(line_contents) <= self.pos[0] + 1):
            # find the difference
            diff = self.pos[0] - len(line_contents) + 2

            # make the right padding
            pad = ''
            for i in range(diff):
                pad += ' '

            # replace line with padding
            self.view.replace(self.edit, line, line_contents + pad)


# Move left or right
class MoveTraverseCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):
        global move
        move = direction


# Stop the game loop
class StopTraverseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print 'stop'

        global stopRequested
        stopRequested = True
