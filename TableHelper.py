from typing import List, Tuple
from tabulate import tabulate

def presentEtaInvariantsOnTable(
    imagesNames: List[str],
    scales: List[int],
    etaInvariants: List[Tuple[float, float, float]],
    etaInvariantsScaled: List[Tuple[float, float, float]]
) -> None:
    # Create table headers
    headers = [
        "Imagen",
        "Factor de Escalado",
        "η00",
        "η11",
        "η22",
        "η00 Escalada",
        "η11 Escalada",
        "η22 Escalada"
    ]
    
    rows = []
    for name, scale, eta, scaled_eta in zip(imagesNames, scales, etaInvariants, etaInvariantsScaled):
        eta00, eta11, eta22 = eta
        scaled_eta00, scaled_eta11, scaled_eta22 = scaled_eta
        
        rows.append([
            name,
            scale,
            f"{eta00:.6f}",
            f"{eta11:.6f}",
            f"{eta22:.6f}",
            f"{scaled_eta00:.6f}",
            f"{scaled_eta11:.6f}",
            f"{scaled_eta22:.6f}"
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def presentMuInvariantsOnTable(
    imageNames: List[str],
    translations: List[Tuple[int,int]],
    muInvariants: List[Tuple[float, float, float]],
    muInvariantsTranslated: List[Tuple[float, float, float]]
) -> None:
    headers = [
        "Imagen",
        "Traslación (x,y)",
        "μ₀₀",
        "μ₁₁",
        "μ₂₂",
        "μ₀₀ Trasladada",
        "μ₁₁ Trasladada",
        "μ₂₂ Trasladada"
    ]
    
    rows = []
    for name, translation, mu, mu_translated in zip(imageNames, translations, muInvariants, muInvariantsTranslated):
        mu1, mu2, mu3 = mu
        mu_rotated1, mu_rotated2, mu_rotated3 = mu_translated
        x, y = translation
        
        rows.append([
            name,
            f"({x},{y})",
            f"{mu1:.6f}",
            f"{mu2:.6f}",
            f"{mu3:.6f}",
            f"{mu_rotated1:.6f}",
            f"{mu_rotated2:.6f}",
            f"{mu_rotated3:.6f}"
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))

def presentPhiInvariantsOnTable(
    imageNames: List[str],
    degrees: List[int],
    phiInvariants: List[Tuple[float, float, float]],
    phiInvariantsRotated: List[Tuple[float, float, float]]
) -> None:
    headers = [
        "Imagen",
        "Grados de Rotación",
        "φ₁",
        "φ₂",
        "φ₃",
        "φ₁ Rotada",
        "φ₂ Rotada",
        "φ₃ Rotada"
    ]
    
    rows = []
    for name, degree, phi, phi_rotated in zip(imageNames, degrees, phiInvariants, phiInvariantsRotated):
        phi1, phi2, phi3 = phi
        phi_rotated1, phi_rotated2, phi_rotated3 = phi_rotated
        
        rows.append([
            name,
            f"{degree}°",
            f"{phi1:.6f}",
            f"{phi2:.6f}",
            f"{phi3:.6f}",
            f"{phi_rotated1:.6f}",
            f"{phi_rotated2:.6f}",
            f"{phi_rotated3:.6f}"
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))