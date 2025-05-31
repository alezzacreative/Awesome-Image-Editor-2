from typing import Union

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtWidgets import QFileDialog


def create_file_dialog(
    file_mode: QFileDialog.FileMode,
    default_directory: Union[str, QDir],
    name_filter: str,
    accept_mode: QFileDialog.AcceptMode,
) -> QFileDialog:
    """
    Creates and configures a QFileDialog instance.

    This is a general helper function to create file dialogs with common settings.
    It sets the dialog to be application modal and prefers Qt's custom dialog
    over the native system dialog due to a known bug.

    Args:
        file_mode: The file mode for the dialog (e.g., AnyFile, ExistingFile).
        default_directory: The initial directory the dialog should open to.
        name_filter: The filter for file types (e.g., "Images (*.png *.jpg)").
        accept_mode: The accept mode (e.g., AcceptSave, AcceptOpen).

    Returns:
        The configured QFileDialog instance.
    """
    dlg = QFileDialog()
    dlg.setNameFilter(name_filter)
    dlg.setDirectory(default_directory)
    dlg.setWindowModality(
        Qt.WindowModality.ApplicationModal
    )  # Disable entire app while showing dialog
    dlg.setOption(
        QFileDialog.Option.DontUseNativeDialog, True
    )  # Use Qt custom file dialog instead of system's native file dialog, because of a bug https://stackoverflow.com/a/12406457/8094047
    dlg.setFileMode(file_mode)
    dlg.setAcceptMode(accept_mode)
    return dlg


def create_save_file_dialog(
    default_directory: Union[str, QDir], name_filter: str
) -> QFileDialog:
    """
    Creates a pre-configured QFileDialog for saving files.

    Sets the file mode to `AnyFile` and accept mode to `AcceptSave`.

    Args:
        default_directory: The initial directory the dialog should open to.
        name_filter: The filter for file types (e.g., "Awesome Image Editor Project (*.aie)").

    Returns:
        A QFileDialog instance configured for saving files.
    """
    return create_file_dialog(
        QFileDialog.FileMode.AnyFile,
        default_directory,
        name_filter,
        QFileDialog.AcceptMode.AcceptSave,
    )


def create_open_file_dialog(
    default_directory: Union[str, QDir], name_filter: str
) -> QFileDialog:
    """
    Creates a pre-configured QFileDialog for opening existing files.

    Sets the file mode to `ExistingFile` and accept mode to `AcceptOpen`.

    Args:
        default_directory: The initial directory the dialog should open to.
        name_filter: The filter for file types (e.g., "Image files (*.jpg *.png)").

    Returns:
        A QFileDialog instance configured for opening files.
    """
    return create_file_dialog(
        QFileDialog.FileMode.ExistingFile,
        default_directory,
        name_filter,
        QFileDialog.AcceptMode.AcceptOpen,
    )
