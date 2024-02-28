# global constant variables
WORDLENGTH = 4
MEM_SIZE = 65536
CACHE_SIZE = 1024
CACHE_BLOCK_SIZE = 64
ASSOCIATIVITY = 4
NUM_SETS = CACHE_SIZE // (CACHE_BLOCK_SIZE * ASSOCIATIVITY)
NUM_BLOCKS = CACHE_SIZE // CACHE_BLOCK_SIZE


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
        memory_size_bits = logb2(MEM_SIZE)
        self.cache_size_bits = logb2(CACHE_SIZE)
        self.cache_block_size_bits = logb2(CACHE_BLOCK_SIZE)
        self.index_length = logb2(num_sets)
        self.block_offset_length = logb2(CACHE_BLOCK_SIZE)


# global cache and memory
memory = bytearray(MEM_SIZE)
memory_size_bits = 0
cache = None


def main():
    # initialize cache and memory
    global cache
    cache = Cache(NUM_SETS, ASSOCIATIVITY, CACHE_BLOCK_SIZE)
    for i in range(MEM_SIZE // 4):
        word_to_bytes(memory, 4*i, 4*i, WORDLENGTH)
    print(readWord(1152))


"""def readWord(address):
    # validate address
    checkAllignment(address)

    # calculate tag, index, offset, and ranges
    tag = (address >> (cache.block_offset_length + cache.index_length)) & (2**(NUM_SETS - cache.block_offset_length - cache.index_length) - 1)
    index = (address >> cache.block_offset_length) & (2**cache.index_length - 1)
    offset = address & (2**cache.block_offset_length - 1)

    # check if tag is used in block set
    found = False
    for blockIndex in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[blockIndex].tag == tag:
            found = True

    if found: # read hit
        if not cache.sets[index].blocks[blockIndex].valid:
            print("tag found, block invalid")
            assert cache.sets[index].blocks[blockIndex].valid
        return bytes_to_word(cache.sets[index].blocks[blockIndex].data, offset, WORDLENGTH)

    # caculate block start and end
    range_low = (address >> cache.cache_block_size_bits) * CACHE_BLOCK_SIZE
    range_high = range_low + CACHE_BLOCK_SIZE - 1
    lastUsed = cache.sets[index].tag_queue[ASSOCIATIVITY - 1]
    print(lastUsed)
    if cache.sets[index].blocks.index(lastUsed).dirty:
        # write the blockSize byes of block j of set i to memory at A to A+blockSize-1
        pass"""


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
        print(cache.sets[index].blocks[i].tag)
        if cache.sets[index].blocks[i].tag == tag:
            # update tag queue
            # update tag queue - make sure it doesn't overfill
            if cache.sets[index].tag_queue[0] == -1:
                cache.sets[index].tag_queue[0] = tag
            else:
                for x in range(ASSOCIATIVITY - 2, -1, -1):
                    cache.sets[index].tag_queue[x + 1] = cache.sets[index].tag_queue[x]
                cache.sets[index].tag_queue[0] = tag

            # set dirty flag to true
            cache.sets[index].blocks[i].dirty = True

            #return cache
            print("read hit: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset)
            return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]

    # check if there are any empty blocks in the set - read miss
    for m in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[m].valid == False:
            # update tag queue
            cache.sets[index].blocks[m].tag = tag
            cache.sets[index].blocks[m].valid = True
            rangeStart = CACHE_BLOCK_SIZE * (address // CACHE_BLOCK_SIZE)
            for j in range(rangeStart, rangeStart + CACHE_BLOCK_SIZE):
                cache.sets[index].blocks[m].data.append(memory[j])
            print("read miss: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset, " range: ", rangeStart, "-", rangeStart + CACHE_BLOCK_SIZE - 1)
            return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]

    # replace least recently used block - read miss + replace
    for n in range(ASSOCIATIVITY): # update for part 2
        # find least recently used block and update tag queue
        cache.sets[index].blocks[i].tag = tag
        cache.sets[index].blocks[i].valid = True
        rangeStart = CACHE_BLOCK_SIZE * (address // CACHE_BLOCK_SIZE)
        for j in range(rangeStart, rangeStart + CACHE_BLOCK_SIZE):
            cache.sets[index].blocks[i].data.append(memory[j])
        print("read miss + replace: adress = ", address, " index: ", index, " block index: ", i," tag: ", tag, " offset: ", offset, " new range: ", rangeStart, "-", rangeStart + CACHE_BLOCK_SIZE - 1)
        return memory[address] + 256*memory[address + 1] + 256**2*memory[address + 2] + 256**3*memory[address + 3]


def writeWord(address, word):
    pass
    # validate address
    checkAllignment(address)

    # calculate tag, index, and offset
    indexSize = logb2(NUM_SETS)
    offsetSize = logb2(CACHE_BLOCK_SIZE)
    tag = (address >> (offsetSize + indexSize)) & (2 ** (NUM_SETS - offsetSize - indexSize) - 1)
    index = (address >> offsetSize) & (2 ** indexSize - 1)
    offset = address & (2 ** offsetSize - 1)

    # check if tag is in use in set of blocks - read hit
    for i in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[i].tag == tag:
            # update tag queue - make sure it doesn't overfill
            if cache.sets[index].tag_queue[0] == -1:
                cache.sets[index].tag_queue[0] = tag
            else:
                for x in range(ASSOCIATIVITY - 2, -1, -1):
                    cache.sets[index].tag_queue[x + 1] = cache.sets[index].tag_queue[x]
                cache.sets[index].tag_queue[0] = tag

            # set dirty flag to true
            cache.sets[index].blocks[i].dirty = True

            # print and write given word
            print("read hit: address = ", address, " index: ", index, " block index: ", i, " tag: ", tag, " offset: ",
                  offset)
            cache.sets[index].blocks[i].data = (
                    memory[address] + 256 * memory[address + 1] + 256 ** 2 * memory[address + 2] + 256 ** 3 *
                    memory[
                        address + 3])

    for m in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[m].valid == False:
            # update tag queue
            cache.sets[index].blocks[m].tag = tag
            cache.sets[index].blocks[m].valid = True
            rangeStart = CACHE_BLOCK_SIZE * (address // CACHE_BLOCK_SIZE)
            for j in range(rangeStart, rangeStart + CACHE_BLOCK_SIZE):
                cache.sets[index].blocks[m].data.append(memory[j])
            print("read miss: address = ", address, " index: ", index, " block index: ", i, " tag: ", tag, " offset: ",
                  offset, " range: ", rangeStart, "-", rangeStart + CACHE_BLOCK_SIZE - 1)
            return memory[address] + 256 * memory[address + 1] + 256 ** 2 * memory[address + 2] + 256 ** 3 * memory[
                address + 3]


def checkAllignment(address):
    assert address + 3 < MEM_SIZE
    assert address % 4 == 0


def word_to_bytes(destination, start, word, size):
    for i in range(size):
        v = word % 256
        destination[i+start] = v
        word = word // 256


def bytes_to_word(source, start, size):
    word = 0
    mult = 1
    for i in range(size):
        word = word + mult * source[start+i]
        mult = mult * 256
    return word



main()
