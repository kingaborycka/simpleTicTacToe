import pygame as pg
import numpy as np
import re
import math
import random as r


#strona ze znakami/symbolami
#https://www.compart.com/en/unicode/category/So

class Player():
    def __init__(self, name):
        self.sign = 1  
        self.name = name  

    @staticmethod
    def move(a, b):
        turn = board.whoPlay()
        pattern = re.compile(r".+("+ str(a) +", "+ str(b) +").+")
        s = board.s_list[a][b] #odwołanie do obiektu Square(a,b)

        if s.getValue() == 0:
            s.setValue(turn.sign) #wstawienie wartości -1 -> kółko, 1 -> krzyżyk
            print(s.getValue(), "turn = ", turn.sign)
            for key, value in board.goals.items():
                if re.match(pattern, key):
                    board.goals[key] += turn.sign

            if turn.sign == 1:
                board.computer.setChanceOfWinning(a,b)

            del board.computer.empty_pattern[(a, b)]
            board.move += 1 #zliczanie ruchów

            board.printBoard()
            print("move:",board.move)
            return True
        else: 
            return False
                

class Computer(Player): #kółko -> -1
    def __init__(self,name):
        self.sign = -1
        self.name = name  

        #priority levels of empty squares 0 -> nieważne, 1 -> potrzebne 2 ruchy do wygranej, 2 -> 2 ruchy do wygranej przeciwnika, 3 -> 1 blokuj wygraną przeciwnika, 4 -> 1 ruch do wygranej
        #drugi element tablicy = ilość możliwości wygranej przez komputer
        self.empty_pattern = {  (0, 0):[0,3],
                                (0, 1):[0,2],
                                (0, 2):[0,3],
                                (1, 0):[0,2],
                                (1, 1):[0,4],
                                (1, 2):[0,2],
                                (2, 0):[0,3],
                                (2, 1):[0,2],
                                (2, 2):[0,3] }

    def setChanceOfWinning(self, a, b):
        # po wstawieniu przez gracza znaku, sprawdzamy ile pozostaje możliwości wygranej dla każdego kwadratu
        
        pattern = re.compile(r".+("+ str(a) +", "+ str(b) +").+")
        m = '('+str(a)+', '+str(b)+')' #bieżący ruch
        lower_chance = True

        for goals_key in board.goals.keys():
            if re.match(pattern, goals_key):
                squares_list = goals_key.split(";") #lista kwadratów do zmniejszenia szansy wygranej
                if m in squares_list: squares_list.remove(m)
                print(squares_list)
                
                for square in squares_list:
                    a,b = int(square[1]), int(square[4])
                    s = board.s_list[a][b]
                    print("Value:", s.getValue())
                    if s.getValue() == 1:
                        lower_chance = False
  
                if lower_chance:
                    for square in squares_list:    
                        for empty_pattern_key in board.computer.empty_pattern.keys():
                            if str(empty_pattern_key) == str(square):
                                board.computer.empty_pattern[empty_pattern_key][1] -= 1

    def move(self):
        empty = self.empty_pattern.copy()
        best_choices = []
        for empty_key in empty.keys():
            pattern = re.compile(r".+("+ str(empty_key[0]) +", "+ str(empty_key[1]) +").+")
            for goals_key, goals_value in board.goals.items():
                if re.match(pattern,goals_key):
                    if goals_value == -2:
                        empty[empty_key][0] = max(empty[empty_key][0],4)
                    elif goals_value == 2:
                        empty[empty_key][0] = max(empty[empty_key][0],3)
                    elif goals_value == 1:
                        empty[empty_key][0] = max(empty[empty_key][0],2)
                    elif goals_value == -1: 
                        empty[empty_key][0] = max(empty[empty_key][0],1)
                    else:
                        empty[empty_key][0] = max(empty[empty_key][0],0)
        if empty:
            if (1, 1) in empty:
                Player.move(1,1)
            else:
                choice = max(empty.values())

                while choice == [2, 0]:
                    for key, value in empty.items():
                        if value == choice:
                            empty[key] = [0, 0]

                    choice = max(empty.values())
        
                for key, value in empty.items():
                    if value == choice:
                        best_choices.append((key[0],key[1]))
                
                choice = r.choice(best_choices)
                Player.move(choice[0],choice[1])
                
                print("\nEMPTY:\n", empty)
                print("choice:", choice)
        


class Square():
    #Klasa reprezentująca pole, w które można wstawić kółko lub krzyżyk

    def __init__(self, name, screen, left, top, width, height):
        self.screen = screen
        self.name = name #(a,b) -> położenie na planszy
        self.value = 0 # 0 -> puste , -1 -> kółko, 1 -> krzyżyk

        self.dimension = ( left, top, width, height) #(left, top, width, height)
        self.square = pg.draw.rect(self.screen,(255,255,255), self.dimension)
        self.circle = pg.font.Font(None,22).render(chr(0x97),False, (0,0,0))
        self.cross = pg.font.Font(None,22).render(chr(0x95),False, (0,0,0))

    def __repr__(self):
        return f'Square({self.name}, value = {self.value})'

    # def setValue(self, value):
    #     if value == -1:
    #         rect = self.circle.get_rect()
    #         self.screen.blit(self.circle, rect)
    #         print(chr(168))
    #     else:
    #         rect = self.cross.get_rect()
    #         self.screen.blit(self.cross, rect)
    #         print("ZNAKs",chr(195))

    def setValue(self, value):
        self.value = value
        if value == 1:
            color = (255,0,0) 
        else: 
            color = (0,255,0)
            
        sub = (-15,-15,34,34)
        pg.draw.rect(self.screen, color, [self.dimension[i] - sub[i] for i in range(4)])

    def getValue(self):
        return self.value

class Board():
    #Klasa reprezentująca planszę do gry

    def __init__(self,name):        
        self.s_list = [[0,0,0],[0,0,0],[0,0,0]]
        self.player = Player(name)
        self.computer = Computer("Komputer")
        self.move = 0

        self.goals = {
            #sukces => -3 lub 3
            '(0, 0);(0, 1);(0, 2)':0,#row1
            '(1, 0);(1, 1);(1, 2)':0,#row2
            '(2, 0);(2, 1);(2, 2)':0,#row3
            '(0, 0);(1, 0);(2, 0)':0,#col1
            '(0, 1);(1, 1);(2, 1)':0,#col2
            '(0, 2);(1, 2);(2, 2)':0,#col3
            '(0, 0);(1, 1);(2, 2)':0,#dm1
            '(0, 2);(1, 1);(2, 0)':0 #dm2
        }


    def prepare(self):
        screen = pg.display.set_mode((500,500))

        #zapis do poprawki
        self.s_list[0][0] = Square((0,0),screen,2,2,164,164)
        self.s_list[0][1] = Square((0,1),screen,168,2,164,164)
        self.s_list[0][2] = Square((0,2),screen,334,2,164,164)
        self.s_list[1][0] = Square((1,0),screen,2,168,164,164)
        self.s_list[1][1] = Square((1,1),screen,168,168,164,164)
        self.s_list[1][2] = Square((1,2),screen,334,168,164,164)
        self.s_list[2][0] = Square((2,0),screen,2,334,164,164)
        self.s_list[2][1] = Square((2,1),screen,168,334,164,164)
        self.s_list[2][2] = Square((2,2),screen,334,334,164,164)
    
    def whoPlay(self):
        if self.move % 2 == 0:
            return self.player
        else:
            return self.computer
    
    def check_winner(self):
        if board.winner() != 0:
            print("Zwyciężył/a "+ board.winner() +"!")
            return False
        return True

    def winner(self):
        if 3 in board.goals.values():
            if board.computer.sign == 1:
                return board.computer.name
            else: 
                return board.player.name
        elif -3 in board.goals.values():
            if board.computer.sign == -1:
                return board.computer.name
            else:
                return board.player.name
        else:
            return 0

    def printBoard(self):
        print(f'\n[[{self.s_list[0][0].getValue(),self.s_list[0][1].getValue(),self.s_list[0][2].getValue()}]\n[{self.s_list[1][0].getValue(),self.s_list[1][1].getValue(),self.s_list[1][2].getValue()}]\n[{self.s_list[2][0].getValue(),self.s_list[2][1].getValue(),self.s_list[2][2].getValue()}]]')

    def __repr__(self):
        return f'[[{self.s_list[0][0],self.s_list[0][1],self.s_list[0][2]}]\n[{self.s_list[1][0],self.s_list[1][1],self.s_list[1][2]}]\n[{self.s_list[2][0],self.s_list[2][1],self.s_list[2][2]}]]'

pg.font.init()
run = True

name = input("Podaj imię: ")
# sign = input("Wybierz znak, którym chcesz grać (-1 -> kółko, 1 -> krzyżyk): ")

board = Board(name)
board.prepare()

while run:
    
    pg.time.delay(100)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        
        if board.move == 9:
            print("REMIS!")
            run = False

        turn = board.whoPlay()

        if event.type == pg.MOUSEBUTTONDOWN and turn == board.player: #kliknięcie/wstawienie kółka lub krzyżyka
            if pg.mouse.get_pressed()[0]:
                position = pg.mouse.get_pos()
                a = position[1]//167
                b = position[0]//167

                if Player.move(a, b):    
                    print("Po ruchu gracza",board.goals)  

                    run = board.check_winner()

                    if run:
                        board.computer.move()
                        print("Po ruchu pc",board.goals)
                        run = board.check_winner()
                        pg.display.update()              

    pg.display.update()


