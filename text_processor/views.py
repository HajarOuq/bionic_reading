from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TextEntry
from .utils import bionic_reading
from .pdf_utils import extract_pdf_text
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.contrib.auth.decorators import login_required
from .models import TextEntry
from bs4 import BeautifulSoup

@login_required
def process_text(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            if uploaded_file.name.endswith('.txt'):
                text = uploaded_file.read().decode('utf-8')
            elif uploaded_file.name.endswith('.pdf'):
                text = extract_pdf_text(uploaded_file)

        bionic = bionic_reading(text)

        entry = TextEntry.objects.create(
            user=request.user,
            original_text=text,
            bionic_text=bionic,
            uploaded_file=uploaded_file
        )

        return render(request, 'text_processor/result.html', {'entry': entry})

    return render(request, 'text_processor/upload.html')

@login_required
def history_view(request):
    entries = TextEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'text_processor/history.html', {'entries': entries})

@login_required
def view_entry(request, pk):
    entry = get_object_or_404(TextEntry, pk=pk, user=request.user)
    return render(request, 'text_processor/result.html', {'entry': entry})

@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(TextEntry, pk=pk, user=request.user)
    entry.delete()
    return redirect('history')

@login_required
def download_pdf(request, pk):
    entry = TextEntry.objects.get(pk=pk, user=request.user)
    html_text = entry.bionic_text

    soup = BeautifulSoup(html_text, 'html.parser')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    x, y = 40, 800
    line_height = 18
    max_width = 500

    normal_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    font_size = 12

    # Helper to write a chunk of text (whole node at once)
    def write_text(text, bold):
        nonlocal x, y
        font_name = bold_font if bold else normal_font
        p.setFont(font_name, font_size)
        if not text.strip():
            return
        # Wrap text if needed
        text_width = p.stringWidth(text, font_name, font_size)
        if x + text_width > max_width:
            x = 40
            y -= line_height
            if y < 40:
                p.showPage()
                x, y = 40, 800
        p.drawString(x, y, text)
        x += text_width

    # Iterate over top-level elements only
    for elem in soup.contents:
        if elem.name == 'strong':
            write_text(elem.get_text(), bold=True)
        elif elem.name == 'br':
            x = 40
            y -= line_height
            if y < 40:
                p.showPage()
                x, y = 40, 800
        elif elem.string:
            write_text(elem.string, bold=False)

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bionic_text.pdf"'
    return response