import json
import pandas as pd

ruta_json = r'Direccion de \output.json'
ruta_excel = r'Direccion del resultado'

with open(ruta_json, 'r') as file:
    data = json.load(file)

eventos_por_tipo = {}
for evento in data:
    tipo = evento['kind']
    if tipo not in eventos_por_tipo:
        eventos_por_tipo[tipo] = []
    eventos_por_tipo[tipo].append(evento['content'])


with pd.ExcelWriter(ruta_excel, engine='xlsxwriter') as writer:
    hojas = {}
    for tipo, eventos in eventos_por_tipo.items():
        df = pd.json_normalize(eventos)
        df.columns = df.columns.str.strip().str.lower().str.replace('_', '-')
        df.to_excel(writer, sheet_name=tipo[:31], index=False)
        hojas[tipo] = df


hoja_bloques = None
for nombre, df in hojas.items():
    columnas = df.columns.str.strip().str.lower().str.replace('_', '-')
    if all(col in columnas for col in ['timestamp', 'node-id', 'block-id']):
        hoja_bloques = df.copy()
        print(f"Usando la hoja '{nombre}' como fuente de origen de bloques.")
        break

if hoja_bloques is None:
    raise ValueError("No se encontró ninguna hoja que tenga 'timestamp', 'node-id' y 'block-id'.")
df_flow = hojas.get("flow-block")
if df_flow is None:
    raise ValueError("No se encontró la hoja 'flow-block'.")

df_flow.columns = df_flow.columns.str.strip().str.lower().str.replace('_', '-')
df_filtrado = df_flow[['begin-node-id', 'end-node-id', 'block-id']]
df_sin_duplicados = df_filtrado.drop_duplicates(subset=['block-id', 'end-node-id'], keep='first')

hoja_bloques.columns = hoja_bloques.columns.str.strip().str.lower().str.replace('_', '-')
df_bloques_ordenado = hoja_bloques.sort_values(by='timestamp')
origenes = df_bloques_ordenado.drop_duplicates(subset='block-id', keep='first')[['block-id', 'node-id']]
origenes = origenes.rename(columns={'node-id': 'origin-node-id'})

df_con_origen = df_sin_duplicados.merge(origenes, on='block-id', how='left')

conteo = df_con_origen.groupby(['end-node-id', 'begin-node-id']).size().reset_index(name='total')
total_por_end = conteo.groupby('end-node-id')['total'].transform('sum')
conteo['porcentaje'] = (conteo['total'] / total_por_end * 100).round(2)
conteo = conteo.sort_values(['end-node-id', 'porcentaje'], ascending=[True, False])


df_con_origen['es_origen'] = df_con_origen['begin-node-id'] == df_con_origen['origin-node-id']
total_transmisiones = len(df_con_origen)
transmisiones_desde_origen = df_con_origen['es_origen'].sum()
porc_origen = round((transmisiones_desde_origen / total_transmisiones) * 100, 2)

df_addnode = hojas.get("add-node")
if df_addnode is None:
    raise ValueError("No se encontró la hoja 'add-node' con regiones.")

df_addnode.columns = df_addnode.columns.str.strip().str.lower().str.replace('_', '-')
region_map = df_addnode[['node-id', 'region-id']].drop_duplicates().set_index('node-id')['region-id']

df_con_origen['region-begin'] = df_con_origen['begin-node-id'].map(region_map)
df_con_origen['region-origen'] = df_con_origen['origin-node-id'].map(region_map)
df_con_origen['misma-region'] = df_con_origen['region-begin'] == df_con_origen['region-origen']

transmisiones_misma_region = df_con_origen['misma-region'].sum()
porc_misma_region = round((transmisiones_misma_region / total_transmisiones) * 100, 2)


df_no_origen = df_con_origen[df_con_origen['es_origen'] == False]
df_no_region = df_con_origen[df_con_origen['misma-region'] == False]


output_final = r'C:\Users\CPR\Desktop\SimBlock\Simulaciones\Interprete\resultado_final.xlsx'
with pd.ExcelWriter(output_final, engine='xlsxwriter') as writer:
    df_flow.to_excel(writer, sheet_name="flow-block", index=False)
    hoja_bloques.to_excel(writer, sheet_name="bloques-propagados", index=False)
    df_sin_duplicados.to_excel(writer, sheet_name="flow-filtrado", index=False)
    df_con_origen.to_excel(writer, sheet_name="flow-con-origen", index=False)
    conteo.to_excel(writer, sheet_name="porcentajes", index=False)

    
    resumen = pd.DataFrame([{
        'transmisiones_totales': total_transmisiones,
        'transmisiones_desde_origen': transmisiones_desde_origen,
        'porcentaje_desde_origen': porc_origen,
        'transmisiones_misma_region': transmisiones_misma_region,
        'porcentaje_misma_region': porc_misma_region
    }])
    resumen.to_excel(writer, sheet_name="resumen_origen_region", index=False)

   
    df_no_origen.to_excel(writer, sheet_name="transmisiones_no_desde_origen", index=False)
    df_no_region.to_excel(writer, sheet_name="transmisiones_fuera_de_region", index=False)

print(" Proceso completado")
