# -*- coding: utf-8 -*-
"""
Created on Fri May  5 09:17:14 2023

@author: s.Shaji
"""
import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx


def generateSampleQuads(cols=9):
    pos = np.dstack(np.meshgrid(np.arange(cols), np.arange(2))).reshape(-1, 2)
    z = np.abs([*np.arange(-cols/2, cols/2), *np.arange(-cols/2, cols/2)])
    pos = np.c_[pos, z].astype('f')
    n1 = np.arange(cols)
    n2 = np.full(cols-1, 0)
    n3 = np.full(cols-1, 1)
    idx = np.dstack((n1[:-1], n2, n1[:-1], n3, n1[1:],
                    n3, n1[1:], n2)).reshape(-1, 2)
    indices = (idx[:, 0] + idx[:, 1]*cols).reshape(-1, 4)
    return pos, indices


canvas = WgpuCanvas(title = "Mesh Object with quads. Press 1,2 or 3 for wireframe, per vertex coloring or per face coloring")
renderer = gfx.renderers.WgpuRenderer(canvas)

# Show something
scene = gfx.Scene()
camera = gfx.PerspectiveCamera()

controller = gfx.OrbitController(
    camera=camera, register_events=renderer)
controller.controls['mouse3'] = ('pan', 'drag', (1.0, 1.0))

# Generate Sample quads and draw them
pos, indices = generateSampleQuads()
colors = np.repeat(pos[:, -1]/pos[:, -1].max(), 4).reshape(-1, 4)
colors[:, -1] = 1

patches = gfx.Mesh(
    gfx.Geometry(indices=indices,
                 positions=pos,
                 colors=colors,
                 texcoords=np.arange(len(indices))),
    gfx.MeshBasicMaterial(wireframe=True)
)

sphere = gfx.Mesh(
    gfx.sphere_geometry(0.1),
    gfx.MeshBasicMaterial(color="yellow"),
)

scene.add(patches, sphere)
camera.show_object(patches)

# Let there be ...
scene.add(gfx.AmbientLight())
light = gfx.DirectionalLight()
light.local.position = (0, 0, 1)

# Create a contrasting background
clr = [i/255 for i in [87,188,200,255]]
background = gfx.Background(
    None, gfx.BackgroundMaterial(clr))
scene.add(background)

def make_wireframe():
    patches.material.wireframe = True
    patches.material.vertex_colors = False


def make_vertex_color():
    patches.material.wireframe = False
    patches.material.vertex_colors = True


def make_face_color():
    patches.material.vertex_colors = False
    patches.material.face_colors = True


@renderer.add_event_handler("key_down")
def on_key(e):
    if e.key == "1":
        make_wireframe()
    elif e.key == "2":
        make_vertex_color()
    elif e.key == "3":
        make_face_color()


@renderer.add_event_handler("click")
def pick_id(event):
    # print(event.pick_info)
    if event.pick_info["world_object"] is patches:
        face_index = event.pick_info["face_index"]
        face_coord = event.pick_info["face_coord"]
        vertex_indices = patches.geometry.positions.data[face_index]
        positions = [patches.geometry.positions.data[int(i)] for i in vertex_indices]
        pos = sum(p * w for p, w in zip(positions, face_coord)) / sum(face_coord)
        sphere.local.position = pos
        print(pos)


def animate():
    renderer.render(scene, camera)
    canvas.request_draw()


if __name__ == "__main__":
    canvas.request_draw(animate)
    run()
