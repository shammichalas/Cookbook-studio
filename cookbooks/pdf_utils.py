import io
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Color Palette hex definitions
COLOR_BG = colors.HexColor('#FFFDF8')
COLOR_PRIMARY = colors.HexColor('#1F1F1F')
COLOR_ACCENT = colors.HexColor('#C65D3A')
COLOR_SECONDARY = colors.HexColor('#556B2F')
COLOR_HIGHLIGHT = colors.HexColor('#D9A441')
COLOR_CARD = colors.HexColor('#FFFFFF')
COLOR_BORDER = colors.HexColor('#ECE8E1')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to draw custom header, footer, and page numbers.
    Prevents hardcoding total pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        # Draw background color on all pages
        self.saveState()
        self.setFillColor(COLOR_BG)
        self.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        self.restoreState()

        # Cover page (Page 1) doesn't get headers/footers
        if self._pageNumber == 1:
            # Draw beautiful border on Cover Page
            self.saveState()
            self.setStrokeColor(COLOR_ACCENT)
            self.setLineWidth(2)
            self.rect(30, 30, A4[0] - 60, A4[1] - 60)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_PRIMARY)
        
        # Header (Top)
        self.drawString(54, A4[1] - 40, "COOKBOOK STUDIO COLLECTION")
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(54, A4[1] - 46, A4[0] - 54, A4[1] - 46)
        
        # Footer (Bottom)
        self.line(54, 50, A4[0] - 54, 50)
        self.drawString(54, 38, "Create, share and preserve your favorite recipes beautifully.")
        self.drawRightString(A4[0] - 54, 38, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()

def generate_cookbook_pdf(cookbook):
    """
    Generates a print-ready A4 PDF document containing
    cover page, table of contents, and all recipes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=36,
        leading=42,
        textColor=COLOR_ACCENT,
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=16,
        leading=22,
        textColor=COLOR_SECONDARY,
        alignment=1,
        spaceAfter=40
    )
    
    metadata_style = ParagraphStyle(
        'CoverMetadata',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=COLOR_PRIMARY,
        alignment=1
    )
    
    heading1_style = ParagraphStyle(
        'MainHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=24,
        leading=30,
        textColor=COLOR_PRIMARY,
        spaceBefore=15,
        spaceAfter=15
    )
    
    heading2_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=22,
        textColor=COLOR_ACCENT,
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=COLOR_PRIMARY,
        spaceAfter=8
    )
    
    italic_body = ParagraphStyle(
        'ItalicBody',
        parent=body_style,
        fontName='Helvetica-Oblique'
    )
    
    meta_badge_style = ParagraphStyle(
        'MetaBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1
    )

    category_badge_style = ParagraphStyle(
        'CategoryBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=COLOR_ACCENT,
        spaceAfter=5
    )

    story = []

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    story.append(Spacer(1, 150))
    story.append(Paragraph(cookbook.title, title_style))
    story.append(Spacer(1, 10))
    if cookbook.description:
        story.append(Paragraph(cookbook.description, subtitle_style))
    story.append(Spacer(1, 180))
    story.append(Paragraph(f"Curated by Chef {cookbook.owner.get_full_name() or cookbook.owner.username}", metadata_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"Published on {timezone.now().strftime('%B %d, %Y')}", metadata_style))
    story.append(Paragraph(f"Contains {cookbook.recipe_count} Exquisite Recipes", metadata_style))
    story.append(PageBreak())

    # ==========================================
    # 2. TABLE OF CONTENTS
    # ==========================================
    story.append(Spacer(1, 30))
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 15))
    
    toc_data = []
    # Header row
    toc_data.append([
        Paragraph("<b>Recipe Name</b>", body_style),
        Paragraph("<b>Difficulty</b>", body_style),
        Paragraph("<b>Category</b>", body_style),
        Paragraph("<b>Time</b>", body_style)
    ])
    
    for r in cookbook.recipes.all():
        toc_data.append([
            Paragraph(r.title, body_style),
            Paragraph(r.difficulty, body_style),
            Paragraph(r.category.name if r.category else "Uncategorized", body_style),
            Paragraph(f"{r.total_time} mins", body_style)
        ])
        
    toc_table = Table(toc_data, colWidths=[2.5*inch, 1.2*inch, 1.8*inch, 1.0*inch])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, COLOR_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ==========================================
    # 3. RECIPES PAGES
    # ==========================================
    for r in cookbook.recipes.all():
        recipe_story = []
        
        # Category header
        cat_name = r.category.name.upper() if r.category else "RECIPE"
        recipe_story.append(Paragraph(cat_name, category_badge_style))
        # Title
        recipe_story.append(Paragraph(r.title, heading1_style))
        recipe_story.append(Spacer(1, 10))

        # Metainfo table row
        meta_data = [
            [
                Paragraph("<b>PREP TIME</b>", body_style),
                Paragraph("<b>COOK TIME</b>", body_style),
                Paragraph("<b>SERVINGS</b>", body_style),
                Paragraph("<b>DIFFICULTY</b>", body_style),
            ],
            [
                Paragraph(f"{r.prep_time} mins", body_style),
                Paragraph(f"{r.cook_time} mins", body_style),
                Paragraph(f"{r.servings}", body_style),
                Paragraph(r.difficulty, body_style),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ECE8E1')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
        ]))
        recipe_story.append(meta_table)
        recipe_story.append(Spacer(1, 15))

        # Ingredients (Checklist format)
        recipe_story.append(Paragraph("Ingredients", heading2_style))
        ingredients_list = []
        for ing in r.ingredients.all():
            amt_unit = f"<b>{ing.amount} {ing.unit}</b>" if ing.amount or ing.unit else ""
            item_text = f"[  ]  {amt_unit} {ing.name}"
            ingredients_list.append([Paragraph(item_text, body_style)])
            
        if ingredients_list:
            ing_table = Table(ingredients_list, colWidths=[6.4*inch])
            ing_table.setStyle(TableStyle([
                ('PADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            recipe_story.append(ing_table)
        else:
            recipe_story.append(Paragraph("<i>No ingredients listed.</i>", body_style))
        recipe_story.append(Spacer(1, 15))

        # Cooking Steps
        recipe_story.append(Paragraph("Preparation & Method", heading2_style))
        for step in r.steps.all():
            step_heading = f"<b>Step {step.step_number}</b>"
            recipe_story.append(Paragraph(step_heading, body_style))
            recipe_story.append(Paragraph(step.description, body_style))
            if step.tip:
                tip_text = f"<i>Chef's Tip: {step.tip}</i>"
                recipe_story.append(Paragraph(tip_text, italic_body))
            recipe_story.append(Spacer(1, 8))

        # Chef Notes Box
        if r.chef_notes:
            recipe_story.append(Spacer(1, 10))
            notes_data = [[
                Paragraph("<b>Chef Notes</b><br/>" + r.chef_notes.replace('\n', '<br/>'), body_style)
            ]]
            notes_table = Table(notes_data, colWidths=[6.4*inch])
            notes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAF7F2')),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('LINELEFT', (0, 0), (0, -1), 3, COLOR_ACCENT),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ]))
            recipe_story.append(notes_table)

        # Nutrition Card
        recipe_story.append(Spacer(1, 12))
        nut_data = [
            [
                Paragraph("<b>CALORIES</b>", body_style),
                Paragraph("<b>CARBS</b>", body_style),
                Paragraph("<b>PROTEIN</b>", body_style),
                Paragraph("<b>FAT</b>", body_style)
            ],
            [
                Paragraph(f"{r.nutrition_calories} kcal", body_style),
                Paragraph(f"{r.nutrition_carbs}g", body_style),
                Paragraph(f"{r.nutrition_protein}g", body_style),
                Paragraph(f"{r.nutrition_fat}g", body_style)
            ]
        ]
        nut_table = Table(nut_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
        nut_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAF7F2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ]))
        recipe_story.append(nut_table)

        # Build recipe elements as a cohesive section
        story.append(KeepTogether(recipe_story))
        story.append(PageBreak())

    # ==========================================
    # 4. ENDING PAGE
    # ==========================================
    story.append(Spacer(1, 200))
    end_title = ParagraphStyle(
        'EndTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=28,
        leading=34,
        textColor=COLOR_PRIMARY,
        alignment=1,
        spaceAfter=15
    )
    story.append(Paragraph("Discovery is in the Details", end_title))
    story.append(Paragraph("Thank you for sharing the journey of creating beautiful meals.", metadata_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("COOKBOOK STUDIO", metadata_style))
    story.append(Paragraph("www.cookbookstudio.com", metadata_style))

    # Build the document using our NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
