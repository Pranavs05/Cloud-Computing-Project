import networkx.algorithms.approximation
import networkx as nx
import numpy as np
from numpy import random
from func_timeout import func_timeout, FunctionTimedOut
import time
import timeout_decorator
import sys
import matplotlib.pyplot as plt


def plot_results(sol):
    for i in range(len(sol)):
        plt.plot(sol[i], label='Gene'+str(i+1))
    plt.ylabel('Fitness Scores of Networks')
    plt.xlabel('Genetic Algorithm iteration')
    plt.legend()
    plt.savefig('Plot.png')
    plt.show()

def crossover (G1,G2):

    Gc1 = nx.Graph()
    Gc2 = nx.Graph()
    t1 = list(G1.edges())
    t2 = list(G2.edges())
    x = random.randint(0,len(t1)+1)
    if x == len(t1)+1:
        x = len(t1)
    for j in range(x):

        Gc1.add_edge(*t1[j],weight = G1.get_edge_data(*t1[j])['weight'])    

    z = x
    for k in range(len(t2)-1,x,-1):
            if z == len(t1):
                break
            else:
                if t2[k] not in t1  and  G2.get_edge_data(*t2[k])!= '': 
                    Gc1.add_edge(*t2[k], weight = G2.get_edge_data(*t2[k])['weight'])
            z=z+1
    x = random.randint(0,len(t2)+1)
    if x == len(t2)+1:
        x = len(t2)
    for j in range(x):
        Gc2.add_edge(*t2[j],weight = G2.get_edge_data(*t2[j])['weight'])

    z=x
    for k in range(len(t1)-1,x,-1):
            if z == len(t1):
                break
            else:
                if t1[k] not in t2 and  G1.get_edge_data(*t1[k])!='': 
                    Gc2.add_edge(*t1[k], weight = G1.get_edge_data(*t1[k])['weight'])
            z=z+1

    
    return Gc1, Gc2





def add_new_node(G):

    t = list(G.nodes())
    for item in t:
        item = int(item)
    maxi = int(max(t))
    maxi += 1
    td = np.random.randint(0, len(t))
    G.add_edge(str(maxi), t[td])
    return G


def max_degree(G):
    mdegree =0
   
    for j in list(G.nodes()):
            if G.degree(j)>mdegree:
                mdegree=G.degree(j)
           #Degree of a node 
    return mdegree


def avg_degree(G):
    sum1=0
    if len(list(G.nodes()))>0:
        for j in list(G.nodes()):
                sum1+=G.degree(j)
        avgdegree= sum1/len(list(G.nodes()))
        return avgdegree
    else:
        return 0
    
def normalize(scoret):
    tmax = np.max(scoret, axis = 0)
    score = []
    for i in scoret:
        score.append((i[0])/((i[1])+(i[2])+(i[3])+(i[4])))
        #score.append((i[0]/tmax[0])/((i[1]/tmax[1])+(i[2]/tmax[2])+(i[3]/tmax[3])+(i[4]/tmax[4])))
    return score

def mutation(G):
    t = list(G.nodes())
    td1 = np.random.randint(0, len(t))
    td2 = np.random.randint(0, len(t))
    l1 = list(G.edges(t[td1]))
    l2 = list(G.edges(t[td2]))
    for item in l1:
        x = np.random.randint(0, 2)
        if x % 2 == 0:
            w =  G.get_edge_data(item[0], item[1])['weight']
            G.remove_edge(item[0],item[1])
            G.add_edge(t[td2],item[1], weight = w)
    for item in l2:
        x = np.random.randint(0, 2)
        if x % 2 == 0:
            if  G.has_edge(item[0], item[1])==True:
                w =  G.get_edge_data(item[0], item[1])['weight']
                G.remove_edge(item[0],item[1])
                G.add_edge(t[td1],item[1], weight = w)

    return G

@timeout_decorator.timeout(5, timeout_exception=FunctionTimedOut)
def min_cut_edge(G):
    return len(nx.minimum_edge_cut(G))


@timeout_decorator.timeout(5, timeout_exception=FunctionTimedOut)
def time_delay(G):
         T = nx.algorithms.approximation.steinertree.metric_closure(G)
         return nx.Graph.size(T)


@timeout_decorator.timeout(5, timeout_exception=FunctionTimedOut)
def get_size(G):
    return G.size(weight='weight')



    


def fitness(x):
    if (max_degree(x)+avg_degree(x))!=0:
        try:
            f = min_cut_edge(x)
        except FunctionTimedOut:
            f = 20
        try:
            g = time_delay(x)
        except FunctionTimedOut:
            g = 15


        s=(f/(max_degree(x)+avg_degree(x))+g)
        return ([f,g,max_degree(x),avg_degree(x),x.size(weight='weight')])#+min_cut_edge(x,) 
    else:
        return 1 

mutation_rate = 5
g = sys.argv[1]
n = 9 #number of genes
niter = 10
child_option = 1 #whether to mutate children if disconnected or wether to simply drop them
genes = []
f = open(g,"r")
G = nx.Graph()
i =  0
for line in f:
    i = i+1
    if i > 4:
        line = line.replace("\n","")
        t = line.split("\t")
        if t[0] != t[1]:
            G.add_edge(t[0],t[1],weight = 1)

#generate initial population

genes.append(G)
t = mutation(G)
for i in range(n):
    while(nx.is_connected(t)==False):
        t = mutation(t)
    genes.append(t)

n = n+1
score = []
scoret = []
log = []
children_log = []
for i in range(n):
    children_log.append([])
for i in range(n):
    scoret.append(fitness(genes[i]))
score = normalize(scoret)
for q in range(niter):
    children = []
    children_score = []

    print('Entered iteration: {} of {}'.format(q+1, n))
    for i in range(int(n/2)):
        x = np.random.choice(n, 2, p=score/np.sum(score))
        a, b = crossover(genes[x[0]],genes[x[1]])
        if child_option == 0:
             if nx.is_empty(a)==False and nx.is_empty(b)==False:
                while(nx.is_connected(a)==False):
                    a = mutation(a)
                while(nx.is_connected(b)==False):
                    b = mutation(b)
                children.append(a)
                children.append(b)
                children_score.append(fitness(a))
                children_score.append(fitness(b))
        else:
            if nx.is_empty(a)==False and nx.is_empty(b)==False:
                if nx.is_connected(a)==True:
                    children.append(a)
                    children_score.append(fitness(a))
                if nx.is_connected(b)==True:
                    children.append(b)
                    children_score.append(fitness(b))
            
    genes.extend(children)
    scoret.extend(children_score)
    score = normalize(scoret)
    genes = [x for _,x in sorted(zip(score,genes), key = lambda x: x[0], reverse = True)][:n]
    scoret = [x for _,x in sorted(zip(score,scoret), key = lambda x: x[0], reverse = True)][:n]
    score = sorted(score , reverse = True)[:n]
    for i in range(n):
        x = np.random.choice(100)
        if x < mutation_rate:
            t = mutation(G)

            while(nx.is_connected(t)==False):
                t = mutation(t)            
            genes[i] = t
            scoret[i] = fitness(genes[i])
            score = normalize(scoret)
    for i in range(n):
        children_log[i].append(score[i])
    print(score)
print(score)
print(genes)
plot_results(children_log)