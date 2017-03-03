class EffectPriority:
    # before__turn_starts
    TURN_TYPE_KNOWLEDGE_PRIORITY = 2
    RECEIVE_MANA_PRIORITY = 1

    # before__receive_damage
    ELEMENTAL_PROTECTION_PRIORITY = 2 # also before__turn_end, but doesn't matter
    MANA_SHIELD_PRIORITY = 1

    # before__turn_end
    CHAIN_LIGHTNING_PRIORITY = 1

    #
