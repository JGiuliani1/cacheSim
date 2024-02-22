# global variables
MEM_SIZE = 65536
CACHE_SIZE = 1024
CACHE_BLOCK_SIZE = 64
ASSOCIATIVITY = 1
NUM_SETS = CACHE_SIZE // CACHE_BLOCK_SIZE


# helper funtions
def logb2(val):
        i = 0
        assert val > 0
        while val > 0:
            i = i + 1
            val = val >> 1
        return i - 1


# data structures
class CacheBlock:
    def __init__(self, cache_block_size):
        self.tag = -1
        self.dirty = False # not needed for Part One
        self.valid = False
        self.data = bytearray(cache_block_size)


class CacheSet:
    def __init__(self, cache_block_size, associativity):
        self.blocks = [CacheBlock(cache_block_size) for i in range(associativity)]
        self.tag_queue = [-1 for i in range(associativity)] # not needed for Part One


class Cache:
    def __init__(self, num_sets, associativity, cache_block_size):
        self.write_through = False # not needed for Part One
        self.sets = [CacheSet(cache_block_size, associativity) for i in range(num_sets)]
        self.memory_size_bits = logb2(MEM_SIZE)
        self.cache_size_bits = logb2(CACHE_SIZE)
        self.cache_block_size_bits = logb2(CACHE_BLOCK_SIZE)
        self.index_length = logb2(num_sets)
        self.block_offset_length = logb2(CACHE_BLOCK_SIZE)


# global cache and memory
sysCache = Cache(NUM_SETS, ASSOCIATIVITY, CACHE_BLOCK_SIZE)
list = []
for i in range(MEM_SIZE):
    list.append(i)
memory = bytearray(list)


def main():
    readWord(46916)
    readWord(46932)
    readWord(12936)
    readWord(13964)
    readWord(46956)
    readWord(56132)


#TODO fix return statement - think it's a problem with the way memory is initialized but not entirely sure?
def readWord(address):
    # validate address
    checkAllignment(address)

    # calculate tag, index, and offset
    indexSize = logb2(NUM_SETS)
    offsetSize = logb2(CACHE_BLOCK_SIZE)
    tag = (address >> (offsetSize + indexSize)) & (2**(NUM_SETS - offsetSize - indexSize) - 1)
    index = (address >> offsetSize) & (2**indexSize - 1)
    offset = address & (2**offsetSize - 1)

    # check if tag is in use in set of blocks - read hit
    for i in range(ASSOCIATIVITY):
        if sysCache.sets[index].blocks[i].tag == tag:
            # update tag queue
            print("read hit: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset)
            return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]
    
    # check if there are any empty blocks in the set - read miss
    for m in range(ASSOCIATIVITY):
        if sysCache.sets[index].blocks[m].valid == False:
            # update tag queue
            sysCache.sets[index].blocks[m].tag = tag
            sysCache.sets[index].blocks[m].valid = True
            rangeStart = CACHE_BLOCK_SIZE * (address // CACHE_BLOCK_SIZE)
            for j in range(rangeStart, rangeStart + CACHE_BLOCK_SIZE):
                sysCache.sets[index].blocks[m].data.append(memory[j])
            print("read miss: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset, " range: ", rangeStart, "-", rangeStart + CACHE_BLOCK_SIZE - 1)
            return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]
    
    # replace least recently used block - read miss + replace
    for n in range(ASSOCIATIVITY): # update for part 2
        # find least recently used block and update tag queue
        sysCache.sets[index].blocks[i].tag = tag
        sysCache.sets[index].blocks[i].valid = True
        rangeStart = CACHE_BLOCK_SIZE * (address // CACHE_BLOCK_SIZE)
        for j in range(rangeStart, rangeStart + CACHE_BLOCK_SIZE):
            sysCache.sets[index].blocks[i].data.append(memory[j])
        print("read miss + replace: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset, " new range: ", rangeStart, "-", rangeStart + CACHE_BLOCK_SIZE - 1)
        return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]


def writeWord(address, word):
    pass


def checkAllignment(address):
    assert address + 3 < MEM_SIZE
    assert address % 4 == 0


main()