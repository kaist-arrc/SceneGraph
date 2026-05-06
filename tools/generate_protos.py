from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = ROOT / "proto"
PROTO_FILE = PROTO_DIR / "scenegraph.proto"


def grpc_tools_include() -> Path | None:
    try:
        import grpc_tools  # type: ignore[import-not-found]
    except ImportError:
        return None

    return Path(grpc_tools.__file__).resolve().parent / "_proto"


def build_command(out_dir: Path, languages: list[str]) -> list[str]:
    protoc = shutil.which("protoc")
    include_args = ["-I", str(PROTO_DIR)]
    include_dir = grpc_tools_include()
    if include_dir is not None:
        include_args.extend(["-I", str(include_dir)])

    protoc_only_languages = {"cpp", "csharp"}
    requested_protoc_only_languages = protoc_only_languages.intersection(languages)
    if requested_protoc_only_languages and protoc is None:
        language_list = ", ".join(sorted(requested_protoc_only_languages))
        raise RuntimeError(
            f"{language_list} generation requires the protoc compiler. "
            "grpcio-tools can generate Python bindings, but it does not "
            "provide the C++ or C# generators. Install protoc, or run with "
            "`--language python`."
        )

    if protoc:
        command = [protoc]
    else:
        if include_dir is None:
            raise RuntimeError(
                "Could not find protoc or grpc_tools. Install protoc, or run "
                "`python -m pip install grpcio-tools`."
            )
        command = [sys.executable, "-m", "grpc_tools.protoc"]

    for language in languages:
        language_out = out_dir / language
        language_out.mkdir(parents=True, exist_ok=True)

        if language == "python":
            include_args.append(f"--python_out={language_out}")
        elif language == "cpp":
            include_args.append(f"--cpp_out={language_out}")
        elif language == "csharp":
            include_args.append(f"--csharp_out={language_out}")
            include_args.append("--csharp_opt=file_extension=.g.cs")
        else:
            raise ValueError(f"Unsupported language: {language}")

    return command + include_args + [str(PROTO_FILE)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SceneGraph protobuf bindings.")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "generated",
        help="Output directory for generated source files.",
    )
    parser.add_argument(
        "--language",
        action="append",
        choices=["python", "cpp", "csharp"],
        dest="languages",
        help="Language to generate. Can be passed multiple times. Defaults to all.",
    )
    args = parser.parse_args()

    languages = args.languages or ["python", "cpp", "csharp"]
    command = build_command(args.out.resolve(), languages)
    print("Running:", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
