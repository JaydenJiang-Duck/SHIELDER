import pygame, math, random

pygame.init()
pygame.font.init()

#setup variables
screen_x = 500
screen_y = 500
black = (0,0,0)
hp_bar_color = (0,255,25)
catchup_hp_bar_color = (250,250,250)
ability_bar_color = (255,255,255)
slant = 4 # slant on the blocks

#player variables
player_x = screen_x/2
player_y = screen_y/2

player_color = (255,255,255)
player_speed = 1
player_radius = 10
player_max_hp = 100
player_hp = player_max_hp
player_display_hp = player_max_hp
player_hp_delay = 0

#shield & mouse variables
mouse_x, mouse_y = pygame.mouse.get_pos()
angle = math.atan2(mouse_y - player_y,mouse_x - player_x)

shield_radius = 20 #you can add more numbers here
shield_color = (255,255,255)
shield_length = 2.5
shield_width = 3
shield_state = "idle"
shield_base_attack = "bash"

#types
bash = {'min': 0, 'max': 20, 'speed': 2, 'damage': 1, 'hits' : []} #hits is the # of zombies hit
shield_offset = 0.0

#global zombie variables
zombie_color = (50,255,100)
zombie_health = 3
zombie_radius = 10 
zombie_speed = 0.5
zombie_tick = 0
zombie_place_tick = 100
zombies = []
zombie_id = 0

#abilites
abilities_max = 3
abilities = []

dash = {'speed': 7, 'duration': 12, 'timer': 0, 'dx': 0, 'dy': 0, 'damage':3, 'hits':[]}


#other
font = pygame.font.SysFont("couriernew", 18, bold = True, italic = True)
screen = pygame.display.set_mode((screen_x,screen_y))
running = True
game_state = "playing"



def player_keys():
#keys = moving
    global player_x, player_y
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_y += player_speed

def player_attack():
    global shield_state
    if shield_state == "idle":
        shield_state = "bash"
    
def walls(): 
#left and right
    global player_x, player_y, shield_y
    if player_x < player_radius:
        player_x = player_radius
    if player_x > screen_x - player_radius:
        player_x = screen_x - player_radius

#top and down
    if player_y < player_radius:
            player_y = player_radius
    if player_y > screen_y - player_radius:
        player_y = screen_y - player_radius

def spawn_zombie():
    global zombie_id

    #random side
    edge = random.randint(1,4)
    if edge == 1:
        x = random.randint(0,screen_x)
        y = 0
    elif edge == 2:
        x = random.randint(0,screen_x)
        y = screen_y
    elif edge == 3:
        x = 0
        y = random.randint(0,screen_x)
    elif edge == 4:
        x = screen_x
        y = random.randint(0,screen_x)

    #set up zombie
    zombie = {'id': zombie_id, 
              'x': x,
              'y': y, 
              'health': zombie_health, 
              'speed': zombie_speed,
              'damage': 1,
              'attack_cd': 0,}
    zombie_id += 1
    return zombie

def hp_bar():
    global player_hp, player_display_hp, player_hp_delay, slant

    if player_hp_delay > 0:
        player_hp_delay -= 1
    else:
        if player_display_hp > player_hp:
            player_display_hp -= .35
            if player_display_hp < player_hp:
                player_display_hp = player_hp

    hp_x = 15
    hp_y = 25
    width = 10

    hp_text_color = (0,0,0)
    hp_text = font.render("HP", True, hp_text_color)
    o_width, o_height = hp_text.get_size()
    stretched_hp_text = pygame.transform.scale(hp_text, (o_width*1.5,o_height))

    #catchup hp bar
    white_points = [ 
            (hp_x, hp_y), #top left
            (hp_x + (player_display_hp * 2), hp_y), #top right
            (hp_x+slant +  (player_display_hp * 2), hp_y - width), #bottom left
            (hp_x+slant, hp_y - width), #bottom right
        ]
    

    #main green hp bar
    hp_points = [ 
        (hp_x, hp_y), #top left
        (hp_x + (player_hp * 2), hp_y), #top right
        (hp_x+4 +  (player_hp * 2), hp_y - width), #bottom left
        (hp_x+4, hp_y - width), #bottom right
    ]

    if player_display_hp > 0:
        pygame.draw.polygon(screen, catchup_hp_bar_color, white_points)
    if player_hp > 0:
            pygame.draw.polygon(screen, hp_bar_color, hp_points)
    
    screen.blit(stretched_hp_text, (hp_x+10, hp_y-13))

def ability_bar():
    global slant

    width = 10
    length = 45
    ab_y = 25
    bars = 3

    for a in range(bars):
        block_offset = a * (length + 15)
        start_x = screen_x - 15 - block_offset

        ability_bar = [ 
            (start_x - length, ab_y),              
            (start_x, ab_y),                       
            (start_x + slant, ab_y - width),       
            (start_x + slant - length, ab_y - width) 
        ]

        pygame.draw.polygon(screen, ability_bar_color, ability_bar)

def dev_window():
    dev_data = [
        f"PLAYER HP: {int(player_hp)/int(player_max_hp)}"
        f"SHIELD STATE: {shield_state}",
        f"SHIELD OFFSET: {int(shield_offset)}",
        f"DASH DURIATION: {dash['duration']}",
        f"ACTIVE ZOMBIES: {len(zombies)}"
    ]

    start_x = 15
    start_y = screen_y-50
    line_height = 10

    for index, text_string in enumerate(dev_data):
        text_color = (0,255,255)
        rendered_text = font.render(text_string, True, text_color)

        current_y = start_y + (index * line_height)
        screen.blit(rendered_text, (start_x, current_y))

def death_screen():
    overlay = pygame.Surface((screen_x, screen_y), pygame.SCRALPHA)
    overlay.fill(0,0,0,180)
    screen.bilt(overlay, (0,0))

    game_over_font = pygame.font.SysFont("couriernew", 36, bold=True)
    title_surface = game_over_font.render("GAME OVER", True, (255, 50, 50))
    title_rect = title_surface.get_rect(center=(screen_x //2, screen_y // 2 - 50))
    screen.blit(title_surface, title_rect)

    prompt_surface1 = font.render("Press 'R' to Restart", True, (255,255,255))
    prompt_rect1 = prompt_surface1.get_rect(centrer = (screen_x // 2, screen_y // 2 + 20))
    screen.blit(prompt_surface1, prompt_rect1)

    prompt_surface2 = font.render("Press 'Q' to Quit", True, (200,200,200))
    prompt_rect2 = prompt_surface2.get_rect(center = (screen_x // 2, screen_y // 2 + 50))
    screen.blit(prompt_surface2, prompt_rect2)

def reset_game():
    global player_x, player_y, player_hp, player_display_hp, player_hp_delay
    global zombies, zombie_tick, shield_state, shield_offset, game_state

    player_x = screen_x / 2
    player_y = screen_y / 2
    player_hp = player_max_hp
    player_display_hp = player_max_hp
    player_hp_delay = 0

    shield_state = "idle"
    shield_offset = 0.0

    zombies = []
    zombie_tick = 0
    game_state = "playing"

while running:  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False

 #functions
    player_keys() 
    walls()

    #specific functions
    if event.type == pygame.MOUSEBUTTONDOWN:
        player_attack()

    #drawing
    screen.fill(black)
    pygame.draw.circle(screen, player_color, (player_x, player_y), player_radius)

    #shield drawing
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.atan2(mouse_y - player_y, mouse_x - player_x)

    shield_rect = (player_x - shield_radius, player_y - shield_radius, shield_radius * 2, shield_radius * 2)

    start_angle = -angle - shield_length /2
    end_angle = -angle + shield_length /2

    #shield action
    if shield_state == "bash":
        shield_offset += bash['speed']
        if shield_offset >= bash['max']:
            shield_state = "retract"
    elif shield_state == "retract":
        shield_offset -= (bash['speed']) / 3
        if shield_offset<= bash['min']:
            shield_offset = bash['min']
            shield_state = "idle"

    shield_center_x = player_x + math.cos(angle) * shield_offset
    shield_center_y = player_y + math.sin(angle) * shield_offset

    shield_rect = (shield_center_x - shield_radius, shield_center_y - shield_radius, shield_radius * 2, shield_radius * 2)

    #zombies
    zombie_tick += 1
    if zombie_tick >= zombie_place_tick:
        zombies.append(spawn_zombie())
        zombie_tick = 0

    for z in zombies[:]:
        #zombie movement\
        dx = player_x - z['x']
        dy = player_y - z['y']
        distance = math.hypot(dx,dy)

        if distance > 0:
            z['x'] += (dx/distance) * zombie_speed
            z['y'] += (dy/distance) * zombie_speed

        current_dx = player_x - z['x']
        current_dy = player_y - z['y']
        current_distance = math.hypot(current_dx, current_dy)
        #shield check zombies
        
        #this one i stole from the internet, too hard
        zombie_angle = math.atan2(z['y'] - player_y, z['x'] - player_x)
        angle_difference = (zombie_angle - angle + math.pi) % (2 * math.pi) - math.pi

        shield_check = abs(angle_difference) <= (shield_length/2)
        shield_hit_distance = shield_radius + zombie_radius

        if current_distance > 0 and current_distance <= shield_hit_distance and shield_check:
            #pushhhhhh
            push_dx = (z['x'] - player_x) / current_distance
            push_dy = (z['y'] - player_y) / current_distance

            if shield_state == "bash":
                if z["id"] not in bash ['hits']:
                    z['health'] -= bash["damage"]

                z['x'] = player_x + push_dx * (shield_hit_distance + 30)
                z['y'] = player_y + push_dy * (shield_hit_distance + 30)

                if z['health'] <= 0:
                    if z in zombies:
                        zombies.remove(z)
                    continue
            else:

                z['x'] = player_x + push_dx * shield_hit_distance
                z['y'] = player_y + push_dy * shield_hit_distance

        # player and zombie collision
        player_distance = math.hypot(player_x - z['x'], player_y - z['y'])
        total_radius = player_radius + zombie_radius

        if z['attack_cd'] > 0:
            z['attack_cd'] -= 1

        if player_distance < player_radius + zombie_radius:
            #did they overlap? 
            overlap = total_radius - player_distance

            #set up push
            push_dx = (z['x'] - player_x) / player_distance
            push_dy = (z['y'] - player_y) / player_distance

            #push
            z['x'] += push_dx * overlap
            z['y'] += push_dy * overlap

            #zombie attack
            if z['attack_cd'] == 0:
                player_hp -= z['damage']
                player_hp_delay = 20
                z['attack_cd'] = 60 #60 frames = 1 second

        #zombie and zombie collision
        for other_z in zombies:
            if z != other_z:
                z_distance = math.hypot(z['x'] - other_z['x'], z['y'] - other_z['y'])
                zombie_total_radius = zombie_radius * 2
                if z_distance < zombie_total_radius and z_distance > 0:

                    #did they overlap?
                    overlap = zombie_total_radius - z_distance

                    #set up push
                    push_dx = (z['x'] - other_z['x']) / z_distance
                    push_dy = (z['y'] - other_z['y']) / z_distance

                    #push
                    z['x'] += push_dx * (overlap / 2)
                    z['y'] += push_dy * (overlap / 2)


    for z in zombies:
        #draws all the zombies
        pygame.draw.circle(screen, zombie_color, (int(z['x']), int(z['y'])), zombie_radius)

    pygame.draw.arc(screen, shield_color, shield_rect, start_angle, end_angle, shield_width)

    #if event.type == pygame:
    #dev_window()
    ability_bar()
    hp_bar()

    if game_state == "playing":
        player_keys()
        walls()
    
    if player_hp <= 0:
        game_state = "gameover"
    
    screen.fill(black)
    pygame.draw.circle(screen, zombie_color, (int(z['x']),int(z['y'])),zombie_radius)

    if game_state == "playing":
        pygame.draw.arc(screen, shield_color, shield_rect, start_angle, end_angle, shield_width)

    if game_state == "gameover":
        death_screen()

    pygame.display.flip()


pygame.quit()
