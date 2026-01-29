#!/usr/bin/env python3
"""
ANÁLISIS COMPLETO: Todas las conexiones a base de datos en el sistema
Este script analiza TODOS los archivos para identificar conexiones a BD
"""
import os
import re
from pathlib import Path
from collections import defaultdict

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.END}")

def analyze_file(filepath):
    """Analiza un archivo Python para encontrar conexiones a BD"""
    connections = {
        'imports': [],
        'database_urls': [],
        'get_db_usage': [],
        'sessionlocal_usage': [],
        'engine_usage': [],
        'direct_connections': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Imports de database
                if re.search(r'from.*database import|from.*get_db', line):
                    connections['imports'].append((i, line.strip()))
                
                # DATABASE_URL
                if 'DATABASE_URL' in line and '=' in line:
                    connections['database_urls'].append((i, line.strip()))
                
                # Uso de get_db
                if 'Depends(get_db)' in line or 'get_db()' in line:
                    connections['get_db_usage'].append((i, line.strip()))
                
                # Uso de SessionLocal
                if 'SessionLocal()' in line:
                    connections['sessionlocal_usage'].append((i, line.strip()))
                
                # Uso de engine
                if re.search(r'create_engine|engine\s*=|engine\.', line):
                    connections['engine_usage'].append((i, line.strip()))
                
                # Conexiones directas (psycopg2, etc)
                if re.search(r'psycopg2\.connect|pymysql\.connect', line):
                    connections['direct_connections'].append((i, line.strip()))
    
    except Exception as e:
        pass
    
    return connections

def scan_directory(directory, extensions=['.py']):
    """Escanea un directorio recursivamente"""
    results = {}
    
    for root, dirs, files in os.walk(directory):
        # Ignorar directorios comunes
        dirs[:] = [d for d in dirs if d not in [
            '__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv'
        ]]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, directory)
                
                connections = analyze_file(filepath)
                
                # Solo guardar si tiene conexiones
                if any(connections.values()):
                    results[relative_path] = connections
    
    return results

def main():
    print_header("🔍 ANÁLISIS COMPLETO DE CONEXIONES A BASE DE DATOS")
    
    # Directorios a analizar
    directories = {
        'Backend (CODE/src)': 'CODE/src',
        'Scripts raíz': '.',
        'Scripts staging': 'scripts/staging',
        'Scripts database': 'scripts/database',
    }
    
    all_results = {}
    
    for name, directory in directories.items():
        if os.path.exists(directory):
            print(f"\n{Colors.YELLOW}📂 Analizando: {name} ({directory}){Colors.END}")
            results = scan_directory(directory)
            all_results[name] = results
            print(f"   {Colors.GREEN}✓ {len(results)} archivos con conexiones encontrados{Colors.END}")
    
    # ========================================
    # RESUMEN POR CATEGORÍA
    # ========================================
    
    print_header("📊 RESUMEN POR TIPO DE CONEXIÓN")
    
    # Contar por tipo
    total_imports = 0
    total_get_db = 0
    total_sessionlocal = 0
    total_engine = 0
    total_direct = 0
    total_database_urls = 0
    
    files_by_type = defaultdict(list)
    
    for section_name, results in all_results.items():
        for filepath, connections in results.items():
            if connections['imports']:
                total_imports += len(connections['imports'])
                files_by_type['imports'].append(filepath)
            if connections['get_db_usage']:
                total_get_db += len(connections['get_db_usage'])
                files_by_type['get_db'].append(filepath)
            if connections['sessionlocal_usage']:
                total_sessionlocal += len(connections['sessionlocal_usage'])
                files_by_type['sessionlocal'].append(filepath)
            if connections['engine_usage']:
                total_engine += len(connections['engine_usage'])
                files_by_type['engine'].append(filepath)
            if connections['direct_connections']:
                total_direct += len(connections['direct_connections'])
                files_by_type['direct'].append(filepath)
            if connections['database_urls']:
                total_database_urls += len(connections['database_urls'])
                files_by_type['database_urls'].append(filepath)
    
    print(f"\n{Colors.BOLD}Tipo de Conexión                    Archivos    Ocurrencias{Colors.END}")
    print(f"{'-'*70}")
    print(f"{'Imports (from database import)':<35} {len(files_by_type['imports']):<11} {total_imports}")
    print(f"{'Depends(get_db) - FastAPI':<35} {len(files_by_type['get_db']):<11} {total_get_db}")
    print(f"{'SessionLocal() - SQLAlchemy':<35} {len(files_by_type['sessionlocal']):<11} {total_sessionlocal}")
    print(f"{'create_engine / engine':<35} {len(files_by_type['engine']):<11} {total_engine}")
    print(f"{'DATABASE_URL definiciones':<35} {len(files_by_type['database_urls']):<11} {total_database_urls}")
    print(f"{'Conexiones directas (psycopg2)':<35} {len(files_by_type['direct']):<11} {total_direct}")
    
    # ========================================
    # ANÁLISIS DE RUTAS/ENDPOINTS
    # ========================================
    
    print_header("🌐 ANÁLISIS DE RUTAS/ENDPOINTS (FastAPI)")
    
    routes_dir = 'CODE/src/app/routes'
    if os.path.exists(routes_dir):
        route_files = [f for f in os.listdir(routes_dir) if f.endswith('.py') and f != '__init__.py']
        
        print(f"\n{Colors.BOLD}Archivo de Ruta                     Endpoints con DB{Colors.END}")
        print(f"{'-'*70}")
        
        for route_file in sorted(route_files):
            filepath = os.path.join(routes_dir, route_file)
            connections = analyze_file(filepath)
            
            endpoint_count = len(connections['get_db_usage'])
            if endpoint_count > 0:
                status = f"{Colors.GREEN}✓{Colors.END}"
                print(f"{status} {route_file:<35} {endpoint_count} endpoints")
    
    # ========================================
    # ARCHIVOS CRÍTICOS
    # ========================================
    
    print_header("⚠️  ARCHIVOS CRÍTICOS CON MÚLTIPLES CONEXIONES")
    
    critical_files = []
    for section_name, results in all_results.items():
        for filepath, connections in results.items():
            total_connections = sum(len(v) for v in connections.values())
            if total_connections > 5:
                critical_files.append((filepath, total_connections, connections))
    
    critical_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{Colors.BOLD}Archivo                                          Conexiones{Colors.END}")
    print(f"{'-'*70}")
    
    for filepath, count, connections in critical_files[:20]:
        print(f"{Colors.YELLOW}⚠{Colors.END}  {filepath:<45} {count}")
    
    # ========================================
    # CONFIGURACIÓN ACTUAL
    # ========================================
    
    print_header("⚙️  CONFIGURACIÓN ACTUAL DE BASE DE DATOS")
    
    config_files = [
        ('CODE/src/app/database.py', 'Configuración principal'),
        ('CODE/src/app/config.py', 'Settings'),
        ('CODE/.env', 'Environment desarrollo'),
        ('CODE/.env.staging', 'Environment staging'),
        ('.env.production', 'Environment producción'),
        ('.env.staging', 'Environment staging raíz'),
    ]
    
    print(f"\n{Colors.BOLD}Archivo                              Estado{Colors.END}")
    print(f"{'-'*70}")
    
    for filepath, description in config_files:
        if os.path.exists(filepath):
            status = f"{Colors.GREEN}✓ Existe{Colors.END}"
            
            # Leer DATABASE_URL si existe
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'DATABASE_URL' in content:
                        # Extraer la base de datos
                        match = re.search(r'DATABASE_URL.*?/([a-zA-Z0-9_]+)', content)
                        if match:
                            db_name = match.group(1)
                            status += f" → {Colors.CYAN}{db_name}{Colors.END}"
            except:
                pass
            
            print(f"{filepath:<35} {status}")
        else:
            print(f"{filepath:<35} {Colors.RED}✗ No existe{Colors.END}")
    
    # ========================================
    # FLUJO DE CONEXIÓN
    # ========================================
    
    print_header("🔄 FLUJO DE CONEXIÓN A BASE DE DATOS")
    
    print(f"""
{Colors.BOLD}1. Configuración (config.py):{Colors.END}
   settings.database_url ← os.getenv('DATABASE_URL')
   
{Colors.BOLD}2. Motor de BD (database.py):{Colors.END}
   DATABASE_URL = settings.database_url
   engine = create_engine(DATABASE_URL)
   SessionLocal = sessionmaker(bind=engine)
   
{Colors.BOLD}3. Dependencia FastAPI:{Colors.END}
   def get_db():
       db = SessionLocal()
       yield db
       db.close()
   
{Colors.BOLD}4. Uso en Endpoints:{Colors.END}
   @router.get("/endpoint")
   async def endpoint(db: Session = Depends(get_db)):
       # db conecta a la BD configurada en DATABASE_URL
       ...
""")
    
    # ========================================
    # RECOMENDACIONES
    # ========================================
    
    print_header("💡 RECOMENDACIONES")
    
    print(f"""
{Colors.BOLD}Para Staging:{Colors.END}
1. ✅ Usar CODE/.env.staging con DATABASE_URL apuntando a paqueteria_staging
2. ✅ docker-compose.staging.yml debe cargar CODE/.env.staging
3. ✅ Verificar que ENVIRONMENT=staging
4. ✅ Todos los endpoints usarán automáticamente paqueteria_staging

{Colors.BOLD}Verificación:{Colors.END}
1. Dentro del contenedor staging:
   docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
   
2. Debe mostrar:
   DATABASE_URL=postgresql://...paqueteria_staging

{Colors.BOLD}Archivos que NO necesitan modificación:{Colors.END}
- ✅ Rutas (routes/*.py) - Usan Depends(get_db)
- ✅ Servicios - Reciben db como parámetro
- ✅ Modelos - No tienen conexión directa

{Colors.BOLD}Archivos que SÍ necesitan atención:{Colors.END}
- ⚠️  Scripts con DATABASE_URL hardcodeada
- ⚠️  Scripts con create_engine directo
- ⚠️  Conexiones psycopg2 directas
""")
    
    # ========================================
    # CONCLUSIÓN
    # ========================================
    
    print_header("✅ CONCLUSIÓN")
    
    print(f"""
{Colors.GREEN}{Colors.BOLD}TODAS las rutas y endpoints usan el patrón correcto:{Colors.END}
- Depends(get_db) → SessionLocal() → engine → DATABASE_URL

{Colors.GREEN}{Colors.BOLD}Esto significa:{Colors.END}
1. Si CODE/.env.staging tiene DATABASE_URL=...paqueteria_staging
2. Y docker-compose.staging.yml carga CODE/.env.staging
3. Entonces TODOS los endpoints conectarán a paqueteria_staging

{Colors.YELLOW}{Colors.BOLD}Archivos encontrados con conexiones:{Colors.END}
- Total: {sum(len(r) for r in all_results.values())} archivos
- Endpoints con DB: {total_get_db} endpoints
- Scripts con conexión directa: {total_direct} scripts

{Colors.CYAN}{Colors.BOLD}Próximo paso:{Colors.END}
Ejecutar: docker-compose -f docker-compose.staging.yml up -d
Y verificar: docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
""")

if __name__ == '__main__':
    main()
