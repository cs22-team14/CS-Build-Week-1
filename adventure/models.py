from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid
import random


TILE_EMPTY = ' '
TILE_CRATE = '#'

class Room(models.Model):
    def __init__(self, id, name, description, x, y):
        self.id = id
        self.name = name
        self.description = description
        self.n_to = None
        self.s_to = None
        self.e_to = None
        self.w_to = None
        self.x = x
        self.y = y
    def __repr__(self):
        return str(self.name)

      
    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"{direction}_to", connecting_room)
        setattr(connecting_room, f"{reverse_dir}_to", self)


    def get_room_in_direction(self, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        return getattr(self, f"{direction}_to")

      
    def get_possible_directions(self):
      dir_list = {'north': self.n_to, 'south': self.s_to, 
                  'east': self.e_to, 'west': self.w_to}
      
      available_dirs = []
      for direction, value in dir_list.items():
        if value is not None:
          available_dirs.append(direction)
          
      if len(available_dirs) == 1:
        return f'There is a path to the {available_dirs[0]} of you.'
      else:
        possible_directions = 'There are paths to the '
        
      for i, direction in enumerate(available_dirs):
        possible_directions += direction + ', '
      possible_directions = possible_directions.rstrip(', ') + ' of you.'
      
      x = possible_directions.rfind(',')
      possible_directions = possible_directions[:x+1] + ' and'+ possible_directions[x+1:]
      return possible_directions


class World(models.Model):
    def __init__(self):
        # self.grid = None
        self.width = 21
        self.height = 21
    

    def create_grid(self, width, height):
        grid = []
        for row in range(height):
            grid.append([])
            for column in range(width):
                if (column % 2 == 1) and (row % 2 == 1): # Room at 4 corners
                    grid[row].append(TILE_EMPTY)
                elif column == 0 or row == 0 or column == width - 1 or row == height - 1:
                    grid[row].append(TILE_CRATE)
                else:
                    grid[row].append(TILE_CRATE)
        return grid


    def get_corners(self, height, width):
        size = random.randint(3, 6)
  
        x_start = random.randint(1, width-3)
        x_end = x_start+size
        if x_end >= width:
            x_end = x_start
    
        y_start = random.randint(1, height-3)
        y_end = y_start+size
        if y_end >= height:
            y_end = y_start
  
        return x_start, y_start, x_end, y_end


    def add_rooms(self, maze, width, height):
        large_rooms = random.randint(1,min(width, height)//3)
  
        for _ in range(large_rooms):
            x_start, y_start, x_end, y_end = self.get_corners(height, width)
            for i in range(y_start, y_end):
                for j in range(x_start, x_end):
                    maze[i][j] = TILE_EMPTY
        return maze


    def make_maze(self, width, height):
        if ((width*height) > (75**2)) or (width <= 3) or (height <= 3):
            return None
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1
      
        maze = self.create_grid(width, height)

        w = (len(maze[0]) - 1) // 2
        h = (len(maze) - 1) // 2
        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]

        def walk(x, y):
            vis[y][x] = 1

            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            random.shuffle(d)
            for (xx, yy) in d:
                if vis[yy][xx]:
                    continue
                if xx == x:
                    maze[max(y, yy) * 2][x * 2 + 1] = TILE_EMPTY
                if yy == y:
                    maze[y * 2 + 1][max(x, xx) * 2] = TILE_EMPTY

                walk(xx, yy)

        walk(random.randrange(w), random.randrange(h))
        maze = self.add_rooms(maze, width, height)
          
        return maze
  
    def print_maze(self, maze):
        temp = ''
        for row in maze:
            for space in row:
                temp += space
            temp+='\n'
        print(temp)

    def create_dungeon(self, maze):
        grid = [None] * len(maze)
        for i in range(len(grid)):
            grid[i] = [None] * len(maze[0])
        room_count = 0
        count = 0

        for Y, row in enumerate(maze):
            for X, room in enumerate(row):
                if room == '#':
                    grid[Y][X] = Room(id=room_count, name='Wall', description='A wholly unremarkable wall', x=X, y=Y)
                else:
                    grid[Y][X] = Room(id=room_count, name='Room', description='Another empty room', x=X, y=Y)
                    count += 1
                room_count += 1
      
        print('Number of Traversable Rooms: ', count)
        return grid

    def connect_paths(self, grid):
        X = len(grid[0])
        Y = len(grid)
  
        for Y, row in enumerate(grid):
            for X, room in enumerate(row):
                if room.name != 'Wall':
                    if (Y > 0) and grid[Y-1][X].name != 'Wall':
                        room.connect_rooms(grid[Y-1][X], 'n')
                    if (X > 0) and grid[Y][X-1].name != 'Wall':
                        room.connect_rooms(grid[Y][X-1], 'w')
        return grid

    def make_connected_dungeon(self):
        maze = self.make_maze(self.width, self.height)
        dungeon = self.connect_paths(self.create_dungeon(maze))
        return dungeon

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()

