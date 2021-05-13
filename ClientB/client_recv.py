from socket import *
recvPort = 20001
recvSocket = socket(AF_INET, SOCK_DGRAM)
recvSocket.bind(('', recvPort))
print('Ready to receive blockchain data.')

while 1:
    message, clientAddress = recvSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    print('Transactions received from full node:')
    print(modifiedMessage)

    confirmed = ['','','','']
    i = 0
    while i < len(confirmed):
        confirmed[i] = modifiedMessage[i*24:(i+1)*24]
        i += 1

    f = open('unconfirmed_tx.txt', 'rt')
    lines = f.readlines()
    f.close()

    i = 0
    while i < len(confirmed):
        j = 0
        while j < len(lines):
            lines[j] = lines[j].strip()
            if confirmed[i] == lines[j]:
                lines[j] = ''
            j += 1
        i += 1
    
    f = open('unconfirmed_tx.txt', 'wt')
    for x in lines:
        f.write(x)
    f.close()

    f = open('balance.txt', 'rt')
    balances = f.readlines()
    f.close()

    # Process balance changes for the payer
    i = 0
    while i < len(confirmed):
        j = 0
        while j < len(balances):
            balances[j] = balances[j].strip()
            if confirmed[i][:8] == balances[j][:8]:
                balances[j] = balances[j][:18] + str(hex(int(balances[j][-8:],16) - int(confirmed[i][-8:],16) - 2).split('x')[1]).upper().rjust(8,'0')
            j += 1
        i += 1
    
    # Process balance changes for the payee
    i = 0
    while i < len(confirmed):
        j = 0
        while j < len(balances):
            balances[j] = balances[j].strip()
            if confirmed[i][8:16] == balances[j][:8]:
                balances[j] = balances[j][:9] + str(hex(int(balances[j][9:17],16) + int(confirmed[i][-8:],16)).split('x')[1]).upper().rjust(8,'0') + ':' + str(hex(int(balances[j][-8:],16) + int(confirmed[i][-8:],16)).split('x')[1]).upper().rjust(8,'0')
            j += 1
        i += 1

    f = open('balance.txt', 'wt')
    for x in balances:
        f.write(x + '\n')
    f.close()

    f = open('confirmed_tx.txt', 'at')
    for x in confirmed:
        f.write(x + '\n')
    f.close()