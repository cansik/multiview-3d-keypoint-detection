import open3d
import pygfx as gfx
import trimesh
from open3d import geometry
from open3d.visualization import rendering
from trimesh import Trimesh

a: Trimesh = trimesh.load("assets/woman-old2-small/woman-old2.obj")
# a.show()

geo = gfx.geometry_from_trimesh(a)
# tex = gfx.material_from_trimesh(a.visual.material)

from wgpu.gui.auto import WgpuCanvas, run

from muke.rendering.GfxRenderer import GfxRenderer

canvas = WgpuCanvas()
gfx_scene = GfxRenderer(1024, 1024, canvas=canvas)

controller = gfx.OrbitController(gfx_scene.camera, register_events=gfx_scene.renderer)

state = {}

# model: rendering.TriangleMeshModel = open3d.io.read_triangle_model("assets/woman-old2/woman-old2.obj")
model: rendering.TriangleMeshModel = open3d.io.read_triangle_model("assets/woman-old2-small/woman-old2.obj")
mesh_info: rendering.TriangleMeshModel.MeshInfo = model.meshes[0]
mesh: geometry.TriangleMesh = mesh_info.mesh
material = model.materials[mesh_info.material_idx]

gfx_scene.add_geometry(mesh, material)


def on_key_down(event):
    global state
    if event.key == "s":
        state = gfx_scene.camera.get_state()
    elif event.key == "l":
        gfx_scene.camera.set_state(state)
    elif event.key == "r":
        gfx_scene.camera.show_object(gfx_scene.scene)


gfx_scene.renderer.add_event_handler(on_key_down, "key_down")


def animate():
    gfx_scene.renderer.render(gfx_scene.scene, gfx_scene.camera)
    canvas.request_draw()


if __name__ == "__main__":
    canvas.request_draw(animate)
    run()
