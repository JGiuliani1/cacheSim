# global constant variables
WORDLENGTH = 4
MEM_SIZE = 65536
CACHE_SIZE = 1024
CACHE_BLOCK_SIZE = 64
ASSOCIATIVITY = 4
NUM_SETS = CACHE_SIZE // (CACHE_BLOCK_SIZE * ASSOCIATIVITY)
NUM_BLOCKS = CACHE_SIZE // CACHE_BLOCK_SIZE
WRITE_THRU = True  # if true write through cache if false write-back cache


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
memory = bytearray(MEM_SIZE)
memory_size_bits = 0
cache = None


def main():
    # initialize cache and memory
    global cache
    cache = Cache(NUM_SETS, ASSOCIATIVITY, CACHE_BLOCK_SIZE)
    for i in range(MEM_SIZE // 4):
        word_to_bytes(memory, 4 * i, 4 * i, WORDLENGTH)

    # testing
    readWord(1152)
    readWord(2176)
    readWord(3200)

    readWord(4224)
    readWord(5248)
    readWord(7296)
    readWord(4224)
    readWord(3200)
    writeWord(7312, 17)

    readWord(7320)
    readWord(4228)
    readWord(3212)
    writeWord(5248, 5)
    readWord(5248)
    writeWord(8320, 7)
    readWord(8324)
    readWord(9344)
    readWord(11392)
    readWord(16512)
    readWord(17536)
    readWord(8320)
    readWord(17536)
    readWord(17532)



def readWord(address):
    # validate address
    checkAllignment(address)

    # calculate tag, index, offset, and ranges
    tag = address >> (cache.index_length + cache.block_offset_length)
    index = (address // CACHE_BLOCK_SIZE) & (NUM_SETS - 1)
    offset = address & (CACHE_BLOCK_SIZE - 1)
    range_low = (address >> cache.cache_block_size_bits) * CACHE_BLOCK_SIZE
    range_high = range_low + CACHE_BLOCK_SIZE - 1

    # check if tag is used in block set
    found = False
    blockIndex = 0
    for i in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[i].tag == tag:
            blockIndex = i
            found = True

    if found: # read hit
        if not cache.sets[index].blocks[blockIndex].valid:
            print("tag found, block invalid")
            assert cache.sets[index].blocks[blockIndex].valid
        # update tag queue
        tagQueueIndex = 0
        for i in range(ASSOCIATIVITY):
            if cache.sets[index].tag_queue[i] == tag:
                tagQueueIndex = i
        for i in range(tagQueueIndex, ASSOCIATIVITY - 1):
            cache.sets[index].tag_queue[i] = cache.sets[index].tag_queue[i + 1]
        cache.sets[index].tag_queue[ASSOCIATIVITY - 1] = tag
        # print output and return value
        memval = bytes_to_word(cache.sets[index].blocks[blockIndex].data, offset, WORDLENGTH)
        print(f'read hit [addr={address} index={index} block_index={blockIndex} tag={tag}: word={memval} ({range_low} - {range_high})]')
        print(cache.sets[index].tag_queue)
        return memval
    
    # find block that was used the least recently and get its index in the set
    lastUsed = cache.sets[index].tag_queue[0]
    lastUsedIndex = 0
    blockDirty = False
    for i in range(ASSOCIATIVITY - 1, -1, -1):
        if cache.sets[index].blocks[i].tag == lastUsed:
            lastUsedIndex = i
            if cache.sets[index].blocks[i].dirty:
                blockDirty = True
    
    # write to memory if block is dirty - for write back cache
    if blockDirty == True:
        # write the blockSize byes of block j of set i to memory at A to A+blockSize-1
        setBits = logb2(NUM_SETS)
        blockSizeBits = logb2(CACHE_BLOCK_SIZE)
        A = (cache.sets[index].blocks[lastUsedIndex].tag << (setBits + blockSizeBits)) + (i << blockSizeBits)
        for i in range(CACHE_BLOCK_SIZE):
            memory[A + i] = cache.sets[index].blocks[lastUsedIndex].data[i]
    
    # read in data from memory
    blockStart = (address >> cache.cache_block_size_bits) * CACHE_BLOCK_SIZE
    for i in range(CACHE_BLOCK_SIZE):
        cache.sets[index].blocks[lastUsedIndex].data[i] = memory[blockStart + i]
    
    # change tag, dirty, and valid attributes
    cache.sets[index].blocks[lastUsedIndex].valid = True
    cache.sets[index].blocks[lastUsedIndex].dirty = False
    cache.sets[index].blocks[lastUsedIndex].tag = tag
    
    # update tag queue
    for i in range(0, ASSOCIATIVITY):
        if i == ASSOCIATIVITY - 1:
            cache.sets[index].tag_queue[i] = tag
        else:
            cache.sets[index].tag_queue[i] = cache.sets[index].tag_queue[i + 1]
    
    # print output and return value
    memval = bytes_to_word(cache.sets[index].blocks[lastUsedIndex].data, offset, WORDLENGTH)
    if lastUsed == -1:
        print(f'read miss [addr={address} index={index} block_index={lastUsedIndex} tag={tag}: word={memval} ({range_low} - {range_high})]')
    else:
        print(f'read miss + replace [addr={address} index={index} block_index={lastUsedIndex} tag={tag}: word={memval} ({range_low} - {range_high})]')
        print(f'evict tag {lastUsed} in blockIndex {lastUsedIndex}')
    print(cache.sets[index].tag_queue)
    return memval

def writeWord(address, word):
    # validate address
    checkAllignment(address)

    # calculate tag, index, offset, and ranges
    tag = address >> (cache.index_length + cache.block_offset_length)
    index = (address // CACHE_BLOCK_SIZE) & (NUM_SETS - 1)
    offset = address & (CACHE_BLOCK_SIZE - 1)
    range_low = (address >> cache.cache_block_size_bits) * CACHE_BLOCK_SIZE
    range_high = range_low + CACHE_BLOCK_SIZE - 1

    # check if tag is used in block set
    found = False
    blockIndex = 0
    for i in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[i].tag == tag:
            blockIndex = i
            found = True
    if found:  # read hit
        if not cache.sets[index].blocks[blockIndex].valid:
            print("tag found, block invalid")
            assert cache.sets[index].blocks[blockIndex].valid

        # update tag queue
        if cache.sets[index].tag_queue[ASSOCIATIVITY - 1] == -1:
            cache.sets[index].tag_queue[ASSOCIATIVITY - 1] = tag
        else:
            dupe_tag_index = 1
            for i in range(ASSOCIATIVITY):
                if cache.sets[index].tag_queue[i] == tag:
                    dupe_tag_index = i + 1
            for x in range(dupe_tag_index, ASSOCIATIVITY, 1):
                cache.sets[index].tag_queue[x - 1] = cache.sets[index].tag_queue[x]
            cache.sets[index].tag_queue[ASSOCIATIVITY - 1] = tag
        
        # change dirty flag
        cache.sets[index].blocks[blockIndex].dirty = True

        # memval = bytes_to_word(cache.sets[index].blocks[blockIndex].data, offset, WORDLENGTH)
        print(f'write {word} to memory address {address}; should be a write hit')
        print(
            f'write hit [addr={address} index={index} block_index={blockIndex} tag={tag}: word={word} ({range_low} - {range_high})]')
        print(cache.sets[index].tag_queue)
        # write to cache
        word_to_bytes(cache.sets[index].blocks[blockIndex].data, offset, word, WORDLENGTH)
        # if write thru then write to memory as well
        if WRITE_THRU:
            word_to_bytes(memory, offset, word, WORDLENGTH)
            print(f'Write-through cache: write {word} to memory[{address}]')
        print()
        memval = None
        return memval

    lastUsed = cache.sets[index].tag_queue[0]
    lastUsedIndex = 0
    dirty = False
    for i in range(ASSOCIATIVITY):
        if cache.sets[index].blocks[i].tag == lastUsed:
            lastUsedIndex = i
            if cache.sets[index].blocks[i].dirty:
                dirty = True
    if dirty == True:
        # write the blockSize byes of block j of set i to memory at A to A+blockSize-1
        setBits = logb2(NUM_SETS)
        blockSizeBits = logb2(CACHE_BLOCK_SIZE)
        A = (cache.sets[index].blocks[lastUsedIndex].tag << (setBits + blockSizeBits)) + (i << blockSizeBits)
        for i in range(CACHE_BLOCK_SIZE):
            memory[A + i] = cache.sets[index].blocks[lastUsedIndex].data[i]
    blockStart = (address >> cache.cache_block_size_bits) * CACHE_BLOCK_SIZE
    for i in range(CACHE_BLOCK_SIZE):
        cache.sets[index].blocks[lastUsedIndex].data[i] = memory[blockStart + i]
    cache.sets[index].blocks[lastUsedIndex].valid = True
    cache.sets[index].blocks[lastUsedIndex].dirty = False
    cache.sets[index].blocks[lastUsedIndex].tag = tag

    # update tag queue
    if cache.sets[index].tag_queue[ASSOCIATIVITY - 1] == -1:
        cache.sets[index].tag_queue[ASSOCIATIVITY - 1] = tag
    else:
        dupe_tag_index = 1
        for i in range(ASSOCIATIVITY):
            if cache.sets[index].tag_queue[i] == tag:
                dupe_tag_index = i + 1
        for x in range(dupe_tag_index, ASSOCIATIVITY, 1):
            cache.sets[index].tag_queue[x - 1] = cache.sets[index].tag_queue[x]
        cache.sets[index].tag_queue[ASSOCIATIVITY - 1] = tag

    memval = bytes_to_word(cache.sets[index].blocks[lastUsedIndex].data, offset, WORDLENGTH)
    if lastUsed == -1:
        print(
            f'write miss [addr={address} index={index} block_index={lastUsedIndex} tag={tag}: word={memval} ({range_low} - {range_high})]')
        word_to_bytes(cache.sets[index].blocks[lastUsedIndex].data, offset, word, WORDLENGTH)
    else:
        print(
            f'write miss + replace [addr={address} index={index} block_index={lastUsedIndex} tag={tag}: word={memval} ({range_low} - {range_high})]')
        print(f'evict tag {lastUsed} in blockIndex {lastUsedIndex}')
        print(f'read in {range_low}-{range_high}')
        word_to_bytes(cache.sets[index].blocks[lastUsedIndex].data, offset, word, WORDLENGTH)
    print(cache.sets[index].tag_queue)
    if WRITE_THRU:
        word_to_bytes(memory, offset, word, WORDLENGTH)
        print(f'Write-through cache: write {word} to memory[{address}]')
    print()

    return memval


def checkAllignment(address):
    assert address + 3 < MEM_SIZE
    assert address % 4 == 0


def word_to_bytes(destination, start, word, size):
    for i in range(size):
        v = word % 256
        destination[i + start] = v
        word = word // 256


def bytes_to_word(source, start, size):
    word = 0
    mult = 1
    for i in range(size):
        word = word + mult * source[start + i]
        mult = mult * 256
    return word


main()
