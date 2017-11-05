"""
Automatically align columns to produce a pretty looking table.
"""

class Block:
    def __init__(self, minLen):
        '''
        minLen: minimum length of the block, this means that if the text is
                shorter than the minLen, add spaces to the end; if the text
                is longer than the length, then keep the whole length of the
                text.
        '''
        self.text = ''
        self.minLen = minLen
    
    def adjustLen(self, length):
        assert length >= len(self.text) # not nessarily, just a reminder
        self.text = self.text + ' ' * (length - len(self.text))

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text

    def write(self, text):
        self.text = text
        if len(self) < self.minLen:
            self.adjustLen(self.minLen)


class Line:
    def __init__(self, numBlock, spacing, minBlockLen):
        '''
        numBlock: number of blocks in the line.
        spacing: space between blocks.
        minBlockLen: a list of minimum length for each block.
        '''
        self.spacing = spacing
        self.block = []
        for i in range(numBlock):
            self.block.append(Block(minBlockLen[i]))

    def __str__(self):
        output = ''
        for blk in self.block[0:-1]:
            output = output + blk.__str__() + ' ' * self.spacing
        output = output + self.block[-1].__str__() # last block of the line
        return output

    def write(self, text, blockNum):
        self.block[blockNum].write(text)

    def adjustLen(self, blockLen):
        '''
        blockLen: a list of length correspond to each block of the line.
        '''
        for i in range(len(self.block)):
            if blockLen[i] > len(self.block[i]):
                self.block[i].adjustLen(blockLen[i])


class PrettyTable:
    def __init__(self, numBlock = 0, spacing = 2, header = '', footer = ''):
        '''
        numBlock: number of blocks per line.
        spacing: space between blocks.
        '''
        assert numBlock != 0 # You must set a number of blocks!
        self.line = []
        self.header = header
        self.footer = footer
        self.label = ''
        self.numBlock = numBlock
        self.blockLen = [] # Latest length of each block.
        self.spacing = spacing
        self.updateReqest = False
        for i in range(self.numBlock):
            self.blockLen.append(0)

    def addHeader(self, header):
        self.header = header
        
    def addFooter(self, footer):
        self.footer = footer

    def addLabel(self, col_name):
        underline = ['-'*len(s) for s in col_name]
        self.writeLine(col_name)
        self.writeLine(underline)

    def writeLine(self, line):
        '''
        line: a list of string.
        '''
        assert len(line) == self.numBlock
        self.line.append(Line(self.numBlock, self.spacing, self.blockLen))
        for i in range(len(line)):
            self.line[-1].write(line[i], i)
            if len(line[i]) > self.blockLen[i]:
                self.blockLen[i] = len(line[i])
                self.updateReqest = True
        self.__alignBlocks()

    def __alignBlocks(self):
        if self.updateReqest:
            for eachLine in self.line[0:-1]:
                eachLine.adjustLen(self.blockLen)
            self.updateReqest = False
        
    def __str__(self):
        output = ''
        if self.header != '':
            output = self.header + '\n'
        for eachLine in self.line:
            output = output + eachLine.__str__() + '\n'
        output = output + self.footer
        return output

if __name__ == '__main__':
    table = PrettyTable(3)
    table.addLabel(['Name', 'age', 'Address'])
    table.writeLine(['abc', '999', 'abc'])
    table.writeLine(['adf', '123', 'ope'])
    print(table)
