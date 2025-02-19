import pygame
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import random
from pygame import mixer

# تنظیمات صفحه
WIDTH, HEIGHT = 1366, 768

# تنظیمات OpenCV
cap = cv2.VideoCapture(1)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# تنظیمات تشخیص دست
detector = HandDetector(maxHands=1, detectionCon=0.8)

# راه‌اندازی Pygame
pygame.init()

# پخش موسیقی پس‌زمینه
mixer.music.load('music/background.mp3')
mixer.music.play(loops=-1)
closedHand_sound = mixer.Sound('music/slap.mp3')
catching_sound = mixer.Sound('music/catching_sound.wav')

# تعریف صفحه نمایش
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Ball")
icon = pygame.image.load('images/ball_32.png').convert_alpha()
pygame.display.set_icon(icon)
backgroundImg = pygame.image.load('images/TennisBack.png').convert()

# تنظیمات دست
openHandImg = pygame.image.load('images/openHand.png').convert_alpha()
openHandImg = pygame.transform.scale(openHandImg, (128, 128))
closedHandImg = pygame.image.load('images/closedHand.png').convert_alpha()
closedHandImg = pygame.transform.scale(closedHandImg, (128, 128))
openHand_rect = openHandImg.get_rect()
closedHand_rect = closedHandImg.get_rect()

# تنظیمات حشرات
NUM_INSECTS = 10
insects = []
for _ in range(NUM_INSECTS):
    img = pygame.image.load('images/ball_32.png').convert_alpha()
    rect = img.get_rect(topleft=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    move_x, move_y = random.choice([-10, 10]), random.choice([-8, 8])
    insects.append({'img': img, 'rect': rect, 'dx': move_x, 'dy': move_y})

# تنظیمات امتیاز و تایمر
score = 0
font = pygame.font.Font('freesansbold.ttf', 32)
gameOver_font = pygame.font.Font('freesansbold.ttf', 100)
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

# حلقه اصلی بازی
running = True
while running:
    screen.blit(backgroundImg, (0, 0))
    
    # رویدادهای بازی
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
    
    # پردازش تصویر
    success, frame = cap.read()
    hands, frame = detector.findHands(frame)
    
    if hands:
        lmList = hands[0]['lmList']
        hand_x = lmList[9][0]
        hand_y = lmList[9][1]
        
        # قرینه کردن محور X برای حرکت صحیح دست
        fixed_x = WIDTH - (hand_x * 1.5)
        fixed_y = hand_y * 1.5
        
        # تشخیص باز یا بسته بودن دست
        fingers = [lmList[i][1] > lmList[i-2][1] for i in [8, 12, 16, 20]]
        hand_closed = all(fingers)
        
        # تنظیم موقعیت دست در بازی
        if hand_closed:
            closedHand_rect.topleft = (fixed_x - 64, fixed_y - 64)
            screen.blit(closedHandImg, closedHand_rect)
        else:
            openHand_rect.topleft = (fixed_x - 64, fixed_y - 64)
            screen.blit(openHandImg, openHand_rect)
        
        # بررسی گرفتن حشرات
        for insect in insects:
            # Only catch insects when hand is closed
            if closedHand_rect.colliderect(insect['rect']) and hand_closed:
                catching_sound.play()
                score += 1
                insect['rect'].topleft = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    
    # حرکت حشرات
    for insect in insects:
        insect['rect'].x += insect['dx']
        insect['rect'].y += insect['dy']
        
        # برخورد با دیواره‌ها
        if insect['rect'].left <= 0 or insect['rect'].right >= WIDTH:
            insect['dx'] *= -1
        if insect['rect'].top <= 0 or insect['rect'].bottom >= HEIGHT:
            insect['dy'] *= -1
        
        screen.blit(insect['img'], insect['rect'])
    
    # نمایش امتیاز و تایمر
    elapsed_time = (pygame.time.get_ticks() - startTime) // 1000
    timer_text = font.render(f"Time: {100 - elapsed_time}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(timer_text, (WIDTH - 150, 10))
    screen.blit(score_text, (10, 10))
    
    # پایان بازی
    if elapsed_time >= 100:
        game_over_text = gameOver_font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 300, HEIGHT // 2 - 30))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False
    
    # نمایش فریم دوربین
    cv2.imshow("Webcam", frame)
    
    # بروزرسانی صفحه
    pygame.display.update()
    clock.tick(60)

pygame.quit()
