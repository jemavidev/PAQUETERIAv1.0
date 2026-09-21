# -*- coding: utf-8 -*-
"""
Cámara simulada para el seam de navegador real (`.scratch/captura-guia-lector-camara`, ticket 05).

Un CI (y esta máquina) no tiene cámara, y aunque la tuviera no se puede poner un código de barras
frente a ella. Este helper SUSTITUYE `navigator.mediaDevices.getUserMedia` en la página de prueba:

  - `con_error("NotAllowedError")`: la cámara rechaza como lo haría un navegador real (permiso negado,
    sin dispositivo, en uso por otra app...). El nombre es el `DOMException.name` estándar.
  - `con_video()` / `con_video("TEXTO")`: entrega un flujo de video REAL (un `MediaStream` de un
    lienzo). Con texto, dibuja un QR con ese contenido (generado con el propio ZXing vendorizado, el
    mismo que decodifica en la app), así que el escáner lo lee de verdad, de punta a punta.
  - `estado()`: cuántas veces se pidió la cámara, con qué restricciones y en qué estado quedó cada pista
    de cada flujo (`live` o `ended`) -- para comprobar que nada queda encendido.

Se instala con `add_init_script` (sobrevive a las navegaciones) y también en el documento actual. La
configuración se cambia en cualquier momento, incluso entre dos clics en "Escanear".

Uso (el fixture `camara` de `conftest.py` ya lo deja instalado):

    def test_algo(app_viva, pagina, camara):
        ...abrir el modal...
        camara.con_error("NotAllowedError")
        pagina.click("... .scan-btn")
"""

_INSTALADOR = """
(() => {
  if (window.__camara) return;  // ya instalada en este documento
  const camara = { cfg: { modo: 'video', texto: null }, llamadas: 0, restricciones: [], flujos: [] };
  window.__camara = camara;

  async function cargarZXing() {
    if (window.ZXing) return;
    await new Promise((ok, fallo) => {
      const s = document.createElement('script');
      s.src = '/static/vendor/zxing.min.js';
      s.onload = ok;
      s.onerror = fallo;
      document.head.appendChild(s);
    });
  }

  async function fabricarFlujo(texto) {
    const lienzo = document.createElement('canvas');
    lienzo.width = 480;
    lienzo.height = 480;
    const ctx = lienzo.getContext('2d');
    let img = null;
    if (texto) {
      await cargarZXing();
      const svg = new ZXing.BrowserQRCodeSvgWriter().write(texto, 320, 320);
      const xml = new XMLSerializer().serializeToString(svg);
      img = new Image();
      await new Promise((ok, fallo) => {
        img.onload = ok;
        img.onerror = fallo;
        img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(xml);
      });
    }
    const dibujar = () => {
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, 480, 480);
      if (img) ctx.drawImage(img, 80, 80, 320, 320);
    };
    dibujar();
    setInterval(dibujar, 100);  // mantiene fotogramas nuevos fluyendo, como una cámara real
    return lienzo.captureStream(10);
  }

  const pedirCamara = async (restricciones) => {
    camara.llamadas++;
    camara.restricciones.push(restricciones);
    if (camara.cfg.modo === 'error') {
      throw new DOMException('Cámara simulada: ' + camara.cfg.error, camara.cfg.error);
    }
    const flujo = await fabricarFlujo(camara.cfg.texto);
    camara.flujos.push(flujo);
    return flujo;
  };
  if (navigator.mediaDevices) navigator.mediaDevices.getUserMedia = pedirCamara;
})()
"""


class CamaraSimulada:
    def __init__(self, pagina):
        self._pagina = pagina

    def instalar(self):
        self._pagina.add_init_script(_INSTALADOR)
        self._pagina.evaluate(_INSTALADOR)  # el documento actual (about:blank al arrancar)
        return self

    def con_error(self, nombre):
        """La cámara rechaza con un `DOMException` de este nombre (NotAllowedError, NotFoundError...)."""
        self._pagina.evaluate(
            "n => { window.__camara.cfg = { modo: 'error', error: n }; }", nombre
        )

    def con_video(self, texto=None):
        """La cámara entrega un flujo real; con `texto`, con un QR de ese contenido a la vista."""
        self._pagina.evaluate(
            "t => { window.__camara.cfg = { modo: 'video', texto: t }; }", texto
        )

    def estado(self):
        return self._pagina.evaluate(
            """() => ({
                llamadas: window.__camara.llamadas,
                restricciones: window.__camara.restricciones,
                pistas: window.__camara.flujos.map(f => f.getTracks().map(t => t.readyState)),
            })"""
        )
