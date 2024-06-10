import numpy as np

class Meteorite:
    def __init__(
            self, name: str, position: tuple,
            petrographic_type: str, weathering_grade: str,
            fa_content: float, fs_content: float,
            mag_sus: float
            ) -> None:

        self.name = name
        self.position = position
      

        if petrographic_type == 'nan' or not isinstance(petrographic_type, (int, float)):
            self.petrographic_type = None
        else:
            try:
                self.petrographic_type = int(petrographic_type)
            except ValueError:
                self.petrographic_type = None

        if weathering_grade == 'nan' or not isinstance(weathering_grade, (int, float)):
            self.weathering_grade = None
        else:
            try:
                self.weathering_grade = int(weathering_grade)
            except ValueError:
                self.weathering_grade = None

        self.fa_content = float(fa_content) if fa_content is not None and isinstance(fa_content, (int, float)) and not np.isnan(fa_content) else None
        self.fs_content = float(fs_content) if fs_content is not None and isinstance(fs_content, (int, float)) and not np.isnan(fs_content) else None
        self.mag_sus = float(mag_sus) if mag_sus is not None and isinstance(mag_sus, (int, float)) and not np.isnan(mag_sus) else None

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"

