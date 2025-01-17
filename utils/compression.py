import os
from mutagen.mp3 import MP3
from pydub import AudioSegment


def get_bitrate(file_path: str) -> int:
    """
    Retrieves the bitrate of an MP3 file using mutagen.
    """
    audio = MP3(file_path)
    return audio.info.bitrate // 1000  # Bitrate in kbps


def process_mp3(input_file: str, output_file: str, target_bitrate: int) -> None:
    """
    Converts an MP3 file to the target bitrate if the current bitrate is higher.
    """
    current_bitrate = get_bitrate(file_path=input_file)
    print(f"Processing '{input_file}' (Current bitrate: {current_bitrate} kbps)")

    if current_bitrate <= target_bitrate:
        print(f"Bitrate is already {current_bitrate} kbps or lower. Copying without conversion.")
        if input_file != output_file:
            # Copy file without conversion
            AudioSegment.from_file(input_file).export(output_file, format="mp3", bitrate=f"{current_bitrate}k")
    else:
        print(f"Converting '{input_file}' to {target_bitrate} kbps...")
        audio = AudioSegment.from_file(input_file, format="mp3")
        audio.export(output_file, format="mp3", bitrate=f"{target_bitrate}k")
        print(f"Conversion complete: '{output_file}'")


def process_folder(target_folder: str, output_folder: str, target_bitrate: int) -> None:
    """
    Traverses a folder recursively, processing all MP3 files to ensure their bitrate matches the target.
    """
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.lower().endswith(".mp3"):
                input_file = os.path.join(root, file)
                # Maintain directory structure in the output folder
                relative_path = os.path.relpath(root, target_folder)
                output_dir = os.path.join(output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, file)
                process_mp3(input_file=input_file, output_file=output_file, target_bitrate=target_bitrate)


# Example usage
if __name__ == "__main__":
    target = "data/other/music_sample"  # Replace with the folder to scan for MP3 files
    bitrate = 192

    process_folder(
        target_folder=target,
        output_folder=target,
        target_bitrate=bitrate,
    )
