# Fencing Tournament Structuring Problem

The task was to create a Python program to help organize the tournament structure 
for a fencing competition. The only input to the program is a file containing 
competitor information including name, club, and rank of each fencer. The program
should output the list of competitors grouped into pools of equal difficulty.

To run the program, simply type the following command into the command line.

``` python fencingTourney.py <filename> ```

## Points of Emphasis
* Similar output to samples
    * When there are no primary club balancing, the output of my program is identical to the sample
    * When there is no secondary balancing, the output of my program is identical to the sample
* Correctness
    * When there is primary and secondary club balancing, the output of my program differs from the sample only in fencer, but those fencers' ranks are the same, and the pools' club distributions are valid.
        * Further testing is needed; I can imagine a test case where a simple swap between two pools is impossible, and a third pool is needed to balance the club distribution
* Code Readability
    * I tried to keep my code organized by using OOP and writing comments where the code
    could be more confusing.
    * ```populatePools(...)``` is undoubtedly poorly written code. I wrote comments to 
    salvage it a bit, but a lot can be refactored here. If I had more time, I would fix
    this.

## Implementation
The problem was divided into 3 main parts, as suggested by the handout.
* Parsing the file
* Evenly distributing the competitors into pools by difficulty
* Balancing the pools by clubs

### Parsing the file
This was by far the easiest part of implementing this program. I read the input
file line by line and then separated the columns using regular expressions and 
the ```re.split()``` command from Python's regular expressions library. I created 
a class called ```Fencer``` to organize competitor information.

All Fencers were stored in a ```list``` which was then sorted by rank and year 
using ```list.sort()``` and lambda functions.

The total club counts for the entire tournament was also stored as a ```dict```.

Fencers and total club counts were stored in a ```Tourney``` object.

### Evenly distributing the competitors into pools by difficulty
This as also a fairly simple implementation. This was achieved by following the 
serpentine pattern suggestion from the handout. I implemented a function called 
```serpentine(...)``` to help with iterating back and forth through the pools.

### Balancing the pools by clubs
The bulk of the problem was this one. This is also where my code turned into
spaghetti, which I would definitely try to fix if I had more time.

This was a bit of a confusing concept, so I spent some time going through the 
sample tests by hand and finding the pattern. I discovered that the pools deviate 
from the serpentine pattern when a pool encounters a competitor from a club that
can no longer be accomodated. The pool would skip forward in the competitors list
until it reaches a competitor from a club that could be accomodated.

Once I implemented that, I ran into a problem where there were no more competitors
to add besides ones from the filled up club. I solved this by

1. Looking through all pools to find one that could accomodate said members of that club

    I kept track of club counts in individual pools. If that club count is less than 
    the maximum bin size left for that club, the pool is a viable candidate.

2. Iterating through those pools to find potential swaps by rank, and finally

    When encountering a viable pool, look for fencers with equal or lower rank, and add 
    it to a list of potential swaps.

    If there are no fencers with a lower rank from that pool, add all fencers to a list 
    of backups

3. Iterating through the potential swaps to find swaps that could work without messing
up the club balance for the two pools.

    First, sort potential swaps by rank and year, starting with equal rank of fencer to 
    be swapped. Then sort backups in reverse, from lowest to highest rank. Append the 
    backups to the potentials, resulting in a potential list with ranks in a parabolic 
    order from high to lowest to highest

    Iterate through the new potentials list and check if the swap keeps the club 
    balances the same. If yes, do the swap and continue.

    This method could potentially fail. There could be a complicated scenario where a 
    swap between two pools is impossible, and a third or even fourth (we could go on) 
    is necessary to break a tie. In this case, the algorithm will settle for an 
    imbalanced club distribution.



