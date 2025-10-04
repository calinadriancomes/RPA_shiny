from shiny import App, ui, render, reactive
import os
import shutil
from lumber5 import process_file  # make sure lumber5.py is in the same folder

# === Config ===
OUTPUT_DIR = "C:/shiny_app/generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Reactive state ===
output_tables_path = reactive.Value(None)
plan_fertilizare_path = reactive.Value(None)
status_message = reactive.Value("")

# === UI ===
app_ui = ui.page_fluid(
    ui.h2("ETL – Cerere Unică de Plată (Shiny App v7)"),

    ui.input_text("an_input", "Anul cererii:", value="2024"),
    ui.input_file("pdf_file", "Încărcați fișierul PDF IPA-Online", accept=[".pdf"]),
    ui.input_action_button("run_btn", "Procesează PDF-ul"),

    ui.hr(),
    ui.output_text_verbatim("result_text"),

    # Container where the download buttons appear after processing
    ui.output_ui("downloads_ui")
)

# === Server ===
def server(input, output, session):
    @reactive.effect
    @reactive.event(input.run_btn)
    def _():
        # reset reactive paths so UI hides buttons until ready
        output_tables_path.set(None)
        plan_fertilizare_path.set(None)

        pdf_list = input.pdf_file()
        if not pdf_list:
            status_message.set("⚠️ Vă rugăm să încărcați un fișier PDF.")
            return

        an_text = input.an_input().strip()
        if not an_text:
            status_message.set("⚠️ Introduceți anul cererii.")
            return

        pdf_file = pdf_list[0]
        pdf_path = os.path.join(OUTPUT_DIR, pdf_file["name"])
        # copy uploaded file to our persistent output folder
        shutil.copy(pdf_file["datapath"], pdf_path)

        try:
            # process_file writes outputs into the same folder as the PDF (OUTPUT_DIR)
            out_tables, plan_path, stats = process_file(pdf_path, an_text=an_text)

            # set reactive values so UI updates and buttons appear
            output_tables_path.set(out_tables)
            plan_fertilizare_path.set(plan_path)

            status_message.set(
                f"✅ Procesare completă!\n"
                f"- Fișier tabel: {os.path.basename(out_tables)}\n"
                f"- Fișier plan: {os.path.basename(plan_path)}\n"
                f"- Rânduri parse: {stats[0]}\n"
                f"- Culturi: {stats[1]}\n"
                f"- Categorii: {stats[2]}"
            )
        except Exception as e:
            status_message.set(f"❌ Eroare la procesare: {str(e)}")

    @render.text
    def result_text():
        return status_message()

    @render.ui
    def downloads_ui():
        out_path = output_tables_path()
        plan_path = plan_fertilizare_path()

        if out_path and plan_path and os.path.isfile(out_path) and os.path.isfile(plan_path):
            # IMPORTANT: The function names below must match these IDs
            return ui.div(
                ui.h4("📥 Descărcați fișierele generate:"),
                ui.download_button("download_tables", "⬇️ Descarcă output_tables.xlsx"),
                ui.download_button("download_plan", "⬇️ Descarcă Plan_de_fertilizare.xlsx"),
                ui.hr(),
                ui.p(f"📁 Fișierele sunt salvate permanent în: {OUTPUT_DIR}")
            )
        return ui.div()

    # The function name MUST MATCH the download_button id: "download_tables"
    @render.download
    def download_tables():
        path = output_tables_path()
        # Return (file_path, download_filename)
        return path, os.path.basename(path)

    # The function name MUST MATCH the download_button id: "download_plan"
    @render.download
    def download_plan():
        path = plan_fertilizare_path()
        return path, os.path.basename(path)

# === Launch ===
app = App(app_ui, server)
