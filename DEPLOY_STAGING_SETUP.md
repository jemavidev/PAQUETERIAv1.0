# 🚀 Setup: Deploy Automático a Staging

## 1️⃣ GENERAR SSH KEY (Si no la tienes)

En tu máquina local:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/staging_deploy -N ""
cat ~/.ssh/staging_deploy.pub
```

## 2️⃣ AGREGAR PUBLIC KEY AL SERVIDOR STAGING

En el servidor:
```bash
ssh staging
mkdir -p ~/.ssh
echo "AQUI_PEGA_TU_PUBLIC_KEY" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Verificar acceso:
```bash
ssh -i ~/.ssh/staging_deploy ubuntu@staging.jemavi.co "echo ✅ SSH OK"
```

## 3️⃣ CONFIGURAR SECRETS EN GITHUB

En GitHub (Settings → Secrets and variables → Actions):

### Secret 1: `STAGING_SSH_KEY`
```
Nombre: STAGING_SSH_KEY
Valor: (Contenido de ~/.ssh/staging_deploy - LA CLAVE PRIVADA)
```

Obtener el contenido:
```bash
cat ~/.ssh/staging_deploy | pbcopy  # macOS
# o
cat ~/.ssh/staging_deploy           # Linux - copiar manualmente
```

## 4️⃣ CREAR RAMA STAGING (Si no existe)

```bash
git checkout -b staging
git push -u origin staging
```

## 5️⃣ CREAR EL WORKFLOW ARCHIVO

El archivo `.github/workflows/deploy-staging.yml` ya existe (se agregó con este PR).

## 6️⃣ PROBAR EL DEPLOY

Hacer un commit a staging:
```bash
git add .
git commit -m "test: trigger staging deployment"
git push origin staging
```

Ir a GitHub Actions y ver el workflow ejecutándose:
- https://github.com/tu-repo/actions

## 🔍 TROUBLESHOOTING

### ❌ "SSH key permission denied"
```bash
# En el servidor staging:
ssh staging
ssh-keygen -f ~/.ssh/staging_deploy -p  # Cambiar passphrase
# En GitHub secrets: pegar la clave sin passphrase
```

### ❌ "Deploy script not found"
```bash
# En servidor:
ssh staging
ls -la /home/ubuntu/paqueteria-staging/deploy.sh
# Si no existe, crear o copiar desde local
```

### ❌ "Service health check failed"
```bash
# En servidor:
ssh staging
docker ps -a
docker logs paqueteria_staging_app
docker-compose -f docker-compose.staging.yml logs
```

### ❌ "Alembic migration failed"
```bash
# En servidor:
ssh staging
cd /home/ubuntu/paqueteria-staging/CODE
docker exec paqueteria_staging_app alembic current
docker exec paqueteria_staging_app alembic heads
docker exec paqueteria_staging_app alembic history
```

## 📋 CHECKLIST DE VALIDACIÓN

- [ ] SSH key generada
- [ ] Public key agregada al servidor
- [ ] SSH manual funciona: `ssh -i ~/.ssh/staging_deploy ubuntu@staging.jemavi.co`
- [ ] Secret `STAGING_SSH_KEY` creado en GitHub
- [ ] Rama `staging` existe en GitHub
- [ ] Archivo `.github/workflows/deploy-staging.yml` existe
- [ ] Primer commit a staging completado
- [ ] GitHub Actions workflow ejecutado exitosamente
- [ ] Servicio responde en http://localhost:8001 (en staging)

## 🔄 FLUJO DE TRABAJO

Después de configurar:

1. Hacer cambios locales
2. Commit en rama `staging`
3. `git push origin staging`
4. GitHub Actions se dispara automáticamente
5. Deploy automático a `staging.jemavi.co`
6. Validar en https://staging.paquetex.papyrus.com.co
7. Cuando esté listo, merge a `main` para producción

## 🛑 ROLLBACK RÁPIDO

Si algo falla en staging:
```bash
ssh staging
cd /home/ubuntu/paqueteria-staging
git reset --hard HEAD~1
./deploy.sh --env staging --deploy
```

---

**¿Preguntas?** Revisar logs en GitHub Actions → Actions → Deploy to Staging
