extends Camera2D


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	get_tree().root.content_scale_size = get_viewport().size
	print(get_viewport().size)
	print(drag_horizontal_offset)
