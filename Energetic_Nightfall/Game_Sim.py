import pygame
import pygame as pg
import Pygame_Tools as Tool
import numpy as np
import sys
SIM_SPEED = 60


class Ship(pg.sprite.Sprite):
    """Main Player and enemy controlled ship
    Needs ability to
    -initialize with correct team id
    -update its image
    -Take user input to move itself
    -Record damage taken and health
    """
    ship_images = (pg.image.load('Assets/Ship/ShipRed.png'),
                   pg.image.load('Assets/Ship/ShipBlue.png'),
                   pg.image.load('Assets/Ship/ShipBlue.png'))
    effects = (pg.image.load('Assets/Ship/ThrustFwd.png'),
               pg.image.load('Assets/Ship/ThrustBkw.png'))

    def __init__(self, id, ship_dat, thrust=1, is_controllable=False):
        super().__init__()
        # Visual Variables
        no_effects = self.ship_images[id % len(self.ship_images)]
        self.image_list = (no_effects, no_effects.copy(), no_effects.copy())
        self.image_list[1].blit(self.effects[0], (0, 0))  # Forwards thrust
        self.image_list[2].blit(self.effects[1], (0, 0))  # Backwards thrust
        self.state = 0
        self.og_image = self.image_list[self.state]
        self.image = self.image_list[self.state]  # Set initial image
        self.rect = self.image.get_rect()
        # Combat Variables
        self.health = ship_dat[3]
        self.max = self.health
        # Movement Requirements
        self.vel = ship_dat[1].astype(float)
        self.pos = ship_dat[0].astype(float)
        self.rect.center = self.pos  # Set position
        self.thrust = thrust/100
        self.atheta = thrust/1000
        self.dtheta = 0
        self.theta = ship_dat[2]
        # Multiplayer
        self.id = id
        self.control = is_controllable
        Tool.rot(self)

    def update(self):
        if self.control:
            self.do_movement()
        self.og_image = self.image_list[self.state]
        self.rect.center = self.pos
        self.pos += self.vel


    def do_movement(self):
        keys = pg.key.get_pressed()
        # Rotation
        if keys[pg.K_a] and self.dtheta < .25:
            self.dtheta += self.atheta
        if keys[pg.K_d] and self.dtheta > -.25:
            self.dtheta -= self.atheta
        # Automation
        elif keys[pg.K_r]:
            self.point_retrograde()
        Tool.rot(self)
        self.theta += self.dtheta
        # Thrust
        if keys[pg.K_w]:
            self.vel -= np.array((-np.cos(self.theta), np.sin(self.theta)))*self.thrust
            self.state = 1
        elif keys[pg.K_s]:
            self.vel += np.array((-np.cos(self.theta), np.sin(self.theta)))*self.thrust/2
            self.state = 2
        else:
            self.state = 0

        offset = 10
        if self.pos[0] <= offset:
            self.vel[0] = 0
            self.pos[0] = 0+offset + offset/100
        elif self.pos[0] >= 1280-offset:
            self.vel[0] = 0
            self.pos[0] = 1280-offset-offset/100
        if self.pos[1] <= offset:
            self.vel[1] = 0
            self.pos[1] = 0+offset + offset/100
        elif self.pos[1] >= 720-offset:
            self.vel[1] = 0
            self.pos[1] = 720-offset-offset/100

    def point_retrograde(self):
        """Buggy control system needs some help"""
        target = (self.vel * -1)
        if np.linalg.norm(target):
            target = np.arctan2(-target[1], target[0])
            if target < 0:
                target += 2*np.pi
            ldif = target-self.theta % (2*np.pi)
            if ldif < 0:
                ldif += 2*np.pi
            if abs(ldif) > .1:
                if ldif < np.pi and self.dtheta > -.05:
                    self.dtheta += self.atheta
                elif self.dtheta < .05:
                    self.dtheta -= self.atheta
            else:
                self.dtheta = 0

    def kill(self):
        if self.health <= 0:
            # Prob nice to add death animation
            for group in self.groups():
                group.remove(self)
            self.groups().clear()
        self.health -= 1

    def new_pos(self, player_data):
        if player_data and player_data.id != self.id:
            data = player_data.ships_pos[self.id]
            self.pos = data[0]
            self.vel = data[1]
            self.theta = data[2]
            self.health = data[3]
            self.state = data[4]
            self.image = self.image_list[self.state]
            Tool.rot(self)


    def up_data(self, player_data):
        player_data.ships_pos[self.id] = [self.pos, self.vel, self.theta, self.health, self.state, True]


class WepRack:
    def __init__(self, ship):
        self.ship = ship

    def check_input(self):
        pass

    def new_weapons(self, new_weapons: list):
        """inputs:
            - [[type <str>, pos <vector>, vel <vector>, target <vetor> or id <int>]]
        Outputs
            - list of weapon sprites"""
        for name, pos, vel, target in new_weapons:
            print(name)
        return new_weapons




class Game:
    def __init__(self, screen, network, key_dat, ships, planets=()):
        self.tics = SIM_SPEED
        self.screen = screen
        self.network = network
        self.player_dat = key_dat
        # Make Map
        self.background = pg.sprite.Group()
        back = Tool.Background(pg.image.load('Assets/Background/Background1.png'),
                               screen.get_width(), screen.get_height())
        self.background.add(back)
        self.planets = pg.sprite.Group()
        self.planets.add(planets)
        # Item Groups
        self.con_ship = ships[0]
        self.ships = pg.sprite.Group()
        self.ships.add(ships)
        self.weapons = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        # Time Management
        self.clock = pg.time.Clock()

    def update(self):
        # Time management
        # Update Game Objects and Positions
        self.manage_events()
        self.ships.update()
        self.weapons.update()
        self.sim_gravity()
        self.check_server()
        # Check Collisions
        self.do_collisions()
        # Draw Everything
        self.background.draw(self.screen)
        self.planets.draw(self.screen)
        self.ships.draw(self.screen)
        self.weapons.draw(self.screen)
        self.explosions.draw(self.screen)
        # Flip display to show new stuff
        pg.display.flip()
        # Stable Frame rate
        self.clock.tick(self.tics)

    def manage_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        if pg.key.get_pressed()[pg.K_ESCAPE]:
            pg.quit()
            sys.exit()

    def do_collisions(self):
        pg.sprite.groupcollide(self.ships, self.weapons, True, True)  # Bullet on brick

    def sim_gravity(self):
        pass

    def check_server(self):
        self.con_ship.up_data(self.player_dat)
        self.player_dat = self.network.send(self.player_dat)
        for ship in self.ships:
            ship.new_pos(self.player_dat)
            if ship.health <= 0:
                ship.kill()
