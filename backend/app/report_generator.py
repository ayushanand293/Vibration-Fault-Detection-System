import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Custom canvas with page numbers and elegant header"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw elegant page footer"""
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor('#6b7280'))
        self.drawRightString(7.75*inch, 0.5*inch, f"Page {self._pageNumber} of {page_count}")
        
        self.setStrokeColor(colors.HexColor('#667eea'))
        self.setLineWidth(3)
        self.line(0.75*inch, 10.6*inch, 7.75*inch, 10.6*inch)
        
        self.setStrokeColor(colors.HexColor('#e5e7eb'))
        self.setLineWidth(1)
        self.line(0.75*inch, 0.7*inch, 7.75*inch, 0.7*inch)

class ReportGenerator:
    """Generate professional PDF diagnostic reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles with proper spacing"""
        
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=36,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=42
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            leftIndent=0,
            leading=20,
            borderWidth=0,
            borderPadding=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            leading=11,
            spaceAfter=3
        ))
    
    def generate_pdf(self, signal, sampling_rate, features, prediction, confidence, probabilities):
        """Generate comprehensive PDF report"""
        
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.1*inch,
            bottomMargin=0.9*inch
        )
        
        story = []
        
        # TITLE
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph('BEARING DIAGNOSTIC REPORT', self.styles['CustomTitle']))
        story.append(Paragraph('AI-Powered Vibration Analysis System', self.styles['Subtitle']))
        story.append(Spacer(1, 0.4*inch))
        
        # METADATA
        metadata_data = [
            ['Report Date', datetime.now().strftime('%B %d, %Y')],
            ['Time Generated', datetime.now().strftime('%I:%M %p')],
            ['Sampling Rate', f'{sampling_rate:,} Hz'],
            ['Signal Length', f'{len(signal):,} samples'],
            ['ML Algorithm', 'Random Forest Classifier']
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2.3*inch, 3.7*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#0284c7')),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#bae6fd')),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 0.5*inch))
        
        # STATUS BADGE
        is_healthy = prediction.lower() == 'normal'
        status_color = colors.HexColor('#10b981') if is_healthy else colors.HexColor('#ef4444')
        status_bg = colors.HexColor('#d1fae5') if is_healthy else colors.HexColor('#fee2e2')
        status_icon = 'HEALTHY' if is_healthy else 'FAULT DETECTED'
        
        status_para = Paragraph(
            f'<b>{status_icon}</b>',
            ParagraphStyle('StatusPara', parent=self.styles['Normal'],
                          fontSize=24, textColor=status_color,
                          alignment=TA_CENTER, fontName='Helvetica-Bold', leading=28)
        )
        
        status_badge = [[status_para]]
        badge_table = Table(status_badge, colWidths=[6*inch], rowHeights=[0.7*inch])
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), status_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2.5, status_color),
        ]))
        
        story.append(KeepTogether([badge_table]))
        story.append(Spacer(1, 0.35*inch))
        
        # DIAGNOSIS DETAILS
        result_para1 = Paragraph(
            f'<b>Fault Classification:</b> {prediction.upper().replace("_", " ")}',
            ParagraphStyle('ResultPara', parent=self.styles['Normal'], 
                          fontSize=14, textColor=colors.HexColor('#374151'), 
                          alignment=TA_LEFT, leading=18)
        )
        
        result_para2 = Paragraph(
            f'<b>Confidence Level:</b> <font color="{status_color.hexval()}">{confidence*100:.1f}%</font>',
            ParagraphStyle('ResultPara2', parent=self.styles['Normal'], 
                          fontSize=14, textColor=colors.HexColor('#374151'), 
                          alignment=TA_LEFT, leading=18)
        )
        
        result_data = [[result_para1], [result_para2]]
        result_table = Table(result_data, colWidths=[6*inch], rowHeights=[0.5*inch, 0.5*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
            ('PADDING', (0, 0), (-1, -1), 14),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#667eea')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#e5e7eb')),
        ]))
        
        story.append(KeepTogether([result_table]))
        story.append(Spacer(1, 0.45*inch))
        
        # PROBABILITY ANALYSIS (GRAPHICAL BARS)
        story.append(Paragraph('Fault Probability Analysis', self.styles['CustomHeading']))
        story.append(Spacer(1, 0.15*inch))
        
        fault_labels = {
            'normal': 'Normal Operation',
            'ball': 'Ball Bearing Fault',
            'inner_race': 'Inner Race Fault',
            'outer_race': 'Outer Race Fault'
        }
        
        for fault_type in ['normal', 'ball', 'inner_race', 'outer_race']:
            prob = probabilities.get(fault_type, 0)
            print(f"DEBUG: {fault_type} = {prob:.3f}")
            
            bar_img = self._generate_probability_bar(
                fault_labels[fault_type], 
                prob,
                fault_type == prediction.lower()
            )
            story.append(Image(bar_img, width=6*inch, height=0.6*inch))
            story.append(Spacer(1, 0.08*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # SIGNAL VISUALIZATION
        story.append(Paragraph('Signal Visualization', self.styles['CustomHeading']))
        story.append(Spacer(1, 0.15*inch))
        
        time_plot = self._generate_time_plot(signal, sampling_rate)
        story.append(Image(time_plot, width=6.5*inch, height=2.8*inch))
        story.append(Spacer(1, 0.25*inch))
        
        freq_plot = self._generate_freq_plot(signal, sampling_rate)
        story.append(Image(freq_plot, width=6.5*inch, height=2.8*inch))
        story.append(Spacer(1, 0.4*inch))
        
        # EXTRACTED FEATURES
        story.append(Paragraph('Extracted Features', self.styles['CustomHeading']))
        story.append(Spacer(1, 0.15*inch))
        
        feature_items = list(features.items())
        mid = len(feature_items) // 2
        
        feature_data = [['Feature', 'Value', 'Feature', 'Value']]
        
        for i in range(mid):
            left = feature_items[i]
            right = feature_items[mid + i] if (mid + i) < len(feature_items) else ('', '')
            feature_data.append([
                left[0].replace('_', ' ').title(),
                f'{left[1]:.5f}',
                right[0].replace('_', ' ').title() if right[0] else '',
                f'{right[1]:.5f}' if right[0] else ''
            ])
        
        feature_table = Table(feature_data, colWidths=[1.85*inch, 1.15*inch, 1.85*inch, 1.15*inch])
        feature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ]))
        
        story.append(feature_table)
        story.append(Spacer(1, 0.4*inch))
        
        # RECOMMENDATIONS
        story.append(Paragraph('Maintenance Recommendations', self.styles['CustomHeading']))
        story.append(Spacer(1, 0.15*inch))
        
        recommendations = {
            'normal': (
                '<b>NO ACTION REQUIRED</b><br/><br/>'
                'The bearing is operating within normal parameters. '
                'Continue standard monitoring schedule and periodic inspections.'
            ),
            'ball': (
                '<b>CRITICAL - IMMEDIATE ACTION REQUIRED</b><br/><br/>'
                'Ball bearing fault detected with high confidence. '
                '<b>Replace bearing immediately</b> to prevent catastrophic failure and equipment damage.'
            ),
            'inner_race': (
                '<b>HIGH PRIORITY MAINTENANCE</b><br/><br/>'
                'Inner race fault identified. Schedule bearing replacement <b>within 48 hours</b>. '
                'Monitor vibration levels closely until replacement.'
            ),
            'outer_race': (
                '<b>MEDIUM PRIORITY MAINTENANCE</b><br/><br/>'
                'Outer race fault detected. Schedule bearing replacement <b>within 72 hours</b>. '
                'Increase monitoring frequency until maintenance is completed.'
            )
        }
        
        rec_text = recommendations.get(prediction.lower(), 'Consult maintenance engineer for detailed assessment.')
        
        rec_para = Paragraph(rec_text, ParagraphStyle(
            'RecText', parent=self.styles['Normal'],
            fontSize=10, leading=14, textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY
        ))
        
        rec_data = [[rec_para]]
        rec_table = Table(rec_data, colWidths=[6*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), 
             colors.HexColor('#fffbeb') if not is_healthy else colors.HexColor('#f0fdf4')),
            ('PADDING', (0, 0), (-1, -1), 16),
            ('BOX', (0, 0), (-1, -1), 2, status_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(rec_table)
        story.append(Spacer(1, 0.5*inch))
        
        # FOOTER
        story.append(Paragraph('─' * 100, self.styles['Footer']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph('<b>Vibration Analysis System</b> | Powered by Machine Learning', self.styles['Footer']))
        story.append(Paragraph('© 2025 All Rights Reserved | Confidential Report', self.styles['Footer']))
        
        doc.build(story, canvasmaker=NumberedCanvas)
        
        return buffer.getvalue()
    
    def _generate_probability_bar(self, label, probability, is_prediction):
        """Generate a graphical probability bar"""
        
        fig, ax = plt.subplots(figsize=(8, 0.8), facecolor='white')
        fig.patch.set_facecolor('#ffffff')
        
        # Colors
        if is_prediction:
            bar_color = '#667eea'
            bg_color = '#e0e7ff'
            text_color = '#1f2937'
            bar_edgecolor = '#4f46e5'
        else:
            bar_color = '#9ca3af'
            bg_color = '#f3f4f6'
            text_color = '#6b7280'
            bar_edgecolor = '#d1d5db'
        
        # Background bar
        ax.barh(0, 1.0, height=0.5, color=bg_color, edgecolor='none', left=0)
        # Filled bar
        ax.barh(0, probability, height=0.5, color=bar_color, 
                edgecolor=bar_edgecolor, linewidth=2, left=0)
        
        # Label
        ax.text(-0.02, 0, label, va='center', ha='right', 
                fontsize=11, fontweight='bold' if is_prediction else 'normal',
                color=text_color)
        
        # Percentage (outside)
        percentage_text = f'{probability*100:.1f}%'
        ax.text(1.02, 0, percentage_text, va='center', ha='left',
                fontsize=11, fontweight='bold' if is_prediction else 'normal',
                color=text_color)
        
        # Percentage (inside if space)
        if probability > 0.15:
            ax.text(probability/2, 0, percentage_text, va='center', ha='center',
                    fontsize=10, fontweight='bold', color='white')
        
        ax.set_xlim(-0.35, 1.15)
        ax.set_ylim(-0.35, 0.35)
        ax.axis('off')
        
        plt.tight_layout(pad=0)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none', pad_inches=0.05)
        plt.close(fig)
        buffer.seek(0)
        
        return buffer
    
    def _generate_time_plot(self, signal, sampling_rate):
        """Generate professional time-domain plot"""
        
        fig, ax = plt.subplots(figsize=(9, 3.2), facecolor='white')
        fig.patch.set_facecolor('#f8fafc')
        
        time = np.arange(len(signal)) / sampling_rate
        
        ax.plot(time, signal, color='#667eea', linewidth=1.5, alpha=0.9, label='Vibration Signal')
        ax.fill_between(time, signal, alpha=0.12, color='#667eea')
        
        ax.set_xlabel('Time (seconds)', fontsize=10, fontweight='600', color='#374151')
        ax.set_ylabel('Amplitude', fontsize=10, fontweight='600', color='#374151')
        ax.set_title('Time-Domain Vibration Signal', fontsize=12, fontweight='bold', 
                     color='#1f2937', pad=12)
        
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.7, color='#94a3b8')
        ax.set_facecolor('#ffffff')
        ax.legend(loc='upper right', framealpha=0.95, fontsize=9)
        
        for spine in ax.spines.values():
            spine.set_edgecolor('#cbd5e1')
            spine.set_linewidth(1.2)
        
        ax.tick_params(labelsize=8, colors='#6b7280')
        
        plt.tight_layout(pad=0.5)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', 
                   facecolor='#f8fafc', edgecolor='none')
        plt.close(fig)
        buffer.seek(0)
        
        return buffer
    
    def _generate_freq_plot(self, signal, sampling_rate):
        """Generate professional frequency-domain plot"""
        
        fig, ax = plt.subplots(figsize=(9, 3.2), facecolor='white')
        fig.patch.set_facecolor('#f8fafc')
        
        fft = np.fft.fft(signal)
        freq = np.fft.fftfreq(len(signal), 1/sampling_rate)
        positive_idx = freq > 0
        freq = freq[positive_idx]
        fft_mag = np.abs(fft[positive_idx])
        
        ax.plot(freq, fft_mag, color='#ef4444', linewidth=1.5, alpha=0.9, label='FFT Magnitude')
        ax.fill_between(freq, fft_mag, alpha=0.12, color='#ef4444')
        
        ax.set_xlabel('Frequency (Hz)', fontsize=10, fontweight='600', color='#374151')
        ax.set_ylabel('Magnitude', fontsize=10, fontweight='600', color='#374151')
        ax.set_title('Frequency Spectrum (FFT)', fontsize=12, fontweight='bold', 
                     color='#1f2937', pad=12)
        
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.7, color='#94a3b8')
        ax.set_facecolor('#ffffff')
        ax.set_xlim(0, min(2500, freq.max()))
        ax.legend(loc='upper right', framealpha=0.95, fontsize=9)
        
        for spine in ax.spines.values():
            spine.set_edgecolor('#cbd5e1')
            spine.set_linewidth(1.2)
        
        ax.tick_params(labelsize=8, colors='#6b7280')
        
        plt.tight_layout(pad=0.5)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', 
                   facecolor='#f8fafc', edgecolor='none')
        plt.close(fig)
        buffer.seek(0)
        
        return buffer
