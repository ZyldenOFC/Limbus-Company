import json
import os
import random

SAVE_FILE = "limbus_save.json"
ENTRADA_ENCERRADA = False

PECADORES = [
    "Yi Sang", "Faust", "Don Quixote", "Ryōshū", "Meursault",
    "Hong Lu", "Heathcliff", "Ishmael", "Rodion", "Sinclair",
    "Outis", "Gregor"
]

CANTOS_IDENTIDADES = {
    "Dieci Association South Section 4": 1,
    "W Corp. L2 Cleanup Agent": 2,
    "Cinq Association East Section 3": 3,
    "Liu Association South Section 3": 4,
    "Dead Rabbits Boss": 5,
    "Kurokumo Clan Wakashu": 6,
    "Wild Hunt Heathcliff": 7,
    "Edgar Family Butler": 8,
    "Rosespanner Workshop Fixer": 9,
    "N Corp. Inquisitor": 10,
    "The One Who Grips": 10,
    "G Corp. Manager Corporal": 5
}

CANTOS_PECADORES = {
    "Yi Sang": 1,
    "Faust": 2,
    "Don Quixote": 3,
    "Ryōshū": 4,
    "Meursault": 5,
    "Hong Lu": 6,
    "Heathcliff": 7,
    "Ishmael": 8,
    "Rodion": 9,
    "Sinclair": 10,
    "Outis": 10,
    "Gregor": 5
}


class Skill:
    def __init__(self, nome, tipo, afinidade, poder, moedas, poder_moeda, efeito, valor):
        self.nome = nome
        self.tipo_dano = tipo
        self.afinidade = afinidade
        self.poder_base = poder
        self.moedas = moedas
        self.poder_moeda = poder_moeda
        self.efeito_status = efeito
        self.valor_status = valor

    def to_dict(self):
        return {
            "nome": self.nome,
            "tipo": self.tipo_dano,
            "afinidade": self.afinidade,
            "poder": self.poder_base,
            "moedas": self.moedas,
            "poder_moeda": self.poder_moeda,
            "efeito": self.efeito_status,
            "valor": self.valor_status
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["nome"], dados["tipo"], dados["afinidade"], dados["poder"],
                   dados["moedas"], dados["poder_moeda"], dados["efeito"], dados["valor"])


class Identidade:
    def __init__(self, nome, raridade, hp, atk, defesa, velocidade_min, velocidade_max,
                 resistencias, skills, passiva_nome, passiva_desc, uptie=1, nivel=1,
                 sp=0, tipo_defesa="Guard", contra_ataque=None, pecador=""):
        self.nome = nome
        self.raridade = raridade
        self.hp_base = hp
        self.atk_base = atk
        self.def_base = defesa
        self.velocidade_min = velocidade_min
        self.velocidade_max = velocidade_max
        self.resistencias = resistencias
        self.skills = skills
        self.passiva_nome = passiva_nome
        self.passiva_desc = passiva_desc
        self.uptie = uptie
        self.nivel = nivel
        self.sp = sp
        self.tipo_defesa = tipo_defesa
        self.contra_ataque = contra_ataque
        self.pecador = pecador

    @property
    def hp_max(self):
        return max(1, int(self.hp_base + (self.nivel - 1) * 1.4 + (self.uptie - 1) * 3))

    @property
    def atk(self):
        return self.atk_base + int((self.nivel - 1) * 0.35) + (self.uptie - 1)

    @property
    def defesa(self):
        return self.def_base + int((self.nivel - 1) * 0.25) + (self.uptie - 1)

    def to_dict(self):
        return {
            "nome": self.nome,
            "raridade": self.raridade,
            "hp": self.hp_base,
            "atk": self.atk_base,
            "defesa": self.def_base,
            "velocidade_min": self.velocidade_min,
            "velocidade_max": self.velocidade_max,
            "resistencias": self.resistencias,
            "skills": [skill.to_dict() for skill in self.skills],
            "passiva_nome": self.passiva_nome,
            "passiva_desc": self.passiva_desc,
            "uptie": self.uptie,
            "nivel": self.nivel,
            "sp": self.sp,
            "tipo_defesa": self.tipo_defesa,
            "contra_ataque": self.contra_ataque,
            "pecador": self.pecador
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["nome"], dados["raridade"], dados["hp"], dados["atk"],
                   dados["defesa"], dados["velocidade_min"], dados["velocidade_max"],
                   dados["resistencias"], [Skill.from_dict(skill) for skill in dados["skills"]],
                   dados["passiva_nome"], dados["passiva_desc"],
                   dados.get("uptie", 1), dados.get("nivel", 1), dados.get("sp", 0),
                   dados.get("tipo_defesa", "Guard"), dados.get("contra_ataque"),
                   dados.get("pecador", ""))


def aplicar_defesa_identidade(identidade):
    nome = identidade.nome.lower()
    if any(palavra in nome for palavra in (
        "w corp", "zwei", "cinq", "dawn office", "full-stop", "molar"
    )):
        identidade.tipo_defesa = "Evade"
        identidade.contra_ataque = None
    elif any(palavra in nome for palavra in (
        "g corp", "middle", "wild hunt", "r corp", "wuthering heights",
        "blunt", "rabbi", "kurokumo", "counter"
    )):
        identidade.tipo_defesa = "Counter"
        identidade.contra_ataque = f"Contra-ataque de {identidade.nome}"
    else:
        identidade.tipo_defesa = "Guard"
        identidade.contra_ataque = None
    return identidade


def clonar_identidade(modelo):
    identidade = Identidade.from_dict(modelo.to_dict())
    identidade.pecador = next(
        (pecador for pecador, modelo_pool in POOL_GACHA if modelo_pool.nome == modelo.nome),
        ""
    )
    return aplicar_defesa_identidade(identidade)


MINI_BOSS_CANTOS = {
    1: ["Peccatulum Invidiae", "Peccatulum Superbiae", "Guardia de Kromer"],
    2: ["The Silver Lining", "Peccatulum Gulae", "Scherezade Soldiers"],
    3: ["N Corp. Hammer Inquisitor", "N Corp. Nagel Und Hammer", "Inquisitor of the Cleaver"],
    4: ["Dongrang's Faction Member", "K Corp. Security", "Marina's Enforcers"],
    5: ["Twinhook Pirates", "Middle Big Brother", "Ahab's Whaling Crew"],
    6: ["Erlking Hound", "The Wild Hunt", "T Corp. Watcher"],
    7: ["Sancho's Bloodfiends", "La Manchaland Bloodfiend", "Carmilla"],
    8: ["Jia Huan's Enforcer", "H Corp. Soldier", "Xianren Bodhisattva"],
    9: ["Jia Qiu's Retainers", "H Corp. Disciple", "Zilu"],
    10: ["Timekilling Time", "Pinky Apprentice", "Sinner of the Black Crimson"],
}

BOSS_CANTOS = {
    1: {"nome": "Kromer", "lv": 35, "hp": 1200, "atk": 38, "defesa": 18},
    2: {"nome": "Richard", "lv": 40, "hp": 1500, "atk": 42, "defesa": 22},
    3: {"nome": "N Corp. Sinclair", "lv": 45, "hp": 1800, "atk": 48, "defesa": 25},
    4: {"nome": "Dongbaek", "lv": 50, "hp": 2200, "atk": 52, "defesa": 28},
    5: {"nome": "Ahab", "lv": 55, "hp": 2800, "atk": 58, "defesa": 32},
    6: {"nome": "Erlking Heathcliff", "lv": 60, "hp": 3400, "atk": 64, "defesa": 36},
    7: {"nome": "Sancho", "lv": 65, "hp": 4000, "atk": 70, "defesa": 40},
    8: {"nome": "Jia Mu", "lv": 70, "hp": 4700, "atk": 76, "defesa": 44},
    9: {"nome": "Jia Huan", "lv": 75, "hp": 5400, "atk": 82, "defesa": 48},
    10: {"nome": "Aeng-du", "lv": 80, "hp": 6200, "atk": 88, "defesa": 52}
}

LCB_BASE_STATS = {
    "Yi Sang": (72, 4, 8, {"Slash": 2.0, "Pierce": 0.5, "Blunt": 1.0}),
    "Faust": (84, 2, 4, {"Slash": 2.0, "Pierce": 0.5, "Blunt": 1.0}),
    "Don Quixote": (66, 3, 6, {"Slash": 1.0, "Pierce": 0.5, "Blunt": 2.0}),
    "Ryōshū": (66, 3, 6, {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0}),
    "Meursault": (90, 2, 3, {"Slash": 1.0, "Pierce": 2.0, "Blunt": 0.5}),
    "Hong Lu": (66, 3, 6, {"Slash": 2.0, "Pierce": 1.0, "Blunt": 0.5}),
    "Heathcliff": (78, 2, 5, {"Slash": 2.0, "Pierce": 1.0, "Blunt": 0.5}),
    "Ishmael": (78, 5, 8, {"Slash": 2.0, "Pierce": 1.0, "Blunt": 0.5}),
    "Rodion": (78, 2, 5, {"Slash": 0.5, "Pierce": 2.0, "Blunt": 1.0}),
    "Sinclair": (60, 3, 7, {"Slash": 0.5, "Pierce": 2.0, "Blunt": 1.0}),
    "Outis": (60, 3, 7, {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0}),
    "Gregor": (72, 3, 7, {"Slash": 1.0, "Pierce": 0.5, "Blunt": 2.0})
}

POOL_GACHA = [
    ("Yi Sang", Identidade("Dieci Association South Section 4", "00", 145, 22, 16, 4, 7,
        {"Slash": 1.0, "Pierce": 0.5, "Blunt": 2.0},
        [Skill("Expend Knowledge", "Pierce", "Gloom", 4, 2, 3, "Sinking", 2),
         Skill("Weight of Wisdom", "Blunt", "Sloth", 5, 2, 4, "Sinking", 3),
         Skill("Illuminating Strike", "Pierce", "Gloom", 6, 3, 4, "Sinking", 5)],
        "Insight", "+2 Poder Base se SP >= 15")),
    ("Faust", Identidade("W Corp. L2 Cleanup Agent", "00", 150, 23, 17, 4, 6,
        {"Slash": 1.0, "Pierce": 2.0, "Blunt": 0.5},
        [Skill("Energy Cycle", "Blunt", "Envy", 4, 2, 3, "Charge", 3),
         Skill("Warp Cleaver", "Slash", "Pride", 5, 2, 5, "Charge", 4),
         Skill("Singularity", "Slash", "Gluttony", 7, 3, 6, "Charge", 6)],
        "Waste Extraction", "Ganha Charge ao acertar ataques")),
    ("Don Quixote", Identidade("Cinq Association East Section 3", "000", 165, 26, 18, 5, 8,
        {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0},
        [Skill("Lunge", "Slash", "Pride", 5, 2, 4, "Poise", 3),
         Skill("Dual Lunge", "Pierce", "Pride", 6, 2, 5, "Poise", 4),
         Skill("Dual-Lens Strike", "Slash", "Pride", 7, 3, 6, "Poise", 6)],
        "Poised Blade", "Ganha Poise ao vencer um Clash")),
    ("Ryōshū", Identidade("Liu Association South Section 3", "000", 160, 29, 17, 5, 9,
        {"Slash": 0.5, "Pierce": 1.5, "Blunt": 1.0},
        [Skill("Scorching Gaze", "Slash", "Wrath", 5, 2, 4, "Burn", 3),
         Skill("Flame Fist", "Blunt", "Wrath", 6, 2, 5, "Burn", 4),
         Skill("Blazing Palm", "Pierce", "Wrath", 7, 3, 6, "Burn", 6)],
        "Incinerating Arts", "Ganha Burn ao acertar ataques")),
    ("Meursault", Identidade("Dead Rabbits Boss", "00", 180, 25, 21, 3, 6,
        {"Slash": 1.5, "Pierce": 1.0, "Blunt": 0.5},
        [Skill("Heavy Swing", "Blunt", "Wrath", 5, 2, 4, "Bleed", 2),
         Skill("Crushing Blow", "Blunt", "Sloth", 6, 2, 5, "Bleed", 3),
         Skill("Execution", "Blunt", "Pride", 8, 3, 6, "Bleed", 5)],
        "Ruthless", "Causa dano extra contra alvos sangrando")),
    ("Hong Lu", Identidade("Kurokumo Clan Wakashu", "00", 155, 24, 17, 5, 8,
        {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0},
        [Skill("Slash", "Slash", "Pride", 5, 2, 4, "Poise", 3),
         Skill("Raging Thorn", "Pierce", "Pride", 6, 2, 5, "Poise", 4),
         Skill("Cloud Cutter", "Slash", "Pride", 7, 3, 6, "Poise", 6)],
        "Kurokumo Arts", "Ganha Poise ao atacar")),
    ("Heathcliff", Identidade("Wild Hunt Heathcliff", "000", 170, 27, 20, 5, 9,
        {"Slash": 0.5, "Pierce": 1.0, "Blunt": 1.5},
        [Skill("Bat of a Lash", "Blunt", "Wrath", 5, 2, 4, "Rupture", 3),
         Skill("Batter", "Blunt", "Sloth", 6, 2, 5, "Rupture", 4),
         Skill("Deeper Wound", "Slash", "Pride", 8, 3, 6, "Rupture", 6)],
        "Wild Hunt", "Causa dano extra com Rupture")),
    ("Ishmael", Identidade("Edgar Family Butler", "00", 160, 25, 18, 4, 7,
        {"Slash": 1.0, "Pierce": 0.5, "Blunt": 2.0},
        [Skill("Clean Sweep", "Slash", "Gluttony", 5, 2, 4, "Bleed", 3),
         Skill("Chop", "Slash", "Wrath", 6, 2, 5, "Bleed", 4),
         Skill("Final Cleaning", "Slash", "Pride", 8, 3, 6, "Bleed", 6)],
        "Butler Discipline", "Ganha Bleed ao atacar")),
    ("Rodion", Identidade("Rosespanner Workshop Fixer", "00", 165, 26, 19, 4, 7,
        {"Slash": 1.0, "Pierce": 1.5, "Blunt": 0.5},
        [Skill("Tighten Bolt", "Blunt", "Gluttony", 5, 2, 4, "Tremor", 3),
         Skill("Overload", "Blunt", "Sloth", 6, 2, 5, "Tremor", 4),
         Skill("Full Overhaul", "Blunt", "Pride", 8, 3, 6, "Tremor", 6)],
        "Workshop Support", "Ganha Tremor ao atacar")),
    ("Sinclair", Identidade("N Corp. Inquisitor", "00", 155, 24, 17, 4, 8,
        {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0},
        [Skill("Purging Slash", "Slash", "Wrath", 5, 2, 4, "Rupture", 3),
         Skill("Forced Reformation", "Slash", "Gloom", 6, 2, 5, "Rupture", 4),
         Skill("Final Sermon", "Slash", "Pride", 8, 3, 6, "Rupture", 6)],
        "Inquisitor Zeal", "Causa dano extra com Rupture")),
    ("Outis", Identidade("The One Who Grips", "000", 175, 28, 22, 3, 6,
        {"Slash": 0.5, "Pierce": 1.0, "Blunt": 2.0},
        [Skill("Conviction", "Slash", "Wrath", 6, 2, 4, "Burn", 3),
         Skill("Command", "Slash", "Pride", 7, 2, 5, "Burn", 4),
         Skill("Grand Inquisition", "Slash", "Gloom", 9, 3, 6, "Burn", 6)],
        "Guiding Hand", "Ganha Burn ao atacar")),
    ("Gregor", Identidade("G Corp. Manager Corporal", "00", 168, 26, 20, 4, 7,
        {"Slash": 1.0, "Pierce": 0.5, "Blunt": 1.5},
        [Skill("Bug Sweep", "Slash", "Gluttony", 5, 2, 4, "Sinking", 3),
         Skill("Augmented Strength", "Slash", "Wrath", 6, 2, 5, "Sinking", 4),
         Skill("Morphing Shell", "Slash", "Pride", 8, 3, 6, "Sinking", 6)],
        "Bug Instinct", "Ganha Sinking ao atacar"))
]

VARIANTES_IDS = {
    "Yi Sang": ["LCB Sinner Yi Sang", "Seven Assoc. South Section 6 Yi Sang", "Molar Office Fixer Yi Sang", "Pequod First Mate Yi Sang", "Blade Lineage Salsu Yi Sang", "Effloresced E.G.O::Spicebush Yi Sang", "W Corp. L3 Cleanup Agent Yi Sang", "Ring Pointillist Student Yi Sang", "Solemn Lament Yi Sang", "Liu Assoc. South Section 3 Yi Sang", "N Corp. E.G.O::Fell Bullet Yi Sang", "Heishou Pack Wu Branch Adept Yi Sang", "House of Spiders Nursefather Yi Sang", "LCE E.G.O::Dimension Shredder Yi Sang"],
    "Faust": ["LCB Sinner Faust", "W Corp. L2 Cleanup Agent Faust", "Lobotomy Corp. Remnant Faust", "Zwei Assoc. South Section 4 Faust", "Wuthering Heights Butler Faust", "One Who Grips Faust", "Seven Assoc. South Section 4 Faust", "Lobotomy E.G.O::Regret Faust", "Blade Lineage Salsu Faust", "MultiCrack Office Rep Faust", "LCE E.G.O::Ardor Blossom Star Faust", "Heishou Pack Mao Branch Adept Faust", "Shi Assoc. East Section 3 Faust", "Dawn Office Fixer Faust"],
    "Don Quixote": ["LCB Sinner Don Quixote", "Shi Assoc. South Section 5 Director Don Quixote", "N Corp. Mittelhammer Don Quixote", "Lobotomy E.G.O::Lantern Don Quixote", "Blade Lineage Salsu Don Quixote", "Cinq Assoc. South Section 5 Director Don Quixote", "Middle Little Sister Don Quixote", "T Corp. Class 3 Collection Staff Don Quixote", "Manager of La Manchaland Don Quixote", "Cinq Assoc. East Section 3 Don Quixote", "Heishou Pack Wei Branch Don Quixote", "Wedge Office Fixer Don Quixote"],
    "Ryōshū": ["LCB Sinner Ryōshū", "Seven Assoc. South Section 6 Ryōshū", "LCCB Assistant Manager Ryōshū", "Liu Assoc. South Section 4 Ryōshū", "District 20 Yurodivy Ryōshū", "Kurokumo Clan Wakashu Ryōshū", "R.B. Chef de Cuisine Ryōshū", "W Corp. L3 Cleanup Agent Ryōshū", "Edgar Family Chief Butler Ryōshū", "Lobotomy E.G.O::Red Eyes & Penitence Ryōshū", "Drifting Blade of Hongyuan Ryōshū", "House of Spiders Blade Ryōshū"],
    "Meursault": ["LCB Sinner Meursault", "Liu Assoc. South Section 6 Meursault", "Rosespanner Workshop Fixer Meursault", "Middle Little Brother Meursault", "Dead Rabbits Boss Meursault", "W Corp. L2 Cleanup Agent Meursault", "N Corp. Großhammer Meursault", "R Corp. 4th Pack Rhino Meursault", "Dieci Assoc. South Section 4 Director Meursault", "Thumb East Capo IIII Meursault", "Prince of La Manchaland Meursault", "Ring Fauvist Student Meursault"],
    "Hong Lu": ["LCB Sinner Hong Lu", "Kurokumo Clan Wakashu Hong Lu", "Liu Assoc. South Section 5 Hong Lu", "W Corp. L2 Cleanup Agent Hong Lu", "Hook Office Fixer Hong Lu", "Fanghunt Office Fixer Hong Lu", "Tingtang Gang Gangleader Hong Lu", "K Corp. Class 3 Excision Staff Hong Lu", "Dieci Assoc. South Section 4 Hong Lu", "District 20 Yurodivy Hong Lu", "Lord of Hongyuan Hong Lu", "Cinq Assoc. East Section 3 Hong Lu"],
    "Heathcliff": ["LCB Sinner Heathcliff", "Shi Assoc. South Section 5 Heathcliff", "N Corp. Kleinhammer Heathcliff", "Seven Assoc. South Section 4 Heathcliff", "R Corp. 4th Pack Rabbit Heathcliff", "Lobotomy E.G.O::Sunshower Heathcliff", "Pequod Harpooneer Heathcliff", "Öufi Assoc. South Section 3 Heathcliff", "Wild Hunt Heathcliff", "Kurokumo Clan Wakashu Heathcliff", "W Corp. L4 Cleanup Agent CCA Heathcliff", "Heishou Pack You Branch Adept Heathcliff", "House of Spiders Thumb Apprentice Heathcliff"],
    "Ishmael": ["LCB Sinner Ishmael", "Shi Assoc. South Section 5 Ishmael", "LCCB Assistant Manager Ishmael", "Lobotomy E.G.O::Sloshing Ishmael", "Edgar Family Butler Ishmael", "R Corp. 4th Pack Reindeer Ishmael", "Liu Assoc. South Section 4 Ishmael", "Molar Boatworks Fixer Ishmael", "Pequod Captain Ishmael", "Zwei Assoc. West Section 3 Ishmael", "Family Hierarch Candidate Ishmael", "House of Spiders Middle Apprentice Ishmael", "LCD OSIR Team Ishmael"],
    "Rodion": ["LCB Sinner Rodion", "LCCB Assistant Manager Rodion", "N Corp. Mittelhammer Rodion", "Zwei Assoc. South Section 5 Rodion", "T Corp. Class 2 Collection Staff Rodion", "Kurokumo Clan Wakashu Rodion", "Rosespanner Workshop Rep Rodion", "Dieci Assoc. South Section 4 Rodion", "Devyat Assoc. North Section 3 Rodion", "Princess of La Manchaland Rodion", "Heishou Pack Si Branch Rodion", "R Corp. 4th Pack Reindeer Rodion"],
    "Sinclair": ["LCB Sinner Sinclair", "Zwei Assoc. South Section 6 Sinclair", "Los Mariachis Jefe Sinclair", "Lobotomy E.G.O::Red Sheet Sinclair", "Molar Boatworks Fixer Sinclair", "Zwei Assoc. West Section 3 Sinclair", "Blade Lineage Salsu Sinclair", "One Who Shall Grip Sinclair", "Cinq Assoc. South Section 4 Director Sinclair", "Dawn Office Fixer Sinclair", "Devyat Assoc. North Section 3 Sinclair", "Middle Little Brother Sinclair", "Thumb East Soldato II Sinclair"],
    "Outis": ["LCB Sinner Outis", "Blade Lineage Salsu Outis", "G Corp. Head Manager Outis", "Cinq Assoc. South Section 4 Outis", "Ring Pointillist Student Outis", "Seven Assoc. South Section 6 Director Outis", "Molar Office Fixer Outis", "Lobotomy E.G.O::Magic Bullet Outis", "Wuthering Heights Chief Butler Outis", "Barber of La Manchaland Outis", "T Corp. Class 3 VDCU Staff Outis", "House of Spiders Middle Nursefather Outis", "Wedge Office Rep Outis"],
    "Gregor": ["LCB Sinner Gregor", "Liu Assoc. South Section 6 Gregor", "R.B. Sous-chef Gregor", "Rosespanner Workshop Fixer Gregor", "Kurokumo Clan Captain Gregor", "G Corp. Manager Corporal Gregor", "Zwei Assoc. South Section 4 Gregor", "Twinhook Pirates First Mate Gregor", "Edgar Family Heir Gregor", "Priest of La Manchaland Gregor", "Firefist Office Survivor Gregor", "Night Awls Capitano Gregor", "LCE E.G.O::AEDD Gregor"]
}


class Jogador:
    def __init__(self):
        self.nome = PECADORES[0]
        self.identidades = []
        self.identidade_ativa = None
        self.equipe = []
        self.lunacy = 1300
        self.debug_lunacy = False
        self.vitorias = 0

    def escolher_inicial(self, modelo):
        identidade = clonar_identidade(modelo)
        identidade.nivel = 65
        identidade.uptie = 4
        self.identidades.append(identidade)
        self.identidade_ativa = identidade
        self.equipe = [identidade]

    def selecionar_equipe(self):
        if not self.identidades:
            print("Nenhuma identidade disponível.")
            print("Faça um Summon antes de montar sua equipe.")
            entrada_segura("Pressione Enter para continuar...")
            return

        print("\nEscolha um Sinner:")
        for numero, pecador in enumerate(PECADORES, 1):
            quantidade = sum(
                1 for identidade in self.identidades
                if identidade.pecador == pecador
            )
            print(f"{numero}. {pecador} ({quantidade} IDs)")
        print("0. Voltar")

        escolha_pecador = ler_numero("Sinner", 0, 12)
        if escolha_pecador in (-1, 0):
            print("Seleção cancelada.")
            return

        pecador = PECADORES[escolha_pecador - 1]
        ids_do_pecador = [
            identidade for identidade in self.identidades
            if identidade.pecador == pecador
        ]
        if not ids_do_pecador:
            print(f"Você ainda não possui nenhum ID de {pecador}.")
            entrada_segura("Pressione Enter para voltar...")
            return

        print(f"\nIDs de {pecador}:")
        for indice, identidade in enumerate(ids_do_pecador, 1):
            print(f"{indice}. {identidade.nome} | Lv.{identidade.nivel} | HP {identidade.hp_max} | Uptie {identidade.uptie} | {identidade.tipo_defesa}")
        print("0. Voltar")

        escolha_id = ler_numero("ID", 0, len(ids_do_pecador))
        if escolha_id in (-1, 0):
            print("Seleção cancelada.")
            return

        if escolha_id < 1 or escolha_id > len(ids_do_pecador):
            print("Seleção de ID inválida.")
            return
        identidade_escolhida = ids_do_pecador[escolha_id - 1]
        if identidade_escolhida in self.equipe:
            print("Este ID já está na equipe.")
            entrada_segura("Pressione Enter para continuar...")
            return
        if len(self.equipe) >= 6:
            print("A equipe já possui 6 membros.")
            entrada_segura("Pressione Enter para continuar...")
            return
        if any(identidade.pecador == pecador for identidade in self.equipe):
            print(f"{pecador} já possui outro ID na equipe.")
            entrada_segura("Pressione Enter para continuar...")
            return

        self.equipe.append(identidade_escolhida)
        self.identidade_ativa = self.equipe[0]
        print(f"\n{identidade_escolhida.nome} foi adicionada à equipe.")
        print("Equipe atual:")
        for identidade in self.equipe:
            print(f"- {identidade.pecador}: {identidade.nome}")
        return

    def trocar_identidade(self):
        if len(self.identidades) == 1:
            self.identidade_ativa = self.identidades[0]
            self.equipe = [self.identidades[0]]
            print("Esta é sua única identidade.")
            return
        print("\nIdentidades disponíveis:")
        for indice, identidade in enumerate(self.identidades, 1):
            print(f"{indice}. {identidade.raridade} - {identidade.nome}")
        escolha = ler_numero("Escolha", 1, len(self.identidades))
        self.identidade_ativa = self.identidades[escolha - 1]

    def salvar(self):
        dados = {
            "estado_inicial": "limbo_v1",
            "debug_lunacy": getattr(self, "debug_lunacy", False),
            "nome": self.nome,
            "lunacy": self.lunacy,
            "vitorias": self.vitorias,
            "identidades": [identidade.to_dict() for identidade in self.identidades],
            "equipe": [identidade.nome for identidade in self.equipe[:6]],
            "identidade_ativa": self.identidade_ativa.nome if self.identidade_ativa else None
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    @classmethod
    def carregar(cls):
        jogador = cls()
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if dados.get("estado_inicial", "vazio") != "limbo_v1":
                return jogador
            jogador.nome = dados.get("nome", PECADORES[0])
            jogador.debug_lunacy = dados.get("debug_lunacy", False)
            jogador.lunacy = dados.get("lunacy", 1300)
            if jogador.lunacy > 1300 and not dados.get("debug_lunacy", False):
                jogador.lunacy = 1300
            jogador.vitorias = dados.get("vitorias", 0)
            jogador.identidades = [Identidade.from_dict(dado) for dado in dados.get("identidades", [])]
            nomes_base = {f"LCB Sinner {pecador}" for pecador in PECADORES}
            nomes_presentes = {identidade.nome for identidade in jogador.identidades}
            if not nomes_base.issubset(nomes_presentes):
                temporario = Jogador()
                criar_lcb_base(temporario)
                ids_extra = {
                    identidade.nome: identidade
                    for identidade in jogador.identidades
                    if identidade.nome not in nomes_base
                }
                jogador.identidades = temporario.identidades + list(ids_extra.values())

            for identidade in jogador.identidades:
                identidade.nivel = max(65, identidade.nivel)
                identidade.uptie = max(4, identidade.uptie)

            nomes_equipe = dados.get("equipe", [])
            jogador.equipe = [
                identidade for identidade in jogador.identidades
                if identidade.nome in nomes_equipe
            ][:6]
            nome_ativa = dados.get("identidade_ativa")
            jogador.identidade_ativa = next(
                (item for item in jogador.identidades if item.nome == nome_ativa),
                jogador.identidades[0] if jogador.identidades else None
            )
            if not jogador.equipe:
                jogador.equipe = []
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return jogador


def limpar_tela():
    print("\n" + "=" * 48)


def entrada_segura(pergunta):
    global ENTRADA_ENCERRADA
    try:
        return input(pergunta).strip()
    except (EOFError, KeyboardInterrupt):
        ENTRADA_ENCERRADA = True
        print("\nEntrada encerrada. Voltando ao menu anterior.")
        return ""


def ler_numero(pergunta, minimo, maximo):
    if ENTRADA_ENCERRADA:
        return -1
    print(f"Comando esperado: número de {minimo} a {maximo}", flush=True)
    while True:
        resposta = entrada_segura(f"{pergunta} ({minimo}-{maximo}): ")
        if ENTRADA_ENCERRADA:
            return -1
        if resposta.isdigit():
            valor = int(resposta)
            if minimo <= valor <= maximo:
                return valor
        print("Entrada inválida.")


def criar_lcb_base(jogador):
    for pecador in PECADORES:
        hp, velocidade_min, velocidade_max, resistencias = LCB_BASE_STATS[pecador]
        identidade = Identidade(
            f"LCB Sinner {pecador}", "00", hp, 18, 14,
            velocidade_min, velocidade_max, resistencias,
            [
                Skill(f"Golpe Básico 1 - {pecador}", "Slash", "Wrath", 4, 1, 3, "", 0),
                Skill(f"Golpe Básico 2 - {pecador}", "Blunt", "Gloom", 5, 1, 4, "", 0)
            ],
            "Passiva LCB",
            "Identidade base inicial do Pecador",
            uptie=1, nivel=40, pecador=pecador
        )
        aplicar_defesa_identidade(identidade)
        jogador.identidades.append(identidade)
    jogador.equipe = []
    jogador.identidade_ativa = None


def criar_novo_jogo():
    print("\n" + "=" * 48)
    print("NOVO JOGO")
    print("Lunacy inicial: 1300")
    print("12 LCB Sinners base estão disponíveis.")
    print("Use Summon no menu Jogar para obter outros IDs.")

    jogador = Jogador()
    criar_lcb_base(jogador)
    jogador.salvar()
    entrada_segura("Pressione Enter para continuar...")
    return jogador


def extracao(jogador, quantidade):
    custo = quantidade * 130
    if jogador.lunacy < custo:
        print("\nLunacy insuficiente.")
        return
    jogador.lunacy -= custo
    print("\nResultados da extração:")
    for _ in range(quantidade):
        _, modelo = random.choice(POOL_GACHA)
        identidade = clonar_identidade(modelo)
        jogador.identidades.append(identidade)
        identidade.nivel = 65
        identidade.uptie = 4
        print(f"- [{identidade.raridade}] {identidade.nome} | Lv.{identidade.nivel} | Uptie {identidade.uptie}")
    jogador.salvar()


def selecionar_boss(jogador):
    limpar_tela()
    print("ESCOLHA UM ALVO")
    print("1. Mini-boss")
    print("2. Boss final do Canto")
    print("0. Voltar")
    escolha = ler_numero("Tipo de encontro", 0, 2)
    if escolha == 0:
        return

    limpar_tela()
    print("ESCOLHA UM CANTO")
    for canto in range(1, 11):
        print(f"{canto}. Canto {canto}")
    canto = ler_numero("Canto", 0, 10)
    if canto == 0:
        return

    if escolha == 1:
        limpar_tela()
        mini_bosses = MINI_BOSS_CANTOS[canto]
        print(f"MINI-BOSSES - CANTO {canto}")
        for indice, nome in enumerate(mini_bosses, 1):
            print(f"{indice}. {nome}")
        print("0. Voltar")
        indice = ler_numero("Mini-boss", 0, len(mini_bosses))
        if indice == 0:
            return
        nome = mini_bosses[indice - 1]
        fator = 0.45 + canto * 0.05
        boss = {
            "nome": nome,
            "lv": 20 + canto * 3,
            "hp": int(900 * fator),
            "atk": 20 + canto * 3,
            "defesa": 10 + canto
        }
        combate(jogador, canto, boss)
        return

    limpar_tela()
    boss = BOSS_CANTOS[canto]
    print(f"BOSS FINAL - CANTO {canto}")
    print(f"{boss['nome']} (Lv.{boss['lv']} | HP {boss['hp']})")
    print("1. Confirmar luta")
    print("0. Voltar")
    resposta = ler_numero("Boss final", 0, 1)
    if resposta == 0:
        return
    combate(jogador, canto)


def combate(jogador, canto=None, boss_override=None):
    if not jogador.equipe:
        print("Você precisa formar uma equipe.")
        return

    if canto is None:
        selecionar_boss(jogador)
        return

    boss = boss_override if boss_override is not None else BOSS_CANTOS[canto]
    hp_equipe = [identidade.hp_max for identidade in jogador.equipe]
    sp_equipe = [identidade.sp for identidade in jogador.equipe]
    hp_boss = boss["hp"]
    escudos = [0 for _ in jogador.equipe]
    evasivas = [False for _ in jogador.equipe]
    contra_ataques = [False for _ in jogador.equipe]
    turno = 1

    print("\n" + "=" * 48)
    print(f"ALVO - CANTO {canto}: {boss['nome']}")
    print(f"Lv.{boss['lv']} | HP {boss['hp']} | ATK {boss['atk']} | DEF {boss['defesa']}")

    while hp_boss > 0 and any(hp > 0 for hp in hp_equipe):
        limpar_tela()
        print(f"CANTO {canto} - TURNO {turno}")
        print(f"Boss: {boss['nome']} | HP {hp_boss}/{boss['hp']}")
        print("Equipe:")
        for indice, identidade in enumerate(jogador.equipe, 1):
            hp = hp_equipe[indice - 1]
            estado = "VIVA" if hp > 0 else "DERROTADA"
            defesa = identidade.tipo_defesa
            escudo = f" | Escudo {escudos[indice - 1]}" if escudos[indice - 1] > 0 else ""
            print(f"{indice}. {identidade.nome} | Lv.{identidade.nivel} | HP {max(0, hp)}/{identidade.hp_max} | SP {sp_equipe[indice - 1]} | {defesa}{escudo} | {estado}")

        acoes = []
        cancelar = False
        indice_linha = 0

        while indice_linha < len(jogador.equipe):
            identidade = jogador.equipe[indice_linha]
            if hp_equipe[indice_linha] <= 0:
                indice_linha += 1
                continue

            limpar_tela()
            print(f"PLANEJAMENTO DO TURNO {turno}")
            print(f"Boss: {boss['nome']} | HP {hp_boss}/{boss['hp']}")
            print(f"Linha {indice_linha + 1}/{len(jogador.equipe)}")
            print(f"Defesa própria: {identidade.tipo_defesa}")
            print(f"{identidade.nome} - HP {hp_equipe[indice_linha]}/{identidade.hp_max} - SP {sp_equipe[indice_linha]}")

            skills = identidade.skills[:2] if len(identidade.skills) >= 2 else identidade.skills
            for numero, skill in enumerate(skills, 1):
                print(f"{numero}. {skill.nome} | {skill.tipo_dano} | Poder {skill.poder_base}+")
            print(f"3. {identidade.tipo_defesa}")
            print("0. Voltar à linha anterior")
            print("9. Cancelar turno inteiro")

            resposta = entrada_segura("Escolha a ação (0/1/2/3/9): ")
            if ENTRADA_ENCERRADA:
                cancelar = True
                break
            if resposta == "9":
                cancelar = True
                break
            if resposta == "0":
                if indice_linha == 0:
                    cancelar = True
                    break
                if acoes:
                    acoes.pop()
                indice_linha -= 1
                continue

            if resposta not in ("1", "2", "3"):
                print("Entrada inválida.")
                entrada_segura("Pressione Enter para continuar...")
                continue

            if resposta == "3":
                acao = {"indice": indice_linha, "tipo": "defender", "skill": None}
            else:
                skill = skills[int(resposta) - 1]
                acao = {"indice": indice_linha, "tipo": "skill", "skill": skill}

            acoes.append(acao)
            indice_linha += 1

        if cancelar:
            print("\nPlanejamento cancelado. Nenhuma ação foi executada.")
            if ENTRADA_ENCERRADA:
                return
            entrada_segura("Pressione Enter para continuar...")
            continue

        for acao in acoes:
            indice = acao["indice"]
            identidade = jogador.equipe[indice]
            if hp_equipe[indice] <= 0 or hp_boss <= 0:
                continue

            if acao["tipo"] == "defender":
                if identidade.tipo_defesa == "Guard":
                    escudos[indice] = identidade.defesa + 20
                    sp_equipe[indice] = max(-45, min(45, sp_equipe[indice] + 3))
                    print(f"\n{identidade.nome} usa Guard e recebe {escudos[indice]} de Escudo.")
                elif identidade.tipo_defesa == "Evade":
                    evasivas[indice] = True
                    sp_equipe[indice] = max(-45, min(45, sp_equipe[indice] + 5))
                    print(f"\n{identidade.nome} usa Evade e prepara um desvio.")
                else:
                    contra_ataques[indice] = True
                    sp_equipe[indice] = max(-45, min(45, sp_equipe[indice] + 4))
                    print(f"\n{identidade.nome} usa Counter: {identidade.contra_ataque}.")
            else:
                skill = acao["skill"]
                poder = skill.poder_base + sum(random.randint(1, skill.poder_moeda) for _ in range(skill.moedas))
                dano = max(1, poder + identidade.atk - boss["defesa"])
                hp_boss -= dano
                sp_equipe[indice] = max(-45, min(45, sp_equipe[indice] + random.randint(-3, 5)))
                print(f"\n{identidade.nome} usa {skill.nome} e causa {dano} de dano.")

        if hp_boss <= 0:
            break

        vivos = [indice for indice, hp in enumerate(hp_equipe) if hp > 0]
        if not vivos:
            break

        vivo_indice = random.choice(vivos)
        vivo = jogador.equipe[vivo_indice]
        dano = max(1, boss["atk"] - vivo.defesa + random.randint(-5, 8))
        dano_real = dano

        if evasivas[vivo_indice]:
            evasivas[vivo_indice] = False
            if random.random() < 0.70:
                dano_real = 0
                print(f"\n{vivo.nome} desvia do ataque de {boss['nome']}.")

        if dano_real > 0 and escudos[vivo_indice] > 0:
            absorvido = min(escudos[vivo_indice], dano_real)
            escudos[vivo_indice] -= absorvido
            dano_real -= absorvido

        hp_equipe[vivo_indice] -= dano_real
        if dano_real > 0:
            print(f"\n{boss['nome']} ataca {vivo.nome} e causa {dano_real} de dano.")

        if contra_ataques[vivo_indice]:
            contra_ataques[vivo_indice] = False
            dano_counter = max(1, int(vivo.atk * 0.75))
            hp_boss -= dano_counter
            print(f"{vivo.nome} executa Counter e causa {dano_counter} de dano de volta.")

        turno += 1
        entrada_segura("Pressione Enter para continuar...")

    if hp_boss <= 0:
        recompensa = random.randint(100, 180) * canto
        jogador.lunacy += recompensa
        jogador.vitorias += 1
        print(f"\nVITÓRIA NO CANTO {canto}!")
        print(f"Chefe derrotado: {boss['nome']}")
        print(f"Recompensa: {recompensa} Lunacy")
    else:
        print("\nDERROTA! Toda a equipe foi derrotada.")

    jogador.salvar()


def mostrar_status(jogador):
    limpar_tela()
    print(f"Pecador: {jogador.nome}")
    print(f"Lunacy: {jogador.lunacy}")
    print(f"Vitórias: {jogador.vitorias}")
    print(f"Identidades obtidas: {len(jogador.identidades)}")
    print("\nEquipe atual:")
    if jogador.equipe:
        for identidade in jogador.equipe:
            canto = CANTOS_IDENTIDADES.get(identidade.nome, CANTOS_PECADORES.get(jogador.nome, 1))
            print(f"- {identidade.raridade} {identidade.nome} | Canto {canto} | Lv.{identidade.nivel} | HP {identidade.hp_max} | ATK {identidade.atk} | DEF {identidade.defesa}")
    else:
        print("Nenhuma equipe selecionada.")


def unlock_todos_ids(jogador):
    jogador.identidades = []
    nomes_existentes = set()

    for _, modelo in POOL_GACHA:
        identidade = clonar_identidade(modelo)
        identidade.nivel = 65
        identidade.uptie = 4
        jogador.identidades.append(identidade)
        nomes_existentes.add(identidade.nome)

    for pecador, nomes in VARIANTES_IDS.items():
        for indice, nome in enumerate(nomes):
            if nome in nomes_existentes:
                continue
            raridade = "000" if indice % 3 == 2 else "00"
            hp = 72 + (indice % 5) * 4
            atk = 24 + (indice % 4) * 2
            defesa = 16 + (indice % 4)
            resistencias = {"Slash": 1.0, "Pierce": 1.0, "Blunt": 1.0}
            skills = [
                Skill(f"{pecador} - Golpe 1", "Slash", "Wrath", 5, 2, 4, "Poise", 3),
                Skill(f"{pecador} - Golpe 2", "Pierce", "Pride", 6, 2, 5, "Rupture", 4)
            ]
            identidade = Identidade(nome, raridade, hp, atk, defesa, 3, 8,
                                   resistencias, skills, "Passiva do ID",
                                   "Passiva resumida; dados exatos disponíveis na wiki",
                                   uptie=4, nivel=65, pecador=pecador)
            aplicar_defesa_identidade(identidade)
            jogador.identidades.append(identidade)
            nomes_existentes.add(nome)
    jogador.equipe = jogador.identidades[:6]
    jogador.identidade_ativa = jogador.identidades[0]
    jogador.salvar()
    print("\nTodos os IDs disponíveis foram desbloqueados.")


def debug_mode(jogador):
    while True:
        if ENTRADA_ENCERRADA:
            return
        limpar_tela()
        print("DEBUG MODE")
        print(f"Lunacy atual: {jogador.lunacy}")
        print(f"IDs disponíveis: {len(jogador.identidades)}")
        print("1. Dar Lunacy")
        print("2. Desbloquear todos os IDs")
        print("3. Escolher boss e lutar")
        print("4. Selecionar equipe")
        print("5. Ver status")
        print("0. Voltar")

        escolha = ler_numero("Debug", 0, 5)
        if escolha == 1:
            quantidade = ler_numero("Quantidade de Lunacy", 1, 999999999)
            jogador.lunacy = quantidade
            jogador.debug_lunacy = True
            jogador.salvar()
            print(f"Lunacy definida para {jogador.lunacy}.")
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 2:
            unlock_todos_ids(jogador)
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 3:
            selecionar_boss(jogador)
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 4:
            jogador.selecionar_equipe()
            jogador.salvar()
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 5:
            mostrar_status(jogador)
            entrada_segura("Pressione Enter para continuar...")
        else:
            break


def menu_jogar(jogador):
    while True:
        if ENTRADA_ENCERRADA:
            return
        limpar_tela()
        print("JOGAR")
        print(f"Lunacy: {jogador.lunacy}")
        print(f"Equipe: {len(jogador.equipe)}/6")
        print("1. Escolher boss e lutar")
        print("2. Summon 1 (130 Lunacy)")
        print("3. Summon 10 (1300 Lunacy)")
        print("4. Selecionar equipe")
        print("5. Ver status")
        print("0. Voltar")

        escolha = ler_numero("Jogar", 0, 5)
        if escolha == 1:
            selecionar_boss(jogador)
            entrada_segura("Pressione Enter para voltar...")
        elif escolha == 2:
            extracao(jogador, 1)
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 3:
            extracao(jogador, 10)
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 4:
            jogador.selecionar_equipe()
            jogador.salvar()
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 5:
            mostrar_status(jogador)
            entrada_segura("Pressione Enter para continuar...")
        else:
            return


def menu_principal():
    print("=" * 48)
    print("LIMBUS COMPANY - TERMINAL VS CODE")
    print("Execute Python; use os números e pressione Enter.")
    print("=" * 48, flush=True)

    save_existia = os.path.isfile(SAVE_FILE)
    jogador = Jogador.carregar()
    if not save_existia:
        jogador = criar_novo_jogo()

    while True:
        if ENTRADA_ENCERRADA:
            jogador.salvar()
            break
        limpar_tela()
        print("LIMBUS COMPANY - MENU PRINCIPAL")
        print(f"Lunacy: {jogador.lunacy}")
        print(f"Equipe: {len(jogador.equipe)}/6")
        print("1. Jogar")
        print("2. Debug Mode")
        print("3. Ver status")
        print("4. Salvar")
        print("0. Sair")

        escolha = ler_numero("Menu", 0, 4)
        if escolha == -1:
            jogador.salvar()
            break
        if escolha == 1:
            menu_jogar(jogador)
        elif escolha == 2:
            debug_mode(jogador)
        elif escolha == 3:
            mostrar_status(jogador)
            entrada_segura("Pressione Enter para continuar...")
        elif escolha == 4:
            jogador.salvar()
            print("\nProgresso salvo.")
            entrada_segura("Pressione Enter para continuar...")
        else:
            jogador.salvar()
            print("Até a próxima, gerente.")
            break


if __name__ == "__main__":
    menu_principal()
