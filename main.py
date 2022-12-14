import sys
from copy import deepcopy
from random import choice

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
	if p.chegada <= i: # Se o processo já chegou
		p.tEspera += 1

def calcula_tempos(procTipo, pAtual, i, list_aux_tResposta):
	
	# CÁLCULO DO TEMPO DE RETORNO
	# A cada iteração atualiza o valor do processo em execução.
	# O último valor inserido será o correto.
	procTipo[pAtual].tRetorno = i+1 - procTipo[pAtual].chegada

	# CÁLCULO DO TEMPO DE RESPOSTA
	# O cálculo é feito logo que um processo começa a executar
	# a lista auxiliar serve para indicar quando o cálculo
	# já foi feito para um processo.
	if list_aux_tResposta[pAtual] == 0:
		procTipo[pAtual].tResposta = i - procTipo[pAtual].chegada
		list_aux_tResposta[pAtual] = 1

	# CÁLCULO DO TEMPO DE ESPERA
	# A cada iteração os valores do tempo de espera de todos os
	# processos são calculados. Para cada processo, verifica-se
	# se não é o processo em execução e se ainda precisa ser
	# executado para que então possa ser aplicada a função
	# calcula_tEspera. Caso não passe nas verificações, nada é
	# feito
	list(map(lambda p: calcula_tEspera(p, i) if p is not procTipo[pAtual] and p.duracao != 0 else p.tEspera, procTipo))

processos = organiza_processos()
numProcessos = len(processos)

tempo_total = 0

for index, processo in enumerate(processos):
    if index == 0:
        tempo_total = processo.duracao
        continue

	# Se o tempo de chegada de um processo for superior a soma dos tempos de execução
	# dos processos que entraram no sistema até então, significa que o processador
	# terá tempo ocioso que deve ser considerado no tempo total necessário para que
	# todos os processos executem 
    if processo.chegada > tempo_total:
		# Incrementa-se ao tempo total o tempo de ociosidade + o tempo de duração do processo
        tempo_total += (processo.chegada - tempo_total-1) +  processo.duracao
    else:
        tempo_total += processo.duracao

# ---------------------------------------PRIORIDADES DINÂMICAS--------------------------------------------
def define_prioridades(listaProcessos):
	lista = []

	# A prioridade padrão é definida pela quantidade de processos + 1

	# No entanto, a fim de obrigar que um processo só tenha uma prioridade
	# suficientemente grande para ser escolhido apenas a partir do momento
	# em que ele chegou no sistema, o valor padrão de prioridade dele é subtraído
	# do seu tempo de chegada no sistema
	for p in listaProcessos:
		lista.append(len(listaProcessos)+1 - p.chegada)
	return lista

def atualiza_prioridadesPRI(lista, indice, parada):
	for index, value in enumerate(lista):
		if lista[index] != parada: # Se o processo ainda não tiver terminado sua execução
			if index == indice:
				# A prioridade do processo que acabou de executar é reduzida
				lista[index] -= 1
			else:
				# As prioridades dos processos que não executaram são aumentadas
				lista[index] += 1

procPRI = deepcopy(processos)

# Processo de remoção do "deslocamento" dos processos
temp = procPRI[0].chegada
for p in procPRI:
	p.chegada -= temp

p_atual = 0 # índice do processo atual em análise
aux_tResposta = [0]*numProcessos # Lista auxiliar que indica se o tempo de resposta
								 # de um processo já foi calculado ou não

prioridades = define_prioridades(procPRI)

# O número que indica que um processo já não deve mais ser processado é aquele
# resultante da subtração do menor valor de prioridade gerado - 1
ind_parada = min(prioridades)-1

for i in range(tempo_total):

	maior = max(prioridades) # Escolha da maior prioridade
	p_atual = prioridades.index(maior) # Descoberta do índice do processo que possui maior prioridade

	if i >= procPRI[p_atual].chegada: # Se o processo escolhido já estiver no sistema
		procPRI[p_atual].duracao -= 1
	else: # Só se chega nesse ponto em caso de ociosidade do processador
		prioridades[p_atual] += 1 # Incrementa-se a prioridade
		continue # E deixa-se o tempo "passar"

	calcula_tempos(procPRI, p_atual, i, aux_tResposta)
	
	# Se o processo já terminou sua execução, um número de parada
	# é atribuído a sua respectiva prioridade para que ele não
	# seja mais considerado
	if procPRI[p_atual].duracao == 0:
		prioridades[p_atual] = ind_parada

	atualiza_prioridadesPRI(prioridades, p_atual, ind_parada)

mRetorno = sum(list(map(lambda p: p.tRetorno, procPRI)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procPRI)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procPRI)))/numProcessos

print(f"PRI {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procPRI, prioridades, ind_parada

# ---------------------------------------------LOTERIA----------------------------------------------------

def adiciona_elegiveis_LOT(proc, lista, tempo, cont):
	for i in range(cont, len(proc)):
		if proc[i].chegada == tempo: # Se o processo chegou
			lista.append(i) # Adiciona índice na lista de elegíveis para processamento
			cont += 1 # Conta quantos processos já foram adicionados
		else: break

	if len(lista) == 0: lista.append(-1) # Sinalização de que o processador está ocioso

	return cont

procLOT = deepcopy(processos)

# Processo de remoção do "deslocamento" dos processos
temp = procLOT[0].chegada
for p in procLOT:
	p.chegada -= temp

aux_tResposta = [0]*numProcessos # Lista auxiliar que indica se o tempo de resposta
								 # de um processo já foi calculado
lista_ind_processos = []
conta_proc_add = 0 # Variável de auxílio para contabilizar quantos processos já entraram no sistema

for i in range(tempo_total):
	# Atualiza lista de índices de processos elegíveis e retorna a quantidade de processos
	# já adicionados ao sistema
	conta_proc_add = adiciona_elegiveis_LOT(procLOT, lista_ind_processos, i, conta_proc_add)

	# Escolha aleatória a partir de uma lista de índices de processos elegíveis
	p_atual = choice(lista_ind_processos)

	if p_atual == -1: # Se o processador está ocioso
		lista_ind_processos.remove(-1)
		continue # Deixa o "tempo passar"

	procLOT[p_atual].duracao -= 1

	# Remove o processo da lista de processos que podem ser escolhidos para serem processados
	if procLOT[p_atual].duracao == 0:
		lista_ind_processos.remove(p_atual)

	calcula_tempos(procLOT, p_atual, i, aux_tResposta)

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

		p_atual = (p_atual + 1)%len(procRR) # De forma circular, escolhe-se o próximo processo na lista
		ind_prox_proc = p_atual

		# Verificação se ainda é inelegível
		inelegivel = procRR[p_atual].duracao == 0 or procRR[p_atual].chegada > i 
		cont += 1

	return ind_prox_proc

procRR = deepcopy(processos)

# Processo de remoção do "deslocamento" dos processos
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

	procRR[p_atual].duracao -= 1

	calcula_tempos(procRR, p_atual, i, aux_tResposta)

	exec += 1
	# Se o processo já executou por um quantum ou já terminou
	if exec == quantum or procRR[p_atual].duracao == 0:
		p_atual = (p_atual + 1)%len(procRR) # De forma circular, escolhe-se o próximo processo na lista
		exec = 0

mRetorno = sum(list(map(lambda p: p.tRetorno, procRR)))/numProcessos
mResposta = sum(list(map(lambda p: p.tResposta, procRR)))/numProcessos
mEspera = sum(list(map(lambda p: p.tEspera, procRR)))/numProcessos

print(f"RR {mRetorno:.2f} {mResposta:.2f} {mEspera:.2f}")

del procRR, temp, p_atual, quantum, exec, aux_tResposta, mRetorno, mResposta, mEspera
del processos, numProcessos, tempo_total