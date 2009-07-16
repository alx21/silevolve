# Dictionary of stances
_STANCES = dict({ 0: ( 0,  0,  0),
                  1: (-1,  1,  1),
                  2: ( 1, -1, -1), })
                  
# opts
_DICE_DROPPED = "DICE_DROPPED"

# penalties
_ATT_PENALTY = "ATT_PENALTY"
_DEF_PENALTY = "DEF_PENALTY"

# internally-used opts
# I don't think this is used right now ...
_SPECIAL_DICE = "SPECIAL_DICE" # dice dropped for special attacks like knockout

# type
_ATT_TYPE = "ATT_TYPE"
_DEFAULT = 0
_HTH_KO = 1
_HTH_KD = 2
_RA_ROF = 1
_RA_HS = 2
_RA_B = 3

_ROF = "ROF"


# DIE PENALTIES
_RANGED_HEADSHOT_PENALTY = -3
_CC_KNOCKOUT_PENALTY = -2
_CC_KNOCKDOWN_PENALTY = -1
