class Enemy:
    
    def __init__(self,hp:int, weakness:list[str], inmunne:list[str]):
        self.hp = hp
        self.weakness = weakness
        self.inmunne = inmunne

    def attack():
        pass

    def death():
        pass


class Ogre(Enemy):
    def __init__(self,hp,weakness,inmunne):
        super().__init__(hp, weakness, inmunne)

    def attack(self):
        print("lo suyo")

    def death(self):
        print("boom")

    def recibir_daño(self, damage):
        if(damage.type in self.weakness):
            self.hp-= damage.power*2

        if(damage.type in self.inmunne):
            pass 