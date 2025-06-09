# Awesome Image Editor

![screen](https://user-images.githubusercontent.com/63913433/200029964-64d68352-e634-4923-a93c-0e3ebadd7923.png)

Awesome Image Editor is a Python-based image editing application. It provides layer-based editing capabilities, allowing users to work with different elements of an image independently. The editor supports importing Adobe Photoshop PSD files, various common image formats, and includes features like Gaussian blur. Projects can be saved and loaded in a custom `.aie` format.

## How to Run

It is recommended to use a Python virtual environment to manage dependencies.

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    Execute the following command from the root of the repository:
    ```bash
    python -m awesome_image_editor
    ```

## Features

*   **Layer-based Editing:** Work with images in a non-destructive way using layers.
*   **PSD File Import:** Import Adobe Photoshop Document (.psd) files, with support for:
    *   Pixel layers
    *   Shape layers
    *   Text layers
    *   Group layers
*   **Image Format Support:** Open and save common image formats (e.g., PNG, JPG).
*   **Custom Project Format:** Save your work as an `.aie` project file and continue editing later.
*   **Gaussian Blur:** Apply a Gaussian blur filter to layers.
*   **Invert Colors Filter:** Apply a color inversion effect to image layers.
*   **Basic Layer Operations:** Add, select, move, and manage visibility of layers through the UI.

## Running Tests

This project uses `pytest` for running unit tests.

1.  Ensure you have installed the development dependencies (including `pytest`) from `requirements.txt`.
2.  To run the tests, execute the following command from the root of the repository:
    ```bash
    PYTHONPATH=. pytest
    ```
    Alternatively, you can set the `PYTHONPATH` environment variable:
    ```bash
    export PYTHONPATH=.
    pytest
    ```
    (For Windows command prompt, use `set PYTHONPATH=.` and for PowerShell, use `$env:PYTHONPATH = "."`)

## Contributing

Contributions are welcome! If you'd like to contribute, please feel free to submit issues or pull requests.
If you are submitting code changes, please ensure that all tests pass before submitting a pull request.
