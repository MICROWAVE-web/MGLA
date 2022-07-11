from copy import copy

import os
import pygame
from itertools import cycle as loop_cycle

pygame.init()


class MapEditor:
    """
    Класс редактора карт
    """
    def __init__(self,
                 width=720,
                 height=480,
                 textures_folder='textures',
                 file_directory='map',
                 extension='mglamap',
                 speed_move=1,
                 fps=60,
                 filename='map',
                 background_color=(0, 0, 0),
                 reversed_moving=False):
        """
        Инициализация цикла редактора карт для игры
        :param width:
        :param height:
        :param textures_folder:
        :param file_directory:
        :param extension:
        :param speed_move:
        :param fps:
        :param filename:
        :param background_color:
        :param reversed_moving:
        """
        pygame.init()
        self.sc = pygame.display.set_mode([width, height])
        self.width, self.height = width, height
        self.direction_hint_place_texture = None
        self.filename = filename
        self.file_directory = file_directory
        self.extension = extension
        self.speed_move = speed_move  # <-- int
        self.reverse_int = 1
        self.speed_move_acceleration_x = 0
        self.speed_move_acceleration_y = 0
        if reversed_moving:
            self.reverse_int = -1
        self.all_placed_sprites = []
        self.about_all_sprites = []
        self.__init_textures(textures_folder)
        self.len_of_texture = len(self.about_all_sprites)
        self.about_all_sprites = loop_cycle(self.about_all_sprites)
        self.move_x = 0
        self.move_y = 0

        self.current_selected_texture = self.about_all_sprites.__next__()

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.place_current_texture(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.direction_hint_place_texture = 'up'
                    if event.key == pygame.K_DOWN:
                        self.direction_hint_place_texture = 'down'
                    if event.key == pygame.K_LEFT:
                        self.direction_hint_place_texture = 'left'
                    if event.key == pygame.K_RIGHT:
                        self.direction_hint_place_texture = 'right'
                    if event.key == pygame.K_DELETE:
                        self.direction_hint_place_texture = 'delete'
                    # if event.key == pygame.KMOD_CTRL and event.key == pygame.K_c:
                    # self.copy_texture_map()
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.save_texture_map()
                    if event.key == pygame.K_e:
                        self.next_texture()
                    if event.key == pygame.K_q:
                        self.prev_texture()
                    if event.key == pygame.K_f:
                        self.get_all_cords_of_texture()

            keys = pygame.key.get_pressed()
            plussed = False
            if keys[pygame.K_ESCAPE]:
                running = False
            if keys[pygame.K_w]:
                plussed = True
                self.speed_move_acceleration_y -= 0.1 * self.speed_move
            elif keys[pygame.K_s]:
                plussed = True
                self.speed_move_acceleration_y += 0.1 * self.speed_move
            if keys[pygame.K_a]:
                plussed = True
                self.speed_move_acceleration_x -= 0.1 * self.speed_move
            elif keys[pygame.K_d]:
                plussed = True
                self.speed_move_acceleration_x += 0.1 * self.speed_move
            if not plussed:
                if self.speed_move_acceleration_y <= -0.1:
                    self.speed_move_acceleration_y += 0.1 * self.speed_move
                elif self.speed_move_acceleration_y >= 0.1:
                    self.speed_move_acceleration_y -= 0.1 * self.speed_move
                if self.speed_move_acceleration_x <= -0.1:
                    self.speed_move_acceleration_x += 0.1 * self.speed_move
                elif self.speed_move_acceleration_x >= 0.1:
                    self.speed_move_acceleration_x -= 0.1 * self.speed_move

            self.update_placed_textures()
            self.show_hint(pygame.mouse.get_pos())
            self.display_selected_texture()
            self.display_fps(clock)
            self.direction_hint_place_texture = None
            pygame.display.update()
            self.sc.fill(background_color)
            clock.tick(fps)
        pygame.quit()

    def update_placed_textures(self):
        """
        Обновляет положение текстур и отрисовывает их
        """
        for texture in self.all_placed_sprites:
            self.move_y += self.speed_move_acceleration_y * self.speed_move * self.reverse_int
            self.move_x += self.speed_move_acceleration_x * self.speed_move * self.reverse_int
            # self.move_y, self.move_x = int(self.move_y), int(self.move_x)
            texture['top_left'][1] += self.speed_move_acceleration_y * self.speed_move * self.reverse_int
            texture['top_left'][0] += self.speed_move_acceleration_x * self.speed_move * self.reverse_int
            # texture['top_left'][0], texture['top_left'][1] = int(texture['top_left'][0]), int(texture['top_left'][1])
            self.sc.blit(texture['object'].image, texture['top_left'])

    def get_all_cords_of_texture(self):
        """
        Запись координат текстур в консоль
        """
        for index, texture in enumerate(self.all_placed_sprites, start=1):
            print(index, '-', texture['placed_coordinate'])
        print()

    def display_fps(self, clock):
        """
        Отображение FPS
        """
        font = pygame.font.SysFont('Verdana', 14)
        text = f"{clock.get_fps():2.0f} FPS"
        fps_text = font.render(text, False, (255, 255, 255))
        fps_text_rect = fps_text.get_rect()
        self.sc.blit(fps_text, (self.width - fps_text_rect.width - 20, 20))

    def save_texture_map(self):
        """
        Сохранение карты в файл
        """
        if not os.path.exists(self.file_directory):
            os.makedirs(self.file_directory)
        with open(f'{self.file_directory}{self.filename}.{self.extension}', mode='w+') as f:
            f.writelines("\n".join(
                [f'{int(float(texture["top_left"][0]))}, '
                 f'{int(float(texture["top_left"][1]))}, '
                 f'{int(float(texture["placed_coordinate"][0]))}, '
                 f'{int(float(texture["placed_coordinate"][1]))}, '
                 f'{texture["object_filename"]}' for texture in
                 self.all_placed_sprites]))

    def mouse_collise_with_textures(self, pos):
        """
        Если курсор пересекается с блоком, ф-я возвращает его top-left координаты
        """
        for texture in self.all_placed_sprites:
            if texture['top_left'][0] < pos[0] < texture['top_left'][0] + texture['object'].rect.width and \
                    texture['top_left'][1] < pos[1] < texture['top_left'][1] + texture['object'].rect.height:
                return texture['top_left'], [texture['object'].rect.width, texture['object'].rect.height], texture[
                    'object']
        return False

    def show_hint(self, pos):
        """
        Ф-я обводки текстуры, на которой находится мышь, и расположение текстур в ряд по вертикали и горизонтали
        """
        mcollid = self.mouse_collise_with_textures(pos)
        if mcollid is not False:
            pygame.draw.rect(self.sc, (200, 0, 0),
                             (*mcollid[0], *mcollid[1]), 2)
            if self.direction_hint_place_texture is not None:
                if self.direction_hint_place_texture == 'up':
                    self.place_current_texture((mcollid[0][0], mcollid[0][1] - mcollid[1][1]))
                elif self.direction_hint_place_texture == 'down':
                    self.place_current_texture((mcollid[0][0], mcollid[0][1] + mcollid[1][1]))
                elif self.direction_hint_place_texture == 'left':
                    self.place_current_texture((mcollid[0][0] - mcollid[1][0], mcollid[0][1]))
                elif self.direction_hint_place_texture == 'right':
                    self.place_current_texture((mcollid[0][0] + mcollid[1][0], mcollid[0][1]))
                elif self.direction_hint_place_texture == 'delete':
                    self.all_placed_sprites = [texture for texture in self.all_placed_sprites if
                                               mcollid[0] != texture['top_left']]

    def place_current_texture(self, pos):
        """
        Поставить текстуру на координату мыши
        """
        if not self.mouse_collise_with_textures(pos):
            self.current_selected_texture['top_left'] = list(pos)
            self.current_selected_texture['placed_coordinate'] = [int(list(pos)[0] - self.move_x),
                                                                  int(list(pos)[1] - self.move_y)]
            self.all_placed_sprites.append(copy(self.current_selected_texture))

    def next_texture(self):
        """
        Переключение текущей текстуры
        """
        self.current_selected_texture = self.about_all_sprites.__next__()

    def prev_texture(self):
        """
        Переключение текущей текстуры
        """
        for _ in range(self.len_of_texture - 1):
            self.current_selected_texture = self.about_all_sprites.__next__()

    def __init_textures(self, directory):
        """
        Ф-я инициализации, и загрузки текстур из файла карты
        """
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f) and f.endswith('.png') or f.endswith('.jpg'):  # <-- delete jpg
                self.about_all_sprites.append({
                    'object': Texture(f),
                    'object_filename': filename,
                    'top_left': [0, 0],
                    'placed_coordinate': [0, 0],
                })
        fp = f'{self.file_directory}{self.filename}.{self.extension}'
        if os.path.isfile(fp):
            with open(fp) as f:
                rl = f.readlines()
                for line in rl:
                    read_texture = line.strip().split(', ')
                    texture = self.__get_texture_by_filename(read_texture[4])
                    texture['top_left'] = [int(read_texture[0]), int(read_texture[1])]
                    texture['placed_coordinate'] = [int(read_texture[2]), int(read_texture[3])]
                    self.all_placed_sprites.append(copy(texture))

    def __get_texture_by_filename(self, filename):
        """
        Возвращает объект текстуры, по ее названию файла
        :param filename:
        :return:
        """
        for texture in self.about_all_sprites:
            if texture['object_filename'] == filename:
                return texture

    def display_selected_texture(self):
        """
        Отображение выбранной текстуры
        :return:
        """
        pygame.draw.rect(self.sc, (200, 200, 200),
                         (10, 10, 100, 100))
        pygame.draw.rect(self.sc, (240, 240, 240),
                         (10, 10, 100, 100), 8)
        texture = self.current_selected_texture['object']
        self.sc.blit(texture.image, (60 - texture.rect.width // 2, 60 - texture.rect.height // 2))


class Texture(pygame.sprite.Sprite):
    """
    Класс текстуры
    """
    def __init__(self, texture_path):
        """
        Ф-я инициализации текстур
        :param texture_path:
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(texture_path).convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()


if __name__ == '__main__':
    me = MapEditor(background_color=(55, 55, 55), reversed_moving=True, filename="map", file_directory='map/',
                   extension='mglamap')
