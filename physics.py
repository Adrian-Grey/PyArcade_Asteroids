import arcade
import entity
import math

tau = math.pi * 2

def _move_sprite(moving_sprite: entity.Thing, walls: arcade.SpriteList, targets: arcade.SpriteList):
    
    assert isinstance(walls, arcade.SpriteList)
    assert isinstance(targets, arcade.SpriteList)
    
    hit_list_y = arcade.SpriteList()
    hit_list_x = arcade.SpriteList()
    hit_list_r = arcade.SpriteList()
    
    # first make sure the sprite isn't already in collision with one of the wall
    if len(arcade.check_for_collision_with_list(moving_sprite, walls)) > 0:
        arcade._circular_check(moving_sprite, walls)

    # now check if the proposed move (change_x, change_y) would put it 
    # in collision with one of the walls
    if moving_sprite.change_x or moving_sprite.change_y:
        # store x movement direction
        if moving_sprite.change_x < 0:
            x_sign = -1
        else:
            x_sign = +1

        # store y movement direction
        if moving_sprite.change_y < 0:
            y_sign = -1
        else:
            y_sign = +1

        # fancy math. create overall movement vector from x and y, subtract friction, decompose back into unsigned x and y vectors
        hyp = math.sqrt(moving_sprite.change_x**2 + moving_sprite.change_y**2)
        angle = math.asin(abs(moving_sprite.change_y) / hyp)
        hyp = max(0, hyp - moving_sprite.friction)

        moving_sprite.change_y = hyp * math.sin(angle)
        moving_sprite.change_x = hyp * math.cos(angle)

        # restore x and y directionality
        moving_sprite.change_x *= x_sign
        moving_sprite.change_y *= y_sign
    
        # move in y-axis
        moving_sprite.center_y += min(moving_sprite.change_y, moving_sprite.max_speed)

        # check for collision due to y-movement
        hit_list_y.extend(arcade.check_for_collision_with_lists(moving_sprite, [walls, targets]))
        
        if len(hit_list_y) > 0:
            adjust_y = -1
            if moving_sprite.change_y < 0: 
                adjust_y = 1

            #back sprite up until no longer inside object and zero out speed 
            while len(arcade.check_for_collision_with_list(moving_sprite, hit_list_y)) > 0:
                moving_sprite.center_y += adjust_y
            assert not len(arcade.check_for_collision_with_list(moving_sprite, hit_list_y))
            moving_sprite.change_y = 0

        # move in x-axis
        moving_sprite.center_x += min(moving_sprite.change_x, moving_sprite.max_speed)

        # check for collision due to x-movement
        hit_list_x.extend(arcade.check_for_collision_with_lists(moving_sprite, [walls, targets]))
        
        if len(hit_list_x) > 0:
            adjust_x = -1
            if moving_sprite.change_x < 0: 
                adjust_x = 1
            
            #back sprite up until no longer inside object and zero out speed
            while len(arcade.check_for_collision_with_list(moving_sprite, hit_list_x)) > 0:
                moving_sprite.center_x += adjust_x
            assert not len(arcade.check_for_collision_with_list(moving_sprite, hit_list_x))
            moving_sprite.change_x = 0

    if moving_sprite.change_r:

        temp_circle = arcade.SpriteCircle(max(moving_sprite.image_width, moving_sprite.image_height), (0,0,0))
        temp_circle.center_x = moving_sprite.center_x
        temp_circle.center_y = moving_sprite.center_y
        hit_list_r.extend(arcade.check_for_collision_with_lists(temp_circle, [walls, targets]))

        if len(hit_list_r) > 0:

            change_increment = moving_sprite.change_r / 20

            for i in range(0,19):
                moving_sprite.radians += change_increment
                if len(arcade.check_for_collision_with_list(moving_sprite, hit_list_r)) > 0:
                    break

            moving_sprite.radians = moving_sprite.radians % tau

            adjust_r = 0

            if len(hit_list_r) > 0:
                adjust_r = -0.01
                if moving_sprite.change_r < 0:
                    adjust_r = 0.01

            while len(arcade.check_for_collision_with_list(moving_sprite, hit_list_r)) > 0:
                moving_sprite.radians += adjust_r
            
            assert not len(arcade.check_for_collision_with_list(moving_sprite, hit_list_r))
            moving_sprite.change_r = 0

        else:

            moving_sprite.radians += moving_sprite.change_r 
            moving_sprite.radians = moving_sprite.radians % tau
            moving_sprite.change_r = 0

    final_check = arcade.check_for_collision_with_lists(moving_sprite, [walls, targets])
    if len(final_check) > 0:
        for res in final_check:
            print(f"moving_sprite {type(moving_sprite).__name__} still in collision with:{type(res).__name__}")
    assert len(final_check) == 0

    complete_hit_list = []

    for hit in hit_list_y:
        if hit not in complete_hit_list:
            complete_hit_list.append(hit)

    for hit in hit_list_x:
        if hit not in complete_hit_list:
            complete_hit_list.append(hit)

    for hit in hit_list_r:
        if hit not in complete_hit_list:
            complete_hit_list.append(hit)
        
    return complete_hit_list
            