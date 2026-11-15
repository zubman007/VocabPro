"""Rounded filter controls with separate dropdown arrows and consistent colors."""
from app.ui.components.search_filter_panel import SearchFilterPanel
from app.ui.module_style import tool_button
from app.ui.theme import FONT
import customtkinter as cst
from app.vocabulary.tags_data import normalize_tags


def filterable_headers(headers, tags_enabled=True):
    excluded = {'Repetition', 'Next repetition', 'Phonetic'}
    if not tags_enabled:excluded.update(('Tags', 'Tag count'))
    return [name for name in headers if name not in excluded]


class VocabularyFilter(SearchFilterPanel):
    def __init__(self, parent, columns, operators, column_var, operator_var, query_var,
                 translate, apply_filter, reset_filter, select_tags=None, on_change=None):
        super().__init__(parent,translate,query_var=query_var,on_apply=apply_filter,
                         on_reset=reset_filter,on_change=on_change)
        # Text, operators and tag selection apply directly; Enter still submits immediately.
        self.apply.destroy()
        self.apply=None
        self.column=self.add_choice('column',columns,variable=column_var,width=230)
        self.operator=self.add_choice('operator',operators,variable=operator_var,width=150)
        self.tag_mode=False
        self.tag_selection=''
        self.tag_operators={translate(label):key for key,label in (
            ('all','Contains all tags'),('none','Contains none of the tags'),('exact','Contains exactly these tags'))}
        self._operators=list(operators)
        self._operator_var=operator_var
        self._text_operator=operator_var.get()
        self._tag_operator=next(iter(self.tag_operators))
        self.tag_button=tool_button(cst.CTkButton(self,text=translate('Select tags'),command=select_tags))
        self.tag_button.configure(height=40)

    def set_tag_mode(self,active):
        if active==self.tag_mode:return
        if active:
            self._text_operator=self._operator_var.get()
            self.query.grid_remove()
            self.tag_button.grid(row=0,column=2,sticky='ew',padx=8,pady=12)
            scale=self._get_widget_scaling()
            font=cst.CTkFont(family=FONT,size=round(17*scale))
            width=max(260,max(font.measure(label)/scale for label in self.tag_operators)+60)
            self.operator.configure(values=list(self.tag_operators),width=width)
            self._operator_var.set(self._tag_operator)
        else:
            self._tag_operator=self._operator_var.get()
            self.tag_button.grid_remove()
            self.query.grid()
            self.operator.configure(values=self._operators,width=150)
            self._operator_var.set(self._text_operator)
        self.tag_mode=active

    def set_tag_selection(self,value):
        self.tag_selection=normalize_tags(value)
        count=len(self.tag_selection.split(', ')) if self.tag_selection else 0
        self.tag_button.configure(text=self.translate('Selected tags: {count}').format(count=count)
            if count else self.translate('Select tags'))
