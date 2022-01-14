scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard players set 5 __int__ 5

scoreboard players add $var __variable__ 0
scoreboard players operation $var __variable__ += 5 __int__
