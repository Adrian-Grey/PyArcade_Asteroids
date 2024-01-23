import arcade
import math

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
ACCEL = 0.1


class Ball:
    def __init__(self, position_x, position_y, change_x, change_y):

        # Take the parameters of the init function above,
        # and create instance variables out of them.
        self.position_x = position_x
        self.position_y = position_y
        self.change_x = change_x
        self.change_y = change_y
        self.radius = 10
        self.color = arcade.color.BLACK
        self.friction = 0.025
        self.max_speed = 6
        
    def draw(self):
        """ Draw the balls with the instance variables we have. """
        arcade.draw_circle_filled(self.position_x,
                                  self.position_y,
                                  self.radius,
                                  self.color)

    def update(self):
        if self.change_x != 0 and self.change_y != 0:
            if self.change_x < 0:
                x_sign = -1
            else:
                x_sign = +1

            if self.change_y < 0:
                y_sign = -1
            else:
                y_sign = +1

            hyp = math.sqrt(self.change_x**2 + self.change_y**2)
            angle = math.asin(abs(self.change_y) / hyp)
            hyp = max(0, hyp - self.friction)

            self.change_y = hyp * math.sin(angle)
            self.change_x = hyp * math.cos(angle)

            self.change_x *= x_sign
            self.change_y *= y_sign
       
        
        self.position_y += min(self.change_y, self.max_speed)
        if self.position_y > (SCREEN_HEIGHT-self.radius):
            self.position_y = (SCREEN_HEIGHT-self.radius)
            self.change_y = 0
            if hasattr(self, "has_collided"):
                self.has_collided = True
        elif self.position_y < (0+self.radius):
            self.position_y = (0+self.radius)
            self.change_y = 0
            if hasattr(self, "has_collided"):
                self.has_collided = True
        self.position_x += min(self.change_x, self.max_speed)
        if self.position_x > (SCREEN_WIDTH-self.radius):
            self.position_x = (SCREEN_WIDTH-self.radius)
            self.change_x = 0
            if hasattr(self, "has_collided"):
                self.has_collided = True
        elif self.position_x < (0+self.radius):
            self.position_x = (0+self.radius)
            self.change_x = 0
            if hasattr(self, "has_collided"):
                self.has_collided = True



class PlayerBall(Ball):
    def __init__(self, position_x, position_y, change_x, change_y):

        super().__init__(position_x, position_y, change_x, change_y)

        self.base_projectile_speed = 5
        self.radius = 15
        self.color = arcade.color.AUBURN

class Projectile(Ball):
    def __init__(self, position_x, position_y, change_x, change_y):

        super().__init__(position_x, position_y, change_x, change_y)
    
        self.age = 0
        self.max_age = 120
        self.friction = 0
        self.max_speed = 10
        self.has_collided = False
        self.radius = 5
        self.color = arcade.color.BLACK

    def update(self):

        super().update()

        self.age += 0
        if self.has_collided:
            self.age += self.max_age

class Fastball(Projectile):
    def __init__(self, position_x, position_y, change_x, change_y):
        
        super().__init__(position_x, position_y, change_x, change_y)

        self.speed_factor = 2
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor
    
        self.radius = 4
        self.color = arcade.color.BLACK
        


class Slowball(Projectile):
    def __init__(self, position_x, position_y, change_x, change_y):

        super().__init__(position_x, position_y, change_x, change_y)
        
        self.speed_factor = 0.7
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor

        self.radius = 6
        self.color = arcade.color.BLACK


class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.

        arcade.set_background_color(arcade.color.ASH_GREY)

        # Create our ball
        self.mainball = PlayerBall(50, 50, 0, 0)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.spawned_balls = []

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        arcade.start_render()
        self.mainball.draw()
        for ball in self.spawned_balls:
            ball.draw()



    def update(self, delta_time):
        if self.left_pressed:
            self.mainball.change_x += -ACCEL
        if self.right_pressed:
            self.mainball.change_x += ACCEL
        if self.up_pressed:
            self.mainball.change_y += ACCEL
        if self.down_pressed:
            self.mainball.change_y += -ACCEL

        to_remove = []

        self.mainball.update()
        for ball in self.spawned_balls:
            ball.update()
            if ball.age > ball.max_age:
                to_remove.append(ball)
        
        for ball in to_remove:
            self.spawned_balls.remove(ball)
        
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
        if button == arcade.MOUSE_BUTTON_LEFT:
            rel_x = x - self.mainball.position_x
            rel_y = y - self.mainball.position_y
            hyp = math.sqrt((rel_x**2)+(rel_y**2))
            scaled_x = rel_x/hyp
            scaled_y = rel_y/hyp
            change_x = scaled_x * self.mainball.base_projectile_speed
            change_y = scaled_y * self.mainball.base_projectile_speed
            self.spawned_balls.append(Fastball(self.mainball.position_x, self.mainball.position_y, change_x, change_y))
            arcade.play_sound(arcade.load_sound("fast_shoot.wav"))
        if button == arcade.MOUSE_BUTTON_RIGHT:
            rel_x = x - self.mainball.position_x
            rel_y = y - self.mainball.position_y
            hyp = math.sqrt((rel_x**2)+(rel_y**2))
            scaled_x = rel_x/hyp
            scaled_y = rel_y/hyp
            change_x = scaled_x * self.mainball.base_projectile_speed
            change_y = scaled_y * self.mainball.base_projectile_speed
            self.spawned_balls.append(Slowball(self.mainball.position_x, self.mainball.position_y, change_x, change_y))
            arcade.play_sound(arcade.load_sound("slow_shoot.wav"))


        


def main():
    window = MyGame(640, 480, "Drawing Example")
    arcade.run()


main()