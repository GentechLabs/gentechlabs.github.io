extends Node3D

# GenTech Smash — Main Game Scene
# N64-style tennis with original characters

# ── Court dimensions ──
const COURT_LENGTH = 24.0
const COURT_WIDTH = 10.0
const NET_HEIGHT = 1.0
const WALL_HEIGHT = 4.0

# ── Players ──
var player1: CharacterBody3D
var player2: CharacterBody3D
var ball: RigidBody3D

# ── Game state ──
var score_p1: int = 0
var score_p2: int = 0
var serving: bool = true
var server: int = 1  # 1 = player1, 2 = player2
var game_state: String = "menu"  # menu, playing, point_scored, game_over

# ── Input ──
var p1_move_dir: Vector2 = Vector2.ZERO
var p1_swing: bool = false

func _ready():
	build_court()
	spawn_players()
	spawn_ball()
	show_menu()

func build_court():
	# Ground
	var ground = MeshInstance3D.new()
	ground.mesh = BoxMesh.new()
	ground.mesh.size = Vector3(COURT_WIDTH + 4, 0.2, COURT_LENGTH + 4)
	ground.position = Vector3(0, -0.1, 0)
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.2, 0.5, 0.2)  # Grass green
	ground.material_override = mat
	add_child(ground)
	
	# Court surface
	var court = MeshInstance3D.new()
	court.mesh = BoxMesh.new()
	court.mesh.size = Vector3(COURT_WIDTH, 0.05, COURT_LENGTH)
	court.position = Vector3(0, 0.05, 0)
	var court_mat = StandardMaterial3D.new()
	court_mat.albedo_color = Color(0.15, 0.4, 0.15)
	court.material_override = court_mat
	add_child(court)
	
	# Court lines (white strips)
	var line_mat = StandardMaterial3D.new()
	line_mat.albedo_color = Color.WHITE
	
	# Center line
	var center_line = MeshInstance3D.new()
	center_line.mesh = BoxMesh.new()
	center_line.mesh.size = Vector3(0.05, 0.02, COURT_LENGTH)
	center_line.position = Vector3(0, 0.06, 0)
	center_line.material_override = line_mat
	add_child(center_line)
	
	# Net
	var net = MeshInstance3D.new()
	net.mesh = BoxMesh.new()
	net.mesh.size = Vector3(COURT_WIDTH + 0.5, NET_HEIGHT, 0.05)
	net.position = Vector3(0, NET_HEIGHT / 2, 0)
	var net_mat = StandardMaterial3D.new()
	net_mat.albedo_color = Color.WHITE
	net_mat.metallic = 0.5
	net.material_override = net_mat
	add_child(net)
	
	# Net posts
	for z in [-1, 1]:
		var post = MeshInstance3D.new()
		post.mesh = CylinderMesh.new()
		post.mesh.top_radius = 0.05
		post.mesh.bottom_radius = 0.05
		post.mesh.height = NET_HEIGHT
		post.position = Vector3(z * (COURT_WIDTH / 2 + 0.3), NET_HEIGHT / 2, 0)
		var post_mat = StandardMaterial3D.new()
		post_mat.albedo_color = Color.WHITE
		post.material_override = post_mat
		add_child(post)
	
	# Walls (invisible collision)
	var wall_mat = StandardMaterial3D.new()
	wall_mat.albedo_color = Color(0.1, 0.1, 0.2)
	wall_mat.transparency = 0.8
	
	for z in [-COURT_LENGTH/2 - 0.5, COURT_LENGTH/2 + 0.5]:
		var wall = StaticBody3D.new()
		var shape = CollisionShape3D.new()
		shape.shape = BoxShape3D.new()
		shape.shape.size = Vector3(COURT_WIDTH + 2, WALL_HEIGHT, 0.2)
		wall.add_child(shape)
		wall.position = Vector3(0, WALL_HEIGHT / 2, z)
		add_child(wall)
		
		var vis = MeshInstance3D.new()
		vis.mesh = BoxMesh.new()
		vis.mesh.size = Vector3(COURT_WIDTH + 2, WALL_HEIGHT, 0.2)
		vis.position = Vector3(0, WALL_HEIGHT / 2, z)
		vis.material_override = wall_mat
		add_child(vis)

func spawn_players():
	player1 = preload("res://characters/player.tscn").instantiate()
	player1.position = Vector3(0, 0.5, -COURT_LENGTH / 3)
	player1.set_meta("player_id", 1)
	player1.set_meta("character", "KAGE")
	add_child(player1)
	
	player2 = preload("res://characters/player.tscn").instantiate()
	player2.position = Vector3(0, 0.5, COURT_LENGTH / 3)
	player2.set_meta("player_id", 2)
	player2.set_meta("character", "HIKARI")
	add_child(player2)

func spawn_ball():
	var ball_scene = preload("res://characters/ball.tscn")
	ball = ball_scene.instantiate()
	ball.position = Vector3(0, 1.5, -COURT_LENGTH / 4)
	add_child(ball)

func _process(delta):
	match game_state:
		"playing":
			handle_input(delta)
			update_ai(delta)
			check_score()

func handle_input(delta):
	# Player 1 controls (arrow keys + Z for swing)
	p1_move_dir = Vector2.ZERO
	if Input.is_action_pressed("ui_right"):
		p1_move_dir.x += 1
	if Input.is_action_pressed("ui_left"):
		p1_move_dir.x -= 1
	if Input.is_action_pressed("ui_down"):
		p1_move_dir.y += 1
	if Input.is_action_pressed("ui_up"):
		p1_move_dir.y -= 1
	
	p1_swing = Input.is_action_just_pressed("ui_accept")
	
	# Move player 1
	var speed = 6.0
	var move = Vector3(p1_move_dir.x, 0, p1_move_dir.y) * speed * delta
	player1.position.x = clamp(player1.position.x + move.x, -COURT_WIDTH / 2 + 0.5, COURT_WIDTH / 2 - 0.5)
	player1.position.z = clamp(player1.position.z + move.z, -COURT_LENGTH / 2 + 0.5, 0)
	
	# Swing
	if p1_swing:
		var dist = player1.position.distance_to(ball.position)
		if dist < 2.0:
			hit_ball(player1, Vector3(0, 0, -1))

func update_ai(delta):
	# Simple AI: follow the ball on their side
	var target_z = ball.position.z
	var target_x = ball.position.x
	
	# Only chase if ball is on AI's side
	if ball.position.z > 0:
		var speed = 4.0
		var dx = target_x - player2.position.x
		var dz = target_z - player2.position.z
		player2.position.x += clamp(dx, -speed * delta, speed * delta)
		player2.position.z += clamp(dz, -speed * delta, speed * delta)
		player2.position.x = clamp(player2.position.x, -COURT_WIDTH / 2 + 0.5, COURT_WIDTH / 2 - 0.5)
		player2.position.z = clamp(player2.position.z, 0, COURT_LENGTH / 2 - 0.5)
		
		# Swing at ball
		var dist = player2.position.distance_to(ball.position)
		if dist < 2.0:
			hit_ball(player2, Vector3(0, 0, 1))

func hit_ball(player: CharacterBody3D, direction: Vector3):
	var hit_dir = direction + Vector3(
		randf_range(-0.3, 0.3),
		randf_range(0.2, 0.5),
		randf_range(-0.3, 0.3)
	)
	hit_dir = hit_dir.normalized()
	var force = 15.0
	ball.linear_velocity = hit_dir * force
	ball.position.y = 1.0

func check_score():
	# If ball goes past a player, the other player scores
	if ball.position.z < -COURT_LENGTH / 2 - 1:
		score_p2 += 1
		reset_point(2)
	elif ball.position.z > COURT_LENGTH / 2 + 1:
		score_p1 += 1
		reset_point(1)

func reset_point(winner: int):
	game_state = "point_scored"
	ball.linear_velocity = Vector3.ZERO
	ball.position = Vector3(0, 1.5, 0)
	player1.position = Vector3(0, 0.5, -COURT_LENGTH / 3)
	player2.position = Vector3(0, 0.5, COURT_LENGTH / 3)
	
	if score_p1 >= 6 or score_p2 >= 6:
		game_state = "game_over"
		show_game_over()
	else:
		await get_tree().create_timer(1.0).timeout
		game_state = "playing"

func show_menu():
	game_state = "menu"
	print("=== GenTech Smash ===")
	print("KAGE (You) vs HIKARI (CPU)")
	print("First to 6 wins!")
	print("Arrow keys: Move | Z: Swing")
	print("Press SPACE to start")

func _input(event):
	if event is InputEventKey and event.keycode == KEY_SPACE and game_state == "menu":
		game_state = "playing"
		print("Match started!")

func show_game_over():
	var winner = "KAGE" if score_p1 > score_p2 else "HIKARI"
	print("Game Over! %s wins! %d - %d" % [winner, score_p1, score_p2])
