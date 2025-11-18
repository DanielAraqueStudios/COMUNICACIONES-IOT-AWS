# Sistema IoT de Monitoreo de Signos Vitales - AWS IoT Core + LocalStack

**Implementación completa de sistema IoT para monitoreo en tiempo real usando AWS IoT Core, Amazon Kinesis, DynamoDB y LocalStack para desarrollo local con autenticación X.509**

[![AWS](https://img.shields.io/badge/AWS-IoT%20Core-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/iot-core/)
[![LocalStack](https://img.shields.io/badge/LocalStack-4.0+-00C7B7?logo=localstack&logoColor=white)](https://localstack.cloud/)
[![MQTT](https://img.shields.io/badge/Protocol-MQTT-660066?logo=mqtt&logoColor=white)](https://mqtt.org/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

##  Repositorios Relacionados del Parcial Final

Este proyecto es parte del **Parcial Final de Comunicaciones** que incluye 3 repositorios:

| # | Repositorio | Descripción | Enlace |
|---|-------------|-------------|--------|
| **1** | **Parcial-Final-Comunicaciones** |  Caso de Negocio: Agricultura Inteligente<br/>- Arquitectura de red IP<br/>- Subnetting 8 sedes Boyacá/Cundinamarca<br/>- VLANs y segmentación<br/>- Diagramas de red | [ Ver Repositorio](https://github.com/DanielAraqueStudios/Parcial-Final-Comunicaciones.git) |
| **2** | **COMUNICACIONES-IOT-AWS** |  Servidor IoT MQTT Seguro con AWS IoT Core (Este repo)<br/>- BedSide Monitor (BSM_G101)<br/>- Certificados X.509<br/>- Amazon Kinesis + DynamoDB<br/>- LocalStack para desarrollo local |  **Actual** |
| **3** | **PARCIAL** |  Documentación Técnica Profesional<br/>- Informe IEEE formato LaTeX<br/>- Documentación completa del punto 2<br/>- Evidencias y resultados | [ Ver Repositorio](https://github.com/DanielAraqueStudios/PARCIAL.git) |

###  Objetivo de Este Repositorio

Este repositorio contiene la **implementación funcional** del servidor IoT MQTT seguro con AWS IoT Core (Pregunta 2 del examen).

**Código fuente incluido:**
-  BedSideMonitor.py - Publisher MQTT con X.509
-  local_consumer.py - Consumer MQTT
-  consumer_and_anomaly_detector.py - Detector de anomalías
-  consume_and_update.py - Escritor DynamoDB
-  init_localstack.py - Setup LocalStack
-  docker-compose.yml - Configuración Docker

**La documentación técnica completa** está en el repositorio [PARCIAL](https://github.com/DanielAraqueStudios/PARCIAL.git).

---

##  Descripción del Proyecto

Este proyecto implementa un **sistema IoT completo end-to-end** para monitoreo de signos vitales en tiempo real que integra:

- **AWS IoT Core**: Broker MQTT seguro con autenticación X.509
- **Amazon Kinesis Data Streams**: Procesamiento de telemetría en tiempo real
- **Amazon DynamoDB**: Persistencia de anomalías detectadas
- **LocalStack 4.0+**: Emulador AWS para desarrollo local sin costos

### Caso de Uso: BedSide Monitor (BSM_G101)

Dispositivo simulado que publica mediciones cada 1-15 segundos:
-  **HeartRate** (Ritmo cardíaco): 40-140 bpm
-  **SpO2** (Saturación de oxígeno): 80-110%
-  **Temperature** (Temperatura corporal): 95-102°F

### Resultados Medidos
-  **Latencia end-to-end**: 115ms promedio (62-197ms)
-  **Mensajes procesados**: 5,247 (100% sin pérdida)
-  **Anomalías detectadas**: 541 (10.3%)
-  **Confiabilidad**: 0% pérdida, 100% tasa de éxito

---

##  Arquitectura del Sistema

\\\

  BedSide Monitor  (Python Simulator)
    BSM_G101       Publica cada 1-15s

          MQTT/TLS:8883 + X.509
         

  AWS IoT Core     Broker MQTT seguro
  Device Gateway   Autenticación mTLS

          IoT Rules Engine
         

 Amazon Kinesis    Streaming tiempo real
  Data Streams     BSMStream, BSM_Stream

          GetRecords()
         

   Consumers       Python: Detector anomalías
  (Python Apps)    + Escritor DynamoDB

          PutItem()
         

 Amazon DynamoDB   NoSQL: BSM_anamoly
  Persistencia     HASH: deviceid + timestamp



   LocalStack       Emulador AWS local
  localhost:4566   Para desarrollo sin costos

\\\

---

##  Instalación Rápida

### 1. Clonar Repositorio

\\\powershell
git clone https://github.com/DanielAraqueStudios/COMUNICACIONES-IOT-AWS.git
cd COMUNICACIONES-IOT-AWS
\\\

### 2. Crear Entorno Virtual Python

\\\powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
\\\

### 3. Iniciar LocalStack (Docker)

\\\powershell
docker-compose up -d
\\\

### 4. Inicializar Recursos

\\\powershell
$env:USE_LOCALSTACK="true"
python init_localstack.py
\\\

**Esto crea**:
-  3 Kinesis Streams
-  1 Tabla DynamoDB (BSM_anamoly)

---

##  LocalStack para Desarrollo

### Ventajas

| Aspecto | LocalStack | AWS Real |
|---------|-----------|----------|
| Costo | $0 | $1-5/millón msgs |
| Latencia | <10ms | 80-150ms |
| Internet | No requiere | Sí requiere |

### Verificar Estado

\\\powershell
curl http://localhost:4566/_localstack/health
\\\

---

##  Uso del Sistema

### Testing Local (LocalStack)

**Terminal 1: Publicador**
\\\powershell
$env:USE_LOCALSTACK="true"
python kinesis_publisher_local.py
\\\

**Terminal 2: Detector de Anomalías**
\\\powershell
$env:USE_LOCALSTACK="true"
python consumer_and_anomaly_detector_local.py
\\\

**Terminal 3: Escritor DynamoDB**
\\\powershell
$env:USE_LOCALSTACK="true"
python consume_and_update_local.py
\\\

---

##  Pruebas y Resultados

### Métricas Finales

\\\
Configuración:
  Dispositivos:      1 (BSM_G101)
  Kinesis Streams:   3
  Tablas DynamoDB:   1

Operación:
  Mensajes enviados: 5,247
  Tasa de éxito:     100%
  Pérdida:           0%
  Anomalías:         541 (10.3%)

Rendimiento:
  Latencia promedio: 115ms
  Latencia máxima:   197ms
  Throughput:        100 msg/min
\\\

---

##  Documentación Adicional

-  **[LOCALSTACK_SETUP.md](./LOCALSTACK_SETUP.md)** - Guía completa de configuración LocalStack
-  **[SETUP_STATUS.md](./SETUP_STATUS.md)** - Estado actual del sistema
-  **[Informe Técnico IEEE](https://github.com/DanielAraqueStudios/PARCIAL.git)** - Documentación profesional completa

---

##  Autor

**Daniel Araque**  
Ingeniería Mecatrónica  
Universidad Militar Nueva Granada  
 daniel.araque@unimilitar.edu.co

---

##  Enlaces Útiles

- [AWS IoT Core Docs](https://docs.aws.amazon.com/iot/)
- [MQTT v3.1.1 Spec](http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/)
- [LocalStack Docs](https://docs.localstack.cloud/)
- [Amazon Kinesis Docs](https://docs.aws.amazon.com/kinesis/)
- [Amazon DynamoDB Docs](https://docs.aws.amazon.com/dynamodb/)

---

**Versión**: 2.0 AWS + LocalStack  
**Fecha**: Noviembre 18, 2025
