from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

from src.core.models import PdfFile


class PreviewWidget(QWidget):
    page_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.current_pdf: PdfFile = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView()
        self.view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        self.view.page().setBackgroundColor(Qt.white)

        # Load PDF.js viewer
        viewer_path = Path(__file__).parent.parent.parent / "resources" / "viewer.html"
        if viewer_path.exists():
            self.view.setUrl(QUrl.fromLocalFile(str(viewer_path)))
        else:
            self.view.setHtml(self._default_viewer_html())

        layout.addWidget(self.view)

    def _default_viewer_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { margin: 0; padding: 20px; background: #f0f0f0; font-family: sans-serif; }
                .viewer { background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                canvas { display: block; }
                .page { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div id="viewer" class="viewer"></div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.js"></script>
            <script>
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.js';
                let pdfDoc = null;
                function render(url) {
                    pdfjsLib.getDocument(url).promise.then(doc => {
                        pdfDoc = doc;
                        renderAll();
                    });
                }
                function renderAll() {
                    const viewer = document.getElementById('viewer');
                    viewer.innerHTML = '';
                    for (let i = 1; i <= pdfDoc.numPages; i++) {
                        renderPage(i);
                    }
                }
                function renderPage(num) {
                    pdfDoc.getPage(num).then(page => {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        const viewport = page.getViewport({scale: 1.5});
                        canvas.width = viewport.width;
                        canvas.height = viewport.height;
                        const div = document.createElement('div');
                        div.className = 'page';
                        div.appendChild(canvas);
                        document.getElementById('viewer').appendChild(div);
                        page.render({canvasContext: ctx, viewport: viewport});
                    });
                }
                window.renderPdf = render;
            </script>
        </body>
        </html>
        """

    def load_pdf(self, pdf: PdfFile):
        self.current_pdf = pdf
        if pdf and pdf.path.exists():
            # Use file:// URL for PDF.js
            file_url = f"file:///{pdf.path.as_posix()}"
            self.view.page().runJavaScript(f"renderPdf('{file_url}')")


    def go_to_page(self, page: int):
        self.view.page().runJavaScript(f"""
            document.querySelectorAll('.page')[{page}].scrollIntoView();
        """)