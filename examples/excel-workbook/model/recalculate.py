import subprocess
from pathlib import Path

PROFILE_DIR = Path("/tmp/lo-profile")
TIMEOUT_SECONDS = 180

# Without OOXMLRecalcMode=0 LibreOffice keeps the cached results stored in the
# file instead of recalculating (0 = always recalculate).
PROFILE_SETTINGS = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""


def write_libreoffice_profile() -> None:
    user_dir = PROFILE_DIR / "user"
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "registrymodifications.xcu").write_text(PROFILE_SETTINGS, encoding="utf-8")


def format_stream(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def run_recalculation(source_path: Path, out_dir: Path) -> Path:
    write_libreoffice_profile()
    command = [
        "soffice",
        "--headless",
        "--norestore",
        f"-env:UserInstallation={PROFILE_DIR.as_uri()}",
        "--convert-to",
        "xlsx",
        "--outdir",
        str(out_dir),
        str(source_path),
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"LibreOffice recalculation timed out after {TIMEOUT_SECONDS} s\n"
            f"{format_stream(error.stderr)}"
        ) from error

    stdout = format_stream(result.stdout)
    stderr = format_stream(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice exited with code {result.returncode}\nstderr: {stderr}\nstdout: {stdout}"
        )

    # stderr is not checked: soffice always prints a javaldx warning there.
    converted = out_dir / source_path.name
    if not converted.exists():
        raise RuntimeError(
            f"LibreOffice produced no file at {converted}\nstdout: {stdout}\nstderr: {stderr}"
        )
    return converted
