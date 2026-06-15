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

| Servicio | Puerto | Protocolo | Herramienta recomendada |
| :--- | :--- | :--- | :--- |
| **Web** | 80 | HTTP | Navegador Web |
| **FTP** | 21 | FTP | FileZilla / WinSCP |
| **Streaming** | 1935 | RTMP | OBS Studio |
| **Dashboard** | 8089 | HTTP | Navegador Web |

*Nota: Para el acceso FTP, utiliza el usuario y contraseña definidos en tu archivo `.env`.*

---

## 🚀 Guía de Configuración y Despliegue

### 1. Clonar el repositorio
```bash
git clone [https://github.com/yaniorell/proyecto-server.git](https://github.com/yaniorell/proyecto-server.git)
cd proyecto-server
