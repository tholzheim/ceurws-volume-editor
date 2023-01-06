import base64
import io
import typing

import justpy as jp

from volumeEditor.file_handler import FileHandler
from volumeEditor.forms import IdSelector, InputTypes, ItemList, LabeledField
from volumeEditor.parser import PaperMetadata

class VolumeForm(jp.Div):

    def __init__(self, **kwargs):
        """
        constructor
        """
        super(VolumeForm, self).__init__(**kwargs)
        self.selection_option_sources: typing.Dict[str, typing.Callable] = {}
        self.header = jp.H1(a=self, text="Enter new Volume")
        self.content_div = jp.Div(a=self, classes="grid grid-cols-6 gap-4 m-6 p-4 bg-slate-200")
        self.event_title = LabeledField(
                a=self.content_div,
                label="Event title",
                classes="col-span-6",
                input_type=InputTypes.TEXT_AREA
        )
        self.acronym = LabeledField(
                a=self.content_div,
                label="Acronym",
                classes="col-span-1"
        )
        self.start_date = LabeledField(
                a=self.content_div,
                label="Start date",
                classes="col-span-1",
                input_type=InputTypes.DATE
        )
        self.end_date = LabeledField(
                a=self.content_div,
                label="End date",
                classes="col-span-1",
                input_type=InputTypes.DATE
        )
        self.country = LabeledField(
                a=self.content_div,
                label="Country",
                classes="col-span-1"
        )
        self.city = LabeledField(
                a=self.content_div,
                label="City",
                classes="col-span-1"
        )
        self.submitting_editor = LabeledField(
                a=self.content_div,
                label="Submitting editor",
                classes="col-span-1",
                input_type=InputTypes.SELECT,
                on_click=self.handle_submitting_editor_field_click
        )
        self.editors = ItemList(
                a=jp.Div(a=self.content_div, classes="col-span-6 mx-4"),
                item_class=EditorForm,
                title="Editors"
        )
        self.affiliations = ItemList(
                a=jp.Div(a=self.content_div, classes="col-span-6 mx-4"),
                item_class=AffiliationForm,
                title="Affiliations"
        )
        self.editors.selection_option_sources["affiliations"] = self.affiliations.get_items
        self.paper = ItemList(
                a=jp.Div(a=self.content_div, classes="col-span-6 mx-4"),
                item_class=PaperForm,
                title="Paper",
                bg="bg-slate-300"
        )

        # test controls
        jp.Button(a=self, text="get records", on_click=self.handle_get_record)
        self.record_div = jp.Div(a=self)

    def handle_get_record(self, msg):
        self.record_div.text = str(self.get_record())

    def get_record(self):
        affiliations = self.affiliations.get_records()
        for i, affiliation in enumerate(affiliations):
            affiliation["affiliation_key"] = i
        paper = self.paper.get_records()
        for i, record in enumerate(paper):
            record["id"] = i
        return dict(
                event_title=self.event_title.get_value(),
                acronym=self.acronym.get_value(),
                start_date=self.start_date.get_value(),
                end_date=self.end_date.get_value(),
                city=self.city.get_value(),
                country=self.country.get_value(),
                submitting_editor_key=self.submitting_editor.get_value(),
                editors=self.editors.get_records(),
                affiliations=affiliations,
                paper=paper
        )

    def handle_submitting_editor_field_click(self, msg):
        self.update_submitting_editor_options()

    def update_selection_options(self):
        """
        update the selection options for the submitting editor
        """
        self.update_submitting_editor_options()

    def update_submitting_editor_options(self):
        editor_forms = self.editors.get_items()
        self.submitting_editor.field.delete_components()
        for i, editor_form in enumerate(editor_forms, start=1):
            label = f"{editor_form.get_name()} (#{i})"
            self.submitting_editor.field.add(jp.Option(value=i, text=label))


class AffiliationForm(jp.Div):
    """
    Form for the affiliations
    """
    LABEL = "Affiliation"

    def __init__(self, **kwargs):
        """
        constructor
        """
        super(AffiliationForm, self).__init__(**kwargs)
        self.x = LabeledField(a=self, label="Name")
        self.homepage = LabeledField(a=self, label="Official website")
        self.country = LabeledField(a=self, label="Country")
        self.city = LabeledField(a=self, label="City")

    def get_record(self) -> dict:
        return dict(
                name=self.x.get_value(),
                homepage=self.homepage.get_value(),
                country=self.country.get_value(),
                city=self.city.get_value()
        )


class PaperForm(jp.Div):
    """
    DropZone
    see https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/File_drag_and_drop
    """
    LABEL = "Paper"


    def __init__(self, paper: PaperMetadata = None, **kwargs):
        super(PaperForm, self).__init__(**kwargs)
        self.paper = paper
        self.container = jp.Div(a=self, classes="grid grid-cols-2")
        # paper metadata
        self.div_form = jp.Div(a=self.container)
        self.title_field = LabeledField(a=self.div_form, label="Title")
        self.authors = ItemList(
                a=jp.Div(a=self.div_form, classes="ml-4"),
                item_class=AuthorForm,
                title="Authors",
                bg="bg-blue-100"
        )
        self.init_authors()

        # pdf
        self.div_pdf = jp.Div(
                a=self.container,
                classes="m-4 outline outline-dashed hover:outline-gray-500"
        )
        self.init_pdf_div()

    def init_authors(self):
        if self.paper is not None:
            self.title_field.set_value(self.paper.title)
            for author in self.paper.authors.split(","):
                author_parts = author.split(" ")
                first_name = " ".join(author_parts[:-1])
                last_name = author_parts[-1]
                af = AuthorForm(first_name=first_name, last_name=last_name)
                self.authors.add_item(af)

    def init_pdf_div(self):
        self.div_pdf.delete_components()
        if self.paper is None or self.paper.filename is None:
            div = jp.Div(a=self.div_pdf, classes="flex grow h-full max-h-30")
            f = jp.Form(
                    a=div,
                    enctype='multipart/form-data',
                    submit=self.handle_file_submit,
                    classes="m-auto"
            )
            file_input = jp.Input(
                    a=f,
                    type='file',
                    classes=jp.Styles.input_classes,
                    multiple=False
            )
            jp.Button(
                    a=f,
                    type='submit',
                    text='Upload',
                    classes=jp.Styles.button_simple
            )
        else:
            jp.Iframe(
                    a=self.div_pdf,
                    src=f"/static/files/{self.paper.filename}",
                    classes="w-full h-full"
            )

    def handle_file_submit(self, msg):
        c = None
        for c in msg.form_data:
            if c.type == 'file':
                break
        # Write the content to a file after decoding the base64 content
        file_handler = FileHandler()
        for i, f in enumerate(c.files):
            file = io.BytesIO(base64.b64decode(f.file_content))
            file_handler.save_user_file(session_id=msg.session_id, filename=f.name, file=file)
            file = file_handler.get_user_file(msg.session_id, f.name)
            paper = PaperMetadata.from_file(file)
            paper.filename = f"{msg.session_id}/{paper.filename}"
            self.paper = paper
        self.init_authors()
        self.init_pdf_div()

    @classmethod
    def from_file(cls, file, a, session_id) -> 'PaperForm':
        paper = PaperMetadata.from_file(file)
        paper.filename = f"{session_id}/{paper.filename}"
        paper_form = PaperForm(a=a, paper=paper)
        return paper_form

    def get_record(self):
        return dict(
                title=self.title_field.get_value(),
                pdf=self.paper.filename if self.paper else None,
                authors=self.authors.get_records()
        )


class AuthorForm(jp.Div):
    LABEL = "Author"
    def __init__(
            self,
            first_name: str = None,
            last_name: str = None,
            **kwargs
    ):
        super().__init__(**kwargs, classes="rounded-xl")
        self.div = jp.Div(a=self, classes="grid grid-cols-6 gap-6")
        self.first_name = self._setup_input_field("First name", first_name, parent=self.div)
        self.last_name = self._setup_input_field("Last name", last_name, parent=self.div)
        self.ids = IdSelector(
                a=jp.Div(a=self.div, classes="col-span-6 mx-4"),
                title="Identifier",
                bg="bg-blue-100"
        )

    def get_record(self) -> dict:
        return dict(
                first_name=self.first_name.value,
                last_name=self.last_name.value,
                identifier=self.ids.get_records()
        )

    def get_name(self) -> str:
        record = self.get_record()
        first_name = record.get("first_name", None)
        last_name = record.get("last_name", None)
        return f"{first_name} {last_name}"

    def _setup_input_field(self, label: str, value: str = None, parent: jp.HTMLBaseComponent = None):
        if parent is None:
            parent = self
        div = jp.Div(a=parent, classes="col-span-6 sm:col-span-3")
        labeled_field = LabeledField(label=label, value=value, a=div)
        return labeled_field.field


class EditorForm(AuthorForm):
    """
    Form for the editor of the volume
    """
    LABEL = "Editor"

    def __init__(self, **kwargs):
        """
        constructor
        """
        super(EditorForm, self).__init__(**kwargs)
        self.selection_option_sources: typing.Dict[str, typing.Callable] = {}
        self.affiliation = LabeledField(a=self.div, label="Affiliation", input_type=InputTypes.SELECT)

    def update_selection_options(self):
        """
        update the selection options for the affiliations
        """
        if "affiliations" in self.selection_option_sources:
            callback = self.selection_option_sources.get("affiliations", None)
            if callable(callback):
                affiliation_option: AffiliationForm
                self.affiliation.field.delete_components()
                for i, affiliation_option in enumerate(callback()):
                    affiliation_record = affiliation_option.get_record()
                    label = f"{affiliation_record.get('name', '')} (#{i+1})"
                    self.affiliation.field.add(jp.Option(value=i, text=label))

    def get_record(self) -> dict:
        return dict(
                **super().get_record(),
                affiliation_key=self.affiliation.get_value()
        )