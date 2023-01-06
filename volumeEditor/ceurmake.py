import datetime

import justpy as jp
from addict import Dict

from volumeEditor.DropZone import Demo
from volumeEditor.template_handler import VolumePageTemplate
from volumeEditor.volume_form import VolumeForm


class CeurVolumeForm(jp.Div):
    """
    Interactive editor to create a ceur-ws proceedings volume
    """

    def __init__(self, **kwargs):
        """
        constructor
        """
        super(CeurVolumeForm, self).__init__(**kwargs)
        self.volume = VolumeForm(a=self)
        self.preview_btn = jp.Button(
                a=self,
                text="Generate Preview",
                classes=jp.Styles.button_simple,
                on_click=self.handle_generate_preview
        )
        self.preview_div = jp.Div(a=self, classes="h-full")

    def handle_generate_preview(self, msg):
        """
        handle generate preview click
        """
        self.generate_preview()

    def get_prepared_volume_record(self) -> Dict:
        volume = Dict(self.volume.get_record())
        # add placeholder values
        volume.vol_number = "Vol-????"
        volume.number = "????"
        volume.publication_year = datetime.datetime.now().year
        if volume.start_date:
            volume.year = volume.start_date.year


        for i, editor in enumerate(volume.editors):
            editor.name = f"{editor.first_name} {editor.last_name}"
            if editor.affiliation_key:
                editor.affiliation = volume.affiliations[int(editor.affiliation_key)]
                editor.country = editor.affiliation.country
            if volume.submitting_editor_key and int(volume.submitting_editor_key) == i+1:
                volume.submitting_editor = editor

        for paper in volume.paper:
            for author in paper.authors:
                author.name = f"{author.first_name} {author.last_name}"
            if paper.pdf:
                paper.pdf = f"/static/files/{paper.pdf}"
        volume.tocPaper = volume.paper
        return volume





    def generate_preview(self):
        """
        Generate the volume page index file from the form input and display the page
        """
        volume_record = self.get_prepared_volume_record()
        vpt = VolumePageTemplate()
        html = vpt.render(volume_record)
        self.preview_div.delete_components()
        print(volume_record)
        print(html)
        jp.Iframe(
                a=self.preview_div,
                srcdoc=html,
                classes="w-full h-full outline outline-blue-500 p-4 m-4"
        )


if __name__ == '__main__':
    def test_app():
        jp.WebPage.debug = True
        wp = jp.WebPage(head_html='<script src="https://cdn.tailwindcss.com"></script>')
        div = jp.Div(a=wp, classes="container mx-auto flex")
        CeurVolumeForm(a=div)
        return wp
    Demo("test_app", test_app)