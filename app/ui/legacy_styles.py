"""Remaining vocabulary/statistics styles; shared components use app.ui.theme."""
from tkinter import NORMAL
from app.ui.theme import FONT

def _lbl_set(font, text_color="white", bg_color=None, fg_color=None, height=7, **extra):
    data = {"height": height, "font": font, "text_color": text_color, **extra}
    if bg_color is not None: data["bg_color"] = bg_color
    if fg_color is not None: data["fg_color"] = fg_color
    return data

def _btn_set(fg_color,font,text_color="white",bg_color=None,hover_color="black",border_color="black",border_width=3,corner_radius=15,state=NORMAL,**extra):
    data = {"border_color": border_color,"border_width": border_width,"corner_radius": corner_radius,"text_color": text_color,"fg_color": fg_color,"font": font,"state": state,**extra,}
    if bg_color is not None: data["bg_color"] = bg_color
    if hover_color is not None: data["hover_color"] = hover_color
    return data

font_01 = (FONT, 25)
font_03 = (FONT, 25, "normal")
font_07 = (FONT, 45, "normal")
font_08 = (FONT, 30, "normal")
font_09 = (FONT, 30, "bold")
font_12 = (FONT, 35)
font_13 = (FONT, 17, "normal")
font_16 = (FONT, 25, "italic")
font_17 = (FONT, 30, "italic")
font_18 = (FONT, 40, "bold")

clr_btn_1 = "#5f8840"
clr_btn_2 = "#5470de"
clr_bg = "#aecbcf"
clr_bg_stats = "#d0cfc6"
clr_border = "#ff4d57"
clr_border_2 = "#979da2"
clr_sel = "#ff4d57"
clr_tbl_bg = "#527043"
clr_tbl_bg_2 = "#384d2e"
clr_tbl_sel = "#828282"
clr_tbl_sel_cell_border = "#1b7a01"
clr_popup_menu_bg = "#a6a4a4"
clr_repeat_bg = "#174523"
clr_bg_trans = "#dad9db"
clr_bg_letters = "#3ec762"

lbl_set_03 = _lbl_set(font_08)
lbl_set_05 = _lbl_set(font_07, fg_color=clr_bg_letters)
lbl_set_07 = _lbl_set(font_09, text_color="black", bg_color=clr_bg_stats)
lbl_set_11 = _lbl_set(font_07, fg_color=clr_repeat_bg)
lbl_set_12 = _lbl_set(font_08, fg_color=clr_repeat_bg)
lbl_set_13 = _lbl_set(font_03)
lbl_set_18 = _lbl_set(font_16)
lbl_set_19 = _lbl_set(font_18)
lbl_set_20 = _lbl_set(font_17)


btn_set_1 = _btn_set(clr_btn_1, font_01, bg_color=clr_bg_trans)
btn_set_6 = _btn_set(clr_btn_2, font_01, bg_color=clr_repeat_bg)
btn_set_7 = _btn_set("white",font_01,text_color="black",bg_color=clr_bg_letters,hover_color=clr_btn_2)

entry_set_01 = {"fg_color": clr_bg_trans,"bg_color": clr_bg_trans,"corner_radius": 10,"border_color": clr_border_2,"font": font_12,"height": 50,"text_color": "black","state": NORMAL}
tbl_bind = ("single_select","drag_select","column_select","row_select","column_width_resize","double_click_column_resize","double_click_row_resize","column_height_resize","row_height_resize" ,"undo","copy","cut","paste","edit_cell","arrowkeys","right_click_popup_menu")
tbl_set = {
    'show_row_index': True,
    'show_top_left': False,
    'show_x_scrollbar': True,
    'show_y_scrollbar': True,
    'table_fg': 'white',
    'show_horizontal_grid': True,
    'show_vertical_grid': True,
    'table_grid_fg': "white",
    'frame_bg': clr_tbl_bg,
    'header_bg': clr_tbl_bg,
    'header_fg': 'white',
    'header_border_fg': clr_border,
    'header_grid_fg': clr_tbl_bg,
    'header_selected_cells_bg': clr_sel,
    'header_selected_columns_bg': clr_sel,
    'header_selected_cells_fg': 'white',
    'table_bg': clr_tbl_bg_2,
    'index_bg': clr_tbl_bg,
    'index_fg': 'white',
    'index_selected_cells_bg': clr_sel,
    'index_selected_cells_fg': 'white',
    'index_selected_rows_bg': clr_sel,
    'index_grid_fg': clr_tbl_bg,
    'resizing_line_fg': clr_tbl_bg,
    'popup_menu_fg': 'black',
    'popup_menu_bg': clr_popup_menu_bg,
    'popup_menu_highlight_bg': 'black',
    'popup_menu_highlight_fg': 'white',
    'popup_menu_font': font_03,
    'header_font': font_03,
    'index_font': font_03,
    'font': font_13,
    'table_selected_cells_border_fg': clr_tbl_sel_cell_border,
    'table_selected_cells_bg': clr_tbl_sel,
    'table_selected_cells_fg': 'white',
    'table_selected_rows_bg': clr_tbl_sel,
    'table_selected_rows_fg': 'white',
    'table_selected_columns_bg': clr_tbl_sel,
    'table_selected_columns_fg': 'white',
    'drag_and_drop_bg': 'green',
    'outline_thickness' : 2,
    'outline_color' : clr_border
}