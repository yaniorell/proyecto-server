# 🚀 Proyecto: Ecosistema de Servidores (Dockerized)

Este repositorio contiene la infraestructura completa para un ecosistema de servicios gestionados mediante **Docker Compose**. Está diseñado para facilitar el despliegue de una plataforma robusta y colaborativa.

## 🛠️ Servicios Incluidos

* **Web**: Servidor Nginx para alojamiento de sitios web estáticos.
* **FTP**: Servidor `vsftpd` para transferencia y gestión de archivos.
* **Streaming**: Servidor Nginx RTMP para transmisión de video en tiempo real.
* **Mail**: Servidor de correo (`docker-mailserver`) para protocolos SMTP/IMAP.
* **Dashboard**: Herramienta de gestión personalizada en Python para monitoreo y control administrativo.

---

## 🔌 Guía de Conectividad

Para gestionar los servicios desde tu máquina local, utiliza las siguientes configuraciones:

| Servicio  | Puerto | Protocolo | Herramienta recomendada |
| --------- | ------ | --------- | ----------------------- |
| Web       | 80     | HTTP      | Navegador Web           |
| FTP       | 21     | FTP       | FileZilla / WinSCP      |
| Streaming | 1935   | RTMP      | OBS Studio              |
| Dashboard | 8089   | HTTP      | Navegador Web           |

> **Nota:** Para el acceso FTP, utiliza el usuario y contraseña definidos en tu archivo `.env`.

---

## 🚀 Guía de Configuración y Despliegue

### 1. Clonar el repositorio

```bash
git clone https://github.com/yaniorell/proyecto-server.git
cd proyecto-server
```

### 2. Configurar el entorno

Crea tu archivo de variables de entorno personal basado en la plantilla y edítalo:

```bash
cp .env.example .env
nano .env
```

Ajusta los valores de usuario, contraseña y puertos según los requisitos del equipo.

Guarda los cambios con:

* `Ctrl + O` para guardar.
* `Ctrl + X` para salir.

### 3. Levantar los servicios

Ejecuta el siguiente comando para poner en marcha el ecosistema:

```bash
sudo docker compose up -d
```

### 4. Verificar el estado

Asegúrate de que todos los contenedores estén activos:

```bash
sudo docker compose ps
```

---

## 💻 Panel de Gestión (Dashboard)

Desarrollamos un panel para monitorear el estado de los contenedores en tiempo real.

### Iniciar el Dashboard

```bash
python3 dashboard.py
```

### Acceso

```text
http://localhost:8089
```

### Funcionalidades

* Monitoreo de uso de CPU y RAM.
* Visualización de logs en tiempo real.
* Reinicio de servicios desde la interfaz.
* Supervisión general de los contenedores Docker.

---

## 📂 Estructura del Repositorio

```text
.
├── web/                 # Archivos fuente del sitio web
├── ftp/                 # Almacenamiento persistente FTP
├── mail/                # Configuración del servidor de correo
├── docker-compose.yml   # Orquestación de contenedores
├── dashboard.py         # Script de monitoreo
└── .env.example         # Plantilla de configuración
```

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

* Docker
* Docker Compose
* Git
* Python 3.10 o superior

Verifica las instalaciones:

```bash
docker --version
docker compose version
git --version
python3 --version
```

---

## 🔄 Flujo de Trabajo para el Equipo

### 1. Sincronización

Antes de comenzar a trabajar:

```bash
git pull
```

### 2. Desarrollo

Realiza tus modificaciones en la carpeta correspondiente al servicio.

### 3. Guardar cambios

```bash
git add .
git commit -m "Descripción clara de los cambios"
git push
```

### 4. Despliegue

Una vez integrados los cambios:

```bash
git pull
sudo docker compose up -d
```


git clone [https://github.com/yaniorell/proyecto-server.git](https://github.com/yaniorell/proyecto-server.git)
cd proyecto-server
