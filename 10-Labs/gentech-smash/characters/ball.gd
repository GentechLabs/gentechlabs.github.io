extends RigidBody3D

# GenTech Smash — Tennis Ball

func _ready():
	build_mesh()
	gravity_scale = 1.0
	contact_monitor = true
	max_contacts_reported = 10

func build_mesh():
	var mesh = MeshInstance3D.new()
	mesh.mesh = SphereMesh.new()
	mesh.mesh.radius = 0.12
	mesh.mesh.height = 0.24
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.9, 0.9, 0.2)  # Tennis ball yellow
	mat.metallic = 0.0
	mat.roughness = 0.8
	mesh.material_override = mat
	add_child(mesh)
	
	# Trail/glow effect
	var glow = MeshInstance3D.new()
	glow.mesh = SphereMesh.new()
	glow.mesh.radius = 0.2
	glow.mesh.height = 0.4
	var glow_mat = StandardMaterial3D.new()
	glow_mat.albedo_color = Color(0.9, 0.9, 0.2, 0.3)
	glow_mat.transparency = 0.7
	glow.material_override = glow_mat
	glow.position = Vector3(0, 0, 0)
	add_child(glow)
