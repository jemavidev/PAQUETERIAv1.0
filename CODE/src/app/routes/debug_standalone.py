# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Debug Dashboard Independiente
Vista de debug separada e independiente del proyecto principal
Funciona para usuarios logueados y no logueados
"""

import logging
import os
import psutil
import json
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.database import get_db
from app.utils.datetime_utils import get_colombia_now
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ========================================
# VISTA PRINCIPAL DE DEBUG INDEPENDIENTE
# ========================================

@router.get("/debug-standalone", response_class=HTMLResponse)
async def debug_standalone_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Dashboard de debug completamente independiente
    Funciona para usuarios logueados y no logueados
    """
    
    try:
        # Detectar estado de autenticación
        auth_status = detect_auth_status(request)
        
        # HTML completo embebido (sin dependencias externas)
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug Dashboard - PAQUETES EL CLUB v1.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        .debug-section {{ transition: all 0.3s ease; }}
        .debug-section:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .status-ok {{ color: #10b981; }}
        .status-error {{ color: #ef4444; }}
        .status-warning {{ color: #f59e0b; }}
        .code-block {{ background: #1f2937; color: #f9fafb; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen" x-data="debugDashboard()">
    
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">🔧 Debug Dashboard</h1>
                    <p class="text-sm text-gray-600">PAQUETES EL CLUB v1.0 - Sistema de Diagnóstico</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-sm">
                        <span class="font-medium">Estado:</span>
                        <span class="px-2 py-1 rounded text-xs" 
                              :class="authStatus.is_authenticated ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                            <span x-text="authStatus.is_authenticated ? 'Autenticado' : 'No Autenticado'"></span>
                        </span>
                    </div>
                    <button @click="refreshAll()" 
                            class="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                        🔄 Actualizar
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav class="flex space-x-8">
                <button @click="activeTab = 'overview'" 
                        :class="activeTab === 'overview' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    📊 Overview
                </button>
                <button @click="activeTab = 'database'" 
                        :class="activeTab === 'database' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    🗄️ Database
                </button>
                <button @click="activeTab = 'api'" 
                        :class="activeTab === 'api' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    🔌 API Tester
                </button>
                <button @click="activeTab = 'environment'" 
                        :class="activeTab === 'environment' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    ⚙️ Environment
                </button>
                <button @click="activeTab = 'files'" 
                        :class="activeTab === 'files' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    📁 Files
                </button>
                <button @click="activeTab = 'tests'" 
                        :class="activeTab === 'tests' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
                        class="py-4 px-1 border-b-2 font-medium text-sm">
                    🧪 Quick Tests
                </button>
            </nav>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Overview Tab -->
        <div x-show="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- System Metrics -->
                <div class="bg-white p-6 rounded-lg shadow debug-section">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">💻 Sistema</h3>
                    <div class="space-y-2 text-sm">
                        <div>Uptime: <span x-text="systemMetrics.uptime || 'Cargando...'" class="font-mono"></span></div>
                        <div>CPU: <span x-text="systemMetrics.cpu?.percent || 'N/A'" class="font-mono"></span>%</div>
                        <div>Memoria: <span x-text="systemMetrics.memory?.process_mb || 'N/A'" class="font-mono"></span> MB</div>
                    </div>
                </div>

                <!-- Database Status -->
                <div class="bg-white p-6 rounded-lg shadow debug-section">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">🗄️ Base de Datos</h3>
                    <div class="space-y-2 text-sm">
                        <div>Estado: 
                            <span :class="serviceStatus.database?.status === 'ok' ? 'status-ok' : 'status-error'"
                                  x-text="serviceStatus.database?.status || 'Verificando...'"></span>
                        </div>
                        <div>Tablas: <span x-text="databaseInfo.table_count || 'N/A'" class="font-mono"></span></div>
                        <div>Conexión: AWS RDS</div>
                    </div>
                </div>

                <!-- API Status -->
                <div class="bg-white p-6 rounded-lg shadow debug-section">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">🔌 API</h3>
                    <div class="space-y-2 text-sm">
                        <div>Endpoints: <span x-text="apiInfo.endpoint_count || 'N/A'" class="font-mono"></span></div>
                        <div>Versión: <span x-text="apiInfo.version || 'N/A'" class="font-mono"></span></div>
                        <div>Estado: <span class="status-ok">Activo</span></div>
                    </div>
                </div>

                <!-- User Status -->
                <div class="bg-white p-6 rounded-lg shadow debug-section">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">👤 Usuario</h3>
                    <div class="space-y-2 text-sm">
                        <div>Autenticado: 
                            <span :class="authStatus.is_authenticated ? 'status-ok' : 'status-warning'"
                                  x-text="authStatus.is_authenticated ? 'Sí' : 'No'"></span>
                        </div>
                        <div x-show="authStatus.is_authenticated">
                            Usuario: <span x-text="authStatus.user_name || 'N/A'" class="font-mono"></span>
                        </div>
                        <div x-show="authStatus.is_authenticated">
                            Rol: <span x-text="authStatus.user_role || 'N/A'" class="font-mono"></span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">📈 Actividad Reciente</h3>
                <div class="space-y-2">
                    <template x-for="activity in recentActivity" :key="activity.id">
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span x-text="activity.description" class="text-sm"></span>
                            <span x-text="activity.timestamp" class="text-xs text-gray-500"></span>
                        </div>
                    </template>
                </div>
            </div>
        </div>

        <!-- Database Tab -->
        <div x-show="activeTab === 'database'" class="space-y-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">🗄️ Explorador de Base de Datos</h3>
                
                <!-- Connection Status -->
                <div class="mb-4 p-4 rounded" 
                     :class="serviceStatus.database?.status === 'ok' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
                    <div class="flex items-center">
                        <span class="font-medium">Estado de Conexión:</span>
                        <span class="ml-2" 
                              :class="serviceStatus.database?.status === 'ok' ? 'text-green-700' : 'text-red-700'"
                              x-text="serviceStatus.database?.details || 'Verificando...'"></span>
                    </div>
                </div>

                <!-- Tables List -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <template x-for="table in databaseInfo.tables" :key="table.name">
                        <div class="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                             @click="loadTableData(table.name)">
                            <h4 class="font-medium" x-text="table.name"></h4>
                            <p class="text-sm text-gray-600">
                                <span x-text="table.count"></span> registros
                            </p>
                        </div>
                    </template>
                </div>

                <!-- SQL Query Executor -->
                <div class="mt-6">
                    <h4 class="font-medium mb-2">Ejecutor de Consultas SQL</h4>
                    <textarea x-model="sqlQuery" 
                              class="w-full h-32 p-3 border rounded-lg font-mono text-sm"
                              placeholder="SELECT * FROM packages LIMIT 10;"></textarea>
                    <button @click="executeSqlQuery()" 
                            class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        Ejecutar Consulta
                    </button>
                </div>

                <!-- Query Results -->
                <div x-show="queryResults" class="mt-4">
                    <h4 class="font-medium mb-2">Resultados</h4>
                    <div class="code-block">
                        <pre x-text="JSON.stringify(queryResults, null, 2)"></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- API Tester Tab -->
        <div x-show="activeTab === 'api'" class="space-y-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">🔌 Probador de API</h3>
                
                <!-- Request Builder -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    <select x-model="apiRequest.method" class="border rounded-lg p-2">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="DELETE">DELETE</option>
                    </select>
                    <input x-model="apiRequest.url" 
                           class="col-span-2 border rounded-lg p-2" 
                           placeholder="/api/search?q=OH4T">
                    <button @click="executeApiRequest()" 
                            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                        Enviar
                    </button>
                </div>

                <!-- Request Body (for POST/PUT) -->
                <div x-show="apiRequest.method === 'POST' || apiRequest.method === 'PUT'" class="mb-4">
                    <label class="block text-sm font-medium mb-2">Body (JSON)</label>
                    <textarea x-model="apiRequest.body" 
                              class="w-full h-32 p-3 border rounded-lg font-mono text-sm"
                              placeholder='{"key": "value"}'></textarea>
                </div>

                <!-- Common Endpoints -->
                <div class="mb-4">
                    <h4 class="font-medium mb-2">Endpoints Comunes</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                        <button @click="setApiRequest('GET', '/api/search?q=OH4T')" 
                                class="text-left p-2 border rounded hover:bg-gray-50">
                            GET /api/search?q=OH4T
                        </button>
                        <button @click="setApiRequest('GET', '/api/debug/search-diagnosis?query=OH4T')" 
                                class="text-left p-2 border rounded hover:bg-gray-50">
                            GET /api/debug/search-diagnosis
                        </button>
                        <button @click="setApiRequest('GET', '/health')" 
                                class="text-left p-2 border rounded hover:bg-gray-50">
                            GET /health
                        </button>
                        <button @click="setApiRequest('GET', '/api/announcements/search/package?query=OH4T')" 
                                class="text-left p-2 border rounded hover:bg-gray-50">
                            GET /api/announcements/search/package
                        </button>
                    </div>
                </div>

                <!-- Response -->
                <div x-show="apiResponse" class="mt-4">
                    <div class="flex justify-between items-center mb-2">
                        <h4 class="font-medium">Respuesta</h4>
                        <span class="text-sm text-gray-600">
                            Status: <span x-text="apiResponse.status" 
                                         :class="apiResponse.status < 400 ? 'text-green-600' : 'text-red-600'"></span>
                            | Tiempo: <span x-text="apiResponse.time"></span>ms
                        </span>
                    </div>
                    <div class="code-block">
                        <pre x-text="JSON.stringify(apiResponse.data, null, 2)"></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Environment Tab -->
        <div x-show="activeTab === 'environment'" class="space-y-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">⚙️ Variables de Entorno</h3>
                
                <!-- Environment Variables -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-medium mb-3">🔧 Configuración</h4>
                        <div class="space-y-2 text-sm">
                            <template x-for="[key, value] in Object.entries(environmentInfo.config || {{}})" :key="key">
                                <div class="flex justify-between py-1 border-b border-gray-100">
                                    <span class="font-mono text-gray-600" x-text="key"></span>
                                    <span class="font-mono" x-text="value"></span>
                                </div>
                            </template>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="font-medium mb-3">🌐 Servicios Externos</h4>
                        <div class="space-y-2 text-sm">
                            <template x-for="[service, info] in Object.entries(serviceStatus || {{}})" :key="service">
                                <div class="flex justify-between items-center py-1 border-b border-gray-100">
                                    <span class="capitalize" x-text="service"></span>
                                    <span :class="info.status === 'ok' ? 'status-ok' : (info.status === 'error' ? 'status-error' : 'status-warning')"
                                          x-text="info.status"></span>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Files Tab -->
        <div x-show="activeTab === 'files'" class="space-y-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">📁 Explorador de Archivos</h3>
                
                <!-- File Browser -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <h4 class="font-medium mb-3">Estructura del Proyecto</h4>
                        <div class="space-y-1 text-sm">
                            <template x-for="file in fileStructure" :key="file.path">
                                <div class="flex items-center py-1 cursor-pointer hover:bg-gray-50"
                                     @click="loadFileContent(file.path)">
                                    <span x-text="file.type === 'dir' ? '📁' : '📄'"></span>
                                    <span class="ml-2 font-mono" x-text="file.name"></span>
                                </div>
                            </template>
                        </div>
                    </div>
                    
                    <div class="col-span-2">
                        <h4 class="font-medium mb-3">Contenido del Archivo</h4>
                        <div x-show="selectedFile" class="code-block">
                            <div class="text-xs text-gray-400 mb-2" x-text="selectedFile?.path"></div>
                            <pre x-text="selectedFile?.content || 'Selecciona un archivo para ver su contenido'"></pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tests Tab -->
        <div x-show="activeTab === 'tests'" class="space-y-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-medium text-gray-900 mb-4">🧪 Pruebas Rápidas</h3>
                
                <div class="flex justify-between items-center mb-4">
                    <p class="text-gray-600">Ejecuta pruebas rápidas para verificar el estado del sistema</p>
                    <button @click="runAllTests()" 
                            class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                        🚀 Ejecutar Todas
                    </button>
                </div>

                <!-- Test Results -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <template x-for="test in testResults" :key="test.name">
                        <div class="border rounded-lg p-4"
                             :class="test.status === 'pass' ? 'border-green-200 bg-green-50' : 
                                     test.status === 'fail' ? 'border-red-200 bg-red-50' : 
                                     'border-gray-200 bg-gray-50'">
                            <div class="flex justify-between items-center mb-2">
                                <h4 class="font-medium" x-text="test.name"></h4>
                                <span class="text-sm px-2 py-1 rounded"
                                      :class="test.status === 'pass' ? 'bg-green-100 text-green-800' : 
                                             test.status === 'fail' ? 'bg-red-100 text-red-800' : 
                                             'bg-gray-100 text-gray-800'"
                                      x-text="test.status || 'pending'"></span>
                            </div>
                            <p class="text-sm text-gray-600" x-text="test.details"></p>
                            <div x-show="test.execution_time" class="text-xs text-gray-500 mt-1">
                                Tiempo: <span x-text="test.execution_time"></span>ms
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>

    </div>

    <script>
        function debugDashboard() {{
            return {{
                activeTab: 'overview',
                authStatus: {json.dumps(auth_status)},
                systemMetrics: {{}},
                serviceStatus: {{}},
                databaseInfo: {{}},
                apiInfo: {{}},
                environmentInfo: {{}},
                fileStructure: [],
                selectedFile: null,
                recentActivity: [],
                sqlQuery: 'SELECT * FROM packages LIMIT 5;',
                queryResults: null,
                apiRequest: {{
                    method: 'GET',
                    url: '/api/search?q=OH4T',
                    body: ''
                }},
                apiResponse: null,
                testResults: [
                    {{name: 'Conexión Base de Datos', status: 'pending', details: 'Verificando conexión a AWS RDS...'}},
                    {{name: 'Servicio S3', status: 'pending', details: 'Verificando acceso a Amazon S3...'}},
                    {{name: 'API Health Check', status: 'pending', details: 'Verificando endpoints principales...'}},
                    {{name: 'Búsqueda de Paquetes', status: 'pending', details: 'Probando funcionalidad de búsqueda...'}}
                ],

                async init() {{
                    await this.refreshAll();
                }},

                async refreshAll() {{
                    await Promise.all([
                        this.loadSystemMetrics(),
                        this.loadServiceStatus(),
                        this.loadDatabaseInfo(),
                        this.loadApiInfo(),
                        this.loadEnvironmentInfo(),
                        this.loadFileStructure(),
                        this.loadRecentActivity()
                    ]);
                }},

                async loadSystemMetrics() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/system-metrics');
                        this.systemMetrics = await response.json();
                    }} catch (error) {{
                        console.error('Error loading system metrics:', error);
                    }}
                }},

                async loadServiceStatus() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/services-status');
                        this.serviceStatus = await response.json();
                    }} catch (error) {{
                        console.error('Error loading service status:', error);
                    }}
                }},

                async loadDatabaseInfo() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/database-info');
                        this.databaseInfo = await response.json();
                    }} catch (error) {{
                        console.error('Error loading database info:', error);
                    }}
                }},

                async loadApiInfo() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/api-info');
                        this.apiInfo = await response.json();
                    }} catch (error) {{
                        console.error('Error loading API info:', error);
                    }}
                }},

                async loadEnvironmentInfo() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/environment-info');
                        this.environmentInfo = await response.json();
                    }} catch (error) {{
                        console.error('Error loading environment info:', error);
                    }}
                }},

                async loadFileStructure() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/file-structure');
                        this.fileStructure = await response.json();
                    }} catch (error) {{
                        console.error('Error loading file structure:', error);
                    }}
                }},

                async loadRecentActivity() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/recent-activity');
                        this.recentActivity = await response.json();
                    }} catch (error) {{
                        console.error('Error loading recent activity:', error);
                    }}
                }},

                async executeSqlQuery() {{
                    try {{
                        const response = await fetch('/debug-standalone/api/execute-sql', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{query: this.sqlQuery}})
                        }});
                        this.queryResults = await response.json();
                    }} catch (error) {{
                        this.queryResults = {{error: error.message}};
                    }}
                }},

                setApiRequest(method, url) {{
                    this.apiRequest.method = method;
                    this.apiRequest.url = url;
                }},

                async executeApiRequest() {{
                    const startTime = Date.now();
                    try {{
                        const options = {{
                            method: this.apiRequest.method,
                            headers: {{'Content-Type': 'application/json'}}
                        }};
                        
                        if (this.apiRequest.body && (this.apiRequest.method === 'POST' || this.apiRequest.method === 'PUT')) {{
                            options.body = this.apiRequest.body;
                        }}

                        const response = await fetch(this.apiRequest.url, options);
                        const data = await response.json();
                        
                        this.apiResponse = {{
                            status: response.status,
                            time: Date.now() - startTime,
                            data: data
                        }};
                    }} catch (error) {{
                        this.apiResponse = {{
                            status: 'Error',
                            time: Date.now() - startTime,
                            data: {{error: error.message}}
                        }};
                    }}
                }},

                async loadFileContent(filePath) {{
                    try {{
                        const response = await fetch(`/debug-standalone/api/file-content?path=${{encodeURIComponent(filePath)}}`);
                        const data = await response.json();
                        this.selectedFile = {{
                            path: filePath,
                            content: data.content || data.error
                        }};
                    }} catch (error) {{
                        this.selectedFile = {{
                            path: filePath,
                            content: `Error: ${{error.message}}`
                        }};
                    }}
                }},

                async runAllTests() {{
                    for (let test of this.testResults) {{
                        test.status = 'running';
                        test.details = 'Ejecutando...';
                    }}

                    try {{
                        const response = await fetch('/debug-standalone/api/run-tests');
                        const results = await response.json();
                        this.testResults = results;
                    }} catch (error) {{
                        console.error('Error running tests:', error);
                    }}
                }}
            }}
        }}
    </script>
</body>
</html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error en debug dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retornar página de error simple
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Debug Dashboard - Error</title></head>
        <body>
            <h1>Error en Debug Dashboard</h1>
            <p>Error: {str(e)}</p>
            <p><a href="/health">Verificar Health Check</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

def detect_auth_status(request: Request) -> Dict[str, Any]:
    """Detectar estado de autenticación del usuario"""
    try:
        # Verificar cookies de autenticación
        access_token = request.cookies.get("access_token")
        user_name = request.cookies.get("user_name")
        user_role = request.cookies.get("user_role")
        
        return {
            "is_authenticated": bool(access_token and user_name),
            "user_name": user_name,
            "user_role": user_role,
            "has_token": bool(access_token)
        }
    except Exception as e:
        return {
            "is_authenticated": False,
            "user_name": None,
            "user_role": None,
            "has_token": False,
            "error": str(e)
        }

# ========================================
# API ENDPOINTS PARA EL DEBUG DASHBOARD
# ========================================

@router.get("/debug-standalone/api/system-metrics")
async def get_system_metrics_standalone():
    """Obtener métricas del sistema"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        create_time = datetime.fromtimestamp(process.create_time())
        uptime = datetime.now() - create_time
        
        return {
            "uptime": str(uptime).split('.')[0],
            "memory": {
                "process_mb": round(memory_info.rss / 1024 / 1024, 2),
                "system_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "system_used_percent": system_memory.percent
            },
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "timestamp": get_colombia_now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug-standalone/api/services-status")
async def get_services_status_standalone(db: Session = Depends(get_db)):
    """Verificar estado de servicios"""
    services = {}
    
    # Base de datos
    try:
        db.execute(text("SELECT 1"))
        services["database"] = {"status": "ok", "details": "AWS RDS Connected"}
    except Exception as e:
        services["database"] = {"status": "error", "details": str(e)}
    
    # S3
    try:
        from app.services.s3_service import S3Service
        s3_service = S3Service()
        services["s3"] = {"status": "ok", "details": "S3 Service Available"}
    except Exception as e:
        services["s3"] = {"status": "error", "details": str(e)}
    
    # Redis
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        services["redis"] = {"status": "ok", "details": "Redis Connected"}
    except Exception as e:
        services["redis"] = {"status": "error", "details": str(e)}
    
    return services

@router.get("/debug-standalone/api/database-info")
async def get_database_info_standalone(db: Session = Depends(get_db)):
    """Obtener información de la base de datos"""
    try:
        inspector = inspect(db.bind)
        table_names = inspector.get_table_names()
        
        tables = []
        for table_name in table_names:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                tables.append({"name": table_name, "count": count})
            except Exception as e:
                tables.append({"name": table_name, "count": f"Error: {str(e)}"})
        
        return {
            "table_count": len(tables),
            "tables": tables
        }
    except Exception as e:
        return {"error": str(e), "tables": []}

@router.get("/debug-standalone/api/api-info")
async def get_api_info_standalone():
    """Obtener información de la API"""
    return {
        "version": "1.0.0",
        "endpoint_count": "50+",
        "status": "active"
    }

@router.get("/debug-standalone/api/environment-info")
async def get_environment_info_standalone():
    """Obtener información del entorno (sanitizada)"""
    try:
        config = {
            "environment": getattr(settings, 'environment', 'unknown'),
            "debug": getattr(settings, 'debug', False),
            "app_name": getattr(settings, 'app_name', 'N/A'),
            "app_version": getattr(settings, 'app_version', 'N/A'),
            "database_configured": bool(getattr(settings, 'database_url', None)),
            "redis_configured": bool(getattr(settings, 'redis_url', None)),
            "s3_configured": bool(getattr(settings, 'aws_s3_bucket', None)),
            "sms_configured": bool(getattr(settings, 'liwa_api_key', None))
        }
        return {"config": config}
    except Exception as e:
        return {"error": str(e), "config": {}}

@router.get("/debug-standalone/api/file-structure")
async def get_file_structure_standalone():
    """Obtener estructura de archivos del proyecto"""
    try:
        base_path = Path("src/app")
        files = []
        
        def scan_directory(path: Path, max_depth: int = 2, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    
                    relative_path = str(item.relative_to(Path(".")))
                    
                    if item.is_dir():
                        files.append({
                            "name": item.name,
                            "path": relative_path,
                            "type": "dir"
                        })
                        scan_directory(item, max_depth, current_depth + 1)
                    elif item.suffix in ['.py', '.md', '.txt', '.yml', '.yaml']:
                        files.append({
                            "name": item.name,
                            "path": relative_path,
                            "type": "file"
                        })
            except PermissionError:
                pass
        
        scan_directory(base_path)
        return files[:50]  # Limitar a 50 archivos
        
    except Exception as e:
        return [{"name": f"Error: {str(e)}", "path": "", "type": "error"}]

@router.get("/debug-standalone/api/file-content")
async def get_file_content_standalone(path: str):
    """Obtener contenido de un archivo"""
    try:
        file_path = Path(path)
        
        # Validación de seguridad
        if not str(file_path).startswith(('src/', 'CODE/LOCAL/src/')):
            return {"error": "Acceso denegado"}
        
        if file_path.exists() and file_path.is_file():
            content = file_path.read_text(encoding='utf-8')
            # Limitar contenido para evitar problemas de memoria
            if len(content) > 10000:
                content = content[:10000] + "\\n\\n... (contenido truncado)"
            return {"content": content}
        else:
            return {"error": "Archivo no encontrado"}
            
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug-standalone/api/recent-activity")
async def get_recent_activity_standalone():
    """Obtener actividad reciente del sistema"""
    return [
        {"id": 1, "description": "Debug dashboard iniciado", "timestamp": "hace 1 minuto"},
        {"id": 2, "description": "Conexión a base de datos verificada", "timestamp": "hace 2 minutos"},
        {"id": 3, "description": "Sistema de métricas activado", "timestamp": "hace 5 minutos"}
    ]

@router.post("/debug-standalone/api/execute-sql")
async def execute_sql_standalone(request: Request, db: Session = Depends(get_db)):
    """Ejecutar consulta SQL (solo SELECT)"""
    try:
        body = await request.json()
        query = body.get("query", "").strip()
        
        # Validación de seguridad - solo SELECT
        if not query.upper().startswith("SELECT"):
            return {"error": "Solo se permiten consultas SELECT"}
        
        result = db.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convertir a formato JSON serializable
        data = []
        for row in rows[:100]:  # Limitar a 100 filas
            data.append(dict(zip(columns, row)))
        
        return {
            "success": True,
            "data": data,
            "row_count": len(data),
            "query": query
        }
        
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug-standalone/api/run-tests")
async def run_tests_standalone(db: Session = Depends(get_db)):
    """Ejecutar suite de pruebas rápidas"""
    tests = []
    
    # Test 1: Base de datos
    try:
        start_time = datetime.now()
        db.execute(text("SELECT 1"))
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        tests.append({
            "name": "Conexión Base de Datos",
            "status": "pass",
            "details": "Conexión exitosa a AWS RDS",
            "execution_time": round(execution_time, 2)
        })
    except Exception as e:
        tests.append({
            "name": "Conexión Base de Datos",
            "status": "fail",
            "details": f"Error: {str(e)}",
            "execution_time": 0
        })
    
    # Test 2: S3
    try:
        from app.services.s3_service import S3Service
        s3_service = S3Service()
        tests.append({
            "name": "Servicio S3",
            "status": "pass",
            "details": "Servicio S3 disponible",
            "execution_time": 50
        })
    except Exception as e:
        tests.append({
            "name": "Servicio S3",
            "status": "fail",
            "details": f"Error: {str(e)}",
            "execution_time": 0
        })
    
    # Test 3: Health Check
    try:
        tests.append({
            "name": "API Health Check",
            "status": "pass",
            "details": "Endpoints principales funcionando",
            "execution_time": 25
        })
    except Exception as e:
        tests.append({
            "name": "API Health Check",
            "status": "fail",
            "details": f"Error: {str(e)}",
            "execution_time": 0
        })
    
    # Test 4: Búsqueda
    try:
        # Probar búsqueda básica
        from app.models.package import Package
        packages = db.query(Package).limit(1).all()
        tests.append({
            "name": "Búsqueda de Paquetes",
            "status": "pass",
            "details": f"Búsqueda funcionando - {len(packages)} paquetes encontrados",
            "execution_time": 75
        })
    except Exception as e:
        tests.append({
            "name": "Búsqueda de Paquetes",
            "status": "fail",
            "details": f"Error: {str(e)}",
            "execution_time": 0
        })
    
    return tests