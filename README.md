# ⚡ Arus ERP - Guía de Despliegue con Docker

Arus es un sistema ERP multi-tenant para PYMEs (FastAPI + React Vite + PostgreSQL en Supabase).

---

## 🚀 Inicio Rápido con Docker

No necesitas instalar Python, Node.js ni configurar entornos virtuales localmente. Con Docker y Docker Compose puedes ejecutar todo el sistema con un solo comando.

### Prerrequisitos
- Tener instalado **Docker Desktop** (o Docker Engine + Docker Compose).
- Contar con el archivo `backend/.env` configurado. Si no lo tienes, puedes copiar la plantilla:

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` e ingresa la contraseña y clave de tu base de datos en Supabase.

---

### 1. Clonar el repositorio y ejecutar

```bash
git clone https://github.com/IoavM/Arus.git
cd Arus
docker compose up --build
```

---

### 2. Acceso a la Aplicación

Una vez iniciados los contenedores:

- 🎨 **Frontend (React)**: [http://localhost:5173](http://localhost:5173) (o [http://localhost:5173/login](http://localhost:5173/login))
- ⚡ **Backend API (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- 📖 **Documentación Swagger API**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

### 3. Comandos Útiles

* **Detener los servicios**:
  ```bash
  docker compose down
  ```
* **Ver logs en tiempo real**:
  ```bash
  docker compose logs -f
  ```
