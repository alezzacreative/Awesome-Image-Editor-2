# Awesome Image Editor

[![screen](https://user-images.githubusercontent.com/63913433/200029964-64d68352-e634-4923-a93c-0e3ebadd7923.png)](https://user-images.githubusercontent.com/63913433/200029964-64d68352-e634-4923-a93c-0e3ebadd7923.png)

## Overview

Awesome Image Editor is a Python-based image editing application built with PyQt6. It provides layer-based editing capabilities, allowing users to work with various image formats, including PSD files.

## Features

*   **Layer-based editing:** Manage and manipulate image layers.
*   **PSD File Support:** Open and view Adobe Photoshop (.psd) files.
*   **Common Image Formats:** Open and save JPEG (.jpg) and PNG (.png) files.
*   **Project Files:** Save and load projects in a custom `.aie` format.
*   **Gaussian Blur:** Apply a gaussian blur effect to layers.
*   **Dark Theme:** User-friendly dark interface.
*   **Toolbar:** Includes a basic toolbar, with plans for more tools in the future.

## Installation

1.  **Clone the repository (or download the source code):**
    ```bash
    git clone https://github.com/username/awesome_image_editor.git # Replace with the actual URL
    cd awesome-image-editor
    ```
    If you have downloaded the source as a ZIP, simply extract it and navigate to the directory.

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    The project uses `PyQt6` for the GUI and `psd-tools` for PSD file handling. These are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

After installing the required packages, navigate to the root directory of the project and run:

```bash
python -m awesome_image_editor
```

## Supported File Types

*   **Project Files:**
    *   `.aie`: Awesome Image Editor's native project format (open/save).
*   **Image Files (Import):**
    *   `.psd`: Adobe Photoshop files (open).
    *   `.jpg`: JPEG images (open).
    *   `.png`: Portable Network Graphics images (open).
*   **Image Files (Export):**
    *   `.jpg`: JPEG images (save).
    *   `.png`: Portable Network Graphics images (save).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.
