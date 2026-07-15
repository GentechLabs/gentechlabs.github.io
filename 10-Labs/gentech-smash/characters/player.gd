extends CharacterBody3D

# GenTech Smash — Player Character
# Simple N64-style character with a body and head

var character_name: String = "KAGE"
var speed: float = 6.0

func _ready():
	build_mesh()

func build_mesh():
	# Body
	var body = MeshInstance3D.new()
	body.mesh = BoxMesh.new()
	body.mesh.size = Vector3(0.6, 0.8, 0.4)
	body.position = Vector3(0, 0.4, 0)
	var body_mat = StandardMaterial3D.new()
	match character_name:
		"KAGE":
			body_mat.albedo_color = Color(0.8, 0.1, 0.1)  # Crimson
		"HIKARI":
			body_mat.albedo_color = Color(0.9, 0.7, 0.9)  # Light purple
		"Forge":
			body_mat.albedo_color = Color(0.2, 0.6, 0.9)  # Blue
		_:
			body_mat.albedo_color = Color(0.5, 0.5, 0.5)
	body.material_override = body_mat
	add_child(body)
	
	# Head
	var head = MeshInstance3D.new()
	head.mesh = SphereMesh.new()
	head.mesh.radius = 0.2
	head.mesh.height = 0.4
	head.position = Vector3(0, 0.9, 0)
	var head_mat = StandardMaterial3D.new()
	head_mat.albedo_color = Color(1.0, 0.8, 0.6)  # Skin tone
	head.material_override = head_mat
	add_child(head)
	
	# Racket (tennis racket in hand)
	var racket = MeshInstance3D.new()
	racket.mesh = BoxMesh.new()
	racket.mesh.size = Vector3(0.05, 0.4, 0.3)
	racket.position = Vector3(0.4, 0.5, 0.2)
	var racket_mat = StandardMaterial3D.new()
	racket_mat.albedo_color = Color(0.9, 0.9, 0.9)
	racket.material_override = racket_mat
	add_child(racket)
