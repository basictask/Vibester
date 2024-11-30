"""
This is the main file that converts musical metadata to a timestamped pdf file that can be printed
"""
import os
import pandas as pd
from typing import List
from pathlib import Path
from config import VibesterConfig
from generator.table import Table
from generator.track import Track

import cairosvg
from PyPDF2 import PdfMerger


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
        svg_file = table.render_svg(mode="qr", page_footer="")
        svg_files.append(svg_file)
    return svg_files


def write_to_pdf(svg_files: List[str], filename: str) -> None:
    """
    Takes a list of Table objects and writes them into a file.
    """
    filepath = os.path.join(VibesterConfig.path_output, filename)
    temp_pdfs = []

    for svg_file in svg_files:
        temp_pdf = svg_file.replace(".svg", ".pdf")
        cairosvg.svg2pdf(url=svg_file, write_to=temp_pdf)
        temp_pdfs.append(temp_pdf)

    # Merge all PDFs into one
    merger = PdfMerger()
    for temp_pdf in temp_pdfs:
        merger.append(temp_pdf)
    merger.write(filepath)
    merger.close()

    # Optionally, cleanup temporary files
    for temp_pdf in temp_pdfs:
        Path(temp_pdf).unlink()


def generate(df: pd.DataFrame, filename: str) -> None:
    """
    Takes a pandas DataFrame and renders a pdf file from it
    """
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