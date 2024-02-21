import math

# global variables
MEM_SIZE = 65600
CACHE_SIZE = 1024
CACHE_BLOCK_SIZE = 64
ASSOCIATIVITY = 1


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
        self.dirty = False  # not needed for Part One
        self.valid = False
        self.data = bytearray(cache_block_size)


class CacheSet:
    def __init__(self, cache_block_size, associativity):
        self.blocks = [CacheBlock(cache_block_size) for i in range(associativity)]
        self.tag_queue = [-1 for i in range(associativity)]  # not needed for Part One


class Cache:
    def __init__(self, num_sets, associativity, cache_block_size):
        self.write_through = False  # not needed for Part One
        self.sets = [CacheSet(cache_block_size, associativity) for i in range(num_sets)]
        memory_size_bits = logb2(MEM_SIZE)
        self.cache_size_bits = logb2(CACHE_SIZE)
        self.cache_block_size_bits = logb2(CACHE_BLOCK_SIZE)
        self.index_length = logb2(num_sets)
        self.block_offset_length = logb2(CACHE_BLOCK_SIZE)


# global cache and memory
sysCache = Cache(8, ASSOCIATIVITY, CACHE_BLOCK_SIZE)
memory = bytearray(MEM_SIZE)


def main():
    readWord(46916)


def readWord(address):
    assert (checkAllignment(address) == True)
    # calculate tag, index, and offset
    numSets = CACHE_SIZE // CACHE_BLOCK_SIZE
    indexSize = logb2(numSets)
    offsetSize = logb2(CACHE_BLOCK_SIZE)
    tag = (address >> (offsetSize + indexSize)) & (2 ** (numSets - offsetSize - indexSize) - 1)
    index = (address >> offsetSize) & (2 ** indexSize - 1)
    offset = address & (2 ** offsetSize - 1)
    print("tag: ", tag, " index: ", index, " offset: ", offset)

    if sysCache.sets[index].blocks[0].tag == tag:


# if in cache: value = memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]

def writeWord(address, word):
    pass


def checkAllignment(address):
    valid = False
    memSize = (MEM_SIZE.bit_length() + 7) // 8
    if memSize > address >= 0:
        if address % 4 == 0:
            return True
    return False


main()
