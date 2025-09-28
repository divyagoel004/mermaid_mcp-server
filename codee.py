from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import subprocess
import tempfile
import uuid
from fastapi_mcp import FastApiMCP
import base64
from cleanup_images import start_cleanup_daemon

start_cleanup_daemon()
app = FastAPI(title="Mermaid Renderer API")
mcp = FastApiMCP(app, include_operations=["Mermaid_render"])
mcp.mount()


base_url = os.getenv("BASE_URL", "")


class MermaidInput(BaseModel):
    code: str



# Create Puppeteer config if missing
puppeteer_config_path = "puppeteer-config.json"
if not os.path.exists(puppeteer_config_path):
    with open(puppeteer_config_path, "w") as f:
        f.write('{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}')

@app.post("/render-mermaid/")
def render_mermaid(data: MermaidInput, request: Request):
    # with tempfile.TemporaryDirectory() as tmpdir:
    #     input_file = os.path.join(tmpdir, "diagram.mmd")
    #     output_file = os.path.join(tmpdir, "diagram.png")

    #     # Write the Mermaid code to file
    #     with open(input_file, "w", encoding="utf-8") as f:
    #         f.write(data.code.strip())

        # Run Mermaid CLI using npx
        try:
            result = subprocess.run(
                [
                    "npx", "@mermaid-js/mermaid-cli",
                    "-i", input_file,
                    "-o", output_file,
                    "--outputFormat", "png",
                    "--scale", "3",
                    "--puppeteerConfigFile", puppeteer_config_path
                ],
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Mermaid rendering timed out.")

        if result.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Mermaid CLI error:\n{result.stderr}"
            )

        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Output image not generated.")

        # Encode PNG as base64
        with open(output_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        return {"image_base64": encoded_string}

@app.get("/image/{file_id}")
def get_rendered_image(file_id: str):
    image_path = f"output_images/{file_id}.png"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(image_path, media_type="image/png")

@app.get("/image/{file_id}")
def get_rendered_image(file_id: str):
    image_path = f"output_images/{file_id}.png"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(image_path, media_type="image/png")


@app.post("/greeting/{name}")
def get_greeting(name: str):
    return {"message": f"Hello, {name}!"}

is_ready = False

@app.on_event("startup")
async def startup():
    global is_ready
    mcp.setup_server()




