import sys
from copy import deepcopy
from random import randint

class Processo:
	def __init__(self, tempoChegada, tempoDuracao):
		self.chegada = tempoChegada
		self.duracao = tempoDuracao
		self.tRetorno = 0
		self.tResposta = 0
		self.tEspera = 0

def organiza_processos():
	processos = []
	for line in sys.stdin:
		t = str(line).replace("\r", "").replace("\n", "") # Remove possíveis \r e/ou \n
		cheg, dur = t.split()
		processos.append(Processo(int(cheg), int(dur))) # Cria e salva objetos Processo em um array

	processos.sort(key=lambda p: p.chegada) # Ordena os processos pelo tempo de chegada

	return processos

def calcula_tEspera(p, i):
	if p.chegada <= i:
		p.tEspera += 1

def define_prioridades(listaProcessos):
	lista = []

	for p in listaProcessos:
		lista.append(len(listaProcessos)+1 - p.chegada)
	return lista

def atualiza_prioridadesPRI(lista, indice, parada):
	for index, value in enumerate(lista):
		if lista[index] != parada:
			if index != indice:
				lista[index] += 1
			else:
				lista[index] -= 1

processos = organiza_processos()
numProcessos = len(processos)
#tempo_total = sum(map(lambda p: int(p.duracao), processos)) # Tempo total necessario para execução de todos os processos

tempo_total = 0

for index, processo in enumerate(processos):
    if index == 0:
        tempo_total = processo.duracao
        continue

    if processo.chegada > tempo_total: 
        tempo_total += (processo.chegada - tempo_total) +  processo.duracao
    else: 
        tempo_total += processo.duracao

# ---------------------------------------PRIORIDADES DINÂMICAS--------------------------------------------
procPRI = deepcopy(processos)

temp = procPRI[0].chegada
for p in procPRI:
	p.chegada -= temp

p_atual = 0
chegadasPRI = list(map(lambda p: p.chegada, procPRI)) # Lista com os tempos de chegada de cada processo
aux_tResposta = [0]*numProcessos

prioridades = define_prioridades(procPRI)
ind_parada = min(prioridades)-1
#print("PARADA -> ", ind_parada)
#print(prioridades)
for i in range(tempo_total):

	maior = max(prioridades)
	p_atual = prioridades.index(maior)

	if i >= procPRI[p_atual].chegada:
		procPRI[p_atual].duracao -= 1
	else:
		prioridades[p_atual] += 2

	procPRI[p_atual].tRetorno = i+1 - procPRI[p_atual].chegada # Cálculo do tempo de retorno

	if aux_tResposta[p_atual] == 0: # Cálculo do tempo de resposta
		procPRI[p_atual].tResposta = i - procPRI[p_atual].chegada
		aux_tResposta[p_atual] = 1

	# Cálculo do tempo de espera
	list(map(lambda p: calcula_tEspera(p, i) if p is not procPRI[p_atual] and p.duracao != 0 else p.tEspera, procPRI))

	if procPRI[p_atual].duracao == 0:
		prioridades[p_atual] = ind_parada

	atualiza_prioridadesPRI(prioridades, p_atual, ind_parada)
	#print(prioridades)

mRetorno = sum(list(map(lambda p: p.tRetorno, procPRI)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procPRI)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procPRI)))/numProcessos

print(f"PRI {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procPRI

# ---------------------------------------------LOTERIA----------------------------------------------------

procLOT = deepcopy(processos)

temp = procLOT[0].chegada
for p in procLOT:
	p.chegada -= temp

aux_tResposta = [0]*numProcessos

for i in range(tempo_total):
	p_atual = randint(0, numProcessos-1)

	while procLOT[p_atual].duracao == 0:
		p_atual = randint(0, numProcessos-1)
		#print(p_atual)

	procLOT[p_atual].duracao -= 1
	#print("i: ", i, " atual: ", p_atual, " t: ", procLOT[p_atual].duracao)

	procLOT[p_atual].tRetorno = i+1 - procLOT[p_atual].chegada # Cálculo do tempo de retorno

	if aux_tResposta[p_atual] == 0: # Cálculo do tempo de resposta
		procLOT[p_atual].tResposta = i - procLOT[p_atual].chegada
		aux_tResposta[p_atual] = 1

	# Cálculo do tempo de espera
	list(map(lambda p: calcula_tEspera(p, i) if p is not procLOT[p_atual] and p.duracao != 0 else p.tEspera, procLOT))

	

mRetorno = sum(list(map(lambda p: p.tRetorno, procLOT)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procLOT)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procLOT)))/numProcessos

print(f"LOT {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procLOT

# --------------------------------------------ROUND ROBIN-------------------------------------------------
def escolhe_elegivel_RR(procRR, p_atual, i):
	ind_prox_proc = -1

	inelegivel = True

	cont = 1
	while inelegivel: # Enquanto o processo atual for inelegível para ser processado
		if cont == len(procRR)+1: # Caso todos tenham sido testados,
			cont = 0			  # mas nenhum é elegível, então o processador está ocioso
			ind_prox_proc = -1
			break

		p_atual = (p_atual + 1)%len(procRR) # De forma circular escolhe-se o próximo processo na lista
		ind_prox_proc = p_atual

		# Verificação se ainda é inelegível
		inelegivel = procRR[p_atual].duracao == 0 or procRR[p_atual].chegada > i 
		cont += 1

	return ind_prox_proc

procRR = deepcopy(processos)

temp = procRR[0].chegada
for p in procRR:
	p.chegada -= temp

p_atual = 0 # Índice referente ao processo atualmente em análise
quantum = 2
exec = 0 # Unidades de tempo que um processo passa executando
aux_tResposta = [0]*numProcessos # Lista auxiliar que indica se o tempo de resposta
								 # de um processo já foi calculado

for i in range(tempo_total):
	inelegivel = procRR[p_atual].duracao == 0 or procRR[p_atual].chegada > i
	
	if inelegivel: # Se o processo atual não atender aos requisitos de execução
		p_atual = escolhe_elegivel_RR(procRR, p_atual, i) # Há a tentativa de outro ser escolhido
		if p_atual == -1: # Se nenhum tiver sido escolhido
			p_atual = 0 # Volta-se para o início da lista
			continue    # E deixa-se o tempo "passar"

	#print("ATUAL -> ", p_atual)
	procRR[p_atual].duracao -= 1
	#print("i: ", i, " atual: ", p_atual, " t: ", procRR[p_atual].duracao)

	procRR[p_atual].tRetorno = i+1 - procRR[p_atual].chegada # Cálculo do tempo de retorno

	if aux_tResposta[p_atual] == 0: # Cálculo do tempo de resposta
		procRR[p_atual].tResposta = i - procRR[p_atual].chegada
		aux_tResposta[p_atual] = 1

	# Cálculo do tempo de espera
	list(map(lambda p: calcula_tEspera(p, i) if p is not procRR[p_atual] and p.duracao != 0 else p.tEspera, procRR))

	exec += 1
	# Se o processo já executou por um quantum ou já terminou
	if exec == quantum or procRR[p_atual].duracao == 0:
		p_atual = (p_atual + 1)%len(procRR)
		exec = 0

mRetorno = sum(list(map(lambda p: p.tRetorno, procRR)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procRR)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procRR)))/numProcessos

print(f"RR {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procRR