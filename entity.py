import arcade

class Ball(arcade.Sprite):
    image_src = "./asteroids.png"
    def __init__(self, center_x, center_y, change_x, change_y, change_r = 0):
        # Take the parameters of the init function above,
        # and create instance variables out of them.
        super().__init__(self.image_src, 1, self.image_x, self.image_y, self.image_width, self.image_height, False, False, False, 'Simple')
        self.center_x = center_x
        self.center_y = center_y
        self.change_x = change_x
        self.change_y = change_y
        self.change_r = change_r
        self.friction = 0.025
        self.max_speed = 6

    def update(self, targets, walls):
        import physics
        return physics._move_sprite(self, targets, walls)
