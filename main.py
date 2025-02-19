import pygame
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import random
from pygame import mixer

# Screen settings
WIDTH, HEIGHT = 1366, 768

# OpenCV settings
cap = cv2.VideoCapture(1)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# Hand detection settings
detector = HandDetector(maxHands=1, detectionCon=0.8)

# Initialize Pygame
pygame.init()

# Play background music
mixer.music.load('music/background.mp3')
mixer.music.play(loops=-1)
catching_sound = mixer.Sound('music/catching_sound.wav')

# Define display screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Ball")
icon = pygame.image.load('images/ball_32.png').convert_alpha()
pygame.display.set_icon(icon)
backgroundImg = pygame.image.load('images/TennisBack.png').convert()

# Hand settings
openHandImg = pygame.image.load('images/openHand.png').convert_alpha()
openHandImg = pygame.transform.scale(openHandImg, (128, 128))
closedHandImg = pygame.image.load('images/closedHand.png').convert_alpha()
closedHandImg = pygame.transform.scale(closedHandImg, (128, 128))
openHand_rect = openHandImg.get_rect()
closedHand_rect = closedHandImg.get_rect()

# Insects settings
NUM_INSECTS = 10
insects = []
for _ in range(NUM_INSECTS):
    img = pygame.image.load('images/ball_32.png').convert_alpha()
    rect = img.get_rect(topleft=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    move_x, move_y = random.choice([-10, 10]), random.choice([-8, 8])
    speed = 10  # Initial speed for each insect
    insects.append({'img': img, 'rect': rect, 'dx': move_x, 'dy': move_y, 'speed': speed})

# Score and timer settings
score = 0
font = pygame.font.Font('freesansbold.ttf', 32)
gameOver_font = pygame.font.Font('freesansbold.ttf', 100)
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

# Main game loop
running = True
while running:
    screen.blit(backgroundImg, (0, 0))
    
    # Handle game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
    
    # Process image
    success, frame = cap.read()
    hands, frame = detector.findHands(frame)
    
    if hands:
        lmList = hands[0]['lmList']
        hand_x = lmList[9][0]
        hand_y = lmList[9][1]
        
        # Mirror X-axis for correct hand movement
        fixed_x = WIDTH - (hand_x * 1.5)
        fixed_y = hand_y * 1.5
        
        # Detect open or closed hand
        fingers = [lmList[i][1] > lmList[i-2][1] for i in [8, 12, 16, 20]]
        hand_closed = all(fingers)
        
        # Set hand position in the game
        if hand_closed:
            closedHand_rect.topleft = (fixed_x - 64, fixed_y - 64)
            screen.blit(closedHandImg, closedHand_rect)
        else:
            openHand_rect.topleft = (fixed_x - 64, fixed_y - 64)
            screen.blit(openHandImg, openHand_rect)
        
        # Check if insects are caught and increase speed only for the caught insect
        for insect in insects:
            if closedHand_rect.colliderect(insect['rect']) and hand_closed:
                catching_sound.play()
                score += 1
                
                # Relocate only the caught insect
                insect['rect'].topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

                # Increase speed only for the caught insect
                insect['dx'] *= 1.2  # Increase X-axis speed
                insect['dy'] *= 1.2  # Increase Y-axis speed
    
    # Move insects
    for insect in insects:
        insect['rect'].x += insect['dx']
        insect['rect'].y += insect['dy']
        
        # Handle wall collisions
        if insect['rect'].left <= 0 or insect['rect'].right >= WIDTH:
            insect['dx'] *= -1
        if insect['rect'].top <= 0 or insect['rect'].bottom >= HEIGHT:
            insect['dy'] *= -1
    
        screen.blit(insect['img'], insect['rect'])
    
    # Display score and timer
    elapsed_time = (pygame.time.get_ticks() - startTime) // 1000
    timer_text = font.render(f"Time: {30 - elapsed_time}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(timer_text, (WIDTH - 150, 10))
    screen.blit(score_text, (10, 10))
    
    # End game condition
    if elapsed_time >= 30:
        game_over_text = gameOver_font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 300, HEIGHT // 2 - 30))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False
    
    # Show webcam frame
    cv2.imshow("Webcam", frame)
    
    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
