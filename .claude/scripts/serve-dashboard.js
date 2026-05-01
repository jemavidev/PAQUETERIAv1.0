#!/usr/bin/env node

/**
 * BetterAgents Dashboard Server
 * Serves the memory dashboard with CORS support.
 *
 * Single-project mode  (MULTI_PROJECT unset / false):
 *   Reads from MEMORY_DIR (default: <cwd>/../memory)
 *
 * Multi-project mode (MULTI_PROJECT=true):
 *   Reads from PROJECTS_BASE/<project-name>/ subdirectories.
 *   API endpoints:
 *     GET /api/projects             → list all registered projects
 *     GET /api/project/:name/data   → combined JSON data for a project
 *     GET /memory/:name/:file       → raw file from a project's memory dir
 *     GET /memory/:file             → raw file from root memory (compat)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const PORT = parseInt(process.env.PORT || '3000');

// PROJECTS_JSON: path to ~/.betteragents/projects.json (Node.js multi-project mode)
// MULTI_PROJECT: set to 'true' for Docker mode (projects mounted as subdirs under MEMORY_DIR)
const PROJECTS_JSON_PATH = process.env.PROJECTS_JSON || null;
const MULTI_PROJECT = process.env.MULTI_PROJECT === 'true' || !!PROJECTS_JSON_PATH;

// In multi-project mode the container mounts each project at /memory/<name>/
// In single-project mode we fall back to the classic MEMORY_DIR location.
const PROJECTS_BASE = process.env.MEMORY_DIR || '/memory';
const MEMORY_DIR = process.env.MEMORY_DIR || path.join(__dirname, '..', 'memory');

// Cache for projects.json data (refreshed on each request)
function loadProjectsJson() {
  if (!PROJECTS_JSON_PATH) return null;
  try {
    return JSON.parse(fs.readFileSync(PROJECTS_JSON_PATH, 'utf8'));
  } catch (_) {
    return null;
  }
}

// The dashboard HTML is served from /app/ inside the container, or from the
// script's own directory when running locally.
const APP_DIR = path.join(__dirname);
const TEMPLATES_DIR = process.env.TEMPLATES_DIR || path.join(__dirname, '..', '..', 'templates');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Return an ISO-8601 datetime string from the first line of session-last.md.
 * Expected first line format: "# Last session — YYYY-MM-DD HH:MM"
 */
function readLastActive(projectMemoryPath) {
  try {
    const sessionFile = path.join(projectMemoryPath, 'session-last.md');
    const content = fs.readFileSync(sessionFile, 'utf8');
    const firstLine = content.split('\n')[0] || '';
    // Extract "YYYY-MM-DD HH:MM" pattern
    const match = firstLine.match(/(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})/);
    return match ? match[1] : null;
  } catch (_) {
    return null;
  }
}

/**
 * Scan PROJECTS_BASE for subdirectories; each one is a registered project.
 */
function discoverProjects() {
  // Mode A: read from ~/.betteragents/projects.json (Node.js multi-project)
  if (PROJECTS_JSON_PATH) {
    const data = loadProjectsJson();
    if (!data) return [];
    return (data.projects || []).map(p => ({
      name: p.name,
      last_active: readLastActive(p.memory_path),
      status: fs.existsSync(p.memory_path) ? 'reachable' : 'unreachable',
      path: p.memory_path,
    }));
  }
  // Mode B: scan subdirectories (Docker mode — each project mounted under PROJECTS_BASE)
  try {
    const entries = fs.readdirSync(PROJECTS_BASE, { withFileTypes: true });
    return entries
      .filter(e => e.isDirectory())
      .map(e => {
        const projectPath = path.join(PROJECTS_BASE, e.name);
        return {
          name: e.name,
          last_active: readLastActive(projectPath),
          status: 'reachable',
          path: projectPath,
        };
      });
  } catch (_) {
    return [];
  }
}

// Return the resolved memory directory for a named project
function getProjectMemoryPath(projectName) {
  if (PROJECTS_JSON_PATH) {
    const data = loadProjectsJson();
    const proj = (data && data.projects || []).find(p => p.name === projectName);
    return proj ? proj.memory_path : null;
  }
  return path.join(PROJECTS_BASE, projectName);
}

/**
 * Read all JSON files from a project's memory directory and return them as
 * a combined object keyed by filename (without .json extension).
 */
function readProjectData(projectName) {
  const projectPath = getProjectMemoryPath(projectName) || path.join(PROJECTS_BASE, projectName);
  const result = {};
  try {
    const entries = fs.readdirSync(projectPath, { withFileTypes: true });
    entries
      .filter(e => e.isFile() && e.name.endsWith('.json'))
      .forEach(e => {
        const key = e.name.replace(/\.json$/, '');
        try {
          const raw = fs.readFileSync(path.join(projectPath, e.name), 'utf8');
          result[key] = JSON.parse(raw);
        } catch (_) {
          result[key] = {};
        }
      });
  } catch (_) {
    // Project dir not accessible — return empty result
  }
  return result;
}

/**
 * Resolve requested file path and verify it is inside an allowed directory.
 * Returns null if the resolved path escapes the allowed roots.
 */
function resolveFilePath(pathname) {
  let filePath;

  if (MULTI_PROJECT) {
    // /memory/<project>/<file>  → resolved memory path for that project + file
    const multiMatch = pathname.match(/^\/memory\/([^/]+)\/(.+)$/);
    if (multiMatch) {
      const base = getProjectMemoryPath(multiMatch[1]) || path.join(PROJECTS_BASE, multiMatch[1]);
      filePath = path.join(base, multiMatch[2]);
    } else if (pathname.startsWith('/memory/')) {
      // /memory/<file>  → single-project compat (root of PROJECTS_BASE)
      filePath = path.join(PROJECTS_BASE, pathname.replace('/memory/', ''));
    } else if (pathname.startsWith('/.claude/memory/')) {
      filePath = path.join(PROJECTS_BASE, pathname.replace('/.claude/memory/', ''));
    } else {
      // All other paths → /app/ (dashboard HTML, etc.)
      filePath = path.join(APP_DIR, pathname.replace(/^\//, ''));
    }
  } else {
    // Single-project mode — original routing
    if (pathname.startsWith('/memory/')) {
      filePath = path.join(MEMORY_DIR, pathname.replace('/memory/', ''));
    } else if (pathname.startsWith('/.claude/memory/')) {
      filePath = path.join(MEMORY_DIR, pathname.replace('/.claude/memory/', ''));
    } else {
      filePath = path.join(TEMPLATES_DIR, pathname);
    }
  }

  // Resolve symlinks / .. to prevent traversal
  const resolved = path.resolve(filePath);

  // Check against all allowed roots
  let allowedRoots;
  if (MULTI_PROJECT) {
    allowedRoots = [path.resolve(APP_DIR)];
    if (PROJECTS_JSON_PATH) {
      // Allow each registered project's memory path
      const data = loadProjectsJson();
      (data && data.projects || []).forEach(p => {
        if (p.memory_path) allowedRoots.push(path.resolve(p.memory_path));
      });
    } else {
      allowedRoots.push(path.resolve(PROJECTS_BASE));
    }
  } else {
    allowedRoots = [path.resolve(MEMORY_DIR), path.resolve(TEMPLATES_DIR)];
  }

  const allowed = allowedRoots.some(root => resolved.startsWith(root));
  return allowed ? resolved : null;
}

// ---------------------------------------------------------------------------
// Request handler
// ---------------------------------------------------------------------------
const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://localhost:${PORT}`);
  let pathname = parsedUrl.pathname;

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // -----------------------------------------------------------------------
  // API: /api/projects
  // -----------------------------------------------------------------------
  if (pathname === '/api/projects' && MULTI_PROJECT) {
    const projects = discoverProjects();
    const current = projects.length > 0 ? projects[0].name : null;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ projects, current }));
    return;
  }

  // -----------------------------------------------------------------------
  // API: /api/project/:name/data
  // -----------------------------------------------------------------------
  const projectDataMatch = pathname.match(/^\/api\/project\/([^/]+)\/data$/);
  if (projectDataMatch && MULTI_PROJECT) {
    const projectName = projectDataMatch[1];
    // Prevent path traversal in project name
    if (/[^a-zA-Z0-9_\-]/.test(projectName)) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid project name' }));
      return;
    }
    const data = readProjectData(projectName);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
    return;
  }

  // -----------------------------------------------------------------------
  // API: DELETE /api/project/:name - Remove project from registry
  // -----------------------------------------------------------------------
  const projectDeleteMatch = pathname.match(/^\/api\/project\/([^/]+)$/);
  if (projectDeleteMatch && req.method === 'DELETE' && MULTI_PROJECT && !PROJECTS_JSON_PATH) {
    // Docker subdir mode — no projects.json mounted, can't delete via API
    res.writeHead(501, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Delete not supported: run generate-central-compose.sh --unregister <name> on the host instead.' }));
    return;
  }
  if (projectDeleteMatch && req.method === 'DELETE' && MULTI_PROJECT && PROJECTS_JSON_PATH) {
    const projectName = projectDeleteMatch[1];

    if (/[^a-zA-Z0-9_\-]/.test(projectName)) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid project name' }));
      return;
    }

    try {
      const data = loadProjectsJson();
      if (!data || !data.projects) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Projects file not found' }));
        return;
      }

      const projectIndex = data.projects.findIndex(p => p.name === projectName);
      if (projectIndex === -1) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Project not found' }));
        return;
      }

      data.projects.splice(projectIndex, 1);
      fs.writeFileSync(PROJECTS_JSON_PATH, JSON.stringify(data, null, 2), 'utf8');

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        message: `Project "${projectName}" removed from registry`,
        remaining: data.projects.length
      }));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Failed to update projects file', details: err.message }));
    }
    return;
  }

  // -----------------------------------------------------------------------
  // Dashboard HTML
  // -----------------------------------------------------------------------
  if (pathname === '/' || pathname === '/dashboard') {
    if (MULTI_PROJECT) {
      // Serve from /app/dashboard.html
      const htmlPath = path.resolve(path.join(APP_DIR, 'dashboard.html'));
      if (!htmlPath.startsWith(path.resolve(APP_DIR))) {
        res.writeHead(403, { 'Content-Type': 'text/plain' });
        res.end('Access denied');
        return;
      }
      fs.readFile(htmlPath, (err, data) => {
        if (err) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('Dashboard not found');
          return;
        }
        res.writeHead(200, {
          'Content-Type': 'text/html',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        });
        res.end(data);
      });
      return;
    } else {
      pathname = '/memory/dashboard.html';
    }
  }

  // -----------------------------------------------------------------------
  // Static file serving
  // -----------------------------------------------------------------------
  const filePath = resolveFilePath(pathname);

  if (!filePath) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Access denied');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        if (filePath.endsWith('.json')) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end('{}');
          return;
        }
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('500 Server Error');
      }
      return;
    }

    let contentType = 'text/html';
    if (filePath.endsWith('.json')) contentType = 'application/json';
    else if (filePath.endsWith('.js')) contentType = 'application/javascript';
    else if (filePath.endsWith('.css')) contentType = 'text/css';
    else if (filePath.endsWith('.md')) contentType = 'text/plain';

    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
server.listen(PORT, () => {
  if (MULTI_PROJECT) {
    const projects = discoverProjects();
    console.log(`\n🚀 BetterAgents Dashboard Server`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`🌐 Mode: Multi-project (${projects.length} project(s) detected)`);
    console.log(`📊 Dashboard: http://localhost:${PORT}`);
    console.log(`🔌 API: http://localhost:${PORT}/api/projects`);
    if (projects.length > 0) {
      console.log(`\nProjects:`);
      projects.forEach(p => console.log(`  • ${p.name}  →  ${p.path}`));
    }
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  } else {
    console.log(`\n🚀 BetterAgents Dashboard Server`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`📊 Dashboard: http://localhost:${PORT}`);
    console.log(`📁 Memory Files: http://localhost:${PORT}/memory/*`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  }
  console.log(`Press Ctrl+C to stop\n`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use`);
    console.error(`Try: lsof -i :${PORT} && kill -9 <PID>`);
  } else {
    console.error('Server error:', err);
  }
  process.exit(1);
});
