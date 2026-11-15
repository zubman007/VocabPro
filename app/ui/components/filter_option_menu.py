"""Filter dropdown with a continuous vector arrow instead of a font glyph."""
import customtkinter as cst


class FilterOptionMenu(cst.CTkOptionMenu):
    def _draw(self,no_color_updates=False):
        super()._draw(no_color_updates)
        # Keep CTk's original item for its renderer, but hide the font-based glyph.
        self._canvas.itemconfigure('dropdown_arrow',state='hidden')
        scale=self._get_widget_scaling()
        x=(self._current_width-self._current_height/2)*scale
        y=self._current_height/2*scale
        if not self._canvas.find_withtag('filter_arrow'):
            self._canvas.create_line(0,0,0,0,0,0,tags='filter_arrow',
                capstyle='round',joinstyle='round')
        self._canvas.coords('filter_arrow',x-4*scale,y-2*scale,x,y+2*scale,x+4*scale,y-2*scale)
        color=self.cget('text_color_disabled') if self.cget('state')=='disabled' else self.cget('text_color')
        self._canvas.itemconfigure('filter_arrow',fill=self._apply_appearance_mode(color),width=max(2,1.8*scale))
        self._canvas.tag_raise('filter_arrow')
