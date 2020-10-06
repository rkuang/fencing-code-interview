from __future__ import division
import sys
import re
import math

class Fencer:
    def __init__(self, _first, _last, _club, _rank, _year):
        self.first = _first
        self.last = _last
        self.club = _club
        self.rank = _rank
        self.year = _year

    @staticmethod
    def parse(line):
        my_line = re.split(r'\s*,\s*', line)

        first = my_line[1]
        last = my_line[0]
        club = my_line[2]
        rank = my_line[3][:1]

        if (rank == 'U'):
            year = -1
        else:
            year = int(my_line[3][1:])

        return Fencer(first, last, club, rank, year)

    def printFencer(self):
        year = self.year
        if (year == -1):
            year = ''
        print "{:21}{:24}{:24}{:8}{:2}".format(self.first, self.last, self.club, self.rank, year)

class Tourney:
    def __init__(self, _competitors, _clubs):
        self.competitors = _competitors
        self.clubs = _clubs

    def printInfo(self):
        print "Competitor List"
        for fencer in self.competitors:
            fencer.printFencer()
        print self.clubs

class Pool:
    def __init__(self):
        self.competitors = []
        self.clubs = {}
        

''' parseFile(f)
Takes a file object as input and reads its contents.
Uses regular expressions to split each line by commas.
Information is stored in a Tourney object, which holds fencer
info and club counts.
'''
def parseFile(f):
    competitors = []
    clubs = {}

    for line in f.readlines():
        fencer = Fencer.parse(line)
        competitors.append(fencer)
        clubs[fencer.club] = clubs.get(fencer.club, 0) + 1
    
    competitors.sort(key = lambda fencer: (fencer.rank, -fencer.year))
    return Tourney(competitors, clubs)

''' createPools
Create x number of pools based on number of competitors.
Prioritize making groups of 6 or 7, 7 or 8, and finally 5 or 6.
'''
def createPools(competitors):
    pool_size = 0
    if (len(competitors) % 6 <= 2):  # pool size 6 or 7
        pool_size = len(competitors)//6
    elif (len(competitors) % 7 <= 2): # pool size 7 or 8
        pool_size = len(competitors)//7
    else:                            # pool size 5 or 6
        pool_size = len(competitors)//5

    return [Pool() for _ in range(pool_size)]

''' populatePools(tourney)
Takes a tourney object as an argument.
Copies the list of competitors so that elements can be popped
as they are added to pools while preserving the original data.
'''
def populatePools(tourney):
    competitors = list(tourney.competitors)
    
    pools = createPools(competitors)
    club_capacities = calculateClubDistribution(tourney.clubs, len(pools))

    pool_number = 0
    reverse = False
    while (len(competitors) > 0):
        my_pool = pools[pool_number]
        
        # find a fencer that doesn't cause a club imbalance
        index = 0
        fencer = competitors[index]
        while (fencer.club != '' and 
                index+1 < len(competitors) and
                my_pool.clubs.get(fencer.club, 0) >= club_capacities[fencer.club][0]):
            index += 1
            fencer = competitors[index]
        fencer = competitors.pop(index)
        
        # if cannot find, find another fencer to swap with
        if (fencer.club != '' and my_pool.clubs.get(fencer.club, 0) >= club_capacities[fencer.club][0]):
            potentials = []
            backups = []
            # find a pool that can accomodate
            for p in pools:
                local_potentials = []
                count = p.clubs.get(fencer.club)
                if (count == None or
                        count < club_capacities[fencer.club][0]):
                    # find fencers that are equal or lower rank
                    for newfencer in p.competitors:
                        if (newfencer.rank >= fencer.rank):
                            local_potentials.append((newfencer, p))
                    # if no fencers can be found, add all fencers from this pool
                    if (len(local_potentials) == 0):
                        # backups += p.competitors
                        for newfencer in p.competitors:
                            backups.append((newfencer, p))
                    potentials += local_potentials
            
            # prioritise equal or lower rank potentials
            potentials.sort(key = lambda potential: (potential[0].rank, -potential[0].year))
            # then go through higher rank potentials from lowest to highest
            backups.sort(key = lambda potential: (potential[0].rank, -potential[0].year), reverse = True)
            potentials += backups

            # if a potential can be swapped without imbalancing clubs, swap
            found = False
            for newfencer, p in potentials:
                if (p.clubs[newfencer.club]-1 == my_pool.clubs.get(newfencer.club, 0)):
                    found = True
                    p.competitors.remove(newfencer)
                    p.clubs[newfencer.club] -= 1
                    p.competitors.append(fencer)
                    p.clubs[fencer.club] = p.clubs.get(fencer.club, 0) + 1
                    
                    my_pool.competitors.append(newfencer)
                    if (newfencer.club != ''):
                        my_pool.clubs[newfencer.club] = my_pool.clubs.get(newfencer.club, 0) + 1
                    break
            # if a potential was not found, settle
            if (not found):
                my_pool.competitors.append(fencer)
                if (fencer.club != ''):
                    my_pool.clubs[fencer.club] = my_pool.clubs.get(fencer.club, 0) + 1
                    if (my_pool.clubs[fencer.club] == club_capacities[fencer.club][0]):
                        club_capacities[fencer.club].pop(0)
                        if (len(club_capacities[fencer.club]) == 0 or club_capacities[fencer.club][0] == 0):
                            club_capacities.pop(fencer.club, None)
        else:
            my_pool.competitors.append(fencer)
            if (fencer.club != ''):
                my_pool.clubs[fencer.club] = my_pool.clubs.get(fencer.club, 0) + 1
                if (my_pool.clubs[fencer.club] == club_capacities[fencer.club][0]):
                    club_capacities[fencer.club].pop(0)
                    if (len(club_capacities[fencer.club]) == 0 or club_capacities[fencer.club][0] == 0):
                        club_capacities.pop(fencer.club, None)
        pool_number, reverse = serpentine(pool_number, len(pools), reverse)
    
    for p in pools:
        p.competitors.sort(key=lambda fencer: (fencer.rank, -fencer.year))

    return pools


''' calculateClubDistribution
Using club counts, calculate how many of each club should be in a pool
e.g. Club count of 7 with 4 pools should return a list [2, 2, 2, 1]
'''
def calculateClubDistribution(clubs, num_pools):
    club_capacities = {}
    for c in tourney.clubs:
        if (c == ''):
            pass
        else:
            count = clubs[c]
            distribution = []
            pools_left = num_pools
            while (count != 0):
                binSize = int(math.ceil(count / pools_left))
                count -= binSize
                pools_left -= 1
                distribution.append(binSize)
            distribution += [0] * (pools_left)
            # print c, distribution
            club_capacities[c] = distribution
    return club_capacities

''' serpentine(current, datalen, reverse)
Arguments: current - current index
           datalen - dataset length
           reverse - boolean
Iterate through pools in a serpentine pattern.
e.g. 3 Pools --> 1 2 3 3 2 1 1 2 3 ...
'''
def serpentine(current, datalen, reverse):
    if (reverse):
        current -= 1
    else:
        current += 1
    if (current < 0 or current >= datalen):
        reverse = not reverse
        if (current < 0):
            current = 0
        else:
            current = datalen-1
    return current, reverse

def printPools(pools):
    print "\n\nPool List"

    for i, p in enumerate(pools):
        print "--)------- Pool # {} -------(-- ({})".format(i+1, len(p.competitors))
        for fencer in p.competitors:
            fencer.printFencer()
        print ""


if (__name__ == "__main__"):
    print "Starting..."
    if (len(sys.argv) != 2):
        print "Usage: python fencingTourney.py <filename>"
        exit()

    with open(sys.argv[1], 'r') as f:
        tourney = parseFile(f)
    tourney.printInfo()

    pools = populatePools(tourney)
    printPools(pools)
