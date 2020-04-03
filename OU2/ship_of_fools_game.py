from die_cup import DieCup


class ShipOfFoolsGame:
    def __init__(self, winning_score=21):
        self._cup = DieCup(5)
        self._winning_score = winning_score

    @property
    def winning_score(self):
        return self._winning_score

    def round(self):
        self._cup.release_all()

        has_ship = False
        has_captain = False
        has_mate = False
        
        crew = 0

        for round in range(3):
            self._cup.roll()

            if not has_ship:
                if (die_index := self._cup.find_value_unbanked(6)) >= 0:
                    self._cup.bank(die_index)
                    has_ship = True
            if has_ship and not has_captain:
                if (die_index := self._cup.find_value_unbanked(5)) >= 0:
                    self._cup.bank(die_index)
                    has_captain = True
            if has_captain and not has_mate:
                if (die_index := self._cup.find_value_unbanked(4)) >= 0:
                    self._cup.bank(die_index)
                    has_mate = True
            
            if has_ship and has_captain and has_mate:
                for die in range(2): # There are a maximum of 2 dice that are unbanked at this point
                    if (die_index := self._cup.find_value_unbanked(4)) >= 0:
                        self._cup.bank(die_index)
                    elif (die_index := self._cup.find_value_unbanked(5)) >= 0:
                        self._cup.bank(die_index)
                    elif (die_index := self._cup.find_value_unbanked(6)) >= 0:
                        self._cup.bank(die_index)
                    else:
                        break
        
        if has_ship and has_captain and has_mate:
            crew = self._cup.get_total_value() - 15
        
        return crew