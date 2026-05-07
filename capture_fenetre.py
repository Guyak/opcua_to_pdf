import win32gui
import win32ui
import win32con
from PIL import Image
import os

def find_window_by_title(keyword):
    result = []
    # Recherche de toutes les fenêtres ouvertes sur le PC
    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if keyword.lower() in title.lower():
                # Filtrage du nom des fenêtres pour trouver la bonne à ouvrir
                result.append(hwnd)
    win32gui.EnumWindows(enum_handler, None)
    return result[0] if result else None

def screenshot_fenetre(titre_fenetre, chemin_temp):
    # Recherche de la fenêtre
    hwnd = find_window_by_title(titre_fenetre)
    if hwnd is None:
        raise RuntimeError(f"Aucune fenêtre contenant '{titre_fenetre}' n'a été trouvée")

    # Récupération des dimensions de la fenêtre
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # Capture de la fenêtre
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitmap = win32ui.CreateBitmap()
    saveBitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitmap)

    # Copie de l'écran vers le bitmap
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Conversion en image via PIL
    bmpinfo = saveBitmap.GetInfo()
    bmpstr = saveBitmap.GetBitmapBits(True)
    image = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    image.save(chemin_temp)

    # Nettoyage
    win32gui.DeleteObject(saveBitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)