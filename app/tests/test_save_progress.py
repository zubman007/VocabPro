"""Save card geometry and localized counts, without writing course files."""
from unittest import TestCase
import customtkinter as cst
from app.ui.components.save_progress import SaveProgress
from app.shared.translations import translate


class SaveProgressTests(TestCase):
    def test_counts_background_and_all_locales_fit_narrow_and_wide_headers(self):
        root=cst.CTk();root.geometry('1000x450')
        errors=[];root.report_callback_exception=lambda *args:errors.append(args)
        try:
            for locale in ('cs','en','de','es','fr','sk'):
                for width in (600,1000):
                    with self.subTest(locale=locale,width=width):
                        root.geometry(f'{width}x450')
                        panel=SaveProgress(root,lambda key:translate(key,locale))
                        panel.pack(fill='x',padx=20,pady=20)
                        panel.update_progress(1234,2846);root.update()
                        self.assertIn('1234 / 2846',panel.processed.cget('text'))
                        self.assertIn('1612',panel.remaining.cget('text'))
                        self.assertAlmostEqual(panel.bar.get(),1234/2846)
                        for label in (panel.heading,panel.processed,panel.remaining):
                            self.assertEqual(label.cget('fg_color'),'transparent')
                            self.assertNotIn('?',label.cget('text'))
                            self.assertLessEqual(label._label.winfo_reqwidth(),label.winfo_width()+2)
                            self.assertGreaterEqual(label.winfo_rootx(),panel.winfo_rootx()+10)
                            self.assertLessEqual(label.winfo_rootx()+label.winfo_width(),panel.winfo_rootx()+panel.winfo_width()-10)
                        panel.update_progress(2846,2846)
                        self.assertIn(': 0',panel.remaining.cget('text'))
                        self.assertEqual(panel.bar.get(),1)
                        panel.destroy()
        finally:
            for job in root.tk.call('after','info'):root.tk.call('after','cancel',job)
            root.destroy()
        self.assertEqual(errors,[])
