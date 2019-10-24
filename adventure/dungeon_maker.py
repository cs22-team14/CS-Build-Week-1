from .models import Room

class Dungeon():
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.room_count = 1
    self.tracker = None
    self.dungeon = None
    
    
  def make_grid(self):
    grid = [None] * self.y
    for i in range(self.y):
      grid[i] = [None] * self.x
    return grid
  
  
  def contains_none(self):
    for row in self.tracker:
      if None in row:
        return True
    return False
  
  
  def get_last_position(self, x, y):
    if (x - 1 >= 0) and (self.tracker[y][x-1] == (self.tracker[y][x]-1)):
      return x-1, y
    if ((x + 1 < len(self.tracker[0])) and 
       (self.tracker[y][x+1] == (self.tracker[y][x]-1))):
      return x+1, y
    if (y - 1 >=0) and (self.tracker[y-1][x] == (self.tracker[y][x]-1)):
      return x, y-1
    if ((y + 1 < len(self.tracker)) and 
       (self.tracker[y+1][x] == (self.tracker[y][x]-1))):
      return x, y+1
    
    
  def get_unvisited_options(self, x, y):
    x_lim = len(self.tracker[0])
    y_lim = len(self.tracker)
    dic = {'x':[], 'y':[]}

    if (x + 1 < x_lim) and (self.tracker[y][x+1] == None):
      dic['x'].append(1)
    if (x - 1 >= 0) and (self.tracker[y][x-1] == None):
      dic['x'].append(-1)
    if (y + 1 < y_lim) and (self.tracker[y+1][x] == None):
      dic['y'].append(1)
    if (y - 1 >= 0) and (self.tracker[y-1][x] == None):
      dic['y'].append(-1)

    return dic
  
  
  def get_direction(self, axis, value):
    if axis == 'x':
      if value == 1:
        return 'w'
      else:
        return 'e'
    else:
      if value == 1:
        return 'n'
      else:
        return 's'
      
      
  def get_new_move(self, move_options):
    import random
    
    if move_options['x'] == []:
      axis = 'y'
    elif move_options['y'] == []:
      axis = 'x'
    else:
      axis = random.choice(['x', 'y'])
    value = random.choice(move_options[axis])
    return axis, value


  def create_tracker(self):
    self.tracker = self.make_grid()

    no_new_choice = {'x': [], 'y': []}
    cur_pos_x, cur_pos_y = 0, 0
    self.tracker[cur_pos_y][cur_pos_x] = 0
    
    while self.contains_none():
      move_options = self.get_unvisited_options(cur_pos_x, cur_pos_y)
      if move_options == no_new_choice:
        cur_pos_x, cur_pos_y = self.get_last_position(cur_pos_x, cur_pos_y)
      else:
        axis, value = self.get_new_move(move_options)
        count = self.tracker[cur_pos_y][cur_pos_x]
        if axis == 'x':
          cur_pos_x += value
        else:
          cur_pos_y += value
        self.tracker[cur_pos_y][cur_pos_x] = count + 1


  def create_rooms(self):
    self.dungeon = self.make_grid()

    for y in range(self.y):
      for x in range(self.x):
        self.dungeon[y][x] = Room(title='Room', description='Another empty room')
        self.dungeon[y][x].save()
  

  def link_rooms(self):
    for y in range(self.y):
      for x in range(self.x):
        if (x+1 < self.x) and (self.tracker[y][x+1] == (self.tracker[y][x] + 1)):
          self.dungeon[y][x].connectRooms(self.dungeon[y][x+1], 'e')
          self.dungeon[y][x+1].connectRooms(self.dungeon[y][x], 'w')
        elif (x-1 >= 0) and (self.tracker[y][x-1] == (self.tracker[y][x] + 1)):
          self.dungeon[y][x].connectRooms(self.dungeon[y][x-1], 'w')
          self.dungeon[y][x-1].connectRooms(self.dungeon[y][x], 'e')
        elif (y+1 < self.y) and (self.tracker[y+1][x] == (self.tracker[y][x] + 1)):
          self.dungeon[y][x].connectRooms(self.dungeon[y+1][x], 's')
          self.dungeon[y+1][x].connectRooms(self.dungeon[y][x], 'n')
        elif (y-1 >= 0) and (self.tracker[y-1][x] == (self.tracker[y][x] + 1)):
          self.dungeon[y][x].connectRooms(self.dungeon[y-1][x], 'n')
          self.dungeon[y-1][x].connectRooms(self.dungeon[y][x], 's')

  def generate_dungeon(self):
    self.create_tracker()
    self.create_rooms()
    self.link_rooms()

  def get_dungeon(self):
    return self.dungeon
  
  def visualize_dungeon(self):
    for y in range(self.y):
      row = ''
      for x in range(self.x):
        if self.tracker[y][x] < 10:
          row += str(self.tracker[y][x]) + '  '
        else:
          row += str(self.tracker[y][x]) + ' '
      print(row)