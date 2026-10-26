# =============================================================
#  DEEP DIVE  -  main.py
#
#  You are the captain of a submarine. Find all the treasure,
#  dodge the hidden mines, and get back to the surface before
#  your oxygen runs out.
#
#  YOUR MISSION: complete all 15 "YOU TRY" challenges.
#  Save the file and refresh the page after each one to test it.
#
#  Where do print() messages go?
#  They appear in the browser console, not on the page.
#  Open it with:  Cmd + Option + J  (Mac)  or  Ctrl + Shift + J  (Windows)
# =============================================================

import random
from pyscript import document, window

# The ocean is a grid: 8 squares across (x) and 6 squares deep (y).
#
#          x=0   x=1   x=2   ...   x=7
#   y=0   [   ] [   ] [   ]       [   ]   <- the surface (fresh air!)
#   y=1   [   ] [   ] [   ]       [   ]
#   ...
#   y=5   [   ] [   ] [   ]       [   ]   <- the sea floor
#
# Going RIGHT makes x bigger. Going DOWN makes y bigger.
COLS = 8
ROWS = 6


# -------------------------------------------------------------
#  HELPERS - already done for you. Read them, but don't change them.
# -------------------------------------------------------------

def show(element_id, text):
    """Put text on the page inside the element with this id."""
    document.getElementById(element_id).innerText = str(text)


def status(message):
    """Show a message in the bar under the ocean."""
    show("status-text", message)


def log(message, kind="info"):
    """Show a message AND write it in the Captain's log.
    kind can be "info", "good" or "bad"."""
    status(message)
    entry = document.createElement("div")
    entry.className = "log-entry " + kind
    entry.innerHTML = '<span class="log-time"></span><span class="log-text"></span>'
    entry.querySelector(".log-time").innerText = "T+" + str(moves).zfill(2)
    entry.querySelector(".log-text").innerText = message
    document.getElementById("log").prepend(entry)


def input(question=""):
    """Normal input() doesn't work on a webpage, so this version shows a
    pop-up box instead. You use it exactly like the normal input()."""
    try:
        answer = window.prompt(question)
    except Exception:
        answer = None  # some browsers block pop-ups
    if not answer:
        return "Nemo"
    return answer


def keep_in_range(number, low, high):
    """Keep a number between low and high."""
    if number < low:
        return low
    if number > high:
        return high
    return number


def empty_spot(taken):
    """Pick a random square under the water that isn't in the list 'taken'.
    It's never right next to where the sub starts, so the first move is safe."""
    while True:
        spot = [random.randint(0, COLS - 1), random.randint(1, ROWS - 1)]
        next_to_start = spot[0] <= 1 and spot[1] <= 1
        if spot not in taken and not next_to_start:
            return spot


def draw_ocean():
    """Draw every square of the ocean, then move the sub."""
    global last_x
    html = ""
    for y in range(ROWS):
        for x in range(COLS):
            spot = [x, y]
            classes = "cell"
            if spot in visited:
                classes = classes + " visited"
            if spot in treasures:
                classes = classes + " treasure"
            if spot in found_mines:
                classes = classes + " wreck"
            html = html + '<div class="' + classes + '"></div>'
    document.getElementById("ocean").innerHTML = html

    sub = document.getElementById("sub")
    if sub_x < last_x:
        sub.dataset.facing = "left"
    elif sub_x > last_x:
        sub.dataset.facing = "right"
    last_x = sub_x
    sub.style.setProperty("--x", str(keep_in_range(sub_x, 0, COLS - 1)))
    sub.style.setProperty("--y", str(keep_in_range(sub_y, 0, ROWS - 1)))


def update_screen():
    """Update every instrument on the control deck."""
    show("oxygen", oxygen)
    document.getElementById("oxygen-bar").style.width = str(oxygen) + "%"
    gauge = document.getElementById("oxygen-gauge")
    if oxygen <= 20:
        gauge.dataset.level = "critical"
    elif oxygen <= 45:
        gauge.dataset.level = "low"
    else:
        gauge.dataset.level = "ok"

    show("depth", keep_in_range(sub_y, 0, ROWS - 1) * 50)
    show("treasure-count", treasure_found)
    show("treasure-total", NUM_TREASURES)
    show("moves", moves)
    document.getElementById("hull").dataset.hull = str(keep_in_range(hull, 0, 3))

    nearby = count_nearby_mines()
    show("sonar", nearby)
    document.getElementById("sonar-panel").dataset.level = str(keep_in_range(nearby, 0, 3))
    draw_ocean()


def reset_screen():
    """Clear the log and hide the game-over screen for a new dive."""
    global game_running
    game_running = True
    document.getElementById("log").innerHTML = ""
    document.getElementById("overlay").hidden = True


def game_over(title, message, won):
    """End the game and show the dive report."""
    global game_running
    game_running = False
    show("overlay-title", title)
    show("overlay-text", message)
    overlay = document.getElementById("overlay")
    if won:
        overlay.className = "overlay is-win"
        log(title + " " + message, "good")
    else:
        overlay.className = "overlay is-lose"
        log(title + " " + message, "bad")
    overlay.hidden = False


# -------------------------------------------------------------
#  PART 1: MISSION SETUP
# -------------------------------------------------------------

# YOU TRY 1: Ask the player for their name with input() and store it in
#            captain_name. A pop-up box will appear when the page loads.
#            Hint: captain_name = input("What is your name, Captain? ")
captain_name = "Nemo"


# YOU TRY 2: Use print() to send a secret mission briefing to the console.
#            Include captain_name in your message.
#            Hint: print("Welcome aboard, Captain", captain_name)



# YOU TRY 3: These numbers control how hard the game is.
#            Change them to design your own mission:
#              NUM_TREASURES  how many chests to find     (try 3 to 6)
#              NUM_MINES      how many hidden mines       (try 4 to 10)
#              START_OXYGEN   oxygen at the start         (try 60 to 100)
NUM_TREASURES = 3
NUM_MINES = 5
START_OXYGEN = 100


# -------------------------------------------------------------
#  PART 2: NEW GAME
#  Runs when the page loads and when you press "New dive".
# -------------------------------------------------------------

def new_game(event=None):
    global sub_x, sub_y, last_x, oxygen, hull, moves, treasure_found
    global treasures, mines, found_mines, visited

    sub_x = 0
    sub_y = 0
    last_x = 0
    oxygen = START_OXYGEN
    hull = 3
    moves = 0
    treasure_found = 0
    treasures = []
    mines = []
    found_mines = []
    visited = [[0, 0]]
    reset_screen()

    # YOU TRY 4: Use a FOR LOOP to hide the treasure.
    #            Repeat NUM_TREASURES times. Each time, add a new random
    #            spot to the treasures list.
    #            Hint:
    #                for i in range(NUM_TREASURES):
    #                    treasures.append(empty_spot(treasures))


    # YOU TRY 5: Now hide the mines the same way. Use a FOR LOOP to add
    #            NUM_MINES spots to the mines list.
    #            Careful! A mine can't sit on top of treasure, so this time
    #            the spots that are already taken are: treasures + mines


    show("captain-name", captain_name)
    update_screen()
    log("Dive started. Find " + str(NUM_TREASURES) + " treasure chests, then get back to the surface!")


# -------------------------------------------------------------
#  PART 3: STEERING
#  Runs every time the player presses a button or types a command.
# -------------------------------------------------------------

def handle_command(command):
    global sub_x, sub_y, moves
    if not game_running:
        return
    command = command.lower().strip()

    # YOU TRY 6: Right now the sub can only go DOWN. Add elif blocks so
    #            "up", "left" and "right" work too.
    #              "up"    -> sub_y gets 1 smaller
    #              "left"  -> sub_x gets 1 smaller
    #              "right" -> sub_x gets 1 bigger
    #
    # YOU TRY 7: Add one more elif. The command "surface" should take the
    #            sub straight up to the top (sub_y = 0) in a single move.
    #
    # YOU TRY 8: Lots of players use the W A S D keys. Make "w" work just
    #            like "up", "s" like "down", "a" like "left" and "d" like
    #            "right".
    #            Hint: if command == "down" or command == "s":
    if command == "down":
        sub_y = sub_y + 1
    else:
        log("Unknown command: '" + command + "'. Try up, down, left or right.", "bad")
        return

    # YOU TRY 9: Uh oh, the sub can drive right off the map! Use if
    #            statements to stop it:
    #              if sub_x is less than 0, set it back to 0
    #              if sub_x is bigger than COLS - 1, set it back to COLS - 1
    #            Then do the same for sub_y (it must stay from 0 to ROWS - 1).
    #            Bonus: log("Bonk! That's the edge of the map.", "bad")


    moves = moves + 1
    if [sub_x, sub_y] not in visited:
        visited.append([sub_x, sub_y])
    status("Moved " + command + ". Depth: " + str(sub_y * 50) + " m.")
    use_oxygen()
    check_square()
    update_screen()
    check_game_over()


# -------------------------------------------------------------
#  PART 4: OXYGEN
# -------------------------------------------------------------

def oxygen_cost():
    # YOU TRY 10: The deeper you go, the more oxygen each move uses.
    #             Use if / elif / else to return a different amount:
    #               sub_y is 0 or 1     -> return 3
    #               sub_y is 2 or 3     -> return 6
    #               deeper than that    -> return 10
    #             Hint:
    #                 if sub_y <= 1:
    #                     return 3
    return 5


def use_oxygen():
    global oxygen
    oxygen = oxygen - oxygen_cost()

    # YOU TRY 11: At the surface (sub_y == 0) the crew can breathe fresh air.
    #             If the sub is at the surface, set oxygen back to
    #             START_OXYGEN and show a message with status().


    oxygen = keep_in_range(oxygen, 0, 100)


# -------------------------------------------------------------
#  PART 5: WHAT'S IN THIS SQUARE?
# -------------------------------------------------------------

def check_square():
    global hull, treasure_found
    spot = [sub_x, sub_y]

    # YOU TRY 12: Treasure! If spot is in the treasures list:
    #               - take it out of the list:   treasures.remove(spot)
    #               - add 1 to treasure_found
    #               - log() a happy message with the kind "good"
    #             Hint: if spot in treasures:
    #
    # YOU TRY 13: Use elif to check for a mine. If spot is in the mines list:
    #               - take it out of mines, then add it to found_mines
    #               - take 1 away from hull
    #               - log() a scary message with the kind "bad"
    pass


# -------------------------------------------------------------
#  PART 6: SONAR
# -------------------------------------------------------------

def count_nearby_mines():
    # YOU TRY 14: The sonar counts mines touching the sub (diagonals too).
    #             Use a FOR LOOP to check every mine in the mines list.
    #             A mine is touching the sub if BOTH of these are true:
    #               abs(mine[0] - sub_x) <= 1     (close left or right)
    #               abs(mine[1] - sub_y) <= 1     (close up or down)
    #             abs() makes a number positive, so abs(-1) is 1.
    #             Hint:
    #                 count = 0
    #                 for mine in mines:
    #                     if ... and ...:
    #                         count = count + 1
    #                 return count
    return 0


# -------------------------------------------------------------
#  PART 7: WIN OR LOSE?
# -------------------------------------------------------------

def check_game_over():
    # YOU TRY 15: Use if / elif to end the game with game_over():
    #               hull is 0 or less   -> game_over("Sub destroyed!", "your message", False)
    #               oxygen is 0 or less -> game_over("Out of oxygen!", "your message", False)
    #               ALL the treasure found AND back at the surface
    #                                   -> game_over("Mission complete!", "your message", True)
    #             Bonus: put the number of moves in the winning message.
    pass


# -------------------------------------------------------------
#  BUTTONS - the webpage runs these (already done for you)
# -------------------------------------------------------------

def go_up(event):
    handle_command("up")


def go_down(event):
    handle_command("down")


def go_left(event):
    handle_command("left")


def go_right(event):
    handle_command("right")


def go_surface(event):
    handle_command("surface")


def send_command(event):
    box = document.getElementById("command")
    text = box.value
    box.value = ""
    if text.strip() != "":
        handle_command(text)


# -------------------------------------------------------------
#  START THE GAME
# -------------------------------------------------------------

new_game()
