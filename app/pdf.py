import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from datetime import date
import glob

def generate_health_report(title, dates, bpm, spo2, weight, systolic, diastolic, patient_name, device_serial, data_analysis):
    output_dir = "./temp"
    os.makedirs(output_dir, exist_ok=True)  # ✅ Create folder if it doesn't exist
    
    for f in glob.glob(os.path.join(output_dir, "*.png")):
        os.remove(f)


    def create_plot(y_values, title, ylabel, filename, extra_y=None, extra_label=None):
        plt.figure(figsize=(4, 3))
        plt.plot(dates, y_values, marker='o', label=ylabel)
        plt.xticks(rotation=45)  # or rotation=30
        plt.locator_params(axis='x', nbins=5)  # Show ~5 ticks only
        if extra_y is not None:
            plt.plot(dates, extra_y, marker='o', label=extra_label)
        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel(ylabel if not extra_label else "mmHg")
        plt.grid(True)
        if extra_label:
            plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    # Create plots
    create_plot(bpm, "Heart Rate", "BPM", "bpm.png")
    create_plot(spo2, "Oxygen Saturation", "SpO₂ (%)", "spo2.png")
    create_plot(weight, "Weight", "lbs", "weight.png")
    create_plot(systolic, "Blood Pressure", "Systolic", "bp.png", extra_y=diastolic, extra_label="Diastolic")

    # Create PDF
    pdf = FPDF()
    pdf.add_page()

    logo_path = "./app/static/images/medhome_logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=10, w=50)

    pdf.set_font("Arial", 'B', 16)
    pdf.set_y(30)
    pdf.cell(200, 10, title, ln=True, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 8, f"Date: {date.today().isoformat()}", ln=True, align="C")
    pdf.cell(200, 8, f"Patient Name: {patient_name}", ln=True, align="C")
    pdf.cell(200, 8, f"Device Serial #: {device_serial}", ln=True, align="C")

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Vitals Overview", ln=True, align="L")
    pdf.ln(4)

    positions = [
        (10, pdf.get_y()), (110, pdf.get_y()),
        (10, pdf.get_y() + 75), (110, pdf.get_y() + 75)
    ]
    images = ["bpm.png", "spo2.png", "weight.png", "bp.png"]

    for (x, y), img in zip(positions, images):
        pdf.image(os.path.join(output_dir, img), x=x, y=y, w=90, h=60)

    # Position cursor below the last row of charts
    pdf.set_y(positions[-1][1] + 65)

    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Add data analysis
    if data_analysis:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Data Analysis", ln=True, align="L")
        pdf.set_font("Arial", '', 12)
        for line in data_analysis.strip().split('\n'):
            pdf.multi_cell(0, 8, line)


    pdf_path = os.path.join(output_dir, "health_report.pdf")
    pdf.output(pdf_path)

    print(f"✅ PDF generated: {pdf_path}")

    return {"success"}

"""
    Example usage:
   
    generate_health_report(
        dates=["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
        bpm=[72, 75, 78, 74, 77],
        spo2=[97, 98, 99, 97, 96],
        weight=[150, 152, 151, 153, 150],
        systolic=[120, 122, 118, 121, 119],
        diastolic=[80, 82, 78, 79, 77],
        patient_name="John Doe",
        device_serial="SN-0012345678",
        data_analysis="This is a sample data analysis."
    )

"""

if __name__ == "__main__":
    # Example usage
    generate_health_report(
        title="Health Report",
        dates=["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
        bpm=[72, 75, 78, 74, 77],
        spo2=[97, 98, 99, 97, 96],
        weight=[150, 152, 151, 153, 150],
        systolic=[120, 122, 118, 121, 119],
        diastolic=[80, 82, 78, 79, 77],
        patient_name="John Doe",
        device_serial="SN-0012345678",
        data_analysis="This is a sample data analysis."
    )
