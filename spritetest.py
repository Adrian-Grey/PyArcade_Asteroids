import arcade
import entity
import math
import physics
import random

#Made objects destructible, added little explosions, added cooldowns to shooting
#Fastball attack speed now scales with score
#Asteroids now dissapear upon hitting screen edge, don't collide with each other, and new ones spawn constantly
#Target spawning speeds up over time
#Asteroids now have variable HP (2-5) and score is awarded based on max HP of asteroid destroyed
#Asteroid size now varies based on max HP
#Enabled autofire
#Made timer class
#Still have a bug where a target colliding with the player will cause player sprite to jump positions oddly
#Player can now take damage from collision with asteroids or projectiles, added death effect on zero hp
#Can't figure out how to properly delete player entity on death

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
ACCEL = 0.1

tau = math.pi * 2

class Timer():
    def __init__(self, time = 0):
        self.time = time
    def update(self, interval = 1):
        self.time = max(self.time - interval, 0)

class PlayerBall(entity.Thing):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.image_x = 96
        self.image_y = 128
        self.image_width = 48
        self.image_height = 32
        
        self.fastball_timer = Timer()
        self.fastball_cooldown = 30
        self.slowball_timer = Timer()
        self.slowball_cooldown = 120

        super().__init__(center_x, center_y, change_x, change_y)

        self.hp = 10
        self.max_hp = 10

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
        if button == arcade.MOUSE_BUTTON_LEFT and self.fastball_timer.time == 0:
            arcade.play_sound(arcade.load_sound("fast_shoot.wav"))
            self.fastball_timer.time += self.fastball_cooldown
            return Fastball(self.center_x, self.center_y, change_x, change_y) 
        elif button == arcade.MOUSE_BUTTON_RIGHT and self.slowball_timer.time == 0:
            arcade.play_sound(arcade.load_sound("slow_shoot.wav"))
            self.slowball_timer.time += self.slowball_cooldown
            return Slowball(self.center_x, self.center_y, change_x, change_y)
        
    def point_at(self, x, y):

        rel_x = x - self.center_x
        rel_y = y - self.center_y

        self.change_r = 0
        
        self.change_r = math.atan2(rel_y, rel_x) - self.radians
        self.change_r = (math.pi + self.change_r) % tau - math.pi
            
    def update(self, walls, targets):
        self.fastball_timer.update()
        self.slowball_timer.update()
        return super().update(walls, targets)

class Projectile(entity.Thing):
    def __init__(self, center_x, center_y, change_x, change_y):
        
        super().__init__(center_x, center_y, change_x, change_y)
    
        self.max_age = 120
        self.friction = 0
        self.max_speed = 10
        self.radius = 5
        self.color = arcade.color.BLACK
        self.hp = 1
        self.max_hp = 1

class Fastball(Projectile):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.image_x = 224
        self.image_y = 144
        self.image_width = 16
        self.image_height = 16
        self.damage = 1
        
        super().__init__(center_x, center_y, change_x, change_y)

        self.speed_factor = 2
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor
    
        self.radius = 4
        self.color = arcade.color.WHITE
        


class Slowball(Projectile):
    def __init__(self, center_x, center_y, change_x, change_y):

        self.image_x = 240
        self.image_y = 144
        self.image_width = 16
        self.image_height = 16
        self.damage = 5

        super().__init__(center_x, center_y, change_x, change_y)
        
        self.speed_factor = 0.7
         
        self.change_x *= self.speed_factor
        self.change_y *= self.speed_factor

        self.radius = 6     
        self.color = arcade.color.WHITE

class Target(entity.Thing):
    def __init__(self, center_x, center_y, change_x, change_y):
        
        self.image_x = 0
        self.image_y = 128
        self.image_width = 32
        self.image_height = 32

        super().__init__(center_x, center_y, change_x, change_y)

        self.friction = 0
        self.hp = random.randint(2,5)
        self.max_hp = self.hp
        self.scale = 0.8 + 0.3 * self.max_hp
    def update(self, walls, targets):
        return super().update(walls, targets)

class Wall(arcade.SpriteSolidColor):
    def __init__(self, center_x, center_y, width, height, color):
        
        super().__init__(width, height, color)
        
        self.center_x = center_x
        self.center_y = center_y  

class Explosion():
    def __init__(self, center_x, center_y, expand_step, c1, c2, c3):
        self.timer = Timer(60)
        self.diameter = 5
        self.expand_step = expand_step
        self.center_x = center_x
        self.center_y = center_y
        self.opacity = 255
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.color = [self.c1,self.c2,self.c3,self.opacity]
    def update(self):
        self.diameter += self.expand_step
        self.timer.update()
        self.opacity = max(self.opacity -7, 0)
        self.color = [self.c1,self.c2,self.c3,self.opacity]
    def draw(self):
        return arcade.create_ellipse_outline(self.center_x, self.center_y, self.diameter, self.diameter, self.color)


class MyGame(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.

        arcade.set_background_color(arcade.color.BLACK)

        # Create our ball
        self.player = PlayerBall(50, 50, 0, 0)
        print(f"Starting hp value = {self.player.hp}")

        self.score = 0
        self.upgrade_threshhold = 50

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.mb_left_held = False
        self.mb_right_held = False
        self.mouse_x = 0
        self.mouse_y = 0

        self.projectiles = arcade.SpriteList()
        self.targets = arcade.SpriteList()
        self.walls = arcade.SpriteList()
        self.effects = []

        self.target_timer = Timer(150)
        self.target_interval = Timer(120)

        self.targets.append(Target(SCREEN_WIDTH - 50,SCREEN_HEIGHT/2,random.randint(-3,-1),0))
        for target in self.targets:
            print(f"Target created with hp {target.hp}, change_x {target.change_x}, and change_y {target.change_y}.")

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
        shape_list = arcade.ShapeElementList()
        for effect in self.effects:
            shape_list.append(effect.draw())
        shape_list.draw()
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

        if self.mb_left_held:
            projectile = self.player.spawn_projectile(self._mouse_x, self._mouse_y, arcade.MOUSE_BUTTON_LEFT)
            if projectile:
                self.projectiles.append(projectile)
        
        if self.mb_right_held:
            projectile = self.player.spawn_projectile(self._mouse_x, self._mouse_y, arcade.MOUSE_BUTTON_RIGHT)
            if projectile:
                self.projectiles.append(projectile)

        player_hit_list = self.player.update(self.walls, self.targets)
        
        if len(player_hit_list):
            for hit in player_hit_list:
                if isinstance(hit, Target):
                    self.player.hp -= hit.max_hp
                    print(f"player took {hit.max_hp} damage")
                    hit.remove_from_sprite_lists()
                if isinstance(hit, Projectile):
                    self.player.hp -= hit.damage
                    print(f"player took {hit.damage} damage")
                    hit.remove_from_sprite_lists()

        if self.score >= self.upgrade_threshhold:
            self.player.fastball_cooldown = max(self.player.fastball_cooldown * 0.7, 5)
            self.upgrade_threshhold += 50

        if self.player.hp <= 0:
            self.effects.append(Explosion(self.player.center_x, self.player.center_y, 10, 255, 255, 0))
            print("GAME OVER")
            self.player.remove_from_sprite_lists()

        for projectile in self.projectiles:

            projectile_hit_list = projectile.update(self.walls, self.targets)
            
            if len(projectile_hit_list):
                for hit in projectile_hit_list:
                    if isinstance(hit, Target):
                        hit.hp -= projectile.damage
                        projectile.hp = 0
                    elif isinstance(hit, Wall):
                        projectile.hp = 0
                    else: pass

            if projectile.hp <= 0:
                if isinstance(projectile, Slowball):
                    self.effects.append(Explosion(projectile.center_x, projectile.center_y, 1, 255, 0, 0))
                projectile.remove_from_sprite_lists()

        collidable_list = arcade.SpriteList()

        for target in self.targets:
            
            collidable_list.clear()
            # Make a spritelist of other targets this target might collide with excluding itself  
            #Turning collision with other targets off for now       
            # for sprite in self.targets:
            #     if sprite != target:
            #         collidable_list.append(sprite)

            target_hit_list = target.update(self.walls, collidable_list)
            
            if len(target_hit_list):
                for hit in target_hit_list:
                    if isinstance(hit, Wall):
                        target.remove_from_sprite_lists()  
            
            if target.hp <= 0:
                self.score += target.max_hp
                target.remove_from_sprite_lists()
                self.effects.append(Explosion(target.center_x, target.center_y, 5, 255, 255, 255))

        for effect in self.effects:
            effect.update()
            if effect.timer.time <= 0:
                self.effects.remove(effect)

        if self.target_timer.time == 0:
            self.targets.append(Target(SCREEN_WIDTH - 50,random.randint(50, SCREEN_HEIGHT-50),random.randint(-3,-1),0))
            self.target_timer.time += 30 + self.target_interval.time
            self.target_interval.update(3)

        self.target_timer.update()

                

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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mb_left_held = True
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.mb_right_held = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mb_left_held = False
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.mb_right_held = False

    def on_mouse_motion(self, x, y, dx, dy):
        mouse_x = x
        mouse_y = y
        self.player.point_at(x,y)

def main():
    window = MyGame(640, 480, "Asteroids Ripoff")
    arcade.run()


main()