"""Conjugation cards, shared sorting and antialiased chart surfaces."""
from unittest import TestCase
from unittest.mock import patch
import customtkinter as cst
import pandas as pd
from app.core.context import AppContext
from app.shared.translations import LANGUAGES, translate
from app.statistics.conjugation_panel import ConjugationProgressPanel
from app.statistics.table import StatisticsTable
from app.ui.surfaces import surface
from app.tests.ui_helpers import solid_surface


class ConjugationPresentationTests(TestCase):
    def setUp(self):
        self.root = cst.CTk(); self.root.geometry('1200x800')
        self.context = AppContext(); self.context.bind(self.root)
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)

    def tearDown(self):
        for widget in tuple(self.root.winfo_children()): widget.destroy()
        for job in self.root.tk.call('after', 'info'): self.root.tk.call('after', 'cancel', job)
        self.root.destroy()
        self.assertEqual(self.errors, [])

    def test_coverage_cards_resize_and_reuse_values_in_all_locales(self):
        for language in LANGUAGES:
            panel = ConjugationProgressPanel(self.root, lambda key: translate(key, language))
            panel.pack(fill='x', padx=20)
            panel.set_data(dict(practised=346, unpractised=19, covered_forms=1662))
            self.root.update()
            self.assertEqual([label.cget('text') for label in panel.values.values()], ['346', '19', '1662'])
            for label in panel.labels.values():
                self.assertLessEqual(label._label.winfo_reqwidth(), label.winfo_width() + 2)
                self.assertLessEqual(label._label.winfo_reqheight(), label.winfo_height() + 2)
                self.assertEqual(label.cget('fg_color'), 'transparent')
            with patch.object(panel.values['practised'], 'configure') as update:
                panel.set_data(dict(practised=346, unpractised=19, covered_forms=1662))
                update.assert_not_called()
            panel.set_data(None)
            self.assertTrue(all(label.cget('text') == '-' for label in panel.values.values()))
            panel.destroy()

    def test_sort_controls_use_numeric_cycle_header_sync_and_empty_reset(self):
        table = StatisticsTable(self.root, self.context.translate,
            sort_columns=('Recorded answers', 'Incorrect answers', 'Review accuracy'))
        table.pack(fill='x')
        data = pd.DataFrame({'Verb': ['c', 'a', 'b'], 'Recorded answers': [10, 2, 30],
                             'Incorrect answers': [5, 2, 1], 'Review accuracy': [50., 0., 96.67]})
        table.set_data(data); self.root.update()
        def verbs(): return [table.tree.item(item, 'values')[0] for item in table.tree.get_children()]
        for expected in (['a', 'c', 'b'], ['b', 'c', 'a'], ['c', 'a', 'b']):
            table.sort_buttons['Recorded answers'].invoke()
            self.assertEqual(verbs(), expected)
        table.sort('Review accuracy')
        self.assertIn('↑', table.sort_buttons['Review accuracy'].cget('text'))
        self.assertEqual(table.sort_buttons['Review accuracy'].cget('fg_color'), '#355e59')
        table.search.insert(0, 'b'); table._search_changed()
        self.assertEqual(verbs(), ['b'])
        table.set_data(data.iloc[:0])
        self.assertTrue(all(button.cget('state') == 'disabled' for button in table.sort_buttons.values()))
        pd.testing.assert_frame_equal(data, pd.DataFrame({'Verb': ['c', 'a', 'b'], 'Recorded answers': [10, 2, 30],
            'Incorrect answers': [5, 2, 1], 'Review accuracy': [50., 0., 96.67]}))

    def test_sort_labels_fit_all_locales_and_heading_does_not_change_global_theme(self):
        from tkinter import ttk
        theme = ttk.Style().theme_use()
        for language in LANGUAGES:
            table = StatisticsTable(self.root, lambda key: translate(key, language),
                sort_columns=('Recorded answers', 'Incorrect answers', 'Review accuracy'))
            table.pack(fill='x')
            table.set_data(pd.DataFrame({'Recorded answers': [10], 'Incorrect answers': [2], 'Review accuracy': [80.]}))
            self.root.update()
            for button in table.sort_buttons.values():
                self.assertLessEqual(button._text_label.winfo_reqwidth(), button.winfo_width() - 12)
            self.assertEqual(ttk.Style().theme_use(), theme)
            table.destroy()

    def test_chart_surface_pixels_match_composite_and_leave_native_buttons_alone(self):
        backdrop = solid_surface(self.root, '#123456')
        frame = cst.CTkFrame(self.root, width=300, height=180, corner_radius=24, fg_color='#e7d4c2')
        frame.pack(padx=20, pady=20)
        layer = surface(frame, backdrop, rasterize_frame=True)
        button = cst.CTkButton(self.root, text=translate('Close'), fg_color='#557b61')
        button.pack(); native = surface(button, backdrop)
        self.root.update(); layer.paint(); native.paint()
        for x, y in ((0, 0), (5, 5), (20, 20), (100, 80)):
            pixel = tuple(map(int, self.root.tk.call(str(layer._photo), 'get', x, y)))
            self.assertEqual(pixel, layer._image.getpixel((x, y)))
        self.assertEqual(layer.canvas.itemcget('inner_parts', 'state'), 'hidden')
        self.assertEqual(native.canvas.itemcget('inner_parts', 'state'), 'normal')
        photo = layer._photo
        layer.paint(); self.assertIs(layer._photo, photo)
