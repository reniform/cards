from enum import Enum

class StageValue(Enum):
    BASIC  = 2
    STAGE1 = 3
    STAGE2 = 4

class EnergyValue(Enum):
    pass    

class MonCardClass:
    monTitle:      str
    monStage:      StageValue
    monLevel:      int

    monHealth:     int
    monRetreatVal: int
    
    monType:       int
    monWeakType:   int
    monResistType: int

    monDexNum:     int
    monDexHeight:  float
    monDexWeight:  float
    monDexEntry:   str

    def __init__(self):
        pass

test01 = MonCardClass()
test01.monTitle = 'Charmander'
test01.monStage = StageValue.BASIC
test01.monLevel = 10
test01.monHealth = 50
test01.monRetreatVal = 1
test01.monType = 'fire'
test01.monWeakType = 'water'
test01.monResistType = 0
test01.monDexNum = 4
test01.monDexHeight = 0.6
test01.monDexEntry = "It is such and such"