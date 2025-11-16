# 🔧 CORRECCIÓN DE NGINX - ERROR 403 FORBIDDEN

## Problema
Nginx está intentando servir archivos estáticos directamente con `alias /app/src/static/`, pero ese directorio no existe en el host, solo en el contenedor Docker.

## Solución
Cambiar de `alias` a `proxy_pass` para que nginx proxie las peticiones a FastAPI.

---

## INSTRUCCIONES PASO A PASO

### 1. Conectarte al servidor
```bash
ssh papyrus
```

### 2. Hacer backup del archivo de configuración
```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d)
```

### 3. Ver la sección actual de /static/
```bash
sudo grep -A 20 "location /static" /etc/nginx/nginx.conf
```

### 4. Editar el archivo
```bash
sudo nano /etc/nginx/nginx.conf
# O usa el editor que prefieras: vim, vi, etc.
```

### 5. Buscar y reemplazar

**ENCONTRAR:**
```nginx
location /static/ {
    alias /app/src/static/;
    
    # Cache agresivo para archivos estáticos
    expires 7d;
    add_header Cache-Control "public, immutable";
    add_header X-Cache-Status "STATIC";
    
    # Compresión
    gzip_static on;
    
    # Logs reducidos para estáticos
    access_log off;
    
    # Optimizaciones
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
}
```

**REEMPLAZAR POR:**
```nginx
location /static/ {
    # Proxy a FastAPI (los archivos estáticos están en el contenedor)
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";
    
    # Cache agresivo para archivos estáticos
    expires 7d;
    add_header Cache-Control "public, immutable";
    add_header X-Cache-Status "STATIC";
    
    # Logs reducidos para estáticos
    access_log off;
    
    # Timeouts
    proxy_connect_timeout 10s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

### 6. También corregir /uploads/ si existe

**ENCONTRAR:**
```nginx
location /uploads/ {
    alias /app/uploads/;
    ...
}
```

**REEMPLAZAR POR:**
```nginx
location /uploads/ {
    # Proxy a FastAPI (los uploads están en el contenedor)
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Connection "";
    
    # Cache moderado
    expires 1d;
    add_header Cache-Control "public";
    add_header X-Cache-Status "UPLOADS";
    
    # Logs reducidos
    access_log off;
    
    # Timeouts
    proxy_connect_timeout 10s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

### 7. Verificar la configuración
```bash
sudo nginx -t
```

Debe mostrar: `nginx: configuration file /etc/nginx/nginx.conf test is successful`

### 8. Recargar nginx
```bash
sudo systemctl reload nginx
```

### 9. Probar
```bash
curl -I http://localhost/static/images/logo.png
```

Debe devolver `200 OK` en lugar de `403 Forbidden`.

---

## SOLUCIÓN AUTOMÁTICA (si tienes el script)

```bash
cd ~/paqueteria
git pull origin main
cd CODE/scripts/deployment
sudo bash corregir-nginx.sh
```

---

## SI ALGO SALE MAL

Restaurar el backup:
```bash
sudo cp /etc/nginx/nginx.conf.backup.* /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl reload nginx
```

