from pathlib import Path
import tempfile
import customtkinter as cst
import pandas as pd
from PIL import ImageGrab
from app.core.context import AppContext
from app.statistics.charts import Generate_chart
from app.ui.learning_layout import background
from app.ui.surfaces import surface

root = cst.CTk(); root.geometry('1280x600+40+40')
AppContext().bind(root)
backdrop = background(root, 'statistics_warm_v2.png')
host = cst.CTkFrame(root, fg_color='transparent', corner_radius=0)
host.pack(fill='both', expand=True)
host.grid_columnconfigure(0, weight=1)
surface(host, backdrop)
chart = cst.CTkFrame(host)
chart.grid_columnconfigure(0, weight=1)
chart.grid_rowconfigure(0, weight=1)
surface(chart, backdrop)
Generate_chart(pd.Series([26, 7, 2, 3, 2, 119, 206]), chart, 'Conjugation trailing successes', 0)
root.after(650, root.quit); root.mainloop()
path = Path(tempfile.gettempdir()) / 'vocabpro-conjugation-corners.png'
ImageGrab.grab(window=root.winfo_id()).save(path)
print(path)
print('radius', chart.cget('corner_radius'), 'inset', chart._chart_inset)
for child in tuple(root.winfo_children()): child.destroy()
for job in root.tk.call('after', 'info'): root.tk.call('after', 'cancel', job)
root.destroy()
