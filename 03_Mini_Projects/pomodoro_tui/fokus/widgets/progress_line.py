"""Bar progres baris tunggal: isian penuh dari kiri + chip persentase di tengah.

Pengganti ``ProgressBar`` bawaan Textual. Alasan: ``ProgressBar`` menata
``Bar`` dan ``PercentageStatus`` sebagai dua widget berdampingan, sehingga
bar hanya dapat melebar sampai lebar tetapnya (32 sel) dan persentase
terdorong ke samping. Dengan overlay persentase di atas bar, garis justru
terhapus oleh sel kosong layer atas saat dikomposit.

Satu widget yang merender seluruh baris dalam satu strip menyelesaikan
keduanya: bar membentang penuh dan chip persentase tetap di tengah.
"""

from __future__ import annotations

from rich.style import Style
from rich.text import Text
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widget import Widget

FILL_CHAR = "\u2501"  # ━


class ProgressLine(Widget):
    """Satu baris bar progres dengan chip persentase di tengah."""

    can_focus = False

    COMPONENT_CLASSES = {"line--fill", "line--track", "line--pct"}

    DEFAULT_CSS = """
    ProgressLine {
        width: 100%;
        height: 1;
    }
    """

    fraction: reactive[float] = reactive(0.0)

    def render(self) -> RenderResult:
        width = self.size.width
        if width < 1:
            return Text("")

        fill_style = self.get_component_rich_style("line--fill")
        track_style = self.get_component_rich_style("line--track")
        pct_style = self.get_component_rich_style("line--pct")

        fill_width = int(self.fraction * width)
        chip = f" {int(self.fraction * 100)}% "[:width]
        chip_start = max(0, (width - len(chip)) // 2)

        cells: list[tuple[str, Style]] = [(FILL_CHAR, track_style)] * width
        for index in range(fill_width):
            cells[index] = (FILL_CHAR, fill_style)
        for offset, char in enumerate(chip):
            index = chip_start + offset
            if index < width:
                cells[index] = (char, pct_style)

        line = Text(no_wrap=True)
        for char, style in cells:
            line.append(char, style)
        return line
