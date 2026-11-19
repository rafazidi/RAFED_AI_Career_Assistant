import sys
from pathlib import Path

import gradio as gr


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app as fastapi_app


gr.mount_gradio_app(
    fastapi_app,
    gr.Interface(
        fn=lambda message: "Utilisez l'API POST /api/chat.",
        inputs=gr.Textbox(label="API status"),
        outputs=gr.Textbox(),
        title="Rafed AI API",
    ),
    path="/demo",
)
