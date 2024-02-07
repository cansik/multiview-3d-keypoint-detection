import math
import random

import gradio as gr
import open3d
from open3d import geometry
from open3d.visualization import rendering

from muke.rendering.GfxRenderer import GfxRenderer


def generate_image():
    gfx_scene = GfxRenderer(512, 512)

    model: rendering.TriangleMeshModel = open3d.io.read_triangle_model("assets/woman-old2-small/woman-old2.obj")
    mesh_info: rendering.TriangleMeshModel.MeshInfo = model.meshes[0]
    mesh: geometry.TriangleMesh = mesh_info.mesh
    material = model.materials[mesh_info.material_idx]

    gfx_scene.add_geometry(mesh, material)
    gfx_scene.rotate_scene(0, random.random() * 360, 0)

    return gfx_scene.render()


demo = gr.Interface(
    fn=generate_image,
    inputs=[],
    outputs=["image"],
    allow_flagging="never"
)

demo.launch(server_name="0.0.0.0", server_port=7860)
