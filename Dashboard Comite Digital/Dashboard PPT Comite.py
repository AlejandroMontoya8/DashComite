#!/usr/bin/env python
# coding: utf-8

# In[37]:


import pandas as pd
import os
import numpy as np


# In[38]:


resumen_total = pd.DataFrame(columns=["ORDER_NO","ORDER_DATE","ENTRY_TYPE","LEVEL_OF_SERVICE","STATUS_NAME","EXTN_ORG_REQ_SHIP_DATE","EXTN_ET_FULFILMENT","SHIPNODE_KEY"])
for the_file in os.listdir(r"C:\Users\luis.montoya\Downloads\Resumen OMS Q3 2021"):
    archivo_subida = os.path.join(r"C:\Users\luis.montoya\Downloads\Resumen OMS Q3 2021",the_file)             ###Importación del archivo de resumen
    resumen_parcial=pd.read_csv(archivo_subida,sep=",")
    columnas_resumen= ["RN","ORDER_HEADER_KEY","ENTRY_TYPE","ORDER_NO","DOCUMENT_TYPE","ORDER_DATE","ORDER_TYPE","ENTRY_TYPE2","LEVEL_OF_SERVICE","CUSTOMER_PHONE_NO","EXTN_RUN_RUT_NIT","ORIGINAL_TOTAL_AMOUNT","ENTERPRISE_KEY","PAYMENT_TYPE","STATUS_NAME","EXTN_ORG_REQ_SHIP_DATE","STATUS_DATE","EXTN_ET_FULFILMENT","SHIPNODE_KEY","BLANCOI","BLANCOII","BLANCOIII","BLANCOIV"]  
    resumen_parcial.columns=columnas_resumen
    resumen_parcial=resumen_parcial.drop(0,axis=0)
    print(the_file)
    resumen_parcial=resumen_parcial[["ORDER_NO","ORDER_DATE","ENTRY_TYPE","ORDER_TYPE","LEVEL_OF_SERVICE","EXTN_RUN_RUT_NIT","ORIGINAL_TOTAL_AMOUNT","STATUS_NAME","EXTN_ORG_REQ_SHIP_DATE","EXTN_ET_FULFILMENT","SHIPNODE_KEY"]]
    resumen_total = pd.concat([resumen_total,resumen_parcial],axis=0)


# In[39]:


from datetime import date     ###Ajuste fecha order date, paso a fecha hora colombia
import datetime
resumen_total["ORDER_DATE"] = pd.to_datetime(resumen_total["ORDER_DATE"],format="%Y-%m-%d %H:%M:%S")
order_date_inicial = resumen_total["ORDER_DATE"]
ORDER_DATE_COL =[]
Dia_Orden =[]
Mes_Orden = []
Semana_Orden = []
DiaSemana_Orden =[]
Hora_Orden =[]
Anio_Orden = []
for fecha in order_date_inicial:
    resta = fecha -datetime.timedelta(hours=5)
    ORDER_DATE_COL.append(resta)
    Dia_Orden.append(resta.day)
    Mes_Orden.append(resta.month)
    Semana_Orden.append(resta.isocalendar()[1])
    DiaSemana_Orden.append(resta.isocalendar()[2])
    Hora_Orden.append(resta.hour)
    Anio_Orden.append(resta.year)


resumen_total["ORDER_DATE_COL"] = ORDER_DATE_COL
resumen_total["Dia_Orden"] = Dia_Orden
resumen_total["Mes_Orden"] = Mes_Orden
resumen_total["Semana_Orden"] = Semana_Orden
resumen_total["DiaSemana_Orden"] = DiaSemana_Orden
resumen_total["Hora_Orden"] = Hora_Orden
resumen_total["Anio_Orden"] = Anio_Orden


meses = [1,2,3,4,5,6,7,8,9,10]
#semanas = [34,35,36,37,38,39,40,41]

resumen_total = resumen_total[resumen_total.Mes_Orden.isin(meses)]
#resumen_total = resumen_total[resumen_total.Semana_Orden.isin(semanas)]


# In[40]:


venta = resumen_total["ORIGINAL_TOTAL_AMOUNT"]
venta_nuevo = []

for element in venta:
    element = element[0:element.find(".")]
    venta_nuevo.append(element)

resumen_total["Valor_Venta"] = venta_nuevo

resumen_total["Valor_Venta"] = pd.to_numeric(resumen_total["Valor_Venta"],downcast="integer")

venta_ret_ecomm = pd.pivot_table(resumen_total,index=["ENTRY_TYPE","Mes_Orden"],columns=["STATUS_NAME"],values=["Valor_Venta"],aggfunc=np.sum,fill_value =0)
venta_ret_ecomm=venta_ret_ecomm.loc["CustomerOnWeb"]
venta_ret_ecomm=venta_ret_ecomm[[("Valor_Venta","Customer Picked Up"),("Valor_Venta","Delivered To Customer"),("Valor_Venta","In Transit to Customer")]]
venta_ret_ecomm=venta_ret_ecomm.reset_index()
venta_ret_ecomm.columns=["Mes_Orden","Customer Picked Up","Delivered To Customer","In Transit to Customer"]

venta_ret_ecomm["Venta"] = venta_ret_ecomm["Customer Picked Up"] + venta_ret_ecomm["Delivered To Customer"] +venta_ret_ecomm["In Transit to Customer"]
venta_ret_ecomm["Participacion_ret"] = venta_ret_ecomm["Customer Picked Up"]/venta_ret_ecomm["Venta"]

venta_ret_ecomm["Venta"] = np.round(venta_ret_ecomm["Venta"]/1000000,decimals =3)
venta_ret_ecomm["Participacion_ret"] = np.round(venta_ret_ecomm["Participacion_ret"]*100,decimals=1)
venta_ret_ecomm["Customer Picked Up"] = np.round(venta_ret_ecomm["Customer Picked Up"]/1000000,decimals=3)

ticket_ret_ecomm = pd.pivot_table(resumen_total,index=["ENTRY_TYPE","Mes_Orden"],columns=["STATUS_NAME"],values =["Valor_Venta"],aggfunc =np.mean,fill_value=0)
ticket_ret_ecomm = ticket_ret_ecomm.loc["CustomerOnWeb"]
ticket_ret_ecomm = ticket_ret_ecomm[[("Valor_Venta","Customer Picked Up"),("Valor_Venta","Delivered To Customer")]]
ticket_ret_ecomm = ticket_ret_ecomm.reset_index()
ticket_ret_ecomm.columns=["Mes_Orden","Customer Picked Up","Delivered To Customer"]

ticket_ret_ecomm["Customer Picked Up"] = np.round(ticket_ret_ecomm["Customer Picked Up"]/1000,decimals = 3)
ticket_ret_ecomm["Delivered To Customer"] = np.round(ticket_ret_ecomm["Delivered To Customer"]/1000,decimals = 3)

ordenes_ret = pd.pivot_table(resumen_total,index=["ENTRY_TYPE","Mes_Orden"],columns=["STATUS_NAME"],values=["ORDER_NO"],aggfunc ="count",fill_value=0)
ordenes_ret = ordenes_ret.loc["CustomerOnWeb"]
ordenes_ret = ordenes_ret[[("ORDER_NO","Customer Picked Up")]]
ordenes_ret = ordenes_ret.reset_index()
ordenes_ret.columns = ["Mes_Orden","Customer Picked Up"]


# In[41]:


resumen_total_ciudad = resumen_total[~resumen_total.SHIPNODE_KEY.isnull()] ###eliminación registros sin sucursal asociada
Sucursal_sucia = resumen_total_ciudad["SHIPNODE_KEY"]
nuevos_cod = []
for cod_id in Sucursal_sucia:                    ###Eliminación del prefijo COCV_
    cod_id = str(cod_id)
    cod_id = cod_id[cod_id.find("_")+1:40]
    nuevos_cod.append(cod_id)

resumen_total_ciudad["SHIPNODE_KEY2"] = nuevos_cod

directorio = pd.read_excel(r"C:\Users\luis.montoya\Downloads\DirectorioCv.xlsx")  ###Importación directorio CV
tiendas = directorio["COD. SUC"] 
sucursal = []
for suc in tiendas:
    suc = str(suc)
    sucursal.append(suc)

directorio["COD. SUC"] = sucursal
resumen_total_ciudad = pd.merge(resumen_total_ciudad ,directorio,left_on="SHIPNODE_KEY2",right_on="COD. SUC",how="left")

resumen_total_ciudad = resumen_total_ciudad[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',   ###Cruce directorio para traer la ciudad
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden','Semana_Orden','DiaSemana_Orden',"Hora_Orden",
       'SHIPNODE_KEY2', 'COD. SUC','CIUDAD / MUNICIPIO','GERENTE DE ZONA', 'Localidad']]

ciudades = resumen_total_ciudad["CIUDAD / MUNICIPIO"]

ciudades_b = []                                       ###Categorización ciudades
for registro in ciudades: 
    if registro == "Bogotá":
        city = "Bogotá"
    elif (registro =="Medellín") | (registro == "Medellin"):
        city= "Medellín"
    elif registro == "Cali":
        city = "Cali"
    elif registro == "Barranquilla":
        city = "Barranquilla"
    else: city = "Otras ciudades"
    ciudades_b.append(city)
    
resumen_total_ciudad["CiudadB"] = ciudades_b

resumen_total_ciudad = resumen_total_ciudad.loc[resumen_total_ciudad["ORDER_NO"].str.contains("^CO[a-z]*")]

resumen_total_ciudad = resumen_total_ciudad[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden','DiaSemana_Orden',"Hora_Orden", 'SHIPNODE_KEY2', 'COD. SUC', 'CIUDAD / MUNICIPIO', 'GERENTE DE ZONA', 
      'Localidad', 'CiudadB']]

resumen_total_ciudad.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden','DiaSemana_Orden',"Hora_Orden", 'SHIPNODE_KEY2', 'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 
       'Localidad', 'CiudadB']

resumen_total_ciudad = resumen_total_ciudad[~resumen_total_ciudad.CIUDAD_MUNICIPIO.isnull()]

estado2 = []
estados_iniciales = resumen_total_ciudad["STATUS_NAME"]
for estado in estados_iniciales:                                   ###Categorización cancelados y devoluciones
    if estado == "Cancelled":
        nuevo_estado = "Cancelado"
    elif (estado == "Return Received") | (estado == "Return Created") | (estado == "Delivery Rejected"):
        nuevo_estado = "Devolucion"
    else: nuevo_estado = "Orden"
    estado2.append(nuevo_estado)

resumen_total_ciudad["estado2"] = estado2 


# In[42]:


base_cancelados_call = resumen_total_ciudad[(resumen_total_ciudad["estado2"]=="Cancelado") & (resumen_total_ciudad.ORDER_NO.str.contains("COCC"))]
base_cancelados_ecomm = resumen_total_ciudad[(resumen_total_ciudad["estado2"]=="Cancelado") & (resumen_total_ciudad.ORDER_NO.str.contains("CO1"))]

cancelados_call = pd.read_excel(r"C:\Users\luis.montoya\OneDrive - Grupo Socofar\Dashboard OMS\Call center\Libros Cancelados\Libro cancelados - Call center.xlsx",sheet_name = 'Libro de Cancelados "Otros"')
cancelados_ecomm = pd.read_excel(r"C:\Users\luis.montoya\OneDrive - Grupo Socofar\Dashboard OMS\Call center\Libros Cancelados\Libro cancelados - E-commerce.xlsx",sheet_name = 'Libro de Cancelados "Otros"')
cancelados_call = cancelados_call[['ORDER_NO','Macrotipologia', 'RESPONSABLE']]
cancelados_ecomm = cancelados_ecomm[['ORDER_NO','Macrotipologia','RESPONSABLE']]
#cancelados_call = cancelados_call[~cancelados_call.Macrotipologia.isnull()]
#cancelados_ecomm = cancelados_ecomm[~cancelados_ecomm.Macrotipologia.isnull()]

base_cancelados_call = pd.merge(base_cancelados_call,cancelados_call,left_on = "ORDER_NO",right_on = "ORDER_NO",how = "left")
base_cancelados_ecomm = pd.merge(base_cancelados_ecomm,cancelados_ecomm,left_on ="ORDER_NO",right_on="ORDER_NO",how = "left")
#base_cancelados_call = base_cancelados_call.drop_duplicates(subset = ["ORDER_NO","Macrotipologia"])
#base_cancelados_ecomm = base_cancelados_ecomm.drop_duplicates(subset = ["ORDER_NO","Macrotipologia"])

base_cancelados_total = pd.concat([base_cancelados_call,base_cancelados_ecomm],axis = 0)


# In[43]:


tabla_cancelados = pd.pivot_table(base_cancelados_total,index =["RESPONSABLE"],columns = ["Mes_Orden"],values =["ORDER_NO"],aggfunc = "count",fill_value = 0)
tabla_cancelados = tabla_cancelados.reset_index()

columnas_cancelados = []
columnas_cancelados.append("RESPONSABLE")

for elemento in meses:
    columnas_cancelados.append(str(elemento))
    
tabla_cancelados.columns = columnas_cancelados

total_ordenes = pd.pivot_table(resumen_total_ciudad,index =["Mes_Orden"],values = ["ORDER_NO"],aggfunc = "count")
total_ordenes = total_ordenes.reset_index()
total_ordenes.columns = ["Mes_Orden","Cantidad_Ordenes"]

T = np.empty(len(meses))
z =[None]*len(T)
j = 0

for elemento in meses:
    elemento2 = str(elemento)
    vector_porcentajes = np.round((tabla_cancelados[elemento2]/total_ordenes["Cantidad_Ordenes"])*100,decimals = 3)
    z[j] =vector_porcentajes
    j = j + 1

z = np.transpose(z)
porcentajes_ = pd.DataFrame(z,columns = meses)

index_ultimo = len(porcentajes_) - 1
porcentajes_ = porcentajes_.drop(index_ultimo)
porcentajes_.index = tabla_cancelados["RESPONSABLE"]
porcentajes_ = porcentajes_.reset_index()
porcentajes_.columns = tabla_cancelados.columns


# ### Tablas Dinámicas Cancelados, Devoluciones y participación por ciudad

# In[44]:


cancelados_dev_gral = pd.pivot_table(resumen_total_ciudad,index =["Mes_Orden"],columns = ["ENTRY_TYPE","estado2"],values =["ORDER_NO"],aggfunc = "count")
cancelados_dev_gral[("ORDER_NO","Call Center","Porc Cancelados")] = cancelados_dev_gral[("ORDER_NO","Call Center","Cancelado")] / (cancelados_dev_gral[("ORDER_NO","Call Center","Cancelado")] + cancelados_dev_gral[("ORDER_NO","Call Center","Devolucion")] + cancelados_dev_gral[("ORDER_NO","Call Center","Orden")] ) 
cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Porc Cancelados")] = cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Cancelado")] / (cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Cancelado")] + cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Devolucion")] + cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Orden")] )
cancelados_dev_gral[("ORDER_NO","Call Center","Porc Devoluciones")] = cancelados_dev_gral[("ORDER_NO","Call Center","Devolucion")] / (cancelados_dev_gral[("ORDER_NO","Call Center","Cancelado")] + cancelados_dev_gral[("ORDER_NO","Call Center","Devolucion")] + cancelados_dev_gral[("ORDER_NO","Call Center","Orden")] )
cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Porc Devoluciones")] = cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Devolucion")] / (cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Cancelado")] + cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Devolucion")] + cancelados_dev_gral[("ORDER_NO","CustomerOnWeb","Orden")] )
cancelados_dev_gral = cancelados_dev_gral.reset_index()
cancelados_dev_gral.columns = ["Mes_Orden","Call Cancelado","Call Devolucion","Call Orden","Ecomm Cancelado","Ecomm Devolucion","Ecomm Orden","Call Porc Cancelados","Ecomm Porc Cancelados","Call Porc Dev","Ecomm Porc Dev"]

cancelados_dev_ciudad = pd.pivot_table(resumen_total_ciudad,index = ["CiudadB","Mes_Orden"],columns =["estado2"],values =["ORDER_NO"], aggfunc ="count")
cancelados_dev_ciudad[("ORDER_NO","Porc Cancelados")] = cancelados_dev_ciudad[("ORDER_NO","Cancelado")] / (cancelados_dev_ciudad[("ORDER_NO","Cancelado")] + cancelados_dev_ciudad[("ORDER_NO","Devolucion")] + cancelados_dev_ciudad[("ORDER_NO","Orden")] )
cancelados_dev_ciudad[("ORDER_NO","Porc Devolucion")] = cancelados_dev_ciudad[("ORDER_NO","Devolucion")] / (cancelados_dev_ciudad[("ORDER_NO","Cancelado")] + cancelados_dev_ciudad[("ORDER_NO","Devolucion")] + cancelados_dev_ciudad[("ORDER_NO","Orden")] )
cancelados_dev_ciudad=cancelados_dev_ciudad.reset_index()
cancelados_dev_ciudad.columns = ["Ciudad","Mes_Orden","Cancelados","Devoluciones","Orden","Porc Cancelados","Porc Devoluciones"]

cancelados_dev_gral["Call Porc Cancelados"] = np.round(cancelados_dev_gral["Call Porc Cancelados"]*100,decimals = 1)
cancelados_dev_gral["Ecomm Porc Cancelados"] = np.round(cancelados_dev_gral["Ecomm Porc Cancelados"]*100,decimals = 1)
cancelados_dev_gral["Call Porc Dev"] = np.round(cancelados_dev_gral["Call Porc Dev"]*100,decimals = 1)
cancelados_dev_gral["Ecomm Porc Dev"] = np.round(cancelados_dev_gral["Ecomm Porc Dev"]*100,decimals = 1)

cancelados_dev_ciudad["Porc Cancelados"] = np.round(cancelados_dev_ciudad["Porc Cancelados"]*100,decimals =1)
cancelados_dev_ciudad["Porc Devoluciones"] = np.round(cancelados_dev_ciudad["Porc Devoluciones"]*100,decimals =1)

participacionxciudad = pd.pivot_table(resumen_total_ciudad,index = ["Mes_Orden"],columns = ["CiudadB"],values =["ORDER_NO"],aggfunc ="count")
participacionxciudad = participacionxciudad.reset_index()

participacionxciudad.columns = ["Mes_Orden","Barranquilla","Bogotá","Cali","Medellín","Otras ciudades"]
participacionxciudad["Prt Barranquilla"] = participacionxciudad["Barranquilla"] / (participacionxciudad["Barranquilla"] + participacionxciudad["Bogotá"] + participacionxciudad["Cali"] + participacionxciudad["Medellín"] + participacionxciudad["Otras ciudades"]  )
participacionxciudad["Prt Bogotá"] = participacionxciudad["Bogotá"] / (participacionxciudad["Barranquilla"] + participacionxciudad["Bogotá"] + participacionxciudad["Cali"] + participacionxciudad["Medellín"] + participacionxciudad["Otras ciudades"]  )
participacionxciudad["Prt Cali"] = participacionxciudad["Cali"] / (participacionxciudad["Barranquilla"] + participacionxciudad["Bogotá"] + participacionxciudad["Cali"] + participacionxciudad["Medellín"] + participacionxciudad["Otras ciudades"]  )
participacionxciudad["Prt Medellín"] = participacionxciudad["Medellín"] / (participacionxciudad["Barranquilla"] + participacionxciudad["Bogotá"] + participacionxciudad["Cali"] + participacionxciudad["Medellín"] + participacionxciudad["Otras ciudades"]  )
participacionxciudad["Prt Otras ciudades"] = participacionxciudad["Otras ciudades"] / (participacionxciudad["Barranquilla"] + participacionxciudad["Bogotá"] + participacionxciudad["Cali"] + participacionxciudad["Medellín"] + participacionxciudad["Otras ciudades"]  )
participacionxciudad = participacionxciudad[["Mes_Orden","Prt Barranquilla","Prt Bogotá","Prt Cali","Prt Medellín","Prt Otras ciudades"]]

participacionxciudad["Prt Barranquilla"] = np.round(participacionxciudad["Prt Barranquilla"]*100,decimals =1)
participacionxciudad["Prt Bogotá"] = np.round(participacionxciudad["Prt Bogotá"]*100,decimals =1)
participacionxciudad["Prt Cali"] = np.round(participacionxciudad["Prt Cali"]*100,decimals =1)
participacionxciudad["Prt Medellín"] = np.round(participacionxciudad["Prt Medellín"]*100,decimals =1)
participacionxciudad["Prt Otras ciudades"] = np.round(participacionxciudad["Prt Otras ciudades"]*100,decimals =1)


# In[45]:


fmedica_total = pd.DataFrame(columns=["ORDER_NO","ORDER_HEADER_KEY","ORDER_DATE","DOCUMENT_TYPE","ENTRY_TYPE","PRESCRIPTION_NAME","ENTERPRISE_KEY"])
for the_file in os.listdir(r"C:\Users\luis.montoya\Downloads\F.Medica OMS"):
    
    archivo_subida = os.path.join(r"C:\Users\luis.montoya\Downloads\F.Medica OMS",the_file)
    fmedica_parcial = pd.read_csv(archivo_subida,sep=",")
    columnas_fmedica= ["RN","ORDER_NO","ORDER_HEADER_KEY","ORDER_DATE","DOCUMENT_TYPE","ENTRY_TYPE","PRESCRIPTION_NAME","ENTERPRISE_KEY","BLANCOI","BLANCOII","BLANCOIII"]  
    fmedica_parcial.columns=columnas_fmedica
    fmedica_parcial=fmedica_parcial.drop(0,axis=0)
    print(the_file)
    fmedica_parcial=fmedica_parcial[["ORDER_NO","ORDER_HEADER_KEY","ORDER_DATE","DOCUMENT_TYPE","ENTRY_TYPE","PRESCRIPTION_NAME","ENTERPRISE_KEY"]]
    fmedica_total = pd.concat([fmedica_total,fmedica_parcial],axis=0)


# In[46]:


resumen_total_ciudad = pd.merge(resumen_total_ciudad,fmedica_total,left_on="ORDER_NO",right_on="ORDER_NO",how ="left")

resumen_total_ciudad= resumen_total_ciudad[['ORDER_NO', 'ORDER_DATE_x', 'ENTRY_TYPE_x', 'LEVEL_OF_SERVICE',
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden','DiaSemana_Orden',"Hora_Orden", 'SHIPNODE_KEY2', 'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 
       'Localidad', 'CiudadB','estado2','PRESCRIPTION_NAME']]

resumen_total_ciudad.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden','DiaSemana_Orden',"Hora_Orden", 'SHIPNODE_KEY2', 'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 
       'Localidad', 'CiudadB','estado2','PRESCRIPTION_NAME']

resumen_total_ciudad =resumen_total_ciudad[resumen_total_ciudad.PRESCRIPTION_NAME.isnull()]

resumen_total_ciudad = resumen_total_ciudad[resumen_total_ciudad["EXTN_ET_FULFILMENT"]=="N"]


# In[47]:


um_total = pd.DataFrame(columns=['numorden', 'iniciado', 'asignado', 'llego_punto', 'salio_punto', 'llego_cliente', 'finalizado', 'distancia_km', 'Finalizado Fallido', 'Tipo Fallido', 'Valor Servicio', 'Proveedor', 'Estado UM', 'Mes','Dia'])
for the_file in os.listdir(r"C:\Users\luis.montoya\Downloads\UM Q3 21"):
    archivo_subida = os.path.join(r"C:\Users\luis.montoya\Downloads\UM Q3 21",the_file)   ###Importación de los archivos de última milla
    um_parcial = pd.read_excel(archivo_subida)
    print(the_file)
    um_total = pd.concat([um_total,um_parcial],axis=0)
    
um_total["distancia_km"] = pd.to_numeric(um_total["distancia_km"],downcast = "integer")


# In[48]:


um_total["iniciado"] = pd.to_datetime(um_total["iniciado"], format="%Y-%m-%d %H:%M:%S")
um_total["asignado"] = pd.to_datetime(um_total["asignado"], format="%Y-%m-%d %H:%M:%S")
um_total["salio_punto"] = pd.to_datetime(um_total["salio_punto"], format="%Y-%m-%d %H:%M:%S")
um_total["llego_punto"] = pd.to_datetime(um_total["llego_punto"], format="%Y-%m-%d %H:%M:%S")
um_total["llego_cliente"] = pd.to_datetime(um_total["llego_cliente"], format="%Y-%m-%d %H:%M:%S")
um_total["finalizado"] = pd.to_datetime(um_total["finalizado"], format="%Y-%m-%d %H:%M:%S")


orden_proveedor = um_total["numorden"]
nueva_orden = []
for orden in orden_proveedor:
    orden = str(orden)
    if "_" in orden:
        orden = orden[0:orden.find("_")]
        orden = orden.replace(" ","")
        nueva_orden.append(orden)
    else: 
        orden = orden
        nueva_orden.append(orden)
um_total["numorden2"] = nueva_orden

resumen_total_tiempos = resumen_total_ciudad[resumen_total_ciudad["STATUS_NAME"] == "Delivered To Customer"]

resumen_total_tiempos = pd.merge(resumen_total_tiempos,um_total,left_on="ORDER_NO",right_on="numorden2",how="left")
resumen_total_tiempos = resumen_total_tiempos[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'ORIGINAL_TOTAL_AMOUNT','STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden','DiaSemana_Orden',"Hora_Orden", 'SHIPNODE_KEY2', 'COD_SUC', 'CIUDAD_MUNICIPIO','GERENTE DE ZONA',
       'Localidad', 'CiudadB', 'numorden', 'iniciado', 'asignado',
       'llego_punto', 'salio_punto', 'llego_cliente',
       'distancia_km', 'Finalizado Fallido', 'Valor Servicio',
       'Proveedor', 'Estado UM', 'numorden2']]

df_tiempo_total = resumen_total_tiempos[(~resumen_total_tiempos.llego_cliente.isnull() )& (~resumen_total_tiempos.iniciado.isnull() )]

df_tiempo_total["TiempoTotal"] = df_tiempo_total["llego_cliente"] - df_tiempo_total["ORDER_DATE_COL"]
tiempo_total = df_tiempo_total["TiempoTotal"]
tiempo_total_min = []

for elemento in tiempo_total:
    tiempo_total_min.append(elemento.total_seconds()/60)

df_tiempo_total["TiempoTotal_min"] = tiempo_total_min

df_tiempo_total["TiempoUM"] = df_tiempo_total["llego_cliente"] - df_tiempo_total["iniciado"]
tiempo_um = df_tiempo_total["TiempoUM"]
tiempo_um_min = []

for elemento in tiempo_um:
    tiempo_um_min.append(elemento.total_seconds()/60)
    
df_tiempo_total["TiempoUM_min"] = tiempo_um_min

df_tiempo_total["Tiempo_Reprogramacion"] = df_tiempo_total["iniciado"] - df_tiempo_total["ORDER_DATE_COL"]
tiempo_reprog = df_tiempo_total["Tiempo_Reprogramacion"]
tiempo_reprog_min = []

for elemento in tiempo_reprog:
    tiempo_reprog_min.append(elemento.total_seconds()/60)

df_tiempo_total["Tiempo_Reprogramacion_min"] = tiempo_reprog_min
    
df_tiempo_total["CumpleTiempoTotal1h"] = "No Cumple"
df_tiempo_total["CumpleTiempoTotal90min"] = "No Cumple"
df_tiempo_total["CumpleTiempoUM"] = "No Cumple"
df_tiempo_total["Categoria 6km"] = "Mayor a 6km"

df_tiempo_total.loc[df_tiempo_total["TiempoTotal_min"]<=60,"CumpleTiempoTotal1h"] = "Cumple"
df_tiempo_total.loc[df_tiempo_total["TiempoTotal_min"]<=90,"CumpleTiempoTotal90min"] = "Cumple"
df_tiempo_total.loc[df_tiempo_total["TiempoUM_min"]<=40,"CumpleTiempoUM"] = "Cumple"
df_tiempo_total.loc[df_tiempo_total["distancia_km"]<=6,"Categoria 6km"] = "Menor a 6km"

df_tiempo_total["Valor Servicio"] = pd.to_numeric(df_tiempo_total["Valor Servicio"],downcast = "integer")



# ### Filtros para tiempos totales y cumplimientos

# In[49]:


df_tiempo_total_filtro = df_tiempo_total[(df_tiempo_total["TiempoTotal_min"]>=0) & (df_tiempo_total["TiempoTotal_min"]<=900)]
df_tiempo_total_filtro_6km = df_tiempo_total_filtro[df_tiempo_total_filtro["distancia_km"]<=6]
df_tiempo_total_filtro_reprog = df_tiempo_total_filtro[df_tiempo_total_filtro["Tiempo_Reprogramacion_min"]<=120]
df_tiempo_total_filtro_reprog_6km= df_tiempo_total_filtro_reprog[df_tiempo_total_filtro_reprog["distancia_km"]<=6]


# ### Tabla dinámica kilometraje participación

# In[50]:


pivot_6km = pd.pivot_table(df_tiempo_total_filtro, index =["CiudadB","Mes_Orden"],columns =["Categoria 6km"],values =["ORDER_NO"],aggfunc = "count")
pivot_6km[("ORDER_NO","PorcMenor6km")] = pivot_6km[("ORDER_NO","Menor a 6km")] / (pivot_6km[("ORDER_NO","Menor a 6km")] + pivot_6km[("ORDER_NO","Mayor a 6km")] )
pivot_6km=pivot_6km.reset_index()
pivot_6km.columns=["Ciudad","Mes_Orden","Mayor6km","Menor6km","PorcMenor6km"]
pivot_6km["PorcMenor6km"] = np.round(pivot_6km["PorcMenor6km"]*100,decimals=1)


# ### Tablas Dinámicas - Tiempos Totales, Cumplimientos

# In[51]:


###Generales filtro 900 min

TiempoTotal_promedio = pd.pivot_table(df_tiempo_total_filtro,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoTotal_min"],aggfunc = np.mean)
TiempoUM_promedio = pd.pivot_table(df_tiempo_total_filtro,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)

cumpleTiempoTotal1h = pd.pivot_table(df_tiempo_total_filtro,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal1h","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal1h[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal1h[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal1h[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal1h[("ORDER_NO","No Cumple","SameDay")]) 
cumpleTiempoTotal90min = pd.pivot_table(df_tiempo_total_filtro,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal90min","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal90min[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal90min[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal90min[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal90min[("ORDER_NO","No Cumple","SameDay")]) 

TiempoTotal_promedio =TiempoTotal_promedio.reset_index()
TiempoTotal_promedio.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
TiempoTotal_promedio["SameDayCall"] = np.round(TiempoTotal_promedio["SameDayCall"],decimals =0)
TiempoTotal_promedio["SameDayEcomm"] = np.round(TiempoTotal_promedio["SameDayEcomm"],decimals =0)

TiempoUM_promedio =TiempoUM_promedio.reset_index()
TiempoUM_promedio.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
TiempoUM_promedio["SameDayCall"] = np.round(TiempoUM_promedio["SameDayCall"],decimals = 0)
TiempoUM_promedio["SameDayEcomm"] = np.round(TiempoUM_promedio["SameDayEcomm"],decimals = 0)

cumpleTiempoTotal1h = cumpleTiempoTotal1h.reset_index()
cumpleTiempoTotal1h.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal90min = cumpleTiempoTotal90min.reset_index()
cumpleTiempoTotal90min.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal1h["Cumplimiento"] = np.round(cumpleTiempoTotal1h["Cumplimiento"]*100,decimals = 1)
cumpleTiempoTotal90min["Cumplimiento"] = np.round(cumpleTiempoTotal90min["Cumplimiento"]*100 ,decimals =1)

cumpleUM40min = pd.pivot_table(df_tiempo_total_filtro,index =["CiudadB","Mes_Orden"],columns =["CumpleTiempoUM","LEVEL_OF_SERVICE"],values = ["ORDER_NO"],aggfunc = "count")
cumpleUM40min[("ORDER_NO","Cumplimiento","SameDay")] = cumpleUM40min[("ORDER_NO","Cumple","SameDay")] /(cumpleUM40min[("ORDER_NO","Cumple","SameDay")]  + cumpleUM40min[("ORDER_NO","No Cumple","SameDay")] )
cumpleUM40min = cumpleUM40min.reset_index()
cumpleUM40min.columns = ["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]

cumpleUM40min["Cumplimiento"] = np.round(cumpleUM40min["Cumplimiento"]*100,decimals=1)


#TiempoTotal_promedio_gral = pd.pivot_table(df_tiempo_total_filtro,index =["Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE","TiempoTotal_min"],aggfunc = np.mean)
#TiempoTotal_promedio_gral.reset_index()
#TiempoTotal_promedio_gral.columns =["Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
#TiempoTotal_promedio_gral["SameDayCall"] = np.round(TiempoTotal_promedio_gral["SameDayCall"],decimals =0)
#TiempoTotal_promedio_gral["SameDayEcomm"] = np.round(TiempoTotal_promedio_gral["SameDayEcomm"],decimals =0)

#TiempoUM_gral = pd.pivot_table(df_tiempo_total_filtro,index = ["Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)
#TiempoUM_gral = TiempoUM_gral.reset_index()
#TiempoUM_gral.columns = ["Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
#TiempoUM_gral["SameDayCall"] = np.round(TiempoUM_gral["SameDayCall"],decimals =0)
#TiempoUM_gral["SameDayEcomm"] = np.round(TiempoUM_gral["SameDayEcomm"],decimals =0) 

###Filtro 6km

TiempoTotal_promedio_6km = pd.pivot_table(df_tiempo_total_filtro_6km,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoTotal_min"],aggfunc = np.mean)
TiempoUM_promedio_6km = pd.pivot_table(df_tiempo_total_filtro_6km,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)

cumpleTiempoTotal1h_6km = pd.pivot_table(df_tiempo_total_filtro_6km,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal1h","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal1h_6km[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal1h_6km[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal1h_6km[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal1h_6km[("ORDER_NO","No Cumple","SameDay")]) 
cumpleTiempoTotal90min_6km = pd.pivot_table(df_tiempo_total_filtro_6km,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal90min","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal90min_6km[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal90min_6km[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal90min_6km[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal90min_6km[("ORDER_NO","No Cumple","SameDay")])

TiempoTotal_promedio_6km =TiempoTotal_promedio_6km.reset_index()
TiempoTotal_promedio_6km.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
TiempoUM_promedio_6km =TiempoUM_promedio_6km.reset_index()
TiempoUM_promedio_6km.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]

TiempoTotal_promedio_6km["SameDayCall"] = np.round(TiempoTotal_promedio_6km["SameDayCall"],decimals=0)
TiempoTotal_promedio_6km["SameDayEcomm"] = np.round(TiempoTotal_promedio_6km["SameDayEcomm"],decimals=0)
TiempoUM_promedio_6km["SameDayCall"] = np.round(TiempoUM_promedio_6km["SameDayCall"],decimals =0)
TiempoUM_promedio_6km["SameDayEcomm"] = np.round(TiempoUM_promedio_6km["SameDayCall"],decimals =0)

cumpleTiempoTotal1h_6km = cumpleTiempoTotal1h_6km.reset_index()
cumpleTiempoTotal1h_6km.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal90min_6km = cumpleTiempoTotal90min_6km.reset_index()
cumpleTiempoTotal90min_6km.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]

cumpleTiempoTotal1h_6km["Cumplimiento"] = np.round(cumpleTiempoTotal1h_6km["Cumplimiento"]*100,decimals =1)
cumpleTiempoTotal90min_6km ["Cumplimiento"] = np.round(cumpleTiempoTotal90min_6km ["Cumplimiento"]*100,decimals =1)

###Filtro reprogramación

TiempoTotal_promedio_sinRp = pd.pivot_table(df_tiempo_total_filtro_reprog,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoTotal_min"],aggfunc = np.mean)
TiempoUM_promedio_sinRp = pd.pivot_table(df_tiempo_total_filtro_reprog,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)

cumpleTiempoTotal1h_sinRp = pd.pivot_table(df_tiempo_total_filtro_reprog,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal1h","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal1h_sinRp[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal1h_sinRp[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal1h_sinRp[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal1h_sinRp[("ORDER_NO","No Cumple","SameDay")]) 
cumpleTiempoTotal90min_sinRp = pd.pivot_table(df_tiempo_total_filtro_reprog,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal90min","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal90min_sinRp[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal90min_sinRp[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal90min_sinRp[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal90min_sinRp[("ORDER_NO","No Cumple","SameDay")])

cumpleUM40min_sinRp = pd.pivot_table(df_tiempo_total_filtro_reprog,index =["CiudadB","Mes_Orden"],columns =["CumpleTiempoUM","LEVEL_OF_SERVICE"],values = ["ORDER_NO"],aggfunc = "count")
cumpleUM40min_sinRp[("ORDER_NO","Cumplimiento","SameDay")] = cumpleUM40min_sinRp[("ORDER_NO","Cumple","SameDay")] /(cumpleUM40min_sinRp[("ORDER_NO","Cumple","SameDay")]  + cumpleUM40min_sinRp[("ORDER_NO","No Cumple","SameDay")] ) 

TiempoTotal_promedio_sinRp =TiempoTotal_promedio_sinRp.reset_index()
TiempoTotal_promedio_sinRp.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
TiempoUM_promedio_sinRp =TiempoUM_promedio_sinRp.reset_index()
TiempoUM_promedio_sinRp.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]

TiempoTotal_promedio_sinRp["SameDayCall"] = np.round(TiempoTotal_promedio_sinRp["SameDayCall"],decimals =0)
TiempoTotal_promedio_sinRp["SameDayEcomm"] = np.round(TiempoTotal_promedio_sinRp["SameDayEcomm"],decimals =0)
TiempoUM_promedio_sinRp["SameDayCall"] = np.round(TiempoUM_promedio_sinRp["SameDayCall"],decimals =0)
TiempoUM_promedio_sinRp["SameDayEcomm"] = np.round(TiempoUM_promedio_sinRp["SameDayEcomm"],decimals =0)

cumpleTiempoTotal1h_sinRp = cumpleTiempoTotal1h_sinRp.reset_index()
cumpleTiempoTotal1h_sinRp.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal90min_sinRp = cumpleTiempoTotal90min_sinRp.reset_index()
cumpleTiempoTotal90min_sinRp.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]

cumpleUM40min_sinRp = cumpleUM40min_sinRp.reset_index()
cumpleUM40min_sinRp.columns = ["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]

cumpleUM40min_sinRp["Cumplimiento"] = np.round(cumpleUM40min_sinRp["Cumplimiento"]*100,decimals =1)
cumpleTiempoTotal1h_sinRp["Cumplimiento"] = np.round(cumpleTiempoTotal1h_sinRp["Cumplimiento"]*100,decimals=1)
cumpleTiempoTotal90min_sinRp["Cumplimiento"] = np.round(cumpleTiempoTotal90min_sinRp["Cumplimiento"]*100,decimals =1)

#TiempoTotal_promedio_sinRp_gral =  pd.pivot_table(df_tiempo_total_filtro_reprog,index =["Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE","TiempoTotal_min"],aggfunc = np.mean)
#TiempoTotal_promedio_sinRp_gral.reset_index()
#TiempoTotal_promedio_sinRp_gral.columns =["Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
#TiempoTotal_promedio_sinRp_gral["SameDayCall"] = np.round(TiempoTotal_promedio_sinRp_gral["SameDayCall"],decimals =0)
#TiempoTotal_promedio_sinRp_gral["SameDayEcomm"] = np.round(TiempoTotal_promedio_sinRp_gral["SameDayEcomm"],decimals =0)

#TiempoUM_promedio_sinRp_gral = pd.pivot_table(df_tiempo_total_filtro_reprog,index = ["Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)
#TiempoUM_promedio_sinRp_gral = TiempoUM_promedio_sinRp.reset_index()
#TiempoUM_promedio_sinRp_gral.columns = ["Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
#TiempoUM_promedio_sinRp_gral["SameDayCall"] = np.round(TiempoUM_promedio_sinRp_gral["SameDayCall"],decimals =0)
#TiempoUM_promedio_sinRp_gral["SameDayEcomm"] = np.round(TiempoUM_promedio_sinRp_gral["SameDayEcomm"],decimals =0) 

###Filtro reprogramación y 6km

TiempoTotal_promedio_sinRp_6km = pd.pivot_table(df_tiempo_total_filtro_reprog_6km,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoTotal_min"],aggfunc = np.mean)
TiempoUM_promedio_sinRp_6km = pd.pivot_table(df_tiempo_total_filtro_reprog_6km,index = ["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","ENTRY_TYPE"],values = ["TiempoUM_min"],aggfunc = np.mean)

cumpleTiempoTotal1h_sinRp_6km = pd.pivot_table(df_tiempo_total_filtro_reprog_6km,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal1h","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal1h_sinRp_6km[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal1h_sinRp_6km[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal1h_sinRp_6km[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal1h_sinRp_6km[("ORDER_NO","No Cumple","SameDay")]) 
cumpleTiempoTotal90min_sinRp_6km = pd.pivot_table(df_tiempo_total_filtro_reprog_6km,index= ["CiudadB","Mes_Orden"],columns = ["CumpleTiempoTotal90min","LEVEL_OF_SERVICE"], values = ["ORDER_NO"],aggfunc = "count")
cumpleTiempoTotal90min_sinRp_6km[("ORDER_NO","Cumplimiento","SameDay")] = cumpleTiempoTotal90min_sinRp_6km[("ORDER_NO","Cumple","SameDay")]/(cumpleTiempoTotal90min_sinRp_6km[("ORDER_NO","Cumple","SameDay")] + cumpleTiempoTotal90min_sinRp_6km[("ORDER_NO","No Cumple","SameDay")])

cumpleUM40min_sinRp_6km = pd.pivot_table(df_tiempo_total_filtro_reprog_6km,index =["CiudadB","Mes_Orden"], columns =["CumpleTiempoUM","LEVEL_OF_SERVICE"],values = ["ORDER_NO"], aggfunc ="count")
cumpleUM40min_sinRp_6km[("ORDER_NO","Cumplimiento","SameDay")] = cumpleUM40min_sinRp_6km[("ORDER_NO","Cumple","SameDay")] / (cumpleUM40min_sinRp_6km[("ORDER_NO","Cumple","SameDay")] + cumpleUM40min_sinRp_6km[("ORDER_NO","No Cumple","SameDay")]    )

TiempoTotal_promedio_sinRp_6km = TiempoTotal_promedio_sinRp_6km.reset_index()
TiempoTotal_promedio_sinRp_6km.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]
TiempoUM_promedio_sinRp_6km = TiempoUM_promedio_sinRp_6km.reset_index()
TiempoUM_promedio_sinRp_6km.columns = ["Ciudad","Mes_Orden","NextDayCall","NextDayEcomm","SameDayCall","SameDayEcomm"]

TiempoTotal_promedio_sinRp_6km["SameDayCall"] = np.round(TiempoTotal_promedio_sinRp_6km["SameDayCall"],decimals =0)
TiempoTotal_promedio_sinRp_6km["SameDayEcomm"] = np.round(TiempoTotal_promedio_sinRp_6km["SameDayEcomm"],decimals =0)
TiempoUM_promedio_sinRp_6km["SameDayCall"] = np.round(TiempoUM_promedio_sinRp_6km["SameDayCall"],decimals=0)
TiempoUM_promedio_sinRp_6km["SameDayEcomm"] = np.round(TiempoUM_promedio_sinRp_6km["SameDayEcomm"],decimals=0)

cumpleTiempoTotal1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km.reset_index()
cumpleTiempoTotal1h_sinRp_6km.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km.reset_index()
cumpleTiempoTotal90min_sinRp_6km.columns =["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleTiempoTotal1h_sinRp_6km["Cumplimiento"] = np.round(cumpleTiempoTotal1h_sinRp_6km["Cumplimiento"]*100,decimals=1)
cumpleTiempoTotal90min_sinRp_6km["Cumplimiento"] = np.round(cumpleTiempoTotal90min_sinRp_6km["Cumplimiento"]*100,decimals =1)


cumpleUM40min_sinRp_6km = cumpleUM40min_sinRp_6km.reset_index()
cumpleUM40min_sinRp_6km.columns = ["Ciudad","Mes_Orden","CumpleNextDay","CumpleSameDay","NoCumpleNextDay","NoCumpleSameDay","Cumplimiento"]
cumpleUM40min_sinRp_6km["Cumplimiento"] = np.round(cumpleUM40min_sinRp_6km["Cumplimiento"]*100,decimals=1 )


# ### Calculos Tiempos Alistamiento

# In[52]:


tiempos_total = pd.DataFrame(columns=["ORDER_NO","STATUS","STATUS_DATE","SHIPNODE_KEY"])
for the_file in os.listdir(r"C:\Users\luis.montoya\Downloads\Tiempos OMS"):
    archivo_subida = os.path.join(r"C:\Users\luis.montoya\Downloads\Tiempos OMS",the_file) ###Importación de la base de tiempos
    tiempos_parcial=pd.read_csv(archivo_subida,sep=",")
    columnas_tiempos = ["RN","ORDER_NO","ORDER_HEADER_KEY","STATUS","STATUS_DATE","CREATEUSERID","MODIFYUSERID","SHIPMENT_KEY","SCAC","SHIPNODE_KEY","ASSIGNED_TO_USER_ID"]
    iteracion = len(tiempos_parcial.columns) - len(columnas_tiempos)
    for i in range(iteracion):
        columnas_tiempos.append("BLANCO")
    
    tiempos_parcial.columns=columnas_tiempos
    tiempos_parcial=tiempos_parcial.drop(0,axis=0)
    print(the_file)
    tiempos_parcial = tiempos_parcial[["ORDER_NO","STATUS","STATUS_DATE","SHIPNODE_KEY"]]
    tiempos_total = pd.concat([tiempos_total,tiempos_parcial],axis=0)


# In[53]:


tiempos_total = tiempos_total[tiempos_total.STATUS.isin(["3350.1000","3350.1500.1000"])] ### Se toma solo ready for backroompick y packing complete


tiempos_total["STATUS_DATE"] = pd.to_datetime(tiempos_total["STATUS_DATE"],format="%Y-%m-%d %H:%M:%S")
status_date_inicial = tiempos_total["STATUS_DATE"]
STATUS_DATE_COL =[]

for fecha in status_date_inicial:                        ###Se convierte el status date a fecha hora colombia
    resta = fecha -datetime.timedelta(hours=5)
    STATUS_DATE_COL.append(resta)
    
    
    
tiempos_total["STATUS_DATE_COL"] = STATUS_DATE_COL


readyforback = tiempos_total[tiempos_total["STATUS"]=="3350.1000"]   ###df ready for backroompick
packingcomplete = tiempos_total[tiempos_total["STATUS"]=="3350.1500.1000"] ###df packing complete


# In[54]:


readyforback= readyforback.sort_values("STATUS_DATE_COL",ascending=True) ### Más antiguo al mas reciente
readyforbackprimeros= readyforback.drop_duplicates(subset = ["ORDER_NO"],keep = "first")

packingcomplete = packingcomplete.drop_duplicates()

inicioalistamiento_mas_antiguo = pd.merge(df_tiempo_total,readyforbackprimeros,left_on="ORDER_NO",right_on="ORDER_NO",how="left")


inicioalistamiento_mas_antiguo=inicioalistamiento_mas_antiguo[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','STATUS_DATE_COL']]

inicioalistamiento_mas_antiguo.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE']

inicioalistamiento_mas_antiguo = pd.merge(inicioalistamiento_mas_antiguo,packingcomplete,left_on="ORDER_NO",right_on="ORDER_NO",how= "left") 

inicioalistamiento_mas_antiguo=inicioalistamiento_mas_antiguo[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE','STATUS_DATE_COL']]

inicioalistamiento_mas_antiguo.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE','PackingComplete']

inicioalistamiento_mas_antiguo_final = inicioalistamiento_mas_antiguo[(~inicioalistamiento_mas_antiguo.RFBRP_DATE.isnull())&(~inicioalistamiento_mas_antiguo.PackingComplete.isnull())]


inicioalistamiento_mas_antiguo_final["Alistamiento_a"] = inicioalistamiento_mas_antiguo_final["PackingComplete"] - inicioalistamiento_mas_antiguo_final["RFBRP_DATE"]

dif_alistamiento = inicioalistamiento_mas_antiguo_final["Alistamiento_a"]
Alistamiento_min =[]
for elemento in dif_alistamiento:
    Alistamiento_min.append(elemento.total_seconds()/60)


inicioalistamiento_mas_antiguo_final["TiempoAlistamiento_(min)"] = Alistamiento_min

###Se eliminan valores negativos del tiempo de alistamiento
inicioalistamiento_mas_antiguo_final = inicioalistamiento_mas_antiguo_final[inicioalistamiento_mas_antiguo_final["TiempoAlistamiento_(min)"]>=0]

inicioalistamiento_mas_antiguo_final["CumplimientoAlistamiento_10(min)"] = "No Cumple"
inicioalistamiento_mas_antiguo_final["CumplimientoAlistamiento_3(min)"] = "No Cumple"

inicioalistamiento_mas_antiguo_final.loc[inicioalistamiento_mas_antiguo_final["TiempoAlistamiento_(min)"]<=10,"CumplimientoAlistamiento_10(min)"]="Cumple"
inicioalistamiento_mas_antiguo_final.loc[inicioalistamiento_mas_antiguo_final["TiempoAlistamiento_(min)"]<=3,"CumplimientoAlistamiento_3(min)"]="Cumple"


# In[55]:


readyforbackultimos= readyforback.drop_duplicates(subset = ["ORDER_NO"],keep = "last")
packingcomplete = packingcomplete.drop_duplicates()


inicioalistamiento_mas_reciente = pd.merge(df_tiempo_total,readyforbackultimos,left_on="ORDER_NO",right_on="ORDER_NO",how="left") ###Hace el cruce para tener el tiempo del ready for backroompick mas antiguo

inicioalistamiento_mas_reciente=inicioalistamiento_mas_reciente[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','STATUS_DATE_COL']]

inicioalistamiento_mas_reciente.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE']

inicioalistamiento_mas_reciente = pd.merge(inicioalistamiento_mas_reciente,packingcomplete,left_on="ORDER_NO",right_on="ORDER_NO",how= "left") 

inicioalistamiento_mas_reciente=inicioalistamiento_mas_reciente[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE','STATUS_DATE_COL']]

inicioalistamiento_mas_reciente.columns = ['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden',
       'Semana_Orden', 'DiaSemana_Orden', 'Hora_Orden', 'SHIPNODE_KEY2',
       'COD_SUC', 'CIUDAD_MUNICIPIO', 'GERENTE DE ZONA', 'Localidad',
       'CiudadB', 'numorden', 'iniciado', 'asignado', 'llego_punto',
       'salio_punto', 'llego_cliente', 'distancia_km', 'Finalizado Fallido',
       'Valor Servicio', 'Proveedor', 'Estado UM', 'numorden2', 'TiempoTotal',
       'TiempoTotal_min', 'TiempoUM', 'TiempoUM_min', 'Tiempo_Reprogramacion',
       'Tiempo_Reprogramacion_min', 'CumpleTiempoTotal1h',
       'CumpleTiempoTotal90min', 'CumpleTiempoUM','RFBRP_DATE','PackingComplete']

inicioalistamiento_mas_reciente_final = inicioalistamiento_mas_reciente[(~inicioalistamiento_mas_reciente.RFBRP_DATE.isnull())&(~inicioalistamiento_mas_reciente.PackingComplete.isnull())]


inicioalistamiento_mas_reciente_final["Alistamiento_a"] = inicioalistamiento_mas_reciente_final["PackingComplete"] - inicioalistamiento_mas_reciente_final["RFBRP_DATE"]

dif_alistamiento = inicioalistamiento_mas_reciente_final["Alistamiento_a"]
Alistamiento_min =[]
for elemento in dif_alistamiento:
    Alistamiento_min.append(elemento.total_seconds()/60)


inicioalistamiento_mas_reciente_final["TiempoAlistamiento_(min)"] = Alistamiento_min

###Se eliminan valores negativos del tiempo de alistamiento
inicioalistamiento_mas_reciente_final = inicioalistamiento_mas_reciente_final[inicioalistamiento_mas_reciente_final["TiempoAlistamiento_(min)"]>=0]

inicioalistamiento_mas_reciente_final["CumplimientoAlistamiento_10(min)"] = "No Cumple"
inicioalistamiento_mas_reciente_final["CumplimientoAlistamiento_3(min)"] = "No Cumple"

inicioalistamiento_mas_reciente_final.loc[inicioalistamiento_mas_reciente_final["TiempoAlistamiento_(min)"]<=10,"CumplimientoAlistamiento_10(min)"]="Cumple"
inicioalistamiento_mas_reciente_final.loc[inicioalistamiento_mas_reciente_final["TiempoAlistamiento_(min)"]<=3,"CumplimientoAlistamiento_3(min)"]="Cumple"


# ### Tablas Dinámicas Tiempos de alistamiento y cumplimiento alistamiento

# In[56]:


tiempo_alistamiento1er  = pd.pivot_table(inicioalistamiento_mas_antiguo_final,index =["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE"],values = ["TiempoAlistamiento_(min)"],aggfunc =np.mean)
tiempo_alistamiento1er=tiempo_alistamiento1er.reset_index()
tiempo_alistamiento1er.columns = ["Ciudad","Mes_Orden","Alistamiento_NextDay","Alistamiento_SameDay"]
tiempo_alistamiento1er = tiempo_alistamiento1er[["Ciudad","Mes_Orden","Alistamiento_SameDay"]]

tiempo_alistamientoult  = pd.pivot_table(inicioalistamiento_mas_reciente_final,index =["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE"],values = ["TiempoAlistamiento_(min)"],aggfunc =np.mean)
tiempo_alistamientoult=tiempo_alistamientoult.reset_index()
tiempo_alistamientoult.columns = ["Ciudad","Mes_Orden","Alistamiento_NextDay","Alistamiento_SameDay"]
tiempo_alistamientoult = tiempo_alistamientoult[["Ciudad","Mes_Orden","Alistamiento_SameDay"]]

tiempo_alistamiento1er["Alistamiento_SameDay"] = np.round(tiempo_alistamiento1er["Alistamiento_SameDay"],decimals=0)
tiempo_alistamientoult["Alistamiento_SameDay"] = np.round(tiempo_alistamientoult["Alistamiento_SameDay"],decimals=0)


cumplimiento3min = pd.pivot_table(inicioalistamiento_mas_antiguo_final,index =["CiudadB","Mes_Orden"],columns = ["LEVEL_OF_SERVICE","CumplimientoAlistamiento_3(min)"],values =["ORDER_NO"],aggfunc ="count")
cumplimiento3min[("ORDER_NO","SameDay","Cumplimiento")] = cumplimiento3min[("ORDER_NO","SameDay","Cumple")] / (cumplimiento3min[("ORDER_NO","SameDay","Cumple")] + cumplimiento3min[("ORDER_NO","SameDay","No Cumple")] )
cumplimiento3min = cumplimiento3min.reset_index()
cumplimiento3min.columns = ["Ciudad","Mes_Orden","NextDayCumple","NextDayNoCumple","SameDayCumple","SameDayNoCumple","Cumplimiento3min"]
cumplimiento3min= cumplimiento3min[["Ciudad","Mes_Orden","Cumplimiento3min"]]
cumplimiento3min["Cumplimiento3min"] = np.round(cumplimiento3min["Cumplimiento3min"]*100,decimals=1)


# ### Cobro de domicilios

# In[57]:


total_cobro = pd.DataFrame(columns = ["Fecha_linea","Sucursal","Codigo","Canal","Valor"])
for the_file in os.listdir(r"C:\Users\luis.montoya\OneDrive - Grupo Socofar\PowerBI - Última milla\CobroDomicilios"):
    archivo_cobro = os.path.join(r"C:\Users\luis.montoya\OneDrive - Grupo Socofar\PowerBI - Última milla\CobroDomicilios",the_file)
    parcial_cobro = pd.read_excel(archivo_cobro)
    print(the_file)
    total_cobro = pd.concat([total_cobro,parcial_cobro])

total_cobro["Fecha_linea"] = pd.to_datetime(total_cobro["Fecha_linea"],format ="%Y-%m-%d %H:%M:%S")

fechas_cobro =total_cobro["Fecha_linea"]
mes_cobro = []
for elemento in fechas_cobro:
    mes_cobro.append(elemento.month)

total_cobro["Mes_Cobro"] = mes_cobro

cobro_canal = pd.pivot_table(total_cobro,index =["Mes_Cobro"],columns =["Canal"],values = ["Valor"],aggfunc = np.sum,fill_value=0)
cobro_canal[("Valor","Total_Cobro")] =  cobro_canal[("Valor","Domifacil")] + cobro_canal[("Valor","Mostrador")] + cobro_canal[("Valor","OMS")]
cobro_canal=cobro_canal.reset_index()
cobro_canal.columns =["Mes_Cobro","Domifacil","Mostrador","OMS","Total_Cobro"]

cobro_canal["Domifacil"] =np.round(cobro_canal["Domifacil"]/1000000,decimals=3)
cobro_canal["Mostrador"] =np.round(cobro_canal["Mostrador"]/1000000,decimals=3)
cobro_canal["OMS"] = np.round(cobro_canal["OMS"]/1000000,decimals=3)
cobro_canal["Total_Cobro"] = np.round(cobro_canal["Total_Cobro"]/1000000,decimals=3)


# In[58]:


saltos_total = pd.DataFrame(columns=["ORDER_NO","ORDER_HEADER_KEY","SHIPMENT_KEY","SHIPNODE_KEY","STATUS","STATUS_DATE","DELIVERY_METHOD","ORDER_TYPE","EXTN_SHORT","ASSIGNED_TO_USER_ID"])
for the_file in os.listdir(r"C:\Users\luis.montoya\Downloads\Saltos OMS Q3 2021"):
    archivo_subida = os.path.join(r"C:\Users\luis.montoya\Downloads\Saltos OMS Q3 2021",the_file) 
    saltos_parcial=pd.read_csv(archivo_subida,sep=",")
    columnas_saltos= ["RN","ORDER_NO","ORDER_HEADER_KEY","SHIPMENT_KEY","SHIPNODE_KEY","STATUS","STATUS_DATE","DELIVERY_METHOD","ORDER_TYPE","EXTN_SHORT","ASSIGNED_TO_USER_ID","BLANCOI","BLANCOII"]  
    saltos_parcial.columns=columnas_saltos
    saltos_parcial=saltos_parcial.drop(0,axis=0)
    print(the_file)
    saltos_parcial=saltos_parcial[["ORDER_NO","ORDER_HEADER_KEY","SHIPMENT_KEY","SHIPNODE_KEY","STATUS","STATUS_DATE","DELIVERY_METHOD","ORDER_TYPE","EXTN_SHORT","ASSIGNED_TO_USER_ID"]]
    saltos_total = pd.concat([saltos_total,saltos_parcial],axis=0)
    
saltos_total["Tipo_Salto"] = "Sin tipo"

saltos_total.loc[(saltos_total.EXTN_SHORT.isin(["PCNCL","CNCL","BO"])) & (~saltos_total.ASSIGNED_TO_USER_ID.isnull()),"Tipo_Salto"]="Quiebre"
saltos_total.loc[(saltos_total.EXTN_SHORT.isnull()) & (saltos_total.ASSIGNED_TO_USER_ID.isnull()) ,"Tipo_Salto"]="Tiempo"

saltos_total = saltos_total[saltos_total["Tipo_Salto"]!="Sin tipo"]


resumen_total_ciudad_saltos = pd.merge(resumen_total_ciudad,saltos_total,left_on="ORDER_NO",right_on="ORDER_NO",how="left")

resumen_total_ciudad_saltos = resumen_total_ciudad_saltos[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden', 
       'Semana_Orden','DiaSemana_Orden','Hora_Orden', 'SHIPNODE_KEY2', 'COD_SUC',
       'CIUDAD_MUNICIPIO', 'Localidad', 'CiudadB',
       'estado2', 'Tipo_Salto']]

resumen_total_ciudad_saltos["Tipo_Salto2"] = "Sin Salto"
resumen_total_ciudad_saltos.loc[resumen_total_ciudad_saltos["Tipo_Salto"] == "Quiebre","Tipo_Salto2"] = "Quiebre"
resumen_total_ciudad_saltos.loc[resumen_total_ciudad_saltos["Tipo_Salto"] == "Tiempo","Tipo_Salto2"] = "Tiempo"

Porcentaje_saltos_tipo = pd.pivot_table(resumen_total_ciudad_saltos,index=["CiudadB","Mes_Orden"],columns=["Tipo_Salto2"],values=["ORDER_NO"],aggfunc = 'count')
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos General')] = (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')]) / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos Quiebre')] = Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')]  / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos Tiempo')] = Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')]  / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )



# In[59]:


resumen_total_ciudad_saltos = resumen_total_ciudad_saltos[['ORDER_NO', 'ORDER_DATE', 'ENTRY_TYPE', 'LEVEL_OF_SERVICE',
       'STATUS_NAME', 'EXTN_ORG_REQ_SHIP_DATE', 'EXTN_ET_FULFILMENT',
       'SHIPNODE_KEY_x', 'ORDER_DATE_COL', 'Dia_Orden', 'Mes_Orden', ####Corregir esta parte
       'Semana_Orden','DiaSemana_Orden','Hora_Orden', 'SHIPNODE_KEY2', 'COD_SUC',
       'CIUDAD_MUNICIPIO', 'Localidad', 'CiudadB',
       'estado2', 'Tipo_Salto']]

resumen_total_ciudad_saltos["Tipo_Salto2"] = "Sin Salto"
resumen_total_ciudad_saltos.loc[resumen_total_ciudad_saltos["Tipo_Salto"] == "Quiebre","Tipo_Salto2"] = "Quiebre"
resumen_total_ciudad_saltos.loc[resumen_total_ciudad_saltos["Tipo_Salto"] == "Tiempo","Tipo_Salto2"] = "Tiempo"

Porcentaje_saltos_tipo = pd.pivot_table(resumen_total_ciudad_saltos,index=["CiudadB","Mes_Orden"],columns=["Tipo_Salto2"],values=["ORDER_NO"],aggfunc = 'count')
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos General')] = (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')]) / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos Quiebre')] = Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')]  / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )
Porcentaje_saltos_tipo[('ORDER_NO','%Saltos Tiempo')] = Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')]  / (Porcentaje_saltos_tipo[('ORDER_NO','Quiebre')] + Porcentaje_saltos_tipo[('ORDER_NO','Tiempo')] + Porcentaje_saltos_tipo[('ORDER_NO','Sin Salto')]  )

Porcentaje_saltos_tipo = Porcentaje_saltos_tipo.reset_index()
Porcentaje_saltos_tipo.columns = ["Ciudad","Mes_Orden","Quiebre","Sin Salto","Tiempo","Porc Saltos General","Porc Saltos Quiebre","Porc Saltos Tiempo"]

Porcentaje_saltos_tipo["Porc Saltos General"] = np.round(Porcentaje_saltos_tipo["Porc Saltos General"]*100,decimals =1)
Porcentaje_saltos_tipo["Porc Saltos Quiebre"] = np.round(Porcentaje_saltos_tipo["Porc Saltos Quiebre"]*100,decimals =1)
Porcentaje_saltos_tipo["Porc Saltos Tiempo"] = np.round(Porcentaje_saltos_tipo["Porc Saltos Tiempo"]*100,decimals =1)


# In[60]:


bogotaprimerRFBP= tiempo_alistamiento1er[tiempo_alistamiento1er["Ciudad"]=="Bogotá"]
bquillaprimerRFBP= tiempo_alistamiento1er[tiempo_alistamiento1er["Ciudad"]=="Barranquilla"]
caliprimerRFBP= tiempo_alistamiento1er[tiempo_alistamiento1er["Ciudad"]=="Cali"]
medellinprimerRFBP= tiempo_alistamiento1er[tiempo_alistamiento1er["Ciudad"]=="Medellín"]
otrasprimerRFBP= tiempo_alistamiento1er[tiempo_alistamiento1er["Ciudad"]=="Otras ciudades"]

#####################################################################################################
bogotaultimoRFBP = tiempo_alistamientoult[tiempo_alistamientoult["Ciudad"]=="Bogotá"]
bquillaultimoRFBP = tiempo_alistamientoult[tiempo_alistamientoult["Ciudad"]=="Barranquilla"]
caliultimoRFBP = tiempo_alistamientoult[tiempo_alistamientoult["Ciudad"]=="Cali"]
medellinultimoRFBP = tiempo_alistamientoult[tiempo_alistamientoult["Ciudad"]=="Medellín"]
otrasultimoRFBP = tiempo_alistamientoult[tiempo_alistamientoult["Ciudad"]=="Otras ciudades"]

#############################################################################################################
bogotaCumple3min = cumplimiento3min[cumplimiento3min["Ciudad"]=="Bogotá"]
bquillaCumple3min = cumplimiento3min[cumplimiento3min["Ciudad"]=="Barranquilla"]
caliCumple3min = cumplimiento3min[cumplimiento3min["Ciudad"]=="Cali"]
medellinCumple3min = cumplimiento3min[cumplimiento3min["Ciudad"]=="Medellín"]
otrasCumple3min = cumplimiento3min[cumplimiento3min["Ciudad"]=="Otras ciudades"]

####################################################################################################################
bogotakm = pivot_6km[pivot_6km["Ciudad"]=="Bogotá"]
bquillakm = pivot_6km[pivot_6km["Ciudad"]=="Barranquilla"]
calikm = pivot_6km[pivot_6km["Ciudad"]=="Cali"]
medellinkm = pivot_6km[pivot_6km["Ciudad"]=="Medellín"]
otrasciudadeskm = pivot_6km[pivot_6km["Ciudad"]=="Otras ciudades"]

####################################################################################################################
bogota_cancelados = cancelados_dev_ciudad[cancelados_dev_ciudad["Ciudad"]=="Bogotá"]
bquilla_cancelados = cancelados_dev_ciudad[cancelados_dev_ciudad["Ciudad"]=="Barranquilla"]
cali_cancelados = cancelados_dev_ciudad[cancelados_dev_ciudad["Ciudad"]=="Cali"]
medellin_cancelados = cancelados_dev_ciudad[cancelados_dev_ciudad["Ciudad"]=="Medellín"]
otrasciudades_cancelados = cancelados_dev_ciudad[cancelados_dev_ciudad["Ciudad"]=="Otras ciudades"]

###################################################################################################################
bogota_saltos = Porcentaje_saltos_tipo[Porcentaje_saltos_tipo["Ciudad"]=="Bogotá"]
bquilla_saltos = Porcentaje_saltos_tipo[Porcentaje_saltos_tipo["Ciudad"]=="Barranquilla"]
cali_saltos = Porcentaje_saltos_tipo[Porcentaje_saltos_tipo["Ciudad"]=="Cali"]
medellin_saltos = Porcentaje_saltos_tipo[Porcentaje_saltos_tipo["Ciudad"]=="Medellín"]
otrasciudades_saltos = Porcentaje_saltos_tipo[Porcentaje_saltos_tipo["Ciudad"]=="Otras ciudades"]

#################################################################################################################
bogota_cumpleUM_sinRp_6km = cumpleUM40min_sinRp_6km[cumpleUM40min_sinRp_6km["Ciudad"]=="Bogotá"]
bquilla_cumpleUM_sinRp_6km = cumpleUM40min_sinRp_6km[cumpleUM40min_sinRp_6km["Ciudad"]=="Barranquilla"]
cali_cumpleUM_sinRp_6km = cumpleUM40min_sinRp_6km[cumpleUM40min_sinRp_6km["Ciudad"]=="Cali"]
medellin_cumpleUM_sinRp_6km = cumpleUM40min_sinRp_6km[cumpleUM40min_sinRp_6km["Ciudad"]=="Medellín"]
otrosciudades_cumpleUM_sinRp_6km = cumpleUM40min_sinRp_6km[cumpleUM40min_sinRp_6km["Ciudad"]=="Otras ciudades"]

bogotaUM_sinRp_6km = TiempoUM_promedio_sinRp_6km[TiempoUM_promedio_sinRp_6km["Ciudad"]=="Bogotá"]
bquillaUM_sinRp_6km = TiempoUM_promedio_sinRp_6km[TiempoUM_promedio_sinRp_6km["Ciudad"]=="Barranquilla"]
caliUM_sinRp_6km = TiempoUM_promedio_sinRp_6km[TiempoUM_promedio_sinRp_6km["Ciudad"]=="Cali"]
medellinUM_sinRp_6km = TiempoUM_promedio_sinRp_6km[TiempoUM_promedio_sinRp_6km["Ciudad"]=="Medellín"]
otrasciudadesUM_sinRp_6km = TiempoUM_promedio_sinRp_6km[TiempoUM_promedio_sinRp_6km["Ciudad"]=="Otras ciudades"]

##############################################################################################################################
bogota_cumpleUM_sinRp = cumpleUM40min_sinRp[cumpleUM40min_sinRp["Ciudad"]=="Bogotá"]
bquilla_cumpleUM_sinRp = cumpleUM40min_sinRp[cumpleUM40min_sinRp["Ciudad"]=="Barranquilla"]
cali_cumpleUM_sinRp = cumpleUM40min_sinRp[cumpleUM40min_sinRp["Ciudad"]=="Cali"]
medellin_cumpleUM_sinRp = cumpleUM40min_sinRp[cumpleUM40min_sinRp["Ciudad"]=="Medellín"]
otrasciudades_cumpleUM_sinRp = cumpleUM40min_sinRp[cumpleUM40min_sinRp["Ciudad"]=="Otras ciudades"]

bogotaUM_sinRP=TiempoUM_promedio_sinRp[TiempoUM_promedio_sinRp["Ciudad"]=="Bogotá"]
bquillaUM_sinRP=TiempoUM_promedio_sinRp[TiempoUM_promedio_sinRp["Ciudad"]=="Barranquilla"]
caliUM_sinRP=TiempoUM_promedio_sinRp[TiempoUM_promedio_sinRp["Ciudad"]=="Cali"]
medellinUM_sinRP=TiempoUM_promedio_sinRp[TiempoUM_promedio_sinRp["Ciudad"]=="Medellín"]
otrasciudadesUM_sinRP = TiempoUM_promedio_sinRp[TiempoUM_promedio_sinRp["Ciudad"]=="Otras ciudades"]
##############################################################################################################################
bogota_cumple_total1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km[cumpleTiempoTotal1h_sinRp_6km["Ciudad"]=="Bogotá"]
bquilla_cumple_total1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km[cumpleTiempoTotal1h_sinRp_6km["Ciudad"]=="Barranquilla"]
cali_cumple_total1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km[cumpleTiempoTotal1h_sinRp_6km["Ciudad"]=="Cali"]
medellin_cumple_total1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km[cumpleTiempoTotal1h_sinRp_6km["Ciudad"]=="Medellín"]
otrasciudades_cumple_total1h_sinRp_6km = cumpleTiempoTotal1h_sinRp_6km[cumpleTiempoTotal1h_sinRp_6km["Ciudad"]=="Otras ciudades"]

bogota_cumple_total90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km[cumpleTiempoTotal90min_sinRp_6km["Ciudad"]=="Bogotá"]
bquilla_cumple_total90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km[cumpleTiempoTotal90min_sinRp_6km["Ciudad"]=="Barranquilla"]
cali_cumple_total90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km[cumpleTiempoTotal90min_sinRp_6km["Ciudad"]=="Cali"]
medellin_cumple_total90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km[cumpleTiempoTotal90min_sinRp_6km["Ciudad"]=="Medellín"]
otrasciudades_cumple_total90min_sinRp_6km = cumpleTiempoTotal90min_sinRp_6km[cumpleTiempoTotal90min_sinRp_6km["Ciudad"]=="Otras ciudades"]

bogota_TotalSinRP_6km = TiempoTotal_promedio_sinRp_6km[TiempoTotal_promedio_sinRp_6km["Ciudad"]=="Bogotá"]
bquilla_TotalSinRP_6km = TiempoTotal_promedio_sinRp_6km[TiempoTotal_promedio_sinRp_6km["Ciudad"]=="Barranquilla"]
cali_TotalSinRP_6km = TiempoTotal_promedio_sinRp_6km[TiempoTotal_promedio_sinRp_6km["Ciudad"]=="Cali"]
medellin_TotalSinRP_6km = TiempoTotal_promedio_sinRp_6km[TiempoTotal_promedio_sinRp_6km["Ciudad"]=="Medellín"]
otrasciudades_TotalSinRP_6km = TiempoTotal_promedio_sinRp_6km[TiempoTotal_promedio_sinRp_6km["Ciudad"]=="Otras ciudades"]


#######################################################################################################################
bogota_cumple_total1h_sinRp = cumpleTiempoTotal1h_sinRp[cumpleTiempoTotal1h_sinRp["Ciudad"]=="Bogotá"]
bquilla_cumple_total1h_sinRp = cumpleTiempoTotal1h_sinRp[cumpleTiempoTotal1h_sinRp["Ciudad"]=="Barranquilla"]
cali_cumple_total1h_sinRp = cumpleTiempoTotal1h_sinRp[cumpleTiempoTotal1h_sinRp["Ciudad"]=="Cali"]
medellin_cumple_total1h_sinRp = cumpleTiempoTotal1h_sinRp[cumpleTiempoTotal1h_sinRp["Ciudad"]=="Medellín"]
otrasciudades_cumple_total1h_sinRp =cumpleTiempoTotal1h_sinRp[cumpleTiempoTotal1h_sinRp["Ciudad"]=="Otras ciudades"]

bogota_cumple_total90min_sinRp = cumpleTiempoTotal90min_sinRp[cumpleTiempoTotal90min_sinRp["Ciudad"]=="Bogotá"]
bquilla_cumple_total90min_sinRp = cumpleTiempoTotal90min_sinRp[cumpleTiempoTotal90min_sinRp["Ciudad"]=="Barranquilla"]
cali_cumple_total90min_sinRp = cumpleTiempoTotal90min_sinRp[cumpleTiempoTotal90min_sinRp["Ciudad"]=="Cali"]
medellin_cumple_total90min_sinRp = cumpleTiempoTotal90min_sinRp[cumpleTiempoTotal90min_sinRp["Ciudad"]=="Medellín"]
otrasciudades_cumple_total90min_sinRp = cumpleTiempoTotal90min_sinRp[cumpleTiempoTotal90min_sinRp["Ciudad"]=="Otras ciudades"]

bogota_TotalsinRp = TiempoTotal_promedio_sinRp[TiempoTotal_promedio_sinRp["Ciudad"]=="Bogotá"]
bquilla_TotalsinRp = TiempoTotal_promedio_sinRp[TiempoTotal_promedio_sinRp["Ciudad"]=="Barranquilla"]
cali_TotalsinRp = TiempoTotal_promedio_sinRp[TiempoTotal_promedio_sinRp["Ciudad"]=="Cali"]
medellin_TotalsinRp = TiempoTotal_promedio_sinRp[TiempoTotal_promedio_sinRp["Ciudad"]=="Medellín"]
otrasciudades_totalsinRp = TiempoTotal_promedio_sinRp[TiempoTotal_promedio_sinRp["Ciudad"]=="Otras ciudades"]

#####################################################################################################3
bogota_cumple_total1h = cumpleTiempoTotal1h[cumpleTiempoTotal1h["Ciudad"]=="Bogotá"]
bquilla_cumple_total1h = cumpleTiempoTotal1h[cumpleTiempoTotal1h["Ciudad"]=="Barranquilla"]
cali_cumple_total1h = cumpleTiempoTotal1h[cumpleTiempoTotal1h["Ciudad"]=="Cali"]
medellin_cumple_total1h = cumpleTiempoTotal1h[cumpleTiempoTotal1h["Ciudad"]=="Medellín"]
otrasciudades_cumple_total1h =cumpleTiempoTotal1h[cumpleTiempoTotal1h["Ciudad"]=="Otras ciudades"]

bogota_cumple_total90min = cumpleTiempoTotal90min[cumpleTiempoTotal90min["Ciudad"]=="Bogotá"]
bquilla_cumple_total90min = cumpleTiempoTotal90min[cumpleTiempoTotal90min["Ciudad"]=="Barranquilla"]
cali_cumple_total90min = cumpleTiempoTotal90min[cumpleTiempoTotal90min["Ciudad"]=="Cali"]
medellin_cumple_total90min = cumpleTiempoTotal90min[cumpleTiempoTotal90min["Ciudad"]=="Medellín"]
otrasciudades_cumple_total90min = cumpleTiempoTotal90min[cumpleTiempoTotal90min["Ciudad"]=="Otras ciudades"]

bogota_Total = TiempoTotal_promedio[TiempoTotal_promedio["Ciudad"]== "Bogotá"]
bquilla_Total = TiempoTotal_promedio[TiempoTotal_promedio["Ciudad"]== "Barranquilla"]
cali_Total = TiempoTotal_promedio[TiempoTotal_promedio["Ciudad"]== "Cali"]
medellin_Total = TiempoTotal_promedio[TiempoTotal_promedio["Ciudad"]== "Medellín"]
otrasciudades_Total = TiempoTotal_promedio[TiempoTotal_promedio["Ciudad"]== "Otras ciudades"]


# In[61]:


from dash import Dash, dcc, html,Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

###Figura participación por ciudad

fig_participacion = go.Figure(data = [go.Bar(name ="Bogotá",x = participacionxciudad["Mes_Orden"], y= participacionxciudad["Prt Bogotá"],text =participacionxciudad["Prt Bogotá"],marker_color = '#d57017'),
                                      go.Bar(name ="Barranquilla",x = participacionxciudad["Mes_Orden"], y = participacionxciudad["Prt Barranquilla"], text =participacionxciudad["Prt Barranquilla"],marker_color='#fcdd12'),
                                      go.Bar(name ="Cali",x = participacionxciudad["Mes_Orden"], y = participacionxciudad["Prt Cali"], text = participacionxciudad["Prt Cali"],marker_color = '#bfbf1d' ),
                                      go.Bar(name = "Medellín", x = participacionxciudad["Mes_Orden"], y = participacionxciudad["Prt Medellín"], text = participacionxciudad["Prt Medellín"],marker_color = '#a2c920'),
                                      go.Bar(name = "Otras ciudades", x = participacionxciudad["Mes_Orden"],y =participacionxciudad["Prt Otras ciudades"], text = participacionxciudad["Prt Otras ciudades"],marker_color ='#5dc706')
])

fig_participacion.update_layout(barmode ='stack',margin = dict(l=20, r=20, t=40, b=20),legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),paper_bgcolor = 'rgb(232,230,230)')
fig_participacion.update_yaxes(title ="(%)")
fig_participacion.update_xaxes(dtick = 1, title = "Meses")
fig_participacion.update_traces(textfont_size=10)


    
    
    


###Figuras Tiempo Total promedio sin filtros

fig_Ttotal_nofiltro_bog = go.Figure()
fig_Ttotal_nofiltro_bog.add_trace(go.Scatter(x=bogota_Total["Mes_Orden"],y=bogota_Total["SameDayCall"],name ="Call Center",mode="lines+markers+text",text=bogota_Total["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_nofiltro_bog.add_trace(go.Scatter(x=bogota_Total["Mes_Orden"],y=bogota_Total["SameDayEcomm"],name ="Ecommerce",mode="lines+markers+text",text=bogota_Total["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_nofiltro_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_nofiltro_bog.update_yaxes(range=[40,130], title ="Min")
fig_Ttotal_nofiltro_bog.update_xaxes(dtick = 1, title = "Meses")
fig_Ttotal_nofiltro_bog.update_traces(textfont_size=10)

fig_Ttotal_nofiltro_bquilla = go.Figure()
fig_Ttotal_nofiltro_bquilla.add_trace(go.Scatter(x=bquilla_Total["Mes_Orden"],y=bquilla_Total["SameDayCall"],name="Call Center",mode="lines+markers+text",text=bquilla_Total["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_nofiltro_bquilla.add_trace(go.Scatter(x=bquilla_Total["Mes_Orden"],y=bquilla_Total["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=bquilla_Total["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_nofiltro_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)',uniformtext_minsize=18)
fig_Ttotal_nofiltro_bquilla.update_yaxes(range=[40,130], title ="Min")
fig_Ttotal_nofiltro_bquilla.update_xaxes(dtick = 1, title ="Meses")
fig_Ttotal_nofiltro_bquilla.update_traces(textfont_size=10)

fig_Ttotal_nofiltro_cali = go.Figure()
fig_Ttotal_nofiltro_cali.add_trace(go.Scatter(x=cali_Total["Mes_Orden"],y=cali_Total["SameDayCall"],name="Call Center",mode="lines+markers+text",text=cali_Total["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_nofiltro_cali.add_trace(go.Scatter(x=cali_Total["Mes_Orden"],y=cali_Total["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=cali_Total["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_nofiltro_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_nofiltro_cali.update_yaxes(range=[40,130],title="Min")
fig_Ttotal_nofiltro_cali.update_xaxes(dtick = 1, title ="Meses")
fig_Ttotal_nofiltro_cali.update_traces(textfont_size=10)

fig_Ttotal_nofiltro_med = go.Figure()
fig_Ttotal_nofiltro_med.add_trace(go.Scatter(x=medellin_Total["Mes_Orden"],y=medellin_Total["SameDayCall"],name="Call Center",mode="lines+markers+text",text=medellin_Total["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_nofiltro_med.add_trace(go.Scatter(x=medellin_Total["Mes_Orden"],y=medellin_Total["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=medellin_Total["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_nofiltro_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_nofiltro_med.update_yaxes(range=[40,130],title="Min")
fig_Ttotal_nofiltro_med.update_xaxes(dtick = 1, title ="Meses")
fig_Ttotal_nofiltro_med.update_traces(textfont_size=10)


fig_Ttotal_nofiltro_otros = go.Figure()
fig_Ttotal_nofiltro_otros.add_trace(go.Scatter(x=otrasciudades_Total["Mes_Orden"],y=otrasciudades_Total["SameDayCall"],name="Call Center",mode="lines+markers+text",text=otrasciudades_Total["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_nofiltro_otros.add_trace(go.Scatter(x=otrasciudades_Total["Mes_Orden"],y=otrasciudades_Total["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=otrasciudades_Total["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_nofiltro_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_nofiltro_otros.update_yaxes(range=[40,130], title = "Min")
fig_Ttotal_nofiltro_otros.update_xaxes(dtick = 1, title = "Meses")
fig_Ttotal_nofiltro_otros.update_traces(textfont_size=10)

###Figuras cumplimiento 1h y 90min sin filtros

fig_Cumpletotal_nofiltro_bog = go.Figure()
fig_Cumpletotal_nofiltro_bog.add_trace(go.Scatter(x=bogota_cumple_total1h["Mes_Orden"],y=bogota_cumple_total1h["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bogota_cumple_total1h["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_nofiltro_bog.add_trace(go.Scatter(x=bogota_cumple_total90min["Mes_Orden"],y=bogota_cumple_total90min["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bogota_cumple_total90min["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_nofiltro_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_nofiltro_bog.update_yaxes(range=[40,100], title ="(%)")
fig_Cumpletotal_nofiltro_bog.update_xaxes(dtick=1, title ="Meses")
fig_Cumpletotal_nofiltro_bog.update_traces(textfont_size=10)

fig_Cumpletotal_nofiltro_bquilla = go.Figure()
fig_Cumpletotal_nofiltro_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total1h["Mes_Orden"],y=bquilla_cumple_total1h["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bquilla_cumple_total1h["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_nofiltro_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total90min["Mes_Orden"],y=bquilla_cumple_total90min["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bquilla_cumple_total90min["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_nofiltro_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_nofiltro_bquilla.update_yaxes(range=[40,100],title = "(%)")
fig_Cumpletotal_nofiltro_bquilla.update_xaxes(dtick = 1,title = "Meses")
fig_Cumpletotal_nofiltro_bquilla.update_traces(textfont_size=10)

fig_Cumpletotal_nofiltro_cali = go.Figure()
fig_Cumpletotal_nofiltro_cali.add_trace(go.Scatter(x=cali_cumple_total1h["Mes_Orden"],y=cali_cumple_total1h["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=cali_cumple_total1h["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_nofiltro_cali.add_trace(go.Scatter(x=cali_cumple_total90min["Mes_Orden"],y=cali_cumple_total90min["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=cali_cumple_total90min["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_nofiltro_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_nofiltro_cali.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_nofiltro_cali.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_nofiltro_cali.update_traces(textfont_size=10)


fig_Cumpletotal_nofiltro_med = go.Figure()
fig_Cumpletotal_nofiltro_med.add_trace(go.Scatter(x=medellin_cumple_total1h["Mes_Orden"],y=medellin_cumple_total1h["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=medellin_cumple_total1h["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_nofiltro_med.add_trace(go.Scatter(x=medellin_cumple_total90min["Mes_Orden"],y=medellin_cumple_total90min["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=medellin_cumple_total90min["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_nofiltro_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_nofiltro_med.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_nofiltro_med.update_xaxes(dtick = 1,title ="Meses")
fig_Cumpletotal_nofiltro_med.update_traces(textfont_size=10)

fig_Cumpletotal_nofiltro_otros = go.Figure()
fig_Cumpletotal_nofiltro_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total1h["Mes_Orden"],y=otrasciudades_cumple_total1h["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=otrasciudades_cumple_total1h["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_nofiltro_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total90min["Mes_Orden"],y=otrasciudades_cumple_total90min["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=otrasciudades_cumple_total90min["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_nofiltro_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_nofiltro_otros.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_nofiltro_otros.update_xaxes(dtick = 1,title ="Meses")
fig_Cumpletotal_nofiltro_otros.update_traces(textfont_size=10)

###Figuras Tiempo total promedio filtrando altas reprogramaciones

fig_Ttotal_sinRp_bog = go.Figure()
fig_Ttotal_sinRp_bog.add_trace(go.Scatter(x=bogota_TotalsinRp["Mes_Orden"],y=bogota_TotalsinRp["SameDayCall"],name ="Call Center",mode="lines+markers+text",text=bogota_TotalsinRp["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp_bog.add_trace(go.Scatter(x=bogota_TotalsinRp["Mes_Orden"],y=bogota_TotalsinRp["SameDayEcomm"],name ="Ecommerce",mode="lines+markers+text",text=bogota_TotalsinRp["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp_bog.update_yaxes(range=[30,90],title ="Min")
fig_Ttotal_sinRp_bog.update_xaxes(dtick =1,title ="Meses")
fig_Ttotal_sinRp_bog.update_traces(textfont_size=10)

fig_Ttotal_sinRp_bquilla = go.Figure()
fig_Ttotal_sinRp_bquilla.add_trace(go.Scatter(x=bquilla_TotalsinRp["Mes_Orden"],y=bquilla_TotalsinRp["SameDayCall"],name="Call Center",mode="lines+markers+text",text=bquilla_TotalsinRp["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp_bquilla.add_trace(go.Scatter(x=bquilla_TotalsinRp["Mes_Orden"],y=bquilla_TotalsinRp["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=bquilla_TotalsinRp["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp_bquilla.update_yaxes(range=[30,90],title ="Min")
fig_Ttotal_sinRp_bquilla.update_xaxes(dtick = 1,title ="Meses")
fig_Ttotal_sinRp_bquilla.update_traces(textfont_size=10)

fig_Ttotal_sinRp_cali = go.Figure()
fig_Ttotal_sinRp_cali.add_trace(go.Scatter(x=cali_TotalsinRp["Mes_Orden"],y=cali_TotalsinRp["SameDayCall"],name="Call Center",mode="lines+markers+text",text=cali_TotalsinRp["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp_cali.add_trace(go.Scatter(x=cali_TotalsinRp["Mes_Orden"],y=cali_TotalsinRp["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=cali_TotalsinRp["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp_cali.update_yaxes(range=[30,90],title ="Min")
fig_Ttotal_sinRp_cali.update_xaxes(dtick =1,title ="Meses")
fig_Ttotal_sinRp_cali.update_traces(textfont_size=10)

fig_Ttotal_sinRp_med = go.Figure()
fig_Ttotal_sinRp_med.add_trace(go.Scatter(x=medellin_TotalsinRp["Mes_Orden"],y=medellin_TotalsinRp["SameDayCall"],name="Call Center",mode="lines+markers+text",text=medellin_TotalsinRp["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp_med.add_trace(go.Scatter(x=medellin_TotalsinRp["Mes_Orden"],y=medellin_TotalsinRp["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=medellin_TotalsinRp["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp_med.update_yaxes(range=[30,90],title = "(%)")
fig_Ttotal_sinRp_med.update_xaxes(dtick =1,title = "Meses")
fig_Ttotal_sinRp_med.update_traces(textfont_size=10)

fig_Ttotal_sinRp_otros = go.Figure()
fig_Ttotal_sinRp_otros.add_trace(go.Scatter(x=otrasciudades_totalsinRp["Mes_Orden"],y=otrasciudades_totalsinRp["SameDayCall"],name="Call Center",mode="lines+markers+text",text=otrasciudades_totalsinRp["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp_otros.add_trace(go.Scatter(x=otrasciudades_totalsinRp["Mes_Orden"],y=otrasciudades_totalsinRp["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=otrasciudades_totalsinRp["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp_otros.update_yaxes(range=[30,90],title ="(%)")
fig_Ttotal_sinRp_otros.update_xaxes(dtick =1,title ="Meses")
fig_Ttotal_sinRp_otros.update_traces(textfont_size=10)

###Figuras cumplimiento 1h y 90min filtrando altas reprogramaciones

fig_Cumpletotal_sinRP_bog = go.Figure()
fig_Cumpletotal_sinRP_bog.add_trace(go.Scatter(x=bogota_cumple_total1h_sinRp["Mes_Orden"],y=bogota_cumple_total1h_sinRp["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bogota_cumple_total1h_sinRp["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP_bog.add_trace(go.Scatter(x=bogota_cumple_total90min_sinRp["Mes_Orden"],y=bogota_cumple_total90min_sinRp["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bogota_cumple_total90min_sinRp["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP_bog.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_sinRP_bog.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP_bog.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP_bquilla = go.Figure()
fig_Cumpletotal_sinRP_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total1h_sinRp["Mes_Orden"],y=bquilla_cumple_total1h_sinRp["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bquilla_cumple_total1h_sinRp["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total90min_sinRp["Mes_Orden"],y=bquilla_cumple_total90min_sinRp["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bquilla_cumple_total90min_sinRp["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP_bquilla.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_sinRP_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP_bquilla.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP_cali = go.Figure()
fig_Cumpletotal_sinRP_cali.add_trace(go.Scatter(x=cali_cumple_total1h_sinRp["Mes_Orden"],y=cali_cumple_total1h_sinRp["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=cali_cumple_total1h_sinRp["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP_cali.add_trace(go.Scatter(x=cali_cumple_total90min_sinRp["Mes_Orden"],y=cali_cumple_total90min_sinRp["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=cali_cumple_total90min_sinRp["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP_cali.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_sinRP_cali.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP_cali.update_traces(textfont_size=10)


fig_Cumpletotal_sinRP_med = go.Figure()
fig_Cumpletotal_sinRP_med.add_trace(go.Scatter(x=medellin_cumple_total1h_sinRp["Mes_Orden"],y=medellin_cumple_total1h_sinRp["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=medellin_cumple_total1h_sinRp["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP_med.add_trace(go.Scatter(x=medellin_cumple_total90min_sinRp["Mes_Orden"],y=medellin_cumple_total90min_sinRp["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=medellin_cumple_total90min_sinRp["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP_med.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_sinRP_med.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP_med.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP_otros = go.Figure()
fig_Cumpletotal_sinRP_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total1h_sinRp["Mes_Orden"],y=otrasciudades_cumple_total1h_sinRp["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=otrasciudades_cumple_total1h_sinRp["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total90min_sinRp["Mes_Orden"],y=otrasciudades_cumple_total90min_sinRp["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=otrasciudades_cumple_total90min_sinRp["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP_otros.update_yaxes(range=[40,100],title ="(%)")
fig_Cumpletotal_sinRP_otros.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP_med.update_traces(textfont_size=10)


###Figuras Tiempo total promedio filtrando altas reprogramaciones y 6km

fig_Ttotal_sinRp6km_bog = go.Figure()
fig_Ttotal_sinRp6km_bog.add_trace(go.Scatter(x=bogota_TotalSinRP_6km["Mes_Orden"],y=bogota_TotalSinRP_6km["SameDayCall"],name ="Call Center",mode="lines+markers+text",text=bogota_TotalSinRP_6km["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp6km_bog.add_trace(go.Scatter(x=bogota_TotalSinRP_6km["Mes_Orden"],y=bogota_TotalSinRP_6km["SameDayEcomm"],name ="Ecommerce",mode="lines+markers+text",text=bogota_TotalSinRP_6km["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp6km_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp6km_bog.update_yaxes(range=[30,80],title ="Min")
fig_Ttotal_sinRp6km_bog.update_xaxes(dtick=1,title ="Meses")
fig_Ttotal_sinRp6km_bog.update_traces(textfont_size=10)

fig_Ttotal_sinRp6km_bquilla = go.Figure()
fig_Ttotal_sinRp6km_bquilla.add_trace(go.Scatter(x=bquilla_TotalSinRP_6km["Mes_Orden"],y=bquilla_TotalSinRP_6km["SameDayCall"],name="Call Center",mode="lines+markers+text",text=bquilla_TotalSinRP_6km["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp6km_bquilla.add_trace(go.Scatter(x=bquilla_TotalSinRP_6km["Mes_Orden"],y=bquilla_TotalSinRP_6km["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=bquilla_TotalSinRP_6km["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp6km_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp6km_bquilla.update_yaxes(range=[30,80],title ="Min")
fig_Ttotal_sinRp6km_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_Ttotal_sinRp6km_bquilla.update_traces(textfont_size=10)

fig_Ttotal_sinRp6km_cali = go.Figure()
fig_Ttotal_sinRp6km_cali.add_trace(go.Scatter(x=cali_TotalSinRP_6km["Mes_Orden"],y=cali_TotalSinRP_6km["SameDayCall"],name="Call Center",mode="lines+markers+text",text=cali_TotalSinRP_6km["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp6km_cali.add_trace(go.Scatter(x=cali_TotalSinRP_6km["Mes_Orden"],y=cali_TotalSinRP_6km["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=cali_TotalSinRP_6km["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp6km_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp6km_cali.update_yaxes(range=[30,80],title ="Min")
fig_Ttotal_sinRp6km_cali.update_xaxes(dtick=1,title ="Meses")
fig_Ttotal_sinRp6km_cali.update_traces(textfont_size=10)

fig_Ttotal_sinRp6km_med = go.Figure()
fig_Ttotal_sinRp6km_med.add_trace(go.Scatter(x=medellin_TotalSinRP_6km["Mes_Orden"],y=medellin_TotalSinRP_6km["SameDayCall"],name="Call Center",mode="lines+markers+text",text=medellin_TotalSinRP_6km["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp6km_med.add_trace(go.Scatter(x=medellin_TotalSinRP_6km["Mes_Orden"],y=medellin_TotalSinRP_6km["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=medellin_TotalSinRP_6km["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp6km_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp6km_med.update_yaxes(range=[30,80],title ="Min")
fig_Ttotal_sinRp6km_med.update_xaxes(dtick=1,title ="Meses")
fig_Ttotal_sinRp6km_med.update_traces(textfont_size=10)

fig_Ttotal_sinRp6km_otros = go.Figure()
fig_Ttotal_sinRp6km_otros.add_trace(go.Scatter(x=otrasciudades_TotalSinRP_6km["Mes_Orden"],y=otrasciudades_TotalSinRP_6km["SameDayCall"],name="Call Center",mode="lines+markers+text",text=otrasciudades_TotalSinRP_6km["SameDayCall"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Ttotal_sinRp6km_otros.add_trace(go.Scatter(x=otrasciudades_TotalSinRP_6km["Mes_Orden"],y=otrasciudades_TotalSinRP_6km["SameDayEcomm"],name="Ecommerce",mode="lines+markers+text",text=otrasciudades_TotalSinRP_6km["SameDayEcomm"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Ttotal_sinRp6km_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Ttotal_sinRp6km_otros.update_yaxes(range=[30,80],title ="Min")
fig_Ttotal_sinRp6km_otros.update_xaxes(dtick=1,title ="Meses")
fig_Ttotal_sinRp6km_otros.update_traces(textfont_size=10)

###Figuras cumplimiento 1h y 90min filtrando altas reprogramaciones y 6km

fig_Cumpletotal_sinRP6km_bog = go.Figure()
fig_Cumpletotal_sinRP6km_bog.add_trace(go.Scatter(x=bogota_cumple_total1h_sinRp_6km["Mes_Orden"],y=bogota_cumple_total1h_sinRp_6km["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bogota_cumple_total1h_sinRp_6km["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP6km_bog.add_trace(go.Scatter(x=bogota_cumple_total90min_sinRp_6km["Mes_Orden"],y=bogota_cumple_total90min_sinRp_6km["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bogota_cumple_total90min_sinRp_6km["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP6km_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP6km_bog.update_yaxes(range=[50,100],title ="(%)")
fig_Cumpletotal_sinRP6km_bog.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP6km_bog.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP6km_bquilla = go.Figure()
fig_Cumpletotal_sinRP6km_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total1h_sinRp_6km["Mes_Orden"],y=bquilla_cumple_total1h_sinRp_6km["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=bquilla_cumple_total1h_sinRp_6km["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP6km_bquilla.add_trace(go.Scatter(x=bquilla_cumple_total90min_sinRp_6km["Mes_Orden"],y=bquilla_cumple_total90min_sinRp_6km["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=bquilla_cumple_total90min_sinRp_6km["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP6km_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP6km_bquilla.update_yaxes(range=[50,100],title ="(%)")
fig_Cumpletotal_sinRP6km_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP6km_bquilla.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP6km_cali = go.Figure()
fig_Cumpletotal_sinRP6km_cali.add_trace(go.Scatter(x=cali_cumple_total1h_sinRp_6km["Mes_Orden"],y=cali_cumple_total1h_sinRp_6km["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=cali_cumple_total1h_sinRp_6km["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP6km_cali.add_trace(go.Scatter(x=cali_cumple_total90min_sinRp_6km["Mes_Orden"],y=cali_cumple_total90min_sinRp_6km["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=cali_cumple_total90min_sinRp_6km["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP6km_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP6km_cali.update_yaxes(range=[50,100],title ="(%)")
fig_Cumpletotal_sinRP6km_cali.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP6km_cali.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP6km_med = go.Figure()
fig_Cumpletotal_sinRP6km_med.add_trace(go.Scatter(x=medellin_cumple_total1h_sinRp_6km["Mes_Orden"],y=medellin_cumple_total1h_sinRp_6km["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=medellin_cumple_total1h_sinRp_6km["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP6km_med.add_trace(go.Scatter(x=medellin_cumple_total90min_sinRp_6km["Mes_Orden"],y=medellin_cumple_total90min_sinRp_6km["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=medellin_cumple_total90min_sinRp_6km["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP6km_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP6km_med.update_yaxes(range=[50,100],title ="(%)")
fig_Cumpletotal_sinRP6km_med.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP6km_med.update_traces(textfont_size=10)

fig_Cumpletotal_sinRP6km_otros = go.Figure()
fig_Cumpletotal_sinRP6km_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total1h_sinRp_6km["Mes_Orden"],y=otrasciudades_cumple_total1h_sinRp_6km["Cumplimiento"],name ="1 hora",mode="lines+markers+text",text=otrasciudades_cumple_total1h_sinRp_6km["Cumplimiento"],textposition="middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_Cumpletotal_sinRP6km_otros.add_trace(go.Scatter(x=otrasciudades_cumple_total90min_sinRp_6km["Mes_Orden"],y=otrasciudades_cumple_total90min_sinRp_6km["Cumplimiento"],name ="90 minutos",mode="lines+markers+text",text=otrasciudades_cumple_total90min_sinRp_6km["Cumplimiento"],textposition="middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_Cumpletotal_sinRP6km_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_Cumpletotal_sinRP6km_otros.update_yaxes(range=[50,100],title ="(%)")
fig_Cumpletotal_sinRP6km_otros.update_xaxes(dtick=1,title ="Meses")
fig_Cumpletotal_sinRP6km_otros.update_traces(textfont_size=10)

###Figuras Tiempo UM promedio filtrando altas reprogramaciones

fig_tiempoUM_sinRP_bog = go.Figure()
fig_tiempoUM_sinRP_bog.add_trace(go.Scatter(x =bogotaUM_sinRP["Mes_Orden"],y =bogotaUM_sinRP["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = bogotaUM_sinRP["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP_bog.add_trace(go.Scatter(x =bogotaUM_sinRP["Mes_Orden"],y =bogotaUM_sinRP["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = bogotaUM_sinRP["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP_bog.update_yaxes(range=[15,65],title ="Min")
fig_tiempoUM_sinRP_bog.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP_bog.update_traces(textfont_size=10)

fig_tiempoUM_sinRP_bquilla = go.Figure()
fig_tiempoUM_sinRP_bquilla.add_trace(go.Scatter(x =bquillaUM_sinRP["Mes_Orden"],y = bquillaUM_sinRP["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = bquillaUM_sinRP["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP_bquilla.add_trace(go.Scatter(x = bquillaUM_sinRP["Mes_Orden"],y =bquillaUM_sinRP["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = bquillaUM_sinRP["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP_bquilla.update_yaxes(range=[15,65],title ="Min")
fig_tiempoUM_sinRP_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP_bquilla.update_traces(textfont_size=10)

fig_tiempoUM_sinRP_cali = go.Figure()
fig_tiempoUM_sinRP_cali.add_trace(go.Scatter(x =caliUM_sinRP["Mes_Orden"],y = caliUM_sinRP["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = caliUM_sinRP["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP_cali.add_trace(go.Scatter(x = caliUM_sinRP["Mes_Orden"],y = caliUM_sinRP["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = caliUM_sinRP["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP_cali.update_yaxes(range=[15,65],title ="Min")
fig_tiempoUM_sinRP_cali.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP_cali.update_traces(textfont_size=10)

fig_tiempoUM_sinRP_med = go.Figure()
fig_tiempoUM_sinRP_med.add_trace(go.Scatter(x =medellinUM_sinRP["Mes_Orden"],y = medellinUM_sinRP["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = medellinUM_sinRP["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP_med.add_trace(go.Scatter(x = medellinUM_sinRP["Mes_Orden"],y = medellinUM_sinRP["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = medellinUM_sinRP["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP_med.update_yaxes(range=[15,65],title ="Min")
fig_tiempoUM_sinRP_med.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP_med.update_traces(textfont_size=10)

fig_tiempoUM_sinRP_otros = go.Figure()
fig_tiempoUM_sinRP_otros.add_trace(go.Scatter(x = otrasciudadesUM_sinRP["Mes_Orden"],y = otrasciudadesUM_sinRP["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = otrasciudadesUM_sinRP["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP_otros.add_trace(go.Scatter(x = otrasciudadesUM_sinRP["Mes_Orden"],y = otrasciudadesUM_sinRP["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = otrasciudadesUM_sinRP["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP_otros.update_yaxes(range=[15,65],title ="Min")
fig_tiempoUM_sinRP_otros.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP_otros.update_traces(textfont_size=10)
                                    
###Figuras Cumplimiento UM promedio filtrando altas reprogramaciones

fig_cumpleUM_sinRp_bog = go.Figure()
fig_cumpleUM_sinRp_bog.add_trace(go.Scatter(x = bogota_cumpleUM_sinRp["Mes_Orden"],y =bogota_cumpleUM_sinRp["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = bogota_cumpleUM_sinRp["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp_bog.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp_bog.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp_bog.update_traces(textfont_size=10)
                                      

fig_cumpleUM_sinRp_bquilla = go.Figure()
fig_cumpleUM_sinRp_bquilla.add_trace(go.Scatter(x = bquilla_cumpleUM_sinRp["Mes_Orden"],y =bquilla_cumpleUM_sinRp["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = bquilla_cumpleUM_sinRp["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp_bquilla.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp_bquilla.update_traces(textfont_size=10)

fig_cumpleUM_sinRp_cali = go.Figure()
fig_cumpleUM_sinRp_cali.add_trace(go.Scatter(x = cali_cumpleUM_sinRp["Mes_Orden"],y =cali_cumpleUM_sinRp["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = cali_cumpleUM_sinRp["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp_cali.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp_cali.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp_cali.update_traces(textfont_size=10)

fig_cumpleUM_sinRp_med = go.Figure()
fig_cumpleUM_sinRp_med.add_trace(go.Scatter(x = medellin_cumpleUM_sinRp["Mes_Orden"],y =medellin_cumpleUM_sinRp["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = medellin_cumpleUM_sinRp["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp_med.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp_med.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp_med.update_traces(textfont_size=10)

fig_cumpleUM_sinRp_otros = go.Figure()
fig_cumpleUM_sinRp_otros.add_trace(go.Scatter(x = otrasciudades_cumpleUM_sinRp["Mes_Orden"],y = otrasciudades_cumpleUM_sinRp["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = otrasciudades_cumpleUM_sinRp["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp_otros.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp_otros.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp_otros.update_traces(textfont_size=10)

###Figuras Tiempo UM promedio filtrando altas reprogramaciones y 6km

fig_tiempoUM_sinRP6km_bog = go.Figure()
fig_tiempoUM_sinRP6km_bog.add_trace(go.Scatter(x =bogotaUM_sinRp_6km["Mes_Orden"],y =bogotaUM_sinRp_6km["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = bogotaUM_sinRp_6km["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP6km_bog.add_trace(go.Scatter(x =bogotaUM_sinRp_6km["Mes_Orden"],y =bogotaUM_sinRp_6km["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = bogotaUM_sinRp_6km["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP6km_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP6km_bog.update_yaxes(range=[10,60],title ="Min")
fig_tiempoUM_sinRP6km_bog.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP6km_bog.update_traces(textfont_size=10)

fig_tiempoUM_sinRP6km_bquilla = go.Figure()
fig_tiempoUM_sinRP6km_bquilla.add_trace(go.Scatter(x =bquillaUM_sinRp_6km["Mes_Orden"],y = bquillaUM_sinRp_6km["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = bquillaUM_sinRp_6km["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP6km_bquilla.add_trace(go.Scatter(x =bquillaUM_sinRp_6km["Mes_Orden"],y = bquillaUM_sinRp_6km["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = bquillaUM_sinRp_6km["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP6km_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP6km_bquilla.update_yaxes(range=[10,60],title ="Min")
fig_tiempoUM_sinRP6km_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP6km_bquilla.update_traces(textfont_size=10)

fig_tiempoUM_sinRP6km_cali = go.Figure()
fig_tiempoUM_sinRP6km_cali.add_trace(go.Scatter(x =caliUM_sinRp_6km["Mes_Orden"],y = caliUM_sinRp_6km["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = caliUM_sinRp_6km["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP6km_cali.add_trace(go.Scatter(x = caliUM_sinRp_6km["Mes_Orden"],y = caliUM_sinRp_6km["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = caliUM_sinRp_6km["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP6km_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP6km_cali.update_yaxes(range=[10,60],title ="Min")
fig_tiempoUM_sinRP6km_cali.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP6km_cali.update_traces(textfont_size=10)

fig_tiempoUM_sinRP6km_med = go.Figure()
fig_tiempoUM_sinRP6km_med.add_trace(go.Scatter(x =medellinUM_sinRp_6km["Mes_Orden"],y = medellinUM_sinRp_6km["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = medellinUM_sinRp_6km["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP6km_med.add_trace(go.Scatter(x = medellinUM_sinRp_6km["Mes_Orden"],y = medellinUM_sinRp_6km["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = medellinUM_sinRp_6km["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP6km_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP6km_med.update_yaxes(range=[10,60],title ="Min")
fig_tiempoUM_sinRP6km_med.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP6km_med.update_traces(textfont_size=10)

fig_tiempoUM_sinRP6km_otros = go.Figure()
fig_tiempoUM_sinRP6km_otros.add_trace(go.Scatter(x = otrasciudadesUM_sinRp_6km["Mes_Orden"],y = otrasciudadesUM_sinRp_6km["SameDayCall"], name = "Call Center", mode = "lines+markers+text", text = otrasciudadesUM_sinRp_6km["SameDayCall"], textposition = "middle right",line=dict(color='rgb(0,176,80)',width=2)))
fig_tiempoUM_sinRP6km_otros.add_trace(go.Scatter(x = otrasciudadesUM_sinRp_6km["Mes_Orden"],y = otrasciudadesUM_sinRp_6km["SameDayEcomm"], name = "Ecommerce", mode = "lines+markers+text", text = otrasciudadesUM_sinRp_6km["SameDayEcomm"], textposition = "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_tiempoUM_sinRP6km_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoUM_sinRP6km_otros.update_yaxes(range=[10,60],title ="(%)")
fig_tiempoUM_sinRP6km_otros.update_xaxes(dtick=1,title ="Meses")
fig_tiempoUM_sinRP6km_otros.update_traces(textfont_size=10)

###Figuras Cumplimiento UM promedio filtrando altas reprogramaciones y 6km

fig_cumpleUM_sinRp6km_bog = go.Figure()
fig_cumpleUM_sinRp6km_bog.add_trace(go.Scatter(x = bogota_cumpleUM_sinRp_6km["Mes_Orden"],y =bogota_cumpleUM_sinRp_6km["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = bogota_cumpleUM_sinRp_6km["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp6km_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp6km_bog.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp6km_bog.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp6km_bog.update_traces(textfont_size=10)

fig_cumpleUM_sinRp6km_bquilla = go.Figure()
fig_cumpleUM_sinRp6km_bquilla.add_trace(go.Scatter(x = bquilla_cumpleUM_sinRp_6km["Mes_Orden"],y = bquilla_cumpleUM_sinRp_6km["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = bquilla_cumpleUM_sinRp_6km["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp6km_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp6km_bquilla.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp6km_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp6km_bquilla.update_traces(textfont_size=10)

fig_cumpleUM_sinRp6km_cali = go.Figure()
fig_cumpleUM_sinRp6km_cali.add_trace(go.Scatter(x = cali_cumpleUM_sinRp_6km["Mes_Orden"],y =cali_cumpleUM_sinRp_6km["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = cali_cumpleUM_sinRp_6km["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp6km_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp6km_cali.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp6km_cali.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp6km_cali.update_traces(textfont_size=10)

fig_cumpleUM_sinRp6km_med = go.Figure()
fig_cumpleUM_sinRp6km_med.add_trace(go.Scatter(x = medellin_cumpleUM_sinRp_6km["Mes_Orden"],y =medellin_cumpleUM_sinRp_6km["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = medellin_cumpleUM_sinRp_6km["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp6km_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp6km_med.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp6km_med.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp6km_med.update_traces(textfont_size=10)

fig_cumpleUM_sinRp6km_otros = go.Figure()
fig_cumpleUM_sinRp6km_otros.add_trace(go.Scatter(x = otrosciudades_cumpleUM_sinRp_6km["Mes_Orden"],y = otrosciudades_cumpleUM_sinRp_6km["Cumplimiento"],name = "40 minutos", mode = "lines+markers+text", text = otrosciudades_cumpleUM_sinRp_6km["Cumplimiento"],textposition ="middle center", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumpleUM_sinRp6km_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumpleUM_sinRp6km_otros.update_yaxes(range=[40,100],title ="(%)")
fig_cumpleUM_sinRp6km_otros.update_xaxes(dtick=1,title ="Meses")
fig_cumpleUM_sinRp6km_otros.update_traces(textfont_size=10)


###Figuras %kilometraje menor a 6 km

fig_bogotakm = go.Figure()
fig_bogotakm.add_trace(go.Scatter(x = bogotakm["Mes_Orden"], y = bogotakm["PorcMenor6km"],name ="% ordenes menores a 6km",mode ="lines+markers+text", text = bogotakm["PorcMenor6km"],textposition ="middle center",line = dict(color='rgb(0,176,80)',width =2 )))
fig_bogotakm.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_bogotakm.update_yaxes(range=[50,100],title ="(%)")
fig_bogotakm.update_xaxes(dtick=1,title ="Meses")
fig_bogotakm.update_traces(textfont_size=10)

fig_bquillakm = go.Figure()
fig_bquillakm.add_trace(go.Scatter(x = bquillakm["Mes_Orden"], y = bquillakm["PorcMenor6km"],name ="% ordenes menores a 6km",mode ="lines+markers+text", text = bquillakm["PorcMenor6km"],textposition ="middle center",line = dict(color='rgb(0,176,80)',width =2 )))
fig_bquillakm.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_bquillakm.update_yaxes(range=[50,100],title ="(%)")
fig_bquillakm.update_xaxes(dtick=1,title ="Meses")
fig_bquillakm.update_traces(textfont_size=10)

fig_calikm = go.Figure()
fig_calikm.add_trace(go.Scatter(x = calikm["Mes_Orden"], y = calikm["PorcMenor6km"],name ="% ordenes menores a 6km",mode ="lines+markers+text" ,text = calikm["PorcMenor6km"],textposition ="middle center",line = dict(color='rgb(0,176,80)',width =2 )))
fig_calikm.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_calikm.update_yaxes(range=[50,100],title ="(%)")
fig_calikm.update_xaxes(dtick=1,title ="Meses")
fig_calikm.update_traces(textfont_size=10)

fig_medellinkm = go.Figure()
fig_medellinkm.add_trace(go.Scatter(x = medellinkm["Mes_Orden"], y = medellinkm["PorcMenor6km"],name ="% ordenes menores a 6km",mode ="lines+markers+text", text = medellinkm["PorcMenor6km"],textposition ="middle center",line = dict(color='rgb(0,176,80)',width =2 )))
fig_medellinkm.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_medellinkm.update_yaxes(range=[50,100],title ="(%)")
fig_medellinkm.update_xaxes(dtick=1,title ="Meses")
fig_medellinkm.update_traces(textfont_size=10)


fig_otrasciudadeskm = go.Figure()
fig_otrasciudadeskm.add_trace(go.Scatter(x = otrasciudadeskm["Mes_Orden"], y = otrasciudadeskm["PorcMenor6km"],name ="% ordenes menores a 6km",mode ="lines+markers+text" ,text = otrasciudadeskm["PorcMenor6km"],textposition ="middle center",line = dict(color='rgb(0,176,80)',width =2 )))
fig_otrasciudadeskm.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_otrasciudadeskm.update_yaxes(range=[50,100],title ="(%)")
fig_otrasciudadeskm.update_xaxes(dtick=1,title ="Meses")
fig_otrasciudadeskm.update_traces(textfont_size=10)


###Figuras % saltos por quiebre y tiempo 


fig_saltos_bog = go.Figure()
fig_saltos_bog.add_trace(go.Scatter(x = bogota_saltos["Mes_Orden"],y = bogota_saltos["Porc Saltos Quiebre"],name = "% Saltos por quiebre", mode = "lines+markers+text",text = bogota_saltos["Porc Saltos Quiebre"], textposition ="middle right",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_saltos_bog.add_trace(go.Scatter(x = bogota_saltos["Mes_Orden"],y = bogota_saltos["Porc Saltos Tiempo"], name = "% Saltos por tiempo", mode = "lines+markers+text",text = bogota_saltos["Porc Saltos Tiempo"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_saltos_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_saltos_bog.update_yaxes(range=[0,25],title ="(%)")
fig_saltos_bog.update_xaxes(dtick=1,title ="Meses")
fig_saltos_bog.update_traces(textfont_size=10)

fig_saltos_bquilla = go.Figure()
fig_saltos_bquilla.add_trace(go.Scatter(x = bquilla_saltos["Mes_Orden"],y = bquilla_saltos["Porc Saltos Quiebre"],name = "% Saltos por quiebre", mode = "lines+markers+text",text = bquilla_saltos["Porc Saltos Quiebre"], textposition ="middle right",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_saltos_bquilla.add_trace(go.Scatter(x = bquilla_saltos["Mes_Orden"],y = bquilla_saltos["Porc Saltos Tiempo"], name = "% Saltos por tiempo", mode = "lines+markers+text",text = bquilla_saltos["Porc Saltos Tiempo"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_saltos_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_saltos_bquilla.update_yaxes(range=[0,25],title ="(%)")
fig_saltos_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_saltos_bquilla.update_traces(textfont_size=10)

fig_saltos_cali = go.Figure()
fig_saltos_cali.add_trace(go.Scatter(x = cali_saltos["Mes_Orden"],y = cali_saltos["Porc Saltos Quiebre"],name = "% Saltos por quiebre", mode = "lines+markers+text",text = cali_saltos["Porc Saltos Quiebre"], textposition ="middle right",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_saltos_cali.add_trace(go.Scatter(x = cali_saltos["Mes_Orden"],y = cali_saltos["Porc Saltos Tiempo"], name = "% Saltos por tiempo", mode = "lines+markers+text",text = cali_saltos["Porc Saltos Tiempo"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_saltos_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_saltos_cali.update_yaxes(range=[0,25],title ="(%)")
fig_saltos_cali.update_xaxes(dtick=1,title ="Meses")
fig_saltos_cali.update_traces(textfont_size=10)

fig_saltos_med = go.Figure()
fig_saltos_med.add_trace(go.Scatter(x = medellin_saltos["Mes_Orden"],y = medellin_saltos["Porc Saltos Quiebre"],name = "% Saltos por quiebre", mode = "lines+markers+text",text = medellin_saltos["Porc Saltos Quiebre"], textposition ="middle right",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_saltos_med.add_trace(go.Scatter(x = medellin_saltos["Mes_Orden"],y = medellin_saltos["Porc Saltos Tiempo"], name = "% Saltos por tiempo", mode = "lines+markers+text",text = medellin_saltos["Porc Saltos Tiempo"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_saltos_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_saltos_med.update_yaxes(range=[0,25],title ="(%)")
fig_saltos_med.update_xaxes(dtick=1,title ="Meses")
fig_saltos_med.update_traces(textfont_size=10)

fig_saltos_otros = go.Figure()
fig_saltos_otros.add_trace(go.Scatter(x = otrasciudades_saltos["Mes_Orden"],y = otrasciudades_saltos["Porc Saltos Quiebre"],name = "% Saltos por quiebre", mode = "lines+markers+text",text = otrasciudades_saltos["Porc Saltos Quiebre"], textposition ="middle right",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_saltos_otros.add_trace(go.Scatter(x = otrasciudades_saltos["Mes_Orden"],y = otrasciudades_saltos["Porc Saltos Tiempo"], name = "% Saltos por tiempo", mode = "lines+markers+text",text = otrasciudades_saltos["Porc Saltos Tiempo"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_saltos_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_saltos_otros.update_yaxes(range=[0,25],title ="(%)")
fig_saltos_otros.update_xaxes(dtick=1,title ="Meses")
fig_saltos_otros.update_traces(textfont_size=10)

###Figuras tiempo de alistamiento primer y ultimo readyforbackroompick

fig_tiempoalistamiento_bog = go.Figure()
fig_tiempoalistamiento_bog.add_trace(go.Scatter(x =bogotaprimerRFBP["Mes_Orden"], y = bogotaprimerRFBP["Alistamiento_SameDay"],name = "Alistamiento Primer_Rfbp", mode = "lines+markers+text",text = bogotaprimerRFBP["Alistamiento_SameDay"], textposition = "middle right",line = dict(color = 'rgb(0,176,80)',width=2)))
fig_tiempoalistamiento_bog.add_trace(go.Scatter(x =bogotaultimoRFBP["Mes_Orden"], y = bogotaultimoRFBP["Alistamiento_SameDay"],name = "Alistamiento Último_Rfbp", mode = "lines+markers+text",text = bogotaultimoRFBP["Alistamiento_SameDay"], textposition = "middle center",line = dict(color = 'rgb(255,192,0)',width=2)))
fig_tiempoalistamiento_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoalistamiento_bog.update_yaxes(range=[0,50],title ="Min")
fig_tiempoalistamiento_bog.update_xaxes(dtick=1,title ="Meses")
fig_tiempoalistamiento_bog.update_traces(textfont_size=10)

fig_tiempoalistamiento_bquilla = go.Figure()
fig_tiempoalistamiento_bquilla.add_trace(go.Scatter(x =bquillaprimerRFBP["Mes_Orden"], y = bquillaprimerRFBP["Alistamiento_SameDay"],name = "Alistamiento Primer_Rfbp", mode = "lines+markers+text",text = bquillaprimerRFBP["Alistamiento_SameDay"], textposition = "middle right",line = dict(color = 'rgb(0,176,80)',width=2)))
fig_tiempoalistamiento_bquilla.add_trace(go.Scatter(x =bquillaultimoRFBP["Mes_Orden"], y = bquillaultimoRFBP["Alistamiento_SameDay"],name = "Alistamiento Último_Rfbp", mode = "lines+markers+text",text = bquillaultimoRFBP["Alistamiento_SameDay"], textposition = "middle center",line = dict(color = 'rgb(255,192,0)',width=2)))
fig_tiempoalistamiento_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoalistamiento_bquilla.update_yaxes(range=[0,50],title ="Min")
fig_tiempoalistamiento_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_tiempoalistamiento_bquilla.update_traces(textfont_size=10)

fig_tiempoalistamiento_cali = go.Figure()
fig_tiempoalistamiento_cali.add_trace(go.Scatter(x =caliprimerRFBP["Mes_Orden"], y = caliprimerRFBP["Alistamiento_SameDay"],name = "Alistamiento Primer_Rfbp", mode = "lines+markers+text",text = caliprimerRFBP["Alistamiento_SameDay"], textposition = "middle right",line = dict(color = 'rgb(0,176,80)',width=2)))
fig_tiempoalistamiento_cali.add_trace(go.Scatter(x =caliultimoRFBP["Mes_Orden"], y = caliultimoRFBP["Alistamiento_SameDay"],name = "Alistamiento Último_Rfbp", mode = "lines+markers+text",text = caliultimoRFBP["Alistamiento_SameDay"], textposition = "middle center",line = dict(color = 'rgb(255,192,0)',width=2)))
fig_tiempoalistamiento_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoalistamiento_cali.update_yaxes(range=[0,50],title ="Min")
fig_tiempoalistamiento_cali.update_xaxes(dtick=1,title ="Meses")
fig_tiempoalistamiento_cali.update_traces(textfont_size=10)

fig_tiempoalistamiento_med = go.Figure()
fig_tiempoalistamiento_med.add_trace(go.Scatter(x =medellinprimerRFBP["Mes_Orden"], y = medellinprimerRFBP["Alistamiento_SameDay"],name = "Alistamiento Primer_Rfbp", mode = "lines+markers+text",text = medellinprimerRFBP["Alistamiento_SameDay"], textposition = "middle right",line = dict(color = 'rgb(0,176,80)',width=2)))
fig_tiempoalistamiento_med.add_trace(go.Scatter(x =medellinultimoRFBP["Mes_Orden"], y = medellinultimoRFBP["Alistamiento_SameDay"],name = "Alistamiento Último_Rfbp", mode = "lines+markers+text",text = medellinultimoRFBP["Alistamiento_SameDay"], textposition = "middle center",line = dict(color = 'rgb(255,192,0)',width=2)))
fig_tiempoalistamiento_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoalistamiento_med.update_yaxes(range=[0,50],title ="Min")
fig_tiempoalistamiento_med.update_xaxes(dtick=1,title ="Meses")
fig_tiempoalistamiento_med.update_traces(textfont_size=10)

fig_tiempoalistamiento_otras = go.Figure()
fig_tiempoalistamiento_otras.add_trace(go.Scatter(x =otrasprimerRFBP["Mes_Orden"], y = otrasprimerRFBP["Alistamiento_SameDay"],name = "Alistamiento Primer_Rfbp", mode = "lines+markers+text",text = otrasprimerRFBP["Alistamiento_SameDay"], textposition = "middle right",line = dict(color = 'rgb(0,176,80)',width=2)))
fig_tiempoalistamiento_otras.add_trace(go.Scatter(x =otrasultimoRFBP["Mes_Orden"], y = otrasultimoRFBP["Alistamiento_SameDay"],name = "Alistamiento Último_Rfbp", mode = "lines+markers+text",text = otrasultimoRFBP["Alistamiento_SameDay"], textposition = "middle center",line = dict(color = 'rgb(255,192,0)',width=2)))
fig_tiempoalistamiento_otras.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_tiempoalistamiento_otras.update_yaxes(range=[0,50],title ="Min")
fig_tiempoalistamiento_otras.update_xaxes(dtick=1,title ="Meses")
fig_tiempoalistamiento_otras.update_traces(textfont_size=10)

###Cumplimiento de alistamiento 3 min

fig_cumple3min_bog = go.Figure()
fig_cumple3min_bog.add_trace(go.Scatter(x=bogotaCumple3min["Mes_Orden"], y=bogotaCumple3min["Cumplimiento3min"],name ="Cumplimiento3min", mode = "lines+markers+text", text = bogotaCumple3min["Cumplimiento3min"], textposition = "middle center",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumple3min_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumple3min_bog.update_yaxes(range=[10,100],title ="(%)")
fig_cumple3min_bog.update_xaxes(dtick=1,title ="Meses")
fig_cumple3min_bog.update_traces(textfont_size=10)

fig_cumple3min_bquilla = go.Figure()
fig_cumple3min_bquilla.add_trace(go.Scatter(x=bquillaCumple3min["Mes_Orden"], y=bquillaCumple3min["Cumplimiento3min"],name ="Cumplimiento3min", mode = "lines+markers+text", text = bquillaCumple3min["Cumplimiento3min"], textposition = "middle center",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumple3min_bquilla.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumple3min_bquilla.update_yaxes(range=[10,100],title ="(%)")
fig_cumple3min_bquilla.update_xaxes(dtick=1,title ="Meses")
fig_cumple3min_bquilla.update_traces(textfont_size=10)

fig_cumple3min_cali = go.Figure()
fig_cumple3min_cali.add_trace(go.Scatter(x=caliCumple3min["Mes_Orden"], y=caliCumple3min["Cumplimiento3min"],name ="Cumplimiento3min", mode = "lines+markers+text", text = caliCumple3min["Cumplimiento3min"], textposition = "middle center",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumple3min_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumple3min_cali.update_yaxes(range=[10,100],title ="(%)")
fig_cumple3min_cali.update_xaxes(dtick=1,title ="Meses")
fig_cumple3min_cali.update_traces(textfont_size=10)

fig_cumple3min_medellin = go.Figure()
fig_cumple3min_medellin.add_trace(go.Scatter(x=medellinCumple3min["Mes_Orden"], y=medellinCumple3min["Cumplimiento3min"],name ="Cumplimiento3min", mode = "lines+markers+text", text = medellinCumple3min["Cumplimiento3min"], textposition = "middle center",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumple3min_medellin.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumple3min_medellin.update_yaxes(range=[10,100],title ="(%)")
fig_cumple3min_medellin.update_xaxes(dtick=1,title ="Meses")
fig_cumple3min_medellin.update_traces(textfont_size=10)

fig_cumple3min_otras = go.Figure()
fig_cumple3min_otras.add_trace(go.Scatter(x=otrasCumple3min["Mes_Orden"], y=otrasCumple3min["Cumplimiento3min"],name ="Cumplimiento3min", mode = "lines+markers+text", text = otrasCumple3min["Cumplimiento3min"], textposition = "middle center",line = dict(color = 'rgb(0,176,80)',width =2)))
fig_cumple3min_otras.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cumple3min_otras.update_yaxes(range=[10,100],title ="(%)")
fig_cumple3min_otras.update_xaxes(dtick=1,title ="Meses")
fig_cumple3min_otras.update_traces(textfont_size=10)


### Figuras cancelados y devoluciones

fig_canc_gral = go.Figure()
fig_canc_gral.add_trace(go.Scatter(x = cancelados_dev_gral["Mes_Orden"], y = cancelados_dev_gral["Call Porc Cancelados"], name = "% Cancelados Call", mode = "lines+markers+text",text =cancelados_dev_gral["Call Porc Cancelados"], textposition = "middle right", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_canc_gral.add_trace(go.Scatter(x = cancelados_dev_gral["Mes_Orden"], y = cancelados_dev_gral["Ecomm Porc Cancelados"], name = "% Cancelados Ecomm", mode = "lines+markers+text",text =cancelados_dev_gral["Ecomm Porc Cancelados"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_canc_gral.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_gral.update_yaxes(range=[0,15],title ="(%)")
fig_canc_gral.update_xaxes(dtick=1,title ="Meses")
fig_canc_gral.update_traces(textfont_size=10)

fig_dev_gral = go.Figure()
fig_dev_gral.add_trace(go.Scatter(x = cancelados_dev_gral["Mes_Orden"], y = cancelados_dev_gral["Call Porc Dev"], name = "% Devoluciones Call", mode = "lines+markers+text",text =cancelados_dev_gral["Call Porc Dev"], textposition = "middle right", line = dict(color = 'rgb(0,176,80)',width =2)))
fig_dev_gral.add_trace(go.Scatter(x = cancelados_dev_gral["Mes_Orden"], y = cancelados_dev_gral["Ecomm Porc Dev"], name = "% Devoluciones Ecomm", mode = "lines+markers+text",text =cancelados_dev_gral["Ecomm Porc Dev"], textposition = "middle center", line = dict(color = 'rgb(255,192,0)',width =2)))
fig_dev_gral.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_dev_gral.update_yaxes(range=[0,15],title ="(%)")
fig_dev_gral.update_xaxes(dtick=1,title ="Meses")
fig_dev_gral.update_traces(textfont_size=10)


###Figura responsables cancelaciones
fig_responsables_cancelados = go.Figure(data = [go.Table(header = dict(values = list(porcentajes_.columns),font_size = 10,fill_color = 'lightgray'),
                                                       cells = dict(values = np.transpose(porcentajes_.values), font_size = 10, fill_color = 'rgba(242,242,242)'))])


fig_responsables_cancelados.update_layout(margin = dict(l=20,r=20,t=20,b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_responsables_cancelados.update_layout(width=1215, height=333)


### Figuras Cancelados y devoluciones por ciudad

fig_canc_dev_bog = go.Figure()
fig_canc_dev_bog.add_trace(go.Scatter(x = bogota_cancelados["Mes_Orden"],y = bogota_cancelados["Porc Cancelados"], name = "% Cancelados", mode = "lines+markers+text", text = bogota_cancelados["Porc Cancelados"], textposition ="middle right", line = dict(color ='rgb(0,176,80)', width = 2)))
fig_canc_dev_bog.add_trace(go.Scatter(x = bogota_cancelados["Mes_Orden"],y = bogota_cancelados["Porc Devoluciones"], name = "% Devoluciones", mode = "lines+markers+text", text = bogota_cancelados["Porc Devoluciones"], textposition ="middle center", line = dict(color ='rgb(255,192,0)', width = 2)))
fig_canc_dev_bog.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_dev_bog.update_yaxes(range=[0,25],title ="(%)")
fig_canc_dev_bog.update_xaxes(dtick=1,title ="Meses")
fig_canc_dev_bog.update_traces(textfont_size=10)

fig_canc_dev_baq = go.Figure()
fig_canc_dev_baq.add_trace(go.Scatter(x = bquilla_cancelados["Mes_Orden"],y = bquilla_cancelados["Porc Cancelados"], name = "% Cancelados", mode = "lines+markers+text", text = bquilla_cancelados["Porc Cancelados"], textposition ="middle right", line = dict(color ='rgb(0,176,80)', width = 2)))
fig_canc_dev_baq.add_trace(go.Scatter(x = bquilla_cancelados["Mes_Orden"],y = bquilla_cancelados["Porc Devoluciones"], name = "% Devoluciones", mode = "lines+markers+text", text = bquilla_cancelados["Porc Devoluciones"], textposition ="middle center", line = dict(color ='rgb(255,192,0)', width = 2)))
fig_canc_dev_baq.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_dev_baq.update_yaxes(range=[0,25],title ="(%)")
fig_canc_dev_baq.update_xaxes(dtick=1,title ="Meses")
fig_canc_dev_baq.update_traces(textfont_size=10)

fig_canc_dev_cali = go.Figure()
fig_canc_dev_cali.add_trace(go.Scatter(x = cali_cancelados["Mes_Orden"],y = cali_cancelados["Porc Cancelados"], name = "% Cancelados", mode = "lines+markers+text", text = cali_cancelados["Porc Cancelados"], textposition ="middle right", line = dict(color ='rgb(0,176,80)', width = 2)))
fig_canc_dev_cali.add_trace(go.Scatter(x = cali_cancelados["Mes_Orden"],y = cali_cancelados["Porc Devoluciones"], name = "% Devoluciones", mode = "lines+markers+text", text = cali_cancelados["Porc Devoluciones"], textposition ="middle center", line = dict(color ='rgb(255,192,0)', width = 2)))
fig_canc_dev_cali.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_dev_cali.update_yaxes(range=[0,25],title ="(%)")
fig_canc_dev_cali.update_xaxes(dtick=1,title ="Meses")
fig_canc_dev_cali.update_traces(textfont_size=10)

fig_canc_dev_med = go.Figure()
fig_canc_dev_med.add_trace(go.Scatter(x = medellin_cancelados["Mes_Orden"],y = medellin_cancelados["Porc Cancelados"], name = "% Cancelados", mode = "lines+markers+text", text = medellin_cancelados["Porc Cancelados"], textposition ="middle right", line = dict(color ='rgb(0,176,80)', width = 2)))
fig_canc_dev_med.add_trace(go.Scatter(x = medellin_cancelados["Mes_Orden"],y = medellin_cancelados["Porc Devoluciones"], name = "% Devoluciones", mode = "lines+markers+text", text = medellin_cancelados["Porc Devoluciones"], textposition ="middle center", line = dict(color ='rgb(255,192,0)', width = 2)))
fig_canc_dev_med.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_dev_med.update_yaxes(range=[0,25],title ="(%)")
fig_canc_dev_med.update_xaxes(dtick=1,title ="Meses")
fig_canc_dev_med.update_traces(textfont_size=10)

fig_canc_dev_otros = go.Figure()
fig_canc_dev_otros.add_trace(go.Scatter(x = otrasciudades_cancelados["Mes_Orden"],y = otrasciudades_cancelados["Porc Cancelados"], name = "% Cancelados", mode = "lines+markers+text", text = otrasciudades_cancelados["Porc Cancelados"], textposition ="middle right", line = dict(color ='rgb(0,176,80)', width = 2)))
fig_canc_dev_otros.add_trace(go.Scatter(x = otrasciudades_cancelados["Mes_Orden"],y = otrasciudades_cancelados["Porc Devoluciones"], name = "% Devoluciones", mode = "lines+markers+text", text = otrasciudades_cancelados["Porc Devoluciones"], textposition ="middle center", line = dict(color ='rgb(255,192,0)', width = 2)))
fig_canc_dev_otros.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_canc_dev_otros.update_yaxes(range=[0,25],title ="(%)")
fig_canc_dev_otros.update_xaxes(dtick=1,title ="Meses")
fig_canc_dev_otros.update_traces(textfont_size=10)

###Cobro de domicilios general
fig_cobro_gral = go.Figure()
fig_cobro_gral.add_trace(go.Scatter(x=cobro_canal["Mes_Cobro"],y=cobro_canal["Total_Cobro"],name="cobro domicilios total",mode ="lines+markers+text",text=cobro_canal["Total_Cobro"],textposition="middle center",line=dict(color='rgb(0,176,80)',width=2)))
fig_cobro_gral.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cobro_gral.update_yaxes(title ="($) COP Milones")
fig_cobro_gral.update_xaxes(title ="Meses")
fig_cobro_gral.update_traces(textfont_size=10)

###Cobro de domicilios por canal
fig_cobro_canal =go.Figure()
fig_cobro_canal.add_trace(go.Scatter(x=cobro_canal["Mes_Cobro"],y=cobro_canal["Domifacil"],name="cobro domifacil",mode ="lines+markers+text",text=cobro_canal["Domifacil"],textposition= "middle center",line=dict(color='rgb(0,176,80)',width=2)))
fig_cobro_canal.add_trace(go.Scatter(x=cobro_canal["Mes_Cobro"],y=cobro_canal["Mostrador"],name="cobro Mostrador",mode ="lines+markers+text",text=cobro_canal["Mostrador"],textposition= "middle center",line=dict(color='rgb(255,192,0)',width=2)))
fig_cobro_canal.add_trace(go.Scatter(x=cobro_canal["Mes_Cobro"],y=cobro_canal["OMS"],name="cobro OMS",mode ="lines+markers+text",text=cobro_canal["OMS"],textposition= "middle center",line=dict(color='rgb(213,112,23)',width=2)))
fig_cobro_canal.update_layout(legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),margin = dict(l=20, r=20, t=40, b=20),paper_bgcolor = 'rgb(232,230,230)')
fig_cobro_canal.update_yaxes(title ="($) COP Millones")
fig_cobro_canal.update_xaxes(title ="Meses")
fig_cobro_canal.update_traces(textfont_size=10)

###Retiro en tieda participación vs ecommerce
fig_ret_venta = make_subplots(specs=[[{"secondary_y": True}]])
fig_ret_venta.add_trace(go.Bar(name="Venta Ret",x=venta_ret_ecomm["Mes_Orden"],y=venta_ret_ecomm["Customer Picked Up"],text=venta_ret_ecomm["Customer Picked Up"],marker_color = 'rgb(0,176,80)'),secondary_y=False)
fig_ret_venta.add_trace(go.Scatter(x=venta_ret_ecomm["Mes_Orden"],y=venta_ret_ecomm["Participacion_ret"],name="participacion ret", mode = "lines+markers+text",text = venta_ret_ecomm["Participacion_ret"],textposition = "middle center",line=dict(color = 'rgb(225,192,0)', width=2)),secondary_y=True)
fig_ret_venta.update_layout(yaxis = dict(showgrid=False),margin = dict(l=20, r=20, t=40, b=20),legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),paper_bgcolor = 'rgb(232,230,230)')
fig_ret_venta.update_xaxes(dtick = 1,title ="Meses")
fig_ret_venta.update_yaxes(title_text = "($) COP Millones",showgrid = False,secondary_y = False)
fig_ret_venta.update_yaxes(title_text = "(%)",showgrid = False, secondary_y = True)
fig_ret_venta.update_traces(textfont_size=10)




###Retiro en tienda ticket vs ecommerce
fig_ticket_ecomm = make_subplots(specs=[[{"secondary_y": True}]])
fig_ticket_ecomm.add_trace(go.Bar(name="Ticket Ret",x=ticket_ret_ecomm["Mes_Orden"],y=ticket_ret_ecomm["Customer Picked Up"],text=ticket_ret_ecomm["Customer Picked Up"],marker_color = 'rgb(0,176,80)'),secondary_y=False)
fig_ticket_ecomm.add_trace(go.Bar(name="Ticket Ecomm",x=ticket_ret_ecomm["Mes_Orden"],y=ticket_ret_ecomm["Delivered To Customer"],text=ticket_ret_ecomm["Delivered To Customer"],marker_color = 'rgba(0,176,80,0.2)'),secondary_y=False)
fig_ticket_ecomm.add_trace(go.Scatter(x=ordenes_ret["Mes_Orden"],y=ordenes_ret["Customer Picked Up"],name="ordenes ret",mode = "lines+markers+text",text = ordenes_ret["Customer Picked Up"],textposition = "middle center",line=dict(color = 'rgb(225,192,0)', width=2)),secondary_y=True)
fig_ticket_ecomm.update_layout(barmode = 'group',margin = dict(l=20, r=20, t=40, b=20),legend = dict( orientation = "h", yanchor = "bottom",xanchor ="center",y=1,x=0.5),paper_bgcolor = 'rgb(232,230,230)')
fig_ticket_ecomm.update_xaxes(dtick = 1,title ="Meses")
fig_ticket_ecomm.update_yaxes(title_text ="($) COP Miles",showgrid = False,secondary_y=False)
fig_ticket_ecomm.update_yaxes(title_text ="Cantidad ordenes (RET)",showgrid = False,secondary_y=True)
fig_ticket_ecomm.update_traces(textfont_size=10)




app = Dash(__name__)

app.layout = html.Div([
    

    html.Div([
        html.Div([
            html.Img(src = "assets/LogoCV.png"),
            html.H1("Negocios digitales Colombia"),
            html.H2("Operaciones Omnicanal")
            ])
        ],className = 'contenedor-titulo'),
    
    html.Div([
        ],className = 'posttitulo-contenedor'),
    
   
    
   
    html.Div([
        html.Div([
        html.H2("Participación por ciudad")],className ='titulo-seccion'),
        html.Div([
            dcc.Graph(id="ParticipaCiudad",figure = fig_participacion)],className = 'create_container2')
        
    ]),
    
    
    ###Tiempos totales sin filtro
    html.Div([
        html.Div([
        html.H2("Tiempos sin filtro")],className = 'titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                    dcc.Graph(id="TotalBog",figure = fig_Ttotal_nofiltro_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                    dcc.Graph(id="TotalBog2",figure = fig_Ttotal_nofiltro_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="TotalBog3",figure = fig_Ttotal_nofiltro_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="TotalBog4",figure = fig_Ttotal_nofiltro_bog)], className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="TotalBog5",figure = fig_Ttotal_nofiltro_bog)], className = 'create_container2')
            
 
        ],className='contenedor-graficos')
    ]),
    
    
   
    ###Cumplimientos sin filtro
    html.Div([
        html.Div([
        html.H2("Cumplimiento sin filtros")],className = 'titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumple_bog",figure =fig_Cumpletotal_nofiltro_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumple_bquilla",figure = fig_Cumpletotal_nofiltro_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumple_cali",figure = fig_Cumpletotal_nofiltro_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumple_medellin",figure =fig_Cumpletotal_nofiltro_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="cumple_otros",figure =fig_Cumpletotal_nofiltro_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    ###Tiempos sin reprogramación
    html.Div([
        html.Div([
        html.H2("Tiempos sin reprogramación")],className='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="tiempos_sinRp_bog",figure =fig_Ttotal_sinRp_bog)],className ='create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="tiempos_sinRp_bquilla",figure = fig_Ttotal_sinRp_bquilla)],className ='create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="tiempos_sinRp_cali",figure = fig_Ttotal_sinRp_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="tiempos_sinRp_med",figure =fig_Ttotal_sinRp_med)],className ='create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="tiempos_sinRp_otros",figure =fig_Ttotal_sinRp_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),

    
    ###Cumplimientos sin reprogramación
    html.Div([
        html.Div([
        html.H2("Cumplimiento sin reprogramación")],className = 'titulo-seccion' ),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumple_sinRpBog",figure = fig_Cumpletotal_sinRP_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumple_sinRpBquilla",figure = fig_Cumpletotal_sinRP_bquilla )],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumple_sinRpcali",figure = fig_Cumpletotal_sinRP_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumple_sinRpMed",figure = fig_Cumpletotal_sinRP_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="cumple_sinRpotros",figure =fig_Cumpletotal_sinRP_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
   
    ###Tiempos sin reprogramación y 6km
    html.Div([
        html.Div([
        html.H2("Tiempos 6km y sin reprogramación")],className = 'titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="tiempos_sinRP_6km_bog",figure = fig_Ttotal_sinRp6km_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="tiempos_sinRP_6km_bquilla",figure = fig_Ttotal_sinRp6km_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="tiempos_sinRP_6km_cali",figure = fig_Ttotal_sinRp6km_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="tiempos_sinRP_6km_med",figure =fig_Ttotal_sinRp6km_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="tiempos_sinRP_6km_otros",figure =fig_Ttotal_sinRp6km_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    
    ###Cumplimientos sin reprogramación y 6km
    html.Div([
        html.Div([
        html.H2("Cumplimiento 6km y sin reprogramación")],className = 'titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumple_sinRP6km_bog",figure =fig_Cumpletotal_sinRP6km_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumple_sinRP6km_bquilla",figure = fig_Cumpletotal_sinRP6km_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumple_sinRP6km_cali",figure = fig_Cumpletotal_sinRP6km_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumple_sinRP6km_medellin",figure = fig_Cumpletotal_sinRP6km_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="cumple_sinRP6km_otros",figure = fig_Cumpletotal_sinRP6km_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Tiempos UM sin reprogramación
    html.Div([
        html.Div([
        html.H2("Tiempos UM sin reprogramación")],className ='titulo-seccion'),
        html.Div([
                html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="tiempoUM_sinRP_bog",figure = fig_tiempoUM_sinRP_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="tiempoUM_sinRP_bquilla",figure = fig_tiempoUM_sinRP_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="tiempoUM_sinRP_cali",figure =fig_tiempoUM_sinRP_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="tiempoUM_sinRP_med",figure =fig_tiempoUM_sinRP_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="tiempoUM_sinRP_otros",figure =fig_tiempoUM_sinRP_otros)], className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Cumplimiento UM sin reprogramación
    html.Div([
        html.Div([
        html.H2("Cumplimiento UM sin reprogramación")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumpleUM_sinRP_bog",figure = fig_cumpleUM_sinRp_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumpleUM_sinRP_bquilla",figure = fig_cumpleUM_sinRp_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumpleUM_sinRP_cali",figure = fig_cumpleUM_sinRp_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumpleUM_sinRP_med",figure = fig_cumpleUM_sinRp_med )],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="OtrascumpleUM_sinRP_otros",figure = fig_cumpleUM_sinRp_otros )],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Tiempos UM 6km y sin reprogramación
    html.Div([
        html.Div([
        html.H2("Tiempo UM 6km y sin reprogramación")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="tiempoUM_sinRP6km_bog",figure = fig_tiempoUM_sinRP6km_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="tiempoUM_sinRP6km_bquilla",figure = fig_tiempoUM_sinRP6km_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="tiempoUM_sinRP6km_cali",figure = fig_tiempoUM_sinRP6km_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="tiempoUM_sinRP6km_med",figure = fig_tiempoUM_sinRP6km_med )],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="tiempoUM_sinRP6km_otros",figure = fig_tiempoUM_sinRP6km_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Cumplimiento UM 6km y sin reprogramación
    html.Div([
        html.Div([
        html.H2("Cumplimiento UM 6km y sin reprogramación")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumpleUM_sinRP6km_bog",figure = fig_cumpleUM_sinRp6km_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumpleUM_sinRP6km_bquilla",figure = fig_cumpleUM_sinRp6km_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumpleUM_sinRP6km_cali",figure = fig_cumpleUM_sinRp6km_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumpleUM_sinRP6km_med",figure = fig_cumpleUM_sinRp6km_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="cumpleUM_sinRP6km_otros",figure = fig_cumpleUM_sinRp6km_otros)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###%Ordenes menor a 6km
    html.Div([
        html.Div([
        html.H2("Porcentaje ordenes menor a 6km")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="porc_menor6km_bog",figure = fig_bogotakm )],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="porc_menor6km_bquilla",figure = fig_bquillakm)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="porc_menor6km_cali",figure = fig_calikm)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="porc_menor6km_med",figure = fig_medellinkm)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id="porc_menor6km_otros",figure = fig_otrasciudadeskm )],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    
    ###% Ordenes con salto
    html.Div([
        html.Div([
        html.H2("Porcentaje ordenes con salto por tiempo y quiebre")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="saltos_bog",figure = fig_saltos_bog )],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="saltos_bquilla",figure = fig_saltos_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="saltos_cali",figure = fig_saltos_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="saltos_med",figure = fig_saltos_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id = "saltos_otros",figure = fig_saltos_otros )],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Tiempo de alistamiento
    html.Div([
        html.Div([
        html.H2("Tiempo de alistamiento primer rfbp vs último rfbp")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="alistamiento_bog",figure = fig_tiempoalistamiento_bog )],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="alistamiento_bquilla",figure = fig_tiempoalistamiento_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="alistamiento_cali",figure = fig_tiempoalistamiento_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="alistamiento_med",figure = fig_tiempoalistamiento_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id ="alistamiento_otros",figure = fig_tiempoalistamiento_otras )],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    

    
    ###Cumplimiento alistamiento
    html.Div([
        html.Div([
        html.H2("Cumplimiento alistamiento")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="cumple_alistamiento_bog",figure = fig_cumple3min_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="cumple_alistamiento_bquilla",figure = fig_cumple3min_bquilla)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="cumple_alistamiento_cali",figure =fig_cumple3min_cali )],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="cumple_alistamiento_med",figure = fig_cumple3min_medellin)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudades"),
                dcc.Graph(id ="cumple_alistamiento_otros",figure = fig_cumple3min_otras)],className = 'create_container2')
            ],className='contenedor-graficos')
        ]),
    
    
    ###Porcentaje de cancelados general
    html.Div([
        html.Div([
        html.H2("Porcentaje de cancelados y devoluciones general")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Cancelados"),
                dcc.Graph(id="cancelados_gral",figure = fig_canc_gral)],className = 'create_container2'),
            html.Div([
                html.H3("Devoluciones"),
                dcc.Graph(id="devoluciones_gral",figure = fig_dev_gral)],className = 'create_container2')
            
            ],className='contenedor-graficos-2col')
        ]),
    
    ###Responsables cancelaciones
    
    html.Div([
        html.Div([
            html.H2("Responsables cancelaciones")],className = 'titulo-seccion'),
        html.Div([
            dcc.Graph(id = "responsables_cancelacion",figure = fig_responsables_cancelados)],className = 'create_container2')
        ]),
        

    
    ###Porcentaje de cancelados y devoluciones por ciudad
    html.Div([
        html.Div([
        html.H2("Porcentaje de cancelados y devoluciones por ciudad")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Bogotá"),
                dcc.Graph(id="canc_dev_bog",figure = fig_canc_dev_bog)],className = 'create_container2'),
            html.Div([
                html.H3("Barranquilla"),
                dcc.Graph(id="canc_dev_bquilla",figure = fig_canc_dev_baq)],className = 'create_container2'),
            html.Div([
                html.H3("Cali"),
                dcc.Graph(id="canc_dev_cali",figure = fig_canc_dev_cali)],className = 'create_container2'),
            html.Div([
                html.H3("Medellín"),
                dcc.Graph(id="canc_dev_med",figure = fig_canc_dev_med)],className = 'create_container2'),
            html.Div([
                html.H3("Otras ciudad"),
                dcc.Graph(id="canc_dev_otros",figure = fig_canc_dev_otros)],className = 'create_container2')
            
            ],className='contenedor-graficos')
        ]),
   
    
    ###Retiro en tienda participación
    html.Div([
        html.Div([
        html.H2("Cobro de domicilios")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Total recaudado"),
                dcc.Graph(id="total_recaudo",figure=fig_cobro_gral)],className = 'create_container2'),
            html.Div([
                html.H3("Total recaudado por canal"),
                dcc.Graph(id="total_recaudo_canal",figure= fig_cobro_canal)],className = 'create_container2')
        
            ],className="contenedor-graficos-2col")
        ]),
    

    ###Retiro en tienda ticket
    html.Div([
        html.Div([
        html.H2("Retiro en tienda")],className ='titulo-seccion'),
        html.Div([
            html.Div([
                html.H3("Participación venta retiro en tienda vs venta ecommerce"),
                dcc.Graph(id="participa_ret",figure = fig_ret_venta)],className = 'create_container2'),
            html.Div([
                html.H3("Ticket Promedio Retiro en tienda vs ecommerce"),
                dcc.Graph(id="ticket_ret",figure = fig_ticket_ecomm)],className = 'create_container2')
                
            ],className="contenedor-graficos-2col")
        ])
])
   
if __name__ == '__main__':
    app.run_server(debug=False)


# In[ ]:




