import arcade
import entity
import math
import physics

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
ACCEL = 0.1

SLOW_PROJECTILE = 1
FAST_PROJECTILE = 2

tau = math.pi * 2

class PlayerBall(entity.Ball):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.image_x = 96
        self.image_y = 128
        self.image_width = 48
        self.image_height = 32
        
        super().__init__(center_x, center_y, change_x, change_y)

        self.base_projectile_speed = 5
        self.radius = 15
        self.color = arcade.color.AUBURN

    def spawn_projectile(self, x, y, button):
        rel_x = x - self.center_x
        rel_y = y - self.center_y
        hyp = math.sqrt((rel_x**2)+(rel_y**2))
        scaled_x = rel_x/hyp
        scaled_y = rel_y/hyp
        change_x = scaled_x * self.base_projectile_speed
        change_y = scaled_y * self.base_projectile_speed
        if button == arcade.MOUSE_BUTTON_LEFT:
            arcade.play_sound(arcade.load_sound("fast_shoot.wav"))
            return Fastball(self.center_x, self.center_y, change_x, change_y) 
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            arcade.play_sound(arcade.load_sound("slow_shoot.wav"))
            return Slowball(self.center_x, self.center_y, change_x, change_y)
        
    def point_at(self, x, y):

        rel_x = x - self.center_x
        rel_y = y - self.center_y

        self.change_r = 0
        
        self.change_r = math.atan2(rel_y, rel_x) - self.radians
        self.change_r = (math.pi + self.change_r) % tau - math.pi
            

class Projectile(entity.Ball):
    def __init__(self, center_x, center_y, change_x, change_y):
        
        super().__init__(center_x, center_y, change_x, change_y)
    
        self.max_age = 120
        self.friction = 0
        self.max_speed = 10
        self.radius = 5
        self.color = arcade.color.BLACK

class Fastball(Projectile):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.type = FAST_PROJECTILE
        self.image_x = 224
        self.image_y = 144
        self.image_width = 16
        self.image_height = 16
        
        super().__init__(center_x, center_y, change_x, change_y)

        self.speed_factor = 2
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor
    
        self.radius = 4
        self.color = arcade.color.WHITE
        


class Slowball(Projectile):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.type = SLOW_PROJECTILE
        self.image_x = 240
        self.image_y = 144
        self.image_width = 16
        self.image_height = 16

        super().__init__(center_x, center_y, change_x, change_y)
        
        self.speed_factor = 0.7
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor

        self.radius = 6     
        self.color = arcade.color.WHITE

class Target(arcade.SpriteSolidColor):
    def __init__(self, center_x, center_y, width, height, color):
        
        super().__init__(width, height, color)
        
        self.center_x = center_x
        self.center_y = center_y  

class Wall(arcade.SpriteSolidColor):
    def __init__(self, center_x, center_y, width, height, color):
        
        super().__init__(width, height, color)
        
        self.center_x = center_x
        self.center_y = center_y  

class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.

        arcade.set_background_color(arcade.color.BLACK)

        # Create our ball
        self.player = PlayerBall(50, 50, 0, 0)
        print(f"Starting radian value = {self.player.radians}")

        self.score = 0

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.projectiles = arcade.SpriteList()
        self.targets = arcade.SpriteList()
        self.walls = arcade.SpriteList()

        self.targets.append(Target(SCREEN_WIDTH/2,SCREEN_HEIGHT/2,64,16,(255,0,0)))

        self.walls.append(Wall(-25,SCREEN_HEIGHT/2,50,SCREEN_HEIGHT,(255,255,255))) #Left wall
        self.walls.append(Wall(SCREEN_WIDTH+25,SCREEN_HEIGHT/2,50,SCREEN_HEIGHT,(255,255,255))) #Right wall
        self.walls.append(Wall(SCREEN_WIDTH/2,SCREEN_HEIGHT+25,SCREEN_WIDTH,50,(255,255,255))) #Top wall
        self.walls.append(Wall(SCREEN_WIDTH/2,-25,SCREEN_WIDTH,50,(255,255,255))) #Bottom wall



    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        self.player.draw()
        self.projectiles.draw()
        self.targets.draw()
        self.walls.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)



    def update(self, delta_time):

        if self.left_pressed:
            self.player.change_x += -ACCEL
        if self.right_pressed:
            self.player.change_x += ACCEL
        if self.up_pressed:
            self.player.change_y += ACCEL
        if self.down_pressed:
            self.player.change_y += -ACCEL

        to_remove = []

        self.player.update(self.walls, self.targets)

        for projectile in self.projectiles:

            projectile_hit_list = projectile.update(self.walls, self.targets)
            
            if len(projectile_hit_list):
                if projectile.type == FAST_PROJECTILE:
                    for hit in projectile_hit_list:
                        if isinstance(hit, Target):
                            self.score += 1
                        else: pass
                    to_remove.append(projectile)
                if projectile.type == SLOW_PROJECTILE:
                    for hit in projectile_hit_list:
                        if isinstance(hit, Target):
                            self.score += 3
                        else: pass
                    to_remove.append(projectile)
        
        for projectile in to_remove:
            projectile.remove_from_sprite_lists()
        
        to_remove.clear()
                

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """ Called whenever a user releases a key. """
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False

    def on_mouse_release(self, x, y, button, modifiers):
        projectile = self.player.spawn_projectile(x,y,button)
        if projectile:
            self.projectiles.append(projectile)

    def on_mouse_motion(self, x, y, dx, dy):
        self.player.point_at(x,y)

def main():
    window = MyGame(640, 480, "Asteroids Ripoff")
    arcade.run()


main()