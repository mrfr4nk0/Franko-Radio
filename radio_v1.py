import tkinter as tk
from PIL import Image, ImageTk
import vlc
import requests
import tkinter.font as tkFont  # Add this import for font handling

# Path to your PNG files
PNG_PATH = "images/radio.png"
KNOB_PATH = "images/knob.png"
CLOSE_BTN_PATH = "images/button.png"  # Path to the close button image

# Reversed radio channel URLs (from 5 to 1) and radio names
CHANNELS = {
    1: {"url": "https://mscp1.gazduireradio.ro/cityradio", "name": "City Radio"},  # Position 1 (now channel 5)
    2: {"url": "https://icast.connectmedia.hu/5002/live.mp3", "name": "Retro Radio"},  # Position 2 (now channel 4)
    3: {"url": "https://icast.connectmedia.hu/5201/live.mp3", "name": "Radio 1"},  # Position 3 (now channel 3)
    4: {"url": "https://icast.connectmedia.hu/4738/mr2.mp3", "name": "Petofi Radio"},  # Position 4 (now channel 2)
    5: None  # Position 5 (now channel 1) is disabled
}

# Volume levels (corresponding to knob positions)
VOLUME_LEVELS = {
    1: 1.0,
    2: 0.85,
    3: 0.60,
    4: 0.35,
    5: 0.2
}

def main():
    # Initialize VLC player
    player = vlc.MediaPlayer()

    # Set volume to 0 (lowest volume) at the start
    set_volume(player, 5)  # This will set the volume to 0

    # Create the root window
    root = tk.Tk()
    root.attributes("-topmost", True)  # Make the window always on top
    root.overrideredirect(True)  # Remove borders and title bar
    root.wm_attributes("-transparentcolor", "white")  # Set transparency color (use a color not in your image)

    # Load the PNG image for the background
    image = Image.open(PNG_PATH)
    img_width, img_height = image.size
    background_image = ImageTk.PhotoImage(image)

    # Load the knob image
    knob_image = Image.open(KNOB_PATH)
    knob_texture = ImageTk.PhotoImage(knob_image)

    # Load the close button image
    close_btn_image = Image.open(CLOSE_BTN_PATH)
    close_btn_texture = ImageTk.PhotoImage(close_btn_image)

    # Set the window size to match the image
    root.geometry(f"{img_width}x{img_height}")

    # Create a canvas to display the image
    canvas = tk.Canvas(root, width=img_width, height=img_height, highlightthickness=0, bg="white")
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=background_image)

    # Place the knobs at the specified positions (X=119/2, Y=128/2)
    knob1_x = (119 + 26.5) // 2
    knob1_y = (128 + 26.5) // 2
    knob2_x = (479 + 26.5) // 2
    knob2_y = (128 + 26.5) // 2

    knob1_rotation = 0
    knob2_rotation = 0

    # Create images for knobs on the canvas
    knob1_img_id = canvas.create_image(knob1_x, knob1_y, anchor="center", image=knob_texture)
    knob2_img_id = canvas.create_image(knob2_x, knob2_y, anchor="center", image=knob_texture)

    # Place the close button at the specified position
    close_btn_x = (470 + 47) // 2
    close_btn_y = (42 + 10) // 2
    close_btn_id = canvas.create_image(close_btn_x, close_btn_y, anchor="center", image=close_btn_texture)

    # Keep references to the images to avoid them being garbage collected
    knob1_image_ref = knob_texture
    knob2_image_ref = knob_texture
    close_btn_image_ref = close_btn_texture

    # Load the custom font (SevenSegment.ttf)
    font_path = "SevenSegment.ttf"  # Full path if needed
    try:
        # Load the custom font using tkinter.font.nametofont() after registering it
        custom_font = tkFont.Font(family="Seven Segment", size=12)  # Set the desired font size
        root.option_add('*Font', custom_font)  # Apply globally
    except Exception as e:
        print("Error loading custom font:", e)
        custom_font = tkFont.Font(family="Arial", size=12)  # Fallback to Arial if custom font loading fails

    # Create a text label for displaying the radio name in the middle of the window
    radio_name_text = canvas.create_text(img_width // 2, 47, text="Select channel", font=custom_font, fill="red")

    # Function to rotate knob and update the image
    def rotate_knob(knob, rotation, direction, image_ref, knob_x, knob_y):
        # Rotate the knob image by 72 degrees (5 possible positions, 360 / 5 = 72)
        new_rotation = (rotation + direction * 72) % 360
        # Rotate without expanding
        rotated_image = knob_image.rotate(new_rotation, resample=Image.Resampling.BICUBIC)

        # Convert the rotated image to a Tkinter-compatible format
        rotated_texture = ImageTk.PhotoImage(rotated_image)

        # Keep reference to prevent garbage collection
        image_ref = rotated_texture

        # Update the knob image on the canvas at the same position (no shifting)
        canvas.itemconfig(knob, image=rotated_texture)
        
        return rotated_texture, new_rotation, image_ref

    # Function to handle mouse wheel events for rotating the knobs
    def on_mouse_wheel(event):
        nonlocal knob1_rotation, knob2_rotation, knob1_image_ref, knob2_image_ref
        
        # Determine which knob is being rotated based on the cursor's position
        if abs(event.x - knob1_x) < 50 and abs(event.y - knob1_y) < 50:
            # Reverse direction if needed
            direction = -1 if event.delta > 0 else 1  # Inverse direction for correct clockwise/counterclockwise
            knob1_image_ref, knob1_rotation, knob1_image_ref = rotate_knob(knob1_img_id, knob1_rotation, direction, knob1_image_ref, knob1_x, knob1_y)
            
            # Update volume level based on the knob position (1 to 5, reversed)
            if knob1_rotation == 72:
                set_volume(player, 1)
            elif knob1_rotation == 144:
                set_volume(player, 2)
            elif knob1_rotation == 216:
                set_volume(player, 3)
            elif knob1_rotation == 288:
                set_volume(player, 4)
            elif knob1_rotation == 0:
                set_volume(player, 5)

        elif abs(event.x - knob2_x) < 50 and abs(event.y - knob2_y) < 50:
            # Reverse direction if needed
            direction = -1 if event.delta > 0 else 1  # Inverse direction for correct clockwise/counterclockwise
            knob2_image_ref, knob2_rotation, knob2_image_ref = rotate_knob(knob2_img_id, knob2_rotation, direction, knob2_image_ref, knob2_x, knob2_y)

            # Change channel based on the knob position (5 to 1)
            if knob2_rotation == 0:
                stop_music()
            elif knob2_rotation == 72:
                change_channel(4)
            elif knob2_rotation == 144:
                change_channel(3)
            elif knob2_rotation == 216:
                change_channel(2)
            elif knob2_rotation == 288:
                change_channel(1)

    # Bind mouse wheel event to canvas for rotating the knobs
    canvas.bind_all("<MouseWheel>", on_mouse_wheel) 

    # Function to change channel
    def change_channel(channel_position):
        channel = CHANNELS[channel_position]
        if channel and channel["url"]:
            print(f"Changing to channel {channel_position}: {channel['name']} ({channel['url']})")
            send_cmd_message(channel['name'])  # Send the command message with the radio name
            media = vlc.Media(channel["url"])
            player.set_media(media)
            player.play()
            # Update the radio name label
            canvas.itemconfig(radio_name_text, text=channel['name'], font=custom_font, fill="red")

    # Function to stop music
    def stop_music():
        print("Stopping music")
        player.stop()  # Stop the VLC player
        # Update the radio name label to indicate Select channel is playing
        canvas.itemconfig(radio_name_text, text="Select channel", font=custom_font, fill="red")

    # Function to send a command message
    def send_cmd_message(radio_name):
        # Simulate sending a command message with the radio name
        print(f"Command message: Now playing {radio_name}")

    # Function to close the radio and the window
    def close_radio(event):
        stop_music()  # Stop the radio
        root.destroy()  # Close the window

    # Bind the close button to the close_radio function
    canvas.tag_bind(close_btn_id, "<Button-1>", close_radio)

    # Draggable window functionality
    def on_drag_start(event):
        # Record the starting position
        root.x = event.x
        root.y = event.y

    def on_drag_motion(event):
        # Calculate how far the mouse has moved
        delta_x = event.x - root.x
        delta_y = event.y - root.y
        # Move the window by the distance moved by the mouse
        new_x = root.winfo_x() + delta_x
        new_y = root.winfo_y() + delta_y
        root.geometry(f"+{new_x}+{new_y}")

    # Bind mouse events to the canvas for dragging
    canvas.bind("<Button-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag_motion)

    # Run the Tkinter main loop
    root.mainloop()

def set_volume(player, level):
    player.audio_set_volume(int(VOLUME_LEVELS[level] * 100))

if __name__ == "__main__":
    main()