from pathlib import Path
import csv
import cv2
import numpy as np
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
PRESENT_DIR = BASE_DIR / "data" / "test" / "present"
ABSENT_DIR = BASE_DIR / "data" / "test" / "absent"
OUTPUT_DIR = BASE_DIR / "outputs"

GLOBAL_T = 180
RATIO_LIMIT = 0.03
OTSU_MAX_RATIO = 0.18
LOW_VARIATION = 5.0

# ROI relatif terhadap gambar input.
# Gambar yang diberikan sudah berupa crop area tanda tangan.
ROI_X1, ROI_Y1 = 0.03, 0.26
ROI_X2, ROI_Y2 = 0.88, 0.72


def crop_signature_area(image):
    h, w = image.shape[:2]
    x1, x2 = int(ROI_X1 * w), int(ROI_X2 * w)
    y1, y2 = int(ROI_Y1 * h), int(ROI_Y2 * h)
    return image[y1:y2, x1:x2]


def morphology(binary):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    result = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel, iterations=1)
    return result


def segment(gray):
    # Global threshold
    _, global_bin = cv2.threshold(
        gray, GLOBAL_T, 255, cv2.THRESH_BINARY_INV
    )
    global_morph = morphology(global_bin)

    # Otsu threshold
    otsu_t, otsu_bin = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    otsu_morph = morphology(otsu_bin)

    global_ratio = cv2.countNonZero(global_morph) / global_morph.size
    otsu_ratio = cv2.countNonZero(otsu_morph) / otsu_morph.size

    # Otsu dapat menjadi tidak wajar pada ROI kosong/hampir seragam.
    # Dalam kondisi tersebut digunakan hasil global.
    if gray.std() < LOW_VARIATION or otsu_ratio > OTSU_MAX_RATIO:
        selected_name = "Global (fallback)"
        selected = global_morph
    else:
        selected_name = "Otsu"
        selected = otsu_morph

    return {
        "global_raw": global_bin,
        "global": global_morph,
        "otsu_raw": otsu_bin,
        "otsu": otsu_morph,
        "global_threshold": GLOBAL_T,
        "otsu_threshold": float(otsu_t),
        "global_foreground": cv2.countNonZero(global_morph),
        "global_ratio": global_ratio,
        "otsu_foreground": cv2.countNonZero(otsu_morph),
        "otsu_ratio": otsu_ratio,
        "selected_method": selected_name,
        "selected": selected,
    }


def analyze_image(path, expected):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Gagal membaca gambar: {path}")

    roi = crop_signature_area(image)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    result = segment(gray)

    selected_foreground = cv2.countNonZero(result["selected"])
    selected_ratio = selected_foreground / result["selected"].size
    prediction = (
        "SIGNATURE PRESENT"
        if selected_ratio >= RATIO_LIMIT
        else "SIGNATURE ABSENT"
    )

    return {
        "file": path.name,
        "expected": expected,
        "prediction": prediction,
        "selected_method": result["selected_method"],
        "global_threshold": result["global_threshold"],
        "otsu_threshold": round(result["otsu_threshold"], 2),
        "global_foreground": result["global_foreground"],
        "global_ratio": round(result["global_ratio"], 4),
        "otsu_foreground": result["otsu_foreground"],
        "otsu_ratio": round(result["otsu_ratio"], 4),
        "selected_foreground": selected_foreground,
        "selected_ratio": round(selected_ratio, 4),
    }, gray, result


def save_comparison(path, expected, output_path):
    image = cv2.imread(str(path))
    roi = crop_signature_area(image)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    result = segment(gray)

    panels = [
        ("Grayscale", gray),
        ("Global threshold", result["global_raw"]),
        ("Otsu threshold", result["otsu_raw"]),
        ("Otsu + morphology", result["otsu"]),
    ]

    height, width = gray.shape
    panel_images = []
    for title, panel in panels:
        if panel.ndim == 2:
            panel = cv2.cvtColor(panel, cv2.COLOR_GRAY2BGR)
        panel = cv2.resize(panel, (width // 2, height // 2))
        cv2.putText(panel, title, (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 0, 255), 2, cv2.LINE_AA)
        panel_images.append(panel)

    top = cv2.hconcat(panel_images[:2])
    bottom = cv2.hconcat(panel_images[2:])
    comparison = cv2.vconcat([top, bottom])

    cv2.imwrite(str(output_path), comparison)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    rows = []
    files = []

    for p in sorted(PRESENT_DIR.glob("*.jpg")):
        files.append((p, "SIGNATURE PRESENT"))

    for p in sorted(ABSENT_DIR.glob("*.jpg")):
        files.append((p, "SIGNATURE ABSENT"))

    for path, expected in files:
        row, _, _ = analyze_image(path, expected)
        rows.append(row)

    csv_path = OUTPUT_DIR / "results.csv"
    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Buat contoh visual dari satu data present dan satu data absent.
    save_comparison(
        PRESENT_DIR / "present_1.jpg",
        "SIGNATURE PRESENT",
        OUTPUT_DIR / "comparison_present.png",
    )
    # comparison.png disiapkan sebagai output utama.
    shutil.copy2(
        OUTPUT_DIR / "comparison_present.png",
        OUTPUT_DIR / "comparison.png",
    )
    save_comparison(
        ABSENT_DIR / "absent_1.jpg",
        "SIGNATURE ABSENT",
        OUTPUT_DIR / "comparison_absent.png",
    )

    correct = sum(r["expected"] == r["prediction"] for r in rows)
    accuracy = correct / len(rows) * 100

    print("\nHasil pengujian:")
    print("-" * 100)
    for r in rows:
        print(
            f'{r["file"]:15} {r["expected"]:18} {r["prediction"]:18} '
            f'{r["selected_method"]:18} ratio={r["selected_ratio"]:.4f}'
        )
    print("-" * 100)
    print(f"Benar   : {correct}/{len(rows)}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"\nHasil disimpan di: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
