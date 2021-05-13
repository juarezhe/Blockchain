from socket import *
import hashlib
IP = 'localhost'
nodePort = 10000
clientPort = 20001

recvPort = 20000
recvSocket = socket(AF_INET,SOCK_DGRAM)
recvSocket.bind(('',recvPort))
print('The server is ready to receive')

# Turn is based on full node number
# F1 goes first then F2
f = open('balance.txt', 'rt')
line = f.readline()
f.close()
turn = int(line[1])

Tx_list = ['','','','']
index = 0

def mineBlock():
    # Find merkle root from the transactions
    firstPass = ['','','','']
    i = 0
    while i < len(Tx_list):
        m = hashlib.sha256()
        m.update(Tx_list[i].encode("utf-8"))
        firstPass[i] = m.hexdigest()
        i += 1

    secondPass = ['','']
    i = 0
    while i < 2:
        m = hashlib.sha256()
        m.update((firstPass[i * 2] + firstPass[i * 2 + 1]).encode("utf-8"))
        secondPass[i] = m.hexdigest()
        i += 1

    m = hashlib.sha256()
    m.update((secondPass[0] + secondPass[1]).encode("utf-8"))
    merkle = m.hexdigest()

    # Read last block
    lastBlock = getLastBlock()

    # If this is the first block written to the chain,
    # use 0's for the last block hash
    if lastBlock == '':
        lastBlockHash = '0000000000000000000000000000000000000000000000000000000000000000'
    
    # Otherwise use the hash of the last block
    else:
        h = hashlib.sha256()
        h.update(lastBlock.encode("utf-8"))
        lastBlockHash = h.hexdigest()

    # Find nonce
    hashHandler = hashlib.sha256()
    nonce = 0
    while True:
        blockHeader = str(nonce) + lastBlockHash + merkle
        hashHandler.update(blockHeader.encode("utf-8"))
        hashValue = hashHandler.hexdigest()
        if hashValue[0:4] == '0000':
            break
        else:
            nonce += 1

    # Concatenate entire block, write to file, and share
    block = str(hex(nonce).split('x')[1].rjust(8,'0') + lastBlockHash.rjust(64,'0') + merkle.rjust(32,'0') + (Tx_list[0]+Tx_list[1]+Tx_list[2]+Tx_list[3]).rjust(48,'0')).upper()
    writeBlock(block)
    writeBalance(30 + 2 * 4)

    lastBlock = getLastBlock()
    if (block == lastBlock):
        sendMessage(block,IP,nodePort)

        transactions = block[-96:]
        sendMessage(transactions, IP, clientPort)
    else:
        print('Error: mismatch between processed block and last block.')

def writeBalance(amt):
    f = open('balance.txt', 'rt')
    balance = f.readline()
    f.close()

    balance_new = balance[:9] + str(hex(int(balance[9:17],16) + amt).split('x')[1]).upper().rjust(8,'0') + ':' + str(hex(int(balance[-8:],16) + amt).split('x')[1]).upper().rjust(8,'0')

    f = open('balance.txt', 'wt')
    f.write(balance_new)
    f.close()    

def writeBlock(blockData):
    f = open("blockchain.txt", 'at')
    f.write(blockData + '\n')
    f.close()

def getLastBlock():
    f = open("blockchain.txt", 'rt')
    blockchain = f.read()
    f.close()

    if blockchain == '':
        returnValue = ''
    else:
        returnValue = blockchain.strip()[-232:]
    
    return returnValue

def sendMessage(msg, IP, port):
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.sendto(msg.encode(),(IP,port))

while 1:
    message, clientAddress = recvSocket.recvfrom(2048)
    modifiedMessage = message.decode()

    if(modifiedMessage[:2] == 'BC'):
        f = open("blockchain.txt", 'rt')
        rawBC = f.readlines()
        f.close()

        blockchain = ''
        i = len(rawBC) - 1
        while i >= 0:
            blockchain += rawBC[i]            
            i -= 1

        recvSocket.sendto(blockchain.encode(), clientAddress)
    else:
        # If message is of length 232, it's a block
        if(len(modifiedMessage) == 232):
            print("Block received: " + modifiedMessage) # Print the received block
            writeBlock(modifiedMessage) # Write the block to the blockchain

            # Verify write then send transactions to client
            lastBlock = getLastBlock()
            if (modifiedMessage == lastBlock):
                transactions = lastBlock[-96:]
                sendMessage(transactions, IP, clientPort)
            else:
                print('Error: mismatch between received message and last block.')

        # Otherwise, it's a transaction
        else:
            # If first two chars are FN, the tx is from the other node,
            # so strip the header then proceed.
            if modifiedMessage[:2] == 'FN':
                modifiedMessage = modifiedMessage[-24:]

            # Otherwise, it's from the client, so prepend FN and share
            # tx with other node then proceed.
            else:
                sendMessage('FN' + modifiedMessage,IP,nodePort)
            
            print("Transaction received: " + modifiedMessage)
            Tx_list[index] = modifiedMessage
            index += 1

            # If the Tx_list fills up, reset index for the next four transactions
            if(index == 4):
                index = 0
                turn += 1

                # Determine whose turn it is to mine the block
                if(turn%2==1):
                    print('It\'s the other node\'s turn')
                else:
                    mineBlock() # Mine the block

                    # Clear Tx_list for the next four transactions
                    j = 0
                    while j < len(Tx_list):
                        Tx_list[j] = ''
                        j += 1