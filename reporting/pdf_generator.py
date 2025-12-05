from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt

def fig_to_img(fig):
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    buf.seek(0)
    return buf

def generate_pdf(output_path, stats, fig1=None, fig2=None, fig3=None, fig4=None):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height-50, "Rapport WindLab – Analyse PIV & Optimisation")

    c.setFont("Helvetica", 12)
    c.drawString(50, height-100, f"Vitesse moyenne : {stats['mean']:.3f}")
    c.drawString(50, height-120, f"Variance : {stats['variance']:.3f}")
    c.drawString(50, height-140, f"Turbulence Intensity : {stats['TI']:.3f}")

    y = height - 200
    for fig in [fig1, fig2, fig3, fig4]:
        if fig is None:
            continue
        img = ImageReader(fig_to_img(fig))
        c.drawImage(img, 50, y-250, width=500, height=250)
        y -= 260
        if y < 100:
            c.showPage()
            y = height - 100

    c.save()