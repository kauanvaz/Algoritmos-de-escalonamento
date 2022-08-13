import sys
from copy import deepcopy

class Processo:
	def __init__(self, tempoChegada, tempoDuracao):
		self.chegada = tempoChegada
		self.duracao = tempoDuracao
		self.tRetorno = 0
		self.tResposta = 0
		self.tEspera = 0
    	#self.OrigArrival = self.Arrival
    	#self.Response = 0
    	#self.TotalResponse = 0
    	#self.Wait = 0
    	#self.TurnAround = 0

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

def atualiza_prioridadesPRI(lista, indice):
	for index, value in enumerate(lista):
		if lista[index] != -1:
			if index != indice:
				lista[index] += 1
			else:
				lista[index] -= 1

processos = organiza_processos()
tempo_total = sum(map(lambda p: int(p.duracao), processos)) # Tempo total necessario para execução de todos os processos
numProcessos = len(processos)

# ---------------------------------------PRIORIDADES DINÂMICAS--------------------------------------------
procPRI = deepcopy(processos)
p_atual = 0
chegadasPRI = list(map(lambda p: p.chegada, procPRI)) # Lista com os tempos de chegada de cada processo
aux_tResposta = [0]*len(procPRI)

prioridades = define_prioridades(procPRI)
#print(prioridades)
for i in range(tempo_total):

	maior = max(prioridades)
	p_atual = prioridades.index(maior)

	procPRI[p_atual].duracao -= 1

	procPRI[p_atual].tRetorno = i+1 - procPRI[p_atual].chegada # Cálculo do tempo de retorno

	if aux_tResposta[p_atual] == 0: # Cálculo do tempo de resposta
		procPRI[p_atual].tResposta = i - procPRI[p_atual].chegada
		aux_tResposta[p_atual] = 1

	# Cálculo do tempo de espera
	list(map(lambda p: calcula_tEspera(p, i) if p is not procPRI[p_atual] and p.duracao != 0 else p.tEspera, procPRI))

	if procPRI[p_atual].duracao == 0:
		prioridades[p_atual] = -1

	atualiza_prioridadesPRI(prioridades, p_atual)
	#print(prioridades)

mRetorno = sum(list(map(lambda p: p.tRetorno, procPRI)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procPRI)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procPRI)))/numProcessos

print(f"PRI {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procPRI

# --------------------------------------------ROUND ROBIN-------------------------------------------------
# VERIFICAR DEPOIS PARA PROCESSOS QUE NÃO TEM INSTANTES DE CHEGADAS SEGUIDOS
procRR = deepcopy(processos)

temp = procRR[0].chegada
for p in procRR:
	p.chegada -= temp

p_atual = 0 # Índice referente ao processo atualmente em análise
quantum = 2
exec = 0 # Unidades de tempo que um processo passa executando
aux_tResposta = [0]*len(procRR)

for i in range(tempo_total):
	if procRR[p_atual].duracao == 0 or procRR[p_atual].chegada > i: # PROVAVELMENTE DÁ PRA MELHORAR (TALVEZ REMOVER) ESSE IF
		if p_atual == len(procRR)-1:
			p_atual = 0
		else:
			while procRR[p_atual].duracao == 0 or procRR[p_atual].chegada > i: # Passa os processos na lista que já terminaram a execução
				p_atual += 1
				
	procRR[p_atual].duracao -= 1
	#print("i: ", i, " atual: ", p_atual, " t: ",procRR[p_atual].duracao)

	procRR[p_atual].tRetorno = i+1 - procRR[p_atual].chegada # Cálculo do tempo de retorno

	if aux_tResposta[p_atual] == 0: # Cálculo do tempo de resposta
		procRR[p_atual].tResposta = i - procRR[p_atual].chegada
		aux_tResposta[p_atual] = 1

	# Cálculo do tempo de espera
	list(map(lambda p: calcula_tEspera(p, i) if p is not procRR[p_atual] and p.duracao != 0 else p.tEspera, procRR))

	exec += 1
	if exec == quantum or procRR[p_atual].duracao == 0: # Se o processo já executou por um quantum ou já terminou
		if p_atual == len(procRR)-1:
			p_atual = 0
		else: p_atual += 1
		exec = 0

mRetorno = sum(list(map(lambda p: p.tRetorno, procRR)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procRR)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procRR)))/numProcessos

print(f"RR {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procRR