import pyxel, random

# si pyxel n'est pas installé (pour linux ubuntu): 
#sudo apt install pipx
#pipx install pyxel
#pyxel run /chemin_a_remplir/escrime.py

q,d,v,b,n=pyxel.KEY_Q,pyxel.KEY_D,pyxel.KEY_V,pyxel.KEY_B,pyxel.KEY_N
l,r,k1,k2,k3=pyxel.KEY_LEFT,pyxel.KEY_RIGHT,pyxel.KEY_KP_1,pyxel.KEY_KP_2,pyxel.KEY_KP_3
list_keys_p1=[q,d,v,b,n]
list_keys_p2=[l,r,k1,k2,k3]

class Game:
    def __init__(self):

        # taille de la fenetre 160x112 pixels
        pyxel.init(160, 112, title="Deadly Fencing")
        pyxel.load("ressource.pyxres")
        #rendre la souris visible
        pyxel.mouse(True)
        
        #init des joueurs
        self.player_1=Player(20,47,(0,0),1,0,list_keys_p1)
        self.player_2=Player(130,47,(0,8),-1,1,list_keys_p2)
        self.list_players=[self.player_1,self.player_2]
    
        self.end_game = False
        self.winner = "BOB"
        self.round_winner=None
        self.clock=0
        self.timer_animation_parry=0
        self.start_animation_parry=False
        self.is_in_main_menu=True
        self.is_music_on=True
        self.music=pyxel.playm(0,loop=True)
        self.music_timer=0
        
        pyxel.run(self.update, self.draw)
        
    def hitbox_players(self):
        # Hitbox des épées
        if self.test_hitbox(self.player_1,self.player_2) and not self.player_1.is_disarmed and self.player_1.is_attacking:
            # si le joueur 2 bloque, il se fait parrer, sinon il le tue
            if self.player_2.is_parrying:
                self.got_parried(self.player_1,self.player_2)
            else:
                self.killed_player(self.player_1,self.player_2)

        if self.test_hitbox(self.player_2,self.player_1) and not self.player_2.is_disarmed and self.player_2.is_attacking:
            if self.player_1.is_parrying:
                self.got_parried(self.player_2,self.player_1)
            else:
                self.killed_player(self.player_2,self.player_1)
                
        # changement direction si ils se rentrent dedans     
        if self.player_1.x >= self.player_2.x  and self.player_2.x <= self.player_1.x:
            self.player_1.orientation= -1
            self.player_2.orientation=  1    
        else:
            self.player_1.orientation=  1
            self.player_2.orientation=  -1
        #on remet à jour les hitbox des épées
        self.player_1.hitbox_sword = self.sword_hitbox_maker(self.player_1)
        self.player_2.hitbox_sword = self.sword_hitbox_maker(self.player_2)
    
    
    def got_parried(self,player_att,player_def):
        # player_att se fait parrer
        player_att.is_disarmed=True
        player_att.timer_disarmed=pyxel.frame_count
        player_def.timer_parry-=20
        self.start_animation_parry=True
        pyxel.play(0,4)
        
        
    def killed_player(self,player_att,player_def):
        #player_att tue player_def
        player_def.is_alive=False
        player_def.smoke_list.clear()
        self.round_winner=player_att
        self.round_winner.score+=1
        pyxel.play(0,3)
        
        
    def test_hitbox(self,player_att,player_def):
        #renvoie True si l'épée de player_att touche l'autre sinon False
        if player_att.hitbox_sword[0] >= player_def.x  and player_att.hitbox_sword[0] <= player_def.x+8:
            return True
        return False
            
    def is_a_draw(self):
        #si les 2 joueurs ont 5 points renvoie True sinon False
        if self.player_1.score>=5 and self.player_2.score>=5:
            return True
        else:
            return False    
    
    def end_round(self):
        # à la fin du round remet tout à sa place d'origine
        
        if self.player_1.score>=5:
            #si le joueur a >=5 le désigne gagnant
            self.winner="1"
            self.end_game=True
            self.clock=0
            pyxel.play(0,6)
        if self.player_2.score>=5:
            self.winner="2"
            self.end_game=True
            self.clock=0
            pyxel.play(0,6)
                
        self.player_1.orientation=  1
        self.player_2.orientation=  -1
        self.player_1.x=20
        self.player_2.x=130
        for player in self.list_players: 
            player.hitbox_sword= self.sword_hitbox_maker(player)
            player.is_disarmed= False
            player.timer_death=0
            player.is_alive=True
        
        
    def sword_hitbox_maker(self,player):
        #fabrique la hitbox de l'épée
        if player.orientation==1:
            return [player.x+16 ,player.y+5]
        else:
            return [player.x-8,player.y+5]
        
    def animation_parry(self,player):
        #créer une étincelle au parry réussit
        if self.start_animation_parry:
            #tous les 2 frames jusqu'a 6 frames 
            if pyxel.frame_count % 2 == 0 and self.timer_animation_parry<3:
                    self.timer_animation_parry+=1
            pyxel.blt(player.x+8*player.orientation, player.y, 0,32+(8*(self.timer_animation_parry)),16,8,8,0)
            if self.timer_animation_parry>2:
                #fin de l'animation
                self.start_animation_parry=False
        else:
            self.timer_animation_parry=0
    
    def trigger_music(self):
        #active ou non la musique
        if not self.is_music_on:
            pyxel.stop()
        else:
            pyxel.playm(0,loop=True)
        

            
    def fight_menu(self):
        #Menu de combat
        
        pyxel.bltm(0,0,0,4,9,160,120)
        #Textes
        pyxel.text(5,5, 'Score P1 :'+ str(self.player_1.score), 7)
        pyxel.text(110,5, 'Score P2 :'+ str(self.player_2.score), 7)
        pyxel.text(75,5, str(self.clock//30), 0)
            
    def main_menu(self):
        #Menu Principal
        
        pyxel.bltm(0,0,0,200,0,160,120)
        pyxel.text(120,30, 'Walk', 7)
        pyxel.text(10,93, 'Attack', 7)
        pyxel.text(47,93, 'Dash', 7)
        pyxel.text(117,93, 'Parry', 7)
        pyxel.text(35,13, 'First to 5 points wins !', 7)
        if self.is_music_on==False:
            pyxel.blt(136,8,0,64,160,16,16)
        
            
    def death_menu(self):
        #Menu de fin de partie
        
        pyxel.bltm(0,0,0,392,0,160,120)
        pyxel.text(15,50, 'GAME OVER (presse enter to restart)', 7)
        if self.is_a_draw():
            pyxel.text(48,60, f'DRAW ! NOBODY WON', 7)
            pyxel.blt(70, 80, 0,80,104,32,8,0)
        else:
            pyxel.text(48,60, f'PLAYER {self.winner} HAS WON', 7)
            if self.player_1.score>=5:
                pyxel.blt(70, 72, 0,80,128,32,16,0)
            elif self.player_2.score>=5:
                pyxel.blt(70, 72, 0,80,112,32,16,0)
             
        
    # =====================================================
    # == UPDATE
    # =====================================================
    def update(self):
        
        self.clock+= 1
        """mise à jour des variables (30 fois par seconde)"""
        if pyxel.btn(pyxel.KEY_ESCAPE):
            exit()
          
        if self.is_in_main_menu:
            if self.music_timer>0:
                self.music_timer-=1
            else:
                self.music_timer=0 
            # Boutons 
            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and pyxel.mouse_x<100 and pyxel.mouse_y<70 and pyxel.mouse_x>65 and pyxel.mouse_y>40:
                self.is_in_main_menu=False
            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and pyxel.mouse_x<25 and pyxel.mouse_y<25 and pyxel.mouse_x>5 and pyxel.mouse_y>5:
                exit()
            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and pyxel.mouse_x<150 and pyxel.mouse_y<25 and pyxel.mouse_x>130 and pyxel.mouse_y>5:
                if self.music_timer==0:
                    if self.is_music_on:
                        self.is_music_on=False
                        self.music_timer=10
                        
                    else:
                        self.is_music_on=True
                        self.music_timer=10
                        
                    self.trigger_music()
                
                
                
        else:
            
            if not self.end_game:
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and pyxel.mouse_x<90 and pyxel.mouse_y<120 and pyxel.mouse_x>55 and pyxel.mouse_y>90:
                    self.is_in_main_menu=True
                    self.clock=0
                    self.player_1.score=0
                    self.player_2.score=0
                    self.end_round()
                    
                for player in self.list_players:
                    if player.is_alive:
                        player.input()
                        player.cooldowns()
                        
                if self.player_2.is_alive and self.player_1.is_alive:    
                    self.hitbox_players()  
                else:
                    if pyxel.btn(pyxel.KEY_SPACE):
                        self.end_round()
                        
            else:
                
                if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and pyxel.mouse_x<100 and pyxel.mouse_y<120 and pyxel.mouse_x>65 and pyxel.mouse_y>90:
                    self.end_game= False
                    self.is_in_main_menu=True
                    self.player_1.score,self.player_2.score=0,0
                if pyxel.btn(pyxel.KEY_KP_ENTER):
                    self.end_game=False
                    self.player_1.score,self.player_2.score=0,0
                
                
    # =====================================================
    # == DRAW
    # =====================================================
    def draw(self):
        """création et positionnement des objets (30 fois par seconde)"""

        # vide la fenetre
        pyxel.cls(0)
        
        if self.is_in_main_menu:
            self.main_menu()
            
            
        else:
            
            if not self.end_game > 0:
                self.fight_menu()
                
                for player in self.list_players:
                    player.animation_dash()
                    player.show()
                    #pyxel.rect(player.hitbox_sword[0],player.hitbox_sword[1],4,1,10)
                    
                if self.player_1.is_disarmed:
                    self.animation_parry(self.player_2)
                if self.player_2.is_disarmed:
                    self.animation_parry(self.player_1)
                
                if not self.player_1.is_alive or not self.player_2.is_alive:
                    if not self.player_1.is_alive and not self.player_2.is_alive:
                        pyxel.text(30,25, 'Both players won the round', 7)
                    else:
                        pyxel.text(35,25, f'Player {self.round_winner.team+1} won the round', 7)
                    pyxel.text(35,40, 'Press Space to continue', 7)
                
            else:
                self.death_menu()
                
     
     
### ||| JOUEUR ||| ###

class Player:
    def __init__(self,x,y,sprite_location,orientation,team,list_keys):
        self.x=x
        self.y=y
        self.sprite=sprite_location
        self.orientation=orientation
        self.team=team
        self.keys=list_keys
        
        self.is_attacking=False
        self.cooldown_attack=False
        
        self.is_parrying=False
        self.cooldown_parry=False
        self.timer_parry=0
        self.timer_animation_parry=0
        
        self.is_dashing=False
        self.cooldown_dash=False
        self.dash_speed=0
        self.timer_dash=0
        
        self.smoke_list=[]
        
        self.is_moving=False
        self.is_disarmed=False
        self.timer_disarmed=0
        
        self.timer_animation=0
        self.score=0
        self.timer=0
        self.is_alive=True
        self.timer_death=0
        
        if self.orientation==1:
            self.hitbox_sword=[self.x+16 ,self.y+5]
        else:
            self.hitbox_sword=[self.x-8,self.y+5]
    
        
    def input(self):
        
        #  || DEPLACEMENT ||
        if pyxel.btn(self.keys[1]) and self.x<152:
            self.x += 2 + (self.is_dashing*self.dash_speed)
            self.hitbox_sword[0] += 2 + (self.is_dashing*self.dash_speed)
            self.is_moving=True
        if pyxel.btn(self.keys[0]) and self.x>0:
            self.x += -2 - (self.is_dashing*self.dash_speed)
            self.hitbox_sword[0] += -2 - (self.is_dashing*self.dash_speed)
            self.is_moving=True          
        elif not pyxel.btn(self.keys[0]) and not pyxel.btn(self.keys[1]):
            self.is_moving=False    
            
        
        if not self.is_disarmed:
            # || ATTAQUE ||
            if not self.cooldown_attack and not self.is_parrying and not self.cooldown_parry:  
                if pyxel.btn(self.keys[2]):
                    self.timer=pyxel.frame_count
                    self.is_attacking=True
                    self.cooldown_attack=True
                    pyxel.play(0,7)
                   
            # || DASH ||
            if not self.cooldown_dash:
                if pyxel.btn(self.keys[4]):
                    self.timer_dash=pyxel.frame_count
                    self.is_dashing=True
                    self.dash_speed=5
                    self.cooldown_dash=True
                    pyxel.play(0,5)
        
            #  || PARRY ||
            if not self.cooldown_parry and not self.is_attacking : 
                if pyxel.btn(self.keys[3]):
                    self.timer_parry=pyxel.frame_count
                    self.is_parrying=True
                    self.cooldown_parry=True
                    pyxel.play(0,8)
                        
        
    def cooldowns(self):
        
        t=pyxel.frame_count
        
        if t>self.timer+10:
            self.is_attacking=False
            
        if t>self.timer+20:
            self.cooldown_attack=False
        
        if self.dash_speed>0:
            self.dash_speed-=0.5
            
        if self.dash_speed<=0:
            self.is_dashing=False
            self.dash_speed=0
            
        if t>= self.timer_dash+25:
            self.cooldown_dash=False
        
        if t>self.timer_disarmed+60:
            self.is_disarmed=False
            
        if t>self.timer_parry+20:
            self.is_parrying=False
            
        if t>self.timer_parry+43:
            self.cooldown_parry=False
            
    def animation_dash(self):
        if self.is_dashing: 
            self.smoke_list.append([self.x,self.y,pyxel.frame_count])
            for smoke_cube in self.smoke_list:
                if pyxel.frame_count >= smoke_cube[2]+5:
                    pyxel.rect(smoke_cube[0],smoke_cube[1]+7,6,1,13)
                else:
                    pyxel.rect(smoke_cube[0],smoke_cube[1]+7,6,1,7)
        else:
            if len(self.smoke_list)!=0:
                self.smoke_list.clear()
        
    def show(self):
        if not self.is_alive:
            if pyxel.frame_count % 2 == 0 and self.timer_death<4:
                self.timer_death+=1
            pyxel.blt(self.x, self.y, 0,self.sprite[0]+(8*(self.timer_death-1)),48+8*self.team,8*self.orientation,8,0)
        
        elif self.is_disarmed:
            pyxel.blt(self.x, self.y, 0,self.sprite[0]+(8*self.is_attacking),self.sprite[1],8*self.orientation,8,0)
            pyxel.blt(self.x+8*self.orientation, self.y, 0, 24, 16,8*self.orientation,8,0)
        elif self.is_parrying:
            pyxel.blt(self.x, self.y, 0,self.sprite[0]+8,self.sprite[1],8*self.orientation,8,0)
            pyxel.blt(self.x+8*self.orientation, self.y, 0, 16, 16+8*self.team,8*self.orientation,8,0)
        elif self.is_dashing:
            pyxel.blt(self.x, self.y, 0,self.sprite[0]+24,self.sprite[1],8*self.orientation,8,0)
            pyxel.blt(self.x+8*self.orientation, self.y, 0, 0+(8*self.is_attacking), 16+8*self.team,8*self.orientation,8,0)
        elif self.is_moving:
            if pyxel.frame_count % 2 == 0:
                self.timer_animation+=1
            if self.timer_animation>2:
                self.timer_animation=0
            pyxel.blt(self.x, self.y, 0,0+(8*self.timer_animation),32+(8*self.team),8*self.orientation,8,0)
            pyxel.blt(self.x+8*self.orientation, self.y, 0, 0+(8*self.is_attacking), 16+8*self.team,8*self.orientation,8,0)
            
        else:
            
            pyxel.blt(self.x, self.y, 0,self.sprite[0]+(8*self.is_attacking),self.sprite[1],8*self.orientation,8,0)
            pyxel.blt(self.x+8*self.orientation, self.y, 0, 0+(8*self.is_attacking), 16+8*self.team,8*self.orientation,8,0)
          
Game()
