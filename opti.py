from gurobipy import Model, GRB
# Intente seguir el orden y el nombre de las variables escritas en el modelo
#Intenten ser ordenado y explicitos en lo que hacen, para que los demas entiendan.

# Definicion conjuntos
C = ['cong1','cong2','cong3']
I = ['aditivo1','aditivo2','aditivo3','aditivo4']
T = [str(i) for i in range(1,366)] #va desde 1 a 365

#valores parametros
vu = 7 #vida util orujo 7 dias
Q = 30 #capacidad reactor m3
Co = 5 #costo orujo por kg
Ca = 3 #costo agua por litro -> Invenatdo
Cl = 3 #costo electricidad por kw -> Inventado
P = 1000 #precio agente reductor por kg -> Inventado
D = 100 #demanda -> Inventado

#cantidad agente reductor que se obtiene por kg con aditivo i, g/kg
alpha = {'aditivo1':22, 'aditivo2':106, 'aditivo3': 85, 'aditivo4':101}
#tiempo del ciclo aditivo i, dias
betha = {'aditivo1':7, 'aditivo2':3, 'aditivo3': 2, 'aditivo4':2}
#precio aditivo i por kg
gama = {'aditivo1':984, 'aditivo2':966, 'aditivo3': 958, 'aditivo4':1655}
#proporcion masica de aditivo requerida segun cantidad de orujo, kg
delta = {'aditivo1':0.05, 'aditivo2':0.05, 'aditivo3': 0.05, 'aditivo4':1}
#capacidad congelador c, lts
cc = {'cong1':300, 'cong2':396, 'cong3':490}
#consumo energetico congelador, KW/h
epsilon = {'cong1':420, 'cong2':528, 'cong3':624}

#creamos modelo
m = Model('Produccion de agente reductor')

#crean y rellenan varibles de desicion
# deben seguir el orden de los indices propuesto en el modelo
x = m.addVars(T,I,vtype = GRB.CONTINUOUS,name = 'orujo_fresco')
y = m.addVars(T,I,C, vtype = GRB.CONTINUOUS,name = 'orujo_congelado')
j = m.addVars(T, vtype=GRB.CONTINUOUS, name = 'compra')
z = m.addVars(T,C,vtype=GRB.CONTINUOUS, name = 'congelar')
b = m.addVars(T,I,vtype = GRB.BINARY, name='usar_ad')

#Variables auxiliares, no supe como se definian asi que las defini como variables.
IF = m.addVars(T,vtype=GRB.CONTINUOUS,name='almacen')
IC = m.addVars(T,C,vtype=GRB.CONTINUOUS,name = 'almacen_cong')
a = m.addVars(T,vtype=GRB.BINARY,name='termino')
w = m.addVars(C,T,vtype=GRB.BINARY,name='usando_cong')

# se debe actualizar el modelo luego de agregar variables
m.update()

#Ahora van las restricciones
#Restricción disponibilidad de materia fresca
for t in T:
    for i in I:
        m.addConstr(x[t, i] <= IF[t], "disponibilidadmateriafresca_{}_{}".format(t, i))

#Restricción disponibilidad de materia prima congelada
for t in T:
    for i in I:
        for c in C:
            m.addConstr(y[t, i, c] <= IC[t, c], "disponibilidadmateriaprimacongelada_{}_{}_{}".format(t, i, c))

#Restricción inventario orujo congelado
for t in T:
    for c in C:
        if t == T[0]:
            m.addConstr(IC[t, c] == z[t, c], "inventarioinicialorujocongelado_{}_{}".format(t, c))
            for i in I:
                m.addConstr(y[t, i, c] == 0, "yinicial_{}_{}_{}".format(t, i, c))
        else:
            cantidad = 0
            for i in I:
                cantidad += y[t, i, c]
            m.addConstr(IC[t, c] == IC[T[T.index(t) - 1], c] + z[t, c] - cantidad, "inventarioorujocongelado_{}_{}".format(t, c))

#Restricción capacidad del congelador
for t in T:
    for c in C:
        m.addConstr(IC[t, c] <= cc[c], "capacidadcongelador_{}_{}".format(t, c))

#Restricción inventario orujo fresco
for t in T:
    cantidad_f = 0
    for i in I:
        cantidad_f += x[t, i]
    cantidad_c = 0
    for c in C:
        cantidad_c += z[t, c]
    if t == T[0]:
        m.addConstr(IF[t] == j[t] - cantidad_f - cantidad_c , "inventarioinicialorujofresco_{}".format(t))
        
    else:
        m.addConstr(IF[T[T.index(t) - 1]] + j[t] == IF[t] + cantidad_f + cantidad_c, "inventarioorujofresco_{}".format(t))

#Restricción materia prima que se congela (vida útil)

#Restricción cantidad de producto no debe ser mayor a la demanda, para asegurar su venta
resultado = 0
for t in T:
    for c in C:
        for i in I:
            resultado += (alpha[i] * (x[t, i] + y[t, i, c]))
m.addConstr(resultado <= D , "restricciondemanda")

#Restricción capacidad del reactor considerando masa de aditivos
for t in T:
    for c in C:
        for i in I:
            m.addConstr(((1 + delta[i]) * (x[t, i] + y[t, i, c])) <= 0.8 * Q, "capacidadreactor_{}_{}_{}".format(t, i, c))
                        
      
            
