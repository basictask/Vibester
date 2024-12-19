import os
import tempfile
import pandas as pd
from typing import List
from pathlib import Path
from PyPDF2 import PdfMerger
from config import VibesterConfig
from generator.table import Table
from generator.track import Track
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def get_tracks(df: pd.DataFrame) -> List[Track]:
    """
    Takes a pandas DataFrame and returns a list of Track objects
    """
    # Sort the dataframe by filename
    df.sort_values(by=["year", "artist", "title"], ascending=True, inplace=True)

    tracks: List[Track] = []
    for idx in df.index:
        row = df.loc[idx, :].to_dict()
        track = Track(track=row)
        tracks.append(track)

    return tracks


def get_tables(tracks: List[Track]) -> List[Table]:
    """
    Takes a list of Track objects and organizes them into a list of Table objects
    """
    tables: List[Table] = []
    table = Table()

    # Iterate over tracks and append them to a table
    for track in tracks:
        table.append(track)
        if table.is_full():
            tables.append(table)
            table = Table()

    # Append the final table, which may not be full.
    if not table.is_empty():
        tables.append(table)

    return tables


def get_svg_files(tables: List[Table]) -> List[str]:
    """
    Takes a list of Table objects and converts them into SVG files
    The conversion logic is implemented in the Table class
    """
    svg_files: List[str] = []
    for table in tables:
        svg_file_qr = table.render_svg(mode="qr", page_footer="")  # Render QR code side
        svg_file_info = table.render_svg(mode="title", page_footer="")  # Render info side
        svg_files.append(svg_file_qr)
        svg_files.append(svg_file_info)
    return svg_files


def write_to_pdf(svg_files: List[str], filename: str) -> None:
    """
    Takes a list of SVG files and writes them into a single PDF file.
    """
    filepath = os.path.join(VibesterConfig.path_output, filename)
    temp_pdfs = []

    for svg_content in svg_files:
        # Create a temporary SVG file for the content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_svg:
            temp_svg.write(svg_content.encode("utf-8"))  # Write SVG content to temp file
            temp_svg_path = temp_svg.name

        # Convert the temporary SVG file to a ReportLab drawing
        drawing = svg2rlg(temp_svg_path)
        temp_pdf = temp_svg_path.replace(".svg", ".pdf")  # Temporary PDF file name

        # Write the drawing to a temporary PDF file
        with open(temp_pdf, "wb") as pdf_file:
            renderPDF.drawToFile(drawing, pdf_file)
        temp_pdfs.append(temp_pdf)

        # Clean up the temporary SVG file
        Path(temp_svg_path).unlink()

    # Merge all PDFs into one
    merger = PdfMerger()
    for temp_pdf in temp_pdfs:
        merger.append(temp_pdf)
    merger.write(filepath)
    merger.close()

    # Cleanup temporary PDF files
    for temp_pdf in temp_pdfs:
        Path(temp_pdf).unlink()


def generate(df: pd.DataFrame, filename: str) -> None:
    """
    Takes a pandas DataFrame and renders a pdf file from it
    """
    # Append pdf to
    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"

    # Create output directory
    os.makedirs(VibesterConfig.path_output, exist_ok=True)

    # Convert the DataFrame into tracks
    tracks = get_tracks(df=df)

    # Organize the tracks into tables
    tables = get_tables(tracks=tracks)

    # Render the tables into SVG files
    svg_files = get_svg_files(tables=tables)

    # Render the SVG files into a single pdf
    write_to_pdf(svg_files=svg_files, filename=filename)

    print(f"Successfully output to: {os.path.join(VibesterConfig.path_output, filename)}")


if __name__ == "__main__":
    # To use the main functionality, add a new configurtion with the same inputs as index.py

    # Define a sample dataframe for testing purposes
    df_test = pd.DataFrame(
        [
            {
                "filename": "001. The Jacksons - Blame It on the Boogie.mp3",
                "artist": "The Jacksons",
                "title": "Blame It on the Boogie",
                "year": "1994",
                "genre": "bubblegum pop;funk;pop;pop soul;soul",
                "saved": False,
                "hash": "6f35121888aeef7ca842a2535ceea9"
            },
            {
                "filename": "002. Boney M. - Rivers of Babylon (Single Version).mp3",
                "artist": "Boney M.",
                "title": "Rivers of Babylon",
                "year": "2003",
                "genre": "dance-pop;disco;euro-disco;europop;pop;soul",
                "saved": False,
                "hash": "703e9e895d800f2cb21be8c6525c09"
            },
            {
                "filename": "003. Elvis Presley - Burning Love (Live).mp3",
                "artist": "Elvis Presley",
                "title": "Burning Love",
                "year": "1988",
                "genre": "blue-eyed soul;blues;",
                "saved": False,
                "hash": "21073d8698faa43f59c762276fee0f"
            },
            {
                "filename": "004. Billy Swan - I Can Help.mp3",
                "artist": "Billy Swan",
                "title": "I Can Help",
                "year": "1974",
                "genre": "country pop;pop;rock & roll",
                "saved": False,
                "hash": "9618f6278b7868b59b65b668cd5fe3"
            }
        ]
    )

    # Call the generate function to print the result
    generate(df=df_test, filename="test.pdf")
