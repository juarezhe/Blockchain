from socket import *
IP = 'localhost'
nodePort = 20000

menu = '1. Enter a new transaction.'
menu += '\n2. The current balance for each account.'
menu += '\n3. Print the unconfirmed transactions.'
menu += '\n4. Print the last 10 confirmed transactions.'
menu += '\n5. Print the blockchain.'
menu += '\nEnter \'exit\' to exit.'
tx_fee = 2

def transaction():
    f = open('balance.txt', 'rt')
    print('Select the payer:')
    count = 0
    payer = [0, 0]
    txString = ''

    for x in f:
        payer[count] = x[0:8]
        print(str(count + 1) + '. ' + payer[count])
        count += 1
    
    option = int(input('Choice: '))
    txString += payer[option-1]
    f.close()

    print('Select the payee:')
    count = 0
    payee = [0, 0]
    for x in payer:
        if(payer[count][0] == 'A'):
            payee[count] = 'B'
        else:
            payee[count] = 'A'
        payee[count] += payer[count][1:8]
        print(str(count + 1) + '. ' + payee[count])
        count += 1
    
    option = int(input('Choice: '))
    txString += payee[option-1]

    print('Enter the amount of payment in decimal:')
    tx_amt = input()
    # Read the available accounts from balance file and
    # use the line where the account matches the user's
    # selection
    f = open('balance.txt', 'rt')
    lines = f.readlines()
    f.close()
    count = 0
    while count < len(lines):
        if lines[count][0:8] == txString[0:8]:
            break
        count += 1

    f = open('unconfirmed_tx.txt', 'rt')
    temp_tx_count = f.readlines()
    f.close()

    if int(lines[count][9:17],16) < int(tx_amt) + tx_fee:
        print('Error: Insufficient balance. Please try again.')
    else:
        # Update the temporarily stored balance file content
        # then rewrite the file with the updated values
        new_bal = lines[count][0:9] + str(hex(int(lines[count][9:17],16) - int(tx_amt) - 2).split('x')[1]).upper().rjust(8,'0') + lines[count][17:26] + '\n'
        lines[count] = new_bal
        f = open('balance.txt', 'wt')
        for x in lines:
            f.write(x)
        f.close()
        
        txString += str(hex(int(tx_amt)).split('x')[1]).upper().rjust(8,'0')
        print('Tx: ' + txString[0:8] +' pays ' + txString[8:16] + ' the amount of ' + str(int(txString[16:24],16)) + ' BC.')

        sendSocket = socket(AF_INET, SOCK_DGRAM)
        sendSocket.sendto(txString.encode(),(IP, nodePort))
        sendSocket.close()
        f = open('unconfirmed_tx.txt', 'a')
        f.write(txString + '\n')
        f.close()

def checkBalance():
    print('Account\t\tUnconfirmed\tConfirmed')
    f = open('balance.txt', 'rt')
    balances = f.readlines()
    f.close()

    for x in balances:
        x.strip()
        print(x[:8] + '\t' + str(int(x[9:17],16)) + '\t\t' + str(int(x[-8:],16)))
    print()

def listUnconfirmed():
    print('Transactions listed in order from newest to oldest.')
    print('Payer\t\tPayee\t\tAmount')
    f = open('unconfirmed_tx.txt', 'rt')
    unconfirmed = f.readlines()
    f.close()

    i = len(unconfirmed) - 1
    while i >= 0:
        print(unconfirmed[i][:8] + '\t' + unconfirmed[i][8:16] + '\t' + str(int(unconfirmed[i][-8:],16)))
    print()

def listConfirmed():
    print('Transactions listed in order from newest to oldest.')
    print('Payer\t\tPayee\t\tAmount')
    f = open('confirmed_tx.txt', 'rt')
    confirmed = f.readlines()
    f.close()

    i = len(confirmed) - 1
    count = 1
    while i >= 0 and count <= 10:
        print(confirmed[i][:8] + '\t' + confirmed[i][8:16] + '\t' + str(int(confirmed[i][-8:],16)))
        i -= 1
        count += 1
    print()

def getBlockchain():
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.sendto('BC'.encode(),(IP, nodePort))
    blockchain, nodeAddress = sendSocket.recvfrom(2048)
    sendSocket.close()
    return blockchain.decode()

def printBlockchain(data):
    blocks = data.strip().split('\n')
    for x in blocks:
        print('Hash: ' + x[8:72])
        print('\tPayer\t\tPayee\t\tAmount')
        print('\t' + x[-24:-16] + '\t' + x[-16:-8] + '\t' + str(int(x[-8:],16)))
        print('\t' + x[-48:-40] + '\t' + x[-40:-32] + '\t' + str(int(x[-32:-24],16)))
        print('\t' + x[-72:-64] + '\t' + x[-64:-56] + '\t' + str(int(x[-56:-48],16)))
        print('\t' + x[-96:-88] + '\t' + x[-88:-80] + '\t' + str(int(x[-80:-72],16)))

while 1:
    print(menu)
    option = input()

    if option == 'exit':
        break
    if option == '1':
        transaction()
    elif option == '2':
        checkBalance()
    elif option == '3':
        listUnconfirmed()
    elif option == '4':
        listConfirmed()
    elif option == '5':
        printBlockchain(getBlockchain())
    else:
        print('Command not recognized. Please try again.')