import pygame
import sys
import random
import os
from config import *  # 설정값들을 config.py에서 가져옴

# pygame 초기화
pygame.init()

# 화면 설정
if hasattr(sys, '_MEIPASS'):  # PyInstaller 환경인 경우
    os.chdir(sys._MEIPASS)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Clone')

class Bird:
    def __init__(self):
        self.x = BIRD_X_POS
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = BIRD_GRAVITY
        self.lift = BIRD_LIFT
        self.size = BIRD_SIZE
        
    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        
        # 화면 경계 처리
        if self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.velocity = 0
            return True  # 바닥에 닿으면 True 반환
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        return False
    
    def jump(self):
        self.velocity = self.lift
        
    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))

    def check_collision(self, pipe):
        bird_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        top_pipe = pygame.Rect(pipe.x, 0, pipe.width, pipe.top_height)
        bottom_pipe = pygame.Rect(pipe.x, pipe.bottom_y, pipe.width, SCREEN_HEIGHT - pipe.bottom_y)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = COIN_SIZE
        self.collected = False
        
    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
            
    def check_collision(self, bird):
        if self.collected:
            return False
        bird_center = (bird.x + bird.size/2, bird.y + bird.size/2)
        coin_center = (self.x, self.y)
        distance = ((bird_center[0] - coin_center[0])**2 + (bird_center[1] - coin_center[1])**2)**0.5
        collision_radius = (bird.size + self.size) / 2
        return distance < collision_radius

class Pipe:
    def __init__(self, speed_multiplier=1.0, gap_reducer=0):
        max_gap = max(INITIAL_PIPE_GAP - gap_reducer, MIN_PIPE_GAP)
        self.gap = random.randint(MIN_PIPE_GAP, max_gap)
        self.width = PIPE_WIDTH
        self.x = SCREEN_WIDTH
        self.top_height = random.randint(100, int(SCREEN_HEIGHT - self.gap - 100))
        self.bottom_y = self.top_height + self.gap
        self.speed = PIPE_SPEED
        self.coin = Coin(self.x + self.width/2, self.top_height + self.gap/2)
        
    def update(self):
        self.x -= self.speed
        self.coin.x = self.x + self.width/2
        
    def draw(self):
        pygame.draw.rect(screen, GREEN, (int(self.x), 0, self.width, self.top_height))
        pygame.draw.rect(screen, GREEN, (int(self.x), self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
        self.coin.draw()
        
    def offscreen(self):
        return self.x < -self.width

# 게임 객체 생성
bird = Bird()
pipes = []
score = 0
distance = 0
best_distance = 0
frame_count = 0
game_over = False
spawn_interval = INITIAL_SPAWN_INTERVAL
difficulty_increase_interval = DIFFICULTY_INCREASE_INTERVAL
speed_multiplier = 1.0
gap_reducer = 0

# 게임 루프
clock = pygame.time.Clock()
running = True

while running:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                if not game_over:
                    bird.jump()
                else:
                    bird = Bird()
                    pipes = []
                    score = 0
                    distance = 0
                    frame_count = 0
                    game_over = False
                    speed_multiplier = 1.0
                    gap_reducer = 0
                    spawn_interval = INITIAL_SPAWN_INTERVAL
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                bird.jump()
            else:
                bird = Bird()
                pipes = []
                score = 0
                distance = 0
                frame_count = 0
                game_over = False
                speed_multiplier = 1.0
                gap_reducer = 0
                spawn_interval = INITIAL_SPAWN_INTERVAL
    
    if not game_over:
        frame_count += 1
        distance += speed_multiplier * min(SCREEN_WIDTH / 400, SCREEN_HEIGHT / 600)
        
        # 난이도 증가 로직
        if frame_count % difficulty_increase_interval == 0:
            speed_multiplier += SPEED_INCREASE_RATE
            gap_reducer = min(gap_reducer + GAP_DECREASE_RATE, 250)
            spawn_interval = max(spawn_interval - 5, MIN_SPAWN_INTERVAL)
        
        # 파이프 생성 전에 마지막 파이프와의 거리 확인
        can_spawn = True
        if pipes:
            last_pipe = pipes[-1]
            if SCREEN_WIDTH - last_pipe.x < MIN_PIPE_SPAWN_DISTANCE:
                can_spawn = False
        
        if frame_count % spawn_interval == 0 and can_spawn:
            pipes.append(Pipe(speed_multiplier, gap_reducer))
        
        if bird.update():
            game_over = True
        
        for pipe in pipes[:]:
            pipe.update()
            if bird.check_collision(pipe):
                game_over = True
            if not pipe.coin.collected and pipe.coin.check_collision(bird):
                pipe.coin.collected = True
                score += 1
            if pipe.offscreen():
                pipes.remove(pipe)
    
    # 화면 그리기
    screen.fill(BLACK)
    bird.draw()
    for pipe in pipes:
        pipe.draw()
        
    # 점수와 거리 표시
    font = pygame.font.Font(None, SCORE_FONT_SIZE)
    score_text = font.render(f'Score: {score}', True, WHITE)
    distance_text = font.render(f'Distance: {int(distance)}m', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(distance_text, (10, 10 + SCORE_FONT_SIZE))
    
    # 게임 오버 메시지
    if game_over:
        if distance > best_distance:
            best_distance = distance
            
        game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
        stats_font = pygame.font.Font(None, RESTART_FONT_SIZE)
        
        game_over_text = game_over_font.render('Game Over', True, WHITE)
        current_distance_text = stats_font.render(f'Distance: {int(distance)}m', True, WHITE)
        best_distance_text = stats_font.render(f'Best Distance: {int(best_distance)}m', True, WHITE)
        current_score_text = stats_font.render(f'Score: {score}', True, WHITE)
        restart_text = stats_font.render('Tap to restart', True, WHITE)
        
        center_x = SCREEN_WIDTH // 2
        base_y = SCREEN_HEIGHT // 2 - 100
        line_spacing = int(40 * min(SCREEN_WIDTH / 400, SCREEN_HEIGHT / 600))
        
        screen.blit(game_over_text, (center_x - game_over_text.get_width()//2, base_y))
        screen.blit(current_score_text, (center_x - current_score_text.get_width()//2, base_y + line_spacing))
        screen.blit(current_distance_text, (center_x - current_distance_text.get_width()//2, base_y + line_spacing * 2))
        screen.blit(best_distance_text, (center_x - best_distance_text.get_width()//2, base_y + line_spacing * 3))
        screen.blit(restart_text, (center_x - restart_text.get_width()//2, base_y + line_spacing * 4))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()