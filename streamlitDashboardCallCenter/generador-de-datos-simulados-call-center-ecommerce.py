# -*- coding: utf-8 -*-
"""
Generador simulado de datos para tablero educativo de Call Center Ecommerce.
Produce dos archivos CSV:
  1) llamadas_cdr.csv   -> una fila por llamada (KPIs operativos)
  2) casos_tickets.csv -> una fila por caso generado (FCR, reincidencia, CSAT)

Uso:  python generar_datos_callcenter.py
Requisitos: solo librería estándar (csv, random, datetime).
Ajusta los parámetros en la sección CONFIG.
"""

import csv
import random
from datetime import datetime, timedelta

# ----------------------------- CONFIG -----------------------------
FECHA_INICIO = datetime(2026, 8, 25)   # 60 días de historia
DIAS = 60
LLAMADAS_POR_DIA_BASE = 250           # día típico (sube en fin de semana)
ARCHIVO_CDR = "llamadas_cdr.csv"
ARCHIVO_CASOS = "casos_tickets.csv"
random.seed(42)                       # reproducible; cambia o elimina para variar

# Perfil horario de un ecommerce: pico medio día y pico nocturno (compras online)
PERFIL_HORARIO = {
    7: 0.02, 8: 0.04, 9: 0.06, 10: 0.08, 11: 0.10, 12: 0.09,
    13: 0.07, 14: 0.06, 15: 0.06, 16: 0.06, 17: 0.05, 18: 0.05,
    19: 0.07, 20: 0.08, 21: 0.06, 22: 0.03, 23: 0.01,
}  # suma ~ 0.99; hora 0-6 casi sin llamadas

# Motivos de contacto típicos de ecommerce: (peso, AHT promedio seg, %FCR)
MOTIVOS = {
    "estado_envio":    (0.28, 240, 0.85),
    "devolucion":      (0.20, 420, 0.62),
    "problema_pago":   (0.15, 360, 0.70),
    "cambio_producto": (0.12, 450, 0.58),
    "facturacion":     (0.08, 300, 0.75),
    "cuenta_claves":   (0.07, 210, 0.80),
    "reclamo_calidad": (0.06, 540, 0.45),
    "informacion_preventa": (0.04, 260, 0.88),
}

AGENTES = [f"AG-{i:03d}" for i in range(1, 26)]
TURNOS = {"matutino": list(range(7, 15)), "vespertino": list(range(14, 22)), "nocturno": [22, 23, 7, 8]}
COLAS = ["Soporte_Pedidos", "Soporte_Envios", "Retenciones", "Ventas"]
ESCALAMIENTOS = ["", "", "", "", "", "Supervisor", "Area_Logistica", "Area_Billing"]

# --------------------------- UTILIDADES ---------------------------
def elegir_ponderado(dic):
    r = random.random()
    acum = 0.0
    for k, (peso, *_rest) in dic.items():
        acum += peso
        if r <= acum:
            return k
    return list(dic.keys())[-1]

def agentes_disponibles(hora):
    if hora in TURNOS["matutino"]:
        n = 12
    elif hora in TURNOS["vespertino"]:
        n = 10
    else:
        n = 5
    return random.sample(AGENTES, min(n, len(AGENTES)))

# --------------------------- GENERACIÓN ---------------------------
llamadas = []
casos = []
id_llamada = 100000
id_caso = 50000
id_cliente_pool = [f"CLI-{i:05d}" for i in range(1, 4001)]  # 4.000 clientes

for d in range(DIAS):
    dia = FECHA_INICIO + timedelta(days=d)
    factor = 1.15 if dia.weekday() >= 5 else 1.0        # fin de semana +15%
    total_hoy = int(LLAMADAS_POR_DIA_BASE * factor * random.uniform(0.9, 1.1))

    for _ in range(total_hoy):
        id_llamada += 1
        # Hora según perfil
        r, acum, hora = random.random(), 0.0, 11
        for h, p in PERFIL_HORARIO.items():
            acum += p
            if r <= acum:
                hora = h
                break
        minuto = random.randint(0, 59)
        ts_entrada = dia.replace(hour=hora, minute=minuto, second=random.randint(0, 59))

        motivo = elegir_ponderado(MOTIVOS)
        _, aht_prom, fcr_motivo = MOTIVOS[motivo]
        cola = random.choices(COLAS, weights=[35, 35, 15, 15])[0]

        # Espera depende de la carga de la hora (más espera en picos)
        factor_pico = 2.2 if hora in (11, 12, 20) else (1.5 if hora in (10, 13, 19, 21) else 1.0)
        espera = max(3, int(random.expovariate(1 / (18 * factor_pico))))

        # Abandono correlacionado con la espera
        p_abandono = min(0.55, espera / 180)
        if random.random() < p_abandono:
            resultado, duracion, acw = "abandonada", 0, 0
            agente, escalo = "", ""
            fcr_flag, csat = None, None
        else:
            resultado = "atendida"
            agente = random.choice(agentes_disponibles(hora))
            duracion = max(30, int(random.gauss(aht_prom - 45, aht_prom * 0.25)))
            acw = random.randint(15, 60)
            escalo = random.choice(ESCALAMIENTOS)
            fcr_flag = random.random() < fcr_motivo
            # CSAT sesgado: sin escalamiento y con FCR -> mejor nota
            base = 4.0 if (fcr_flag and not escalo) else 3.2
            csat = max(1, min(5, round(random.gauss(base - (0.8 if escalo else 0), 0.7))))

        llamadas.append({
            "id_llamada": f"L{id_llamada}",
            "fecha": ts_entrada.strftime("%Y-%m-%d"),
            "hora": hora,
            "fecha_hora_entrada": ts_entrada.strftime("%Y-%m-%d %H:%M:%S"),
            "id_cliente": random.choice(id_cliente_pool),
            "id_agente": agente,
            "cola": cola,
            "tipo_llamada": random.choices(["entrante", "saliente"], weights=[90, 10])[0],
            "motivo": motivo,
            "resultado_llamada": resultado,
            "espera_seg": espera,
            "duracion_seg": duracion,
            "acw_seg": acw,
            "escalado_a": escalo,
            "dia_semana": dia.strftime("%A"),
        })

        # Las llamadas atendidas generan caso (~85%)
        if resultado == "atendida" and random.random() < 0.85:
            id_caso += 1
            reincidencia = random.random() > fcr_flag if fcr_flag else random.random() > 0.8
            casos.append({
                "id_caso": f"C{id_caso}",
                "id_llamada": f"L{id_llamada}",
                "fecha_apertura": ts_entrada.strftime("%Y-%m-%d"),
                "id_cliente": llamadas[-1]["id_cliente"],
                "id_agente": agente,
                "categoria": motivo,
                "estado_caso": "reabierto" if reincidencia else random.choices(
                    ["resuelto", "pendiente"], weights=[85, 15])[0],
                "fcr": int(bool(fcr_flag and not reincidencia)),
                "reincidencia": int(reincidencia),
                "horas_resolucion": round(abs(random.gauss(18, 10)), 1),
                "csat": csat if csat is not None else random.randint(1, 5),
                "valor_orden": round(random.uniform(15, 450), 2),
            })

# --------------------------- EXPORT ---------------------------
columnas_cdr = list(llamadas[0].keys())
with open(ARCHIVO_CDR, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=columnas_cdr)
    w.writeheader()
    w.writerows(llamadas)

columnas_casos = list(casos[0].keys())
with open(ARCHIVO_CASOS, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=columnas_casos)
    w.writeheader()
    w.writerows(casos)

# --------------------------- RESUMEN ---------------------------
atendidas = [l for l in llamadas if l["resultado_llamada"] == "atendida"]
sl = 100 * sum(1 for l in llamadas if l["espera_seg"] <= 20) / len(llamadas)
aband = 100 * (len(llamadas) - len(atendidas)) / len(llamadas)
asa = sum(l["espera_seg"] for l in llamadas) / len(llamadas)
aht = (sum(l["duracion_seg"] + l["acw_seg"] for l in atendidas) / len(atendidas))
fcr = 100 * sum(c["fcr"] for c in casos) / len(casos)
csat = sum(c["csat"] for c in casos) / len(casos)

print(f"Archivo {ARCHIVO_CDR}: {len(llamadas):,} llamadas")
print(f"Archivo {ARCHIVO_CASOS}: {len(casos):,} casos")
print("--- KPIs resultantes (verifica que sean realistas) ---")
print(f"Nivel de servicio (<=20s): {sl:.1f}%")
print(f"Tasa de abandono: {aband:.1f}%")
print(f"ASA: {asa:.0f}s | AHT: {aht:.0f}s")
print(f"FCR: {fcr:.1f}% | CSAT: {csat:.2f}/5")